To run headless:
----------------

Linux:
======
python3 pc_main.py pc-fiji --fiji-path /home/hoangnguyen177/bin/ImageJ-linux64 --pixel-width 0.055 --pixel-height 0.055 --pixel-unit μm --min-particle-size 3 --input-path "C:\Users\uqatask1\Desktop\CMM_Projects_Data\Inputs\DSX\Nikky\POM05\4690x\Stitch individual_POM05_05_tif" --output-path "C:\Users\uqatask1\Desktop\CMM_Projects_Data\Outputs\DSX1000\Nikky\POM05\4690x_8" --file-extension tiff --ignored stitched scale --field Area Feret FeretX FeretY FeretAngle MinFeret Angle AR Round "Circ." --threshold "164" --subtract "12" --graph-min-x "0.1" --graph-bins-n-Feret "20" --graph-bins-n-AR "25" --circularity-min "0.05"

Windows:
========
python3 .\pc_main.py pc-fiji --fiji-path C:\fiji\ImageJ-win64.exe --pixel-width 0.055 --pixel-height 0.055 --pixel-unit μm --min-particle-size 3 --input-path "C:\Users\uqatask1\Desktop\CMM_Projects_Data\Inputs\DSX\Nikky\POM05\4690x\Stitch individual_POM05_05_tif" --output-path "C:\Users\uqatask1\Desktop\CMM_Projects_Data\Outputs\DSX1000\Nikky\POM05\4690x_8" --file-extension tiff --ignored stitched scale --field Area Feret FeretX FeretY FeretAngle MinFeret Angle AR Round "Circ." --threshold "164" --subtract "12" --graph-min-x "0.1" --graph-bins-n-Feret "20" --graph-bins-n-AR "25" --circularity-min "0.05"

To run with display:
--------------------
ImageJ-linux64 --ij2 --run /home/hoangnguyen177/Desktop/working/RCC/CMM_Projects/PCount/particleCounting_gui.py

or run it from ImageJ

for Jon:
run .\pc_main_OM.py pc-fiji --fiji-path C:\Users\uqatask1\fiji\ImageJ-win64.exe --pixel-width 0.005 --pixel-height 0.005 --pixel-unit μm --min-particle-size 70 --input-path "C:\Users\uqatask1\OneDrive - The University of Queensland\Desktop\CMM_Projects_Data\Inputs\eline\Bob\converted" --output-path "C:\Users\uqatask1\OneDrive - The University of Queensland\Desktop\CMM_Projects_Data\Outputs\eline\Bob\results" --file-extension tiff --ignored stitched scale --field Area Feret FeretX FeretY FeretAngle MinFeret Angle AR Round "Circ." --threshold "90" --subtract "12" --graph-min-x "0.01" --graph-bins-n-Feret "20" --graph-bins-n-AR "25" --circularity-min "0" --circularity-max "1"