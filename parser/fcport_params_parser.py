import re
from typing import Dict, List, Optional, Self, Tuple, Union

from .base_parser import BaseParser
from .switch_parser import SwitchParser

from collection.switch_telemetry_request import SwitchTelemetryRequest


class FCPortParametersParser(BaseParser):
    """
    Class to create fc port parameters dictionaries.


    Attributes:
        sw_telemetry: set of switch telemetry retrieved from the switch.
        sw_parser: switch parameters retrieved from the sw_telemetry.
        port_owner: dictonary with port name as key and switchname to which port belongs to as value.
        fcport_params: fc port parameters dictionary ({vf_id:{slot_port_id:{param1: value1, param2: value2}}}).
        fcport_params_parser: fc port parameters class instance retrieved from the sw_telemetry (current class instance to find delta).
    """

    FC_INTERFACE_LEAFS = ['wwn', 'name', 'pod-license-status', 'pod-license-state', 'is-enabled-state', 'persistent-disable', 
                          'port-health', 'le-domain', 'port-peer-beacon-enabled', 'port-type-string', 'reserved-buffers',
                          'auto-negotiate', 'speed', 'max-speed', 'neighbor-node-wwn', 'long-distance', 'edge-fabric-id',
                          'qos-enabled', 'compression-configured', 'encryption-enabled', 'compression-active', 'encryption-active',
                          'credit-recovery-enabled', 'credit-recovery-active', 'fec-active', 'vc-link-init', 'npiv-enabled',
                          'trunk-port-enabled'
                          ]
    
    PORT_TYPE_ID = {0: 'Unknown',
                    7: 'E-Port',
                    10: 'G-Port',
                    11: 'U-Port',
                    15: 'F-Port',
                    16: 'L-Port',
                    17: 'FCoE Port',
                    19: 'EX-Port',
                    20: 'D-Port',
                    21: 'SIM Port',
                    22: 'AF-Port',
                    23: 'AE-Port',
                    25: 'VE-Port',
                    26: 'Ethernet Flex Port',
                    29: 'Flex Port',
                    30: 'N-Port',
                    32768: 'LB-Port'}
    

    LONG_DISTANCE_LEVEL = {0: 'LD Disabled',
                            1: 'L0',
                            2: 'L1',
                            3: 'L2',
                            4: 'LE',
                            5: 'L0.5',
                            6: 'LD',
                            7: 'LS'}
    

    PHYSICAL_STATE_ID = {'offline': 0, 'online': 1, 'testing': 2, 'faulty': 3, 'e_port': 4, 'f_port': 5, 
                         'segmented': 6, 'unknown': 7, 'no_port': 8, 'no_module': 9, 'laser_flt': 10, 
                         'no_light': 11, 'no_sync': 12, 'in_sync': 13, 'port_flt': 14, 'hard_flt': 15, 
                         'diag_flt': 16, 'lock_ref': 17, 'mod_inv': 18, 'mod_val': 19, 'no_sigdet': 20}

    FC_PORT_PARAMS_CHANGED = ['port-speed-hrf', 'long-distance-level', 'neighbor-node-wwn', 'neighbor-port-wwn',
                              'physical-state', 'port-enable-status', 'port-name', 'port-type', 'speed', 'max-speed']
    
    BITS_TO_MBYTES = {8_000_000_000: 810,
                      16_000_000_000: 1622,
                      32_000_000_000: 3243,
                      64_000_000_000: 6487}
    
    
    def __init__(self, sw_telemetry: SwitchTelemetryRequest, sw_parser: SwitchParser, fcport_params_prev: Self = None):
        """
        Args:
            sw_telemetry: set of switch telemetry retrieved from the switch.
            sw_parser (BrocadeSwitchParser): switch parameters retrieved from the sw_telemetry.
            fcport_params_prev (FCPortParametersParser): 
        """
        
        super().__init__(sw_telemetry)
        self._sw_parser: SwitchParser = sw_parser
        self._port_owner = self._get_ports_owner()
        self._fcport_params = self. _get_port_params_values()
        if self.fcport_params:
            self._fcport_params_changed = self._get_changed_fcport_params(fcport_params_prev)
        else:
            self._fcport_params_changd = {}
            
    
    def _get_ports_owner(self) -> Dict[str, Union[int, str]]:
        """
        Method creates ports owner (switchname) dictionary for switches in VF mode.
        If VF is disabled method returns empty dictionary.
        
        Returns:
            dict: Dictonary with port name as key and switchname to which port belongs to as value.
        """

        port_owner_dct = {}
        for fc_sw in self.sw_parser.fc_switch.values():
            if fc_sw.get('port-member-list'):
                current_sw_details_dct = {'switch-name': fc_sw['switch-name'],
                                          'switch-wwn': fc_sw['switch-wwn'],
                                          'fabric-user-friendly-name': fc_sw['fabric-user-friendly-name']}
                port_member_lst = fc_sw['port-member-list']
                current_sw_port_owner_dct = {port: current_sw_details_dct for port in port_member_lst}
                port_owner_dct.update(current_sw_port_owner_dct)
        return port_owner_dct


    def _get_port_params_values(self) -> Dict[int, Dict[str, Dict[str, Optional[Union[str, int]]]]]:
        """
        Method retrieves each fc port parameters and status.
        
        Returns:
            dict: FC port parameters. Dictionary of dictionaries of dictionaries.
                External dictionary keys are vf_ids (if vf mode is disabled then vf-id is -1).
                First level nested dictionary keys are slot_port_numbers.
                Second level nested dictionary keys are fc port parameters names.
        """
        
        fcport_params_dct = {}

        for vf_id, fc_interface_telemetry in self.sw_telemetry.fc_interface.items():
            if fc_interface_telemetry.get('Response'):
                # list with fc_interface containers for the each port in the vf_id switch
                fc_interface_container_lst = fc_interface_telemetry['Response']['fibrechannel']
                fcport_params_dct[vf_id] = {}
                
                for fc_interface_container in fc_interface_container_lst:
                    # slot_port_number in the format 'slot_number/port_number' (e.g. '0/1')
                    slot_port_number = fc_interface_container['name']
                    # split slot and port number
                    slot_number, port_number = slot_port_number.split('/')
                    # drop leading '0x' from the port id value (e.g. '0x030100')
                    port_fcid = re.search('0x(.+)', fc_interface_container['fcid-hex']).group(1)
                    # convert speed from bps to gbps
                    port_max_speed = int(fc_interface_container['max-speed']/1000_000_000)
                    port_speed_gbps = int(fc_interface_container['speed']/1000_000_000)
                    # add leading 'N' or closing 'G' to the port_seed value
                    port_speed_gbps_hrf = FCPortParametersParser._label_auto_fixed_speed_mode(port_speed_gbps, fc_interface_container['auto-negotiate'])
                    # The Fibre Channel WWN of the neighbor port
                    # neighbor_port_wwn = ', '.join(fc_interface_container['neighbor']['wwn']) if fc_interface_container['neighbor'] else None
                    neighbor_port_wwn = fc_interface_container['neighbor']['wwn'] if fc_interface_container['neighbor'] else None
                    neighbor_port_wwn_str = '\n'.join(sorted(neighbor_port_wwn, reverse=True)) if neighbor_port_wwn else ""
                    # port owner (remove closing '.')
                    sw_details_dct = self._get_port_owner(slot_port_number, vf_id)
                    # dynamic or static portname
                    port_name = fc_interface_container['user-friendly-name'].rstrip('.')
                    # port enabled or disabled
                    port_enable_status, port_enable_status_id = FCPortParametersParser._get_port_enable_status(fc_interface_container)
                    # online, offline, faulty, no_module, laser_flt, no_light, no_sync, in_sync, mod_inv, mod_val etc
                    physical_state = FCPortParametersParser._get_port_physical_state(fc_interface_container)
                    # flag if fc port is enabled but has no device connected
                    nodevice_enabled_port_flag = FCPortParametersParser._get_nodevice_enabled_port_flag(fc_interface_container)
                    # uport_gport_enabled_flag = BrocadeFCPortParametersParser._get_uport_gport_enabled_flag(fc_interface_container)
                    uport_gport_enabled_flag = self._get_uport_gport_enabled_flag(fc_interface_container, vf_id)
                    
                    if fc_interface_container['is-enabled-state']:
                        self.sw_parser.fc_switch[vf_id]['enabled-port-quantity'] += 1

                    if fc_interface_container['physical-state'] == 'online':
                        self.sw_parser.fc_switch[vf_id]['online-port-quantity'] += 1
                    
                    pod_license_status_id = FCPortParametersParser._get_pod_license_id(fc_interface_container)
                    physical_state_status_id =  FCPortParametersParser._get_physical_state_status_id(fc_interface_container)

                    
                    # create dictionary with current port parameters 
                    fcport_params_current_dct = {
                        # 'swicth-name': sw_name,
                        'vf-id': vf_id,
                        'port-index': fc_interface_container['default-index'],
                        'slot-number': int(slot_number),
                        'port-number': int(port_number),
                        'port-name': port_name,
                        'port-id': port_fcid, 
                        'port-speed-hrf': port_speed_gbps_hrf,
                        'port-speed-gbps': port_speed_gbps,
                        'port-max-speed-gbps': port_max_speed,
                        'port-throughput-megabytes': FCPortParametersParser.get_port_throughput_megabytes(fc_interface_container['speed']),
                        'physical-state': physical_state,
                        'physical-state-id': FCPortParametersParser.PHYSICAL_STATE_ID.get(fc_interface_container['physical-state'], 100),
                        'port-type-id': fc_interface_container['port-type'],
                        'port-type': FCPortParametersParser.PORT_TYPE_ID.get(fc_interface_container['port-type'], fc_interface_container['port-type']),
                        'enabled-port-type-id': FCPortParametersParser._get_enabled_port_type_id(fc_interface_container),
                        'neighbor-port-wwn': neighbor_port_wwn,
                        'neighbor-port-wwn-str': neighbor_port_wwn_str,
                        'port-enable-status': port_enable_status,
                        'port-enable-status-id': port_enable_status_id,
                        'nodevice-enabled-port': nodevice_enabled_port_flag,
                        'uport-gport-enabled': uport_gport_enabled_flag,
                        'long-distance-level': FCPortParametersParser.LONG_DISTANCE_LEVEL.get(fc_interface_container['long-distance']),
                        'pod-license-status-id': pod_license_status_id,
                        'physical-state-status-id': physical_state_status_id,
                        'physical-state-status': FCPortParametersParser.STATUS_ID.get(physical_state_status_id),
                        }
                    
                    fcport_params_current_dct.update(sw_details_dct)
                    # dictionary with unchanged values from fc_interface_container
                    fcport_params_current_default_dct = {leaf: fc_interface_container.get(leaf) for leaf in FCPortParametersParser.FC_INTERFACE_LEAFS}
                    fcport_params_current_dct.update(fcport_params_current_default_dct)
                    # add current port status dictionary to the summary port status dictionary with vf_id and slot_port as consecutive keys
                    fcport_params_dct[vf_id][fc_interface_container['name']] = fcport_params_current_dct
        return fcport_params_dct


    @staticmethod
    def get_port_throughput_megabytes(port_speed: int):
        """Method converts port_speed value to throughput in MB/s.

        Args:
            port_speed (int): port speed in bps

        Returns:
            int: throughput in MB/s.
        """

        if FCPortParametersParser.BITS_TO_MBYTES.get(port_speed):
            return FCPortParametersParser.BITS_TO_MBYTES[port_speed]
        elif port_speed is not None:
            return port_speed/10_000_000


    def _get_changed_fcport_params(self, other) -> Dict[int, Dict[str, Dict[str, Optional[Union[str, int]]]]]:
        """
        Method detects if port paramters from the FC_PORT_PARAMS_CHANGED list have been changed for each switch port.
        It compares port parameters of two instances of BrocadeFCPortParametersParser class.
        All changed parameters are added to to the dictionatry including current and previous values.
        
        Args:
            other {BrocadeFCPortParametersParser}: fc port parameters class instance retrieved from the previous sw_telemetry.
        
        Returns:
            dict: FC ports parameters change dictionary. Any port with changed parameters are in this dictionary.
        """

        # switch ports with changed parameters
        fcport_params_changed_dct = {}

        # other is not exist (for examle 1st iteration)
        # other is not BrocadeFCPortParametersParser type
        # other's fcport_params atrribute is empty
        if other is None or str(type(self)) != str(type(other)) or not other.fcport_params:
            return None
        
        # check if other is for the same switch
        elif self.same_chassis(other):
            for vf_id, fcport_params_vfid_now_dct in self.fcport_params.items():

                fcport_params_changed_dct[vf_id] = {}

                # if there is no vf_id in other check next vf_id 
                if vf_id not in other.fcport_params:
                    continue

                # port params of the vf_id switch for the previous telemetry    
                fcport_params_vfid_prev_dct = other.fcport_params[vf_id]
                # timestamps
                time_now = self.telemetry_date + ' ' + self.telemetry_time
                time_prev = other.telemetry_date + ' ' + other.telemetry_time
                # add changed port parameters for the current vf_id
                fcport_params_changed_dct[vf_id] = FCPortParametersParser.get_changed_vfid_ports(fcport_params_vfid_now_dct, fcport_params_vfid_prev_dct, 
                                                                                        changed_keys=FCPortParametersParser.FC_PORT_PARAMS_CHANGED, 
                                                                                        const_keys=FCPortParametersParser.FC_PORT_PATH, 
                                                                                        time_now=time_now, time_prev=time_prev)
        return fcport_params_changed_dct


    @staticmethod
    def _get_nodevice_enabled_port_flag(fc_interface_container):
        """
        Method to check if fc port is enabled but has no device connected. 
        
        Args:
            fc_interface_container {dict}: container with fc port parameters leafs.
        
        Returns:
            int: 1 if fc port is enabled but has no device connected.
                0 in all other cases.
        """

        if fc_interface_container['is-enabled-state'] and not fc_interface_container['neighbor']:
            return 1
        else:
            return 0
        

    def _get_uport_gport_enabled_flag(self, fc_interface_container, vf_id):
        """
        Method to check if fc port is enabled but has not yet assumed a specific function in the fabric.
        Port type is U-Port or G-port. 10: 'G-Port', 11: 'U-Port'
        
        Args:
            fc_interface_container {dict}: container with fc port parameters leafs.
        
        Returns:
            int: 1 if fc port is enabled but port type is U-Port or G-Port.
                0 in all other cases.
        """



        if fc_interface_container['is-enabled-state'] and fc_interface_container['port-type'] in [10, 11]:
            self.sw_parser.fc_switch[vf_id]['uport-gport-enabled-quantity'] += 1
            if fc_interface_container['port-type'] == 11:
                return 1
            elif fc_interface_container['port-type'] == 10:
                return 2
        else:
            return 0
        

    @staticmethod
    def _get_enabled_port_type_id(fc_interface_container: Dict[str, Optional[Union[str,int]]]) -> Optional[int]:
        """
        Method returns port-type-id for enabled port.
        
        Args:
            fc_interface_container {dict}: container with fc port parameters leafs.
        
        Returns:
            int: port-type-id for enabled port.
        """
        
        if fc_interface_container['is-enabled-state']:
            return fc_interface_container['port-type']


    @staticmethod
    def _get_port_physical_state(fc_interface_container: Dict[str, Optional[Union[str,int]]]) -> Optional[str]:
        """
        Method to get the physical state of the port 
        (online, offline, ,faulty, no_module, laser_flt, no_light, no_sync, in_sync, mod_inv, mod_val etc). 
        
        Args:
            fc_interface_container {dict}: container with fc port parameters leafs.
        
        Returns:
            str: Physical state of the port 
                (online, offline, ,faulty, no_module, laser_flt, no_light, no_sync, in_sync, mod_inv, mod_val etc).
        """  

        if fc_interface_container.get('physical-state'):
            # capitalize each segment of the string to correspond to the physical state in switchshow output
            physical_state = fc_interface_container['physical-state'].split('_')
            physical_state = [symbol.capitalize() for symbol in physical_state]
            physical_state = '_'.join(physical_state)
            return physical_state


    @staticmethod
    def _get_port_enable_status(fc_interface_container: Dict[str, Optional[Union[str,int]]]) -> Optional[str]:
        """
        Method to get port enable status ('Enabled', 'Disabled', 'Disabled (Persistent)'). 
        
        Args:
            fc_interface_container {dict}: container with fc port parameters leafs.
        
        Returns:
            str: Port enable status ('Enabled', 'Disabled', 'Disabled (Persistent)')
        """        

        if fc_interface_container['is-enabled-state'] is None:
            port_enable_status = None
            port_enable_status_id = None
        elif fc_interface_container['is-enabled-state']:
            port_enable_status = 'Enabled'
            port_enable_status_id = 1
        else:
            port_enable_status = 'Disabled'
            port_enable_status_id = 0
            if fc_interface_container['persistent-disable']:
                port_enable_status = port_enable_status + ' (Persistent)'
                port_enable_status_id = -1
        return port_enable_status, port_enable_status_id

    
    def _get_port_owner(self, slot_port_number: str, vf_id: int) -> Optional[str]:
        """
        Method to get slot_port_number switchname owner.
        
        Args:
            slot_port_number {str}: slot and port number in the format'slot/port' (e.g. '0/1').
                                    vf_id: switch vf_id.
        
        Returns:
            str: Switchname to which port belongs to.
        """

        sw_details_keys = ['switch-name', 'switch-wwn', 'fabric-user-friendly-name']

        if self.port_owner:
            sw_details_dct = self.port_owner[slot_port_number]
        elif vf_id == -1 and self.sw_parser.fc_switch[vf_id].get('user-friendly-name'):
            sw_details_dct = {key: self.sw_parser.fc_switch[vf_id][key] for key in sw_details_keys}
            # sw_name = self.sw_parser.fc_switch[vf_id]['user-friendly-name']
        else:
            sw_details_dct = {key: None for key in sw_details_keys}
            # sw_name = None
        return sw_details_dct
        

    @staticmethod
    def _label_auto_fixed_speed_mode(port_speed: int, auto_negotiate_mode: Optional[Union[str, int]]) -> Optional[str]: 
        """
        Method to label the port_speed value with leading 'N' or closing 'G' based on the auto-negotiate mode.
        
        Args:
            port_speed {int}: port speed value in gbps.
            auto_negotiate_mode {int}: auto-negotiate mode off(0), on (1).
        
        Returns:
            str: String in format 'Nx' or 'xG'.
        """

        if port_speed is None:
            return None
        
        if auto_negotiate_mode:
            port_speed = 'N' + str(port_speed)
        else:
            port_speed = str(port_speed) + 'G'
        return port_speed


    @staticmethod
    def _get_pod_license_id(fc_interface_container: Dict[str, Optional[Union[str,int]]]) -> Optional[int]:

        if fc_interface_container.get('pod-license-state'):
            if fc_interface_container['pod-license-state'] == 'reserved':
                return 1
            elif fc_interface_container['pod-license-state'] == 'released':
                return 0
            
        if fc_interface_container.get('pod-license-status') is not None:
            if fc_interface_container['pod-license-status']:
                return 3
            else:
                return 2
            
        return 4
        

    @staticmethod
    def _get_physical_state_status_id(fc_interface_container):
        """
        Method to check port physical state status depending on port enable state.
        Port physical states: offline, online, testing, faulty, e_port, f_port, 
                            segmented, unknown, no_port, no_module, laser_flt, 
                            no_light, no_sync, in_sync, port_flt, hard_flt, 
                            diag_flt, lock_ref, mod_inv, mod_val, no_sigdet
        
        Statuses: ok, unknown, warning, critical
                            
        Args:
            fc_interface_container {dict}: container with fc port parameters leafs.
        
        Returns:
            int: 1 (ok), 2 (unknown), 3 (warning), 4 (critical)
        """

        # unknown status
        if not fc_interface_container['physical-state']:
            return 2
        
        phys_state = fc_interface_container['physical-state'].lower()
        
        # ok status
        if phys_state in ['online', 'e_port', 'f_port']:
            return 1
        
        # critical status
        if phys_state in ['faulty', 'laser_flt', 'port_flt', 'hard_flt', 
                          'diag_flt', 'lock_ref', 'mod_inv', 'mod_val', 'segmented']:
            return 4

        # unknown status
        if phys_state in ['unknown']:
            return 2
        
        # warning status
        if phys_state in ['testing']:
            return 3
        
        if phys_state in ['no_sync', 'in_sync']:
            # critical status
            if fc_interface_container['is-enabled-state']:
                return 4
            # warning status
            else:
                return 3 
        
        if phys_state in ['offline', 'no_port', 'no_module', 'no_light', 'no_sigdet']:
            # warning status
            if fc_interface_container['is-enabled-state']:
                return 3
            # ok status
            else:
                return 1
        # unknown status
        return 2

    
    @property
    def sw_parser(self):
        return self._sw_parser
    

    @property
    def port_owner(self):
        return self._port_owner
    

    @property
    def fcport_params(self):
        return self._fcport_params
    
    @property
    def fcport_params_changed(self):
        return self._fcport_params_changed