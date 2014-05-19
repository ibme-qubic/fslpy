#!/usr/bin/env python
#
# slicecanvas.py - A wx.GLCanvas canvas which displays a single
# slice from a collection of 3D images.
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#

import numpy             as np

import                      wx
import wx.glcanvas       as wxgl

import OpenGL.GL         as gl
import OpenGL.GL.shaders as shaders
import OpenGL.arrays.vbo as vbo

# Under OS X, I don't think I can request an OpenGL 3.2 core profile
# using wx - I'm stuck with OpenGL 2.1 I'm using these ARB extensions
# for functionality which is standard in 3.2.
import OpenGL.GL.ARB.instanced_arrays as arbia
import OpenGL.GL.ARB.draw_instanced   as arbdi
import OpenGL.GL.ARB.texture_rg       as arbrg

import fsl.data.fslimage as fslimage


class GLImageData(object):
    """
    A GLImageData object encapsulates the OpenGL information necessary
    to render an image.
    
    A slice from one image is rendered using three buffers and one
    texture. The first buffer, the 'geometry buffer' simply contains four
    vertices, which define the geometry of a single voxel (using triangle
    strips).

    The second buffer, the 'position buffer', contains the location of every
    voxel in one slice of the image (these locations are identical for every
    slice of the image, so we can re-use the location information for every
    slice). The four vertices for each voxel (from the geometry buffer, above)
    are offset by the voxel position, which is read from this position buffer.

    The third buffer, the 'image buffer' contains the image data itself,
    scaled to lie between 0 and 255. It is used to calculate voxel colours.

    Finally, the texture, the 'colour buffer', is used to store a lookup table
    containing colours.
    """

    def __init__(self, image, canvas):
        """
        Initialise the OpenGL data buffers required to render the given image.
        Parameters:
          - image:  A fsl.data.fslimage.Image object.
          - canvas: The SliceCanvas object which is rendering the image.
        """

        self.image      = image
        self.canvas     = canvas

        # Here, x,y, and z refer to screen
        # coordinates, not image coordinates:
        #   - x: horizontal
        #   - y: vertical
        #   - z: depth

        # number of voxels along each axis
        self.xdim = image.shape[ canvas.xax]
        self.ydim = image.shape[ canvas.yax]
        self.zdim = image.shape[ canvas.zax]

        # length of a voxel along each axis
        self.xlen = image.pixdim[canvas.xax]
        self.ylen = image.pixdim[canvas.yax]
        self.zlen = image.pixdim[canvas.zax]

        # Maximum number of colours used to draw image data
        self.colourResolution = 256

        self.initGLImageData()


    def initGLImageData(self):
        """
        Creates and initialises the OpenGL data for the fslimage.Image
        object that was passed to the GLImageData constructor.
        """

        image           = self.image
        canvas          = self.canvas
        self.dataBuffer = self.initImageBuffer()

        # Data stored in the geometry buffer. Defines
        # the geometry of a single voxel, rendered as
        # a triangle strip.
        halfx    = self.xlen / 2.0
        halfy    = self.ylen / 2.0
        geomData = np.array([-halfx, -halfy,
                              halfx, -halfy,
                             -halfx,  halfy,
                              halfx,  halfy], dtype=np.float32)

        # x/y/z coordinates are stored as
        # VBO arrays in the range [0, 1]
        voxData = []
        for (imgDim, texDim) in zip(image.shape, self.imageTexShape):

            stop = float(imgDim) / texDim
            step = stop / imgDim
            data = np.arange(step / 2.0, stop, step, dtype=np.float32)

            voxData.append(data)        
        
        # the screen x coordinate data has to be repeated (ylen)
        # times - we are drawing row-wise, and opengl does not
        # allow us to loop over a VBO in a single instance
        # rendering call
        voxData[canvas.xax] = np.tile(voxData[canvas.xax], self.ydim)

        xData = voxData[0]
        yData = voxData[1]
        zData = voxData[2]
        
        xBuffer = vbo.VBO(xData, gl.GL_STATIC_DRAW)
        yBuffer = vbo.VBO(yData, gl.GL_STATIC_DRAW)
        zBuffer = vbo.VBO(zData, gl.GL_STATIC_DRAW)        

        # Data stored in the position buffer. Defines
        # the location of every voxel in a single slice.
        # First we create a set of voxel coordinates for
        # every voxel in one slice.
        xidxs        = np.arange(self.xdim, dtype=np.float32)
        yidxs        = np.arange(self.ydim, dtype=np.float32)
        yidxs, xidxs = np.meshgrid(yidxs, xidxs, indexing='ij')

        # And put them into a single array
        positionData = np.vstack((
            xidxs.ravel(order='C'),
            yidxs.ravel(order='C'))).transpose()

        # Then we transform them from voxel
        # coordinates to world coordinates,
        # making sure that they are of type
        # float32
        positionData = image.voxToWorld(positionData, axes=(canvas.xax,
                                                            canvas.yax))
        positionData = np.array(positionData, dtype=np.float32)
        positionData = positionData.ravel('C')

        # The image buffers, containing the image data 
        screenPosBuffer = vbo.VBO(positionData, gl.GL_STATIC_DRAW)
        geomBuffer      = vbo.VBO(geomData,     gl.GL_STATIC_DRAW)

        self.voxXBuffer      = xBuffer
        self.voxYBuffer      = yBuffer
        self.voxZBuffer      = zBuffer
        self.screenPosBuffer = screenPosBuffer
        self.geomBuffer      = geomBuffer

        # Add listeners to this image so the view can be
        # updated when its display properties are changed
        self.configDisplayListeners()

        
    def initImageBuffer(self):
        """
        Initialises the OpenGL buffer used to store the data for the given
        image. The buffer is stored as an attribute of the image and, if it
        has already been created (e.g. by another SliceCanvas object), the
        existing buffer is returned. 
        """

        image = self.image

        texShape = 2 ** (np.ceil(np.log2(image.shape)))
        pad      = [(0, l - s) for (l, s) in zip(texShape, image.shape)]
        self.imageTexShape = texShape 

        try:    imageBuffer = image.getAttribute('glBuffers')
        except: imageBuffer = None

        if imageBuffer is not None:
            return imageBuffer

        # The image data is normalised to lie
        # between 0 and 255, and cast to uint8
        imageData = np.array(image.data, dtype=np.float32)
        imageData = 255.0 * (imageData       - imageData.min()) / \
                            (imageData.max() - imageData.min())

        # and each dimension is padded so
        # it has a power-of-two length
        imageData = np.pad(imageData, pad, 'constant', constant_values=0)
        imageData = np.array(imageData, dtype=np.uint8)

        # Then flattened, with fortran dimension ordering,
        # so the data, as stored on the GPU, has its first
        # dimension as the fastest changing.
        imageData = imageData.ravel(order='F')

        # Image data is stored on the GPU as a 3D texture
        imageBuffer = gl.glGenTextures(1)
        gl.glBindTexture(gl.GL_TEXTURE_3D, imageBuffer)
        gl.glTexParameteri(
            gl.GL_TEXTURE_3D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
        gl.glTexParameteri(
            gl.GL_TEXTURE_3D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)
        gl.glTexParameteri(
            gl.GL_TEXTURE_3D, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE)
        gl.glTexParameteri(
            gl.GL_TEXTURE_3D, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE)
        gl.glTexParameteri(
            gl.GL_TEXTURE_3D, gl.GL_TEXTURE_WRAP_R, gl.GL_CLAMP_TO_EDGE)         
        
        gl.glTexImage3D(gl.GL_TEXTURE_3D,
                        0,
                        arbrg.GL_R8,
                        texShape[0],
                        texShape[1],
                        texShape[2],
                        0,
                        gl.GL_RED,
                        gl.GL_UNSIGNED_BYTE,
                        imageData)

        # And added as an attribute of the image, so
        # other things which want to render the image
        # don't need to recreate all of those buffers.
        image.setAttribute('glBuffers', imageBuffer)

        return imageBuffer


    def configDisplayListeners(self):
        """
        Adds a bunch of listeners to the fslimage.ImageDisplay object
        (accessible as an attribute, called 'display', of the given image),
        which defines how the given image is to be displayed. This is done
        so we can refresh the image view when image display properties are
        changed. 
        """

        def refreshNeeded(*a):
            """
            The view just needs to be refreshed (e.g. the alpha property
            has changed).
            """
            self.canvas.Refresh()

        def colourUpdateNeeded(*a):
            """
            The colour map for this image needs to be recreated (e.g. the
            colour map has been changed).
            """
            self.updateColourBuffer()
            self.canvas.Refresh()

        display           = self.image.display
        lnrName           = 'SliceCanvas_{{}}_{}'.format(id(self))
        refreshProps      = ['alpha', 'enabled']
        colourUpdateProps = ['displayMin', 'displayMax', 'rangeClip', 'cmap']

        for prop in refreshProps:
            display.addListener(prop, lnrName.format(prop), refreshNeeded)

        for prop in colourUpdateProps:
            display.addListener(prop, lnrName.format(prop), colourUpdateNeeded)



# The vertex shader positions and colours a single vertex.
vertex_shader = """
#version 120

/* Opacity - constant for a whole image */
uniform float alpha;

/* image data texture */
uniform sampler3D dataBuffer;

/* Current vertex */
attribute vec2 inVertex;

/* Current screen coordinates */
attribute vec2 screenPos;

/* voxel coordinates */
attribute float voxX;
attribute float voxY;
attribute float voxZ;

/* Voxel value passed through to fragment shader */ 
varying float fragVoxValue;

void main(void) {

    /*
     * Offset the vertex by the current voxel position
     * (and perform standard transformation from data
     * coordinates to screen coordinates).
     */
    gl_Position = gl_ModelViewProjectionMatrix *  \
        vec4(inVertex + screenPos, 0.0, 1.0);

    /* Pass the voxel value through to the shader. */
    vec4 vt = texture3D(dataBuffer, vec3(voxX, voxY, voxZ));
    fragVoxValue = vt.r;
}
"""


# Buffer shader. Given the current voxel value, looks
# up the appropriate colour in the colour buffer.
fragment_shader = """
#version 120

uniform float     alpha; 
varying float     fragVoxValue;

void main(void) {

    vec3 voxColour = vec3(fragVoxValue, fragVoxValue, fragVoxValue);
    float voxAlpha = alpha;

    gl_FragColor = vec4(voxColour, voxAlpha);
}
"""


class SliceCanvas(wxgl.GLCanvas):
    """
    A wx.glcanvas.GLCanvas which may be used to display a single 2D slice from
    a collection of 3D images (see fsl.data.fslimage.ImageList).
    """

    @property
    def zpos(self):
        """
        The slice currently being displayed.
        """
        return self._zpos

    @zpos.setter
    def zpos(self, zpos):
        """
        Change the slice being displayed. You will need to manually call
        Refresh() after changing the zpos.
        """

        if   zpos > self.zmax: zpos = self.zmax
        elif zpos < self.zmin: zpos = self.zmin

        self._zpos = zpos

    @property
    def xpos(self):
        """
        The current X (horizontal) location of the cursor. 
        """
        return self._xpos

    @xpos.setter
    def xpos(self, xpos):
        """
        Change the x cursor position. You will need to manually call
        Refresh() after changing the xpos.
        """ 

        if   xpos > self.xmax: xpos = self.xmax
        elif xpos < self.xmin: xpos = self.xmin 

        self._xpos = xpos

    @property
    def ypos(self):
        """
        The current Y (vertical) location of the cursor.
        """
        return self._ypos

    @ypos.setter
    def ypos(self, ypos):
        """
        Change the y cursor position. You will need to manually call
        Refresh() after changing the ypos.
        """ 
        
        if   ypos > self.ymax: ypos = self.ymax
        elif ypos < self.ymin: ypos = self.ymin 

        self._ypos = ypos


    def __init__(self, parent, imageList, zax=0, context=None):
        """
        Creates a canvas object. The OpenGL data buffers are set up the
        first time that the canvas is displayed/drawn.
        
        Parameters:
        
          parent    - WX parent object
        
          imageList - a fslimage.ImageList object.
        
          zax       - Axis perpendicular to the plane to be displayed
                      (the 'depth' axis), default 0.

          context   - wx.glcanvas.GLContext object. If None, one is created.
        """

        if not isinstance(imageList, fslimage.ImageList):
            raise TypeError(
                'imageList must be a fsl.data.fslimage.ImageList instance') 

        wxgl.GLCanvas.__init__(self, parent)

        # Use the provided shared GL
        # context, or create a new one
        if context is None: self.context = wxgl.GLContext(self)
        else:               self.context = context

        self.imageList = imageList
        self.name      = 'SliceCanvas_{}'.format(id(self))

        # These attributes map from the image axes to
        # the display axes. xax is horizontal, yax
        # is vertical, and zax is depth.
        #
        # TODO Currently, the displayed x/horizontal and
        # y/vertical axes are defined by their order in
        # the image. We could allow the caller to specify
        # which axes should be horizontal/vertical.
        dims = range(3)
        dims.pop(zax)
        self.xax = dims[0]
        self.yax = dims[1]
        self.zax = zax

        # Current cursor location, initialised
        # in _imageListChanged
        self._xpos = None
        self._ypos = None
        self._zpos = None

        self.xmin = 0
        self.ymin = 0
        self.zmin = 0
        self.xmax = 1
        self.ymax = 1
        self.zmax = 1

        # This flag is set by the _initGLData method
        # when it has finished initialising the OpenGL
        # shaders
        self.glReady = False

        # All the work is done by the draw method
        self.Bind(wx.EVT_PAINT, self.draw)

        # When the image list changes, refresh the
        # display, and update the display bounds
        self.imageList.addListener(lambda il: self._imageListChanged())


    def _imageListChanged(self):
        """
        This method is called once by _initGLData on the first draw, and
        then again every time an image is added or removed from the
        image list. For newly added images, it creates a GLImageData
        object, which initialises the OpenGL data necessary to render
        the image. This method also updates the canvas bounds (i.e.
        the min/max x/y/z coordinates across all images being displayed).
        """

        if len(self.imageList) == 0:
            # These attributes define the current location
            # of the cursor, and the current depth, in real
            # world coordinates. 
            self._xpos = 0.5
            self._ypos = 0.5
            self._zpos = 0.5

            # These attributes define the spatial data
            # limits of all displayed images, in real world
            # coordinates. They are updated whenever an
            # image is added/removed from the list.
            self.xmin = 0
            self.ymin = 0
            self.zmin = 0
            self.xmax = 1
            self.ymax = 1 
            self.zmax = 1 
        
        else:

            # Update the minimum/maximum
            # image bounds along each axis
            self.xmin = self.imageList.minBounds[self.xax]
            self.ymin = self.imageList.minBounds[self.yax]
            self.zmin = self.imageList.minBounds[self.zax]

            self.xmax = self.imageList.maxBounds[self.xax]
            self.ymax = self.imageList.maxBounds[self.yax]
            self.zmax = self.imageList.maxBounds[self.zax]

            # initialise the cursor location and displayed
            # slice if they do not yet have values
            if not all((self._xpos, self._ypos, self._zpos)):
                self.xpos = (abs(self.xmax) - abs(self.xmin)) / 2.0
                self.ypos = (abs(self.ymax) - abs(self.ymin)) / 2.0
                self.zpos = (abs(self.zmax) - abs(self.zmin)) / 2.0
                
        # Create a GLImageData object
        # for any new images
        for image in self.imageList:
            try:
                glData = image.getAttribute(self.name)
            except:
                glData = GLImageData(image, self)
                image.setAttribute(self.name, glData)
                
        self.Refresh()


    def _initGLData(self):
        """
        Compiles the vertex and fragment shader programs, and
        stores references to the shader variables as attributes
        of this SliceCanvas object. This method is only called
        once, on the first draw.
        """
 
        self.context.SetCurrent(self)

        self.shaders = shaders.compileProgram(
            shaders.compileShader(vertex_shader,   gl.GL_VERTEX_SHADER),
            shaders.compileShader(fragment_shader, gl.GL_FRAGMENT_SHADER))

        # Indices of all vertex/fragment shader parameters
        self.alphaPos         = gl.glGetUniformLocation(self.shaders, 'alpha')
        self.dataBufferPos    = gl.glGetUniformLocation(self.shaders,
                                                        'dataBuffer')
        self.inVertexPos      = gl.glGetAttribLocation( self.shaders,
                                                        'inVertex')
        self.screenPosPos     = gl.glGetAttribLocation( self.shaders,
                                                        'screenPos')
        self.voxXPos          = gl.glGetAttribLocation( self.shaders, 'voxX')
        self.voxYPos          = gl.glGetAttribLocation( self.shaders, 'voxY')
        self.voxZPos          = gl.glGetAttribLocation( self.shaders, 'voxZ')

        # Initialise data for the images that
        # are already in the image list 
        self._imageListChanged()


        # A bit hacky. We can only set the GL context (and create
        # the GL data) once something is actually displayed on the
        # screen. The _initGLData method is called (asynchronously)
        # by the draw() method if it sees that the glReady flag has
        # not yet been set. But draw() may be called mored than once
        # before _initGLData is called. Here, to prevent
        # _initGLData from running more than once, the first time
        # it is called it simply overwrites itself with a dummy method.
        self._initGLData = lambda s: s

        self.glReady = True

        
    def resize(self):
        """
        Sets up the GL canvas size, viewport, and
        projection. This method is called by draw(),
        so does not need to be called manually.
        """

        size = self.GetSize()
        
        # set up 2D drawing
        gl.glViewport(0, 0, size.width, size.height)
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        gl.glOrtho(self.xmin, self.xmax, self.ymin, self.ymax, 0, 1)
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()


    def draw(self, ev):
        """
        Draws the currently selected slice to the canvas.
        """

        # image data has not been initialised.
        if not self.glReady:
            wx.CallAfter(self._initGLData)
            return

        self.context.SetCurrent(self)
        self.resize()

        # clear the canvas
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

        # load the shaders
        gl.glUseProgram(self.shaders)

        # enable transparency
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

        # disable interpolation
        gl.glShadeModel(gl.GL_FLAT)

        for image in self.imageList:

            # The GL data is stored as an attribute of the image,
            # and is created in the _imageListChanged method when
            # images are added to the image. If there's no data
            # here, ignore it; hopefully by the time draw() is
            # called again, it will have been created.
            try:    glImageData = image.getAttribute(self.name)
            except: continue
            
            imageDisplay   = image.display
            
            dataBuffer      = glImageData.dataBuffer
            voxXBuffer      = glImageData.voxXBuffer
            voxYBuffer      = glImageData.voxYBuffer
            voxZBuffer      = glImageData.voxZBuffer
            geomBuffer      = glImageData.geomBuffer
            screenPosBuffer = glImageData.screenPosBuffer

            xdim = glImageData.xdim
            ydim = glImageData.ydim
            zdim = glImageData.zdim

            # Don't draw the slice if this
            # image display is disabled
            if not imageDisplay.enabled: continue 

            # Figure out which slice we are drawing,
            # and if it's out of range, don't draw it
            zi = int(image.worldToVox(self.zpos, self.zax))
            if zi < 0 or zi >= zdim: continue

            # bind the current alpha value to the
            # shader alpha variable
            gl.glUniform1f(self.alphaPos, imageDisplay.alpha)

            # bind the transformation matrix
            # to the shader variable
            # gl.glUniformMatrix4fv(self.voxToWorldMatPos,
            #                      1, False, transformBuffer)

            # Set up the colour buffer
            # gl.glEnable(gl.GL_TEXTURE_1D)
            # gl.glActiveTexture(gl.GL_TEXTURE0) 
            # gl.glBindTexture(gl.GL_TEXTURE_1D, colourBuffer)
            # gl.glUniform1i(self.colourMapPos, 0) 

            # Set up the image data buffer
            gl.glEnable(gl.GL_TEXTURE_3D)
            # change to texxture 1 when you get working
            gl.glActiveTexture(gl.GL_TEXTURE0) 
            gl.glBindTexture(gl.GL_TEXTURE_3D, dataBuffer)
            gl.glUniform1i(self.dataBufferPos, 0)

            # Screen x/y positions
            screenPosBuffer.bind()
            gl.glVertexAttribPointer(
                self.screenPosPos,
                2,
                gl.GL_FLOAT,
                gl.GL_FALSE,
                0,
                None)
            gl.glEnableVertexAttribArray(self.screenPosPos)
            arbia.glVertexAttribDivisorARB(self.screenPosPos, 1)

            # voxel coordinates
            voxOffs  = [0, 0, 0]
            voxSteps = [1, 1, 1]
            voxOffs[ self.zax] = zi
            voxSteps[self.yax] = xdim
            voxSteps[self.zax] = xdim * ydim
            for buf, pos, step, off in zip(
                    (voxXBuffer, voxYBuffer, voxZBuffer),
                    (self.voxXPos, self.voxYPos, self.voxZPos),
                    voxSteps,
                    voxOffs):

                if off == 0: off = None
                else:        off = buf + (off * 4)
                
                buf.bind()
                gl.glVertexAttribPointer(
                    pos,
                    1,
                    gl.GL_FLOAT,
                    gl.GL_FALSE,
                    0,
                    off)
                gl.glEnableVertexAttribArray(pos)
                arbia.glVertexAttribDivisorARB(pos, step)

            # The geometry buffer, which defines the geometry of a
            # single vertex (4 vertices, drawn as a triangle strip)
            geomBuffer.bind()
            gl.glVertexAttribPointer(
                self.inVertexPos,
                2,
                gl.GL_FLOAT,
                gl.GL_FALSE,
                0,
                None)
            gl.glEnableVertexAttribArray(self.inVertexPos)
            arbia.glVertexAttribDivisorARB(self.inVertexPos, 0)
            
            arbdi.glDrawArraysInstancedARB(
                gl.GL_TRIANGLE_STRIP, 0, 4, xdim * ydim)

            gl.glDisableVertexAttribArray(self.inVertexPos)
            gl.glDisableVertexAttribArray(self.screenPosPos)
            gl.glDisableVertexAttribArray(self.voxXPos)
            gl.glDisableVertexAttribArray(self.voxYPos)
            gl.glDisableVertexAttribArray(self.voxZPos)
#            gl.glDisable(gl.GL_TEXTURE_1D)
            gl.glDisable(gl.GL_TEXTURE_3D)

        gl.glUseProgram(0)

        # A vertical line at xpos, and a horizontal line at ypos
        x = self.xpos
        y = self.ypos

        gl.glBegin(gl.GL_LINES)
        gl.glColor3f(0, 1, 0)
        gl.glVertex2f(x,         self.ymin)
        gl.glVertex2f(x,         self.ymax)
        gl.glVertex2f(self.xmin, y)
        gl.glVertex2f(self.xmax, y)
        gl.glEnd()

        self.SwapBuffers()
