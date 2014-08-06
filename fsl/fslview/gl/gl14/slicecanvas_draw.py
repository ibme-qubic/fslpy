#!/usr/bin/env python
#
# slicecanvas_draw.py - Render slices from a collection of images in an OpenGL
#                       1.4 compatible manner.
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#
"""Render slices from a collection of images in an OpenGL 1.4 compatible
 manner, using immediate mode rendering. 

.. note:: This module is extremely tightly coupled to the
:class:`~fsl.fslview.gl.slicecanvas.SliceCanvas` class, and to the
:class:`~fsl.fslview.gl.gl14.glimagedata.GLImageData` class.

This module provides two functions:

  - :func:`drawScene` draws slices from all of the images in an
    :class:`~fsl.data.image.ImageList` to a
    :class:`~fsl.fslview.gl.slicecanvas.SliceCanvas` display.

  - :func:`drawSlice` (used by :func:`drawScene`) draws slices from one image
    to the :class:`~fsl.fslview.gl.slicecanvas.SliceCanvas`.
"""

import logging

log = logging.getLogger(__name__)

import numpy       as np
import OpenGL.GL   as gl
        
def drawSlice(canvas, image, zpos, xform=None):
    """Draws the specified slice from the specified image on the canvas.

    If ``xform`` is not provided, the
    :class:`~fsl.data.image.Image` ``voxToWorldMat`` transformation
    matrix is used.

    :arg image:   The :class:`~fsl.data.image.Image` object to draw.
    
    :arg zpos:    World Z position of slice to be drawn.
    
    :arg xform:   A 4*4 transformation matrix to be applied to the slice
                  data (or ``None`` to use the
                  :class:`~fsl.data.image.Image` ``voxToWorldMat``
                  matrix).
    """

    # The GL data is stored as an attribute of the image,
    # and is created in the SliceCanvas._imageListChanged
    # method when images are added to the image. If there's
    # no data here, ignore it; hopefully by the time the
    # image is to be drawn again, it will have been created.
    try:    glImageData = image.getAttribute(canvas.name)
    except: return
    
    imageDisplay = image.getAttribute('display')
    
    # Don't draw the slice if this
    # image display is disabled
    if not imageDisplay.enabled: return

    xmin, xmax = image.imageBounds(canvas.xax)
    ymin, ymax = image.imageBounds(canvas.yax)
    
    xmid     = xmin + (xmax - xmin) / 2.0
    ymid     = ymin + (ymax - ymin) / 2.0
    midSlice = image.worldToVox(
        [[xmid, ymid, zpos]],
        axes=[canvas.xax, canvas.yax, canvas.zax])[0][2]

    voxelX =  glImageData.voxelX 
    voxelY =  glImageData.voxelY 
    voxelZ = (glImageData.voxelZ + midSlice)

    xout = (voxelX < 0) | (voxelX >= image.shape[canvas.xax])
    yout = (voxelY < 0) | (voxelY >= image.shape[canvas.yax])
    zout = (voxelZ < 0) | (voxelZ >= image.shape[canvas.zax])

    inVoxels = ~(xout | yout | zout)

    voxelX = voxelX[inVoxels] / imageDisplay.samplingRate
    voxelY = voxelY[inVoxels] / imageDisplay.samplingRate
    voxelZ = voxelZ[inVoxels] / imageDisplay.samplingRate

    worldX = glImageData.worldX[inVoxels]
    worldY = glImageData.worldY[inVoxels]

    imageData      = glImageData.imageData
    texCoordXform  = glImageData.texCoordXform
    colourTexture  = glImageData.colourTexture

    voxelIdxs = [None] * 3
    voxelIdxs[canvas.xax] = np.array(voxelX, dtype=np.int32)
    voxelIdxs[canvas.yax] = np.array(voxelY, dtype=np.int32)
    voxelIdxs[canvas.zax] = np.array(voxelZ, dtype=np.int32)

    worldCoords = [None] * 3
    worldCoords[canvas.xax] = worldX
    worldCoords[canvas.yax] = worldY
    worldCoords[canvas.zax] = np.repeat(zpos, len(worldX))
    
    imageData = imageData[voxelIdxs]
    vertices  = np.vstack(worldCoords)
    vertices  = vertices .ravel('F')
    imageData = imageData.ravel('F')

    if xform is not None: 
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glPushMatrix()
        gl.glMultMatrixf(xform)

    gl.glTexEnvf(gl.GL_TEXTURE_ENV, gl.GL_TEXTURE_ENV_MODE, gl.GL_REPLACE)
    gl.glBindTexture(gl.GL_TEXTURE_1D, colourTexture)

    gl.glMatrixMode(gl.GL_TEXTURE)
    gl.glPushMatrix()
    gl.glMultMatrixf(texCoordXform)

    gl.glEnableClientState(gl.GL_TEXTURE_COORD_ARRAY)
    gl.glEnableClientState(gl.GL_VERTEX_ARRAY)

    gl.glVertexPointer(  3, gl.GL_FLOAT, 0, vertices)
    gl.glTexCoordPointer(1, gl.GL_FLOAT, 0, imageData)

    gl.glDrawArrays(gl.GL_QUADS, 0, len(worldX))

    gl.glDisableClientState(gl.GL_TEXTURE_COORD_ARRAY)
    gl.glDisableClientState(gl.GL_VERTEX_ARRAY)

    if xform is not None:
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glPopMatrix()

    gl.glMatrixMode(gl.GL_TEXTURE)
    gl.glPopMatrix()
    
    
def drawScene(canvas):
    """Draws the currently selected slice (as specified by the ``z``
    value of the :attr:`pos` property) to the canvas."""

    canvas.glContext.SetCurrent(canvas)

    canvas._setViewport()

    # clear the canvas
    gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

    # enable transparency
    gl.glEnable(gl.GL_BLEND)
    gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

    # disable interpolation
    gl.glShadeModel(gl.GL_FLAT)

    gl.glEnable(gl.GL_TEXTURE_1D)

    for image in canvas.imageList:

        log.debug('Drawing {} slice for image {}'.format(
            canvas.zax, image.name))

        drawSlice(canvas, image, canvas.pos.z)

    gl.glDisable(gl.GL_TEXTURE_1D)

    if canvas.showCursor:

        # A vertical line at xpos, and a horizontal line at ypos
        xverts = np.zeros((2, 3))
        yverts = np.zeros((2, 3))

        xmin, xmax = canvas.imageList.bounds.getRange(canvas.xax)
        ymin, ymax = canvas.imageList.bounds.getRange(canvas.yax)

        # add a little padding to the lines if they are
        # on the boundary, so they don't get cropped
        xverts[:, canvas.xax] = canvas.pos.x
        yverts[:, canvas.yax] = canvas.pos.y 

        xverts[:, canvas.yax] = [ymin, ymax]
        xverts[:, canvas.zax] =  canvas.pos.z + 1
        yverts[:, canvas.xax] = [xmin, xmax]
        yverts[:, canvas.zax] =  canvas.pos.z + 1

        gl.glBegin(gl.GL_LINES)
        gl.glColor3f(0, 1, 0)
        gl.glVertex3f(*xverts[0])
        gl.glVertex3f(*xverts[1])
        gl.glVertex3f(*yverts[0])
        gl.glVertex3f(*yverts[1])
        gl.glEnd()

    canvas.SwapBuffers()