# -*- coding: utf-8 -*-
"""
Created on Wed Nov  9 13:19:40 2022

@author: uqatask1
"""

from PIL import Image
 

def should_ignore(filename):
    img = Image.open(filename)
    #r, g, b = img.split()
    #len(img.histogram())
    ### 256 ###
    hist_vals = img.histogram()
    
    max_val = max(hist_vals)
    idx_max = hist_vals.index(max_val)
    
    ignore = False
    if (idx_max == len(hist_vals)-1):
        ignore = True
    
    return ignore

print(should_ignore(r"C:\Users\uqatask1\Desktop\CMM_Projects_Data\Inputs\Hitachi 7700\#20\1P202203291517.tif"))