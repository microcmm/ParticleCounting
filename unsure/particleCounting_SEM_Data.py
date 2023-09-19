import ij
from ij import IJ as j, ImagePlus as ip
import os
import time
import errno

#====================================================================		
# Path to files to be processed
#====================================================================
path = "C:\Users\uqcrami3\OneDrive - The University of Queensland\CMM\R&D_space\Training\ResBaz_2021UQ\AlisonNM"
#path = "C:\Users\uqcrami3\Documents\ToDelete\AlisonData"
# path = "/home/hoangnguyen177/Desktop/working/RCC/CMM_Projects/PCount"
files = os.listdir(path)
#====================================================================
# output directory
#====================================================================
timestr = time.strftime("%Y%m%d")
oDir = 'pdResults_'+timestr
oPath = os.path.join(path,oDir)
#print(oDir)
print(oPath)
#try:
#	os.mkdir(oPath)
#except OSError as e : 
#	if e.errno == errno.EEXIST:
#		print('Dir not Created')
#	else:
#		raise
#	
if not os.path.exists(oPath):
	os.mkdir(oPath)
	print 'Making dir'
else:
	print 'Dir already Exists'


images = []
mdTemp = []

footerpx = 64
#bad carlos
i=-1

[images.append(item.encode('utf-8')) for item in files if item.endswith(".tif")]
#====================================================================		
# Find text files and images
#====================================================================
for item in files:
	if item.endswith(".tif"):
		i+=1
		imp=j.openImage(os.path.join(path,item))
		imp.show()
		item_t,itemx = item.split(".")
		itxt = item_t + ".txt"
		mdTemp.append(itxt.encode('utf-8'))
#====================================================================
# Open Metadata file and extract required parameters (i.e Datasize and PixelSize) TODO: run another script that will prepare a dictionary for parameter labes
#====================================================================
		t_File = open(os.path.join(path, mdTemp[i].encode('utf-8')),'r')
#====================================================================		
# parse lines and extract DataSize
#====================================================================
		for line in t_File: 
			if "DataSize" in line:
				data ,vals= line.split('=')
				x,y = vals.split("x")
				x = x.encode('utf-8')
				y = y.encode('utf-8')
				y = y.strip("\n")
#				print(x,y)
				print(x.encode('utf-8'),y.encode('utf-8')) 
			elif "PixelSize" in line:
				data ,pSize= line.split('=')
				pSize = pSize.strip("\n")
			elif "MicronMarker" in line:
				data ,mMarker= line.split('=')
				mMarker = mMarker.strip("\n")
		#mdTemp.append(itxt.encode('utf-8'))
		t_File.close()
#====================================================================		
#		Image Processing using metada extracted
#====================================================================
		j.setTool("rectangle")
		j.makeRectangle(0, 0, int(x),int(y)-footerpx)
		j.run(imp,"Crop","")
		dis = float(mMarker)/float(pSize)
		dis = str(dis)
		#construct the string for sacale settings
		settings = "distance="+ dis+" "+ "known="+ mMarker+" "+ "pixel=1 unit=nm global"
		j.run(imp,"Set Scale...", settings)
		j.run("8-bit")
#		j.setAutoThreshold("Default")
#		j.setThreshold(0, 159)
#		j.run("Convert to Mask")
#		j.setAutoThreshold("Default dark")
		j.setThreshold(0, 159)
		j.run("Convert to Mask")
		j.run("Make Binary", "thresholded remaining black")
		j.run("Analyze Particles...", " circularity=0.20-1.00  show=[Bare Outlines] display exclude include add")

	
	#j.saveAs("Results", path+"\\Results\\"+item_t.encode('utf-8')+".xls")
	#j.save(outputFilepath)

	#imp.close()	
	#i+=1


##it does not run as a function... WHY!!!
#def cropImages(images):
#	for image in images:
#		imp=j.openImage(os.path.join(path,image))
#		j.setTool("rectangle")
#		j.makeRectangle(0, 0, 512, 512)
#		j.run(imp,"Crop","")
#		imp.show()
#	imp.close()

#imp = j.getImage()
#print(files)
#print(images)
#print(i)
#print(mdTemp)
#print(vals)
#a = cropImages(images)
