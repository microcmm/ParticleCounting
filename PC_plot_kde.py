# -*- coding: utf-8 -*-
"""
Created on Fri Jul 15 11:11:05 2022

@author: uqatask1
"""

import numpy as np
import pandas as pd
import seaborn as sns
import matlibplot as plt


#Read csv
pc_df = pd.read_csv("Outputs_NP1_mod_min3_DSX.csv")


# plot for density distribution, despine top, bottom, L, R, all set to false to give border

sns.set_style=("ticks")
g = sns.displot(pc_df, x="Feret", kind="kde", log_scale=(True), color="lime", height=3.5, aspect=1, facet_kws=dict(margin_titles=True),)
sns.despine(top=False, right=False, left=False, bottom=False)

g.set_axis_labels(x_var="Diameter $(µm)$", y_var="Frequency",)
g.ax.set_xlim(0.1, 100)

