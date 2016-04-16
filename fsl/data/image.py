#!/usr/bin/env python
# 
# image.py - Provides the :class:`Image` class, for representing 3D/4D NIFTI
#            images.
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#
"""This module provides the :class:`Image` class, for representing 3D/4D NIFTI1
images. The ``nibabel`` package is used for file I/O.

.. note:: Currently, only NIFTI1 images are supported.


It is very easy to load a NIFTI image::

    from fsl.data.image import Image
    myimg = Image('MNI152_T1_2mm.nii.gz')


A number of other functions are also provided for working with image files and
file names:

.. autosummary::
   :nosignatures:

   looksLikeImage
   removeExt
   addExt
   loadImage
   saveImage
"""


import               logging
import               tempfile
import               string
import               os 
import os.path    as op
import subprocess as sp

import               six 
import numpy      as np
import nibabel    as nib

import props

import fsl.utils.transform as transform
import fsl.utils.status    as status
import fsl.utils.path      as fslpath
import fsl.data.constants  as constants


log = logging.getLogger(__name__)


class Nifti1(object):
    """The ``Nifti1`` class is intended to be used as a base class for
    things which either are, or are associated with, a NIFTI1 image.


    When a ``Nifti1`` instance is created, it adds the following attributes
    to itself:

    
    ================= ====================================================
    ``nibImage``      The :mod:`nibabel` image object.
    ``dataSource``    The name of the file that the image was loaded from. 
    ``tempFile``      The name of the temporary file which was created (in
                      the event that the image was large and was gzipped -
                      see :func:`loadImage`).
    ``shape``         A list/tuple containing the number of voxels along
                      each image dimension. 
    ``voxToWorldMat`` A 4*4 array specifying the affine transformation
                      for transforming voxel coordinates into real world
                      coordinates.
    ``worldToVoxMat`` A 4*4 array specifying the affine transformation
                      for transforming real world coordinates into voxel
                      coordinates.
    ================= ====================================================
    """

    def __init__(self,
                 image,
                 xform=None,
                 header=None,
                 loadData=True):
        """Create a ``Nifti1`` object.

        :arg image:    A string containing the name of an image file to load, 
                       or a :mod:`numpy` array, or a :mod:`nibabel` image
                       object.

        :arg xform:    A :math:`4\\times 4` affine transformation matrix 
                       which transforms voxel coordinates into real world
                       coordinates.

        :arg header:   If not ``None``, assumed to be a
                       :class:`nibabel.nifti1.Nifti1Header` to be used as the 
                       image header. Not applied to images loaded from file,
                       or existing :mod:`nibabel` images.

        :arg loadData: Defaults to ``True``. If ``False``, the image data is
                       not loaded - this is useful if you're only interested
                       in the header data, as the file will be loaded much
                       more quickly. The image data may subsequently be loaded
                       via the :meth:`loadData` method. 
        """
        
        self.nibImage      = None
        self.dataSource    = None
        self.tempFile      = None
        self.shape         = None
        self.pixdim        = None
        self.voxToWorldMat = None
        self.worldToVoxMat = None

        if header is not None:
            header = header.copy()

        # The image parameter may be the name of an image file
        if isinstance(image, six.string_types):
            
            nibImage, filename = loadImage(addExt(image))
            self.nibImage      = nibImage
            self.dataSource    = op.abspath(image) 

            # if the returned file name is not the same as
            # the provided file name, that means that the
            # image was opened from a temporary file
            if filename != image:
                self.tempFile = nibImage.get_filename()
                
        # Or a numpy array - we wrap it in a nibabel image,
        # with an identity transformation (each voxel maps
        # to 1mm^3 in real world space)
        elif isinstance(image, np.ndarray):

            if xform is None:
                if header is None: xform = np.identity(4)
                else:              xform = header.get_best_affine()
            
            self.nibImage  = nib.nifti1.Nifti1Image(image,
                                                    xform,
                                                    header=header)
            
        # otherwise, we assume that it is a nibabel image
        else:
            self.nibImage = image

        shape, pixdim = self.__determineShape(self.nibImage)
        
        self.shape         = shape
        self.pixdim        = pixdim
        self.voxToWorldMat = np.array(self.nibImage.get_affine())
        self.worldToVoxMat = transform.invert(self.voxToWorldMat)

        if loadData:
            self.loadData()
        else:
            self.data = None

        if len(self.shape) < 3 or len(self.shape) > 4:
            raise RuntimeError('Only 3D or 4D images are supported')


    def __determineShape(self, nibImage):
        """This method is called by :meth:`__init__`. It figures out the shape
        of the image data, and the zooms/pixdims for each data axis. Any empty
        trailing dimensions are squeezed, but the returned shape is guaranteed
        to be at least 3 dimensions.
        """

        nibHdr  = nibImage.get_header()
        shape   = list(nibImage.shape)
        pixdims = list(nibHdr.get_zooms())

        # Squeeze out empty dimensions, as
        # 3D image can sometimes be listed
        # as having 4 or more dimensions 
        for i in reversed(range(len(shape))):
            if shape[i] == 1: shape = shape[:i]
            else:             break

        # But make sure the shape is 3D
        if len(shape) < 3:
            shape = shape + [1] * (3 - len(shape))

        # The same goes for the pixdim - if get_zooms()
        # doesn't return at least 3 values, we'll fall
        # back to the pixdim field in the header.
        if len(pixdims) < 3:
            pixdims = nibHdr['pixdim'][1:]

        pixdims = pixdims[:len(shape)]
        
        return shape, pixdims
 
    
    def loadData(self):
        """Loads the image data from the file. This method only needs to
        be called if the ``loadData`` parameter passed to :meth:`__init__`
        was ``False``.
        """

        # Get the data, and reshape it according
        # to the shape that the __determineShape
        # method figured out.
        data      = self.nibImage.get_data()
        origShape = data.shape
        data      = data.reshape(self.shape)

        # Tell numpy to make the
        # data array read-only
        data.flags.writeable = False
        
        self.data = data

        log.debug('Loaded image data ({}) - original '
                  'shape {}, squeezed shape {}'.format(
                      self.dataSource,
                      origShape,
                      data.shape))

        
    # TODO: Remove this method, and use the shape attribute directly
    def is4DImage(self):
        """Returns ``True`` if this image is 4D, ``False`` otherwise. """
        return len(self.shape) > 3 and self.shape[3] > 1 

    
    def getXFormCode(self, code=None):
        """This method returns the code contained in the NIFTI1 header,
        indicating the space to which the (transformed) image is oriented.

        The ``code`` parameter may be either ``sform`` (the default) or
        ``qform`` in which case the corresponding matrix is used.

        :returns: one of the following codes:
                    - :data:`~.constants.NIFTI_XFORM_UNKNOWN`
                    - :data:`~.constants.NIFTI_XFORM_SCANNER_ANAT`
                    - :data:`~.constants.NIFTI_XFORM_ALIGNED_ANAT`
                    - :data:`~.constants.NIFTI_XFORM_TALAIRACH`
                    - :data:`~.constants.NIFTI_XFORM_MNI_152`
        """

        if   code is None:     code = 'sform_code'
        elif code == 'sform' : code = 'sform_code'
        elif code == 'qform' : code = 'qform_code'
        else: raise ValueError('code must be None, sform, or qform')

        code = self.nibImage.get_header()[code]

        # Invalid values
        if   code > 4: code = constants.NIFTI_XFORM_UNKNOWN
        elif code < 0: code = constants.NIFTI_XFORM_UNKNOWN
        
        return int(code)


    def axisMapping(self, xform):
        """Returns the (approximate) correspondence of each axis in the source
        coordinate system to the axes in the destination coordinate system,
        where the source and destinations are defined by the given affine
        transformation matrix.
        """

        import nibabel as nib

        inaxes = [[-1, 1], [-2, 2], [-3, 3]]

        return nib.orientations.aff2axcodes(xform, inaxes)


    def isNeurological(self):
        """Returns ``True`` if it looks like this ``Nifti1`` object is in
        neurological orientation, ``False`` otherwise. This test is purely
        based on the determinent of the voxel-to-mm transformation matrix -
        if it has a positive determinant, the image is assumed to be in
        neurological orientation, otherwise it is assumed to be in
        radiological orientation.

        http://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FLIRT/FAQ#What_is_the_format_\
          of_the_matrix_used_by_FLIRT.2C_and_how_does_it_relate_to_the_\
          transformation_parameters.3F
        """
        import numpy.linalg as npla
        return npla.det(self.voxToWorldMat) > 0


    def getOrientation(self, axis, xform):
        """Returns a code representing the orientation of the specified data
        axis in the coordinate system defined by the given transformation
        matrix.

        :arg xform: A transformation matrix which is assumed to transform
                    coordinates from the image world coordinate system to
                    some other coordinate system.

        This method returns one of the following values, indicating the
        direction in which coordinates along the specified axis increase:
        
          - :attr:`~.constants.ORIENT_L2R`:     Left to right
          - :attr:`~.constants.ORIENT_R2L`:     Right to left
          - :attr:`~.constants.ORIENT_A2P`:     Anterior to posterior
          - :attr:`~.constants.ORIENT_P2A`:     Posterior to anterior
          - :attr:`~.constants.ORIENT_I2S`:     Inferior to superior
          - :attr:`~.constants.ORIENT_S2I`:     Superior to inferior
          - :attr:`~.constants.ORIENT_UNKNOWN`: Orientation is unknown

        The returned value is dictated by the XForm code contained in the
        image file header (see the :meth:`getXFormCode` method). Basically, if
        the XForm code is *unknown*, this method will return
        ``ORIENT_UNKNOWN`` for all axes. Otherwise, it is assumed that the
        image is in RAS orientation (i.e. the X axis increases from left to
        right, the Y axis increases from posterior to anterior, and the Z axis
        increases from inferior to superior).
        """

        if self.getXFormCode() == constants.NIFTI_XFORM_UNKNOWN:
            return constants.ORIENT_UNKNOWN 
        
        import nibabel as nib
        code = nib.orientations.aff2axcodes(
            xform,
            ((constants.ORIENT_R2L, constants.ORIENT_L2R),
             (constants.ORIENT_A2P, constants.ORIENT_P2A),
             (constants.ORIENT_S2I, constants.ORIENT_I2S)))[axis]

        return code 


