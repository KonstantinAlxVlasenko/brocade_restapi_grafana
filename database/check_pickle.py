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

# pickle_prev_file = db.load_object(current, 'n3-g620-118-stg-f2-prev-parser.pickle')

# print(pickle_file.__dict__)

# print(pickle_file.sw_telemetry.__dict__)
# print(dir(pickle_file.sw_telemetry))

# print(dir(pickle_file.brocade_parser_prev))

# print(dir(pickle_file.brocade_parser_prev.ch_parser.sw_telemetry))


# print(dir(pickle_file.brocade_parser_prev.sw_telemetry))



# print(dir(pickle_prev_file.brocade_parser_prev.brocade_parser_prev))


print((pickle_file.sw_parser.sw_telemetry))
