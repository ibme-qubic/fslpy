#!/usr/bin/env python
#
# strings.py -
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#

from fsl.utils.typedict import TypeDict
import fsl.data.constants as constants

messages = TypeDict({

    'FSLDirDialog.FSLDirNotSet'    : 'The $FSLDIR environment variable '
                                     'is not set - \n{} may not behave '
                                     'correctly.',
    'FSLDirDialog.selectFSLDir'    : 'Select the directory in which '
                                     'FSL is installed',

    'fslview.loading'              : 'Loading {}',
    'FSLViewSplash.default'        : 'Loading ...',

    'image.saveImage.error'      : 'An error occurred saving the file. '
                                   'Details: {}',
    
    'image.loadImage.decompress' : '{} is a large file ({} MB) - '
                                   'decompressing to {}, to allow memory '
                                   'mapping...',

    'ProcessingDialog.error' : 'An error has occurred: {}'
                               '\n\nDetails: {}',

    'overlay.loadOverlays.loading'     : 'Loading {} ...',
    'overlay.loadOverlays.error'       : 'An error occurred loading the image '
                                         '{}\n\nDetails: {}',

    'overlay.loadOverlays.unknownType' : 'Unknown data type',

    'actions.loadcolourmap.loadcmap'    : 'Open colour map file',
    'actions.loadcolourmap.namecmap'    : 'Enter a name for the colour map - '
                                          'please use only letters, numbers, '
                                          'and underscores.',
    'actions.loadcolourmap.installcmap' : 'Do you want to install '
                                          'this colour map permanently?',
    'actions.loadcolourmap.alreadyinstalled' : 'A colour map with that name '
                                               'already exists - choose a '
                                               'different name.',
    'actions.loadcolourmap.invalidname'      : 'Please use only letters, '
                                               'numbers, and underscores.',
    'actions.loadcolourmap.installerror'     : 'An error occurred while '
                                               'installing the colour map',

    'AtlasOverlayPanel.loadRegions' : 'Loading region descriptions for {} ...',

    'AtlasInfoPanel.notMNISpace'   : 'Atlas lookup can only be performed on '
                                     'images oriented to MNI152 space',

    'AtlasInfoPanel.noReference' : 'No reference image available',

    'AtlasInfoPanel.chooseAnAtlas' : 'Choose an atlas!',
    'AtlasInfoPanel.atlasDisabled' : 'Atlases are not available',

    'CanvasPanel.screenshot'            : 'Save screenshot',
    'CanvasPanel.screenshot.notSaved'   : 'Overlay {} needs saving before a '
                                          'screenshot can be taken.',
    'CanvasPanel.screenshot.pleaseWait' : 'Saving screenshot - '
                                          'please wait ...',
    'CanvasPanel.screenshot.error'      : 'Sorry, there was an error '
                                          'saving the screenshot. Try '
                                          'calling render directly with '
                                          'this command: \n{}',

    'CanvasPanel.showCommandLineArgs.title'   : 'Scene parameters',
    'CanvasPanel.showCommandLineArgs.message' : 'Use these parameters on the '
                                                'command line to recreate '
                                                'the current scene',

    'PlotPanel.screenshot'              : 'Save screenshot',

    'PlotPanel.screenshot.error'       : 'An error occurred while saving the '
                                         'screenshot.\n\n'
                                         'Details: {}',

    'HistogramPanel.calcHist'           : 'Calculating histogram for {} ...',


    'LookupTablePanel.notLutOverlay' : 'Choose an overlay which '
                                       'uses a lookup table',

    'LookupTablePanel.labelExists' : 'The {} LUT already contains a '
                                     'label with value {}',

    'NewLutDialog.newLut' : 'Enter a name for the new LUT',

    'ClusterPanel.noOverlays'     : 'Add a FEAT overlay',
    'ClusterPanel.notFEAT'        : 'Choose a FEAT overlay',
    'ClusterPanel.noClusters'     : 'No cluster results exist '
                                    'in this FEAT analysis',
    'ClusterPanel.badData'        : 'Cluster data could not be parsed - '
                                    'check your cluster_*.txt files.',
    'ClusterPanel.loadingCluster' : 'Loading data for cluster {} ...',
})



