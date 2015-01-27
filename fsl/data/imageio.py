#!/usr/bin/env python
#
# imageio.py -
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#

import                     logging
import                     os 
import os.path          as op
import subprocess       as sp
import                     tempfile

import nibabel          as nib

import fsl.data.strings as strings
import image            as fslimage


log = logging.getLogger(__name__)


# TODO The wx.FileDialog does not    
# seem to handle wildcards with      
# multiple suffixes (e.g. '.nii.gz'),
# so i'm just providing '*.gz'for now
ALLOWED_EXTENSIONS = ['.nii.gz', '.nii', '.img', '.hdr', '.img.gz', '.gz']
"""The file extensions which we understand. This list is used as the default
if if the ``allowedExts`` parameter is not passed to any of the functions in
this module.
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


def makeWildcard(allowedExts=None):
    """Returns a wildcard string for use in a file dialog, to limit
    the acceptable file types.
    
    :arg allowedExts: A list of strings containing the allowed file
                      extensions.
    """
    
    if allowedExts is None:
        allowedExts  = ALLOWED_EXTENSIONS
        descs        = EXTENSION_DESCRIPTIONS
    else:
        descs        = allowedExts

    exts  = ['*{}'.format(ext) for ext in allowedExts]
    exts  = [';'.join(exts)]        + exts
    descs = ['All supported files'] + descs

    wcParts = ['|'.join((desc, ext)) for (desc, ext) in zip(descs, exts)]

    return '|'.join(wcParts)


def isSupported(filename, allowedExts=None):
    """
    Returns ``True`` if the given file has a supported extension, ``False``
    otherwise.

    :arg filename:    The file name to test.
    
    :arg allowedExts: A list of strings containing the allowed file
                      extensions.
    """

    if allowedExts is None: allowedExts = ALLOWED_EXTENSIONS

    return any(map(lambda ext: filename.endswith(ext), allowedExts))


def removeExt(filename, allowedExts=None):
    """
    Removes the extension from the given file name. Returns the filename
    unmodified if it does not have a supported extension.

    :arg filename:    The file name to strip.
    
    :arg allowedExts: A list of strings containing the allowed file
                      extensions.    
    """

    if allowedExts is None: allowedExts = ALLOWED_EXTENSIONS

    # figure out the extension of the given file
    extMatches = map(lambda ext: filename.endswith(ext), allowedExts)

    # the file does not have a supported extension
    if not any(extMatches):
        return filename

    # figure out the length of the matched extension
    extIdx = extMatches.index(True)
    extLen = len(allowedExts[extIdx])

    # and trim it from the file name
    return filename[:-extLen]


def addExt(
        prefix,
        mustExist=True,
        allowedExts=None,
        defaultExt=None):
    """Adds a file extension to the given file ``prefix``.

    If ``mustExist`` is False, and the file does not already have a 
    supported extension, the default extension is appended and the new
    file name returned. If the prefix already has a supported extension,
    it is returned unchanged.

    If ``mustExist`` is ``True`` (the default), the function checks to see 
    if any files exist that have the given prefix, and a supported file 
    extension.  A :exc:`ValueError` is raised if:

       - No files exist with the given prefix and a supported extension.
       - More than one file exists with the given prefix, and a supported
         extension.

    Otherwise the full file name is returned.

    :arg prefix:      The file name refix to modify.
    :arg mustExist:   Whether the file must exist or not.
    :arg allowedExts: List of allowed file extensions.
    :arg defaultExt:  Default file extension to use.
    """

    if allowedExts is None: allowedExts = ALLOWED_EXTENSIONS
    if defaultExt  is None: defaultExt  = DEFAULT_EXTENSION

    if not mustExist:

        # the provided file name already
        # ends with a supported extension 
        if any(map(lambda ext: prefix.endswith(ext), allowedExts)):
            return prefix

        return prefix + defaultExt

    # If the provided prefix already ends with a
    # supported extension , check to see that it exists
    if any(map(lambda ext: prefix.endswith(ext), allowedExts)):
        extended = [prefix]
        
    # Otherwise, make a bunch of file names, one per
    # supported extension, and test to see if exactly
    # one of them exists.
    else:
        extended = map(lambda ext: prefix + ext, allowedExts)

    exists = map(op.isfile, extended)

    # Could not find any supported file
    # with the specified prefix
    if not any(exists):
        raise ValueError(
            'Could not find a supported file with prefix {}'.format(prefix))

    # Ambiguity! More than one supported
    # file with the specified prefix
    if len(filter(bool, exists)) > 1:
        raise ValueError('More than one file with prefix {}'.format(prefix))

    # Return the full file name of the
    # supported file that was found
    extIdx = exists.index(True)
    return extended[extIdx]


def loadImage(filename):
    """Given the name of an image file, loads it using nibabel.

    If the file is large, and is gzipped, it is decompressed to a temporary
    location, so that it can be memory-mapped.  A tuple is returned,
    consisting of the nibabel image object, and the name of the file that it
    was loaded from (either the passed-in file name, or the name of the
    temporary decompressed file).
    """

    # If we have a GUI, we can display a dialog
    # message. Otherwise we print a log message
    haveGui = False
    try:
        import wx
        if wx.GetApp() is not None: 
            haveGui = True
    except:
        pass

    realFilename = filename
    mbytes = op.getsize(filename) / 1048576.0

    # The mbytes limit is arbitrary
    if filename.endswith('.nii.gz') and mbytes > 512:

        unzipped, filename = tempfile.mkstemp(suffix='.nii')

        unzipped = os.fdopen(unzipped)

        msg = strings.messages['imageio.loadImage.decompress']
        msg = msg.format(realFilename, mbytes, filename)

        if not haveGui:
            log.info(msg)
        else:
            busyDlg = wx.BusyInfo(msg, wx.GetTopLevelWindows()[0])

        gzip = ['gzip', '-d', '-c', realFilename]
        log.debug('Running {} > {}'.format(' '.join(gzip), filename))

        # If the gzip call fails, revert to loading from the gzipped file
        try:
            sp.call(gzip, stdout=unzipped)
            unzipped.close()

        except OSError as e:
            log.warn('gzip call failed ({}) - cannot memory '
                     'map file: {}'.format(e, realFilename),
                     exc_info=True)
            unzipped.close()
            os.remove(filename)
            filename = realFilename

        if haveGui:
            busyDlg.Destroy()

    log.debug('Loading image from {}'.format(filename))
    
    return nib.load(filename), filename


def saveImage(image, imageList=None, fromDir=None):
    """Convenience method for interactively saving changes to an image.

    If the :mod:`wx` package is available, a dialog is popped up, prompting
    the user to select a destination. Or, if the image has been loaded 
    from a file, the user is prompted to confirm that they want to overwrite  
    the image.


    :param image:         The :class:`~fsl.data.image.Image` instance to
                          be saved.


    :param imageList:     The :class:`~fsl.data.image.ImageList` instance
                          which contains the given image.


    :param str fromDir:   Directory in which the file dialog should start.
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
        if image.imageFile is None: lastDir = os.getcwd()
        else:                       lastDir = op.dirname(image.imageFile)

    # TODO make image.name safe (spaces to 
    # underscores, filter non-alphanumeric)
    if image.imageFile is None: filename = image.name
    else:                       filename = op.basename(image.imageFile)

    filename = removeExt(filename)

    saveLastDir = False
    if fromDir is None:
        fromDir = lastDir
        saveLastDir = True

    dlg = wx.FileDialog(app.GetTopWindow(),
                        message=strings.titles['imageio.saveImage.dialog'],
                        defaultDir=fromDir,
                        defaultFile=filename, 
                        style=wx.FD_SAVE)

    if dlg.ShowModal() != wx.ID_OK: return False

    if saveLastDir: saveImage.lastDir = lastDir

    path     = dlg.GetPath()
    nibImage = image.nibImage

    if not isSupported(path):
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
            pass

        # TODO handle error

        # this is just a normal image
        # which has been loaded from
        # a file, or an in-memory image
        else:

            log.debug('Saving image ({}) to {}'.format(image, path))

            nib.save(nibImage, path)
            image.imageFile = path
            
    except Exception as e:

        msg = strings.messages['imageio.saveImage.error'].format(e.msg)
        log.warn(msg)
        wx.MessageDialog(app.GetTopWindow(),
                         message=msg,
                         style=wx.OK | wx.ICON_ERROR)
        return

    image.saved = True


