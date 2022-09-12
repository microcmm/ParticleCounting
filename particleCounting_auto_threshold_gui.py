##@ String path
from ij import IJ, ImagePlus, measure
import os
import sys
import time
import os.path
from datetime import datetime
from ij.process import ImageConverter, ImageProcessor, AutoThresholder
from ij.gui import Roi
from ij.plugin.filter import ParticleAnalyzer
from java.lang import Double
from ij.plugin.frame import RoiManager
import math
from ij.plugin import ImageCalculator


######################################################################
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

def process_image(input_path, image, output_path):
    """
    Process file
    """
    if os.path.exists(os.path.join(input_path,image)):
        _output_csv_file = os.path.join(output_path, os.path.splitext(image)[0] + '.csv')
        print ("Processing >>>>>>>>>>>>>>", os.path.join(input_path,image))
        img_stack = IJ.openImage( os.path.join(input_path,image) )
        newcal = img_stack.getCalibration().copy()
        newcal.setUnit("mm")
        newcal.pixelWidth = 28490.8135
        newcal.pixelHeight = 28490.8135
        img_stack.setGlobalCalibration(None)
        img_stack.setCalibration(newcal)
        IJ.run( img_stack, "Smooth", "stack" )
        IJ.run( img_stack, "Sharpen", "stack" )
        IJ.setAutoThreshold(img_stack, "Default")
        IJ.run( img_stack, "Convert to Mask", "calculate black")
        img_stack.getProcessor().invert()
        # img_stack.show()

        stack = img_stack.getStack()
        IJ.saveAsTiff(img_stack, os.path.join(output_path, os.path.splitext(image)[0] + '_threshold.tif'))
        ### analyse particle
        for i in range( 1,img_stack.getStackSize()+1):
            # print ("i=", i)
            stack.getProcessor(i).invert()
            table = measure.ResultsTable()
            pa = ParticleAnalyzer( ParticleAnalyzer.SHOW_OUTLINES, # ParticleAnalyzer.BARE_OUTLINES, # 
                               measure.Measurements.ALL_STATS,
                               table,
                               0,
                               Double.POSITIVE_INFINITY,
                               0.2,
                               1.0 )

            pa.setHideOutputImage(True)
            if pa.analyze(img_stack, stack.getProcessor(i)):
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
path = "/home/hoangnguyen177/Desktop/working/RCC/CMM_Projects_data/20220225_NP_Characterisation/IMAGES/NP5"
print ('intput path=', path)
output_path = os.path.join(path, 'output_' + datetime.now().strftime("%m_%d_%Y"))
if not os.path.exists(output_path):
    # create a new one
    os.makedirs(output_path)
images = get_files(path, regex='^NP.*.bmp$')
for image in images:
    if "back" in image:
        continue
    process_image(path, image, output_path)