titles = TypeDict({

    'FSLDirDialog'           : '$FSLDIR is not set',
    
    'image.saveImage.dialog' : 'Save image file',

    'ProcessingDialog.error' : 'Error',
    
    'overlay.addOverlays.dialog' : 'Open overlay files',
    
    'overlay.loadOverlays.error'  : 'Error loading overlay',

    'OrthoPanel'      : 'Ortho View',
    'LightBoxPanel'   : 'Lightbox View',
    'TimeSeriesPanel' : 'Time series',
    'HistogramPanel'  : 'Histogram',

    'CanvasPanel.screenshot'          : 'Save screenshot',
    'CanvasPanel.screenshot.notSaved' : 'Save overlay before continuing',
    'CanvasPanel.screenshot.error'    : 'Error saving screenshot',

    'PlotPanel.screenshot.error'      : 'Error saving screenshot',

    'AtlasInfoPanel'      : 'Atlas information',
    'AtlasOverlayPanel'   : 'Atlas overlays',

    'OverlayListPanel'       : 'Overlay list',
    'AtlasPanel'             : 'Atlases',
    'LocationPanel'          : 'Location',
    'OverlayDisplayToolBar'  : 'Display toolbar',
    'CanvasSettingsPanel'    : 'View settings',
    'OverlayDisplayPanel'    : 'Display settings',
    'OrthoToolBar'           : 'Ortho view toolbar',
    'OrthoProfileToolBar'    : 'Ortho view mode toolbar',
    'LightBoxToolBar'        : 'Lightbox view toolbar',
    'LookupTablePanel'       : 'Lookup tables',
    'LutLabelDialog'         : 'New LUT label',
    'NewLutDialog'           : 'New LUT',
    'TimeSeriesListPanel'    : 'Time series list',
    'TimeSeriesControlPanel' : 'Time series control',
    'HistogramListPanel'     : 'Histogram list',
    'HistogramControlPanel'  : 'Histogram control',
    'ClusterPanel'           : 'Cluster browser',
    'OverlayInfoPanel'       : 'Overlay information',

    'LookupTablePanel.loadLut'     : 'Select a lookup table file',
    'LookupTablePanel.labelExists' : 'Label already exists',
})


actions = TypeDict({

    'OpenFileAction'      : 'Add overlay file',
    'OpenStandardAction'  : 'Add standard',
    'CopyOverlayAction'   : 'Copy overlay',
    'SaveOverlayAction'   : 'Save overlay',
    'LoadColourMapAction' : 'Load custom colour map',

    'FSLViewFrame.closeViewPanel' : 'Close',

    'CanvasPanel.screenshot'              : 'Take screenshot',
    'CanvasPanel.showCommandLineArgs'     : 'Show command line for scene',
    'CanvasPanel.toggleColourBar'         : 'Colour bar',
    'CanvasPanel.toggleOverlayList'       : 'Overlay list',
    'CanvasPanel.toggleDisplayProperties' : 'Overlay display properties',
    'CanvasPanel.toggleLocationPanel'     : 'Location panel',
    'CanvasPanel.toggleAtlasPanel'        : 'Atlas panel',
    'CanvasPanel.toggleLookupTablePanel'  : 'Lookup tables',
    'CanvasPanel.toggleClusterPanel'      : 'Cluster browser',
    'CanvasPanel.toggleOverlayInfo'       : 'Overlay information',
    
    'OrthoPanel.toggleOrthoToolBar'     : 'View properties',
    'OrthoPanel.toggleProfileToolBar'   : 'Mode controls',

    'OrthoToolBar.more'           : 'More settings',
    'LightBoxToolBar.more'        : 'More settings',
    'OverlayDisplayToolBar.more'  : 'More settings',
    
    'LightBoxPanel.toggleLightBoxToolBar' : 'View properties',

    'PlotPanel.screenshot'                    : 'Take screenshot',
    'TimeSeriesPanel.toggleTimeSeriesList'    : 'Time series list',
    'TimeSeriesPanel.toggleTimeSeriesControl' : 'Time series control', 
    'HistogramPanel.toggleHistogramList'      : 'Histogram list',
    'HistogramPanel.toggleHistogramControl'   : 'Histogram control', 

    'OrthoViewProfile.centreCursor' : 'Centre cursor',
    'OrthoViewProfile.resetZoom'    : 'Reset zoom',


    'OrthoEditProfile.undo'                    : 'Undo',
    'OrthoEditProfile.redo'                    : 'Redo',
    'OrthoEditProfile.fillSelection'           : 'Fill',
    'OrthoEditProfile.clearSelection'          : 'Clear',
    'OrthoEditProfile.createMaskFromSelection' : 'Mask',
    'OrthoEditProfile.createROIFromSelection'  : 'ROI',
})