def addImages(imageList, fromDir=None, addToEnd=True):
    """Convenience method for interactively adding images to an
    :class:`fsl.data.image.ImageList`.
    If the :mod:`wx` package is available, pops up a file dialog
    prompting the user to select one or more images to append to the
    image list.

    :param str fromDir:   Directory in which the file dialog should start.
                          If ``None``, the most recently visited directory
                          (via this method) is used, or a directory from
                          an already loaded image, or the current working
                          directory.

    :param bool addToEnd: If True (the default), the new images are added
                          to the end of the list. Otherwise, they are added
                          to the beginning of the list.

    Returns: True if images were successfully added, False if no images
    were added.
    
    :raise ImportError:  if :mod:`wx` is not present.
    :raise RuntimeError: if a :class:`wx.App` has not been created.
    """
    import wx

    app = wx.GetApp()

    if app is None:
        raise RuntimeError('A wx.App has not been created')

    lastDir = getattr(addImages, 'lastDir', None)

    if lastDir is None:
        if len(imageList) > 0 and imageList[-1].imageFile is not None:
            lastDir = op.dirname(imageList[-1].imageFile)
        else:
            lastDir = os.getcwd()

    saveLastDir = False
    if fromDir is None:
        fromDir = lastDir
        saveLastDir = True

    dlg = wx.FileDialog(app.GetTopWindow(),
                        message=strings.titles['imageio.addImages.dialog'],
                        defaultDir=fromDir,
                        wildcard=makeWildcard(),
                        style=wx.FD_OPEN | wx.FD_MULTIPLE)

    if dlg.ShowModal() != wx.ID_OK: return False

    paths         = dlg.GetPaths()
    images        = map(fslimage.Image, paths)

    if saveLastDir: addImages.lastDir = op.dirname(paths[-1])

    if addToEnd: imageList.extend(      images)
    else:        imageList.insertAll(0, images)

    return True