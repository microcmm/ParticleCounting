#@ String input
#@ String output
#@ boolean keepcroppedfiles
#@ boolean keepthresholdfiles
from ij import IJ, ImagePlus, measure
import os
import sys
import time, math
import os.path
from datetime import datetime
from ij.process import ImageConverter, ImageProcessor
from ij.gui import Roi
from ij.plugin.filter import ParticleAnalyzer
from java.lang import Double
######################################################################
### values added to stdDEv when calculating min and max threshold
STDDEV_COEFFICIENT=3   # Assuming normal distributed data, 1 = ~68%, 2=~95%, 3=~99% of all values
######################################################################

def get_files(folder, ending='.tif'):
    """
    Walk over the folder and find files ending in 
    """
    _files = os.listdir(folder)
    return [item for item in _files if item.endswith(ending)]

def read_metadata(_metadata_file):
    """
    get metadata file
    """
    with open(_metadata_file) as f:
        lines = f.readlines()
    metadata = {}
    for line in lines:
        line = line.strip()
        if not '=' in line:
            continue
        _field, _val = line.split("=", 1)
        _field = _field.strip()
        _val = _val.strip()
        metadata[_field] = _val
        if _field == 'DataSize':
            x,y = _val.split("x")
            x,y=int(x), int(y)
        elif _field == 'PixelSize':
            _pSize = float(_val)
        elif _field == 'MicronMarker':
            _mMarker = float(_val)
    return {'datasize': (x,y), 'pixelsize': _pSize, 'mmarker': _mMarker}


def calculate_footer_height(image):
    """
    Calculate footer height
    Should look at the bottom two corners, right now returns 64
    Assumption is that footer is always black
    We get the height from left side, and right side, get the smaller value
    """
    _leftLastBlackPixelY = image.getHeight()
    while image.getPixel(0, _leftLastBlackPixelY)[0] == 0:
        _leftLastBlackPixelY = _leftLastBlackPixelY - 1
    _rightLastBlackPixelY = image.getHeight()
    while image.getPixel(0, _rightLastBlackPixelY)[0] == 0:
        _rightLastBlackPixelY = _rightLastBlackPixelY - 1
    _footerHeightLeft = image.getHeight() - _leftLastBlackPixelY - 1
    _footerHeightRight = image.getHeight() - _rightLastBlackPixelY -1 
    return _footerHeightLeft if _footerHeightLeft < _footerHeightRight else _footerHeightRight

def process_image(input_path, image, output_path, keepcroppedfiles, keepthresholdfiles, metadata_ending='.txt'):
    """
    Process file
    """
    print ("Processing:", image)
    # make sure the image has a txt file as metadata
    _metadata_file = os.path.join(input_path, os.path.splitext(image)[0] + metadata_ending)
    _output_csv_file = os.path.join(output_path, os.path.splitext(image)[0] + '.csv')
    if os.path.exists(_metadata_file):
        # extract metadata file
        _metadata = read_metadata(_metadata_file)
        _image = ImagePlus(os.path.join(input_path,image))
        # duplicate the image to the working one, then we keep working on output
        _workingImage = _image.duplicate()
        # if the image is not GRAY8, then convert it to GRAY8
        if _image.getType() != ImagePlus.GRAY8:
            imgConverter = ImageConverter(_workingImage)
            imgConverter.convertToGray8()
            _workingImage.updateImage()
        # now the working image should be 8bit 
        # create ROI
        rectangle = Roi(0, 0, _metadata.get('datasize')[0], _metadata.get('datasize')[1] - calculate_footer_height(_workingImage))
        [_croppedImage] = _workingImage.crop([rectangle], "stack")
        # set scale - really, just the calibratrion
        newcal = _croppedImage.getCalibration().copy()
        newcal.setUnit("nm")
        newcal.pixelWidth =  _metadata.get('pixelsize')
        newcal.pixelHeight = _metadata.get('pixelsize')
        _croppedImage.setGlobalCalibration(None)
        _croppedImage.setCalibration(newcal)
        if keepcroppedfiles:
            IJ.saveAsTiff(_croppedImage, os.path.join(output_path, os.path.splitext(image)[0] + '_cropped.tif'))
        # j.setThreshold(0, 159)
        # j.run("Convert to Mask")
        stats = _croppedImage.getProcessor().getStatistics()
        print (stats.histogram())
        mean = stats.mean
        stdDev = stats.stdDev
        _minThreshold = int(math.floor(mean - 2*STDDEV_COEFFICIENT*stdDev))
        _maxThreshold = int(math.ceil(mean + 2*STDDEV_COEFFICIENT*stdDev))
        # set threshold
        _processor = _croppedImage.getProcessor()
        _processor.setBinaryThreshold()
        _processor.setThreshold(_minThreshold, _maxThreshold, ImageProcessor.BLACK_AND_WHITE_LUT)
        _mask = _processor.createMask()
        _mask.invertLut()
        _croppedImage.setProcessor(_mask)
        ### analyse particle
        if keepthresholdfiles:
            IJ.saveAsTiff(_croppedImage, os.path.join(output_path, os.path.splitext(image)[0] + '_thresholded.tif'))
        table = measure.ResultsTable()
        pa = ParticleAnalyzer( ParticleAnalyzer.SHOW_OUTLINES,
                               measure.Measurements.ALL_STATS,
                               table,
                               0,
                               Double.POSITIVE_INFINITY,
                               0.2,
                               1.0 )
        pa.setHideOutputImage(True)
        if pa.analyze(_croppedImage):
            print ("All ok")
        else:
            print ("There was a problem in analyzing", image)
        # write table
        table.save(_output_csv_file)
    else:
        print (">>>>>File ", image, " does not have metadata file")
     
path = os.path.expanduser(input.strip())
print ('intput path=', path)
# path = "/home/hoangnguyen177/Desktop/working/RCC/CMM_Projects/PCount"
# output_path = os.path.join(path, 'output_' + datetime.now().strftime("%m_%d_%Y"))
output_path = os.path.expanduser(output.strip())
print ('output path=', output_path)
if not os.path.exists(output_path):
    # create a new one
    os.makedirs(output_path)
images = get_files(path)
for image in images:
    process_image(path, image, output_path, keepcroppedfiles, keepthresholdfiles)