#!/usr/bin/env python
#
# lightboxcanvas.py - A wx.GLCanvas canvas which displays multiple slices
# along a single axis from a collection of 3D images.
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#

import wx

import numpy as np

import OpenGL.GL as gl

import fsl.fslview.slicecanvas as slicecanvas
import fsl.props               as props


class LightBoxCanvas(slicecanvas.SliceCanvas, props.HasProperties):


    # Properties which control the starting and end bounds of the
    # displayed slices, and the spacing between them (in real
    # world coordinates)
    sliceStart   = props.Double(clamped=True)
    sliceEnd     = props.Double(clamped=True)
    sliceSpacing = props.Double(clamped=True, minval=0.1, default=2.0)

    # This property controls the number of slices
    # to be displayed on a single row.
    ncols        = props.Int(   clamped=True, minval=1, maxval=15, default=5)

    _labels = {
        'sliceStart'   : 'First slice',
        'sliceEnd'     : 'Last slice',
        'sliceSpacing' : 'Slice spacing',
        'ncols'        : 'Number of columns'}


    _view = props.HGroup(('sliceStart', 'sliceEnd', 'sliceSpacing', 'ncols'))

    def __init__(self,
                 parent,
                 imageList,
                 zax,
                 context=None,
                 scrollbar=None):

        if (scrollbar is not None) and (not scrollbar.IsVertical()):
            raise RuntimeError('LightBoxCanvas only supports '
                               'a vertical scrollbar')

        slicecanvas.SliceCanvas.__init__(self, parent, imageList, zax, context)
        props.HasProperties.__init__(self)

        self._scrollbar = scrollbar

        # nrows is automatically calculated 
        # in the _imageListChangd method -
        # the value 0 is just a placeholder
        self._nrows = 0

        if scrollbar is not None:
            scrollbar.Bind(wx.EVT_SCROLL, self._draw)

        def propChanged(*a):
            self._genSliceLocations()
            self._refresh()

        self.addListener('sliceStart',   self.name, propChanged)
        self.addListener('sliceEnd',     self.name, propChanged)
        self.addListener('sliceSpacing', self.name, propChanged)
        self.addListener('ncols',        self.name, propChanged)


    def _imageListChanged(self):
        """
        Called when the list of displayed images changes. Calls
        SliceCanvas._imageListChanged (which recalculates the
        bounds of all images in the list), then calls
        _genSliceLocations
        """

        # recalculate image bounds, and create
        # GL data for any newly added images.
        slicecanvas.SliceCanvas._imageListChanged(self)

        zmin = self.imageList.minBounds[self.zax]
        zmax = self.imageList.maxBounds[self.zax]
        
        # update bounds on the slice start/end properties
        self.setConstraint('sliceStart', 'minval', zmin)
        self.setConstraint('sliceStart', 'maxval', zmax)
        self.setConstraint('sliceEnd',   'minval', zmin)
        self.setConstraint('sliceEnd',   'maxval', zmax)

        # I'm assuming here that if both the start and end
        # locations are 0, they need initialising. Or the
        # user is just weird.
        if self.sliceStart == 0.0 and self.sliceEnd == 0.0:
            self.sliceStart = zmin
            self.sliceEnd   = zmax

        self._genSliceLocations()
        


    def _genSliceLocations(self):
        """
        Called when the image list changes, or when any of the slice
        display properties change. For every image in the image list,
        generates a list of transformation matrices, and a list of
        slice indices. The latter specifies the slice indices from
        the image to be displayed, and the former specifies the
        transformation matrix to be used to position the slice on the
        canvas.        
        """
        
        # calculate the locations, in real world coordinates,
        # of all slices to be displayed on the canvas
        sliceLocs = np.arange(
            self.sliceStart,
            self.sliceEnd + self.sliceSpacing,
            self.sliceSpacing)

        self._nslices = len(sliceLocs)
        self._nrows   = int(np.ceil(self._nslices / float(self.ncols)))
        
        self._sliceIdxs  = []
        self._transforms = []

        # calculate the transformation for each
        # slice in each image, and the index of
        # each slice to be displayed
        for i, image in enumerate(self.imageList):
            
            self._transforms.append([])
            self._sliceIdxs .append([])

            for zi, zpos in enumerate(sliceLocs):

                imgZi = image.worldToVox(zpos, self.zax)
                xform = self._calculateSliceTransform(image, zi)

                self._transforms[-1].append(xform)
                self._sliceIdxs[ -1].append(imgZi)

        # update the scrollbar (if there is one),
        # as the image bounds and hence the number
        # of slices may have changed
        self._updateScrollBar()


    def _calculateSliceTransform(self, image, sliceno):
        """
        Calculates a transformation matrix for the given slice
        number. Each slice is displayed on the same canvas, but
        is translated to a specific row/column. So a copy of
        the voxToWorld transformation matrix of the given image
        is made, and a translation applied to it, to position
        the slice in the correct location on the canvas.
        """

        nrows = self._nrows
        ncols = self.ncols

        xform = np.array(image.voxToWorldMat, dtype=np.float32)

        row = nrows - int(np.floor(sliceno / ncols)) - 1
        col = int(np.floor(sliceno % ncols))

        xlen = abs(self.xmax - self.xmin)
        ylen = abs(self.ymax - self.ymin)

        translate              = np.identity(4, dtype=np.float32)
        translate[3, self.xax] = xlen * col
        translate[3, self.yax] = ylen * row
        translate[3, self.zax] = 0
        
        return xform.dot(translate)


    def _updateScrollBar(self):
        """
        If a scroll bar was passed in when this LightBoxCanvas was created,
        this method updates it to reflect the current state of the canvas
        size and the displayed list of images.
        """
        
        if self._scrollbar is None: return
        
        if len(self.imageList) == 0:
            self._scrollbar.SetScrollbar(0, 99, 1, 99, True)
            return

        screenSize = self.GetClientSize()
        sliceRatio = abs(self.xmax - self.xmin) / abs(self.ymax - self.ymin)
        
        sliceWidth   = screenSize.width / float(self.ncols)
        sliceHeight  = sliceWidth * sliceRatio
        
        rowsOnScreen = int(np.floor(screenSize.height / sliceHeight))
        oldPos       = self._scrollbar.GetThumbPosition()

        if rowsOnScreen == 0:
            rowsOnScreen = 1

        self._scrollbar.SetScrollbar(oldPos,
                                     rowsOnScreen,
                                     self._nrows,
                                     rowsOnScreen,
                                     True)


    def _calculateCanvasBBox(self, ev):
        """
        Calculates the bounding box for slices to be displayed
        on the canvas, such that their aspect ratio is maintained.
        """

        # _calculateCanvasBBox is called on window resizes.
        # We also want the scroll bar to be updated when
        # the window size changes, so there you go.
        self._updateScrollBar()

        worldSliceWidth  = float(abs(self.xmax - self.xmin))
        worldSliceHeight = float(abs(self.ymax - self.ymin))

        # If there's no scrollbar, we display
        # all the slices on the screen
        if self._scrollbar is not None:
            rowsOnScreen = self._scrollbar.GetPageSize()
            worldWidth   = worldSliceWidth  * self.ncols
            worldHeight  = worldSliceHeight * rowsOnScreen

        else:
            worldWidth   = worldSliceWidth  * self.ncols
            worldHeight  = worldSliceHeight * self._nrows

        slicecanvas.SliceCanvas._calculateCanvasBBox(self,
                                                     ev,
                                                     worldWidth=worldWidth,
                                                     worldHeight=worldHeight)


    def _resize(self):
        """
        Sets up the GL canvas size, viewport and projection.
        """

        xlen = abs(self.xmax - self.xmin)
        ylen = abs(self.ymax - self.ymin)        

        worldYMin  = None
        worldXMax  = self.xmin + xlen * self.ncols
        worldYMax  = self.ymin + ylen * self._nrows

        if self._scrollbar is not None:

            rowsOnScreen = self._scrollbar.GetPageSize()
            currentRow   = self._scrollbar.GetThumbPosition()
            currentRow   = self._nrows - currentRow - rowsOnScreen

            worldYMin = self.ymin + ylen * currentRow
            worldYMax = worldYMin + ylen * rowsOnScreen

        slicecanvas.SliceCanvas._resize(self,
                                        xmax=worldXMax,
                                        ymin=worldYMin,
                                        ymax=worldYMax)

        
    def _draw(self, ev):
        """
        Draws the currently visible slices to the canvas.
        """

        # image data has not been initialised.
        if not self.glReady:
            wx.CallAfter(self._initGLData)
            return

        # No scrollbar -> draw all the slices 
        if self._scrollbar is None:
            startSlice = 0
            endSlice   = self._nslices

        # Scrollbar -> draw a selection of slices
        else:
            rowsOnScreen = self._scrollbar.GetPageSize()
            startRow     = self._scrollbar.GetThumbPosition()
            
            startSlice   = self.ncols * startRow
            endSlice     = startSlice + rowsOnScreen * self.ncols

            if endSlice > self._nslices:
                endSlice = self._nslices

        self.context.SetCurrent(self)
        self._resize()

        # clear the canvas
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

        # load the shaders
        gl.glUseProgram(self.shaders)

        # enable transparency
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

        # disable interpolation
        gl.glShadeModel(gl.GL_FLAT)

        # Draw all the slices for all the images.
        for i, image in enumerate(self.imageList):
            for zi in range(startSlice, endSlice):
                self._drawSlice(image,
                                self._sliceIdxs[ i][zi],
                                self._transforms[i][zi]) 

        gl.glUseProgram(0)

        self.SwapBuffers()


