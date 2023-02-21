To run headless:
----------------

Linux:
======
python3 pc_main.py pc-fiji --fiji-path /home/hoangnguyen177/bin/ImageJ-linux64 --pixel-width 0.1108 --pixel-height 0.1108 --pixel-unit μm --min-particle-size 3 --input-path /home/hoangnguyen177/Desktop/working/RCC/CMM_Projects_data/NP_Characterisation_20220519/NP1/ --output-path /home/hoangnguyen177/Desktop/working/RCC/CMM_Projects/OlympusDSX1000-output-2022-05-20/NP1 --file-extension tiff --ignored stiched scale --field Area Feret FeretX FeretY FeretAngle MinFeret Angle AR Round "Circ."

Windows:
========
python3 .\pc_main.py pc-fiji --fiji-path C:\fiji\ImageJ-win64.exe --pixel-width 0.1108 --pixel-height 0.1108 --pixel-unit µm --min-particle-size 3 --input-path "C:\Users\Ngoc Thao\Downloads\hoang-downloads\npc\test" --output-path "C:\Users\Ngoc Thao\Downloads\hoang-downloads\npc\test\output" --file-extension tiff --ignored stiched scale --field Area Feret FeretX FeretY FeretAngle MinFeret Angle AR Round "Circ."

To run with display:
--------------------
ImageJ-linux64 --ij2 --run /home/hoangnguyen177/Desktop/working/RCC/CMM_Projects/PCount/particleCounting_gui.py

or run it from ImageJ
