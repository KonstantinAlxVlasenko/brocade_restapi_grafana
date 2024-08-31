import os
import pickle
from typing import Any

NS_FILENAME = 'nameserver.pickle'
NS_DIR = os.path.dirname(os.path.abspath(__file__))


def load_object(dirname: str, filename: str) -> Any:
    """Functions is used to load an object from the pickle file.

    Args:
        dirname (str): directory of the pickle file
        filename (str): name of the pickle file

    Returns:
        Any: the loaded object
    """

    filpath = os.path.join(dirname, filename)
    # Reading the object back from the file
    with open(filpath, "rb") as file:
        loaded_obj = pickle.load(file)
    print(f'Object successfully loaded from "{filename}"')
    return loaded_obj


def save_object(obj: Any, dirname: str, filename: str) -> None:
    """Function is used to save an object to the pickle file.

    Args:
        obj (Any): object to be saved
        dirname (str): directory of the pickle file
        filename (str): name of the pickle file
    """
    
    filpath = os.path.join(dirname, filename)
    # Writing the object to a file using pickle
    with open(filpath, 'wb') as file:
        pickle.dump(obj, file)
        print(f'Object successfully saved to "{filename}"')


def create_nameserver(ns_dir=NS_DIR, ns_filename=NS_FILENAME):
    """Function is used to create an empty nameserver file if it does not exist.
    Nameserver file contains a dictionary with the IP address as key and the chassis name as value.

    Args:
        ns_dir (str, optional): directory of the pickle file. Defaults to NS_DIR.
        ns_filename (str, optional): name of the pickle file. Defaults to NS_FILENAME.
    """    
 
    ns_empty_dct = {}
    ns_filepath = os.path.join(ns_dir, ns_filename)

    if not os.path.exists(ns_filepath):
        print('Creating chname_ip_db derfault file')
        save_object(ns_empty_dct, ns_dir, ns_filename)


def update_nameserver(nameserver_dct, ch_parser, ns_dir=NS_DIR, ns_filename=NS_FILENAME) -> None:
    """Function is used to change the nameserver file.
    Add new chassis name of the ip address or update existing one.
    If the nameserver file is changed the file is saved.

    Args:
        nameserver_dct (_type_): current nameserver dictionary.
        ch_parser (_type_): chassis parser file containing the ip address and the chassis name.
        ns_dir (str): directory of the pickle file. Defaults to NS_DIR.
        ns_filename (str): name of the pickle file. Defaults to NS_FILENAME.
    """

    if not ch_parser.ch_name:
        return
    sw_ipaddress = ch_parser.sw_telemetry.sw_ipaddress
    if not nameserver_dct.get(sw_ipaddress) or nameserver_dct[sw_ipaddress] != ch_parser.ch_name:
        nameserver_dct[sw_ipaddress] = ch_parser.ch_name
        save_object(nameserver_dct, ns_dir, ns_filename)