class Image(Nifti1, props.HasProperties):
    """Class which represents a 3D/4D NIFTI1 image. Internally, the image
    is loaded/stored using :mod:`nibabel`.

    
    In addition to the :attr:`data`, and :attr:`saved` properties, and
    the attributes added by the :meth:`Nifti1.__init__` method, the
    following attributes are present on an ``Image`` instance: 


    ================= ====================================================
    ``name``          the name of this ``Image`` - defaults to the image
                      file name, sans-suffix.
    
    ``dataMin``       Minimum value in the image data. This is only
                      calculated if the ``loadData`` parameter to
                      :meth:`__init__` is ``True``, or when the
                      :meth:`loadData` method is called. If this is not 
                      the case, ``dataMin`` will be ``None``. The
                      ``dataMin`` value is updated on every call to
                      :meth:`applyChange`.
    
    ``dataMax``       Maximum value in the image data. This is calculated
                      alongside ``dataMin``.
    ================= ==================================================== 
    """


    data = props.Object()
    """The image data. This is a read-only :mod:`numpy` array - all changes
       to the image data must be via the :meth:`applyChange` method.
    """


    saved = props.Boolean(default=False)
    """A read-only property (not enforced) which is ``True`` if the image,
    as stored in memory, is saved to disk, ``False`` otherwise.
    """


    dataRange = props.Bounds(ndims=1, default=(np.inf, -np.inf))
    """A read-only property (not enforced) which contains the image
    data range. This property is updated every time the image data
    is changed (via :meth:`applyChange`).
    """


    def __init__(self, image, name=None, **kwargs):
        """Create an ``Image`` object with the given image data or file name.

        :arg image:    A string containing the name of an image file to load, 
                       or a :mod:`numpy` array, or a :mod:`nibabel` image
                       object.

        :arg name:     A name for the image.

        All other arguments are passed through to :meth:`Nifti1.__init__`.
        """
                    
        Nifti1.__init__(self, image, **kwargs)

        # Figure out the name of this image.
        # It might have been explicitly passed in
        if name is not None:
            self.name = name
            
        # Or, if this image was loaded 
        # from disk, use the file name
        elif isinstance(image, six.string_types):
            self.name  = removeExt(op.basename(self.dataSource))
            self.saved = True
            
        # Or the image was created from a numpy array
        elif isinstance(image, np.ndarray):
            self.name = 'Numpy array'
            
        # Or image from a nibabel image
        else:
            self.name = 'Nibabel image'


    def __hash__(self):
        """Returns a number which uniquely idenfities this ``Image`` instance
        (the result of ``id(self)``).
        """
        return id(self)


    def __str__(self):
        """Return a string representation of this ``Image`` instance."""
        return '{}({}, {})'.format(self.__class__.__name__,
                                   self.name,
                                   self.dataSource)

        
    def __repr__(self):
        """See the :meth:`__str__` method."""
        return self.__str__()


    def loadData(self):
        """Overrides :meth:`Nifti1.loadData`. Calls that method, and
        calculates initial values for :attr:`dataRange`.
        """

        Nifti1.loadData(self)

        status.update('Calculating minimum/maximum '
                      'for {}...'.format(self.dataSource), None)

        dataMin = np.nanmin(self.data)
        dataMax = np.nanmax(self.data)

        log.debug('Calculated data range for {}: [{} - {}]'.format(
            self.dataSource, dataMin, dataMax))
        
        if np.any(np.isnan((dataMin, dataMax))):
            dataMin = 0
            dataMax = 0

        status.update('{} range: [{} - {}]'.format(
            self.dataSource, dataMin, dataMax))

        self.dataRange.x = [dataMin, dataMax]

        
    def applyChange(self, offset, newVals, vol=None):
        """Changes the image data according to the given new values.
        Any listeners registered on the :attr:`data` property will be
        notified of the change.

        :arg offset:  A tuple of three values, containing the xyz
                      offset of the image region to be changed.
        
        :arg newVals: A 3D numpy array containing the new image values.
        
        :arg vol:     If this is a 4D image, the volume index.
        """
        
        if self.is4DImage() and vol is None:
            raise ValueError('Volume must be specified for 4D images')

        newVals = np.array(newVals)

        if newVals.size == 0:
            return
        
        data          = self.data
        xlo, ylo, zlo = offset
        xhi           = xlo + newVals.shape[0]
        yhi           = ylo + newVals.shape[1]
        zhi           = zlo + newVals.shape[2]

        log.debug('Image {} data change - offset: {}, shape: {}, '
                  'volume: {}'.format(self.name, offset, newVals.shape, vol))

        try:
            data.flags.writeable = True
            
            if self.is4DImage(): oldVals = data[xlo:xhi, ylo:yhi, zlo:zhi, vol]
            else:                oldVals = data[xlo:xhi, ylo:yhi, zlo:zhi]
            
            if self.is4DImage(): data[xlo:xhi, ylo:yhi, zlo:zhi, vol] = newVals
            else:                data[xlo:xhi, ylo:yhi, zlo:zhi]      = newVals
            
            data.flags.writeable = False
            
        except:
            data.flags.writeable = False
            raise

        newMin, newMax = self.__calculateDataRange(oldVals, newVals)
        
        log.debug('Image {} new data range: {} - {}'.format(
            self.name, newMin, newMax)) 

        # Make sure the dataRange is up to date
        self.dataRange.x = [newMin, newMax]
        
        # Force a notification on the 'data' property
        # by assigning its value back to itself
        self.data  = data
        self.saved = False


    def save(self):
        """Convenience method to save any changes made to the :attr:`data` of 
        this :class:`Image` instance.

        See the :func:`saveImage` function.
        """
        return saveImage(self)


    def __calculateDataRange(self, oldVals, newVals):
        """Called by :meth:`applyChange`. Re-calculates the image data range,
        and returns a tuple containing the ``(min, max)`` values.
        """

        data = self.data

        status.update('Calculating minimum/maximum '
                      'for {}...'.format(self.dataSource), None)

        # The old image wide data range.
        oldMin    = self.dataRange.xlo
        oldMax    = self.dataRange.xhi

        # The data range of the changed sub-array.
        newValMin = np.nanmin(newVals)
        newValMax = np.nanmax(newVals)

        # Has the entire image been updated?
        wholeImage = tuple(newVals.shape) == tuple(data.shape[:3])

        # If the minimum of the new values
        # is less than the old image minimum, 
        # then it becomes the new minimum.
        if   (newValMin <= oldMin) or wholeImage: newMin = newValMin

        # Or, if the old minimum is being
        # replaced by the new values, we
        # need to re-calculate the minimum
        elif np.nanmin(oldVals) == oldMin:        newMin = np.nanmin(data)

        # Otherwise, the image minimum
        # has not changed.
        else:                                     newMin = oldMin

        # The same logic applies to the maximum
        if   (newValMax >= oldMax) or wholeImage: newMax = newValMax
        elif np.nanmax(oldVals) == oldMax:        newMax = np.nanmax(data)
        else:                                     newMax = oldMax

        if np.isnan(newMin): newMin = 0
        if np.isnan(newMax): newMax = 0

        status.update('{} range: [{} - {}]'.format(
            self.dataSource, newMin, newMax))        

        return newMin, newMax
    

