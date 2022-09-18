This repository contains a number of scripts that automates the steps of preping images and counting particles in the given images.

Disclaimer:
-----------
This repository is still under development.

Requirements:
-------------
* Python 3 (preferred 3.10 or later)
* Fiji (1.53)

Installation:
-------------
1. Fiji can be installed at C:\fiji (for Windows) or /opt/fiji
2. Clone this repository (C:\Users\ **myusername** \ParticleCounting)
3. Once Python3.10 is installed
    
    > cd  C:\Users\ **myusername** \ParticleCounting

4. Create virtual environment
    
    > python3 -m venv venv

In *Linux*

    source ./venv/bin/activate

In *Windows*

    .\venv\Scripts\activate

5. Install dependencies (first time)  
    
    > pip3 install -r requirements.txt

Usage:
------
Assume you are already inside the virtual environment

*Linux:
> python3 pc_main.py pc-fiji --fiji-path /opt/fiji/bin/ImageJ-linux64 --pixel-width 0.1108 --pixel-height 0.1108 --pixel-unit μm --min-particle-size 3 --graph-min-x 0.01 --graph-max-x 100 --circularity-min 0.2 --input-path **input_path** --output-path **output_path** --file-extension tiff --ignored stiched scale --field Area Feret FeretX FeretY FeretAngle MinFeret Angle AR Round "Circ."

*Windows:
> python3 .\pc_main.py pc-fiji --fiji-path C:\fiji\ImageJ-win64.exe --pixel-width 0.1108 --pixel-height 0.1108 --pixel-unit µm --min-particle-size 3  --graph-min-x 0.01 --graph-max-x 100 --circularity-min 0.2 --input-path "**input_path**" --output-path "**output_path**" --file-extension tiff --ignored stiched scale --field Area Feret FeretX FeretY FeretAngle MinFeret Angle AR Round "Circ."


To display help
> python3 pc_main.py pc-fiji --help

Output:
> usage: pc_main pc-fiji [-h] [--fiji-path FIJI_PATH] --input-path INPUT_PATH [--scratch {True,False}] [--output-path OUTPUT_PATH] [--keep-cropped-files {True,False}]
                       [--keep-threshold-files {True,False}] [--pixel-width PIXEL_WIDTH] [--pixel-height PIXEL_HEIGHT] [--pixel-unit {mm,μm,nm}]
                       [--min-particle-size MIN_PARTICLE_SIZE] [--file-extension FILE_EXTENSION] [--ignored IGNORED [IGNORED ...]]
                       [--fields {Area,Mean,StdDev,Mode,Min,Max,X,Y,XM,YM,Perim.,BX,BY,Width,Height,Major,Minor,Angle,Circ.,Feret,IntDen,Median,Skew,Kurt,%Area,RawIntDen,FeretX,FeretY,FeretAngle,MinFeret,AR,Round,Solidity} [{Area,Mean,StdDev,Mode,Min,Max,X,Y,XM,YM,Perim.,BX,BY,Width,Height,Major,Minor,Angle,Circ.,Feret,IntDen,Median,Skew,Kurt,%Area,RawIntDen,FeretX,FeretY,FeretAngle,MinFeret,AR,Round,Solidity} ...]]
                       [--graph-min-x GRAPH_MIN_X] [--graph-max-x GRAPH_MAX_X] [--circularity-min CIRCULARITY_MIN]

    Particle counting using Fiji

    options:
    -h, --help            show this help message and exit
    --fiji-path FIJI_PATH
                            Fiji path (default: None)
    --input-path INPUT_PATH
                            input path (default: None)
    --scratch {True,False}
                            scratch (default: False)
    --output-path OUTPUT_PATH
                            output path (default: None)
    --keep-cropped-files {True,False}
                            keeping cropped files (default: True)
    --keep-threshold-files {True,False}
                            keeping thresholded files (default: True)
    --pixel-width PIXEL_WIDTH
                            pixel width (default: None)
    --pixel-height PIXEL_HEIGHT
                            pixel height (default: None)
    --pixel-unit {mm,μm,nm}
                            pixel unit (default: μm)
    --min-particle-size MIN_PARTICLE_SIZE
                            the smallest particle size in pixels (default: None)
    --file-extension FILE_EXTENSION
                            file extension (default: tiff)
    --ignored IGNORED [IGNORED ...]
                            files to be ignored, without extension (default: None)
    --fields {Area,Mean,StdDev,Mode,Min,Max,X,Y,XM,YM,Perim.,BX,BY,Width,Height,Major,Minor,Angle,Circ.,Feret,IntDen,Median,Skew,Kurt,%Area,RawIntDen,FeretX,FeretY,FeretAngle,MinFeret,AR,Round,Solidity} [{Area,Mean,StdDev,Mode,Min,Max,X,Y,XM,YM,Perim.,BX,BY,Width,Height,Major,Minor,Angle,Circ.,Feret,IntDen,Median,Skew,Kurt,%Area,RawIntDen,FeretX,FeretY,FeretAngle,MinFeret,AR,Round,Solidity} ...]
                            list of fields to store in excel (default: None)
    --graph-min-x GRAPH_MIN_X
                            minimum value for graph x axis (default: 0.01)
    --graph-max-x GRAPH_MAX_X
                            maximum value for graph x axis (default: 100)
    --circularity-min CIRCULARITY_MIN
                            circularity lower limit (default: 0.2)




