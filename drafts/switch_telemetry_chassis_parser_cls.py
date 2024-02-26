# -*- coding: utf-8 -*-
"""
Created on Tue Feb 20 15:19:38 2024

@author: kavlasenko
"""

from datetime import datetime, date
from typing import List, Dict, Union


class BrocadeChassisParser:
    """
    Class to create chassis level parameters dictionaries.


    Attributes:
        sw_telemetry: set of switch telemetry retrieved from the switch
        chassis: chassis parameters dictionary
        ntp_server: clock server parameters dictioanry
        sw_license: dictionary with licenses installed on the switch
    """
    

    CHASSIS_LEAFS = ['chassis-user-friendly-name', 'chassis-wwn', 'serial-number', 
                     'vendor-serial-number', 'product-name', 'date', 'vf-enabled', 
                     'vf-supported', 'max-blades-supported']
    
    
    def __init__(self, sw_telemetry):
        """
        Args:
            sw_telemetry: set of switch telemetry retrieved from the switch
        """
        
        self._sw_telemetry = sw_telemetry
        self._chassis = self._get_chassis_value()
        if self.chassis:
            self._get_switch_value()
            self._get_vf_mode()
            self._get_timezone_value()
        self._ntp_server = self._get_ntp_server_value()
        self._sw_license = self._get_license_value()
        

    def _get_chassis_value(self) -> Dict[str, Union[str, int, bool]]:
        """
        Method extracts chassis parameters from the chassis module.
        
        Returns:
            Chassis parameters dictionary.
            Dictionary keys are CHASSIS_LEAFS. 
        """
        
        
        if self.sw_telemetry.chassis.get('Response'):
            container = self.sw_telemetry.chassis['Response']['chassis']
            chassis_dct = {key: container[key] for key in BrocadeChassisParser.CHASSIS_LEAFS}
            # leading 'Brocade' is added to the switch model  
            if chassis_dct.get('product-name'):
                chassis_dct['product-name'] = 'Brocade ' + chassis_dct['product-name'].capitalize()
            # date is splitted to date and time
            if chassis_dct.get('date'):
                chassis_dct['date'], chassis_dct['time'] = chassis_dct['date'].split('-')
            else:
                chassis_dct['time'] = None
            # switch serial number is OEM serial number otherwise Brocade serial number 
            chassis_dct['switch-serial-number'] = \
                chassis_dct['vendor-serial-number'] if chassis_dct.get('vendor-serial-number') else chassis_dct.get('serial-number')
        else:
            chassis_dct = {}
        return chassis_dct


    def _get_vf_mode(self) -> None:
        """
        Method adds virtual fabrics mode and logical switch number
        to the chassis parameters attribute.
        
        Returns:
            None. 
        """
        
        # if switch doesn't support virtual fabrics
        if self.chassis['vf-supported'] is False:
            self.chassis['virtual-fabrics'] = 'Not Applicable'
            self.chassis['ls-number'] = 0
        else: 
            # if virtual mode is enabled ls number is calculated by '_get_switch_value' method
            if self.chassis['vf-enabled'] is True:
                self.chassis['virtual-fabrics'] = 'Enabled'
            # if virtual mode is disabled ls number is 0
            elif self.chassis['vf-enabled'] is False:
                self.chassis['virtual-fabrics'] = 'Disabled'
                self.chassis['ls-number'] = 0
            else:
                self.chassis['virtual-fabrics'] = None
                if not 'ls-number' in self.chassis:
                    self.chassis['ls-number'] = None
                

    def _get_switch_value(self) -> None:
        """
        Method adds firmware version, swith type (model) and
        logical switch number to the chassis parameters attribute.
        
        Returns:
            None. 
        """

        for fc_switch_telemetry in self.sw_telemetry.fc_switch.values():
            if fc_switch_telemetry.get('Response'):
                
                fc_sw_container_lst = fc_switch_telemetry['Response']['fibrechannel-switch']
                
                for fc_sw in fc_sw_container_lst:
                    self.chassis['firmware-version'] = fc_sw['firmware-version']
                    # switchType
                    self.chassis['model'] = fc_sw['model']
        # logical switch number
        # if vf is disabled 'ls-number' is redefined as 0 in '_get_vf_mode' method
        self.chassis['ls-number'] = len(self.sw_telemetry.fc_switch.items())
                    

    def _get_timezone_value(self) -> None:
        """
        Method adds timezone to the chassis parameters attribute.
        If timezone is not defined hourOffset and minuteOffset are added as timezone.
        
        Returns:
            None. 
        """
        
        if self.sw_telemetry.ts_timezone['Response']:
            container = self.sw_telemetry.ts_timezone['Response']['time-zone']
            if container.get('name'):
                # timezone as timezone
                ts_tz = container['name']
            elif container.get('gmt-offset-hours') is not None \
                and container.get('gmt-offset-minutes') is not None:
                    # timezone as hours and mins offset
                    ts_tz = str(container.get('gmt-offset-hours')) \
                        + ':' + str(container.get('gmt-offset-minutes'))
            else:
                ts_tz = 'unknown'
        else:
            ts_tz = None
        
        self.chassis['time-zone'] = ts_tz   


    def _get_ntp_server_value(self) -> Dict[str, str]:
        """
        Method extracts ntp clock server settings from the clock-server module.
        
        Returns:
            NTP parameters dictionary.
            Dictionary contains defined and active ntp servers. 
        """
        
        ntp_dct = {}
        
        if self.sw_telemetry.clock_server.get('Response'):
            container = self.sw_telemetry.clock_server['Response']['clock-server']
            # active ntp server
            ntp_dct['active-server'] = container.get('active-server')
            if container.get('ntp-server-address'):
                ntp_lst = container['ntp-server-address'].get('server-address')
                # defined ntp servers
                ntp_dct['ntp-server-address'] = ', '.join(ntp_lst) if ntp_lst else None
        return ntp_dct
                
       
    def _get_license_value(self) -> List[Dict[str, Union[str, int]]]:
        """
        Method extracts license and expiration date from the license container.
        
        License status:
            0 - No expiration date
            1 - Expiration date has not arrived
            2 - Expiration date has arrived
        
        Returns:
            List of licenses with nested dictionaries.
            Nested dictionary contains license title, expiration date, license status (expired or not).
        """
        
        license_feature_lst = []
        if self.sw_telemetry.sw_license.get('Response'):
            container = self.sw_telemetry.sw_license['Response']['license']
            for lic_leaf in container:
                lic_feature = ', '.join(lic_leaf['features']['feature'])
                # add expiration date and expiration date status (exoired or not)
                # expiration date present
                if lic_leaf.get('expiration-date'):
                    exp_date_str = lic_leaf['expiration-date']
                    exp_date = datetime.strptime(exp_date_str, '%m/%d/%Y').date()
                    # license expired
                    if date.today() > exp_date:
                        lic_status = 2
                    # license is not expired
                    else:
                        lic_status = 1
                # no expiration date
                else: 
                    lic_status = 0
                    exp_date_str = 'No expiration date'
                # license_feature_lst.append([lic_feature, exp_date_str, lic_status])
                license_feature_lst.append({'feature': lic_feature, 
                                            'expiration-date': exp_date_str, 
                                            'license-status-id': lic_status})
        # license module extracted but container is empty
        else:
            if self.sw_telemetry.sw_license.get('status-code'):
                lic_feature = self.sw_telemetry.sw_license['error-message']
                # license_feature_lst.append([lic_feature, 'Not applicable', 0])
                license_feature_lst.append({'feature': lic_feature, 
                                            'expiration-date': 'Not Applicable', 
                                            'license-status-id': 0})
        return license_feature_lst
            

    def __repr__(self):
        return f"{self.__class__.__name__} ip_address: {self.sw_telemetry.sw_ipaddress}"


    @property
    def sw_telemetry(self):
        return self._sw_telemetry
    
    
    @property
    def chassis(self):
        return self._chassis
    
    
    @property
    def sw_license(self):
        return self._sw_license
    
    
    @property
    def ntp_server(self):
        return self._ntp_server