#!/usr/bin/env python
#
# imagelistpanel.py - A panel which displays a list of images in the image
# list.
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#
"""A panel which displays a list of image list in the image list (see
:class:fsl.data.fslimage.ImageList), and allows the user to add/remove
images, and to change their order.
"""

import logging
log = logging.getLogger(__name__)


import wx
import pwidgets.elistbox as elistbox


class ImageListPanel(wx.Panel):
    """A panel which contains an :class:`~pwidgets.EditableListBox` displaying
    the list of loaded images.
    
    The list box allows the image order to be changed, and allows images to be
    added and removed from the list.
    """
    
    def __init__(self, parent, imageList):
        """Create and lay out an :class:`ImageListPanel`.

        :param parent:    The :mod:`wx` parent object.
        :param imageList: A :class:`~fsl.data.fslimage.ImageList` instance.
        """
        
        wx.Panel.__init__(self, parent)
        self._imageList = imageList

        self._name = '{}_{}'.format(self.__class__.__name__, id(self))

        # list box containing the list of images - it 
        # is populated in the _imageListChanged method
        self._listBox = elistbox.EditableListBox(
            self,
            style=elistbox.ELB_REVERSE | elistbox.ELB_TOOLTIP)

        # listeners for when the user does
        # something with the list box
        self._listBox.Bind(elistbox.EVT_ELB_SELECT_EVENT, self._lbSelect)
        self._listBox.Bind(elistbox.EVT_ELB_MOVE_EVENT,   self._lbMove)
        self._listBox.Bind(elistbox.EVT_ELB_REMOVE_EVENT, self._lbRemove)
        self._listBox.Bind(elistbox.EVT_ELB_ADD_EVENT,    self._lbAdd)

        self._sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(self._sizer)

        self._sizer.Add(self._listBox, flag=wx.EXPAND, proportion=1)

        self._imageList.addListener(
            'images',
            self._name,
            self._imageListChanged)

        # This flag is set by the listbox listeners (bound above),
        # and read by the _imageListChanged, to ensure that user
        # actions on the list box do not trigger a list box refresh.
        self._listBoxNeedsUpdate = True

        self._imageListChanged()

        self.Layout()

        
    def _imageListChanged(self, *a):
        """Called when the :class:`~fsl.data.fslimage.ImageList.images`
        list changes.

        If the change was due to user action on the
        :class:`~pwidgets.EditableListBox`, this method does nothing.
        Otherwise, this method updates the :class:`~pwidgets.EditableListBox`
        """
        if not self._listBoxNeedsUpdate:
            return

        selection = self._listBox.GetSelection()
        self._listBox.Clear()

        for i in range(len(self._imageList)):

            image = self._imageList[i]

            self._listBox.Append(image.name, image, image.imageFile)

        self._listBox.SetSelection(selection)
        
        
    def _lbMove(self, ev):
        """Called when an image name is moved in the
        :class:`~pwidgets.elistbox.EditableListBox`. Reorders the
        :class:`~fsl.data.fslimage.ImageList` to reflect the change.
        """
        self._listBoxNeedsUpdate = False
        self._imageList.move(ev.oldIdx, ev.newIdx)
        self._listBoxNeedsUpdate = True

        
    def _lbSelect(self, ev):
        """Called when an image is selected in the
        :class:`~pwidgets.elistbox.EditableListBox`. Sets the
        :attr:`fsl.data.fslimage.ImageList.selectedImage property.
        """
        self._imageList.selectedImage = ev.idx

        
    def _lbAdd(self, ev):
        """Called when the 'add' button on the list box is pressed.
        Calls the :meth:`~fsl.data.fslimage.ImageList.addImages` method.
        """
        self._imageList.addImages()


    def _lbRemove(self, ev):
        """Called when an item is removed from the image listbox.

        Removes the corresponding image from the
        :class:`~fsl.data.fslimage.ImageList`. 
        """
        self._listBoxNeedsUpdate = False
        self._imageList.pop(ev.idx)
        self._listBoxNeedsUpdate = True