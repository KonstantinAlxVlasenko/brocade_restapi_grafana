# -*- coding: utf-8 -*-
"""
Created on Thu Mar 21 17:44:17 2024

@author: kavlasenko
"""

import pickle
import os

script_dir = r'E:\Documents\05.PYTHON\Projects\brocade_restapi_grafana\drafts'
# Change the current working directory
os.chdir(script_dir)


def save_object(obj, dirname, filename):
    
    filpath = os.path.join(dirname, filename)
    # Writing the student object to a file using pickle
    with open(filpath, 'wb') as file:
        pickle.dump(obj, file)
        print(f'Object successfully saved to "{filename}"')

    
def load_object(dirname, filename):
    filpath = os.path.join(dirname, filename)
    # Reading the student object back from the file
    with open(filpath, "rb") as file:
        loaded_obj = pickle.load(file)
    print(f'Object successfully loaded from "{filename}"')
    return loaded_obj