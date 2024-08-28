import os
import pickle


CHNAME_IP_DB_FILENAME = 'chname_ip_db.pickle'
CHNAME_IP_DB_DIR = os.path.dirname(os.path.abspath(__file__))


def load_object(dirname, filename):
    filpath = os.path.join(dirname, filename=CHNAME_IP_DB_FILENAME)
    # Reading the object back from the file
    with open(filpath, "rb") as file:
        loaded_obj = pickle.load(file)
    print(f'Object successfully loaded from "{filename}"')
    return loaded_obj




def save_object(obj, dirname, filename):
    
    filpath = os.path.join(dirname, filename)
    # Writing the object to a file using pickle
    with open(filpath, 'wb') as file:
        pickle.dump(obj, file)
        print(f'Object successfully saved to "{filename}"')




def create_chname_ip_db_file(db_dir=CHNAME_IP_DB_DIR, chname_ip_db_filename=CHNAME_IP_DB_FILENAME):

    
    chname_ip_default_dct = {}
    
    chname_ip_db_filepath = os.path.join(db_dir, chname_ip_db_filename)

    if not os.path.exists(chname_ip_db_filepath):
        print('Creating chname_ip_db derfault file')
        save_object(chname_ip_default_dct, db_dir, chname_ip_db_filename)


def update_chname_ip_db(chname_ip_dct, ch_parser, chname_ip_db_dir=CHNAME_IP_DB_DIR, chname_ip_db_filename=CHNAME_IP_DB_FILENAME):

    if not ch_parser.ch_name:
        return
    sw_ipaddress = ch_parser.sw_telemetry.sw_ipaddress
    if not chname_ip_dct.get(sw_ipaddress) or chname_ip_dct[sw_ipaddress] != ch_parser.ch_name:
        chname_ip_dct[sw_ipaddress] = ch_parser.ch_name
        save_object(chname_ip_dct, chname_ip_db_dir, chname_ip_db_filename)