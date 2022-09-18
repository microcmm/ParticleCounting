1. Preprocessing:

    Image preparation needs some work. As images come from different types of instruments, the type of noises in each type is different. As a result, reducing noise for all type of images is not easy. A possible solution is to remove noise based on type of image. A new parameter can be introduced to the pc_main.py that indicate the type of instrument generating the input images. Then appropriate noise reduction algorithm can be applied. 


2. UI

    The users have to execute scripts to run the script. A better way is to write some user interface to invovke the script. It can be Fiji macros or javascript UI for the parameters.