# TODO The wx.FileDialog does not    
# seem to handle wildcards with      
# multiple suffixes (e.g. '.nii.gz'),
# so i'm just providing '*.gz'for now
ALLOWED_EXTENSIONS = ['.nii.gz', '.nii', '.img', '.hdr', '.img.gz', '.gz']
"""The file extensions which we understand. This list is used as the default
if the ``allowedExts`` parameter is not passed to any of the functions
below.
"""


EXTENSION_DESCRIPTIONS = ['Compressed NIFTI1 images',
                          'NIFTI1 images',
                          'ANALYZE75 images',
                          'NIFTI1/ANALYZE75 headers',
                          'Compressed NIFTI1/ANALYZE75 images',
                          'Compressed images']
"""Descriptions for each of the extensions in :data:`ALLOWED_EXTENSIONS`. """


DEFAULT_EXTENSION  = '.nii.gz'
"""The default file extension (TODO read this from ``$FSLOUTPUTTYPE``)."""


def looksLikeImage(filename, allowedExts=None):
    """Returns ``True`` if the given file looks like an image, ``False``
    otherwise.

    :arg filename:    The file name to test.
    
    :arg allowedExts: A list of strings containing the allowed file
                      extensions.
    """

    if allowedExts is None: allowedExts = ALLOWED_EXTENSIONS

    # TODO A much more robust approach would be
    #      to try loading the file using nibabel.

    return any([filename.endswith(ext) for ext in allowedExts])


