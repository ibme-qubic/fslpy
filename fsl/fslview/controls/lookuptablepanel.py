#!/usr/bin/env python
#
# lookuptablepanel.py -
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#

import logging

import wx

import numpy as np

import props

import pwidgets.elistbox          as elistbox

import fsl.fslview.panel          as fslpanel
import fsl.fslview.displaycontext as fsldisplay
import fsl.data.strings           as strings


log = logging.getLogger(__name__)




class LabelWidget(wx.Panel):
    
    def __init__(self, lutPanel, overlayOpts, lut, value):
        wx.Panel.__init__(self, lutPanel)

        self.lutPanel = lutPanel
        self.opts     = overlayOpts
        self.lut      = lut
        self.value    = value

        # TODO Change the enable box to a toggle
        #      button with an eye icon
        
        self.valueLabel   = wx.StaticText(self,
                                          style=wx.ALIGN_CENTRE_VERTICAL |
                                                wx.ALIGN_RIGHT)
        self.enableBox    = wx.CheckBox(self)
        self.colourButton = wx.ColourPickerCtrl(self)

        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(self.sizer)
        self.sizer.Add(self.valueLabel,   flag=wx.ALIGN_CENTRE, proportion=1)
        self.sizer.Add(self.enableBox,    flag=wx.ALIGN_CENTRE, proportion=1)
        self.sizer.Add(self.colourButton, flag=wx.ALIGN_CENTRE, proportion=1)

        label  = lut.get(value)
        colour = [np.floor(c * 255.0) for c in label.colour()]

        self.valueLabel  .SetLabel(str(value))
        self.colourButton.SetColour(colour)
        self.enableBox   .SetValue(label.enabled())

        self.enableBox   .Bind(wx.EVT_CHECKBOX,             self.__onEnable)
        self.colourButton.Bind(wx.EVT_COLOURPICKER_CHANGED, self.__onColour)

        
    def __onEnable(self, ev):

        # Disable the LutPanel listener, otherwise
        # it will recreate the label list (see
        # LookupTablePanel._initLabelList)
        self.lut.disableListener('labels', self.lutPanel._name)
        self.lut.set(self.value, enabled=self.enableBox.GetValue())
        self.lut.enableListener('labels', self.lutPanel._name)

        
    def __onColour(self, ev):

        newColour = self.colourButton.GetColour()
        newColour = [c / 255.0 for c in newColour]

        self.lut.disableListener('labels', self.lutPanel._name)
        self.lut.set(self.value, colour=newColour)
        self.lut.enableListener('labels', self.lutPanel._name)