class LightBoxPanel(wx.Panel):
    """
    Convenience Panel which contains a a LightBoxCanvas and a scrollbar,
    and sets up mouse-scrolling behaviour.
    """

    def __init__(self, parent, *args, **kwargs):
        """
        Accepts the same parameters as the LightBoxCanvas constructor,
        although if you pass in a scrollbar, it will be ignored.
        """

        wx.Panel.__init__(self, parent)

        self.scrollbar = wx.ScrollBar(self, style=wx.SB_VERTICAL)
        
        kwargs['scrollbar'] = self.scrollbar
        
        self.canvas = LightBoxCanvas(self, *args, **kwargs)

        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(self.sizer)

        self.sizer.Add(self.canvas,    flag=wx.EXPAND, proportion=1)
        self.sizer.Add(self.scrollbar, flag=wx.EXPAND)

        def scrollOnMouse(ev):

            wheelDir = ev.GetWheelRotation()

            if   wheelDir > 0: wheelDir = -1
            elif wheelDir < 0: wheelDir =  1

            curPos = self.scrollbar.GetThumbPosition()
            self.scrollbar.SetThumbPosition(curPos + wheelDir)
            self.canvas._draw(None)

        self.Bind(wx.EVT_MOUSEWHEEL, scrollOnMouse)

        self.Layout()        