labels = TypeDict({

    'FSLDirDialog.locate' : 'Locate $FSLDIR',
    'FSLDirDialog.skip'   : 'Skip',
    
    'LocationPanel.worldLocation'         : 'Coordinates: ',
    'LocationPanel.worldLocation.unknown' : 'Unknown',
    'LocationPanel.voxelLocation'         : 'Voxel location',
    'LocationPanel.volume'                : 'Volume',
    'LocationPanel.noData'                : 'No data',
    'LocationPanel.outOfBounds'           : 'Out of bounds',
    'LocationPanel.notAvailable'          : 'N/A',

    'CanvasPanel.screenshot.notSaved.save'   : 'Save overlay now',
    'CanvasPanel.screenshot.notSaved.skip'   : 'Skip overlay (will not appear '
                                               'in screenshot)',
    'CanvasPanel.screenshot.notSaved.cancel' : 'Cancel screenshot',


    'LookupTablePanel.addLabel' : 'Add label',
    'LookupTablePanel.newLut'   : 'New',
    'LookupTablePanel.copyLut'  : 'Copy',
    'LookupTablePanel.saveLut'  : 'Save',
    'LookupTablePanel.loadLut'  : 'Load',

    'LutLabelDialog.value'    : 'Value',
    'LutLabelDialog.name'     : 'Name',
    'LutLabelDialog.colour'   : 'Colour',
    'LutLabelDialog.ok'       : 'Ok',
    'LutLabelDialog.cancel'   : 'Cancel',
    'LutLabelDialog.newLabel' : 'New label',

    'NewLutDialog.ok'     : 'Ok',
    'NewLutDialog.cancel' : 'Cancel',
    'NewLutDialog.newLut' : 'New LUT',

    'PlotPanel.plotSettings'    : 'General plot settings',
    'PlotPanel.currentSettings' : 'Settings for currently '
                                  'selected plot ({})',
    'PlotPanel.xlim'            : 'X limits',
    'PlotPanel.ylim'            : 'Y limits',
    'PlotPanel.labels'          : 'Labels',
    'PlotPanel.xlabel'          : 'X',
    'PlotPanel.ylabel'          : 'Y',

    'HistogramControlPanel.histSettings'        : 'Histogram plot settings',

    'TimeSeriesControlPanel.tsSettings'         : 'Time series plot settings',
    'TimeSeriesControlPanel.currentSettings'    : 'Settings for current '
                                                  'voxel time course',
    'TimeSeriesControlPanel.currentFEATSettings' : 'FEAT settings for '
                                                   'selected overlay ({})',

    'TimeSeriesListPanel.featReduced' : 'Reduced against {}',

    'FEATModelFitTimeSeries.full' : 'Full model fit',
    'FEATModelFitTimeSeries.cope' : 'COPE{} fit: {}',
    'FEATModelFitTimeSeries.pe'   : 'PE{} fit',

    'FEATReducedTimeSeries.cope' : 'Reduced against COPE{}: {}',
    'FEATReducedTimeSeries.pe'   : 'Reduced against PE{}',

    'FEATResidualTimeSeries'     : 'Residuals',

    'ClusterPanel.clustName'     : 'Z statistics for COPE{} ({})',
    
    'ClusterPanel.index'         : 'Cluster index',
    'ClusterPanel.nvoxels'       : 'Size (voxels)',
    'ClusterPanel.p'             : 'P',
    'ClusterPanel.logp'          : '-log10(P)',
    'ClusterPanel.zmax'          : 'Z Max',
    'ClusterPanel.zmaxcoords'    : 'Z Max location',
    'ClusterPanel.zcogcoords'    : 'Z Max COG location',
    'ClusterPanel.copemax'       : 'COPE Max',
    'ClusterPanel.copemaxcoords' : 'COPE Max location',
    'ClusterPanel.copemean'      : 'COPE mean',
    
    'ClusterPanel.addZStats'    : 'Add Z statistics',
    'ClusterPanel.addClustMask' : 'Add cluster mask',


    'OverlayDisplayPanel.Display'        : 'General display settings',
    'OverlayDisplayPanel.VolumeOpts'     : 'Volume settings',
    'OverlayDisplayPanel.MaskOpts'       : 'Mask settings',
    'OverlayDisplayPanel.LabelOpts'      : 'Label settings',
    'OverlayDisplayPanel.RGBVectorOpts'  : 'RGB vector settings',
    'OverlayDisplayPanel.LineVectorOpts' : 'Line vector settings',
    'OverlayDisplayPanel.ModelOpts'      : 'Model settings',
    
    'OverlayDisplayPanel.loadCmap'       : 'Load colour map',

    'CanvasSettingsPanel.scene'    : 'Scene settings',
    'CanvasSettingsPanel.ortho'    : 'Ortho view settings',
    'CanvasSettingsPanel.lightbox' : 'Lightbox settings',

    'OverlayInfoPanel.Image.dimensions'   : 'Dimensions',
    'OverlayInfoPanel.Image.transform'    : 'Transform/space',
    'OverlayInfoPanel.Image.orient'       : 'Orientation',
    
    'OverlayInfoPanel.Image'              : 'NIFTI1 image',
    'OverlayInfoPanel.FEATImage'          : 'NIFTI1 image (FEAT analysis)',
    'OverlayInfoPanel.FEATImage.featInfo' : 'FEAT information',
    'OverlayInfoPanel.Model'              : 'VTK model',
    'OverlayInfoPanel.Model.numVertices'  : 'Number of vertices',
    'OverlayInfoPanel.Model.numIndices'   : 'Number of indices',
    'OverlayInfoPanel.dataSource'         : 'Data source',
})


