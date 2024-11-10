import os
import pickle
from typing import Any
from parser.chassis_parser import ChassisParser

NS_FILENAME = 'nameserver.pickle'
DATABASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARCHIVE_DIR = os.path.join(DATABASE_DIR, 'archive')

SWITCH_LOG_DIR = os.path.join(DATABASE_DIR, 'switch_log')
MAX_SWITCH_LOG_LINES = 103
SWITCH_LOG_FILENAME_EXT = '_swlog.pickle'



def file_exist(dirname: str, filename: str) -> bool:

    filpath = os.path.join(dirname, filename)
    return os.path.exists(filpath)



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

    # add file extension
    if not filename.endswith(".pickle"):
        filename += '.pickle'

    if not os.path.isdir(dirname): 
        os.makedirs(dirname) 
    
    filpath = os.path.join(dirname, filename)
    # Writing the object to a file using pickle
    with open(filpath, 'wb') as file:
        pickle.dump(obj, file)
        print(f'Object successfully saved to "{filename}"')
        

def create_nameserver(ns_dir=DATABASE_DIR, ns_filename=NS_FILENAME):
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


def update_nameserver(ch_parser: ChassisParser, ns_dir=DATABASE_DIR, ns_filename=NS_FILENAME) -> None:
    """Function is used to change the nameserver file.
    Loads current nameserver from the database.
    Add new chassis name of the ip address or update existing one.
    If the nameserver file is changed then file is saved.

    Args:
        ch_parser (ChassisParser): chassis parser file containing the ip address and the chassis name.
        ns_dir (str): directory of the pickle file. Defaults to NS_DIR.
        ns_filename (str): name of the pickle file. Defaults to NS_FILENAME.
    """

    if not ch_parser.ch_name:
        return
    sw_ipaddress = ch_parser.sw_telemetry.sw_ipaddress

    # load current nameserver from the database
    nameserver_dct = load_object(ns_dir, ns_filename)
    if not nameserver_dct.get(sw_ipaddress) or nameserver_dct[sw_ipaddress] != ch_parser.ch_name:
        nameserver_dct[sw_ipaddress] = ch_parser.ch_name
        save_object(nameserver_dct, ns_dir, ns_filename)


def create_directory_if_not_exists(directory_path: str) -> None:
    """Создает папку по указанному пути, если она не существует.

    Args:
        directory_path (str): Абсолютный путь к папке.
    """
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        print(f"Папка '{directory_path}' успешно создана.")
    else:
        print(f"Папка '{directory_path}' уже существует.")


class LimitedList(list):
    def __init__(self, max_size):
        super().__init__()
        self.max_size = max_size

    def append(self, item):
        if len(self) >= self.max_size:
            self.pop(0)  # Удаляем первый элемент, если достигнут предел
        super().append(item)

    def extend(self, iterable):
        for item in iterable:
            self.append(item)  # Используем переопределенный append

    def insert(self, index, item):
        if len(self) >= self.max_size:
            self.pop(0)  # Удаляем первый элемент, если достигнут предел
        super().insert(index, item)