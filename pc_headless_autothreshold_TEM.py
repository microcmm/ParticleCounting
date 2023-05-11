#@ String CONFIG
#from distutils import extension
from ij import IJ, ImagePlus, measure
import os, ConfigParser, sys, time, math, ast
import os.path
from ij.process import ImageConverter#, ImageProcessor, ImageStatistics
#from ij.gui import Roi
from ij.plugin.filter import ParticleAnalyzer
from java.lang import Double
import logging


######################################################################
######################################################################
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s [%(name)s] %(levelname)s : %(message)s')
logger = logging.getLogger(__name__)

def get_files(folder, ending='.tif'):
    """
    Walk over the folder and find files ending in 
    """
    _files = os.listdir(folder)
    return [ item for item in _files if item.endswith(ending) ]

def should_ignore(hist_vals):
                       
    max_val = max(hist_vals)
    idx_max = hist_vals.index(max_val)
            
    ignore = False
    if (idx_max == len(hist_vals)-1):
        ignore = True
    
    return ignore

def process_image(input_path, image, output_path, keepthresholdfiles, pixelwidth, pixelheight, pixelunit, minparticlesize, min_circularity):
    """
    Process file
    """
    print ("Processing:", image)
    
    
    # make sure the image has a txt file as metadata
    if os.path.exists(os.path.join(input_path,image)):
        
        _output_csv_file = os.path.join(output_path, os.path.splitext(image)[0] + '.csv')
        print ("Processing >>>>>>>>>>>>>>", os.path.join(input_path,image))
        #print(test.should_ignore(os.path.join(input_path,image)))
        
        
        img_stack = IJ.openImage( os.path.join(input_path,image) )
        #IJ.run(img_stack, "getHistogram(values, counts, nBins[, histMin, histMax])", "stack")
        #IJ.getValue(img_stack, "Mode")
        hist = img_stack.getStatistics(1043199, 1024).getHistogram()
        #hist = img_stack.getAllStatistics().getHistogram()
        logger.info (hist)
        logger.info (should_ignore(hist))
        if should_ignore(hist) == True:
            logger.info("ignoring file: "+ image)
            print ("ignoring file: ", image)
           # time.sleep(20)
            return
        #IJ.run(img_stack, "ImageStatistics", "stack")
        #logging.info(__dir__(measure))
        #logging.info (img_stack ImageStatistics ip)
        # IJ.run(img_stack, "Table", "stack")
        print(input_path)
        print(img_stack.getType())  
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
        #IJ.run( img_stack, "8-bit", "stack")
        #IJ.run( img_stack, "Options...", "iterations=1 count=1 black")
       
        IJ.run(img_stack, "Smooth", "stack")
        IJ.run( img_stack, "Smooth", "stack")
        IJ.run(img_stack, "Mean...", "radius=25")
        #IJ.run( img_stack, "Enhance Contrast...", "saturated=4 normalize")
        #IJ.run( img_stack, "Smooth", "stack" )
        IJ.run(img_stack, "adaptiveThr ", "using=Mean from=4758 then=23")
        IJ.setAutoThreshold(img_stack, "Default no-reset")
        IJ.run( img_stack, "Convert to Mask", "calculate black")
        IJ.run( img_stack, "Watershed", "stack")
        #IJ.run( img_stack, "Find Edges", "stack")
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
                               min_circularity,
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

logger.info ("pina")
logger.info(os.path.exists(CONFIG))
### first read config file here
if not os.path.exists(CONFIG):
    logger.info("[ERROR] " + CONFIG + " not exist")
    print ("[ERROR] " + CONFIG + " not exist")
    os._exit(1)
###
logger.info(CONFIG)
config = ConfigParser.ConfigParser()
config.readfp(open(CONFIG))
# now read the parameters
input_path = str(config.get("npc", "input_path")).strip()
if not os.path.exists(input_path):
    print ("[ERROR] Input path" + input_path + " not exist")
    os._exit(1)
logger.info(input_path)
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
logger.info(len(images))
excluded = ast.literal_eval(config.get("npc", "excluded"))
logger.info(config)
min_circularity=config.getfloat("npc", "circularity_min")
excluded_files = [ i+"."+fextension for i in excluded ]
logger.info ("banana")
### now run it
for image in images:
    if not image in excluded_files:
        process_image(input_path, image, output_path, keepthresholdfiles, pixelwidth, pixelheight, pixelunit, minparticlesize, min_circularity)
logger.info ("apple")
IJ.run("Quit")