properties = TypeDict({
    
    'Profile.mode' : 'Profile',

    'CanvasPanel.syncLocation'       : 'Sync location',
    'CanvasPanel.syncOverlayOrder'   : 'Sync overlay order',
    'CanvasPanel.syncOverlayDisplay' : 'Sync overlay display settings',
    'CanvasPanel.movieMode'          : 'Movie mode',
    'CanvasPanel.movieRate'          : 'Movie update rate',
    'CanvasPanel.profile'            : 'Mode',

    'SceneOpts.showCursor'         : 'Show location cursor',
    'SceneOpts.showColourBar'      : 'Show colour bar',
    'SceneOpts.performance'        : 'Rendering performance',
    'SceneOpts.zoom'               : 'Zoom',
    'SceneOpts.colourBarLocation'  : 'Colour bar location',
    'SceneOpts.colourBarLabelSide' : 'Colour bar label side',

    'LightBoxOpts.zax'            : 'Z axis',
    'LightBoxOpts.highlightSlice' : 'Highlight slice',
    'LightBoxOpts.showGridLines'  : 'Show grid lines',
    'LightBoxOpts.sliceSpacing'   : 'Slice spacing',
    'LightBoxOpts.zrange'         : 'Z range',

    'OrthoOpts.showXCanvas' : 'Show X canvas',
    'OrthoOpts.showYCanvas' : 'Show Y canvas',
    'OrthoOpts.showZCanvas' : 'Show Z canvas',
    'OrthoOpts.showLabels'  : 'Show labels',
    'OrthoOpts.layout'      : 'Layout',
    'OrthoOpts.xzoom'       : 'X zoom',
    'OrthoOpts.yzoom'       : 'Y zoom',
    'OrthoOpts.zzoom'       : 'Z zoom',

    'PlotPanel.legend'    : 'Show legend',
    'PlotPanel.ticks'     : 'Show ticks',
    'PlotPanel.grid'      : 'Show grid',
    'PlotPanel.smooth'    : 'Smooth',
    'PlotPanel.autoScale' : 'Auto-scale',
    'PlotPanel.xLogScale' : 'Log scale (x axis)',
    'PlotPanel.yLogScale' : 'Log scale (y axis)',
    'PlotPanel.xlabel'    : 'X label',
    'PlotPanel.ylabel'    : 'Y label',
    
    'TimeSeriesPanel.plotMode'         : 'Plotting mode',
    'TimeSeriesPanel.usePixdim'        : 'Use pixdims',
    'TimeSeriesPanel.showCurrent'      : 'Plot time series for current voxel',
    'TimeSeriesPanel.currentColour'    : 'Colour for current time course',
    'TimeSeriesPanel.currentAlpha'     : 'Transparency for current '
                                         'time course',
    'TimeSeriesPanel.currentLineWidth' : 'Line width for current time course',
    'TimeSeriesPanel.currentLineStyle' : 'Line style for current time course',
    'TimeSeriesPanel.plotFullModelFit' : 'Plot full model fit',
    'TimeSeriesPanel.plotResiduals'    : 'Plot residuals',
    
    'HistogramPanel.histType'    : 'Histogram type',
    'HistogramPanel.autoBin'     : 'Automatic histogram binning', 
    'HistogramPanel.showCurrent' : 'Plot histogram for current overlay',
    
    'HistogramSeries.nbins'           : 'Number of bins',
    'HistogramSeries.ignoreZeros'     : 'Ignore zeros',
    'HistogramSeries.includeOutliers' : 'Include values out of data range',
    'HistogramSeries.volume'          : 'Volume',
    'HistogramSeries.dataRange'       : 'Data range',
    'HistogramSeries.showOverlay'     : 'Show 3D histogram overlay',

    'FEATTimeSeries.plotFullModelFit' : 'Plot full model fit',
    'FEATTimeSeries.plotEVs'          : 'Plot EV{} ({})',
    'FEATTimeSeries.plotPEFits'       : 'Plot PE{} fit ({})',
    'FEATTimeSeries.plotCOPEFits'     : 'Plot COPE{} fit ({})',
    'FEATTimeSeries.plotResiduals'    : 'Plot residuals',
    'FEATTimeSeries.plotReduced'      : 'Plot data reduced against',
    'FEATTimeSeries.plotData'         : 'Plot data',

    'OrthoEditProfile.selectionSize'          : 'Selection size',
    'OrthoEditProfile.selectionIs3D'          : '3D selection',
    'OrthoEditProfile.fillValue'              : 'Fill value',
    'OrthoEditProfile.intensityThres'         : 'Intensity threshold',
    'OrthoEditProfile.localFill'              : 'Only select adjacent voxels',
    'OrthoEditProfile.searchRadius'           : 'Limit search to radius (mm)',
    'OrthoEditProfile.selectionOverlayColour' : 'Selection overlay',
    'OrthoEditProfile.selectionCursorColour'  : 'Selection cursor',
    
    'Display.name'              : 'Overlay name',
    'Display.overlayType'       : 'Overlay data type',
    'Display.enabled'           : 'Enabled',
    'Display.alpha'             : 'Opacity',
    'Display.brightness'        : 'Brightness',
    'Display.contrast'          : 'Contrast',

    'ImageOpts.resolution' : 'Resolution',
    'ImageOpts.transform'  : 'Image transform',
    'ImageOpts.volume'     : 'Volume',
    
    'VolumeOpts.displayRange'   : 'Display range',
    'VolumeOpts.clippingRange'  : 'Clipping range',
    'VolumeOpts.cmap'           : 'Colour map',
    'VolumeOpts.invert'         : 'Invert colour map',
    'VolumeOpts.invertClipping' : 'Invert clipping range',
    'VolumeOpts.interpolation'  : 'Interpolation',

    'MaskOpts.colour'         : 'Colour',
    'MaskOpts.invert'         : 'Invert',
    'MaskOpts.threshold'      : 'Threshold',

    'VectorOpts.xColour'       : 'X Colour',
    'VectorOpts.yColour'       : 'Y Colour',
    'VectorOpts.zColour'       : 'Z Colour',

    'VectorOpts.suppressX'     : 'Suppress X value',
    'VectorOpts.suppressY'     : 'Suppress Y value',
    'VectorOpts.suppressZ'     : 'Suppress Z value',
    'VectorOpts.modulate'      : 'Modulate by',
    'VectorOpts.modThreshold'  : 'Modulation threshold',

    'RGBVectorOpts.interpolation' : 'Interpolation',

    'LineVectorOpts.directed'  : 'Interpret vectors as directed',
    'LineVectorOpts.lineWidth' : 'Line width',

    'ModelOpts.colour'       : 'Colour',
    'ModelOpts.outline'      : 'Show outline only',
    'ModelOpts.outlineWidth' : 'Outline width',
    'ModelOpts.refImage'     : 'Reference image',
    'ModelOpts.coordSpace'   : 'Model coordinate space',
    'ModelOpts.showName'     : 'Show model name',

    'LabelOpts.lut'          : 'Look-up table',
    'LabelOpts.outline'      : 'Show outline only',
    'LabelOpts.outlineWidth' : 'Outline width',
    'LabelOpts.showNames'    : 'Show label names',
})


