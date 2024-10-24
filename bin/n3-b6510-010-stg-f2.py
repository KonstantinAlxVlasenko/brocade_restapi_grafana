"""
SAN: Ost_stg
Fabric: B
Switch name: n3-b6510-010-stg-f2
Switch IP: 10.213.164.102
"""

SW_IP_ADDRESS = "10.213.164.102"

import sys
import os

from pathlib import Path

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
from collection.switch_metrics_collection import collect_switch_metrics


if __name__ == '__main__':
    current_filename = Path(__file__).stem
    collect_switch_metrics(sw_ipaddress=SW_IP_ADDRESS, initiator_filename=current_filename)