def removeExt(filename):
    """Removes the extension from the given file name. Returns the filename
    unmodified if it does not have a supported extension.

    See :func:`~fsl.utils.path.removeExt`.

    :arg filename: The file name to strip.
    """
    return fslpath.removeExt(filename, ALLOWED_EXTENSIONS)


def addExt(prefix, mustExist=True):
    """Adds a file extension to the given file ``prefix``.

    See :func:`~fsl.utils.path.addExt`.
    """
    return fslpath.addExt(prefix,
                          ALLOWED_EXTENSIONS,
                          mustExist,
                          DEFAULT_EXTENSION)


def loadImage(filename):
    """Given the name of an image file, loads it using nibabel.

    If the file is large, and is gzipped, it is decompressed to a temporary
    location, so that it can be memory-mapped.

    In any case, a tuple is returned, consisting of the nibabel image object,
    and the name of the file that it was loaded from (either the passed-in
    file name, or the name of the temporary decompressed file).

    .. note:: The decompressing logic has been disabled for the time being.
    """

    # realFilename = filename
    # mbytes       = op.getsize(filename) / 1048576.0

    # # The mbytes limit is arbitrary
    # if filename.endswith('.gz') and mbytes > 512:

    #     unzipped, filename = tempfile.mkstemp(suffix='.nii')

    #     unzipped = os.fdopen(unzipped)

    #     msg = fslstrings.messages['image.loadImage.decompress']
    #     msg = msg.format(op.basename(realFilename), mbytes, filename)

    #     status.update(msg, None)

    #     gzip = ['gzip', '-d', '-c', realFilename]
    #     log.debug('Running {} > {}'.format(' '.join(gzip), filename))

    #     # If the gzip call fails, revert to loading from the gzipped file
    #     try:
    #         sp.call(gzip, stdout=unzipped)
    #         unzipped.close()

    #     except OSError as e:
    #         log.warn('gzip call failed ({}) - cannot memory '
    #                  'map file: {}'.format(e, realFilename),
    #                  exc_info=True)
    #         unzipped.close()
    #         os.remove(filename)
    #         filename = realFilename

    log.debug('Loading image from {}'.format(filename))

    import nibabel as nib

    # if mbytes > 512:
    #     msg     = fslstrings.messages['image.loadImage.largeFile']
    #     msg     = msg.format(op.basename(filename),  mbytes)
    #     status.update(msg)
    
    image = nib.load(filename)

    return image, filename