class LookupTablePanel(fslpanel.FSLViewPanel):

    def __init__(self, parent, overlayList, displayCtx):

        fslpanel.FSLViewPanel.__init__(self, parent, overlayList, displayCtx)

        # If non-lut image is shown, just show a message

        # Overlay name
        # Change lookup table
        # Add label
        # New lut
        # Copy lut
        # Save lut
        # Load lut

        self.__controlRow = wx.Panel(self)

        self.__disabledLabel = wx.StaticText(self,
                                             style=wx.ALIGN_CENTER_VERTICAL |
                                                   wx.ALIGN_CENTER_HORIZONTAL)
        self.__labelList     = elistbox.EditableListBox(
            self,
            style=elistbox.ELB_NO_MOVE | elistbox.ELB_EDITABLE)

        self.__overlayNameLabel = wx.StaticText(self,
                                                style=wx.ST_ELLIPSIZE_MIDDLE)

        self.__lutWidget        = None
        self.__newLutButton     = wx.Button(self.__controlRow)
        self.__copyLutButton    = wx.Button(self.__controlRow)
        self.__saveLutButton    = wx.Button(self.__controlRow)
        self.__loadLutButton    = wx.Button(self.__controlRow)

        self.__controlRowSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.__sizer           = wx.BoxSizer(wx.VERTICAL)

        self.__controlRow.SetSizer(self.__controlRowSizer)
        self             .SetSizer(self.__sizer)

        self.__controlRowSizer.Add(self.__newLutButton,
                                   flag=wx.EXPAND, proportion=1)
        self.__controlRowSizer.Add(self.__copyLutButton,
                                   flag=wx.EXPAND, proportion=1) 
        self.__controlRowSizer.Add(self.__loadLutButton,
                                   flag=wx.EXPAND, proportion=1)
        self.__controlRowSizer.Add(self.__saveLutButton,
                                   flag=wx.EXPAND, proportion=1)

        self.__sizer.Add(self.__overlayNameLabel, flag=wx.EXPAND)
        self.__sizer.Add(self.__controlRow,       flag=wx.EXPAND)
        self.__sizer.Add(self.__disabledLabel,    flag=wx.EXPAND, proportion=1)
        self.__sizer.Add(self.__labelList,        flag=wx.EXPAND, proportion=1)

        # Label the labels and buttons
        self.__disabledLabel.SetLabel(strings.messages[self, 'notLutOverlay'])
        self.__newLutButton .SetLabel(strings.labels[  self, 'newLut'])
        self.__copyLutButton.SetLabel(strings.labels[  self, 'copyLut'])
        self.__loadLutButton.SetLabel(strings.labels[  self, 'loadLut'])
        self.__saveLutButton.SetLabel(strings.labels[  self, 'saveLut'])

        # Make the label name a bit smaller
        font = self.__overlayNameLabel.GetFont()
        font.SetPointSize(font.GetPointSize() - 2)
        font.SetWeight(wx.FONTWEIGHT_LIGHT)
        self.__overlayNameLabel.SetFont(font)

        # Listen for listbox events
        self.__labelList.Bind(elistbox.EVT_ELB_ADD_EVENT,
                              self.__onLabelAdd)
        self.__labelList.Bind(elistbox.EVT_ELB_REMOVE_EVENT,
                              self.__onLabelRemove)
        self.__labelList.Bind(elistbox.EVT_ELB_EDIT_EVENT,
                              self.__onLabelEdit)

        self.__newLutButton .Bind(wx.EVT_BUTTON, self.__onNewLut)
        self.__copyLutButton.Bind(wx.EVT_BUTTON, self.__onCopyLut)
        self.__loadLutButton.Bind(wx.EVT_BUTTON, self.__onLoadLut)
        self.__saveLutButton.Bind(wx.EVT_BUTTON, self.__onSaveLut)

        self.__selectedOverlay = None
        self.__selectedOpts    = None
        self.__selectedLut     = None

        overlayList.addListener('overlays',
                                self._name,
                                self.__selectedOverlayChanged)
        displayCtx .addListener('selectedOverlay',
                                self._name,
                                self.__selectedOverlayChanged)

        self.__selectedOverlayChanged()

        
    def destroy(self):

        self._overlayList.removeListener('overlays',        self._name)
        self._displayCtx .removeListener('selectedOverlay', self._name)

        overlay = self.__selectedOverlay
        opts    = self.__selectedOpts
        lut     = self.__selectedLut

        if overlay is not None:

            display = self._displayCtx.getDisplay(overlay)

            display.removeListener('name',        self._name)
            display.removeListener('overlayType', self._name)

        if opts is not None:
            opts.removeListener('lut', self._name)

        if lut is not None:
            lut.removeListener('labels', self._name)
            lut.removeListener('saved',  self._name)
    

    def __selectedOverlayChanged(self, *a):

        newOverlay = self._displayCtx.getSelectedOverlay()

        if self.__selectedOverlay == newOverlay:
            return

        if self.__selectedOverlay is not None:
            
            display = self._displayCtx.getDisplay(self.__selectedOverlay)
            
            display.removeListener('name',        self._name)
            display.removeListener('overlayType', self._name)

        self.__selectedOverlay = newOverlay

        if newOverlay is not None:
            display = self._displayCtx.getDisplay(newOverlay)
            display.addListener('name',
                                self._name,
                                self.__overlayNameChanged)
            display.addListener('overlayType',
                                self._name,
                                self.__overlayTypeChanged)

        self.__overlayNameChanged()
        self.__overlayTypeChanged()


    def __overlayNameChanged(self, *a):

        overlay = self.__selectedOverlay

        if overlay is None:
            self.__overlayNameLabel.SetLabel('')
            return

        display = self._displayCtx.getDisplay(overlay)

        self.__overlayNameLabel.SetLabel(display.name)
        

    def __overlayTypeChanged(self, *a):

        if self.__lutWidget is not None:
            self.__controlRowSizer.Detach(self.__lutWidget)
            self.__lutWidget.Destroy()
            self.__lutWidget = None

        if self.__selectedOpts is not None:
            self.__selectedOpts.removeListener('lut', self._name)
            self.__selectedOpts = None

        overlay = self.__selectedOverlay
        enabled = False

        if overlay is not None:
            opts = self._displayCtx.getOpts(overlay)

            if isinstance(opts, fsldisplay.LabelOpts):
                enabled = True

        self.__overlayNameLabel.Show(    enabled)
        self.__controlRow      .Show(    enabled)
        self.__labelList       .Show(    enabled)
        self.__disabledLabel   .Show(not enabled)

        if not enabled:
            self.Layout()
            return

        opts = self._displayCtx.getOpts(overlay)

        opts.addListener('lut', self._name, self.__lutChanged)
        
        self.__selectedOpts = opts
        self.__lutWidget    = props.makeWidget(
            self.__controlRow, opts, 'lut')

        self.__controlRowSizer.Insert(
            0, self.__lutWidget, flag=wx.EXPAND, proportion=1)

        self.__lutChanged()

        self.Layout()


    def __lutChanged(self, *a):

        if self.__selectedLut is not None:
            self.__selectedLut.removeListener('labels', self._name)
            self.__selectedLut.removeListener('saved',  self._name)
            self.__selecedLut = None

        opts = self.__selectedOpts

        if opts is not None:
            self.__selectedLut = opts.lut

            self.__selectedLut.addListener(
                'labels', self._name, self.__initLabelList)
            self.__selectedLut.addListener(
                'saved', self._name, self.__lutSaveStateChanged) 

        self.__initLabelList()
        self.__lutSaveStateChanged()

        
    def __lutSaveStateChanged(self, *a):
        self.__saveLutButton.Enable(not self.__selectedLut.saved)

        
    def __initLabelList(self, *a):

        self.__labelList.Clear()

        if self.__selectedOpts is None:
            return

        opts = self.__selectedOpts
        lut  = opts.lut

        for i, label in enumerate(lut.labels):

            self.__labelList.Append(label.name())

            widget = LabelWidget(self, opts, lut, label.value())
            self.__labelList.SetItemWidget(i, widget)


    def __onNewLut(self, ev):
        pass


    def __onCopyLut(self, ev):
        pass

    
    def __onLoadLut(self, ev):
        pass

    
    def __onSaveLut(self, ev):
        pass 

    
    def __onLabelAdd(self, ev):

        dlg = LutLabelDialog(self.GetTopLevelParent())
        if dlg.ShowModal() != wx.ID_OK:
            return

        opts   = self.__selectedOpts
        value  = dlg.value
        name   = dlg.name
        colour = dlg.colour[:3]
        colour = [c / 255.0 for c in colour]

        if opts.lut.get(value) is not None:
            wx.MessageBox(
                strings.messages[self, 'labelExists'].format(
                    opts.lut.name, value),
                strings.titles[  self, 'labelExists'],
                wx.ICON_INFORMATION | wx.OK)
            return

        log.debug('New lut label for {}: {}, {}, {}'.format(
            opts.lut.name,
            value,
            name,
            colour))

        opts.lut.set(value, name=name, colour=colour)

    
    def __onLabelRemove(self, ev):

        opts  = self.__selectedOpts
        value = opts.lut.labels[ev.idx].value()

        self.__selectedLut.disableListener('labels', self._name)
        opts.lut.delete(value)
        self.__selectedLut.enableListener('labels', self._name)


    def __onLabelEdit(self, ev):

        opts  = self.__selectedOpts
        value = opts.lut.labels[ev.idx].value()

        self.__selectedLut.disableListener('labels', self._name)
        opts.lut.set(value, name=ev.label)
        self.__selectedLut.enableListener('labels', self._name)