profiles = TypeDict({
    'CanvasPanel.view' : 'View',
    'OrthoPanel.edit'  : 'Edit',
})

modes = TypeDict({
    ('OrthoViewProfile', 'nav')    : 'Navigate',
    ('OrthoViewProfile', 'pan')    : 'Pan',
    ('OrthoViewProfile', 'zoom')   : 'Zoom',

    ('OrthoEditProfile', 'nav')    : 'Navigate',
    ('OrthoEditProfile', 'pan')    : 'Pan',
    ('OrthoEditProfile', 'zoom')   : 'Zoom',
    ('OrthoEditProfile', 'sel')    : 'Select',
    ('OrthoEditProfile', 'desel')  : 'Deselect',
    ('OrthoEditProfile', 'selint') : 'Select by intensity',


    ('LightBoxViewProfile', 'view')   : 'View',
    ('LightBoxViewProfile', 'zoom')   : 'Zoom',

})


choices = TypeDict({

    'SceneOpts.colourBarLocation.top'    : 'Top',
    'SceneOpts.colourBarLocation.bottom' : 'Bottom',
    'SceneOpts.colourBarLocation.left'   : 'Left',
    'SceneOpts.colourBarLocation.right'  : 'Right',

    'SceneOpts.performance.1' : 'Fastest',
    'SceneOpts.performance.2' : 'Faster',
    'SceneOpts.performance.3' : 'Good looking',
    'SceneOpts.performance.4' : 'Better looking',
    'SceneOpts.performance.5' : 'Best looking',

    'HistogramPanel.dataRange.min' : 'Min.',
    'HistogramPanel.dataRange.max' : 'Max.',
    
    'ColourBarCanvas.orientation.horizontal' : 'Horizontal',
    'ColourBarCanvas.orientation.vertical'   : 'Vertical',
    
    'ColourBarCanvas.labelSide.top-left'     : 'Top / Left',
    'ColourBarCanvas.labelSide.bottom-right' : 'Bottom / Right', 

    'VolumeOpts.displayRange.min' : 'Min.',
    'VolumeOpts.displayRange.max' : 'Max.',

    'VectorOpts.displayType.line' : 'Lines',
    'VectorOpts.displayType.rgb'  : 'RGB',

    'VectorOpts.modulate.none'    : 'No modulation',

    'ImageOpts.transform.affine' : 'Use qform/sform transformation matrix',
    'ImageOpts.transform.pixdim' : 'Use pixdims only',
    'ImageOpts.transform.id'     : 'Do not use qform/sform or pixdims',

    'ModelOpts.refImage.none' : 'None',

    'VolumeOpts.interpolation.none'   : 'No interpolation', 
    'VolumeOpts.interpolation.linear' : 'Linear interpolation', 
    'VolumeOpts.interpolation.spline' : 'Spline interpolation',

    'Display.overlayType.volume'     : '3D/4D volume',
    'Display.overlayType.mask'       : '3D/4D mask image',
    'Display.overlayType.label'      : 'Label image',
    'Display.overlayType.rgbvector'  : '3-direction vector image (RGB)',
    'Display.overlayType.linevector' : '3-direction vector image (Line)',
    'Display.overlayType.model'      : '3D model',

    'HistogramPanel.histType.probability' : 'Probability',
    'HistogramPanel.histType.count'       : 'Count',
    
    'TimeSeriesPanel.plotMode.normal'        : 'Normal - no scaling/offsets',
    'TimeSeriesPanel.plotMode.demean'        : 'Demeaned',
    'TimeSeriesPanel.plotMode.normalise'     : 'Normalised',
    'TimeSeriesPanel.plotMode.percentChange' : 'Percent changed',
})


