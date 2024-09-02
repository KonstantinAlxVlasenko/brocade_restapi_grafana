"""
SAN: Ost_stg
Fabric: A
Switch name: n3-g620-117-stg-f1
Switch IP: 10.213.164.101
"""

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
from collection.switch_metrics_collection import collect_switch_metrics

print(os.path.basename(__file__))

if __name__ == '__main__':
    collect_switch_metrics(sw_ipaddress="10.213.164.101")