class LutLabelDialog(wx.Dialog):

    def __init__(self, parent):

        wx.Dialog.__init__(self, parent, title=strings.titles[self])

        self._value  = wx.SpinCtrl(        self)
        self._name   = wx.TextCtrl(        self)
        self._colour = wx.ColourPickerCtrl(self)

        self._valueLabel  = wx.StaticText(self)
        self._nameLabel   = wx.StaticText(self)
        self._colourLabel = wx.StaticText(self)

        self._ok     = wx.Button(self)
        self._cancel = wx.Button(self)

        self._valueLabel .SetLabel(strings.labels[self, 'value'])
        self._nameLabel  .SetLabel(strings.labels[self, 'name'])
        self._colourLabel.SetLabel(strings.labels[self, 'colour'])
        self._ok         .SetLabel(strings.labels[self, 'ok'])
        self._cancel     .SetLabel(strings.labels[self, 'cancel'])

        self._value.SetValue(0)
        self._name .SetValue('New label')

        self._sizer = wx.GridSizer(4, 2)
        self.SetSizer(self._sizer)

        self._sizer.Add(self._valueLabel,  flag=wx.EXPAND)
        self._sizer.Add(self._value,       flag=wx.EXPAND)
        self._sizer.Add(self._nameLabel,   flag=wx.EXPAND)
        self._sizer.Add(self._name,        flag=wx.EXPAND)
        self._sizer.Add(self._colourLabel, flag=wx.EXPAND)
        self._sizer.Add(self._colour,      flag=wx.EXPAND)
        self._sizer.Add(self._ok,          flag=wx.EXPAND)
        self._sizer.Add(self._cancel,      flag=wx.EXPAND)

        self._ok    .Bind(wx.EVT_BUTTON, self.onOk)
        self._cancel.Bind(wx.EVT_BUTTON, self.onCancel)

        self.Fit()
        self.Layout()

        self.CentreOnParent()

        self.value  = None
        self.name   = None
        self.colour = None


    def onOk(self, ev):
        self.value  = self._value .GetValue()
        self.name   = self._name  .GetValue()
        self.colour = self._colour.GetColour()

        self.EndModal(wx.ID_OK)


    def onCancel(self, ev):
        self.EndModal(wx.ID_CANCEL)