def saveImage(image, fromDir=None):
    """Convenience function for interactively saving changes to an image.

    If the :mod:`wx` package is available, a dialog is popped up, prompting
    the user to select a destination. Or, if the image has been loaded 
    from a file, the user is prompted to confirm that they want to overwrite  
    the image.


    :arg image:           The :class:`.Image` instance to be saved.

    :arg fromDir:         Directory in which the file dialog should start.
                          If ``None``, the most recently visited directory
                          (via this method) is used, or the directory from
                          the given image, or the current working directory.

    :raise ImportError:  if :mod:`wx` is not present.
    :raise RuntimeError: if a :class:`wx.App` has not been created.
    """

    if image.saved:
        return
    
    import wx

    app = wx.GetApp()

    if app is None:
        raise RuntimeError('A wx.App has not been created') 

    lastDir = getattr(saveImage, 'lastDir', None)

    if lastDir is None:
        if image.dataSource is None: lastDir = os.getcwd()
        else:                        lastDir = op.dirname(image.dataSource)

    if image.dataSource is None:
        filename = image.name

        # Make sure the image name is safe to
        # use as a file name - replace all
        # non-alphanumeric/-/_ characters with _.
        safechars = string.letters + string.digits + '_-'
        filename  = ''.join([c if c in safechars else '_' for c in filename])
    else:
        filename = op.basename(image.dataSource)

    filename = removeExt(filename)

    saveLastDir = False
    if fromDir is None:
        fromDir = lastDir
        saveLastDir = True

    dlg = wx.FileDialog(app.GetTopWindow(),
                        message='Save image file',
                        defaultDir=fromDir,
                        defaultFile=filename, 
                        style=wx.FD_SAVE)

    if dlg.ShowModal() != wx.ID_OK: return False

    if saveLastDir: saveImage.lastDir = lastDir

    path     = dlg.GetPath()
    nibImage = image.nibImage

    # Add a file extension if not specified
    if not looksLikeImage(path):
        path = addExt(path, False)

    # this is an image which has been
    # loaded from a file, and ungzipped
    # to a temporary location
    try:
        if image.tempFile is not None:

            # if selected path is same as original path,
            # save to both temp file and to path

            # else, if selected path is different from
            # original path, save to temp file and to
            # new path, and update the path

            # actually, the two behaviours just described
            # are identical
            log.warn('Saving large images is not yet functional')
            pass

        # this is just a normal image
        # which has been loaded from
        # a file, or an in-memory image
        else:

            log.debug('Saving image ({}) to {}'.format(image, path))

            import nibabel as nib
            nib.save(nibImage, path)
            image.dataSource = path
            
    except Exception as e:

        msg = 'An error occurred saving the file. Details: {}'.format(e.msg)
        log.warn(msg)
        wx.MessageDialog(app.GetTopWindow(),
                         message=msg,
                         style=wx.OK | wx.ICON_ERROR).ShowModal()
        return

    image.saved = True
