#@ String CONFIG
from distutils import extension
from ij import IJ, ImagePlus, measure
import os, ConfigParser, sys, time, math, ast
import os.path
from ij.process import ImageConverter, ImageProcessor
from ij.gui import Roi
from ij.plugin.filter import ParticleAnalyzer
from java.lang import Double
######################################################################
######################################################################

def get_files(folder, ending='.tif'):
    """
    Walk over the folder and find files ending in 
    """
    _files = os.listdir(folder)
    return [ item for item in _files if item.endswith(ending) ]


def process_image(input_path, image, output_path, keepthresholdfiles, pixelwidth, pixelheight, pixelunit, minparticlesize):
    """
    Process file
    """
    print ("Processing:", image)
    # make sure the image has a txt file as metadata
    if os.path.exists(os.path.join(input_path,image)):
        _output_csv_file = os.path.join(output_path, os.path.splitext(image)[0] + '.csv')
        print ("Processing >>>>>>>>>>>>>>", os.path.join(input_path,image))
        img_stack = IJ.openImage( os.path.join(input_path,image) )
        if img_stack.getType() != ImagePlus.GRAY8:
            imgConverter = ImageConverter(img_stack)
            imgConverter.convertToGray8()
            img_stack.updateImage()
        newcal = img_stack.getCalibration().copy()
        newcal.setUnit(pixelunit)
        newcal.pixelWidth = pixelwidth
        newcal.pixelHeight = pixelheight
        img_stack.setGlobalCalibration(None)
        img_stack.setCalibration(newcal)
        IJ.run( img_stack, "Smooth", "stack" )
        IJ.run( img_stack, "Sharpen", "stack" )
        IJ.setAutoThreshold(img_stack, "Default")
        IJ.run( img_stack, "Convert to Mask", "calculate black")
        img_stack.getProcessor().invert()
        # img_stack.show()

        stack = img_stack.getStack()
        if keepthresholdfiles:
            IJ.saveAsTiff(img_stack, os.path.join(output_path, os.path.splitext(image)[0] + '_threshold.tif'))
        for i in range( 1,img_stack.getStackSize()+1):
            # print ("i=", i)
            stack.getProcessor(i).invert()
            table = measure.ResultsTable()
            pa = ParticleAnalyzer( #ParticleAnalyzer.SHOW_OUTLINES, # ParticleAnalyzer.BARE_OUTLINES, # 
                               ParticleAnalyzer.SHOW_OUTLINES,
                               measure.Measurements.ALL_STATS,
                               table,
                               minparticlesize,
                               Double.POSITIVE_INFINITY,
                               0.1,
                               1.0 )

            pa.setHideOutputImage(True)
            if pa.analyze(img_stack, stack.getProcessor(i)):
                print ("All ok")
            else:
                print ("There was a problem in analyzing", image)
            # write table
            _pa_output_img = pa.getOutputImage()
            if _pa_output_img:
                IJ.saveAsTiff(_pa_output_img, os.path.join(output_path, os.path.splitext(image)[0] + '_countmask.tif'))
            table.save(_output_csv_file)
    else:
        print (">>>>>File ", image, " does not exist")

### first read config file here
if not os.path.exists(CONFIG):
    print ("[ERROR] " + CONFIG + " not exist")
    os._exit(1)
###
config = ConfigParser.ConfigParser()
config.readfp(open(CONFIG))
# now read the parameters
input_path = str(config.get("npc", "input_path")).strip()
if not os.path.exists(input_path):
    print ("[ERROR] Input path" + input_path + " not exist")
    os._exit(1)
output_path = str(config.get("npc", "output_path")).strip()
if not os.path.exists(output_path):
    os.makedirs(output_path)
keepcroppedfiles=config.getboolean("npc", "keep_cropped_files")
keepthresholdfiles=config.getboolean("npc", "keep_threshold_files")
pixelwidth=config.getfloat("npc", "pixelwidth")
pixelheight=config.getfloat("npc", "pixelheight")
pixelunit=str(config.get("npc", "pixelunit"))
minparticlesize=config.getfloat("npc", "minparticlesize")
fextension=str(config.get("npc", "fextension"))
images = get_files(input_path, '.' + fextension)
excluded = ast.literal_eval(config.get("npc", "excluded"))
excluded_files = [ i+"."+fextension for i in excluded ]
### now run it
for image in images:
    if not image in excluded_files:
        process_image(input_path, image, output_path, keepthresholdfiles, pixelwidth, pixelheight, pixelunit, minparticlesize)