anatomy = TypeDict({

    ('Image', 'lowlong',   constants.ORIENT_A2P)               : 'Anterior',
    ('Image', 'lowlong',   constants.ORIENT_P2A)               : 'Posterior',
    ('Image', 'lowlong',   constants.ORIENT_L2R)               : 'Left',
    ('Image', 'lowlong',   constants.ORIENT_R2L)               : 'Right',
    ('Image', 'lowlong',   constants.ORIENT_I2S)               : 'Inferior',
    ('Image', 'lowlong',   constants.ORIENT_S2I)               : 'Superior',
    ('Image', 'lowlong',   constants.ORIENT_UNKNOWN)           : 'Unknown',
    ('Image', 'highlong',  constants.ORIENT_A2P)               : 'Posterior',
    ('Image', 'highlong',  constants.ORIENT_P2A)               : 'Anterior',
    ('Image', 'highlong',  constants.ORIENT_L2R)               : 'Right',
    ('Image', 'highlong',  constants.ORIENT_R2L)               : 'Left',
    ('Image', 'highlong',  constants.ORIENT_I2S)               : 'Superior',
    ('Image', 'highlong',  constants.ORIENT_S2I)               : 'Inferior',
    ('Image', 'highlong',  constants.ORIENT_UNKNOWN)           : 'Unknown',
    ('Image', 'lowshort',  constants.ORIENT_A2P)               : 'A',
    ('Image', 'lowshort',  constants.ORIENT_P2A)               : 'P',
    ('Image', 'lowshort',  constants.ORIENT_L2R)               : 'L',
    ('Image', 'lowshort',  constants.ORIENT_R2L)               : 'R',
    ('Image', 'lowshort',  constants.ORIENT_I2S)               : 'I',
    ('Image', 'lowshort',  constants.ORIENT_S2I)               : 'S',
    ('Image', 'lowshort',  constants.ORIENT_UNKNOWN)           : '?',
    ('Image', 'highshort', constants.ORIENT_A2P)               : 'P',
    ('Image', 'highshort', constants.ORIENT_P2A)               : 'A',
    ('Image', 'highshort', constants.ORIENT_L2R)               : 'R',
    ('Image', 'highshort', constants.ORIENT_R2L)               : 'L',
    ('Image', 'highshort', constants.ORIENT_I2S)               : 'S',
    ('Image', 'highshort', constants.ORIENT_S2I)               : 'I',
    ('Image', 'highshort', constants.ORIENT_UNKNOWN)           : '?',
    ('Image', 'space',     constants.NIFTI_XFORM_UNKNOWN)      : 'Unknown',
    ('Image', 'space',     constants.NIFTI_XFORM_SCANNER_ANAT) : 'Scanner '
                                                                 'anatomical',
    ('Image', 'space',     constants.NIFTI_XFORM_ALIGNED_ANAT) : 'Aligned '
                                                                 'anatomical',
    ('Image', 'space',     constants.NIFTI_XFORM_TALAIRACH)    : 'Talairach', 
    ('Image', 'space',     constants.NIFTI_XFORM_MNI_152)      : 'MNI152',
})


