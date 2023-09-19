##@ String path
from ij import IJ, ImagePlus, measure
import os
import sys
import time
import os.path
from datetime import datetime
from ij.process import ImageConverter, ImageProcessor
from ij.gui import Roi
from ij.plugin.filter import ParticleAnalyzer
from java.lang import Double
from ij.plugin.frame import RoiManager
import math
from ij.plugin import ImageCalculator
######################################################################
### values added to stdDEv when calculating min and max threshold
STDDEV_COEFFICIENT=2   # Assuming normal distributed data, 1 = ~68%, 2=~95%, 3=~99% of all values
######################################################################
import re
def get_files(folder, regex='*'):
    """
    Walk over the folder and find files ending in 
    """
    pattern = re.compile(regex)
    _files = os.listdir(folder)
    return [ item for item in _files if pattern.match(item) ]

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

def process_image(input_path, image, backgroundimage, output_path, metadata_ending='.txt'):
    """
    Process file
    """
    # make sure the image has a txt file as metadata
    _bgimage = ImagePlus(backgroundimage)
    if _bgimage.getType() != ImagePlus.GRAY8:
        bgImgConverter = ImageConverter(_bgimage)
        bgImgConverter.convertToGray8()
        _bgimage.updateImage()

    _output_csv_file = os.path.join(output_path, os.path.splitext(image)[0] + '.csv')
    if os.path.exists(os.path.join(input_path,image)):
        _image = ImagePlus(os.path.join(input_path,image))
        # duplicate the image to the working one, then we keep working on output
        _workingImage = _image.duplicate()
        # if the image is not GRAY8, then convert it to GRAY8
        if _image.getType() != ImagePlus.GRAY8:
            imgConverter = ImageConverter(_workingImage)
            imgConverter.convertToGray8()
            _workingImage.updateImage()
        
        _workingImage = ImageCalculator.run(_workingImage, _bgimage, "subtract")
        IJ.saveAsTiff(_workingImage, os.path.join(output_path, os.path.splitext(image)[0] + '_subtracted.tif'))

        # now the working image should be 8bit 
        stats = _workingImage.getProcessor().getStatistics()
        mean = stats.mean
        stdDev = stats.stdDev
        # print ("---------------------")
        # print ("Processing:", image)
        # print ("mean=", mean, " stddev=", stdDev, " skewness=", stats.skewness, " Kurtosis=", stats.kurtosis)
        # print ("1STDDEV_COEFFICIENT min=", int(math.floor(mean - STDDEV_COEFFICIENT*stdDev)), " max=", int(math.ceil(mean + STDDEV_COEFFICIENT*stdDev)))
        _minThreshold = int(math.floor(mean - 2*STDDEV_COEFFICIENT*stdDev))
        _maxThreshold = int(math.ceil(mean + 2*STDDEV_COEFFICIENT*stdDev))
        print ("min=", _minThreshold, " max=", _maxThreshold)
        # _croppedImage.getProcessor().setThreshold(_minThreshold, _maxThreshold, ImageProcessor.NO_LUT_UPDATE)
        
        _processor = _workingImage.getProcessor()
        _processor.setBinaryThreshold()
        _processor.setThreshold(_minThreshold, _maxThreshold, ImageProcessor.BLACK_AND_WHITE_LUT)
        _mask = _processor.createMask()
        _mask.invertLut()
        _workingImage.setProcessor(_mask)

        IJ.saveAsTiff(_workingImage, os.path.join(output_path, os.path.splitext(image)[0] + '_threshold.tif'))
        ### analyse particle
        table = measure.ResultsTable()
        # roim = RoiManager(True)
        pa = ParticleAnalyzer( ParticleAnalyzer.SHOW_OUTLINES, # ParticleAnalyzer.BARE_OUTLINES, # 
                               measure.Measurements.ALL_STATS,
                               table,
                               0,
                               Double.POSITIVE_INFINITY,
                               0.2,
                               1.0 )
        pa.setHideOutputImage(False)
        if pa.analyze(_workingImage):
            print ("All ok")
        else:
            print ("There was a problem in analyzing", image)
        # write table
        # _pa_output_img = pa.getOutputImage()
        # if _pa_output_img:
        #     print "output can be displayed"
        #     _pa_output_img.show()
        table.save(_output_csv_file)
    else:
        print (">>>>>File ", image, " does not have metadata file")
     
# path = os.path.expanduser(path.strip())
path = "/home/hoangnguyen177/Desktop/working/RCC/CMM_Projects_data/IMAGES/NP1"
print ('intput path=', path)
backgroundimage = "/home/hoangnguyen177/Desktop/working/RCC/CMM_Projects_data/IMAGES/NP1/NP1_100x_002_b_back.bmp"
if not os.path.exists(backgroundimage):
    raise Exception("Background image not eixsts")
output_path = os.path.join(path, 'output_' + datetime.now().strftime("%m_%d_%Y"))
if not os.path.exists(output_path):
    # create a new one
    os.makedirs(output_path)
images = get_files(path, regex='^NP.*.bmp$')
for image in images:
    process_image(path, image, backgroundimage, output_path)