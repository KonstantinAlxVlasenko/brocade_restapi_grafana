import sys
import os


# getting the name of the directory
# where the this file is present.
current = os.path.dirname(os.path.realpath(__file__))


# Getting the parent directory name
# where the current directory is present.
parent = os.path.dirname(current)
# archive = os.path.join(current, 'ar')

# adding the parent directory to 
# the sys.path.
sys.path.append(parent)

# now we can import the collection module in the parent
import db_operations as db


pickle_tlm_file = db.load_object(db.ARCHIVE_DIR, 'n3-g620-118-stg-f2-telemetry.pickle')
pickle_prs_file = db.load_object(db.ARCHIVE_DIR, 'n3-g620-118-stg-f2-parser.pickle')
pickle_rs_file = db.load_object(db.ARCHIVE_DIR, 'n3-g620-118-stg-f2-request.pickle')
# pickle_tlm_correct_file = db.load_object(current, 'n3-g620-118-stg-f2-telemetry_correct.pickle')


# print(pickle_file.__dict__)

# print(pickle_file.sw_telemetry.__dict__)
# print(dir(pickle_file.sw_telemetry))

# print(dir(pickle_file.brocade_parser_prev))

# print(dir(pickle_file.brocade_parser_prev.ch_parser.sw_telemetry))


# print(dir(pickle_file.brocade_parser_prev.sw_telemetry))



# print(dir(pickle_prev_file.brocade_parser_prev.brocade_parser_prev))

# print(dir(pickle_tlm_file.chassis.__dict__))

# print(pickle_tlm_file.__dict__)
# print(dir(pickle_tlm_file.fc_interface))
print(pickle_tlm_file.fc_interface)


# print(pickle_tlm_correct_file.fc_interface))

