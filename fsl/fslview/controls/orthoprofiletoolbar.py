#!/usr/bin/env python
#
# orthoprofiletoolbar.py -
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#

import logging

import props

import fsl.fslview.panel   as fslpanel
import fsl.fslview.actions as actions
import fsl.data.strings    as strings


log = logging.getLogger(__name__)


class OrthoProfileToolBar(fslpanel.FSLViewToolBar):

    def __init__(self, parent, imageList, displayCtx, ortho):
        fslpanel.FSLViewToolBar.__init__(self, parent, imageList, displayCtx)

        self.orthoPanel = ortho

        ortho.addListener('profile', self._name, self._profileChanged)

        self.profileTool = props.makeWidget(self, ortho, 'profile')
        self.AddTool(self.profileTool, strings.properties[ortho, 'profile'])

        self._profileChanged()


    def destroy(self):
        fslpanel.FSLViewToolBar.destroy(self)
        self.orthoPanel.removeListener('profile', self._name)


    def _profileChanged(self, *a):

        import fsl.fslview.layouts as layouts

        profile       = self.orthoPanel.profile
        tools, labels = self._makeProfileTools(layouts.layouts[self, profile])

        self.ClearTools(destroy=True, startIdx=1)
        self.InsertTools(tools, labels, 1)

        
    def _makeProfileTools(self, toolSpecs):
            
        profile = self.orthoPanel.getCurrentProfile()

        tools  = []
        labels = []

        for toolSpec in toolSpecs:

            tool = props.buildGUI(self, profile, toolSpec)
            
            tools.append(tool)

            if isinstance(toolSpec, actions.ActionButton):
                labels.append(None)
            else:
                labels.append(strings.properties[profile, toolSpec.key])

        return tools, labels
