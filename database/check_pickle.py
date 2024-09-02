import sys
import os


# getting the name of the directory
# where the this file is present.
current = os.path.dirname(os.path.realpath(__file__))


# Getting the parent directory name
# where the current directory is present.
parent = os.path.dirname(current)

# adding the parent directory to 
# the sys.path.
sys.path.append(parent)

# now we can import the collection module in the parent
import db_operations as db

pickle_file = db.load_object(current, 'n3-g620-118-stg-f2-parser.pickle')

# print(pickle_file.__dict__)

print(pickle_file.ch_parser.chassis)