class LightBoxFrame(wx.Frame):
    """
    Convenience class for displaying a LightBoxPanel in a standalone window.
    """

    def __init__(self, parent, imageList, title=None):

        wx.Frame.__init__(self, parent, title=title)

        import fsl.fslview.imagelistpanel as imagelistpanel

        self.listPanel = imagelistpanel.ImageListPanel(self, imageList)
        self.mainPanel = LightBoxPanel(self, imageList, zax=1)
        self.ctrlPanel = props.buildGUI(self, self.mainPanel.canvas)

        self.sizer = wx.BoxSizer(wx.VERTICAL)

        self.sizer.Add(self.ctrlPanel, flag=wx.EXPAND)
        self.sizer.Add(self.mainPanel, flag=wx.EXPAND, proportion=1)
        self.sizer.Add(self.listPanel, flag=wx.EXPAND)

        self.SetSizer(self.sizer)
        self.Layout()


if __name__ == '__main__':

    import sys
    import fsl.data.fslimage as fslimage

    files = sys.argv[1:]
    # files = ['/Users/paulmc/MNI152_T1_2mm.nii']

    imgs    = map(fslimage.Image, files)
    imgList = fslimage.ImageList(imgs)
    app     = wx.App()
    oframe  = LightBoxFrame(None, imgList, "Test")
    
    oframe.Show()



    # import wx.lib.inspection
    # wx.lib.inspection.InspectionTool().Show()    
    app.MainLoop()