nifti = TypeDict({

    'dimensions' : 'Number of dimensions',
    
    'datatype'    : 'Data type',
    'vox_units'   : 'XYZ units',
    'time_units'  : 'Time units',
    'descrip'     : 'Description',
    'qform_code'  : 'QForm code',
    'sform_code'  : 'SForm code',
    'intent_code' : 'Intent code',
    'intent_name' : 'Intent name',

    'voxOrient.0'   : 'X voxel orientation',
    'voxOrient.1'   : 'Y voxel orientation',
    'voxOrient.2'   : 'Z voxel orientation',
    'sformOrient.0' : 'X sform orientation',
    'sformOrient.1' : 'Y sform orientation',
    'sformOrient.2' : 'Z sform orientation',
    'qformOrient.0' : 'X qform orientation',
    'qformOrient.1' : 'Y qform orientation',
    'qformOrient.2' : 'Z qform orientation', 

    'qform' : 'QForm matrix',
    'sform' : 'SForm matrix',

    'dim1' : 'dim1',
    'dim2' : 'dim2',
    'dim3' : 'dim3',
    'dim4' : 'dim4',
    'dim5' : 'dim5',
    'dim6' : 'dim6',
    'dim7' : 'dim7',

    'pixdim1' : 'pixdim1',
    'pixdim2' : 'pixdim2',
    'pixdim3' : 'pixdim3',
    'pixdim4' : 'pixdim4',
    'pixdim5' : 'pixdim5',
    'pixdim6' : 'pixdim6',
    'pixdim7' : 'pixdim7', 

    ('datatype', 0)    : 'UNKNOWN',
    ('datatype', 1)    : 'BINARY',
    ('datatype', 2)    : 'UINT8',
    ('datatype', 4)    : 'INT16',
    ('datatype', 8)    : 'INT32',
    ('datatype', 16)   : 'FLOAT32',
    ('datatype', 32)   : 'COMPLEX64',
    ('datatype', 64)   : 'DOUBLE64',
    ('datatype', 128)  : 'RGB',
    ('datatype', 255)  : 'ALL',
    ('datatype', 256)  : 'INT8',
    ('datatype', 512)  : 'UINT16',
    ('datatype', 768)  : 'UINT32',
    ('datatype', 1024) : 'INT64',
    ('datatype', 1280) : 'UINT64',
    ('datatype', 1536) : 'FLOAT128',
    ('datatype', 1792) : 'COMPLEX128',
    ('datatype', 2048) : 'COMPLEX256',
    ('datatype', 2304) : 'RGBA32',

    ('intent_code',  0)     :  'NIFTI_INTENT_CODE_NONE',
    ('intent_code',  2)     :  'NIFTI_INTENT_CODE_CORREL',
    ('intent_code',  3)     :  'NIFTI_INTENT_CODE_TTEST',
    ('intent_code',  4)     :  'NIFTI_INTENT_CODE_FTEST',
    ('intent_code',  5)     :  'NIFTI_INTENT_CODE_ZSCORE',
    ('intent_code',  6)     :  'NIFTI_INTENT_CODE_CHISQ',
    ('intent_code',  7)     :  'NIFTI_INTENT_CODE_BETA',
    ('intent_code',  8)     :  'NIFTI_INTENT_CODE_BINOM',
    ('intent_code',  9)     :  'NIFTI_INTENT_CODE_GAMMA',
    ('intent_code',  10)    :  'NIFTI_INTENT_CODE_POISSON',
    ('intent_code',  11)    :  'NIFTI_INTENT_CODE_NORMAL',
    ('intent_code',  12)    :  'NIFTI_INTENT_CODE_FTEST_NONC',
    ('intent_code',  13)    :  'NIFTI_INTENT_CODE_CHISQ_NONC',
    ('intent_code',  14)    :  'NIFTI_INTENT_CODE_LOGISTIC',
    ('intent_code',  15)    :  'NIFTI_INTENT_CODE_LAPLACE',
    ('intent_code',  16)    :  'NIFTI_INTENT_CODE_UNIFORM',
    ('intent_code',  17)    :  'NIFTI_INTENT_CODE_TTEST_NONC',
    ('intent_code',  18)    :  'NIFTI_INTENT_CODE_WEIBULL',
    ('intent_code',  19)    :  'NIFTI_INTENT_CODE_CHI',
    ('intent_code',  20)    :  'NIFTI_INTENT_CODE_INVGAUSS',
    ('intent_code',  21)    :  'NIFTI_INTENT_CODE_EXTVAL',
    ('intent_code',  22)    :  'NIFTI_INTENT_CODE_PVAL',
    ('intent_code',  23)    :  'NIFTI_INTENT_CODE_LOGPVAL',
    ('intent_code',  24)    :  'NIFTI_INTENT_CODE_LOG10)  :PVAL',
    ('intent_code',  2)     :  'NIFTI_FIRST_STATCODE',
    ('intent_code',  24)    :  'NIFTI_LAST_STATCODE',
    ('intent_code',  1001)  :  'NIFTI_INTENT_CODE_ESTIMATE',
    ('intent_code',  1002)  :  'NIFTI_INTENT_CODE_LABEL',
    ('intent_code',  1003)  :  'NIFTI_INTENT_CODE_NEURONAME',
    ('intent_code',  1004)  :  'NIFTI_INTENT_CODE_GENMATRIX',
    ('intent_code',  1005)  :  'NIFTI_INTENT_CODE_SYMMATRIX',
    ('intent_code',  1006)  :  'NIFTI_INTENT_CODE_DISPVECT',
    ('intent_code',  1007)  :  'NIFTI_INTENT_CODE_VECTOR',
    ('intent_code',  1008)  :  'NIFTI_INTENT_CODE_POINTSET',
    ('intent_code',  1009)  :  'NIFTI_INTENT_CODE_TRIANGLE',
    ('intent_code',  1010)  :  'NIFTI_INTENT_CODE_QUATERNION',
    ('intent_code',  1011)  :  'NIFTI_INTENT_CODE_DIMLESS',
    ('intent_code',  2001)  :  'NIFTI_INTENT_CODE_TIME_SERIES',
    ('intent_code',  2002)  :  'NIFTI_INTENT_CODE_NODE_INDEX',
    ('intent_code',  2003)  :  'NIFTI_INTENT_CODE_RGB_VECTOR',
    ('intent_code',  2004)  :  'NIFTI_INTENT_CODE_RGBA_VECTOR',
    ('intent_code',  2005)  :  'NIFTI_INTENT_CODE_SHAPE',
})


feat = TypeDict({
    'analysisName' : 'Analysis name',
    'numPoints'    : 'Number of volumes',
    'numEVs'       : 'Number of EVs',
    'numContrasts' : 'Number of contrasts',
})
