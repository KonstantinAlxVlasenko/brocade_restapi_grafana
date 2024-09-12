from datetime import datetime
from ipaddress import ip_address
from typing import Any, List, Optional

import httpx
from requests.auth import HTTPBasicAuth



class SwitchTelemetryRequest:
    """
    Class to perform Brocade switch http telemetry requests.
    Requested modules: 
    
    VF independent: 'chassis', 'fibrechannel-logical-switch', 'time-zone', 'clock-server', 
                        'power-supply', 'fan', 'sensor', 'switch-status-policy-report', 
                        'system-resources', 'license', 
                        
    VF dependent: 'fabric-switch',  'fibrechannel-switch', 'maps-policy', 'maps-config', 
                    'dashboard-rule', 'fibrechannel', 'fibrechannel-statistics',  
                    'media-rdp', 'hba', 'port', 'fibrechannel-name-server'.           

    Attributes:
        sw_ipaddress (ip_address): IP address of the switch.
        username (str): Username to access the switch.
        password (str): Password to access the switch.
        seccure_access (bool): True if httttps is used. False if http is used. Default is False (http).
    """
    

    HEADERS = {
        'Accept': 'application/yang-data+json', 
        'Content-Type': 'application/yang-data+json',
        }
    
    VF_MODE_RETRIEVE_ERROR = {'errors': {'error': [{'error-message': 'VF mode has not been retreived'}]}}
    VF_ID_RETRIEVE_ERROR = {'errors': {'error': [{'error-message': 'VF IDs has not been retreived'}]}}

    VALID_STATUS_CODES = [200, 400, 404]
    

    def __init__(self, sw_ipaddress: ip_address, username: str, password: str, secure_access: bool = False):
        """
        Args:
            sw_ipaddress (ip_address): IP address of the switch.
            username (str): Username to access the switch.
            password (str): Password to access the switch.
            seccure_access (bool): True if httttps is used. False if http is used. Default is False (http).
        """
        
        self._sw_ipaddress = ip_address(sw_ipaddress)
        self._username = username
        self._password = password
        self._secure_access = secure_access

        self._corrupted_request = False
        
        # VF independent attributes
        self._chassis = {}
        self._fc_logical_switch = {}
        self._ts_timezone = {}
        self._clock_server = {}
        self._fru_ps = {}
        self._fru_fan = {}
        self._fru_sensor = {}
        self._ssp_report = {}
        self._system_resources = {}
        self._sw_license = {}

        
        self._ch_unique_containers =[
            [self._chassis, ('brocade-chassis', 'chassis')],
            [self._fc_logical_switch, ('brocade-fibrechannel-logical-switch', 'fibrechannel-logical-switch')],
            [self._ts_timezone, ('brocade-time', 'time-zone')],
            [self._clock_server, ('brocade-time', 'clock-server')],
            [self._fru_ps, ('brocade-fru', 'power-supply')],
            [self._fru_fan, ('brocade-fru', 'fan')],
            [self._fru_sensor, ('brocade-fru', 'sensor')],
            [self._ssp_report, ('brocade-maps', 'switch-status-policy-report')],
            [self._system_resources, ('brocade-maps', 'system-resources')],
            [self._sw_license, ('brocade-license', 'license')]
            ]
        
        with httpx.Client(verify=False) as client:
            for container, (module_name, module_type) in self._ch_unique_containers:
                container.update(self._get_sw_telemetry(client, module_name, module_type))
                SwitchTelemetryRequest._get_container_error_message(container)
            
        self._vf_enabled = self._check_vfmode_on()
        self._vfid_lst = self._get_vfid_list()
        
        # VF dependent attributes
        self._fabric_switch = {}
        self._fc_switch = {}
        self._maps_policy = {}
        self._maps_config = {}
        self._dashboard_rule = {}
        self._fc_interface = {}
        self._fc_statistics = {}
        self._media_rdp = {}
        self._fdmi_hba = {}
        self._fdmi_port = {}
        self._fc_nameserver = {}

        # self._vf_unique_containers = [
        #     [self._fabric_switch, ('brocade-fabric', 'fabric-switch')],
        #     [self._fc_switch, ('brocade-fibrechannel-switch', 'fibrechannel-switch')],
        #     [self._maps_policy, ('brocade-maps', 'maps-policy')],
        #     [self._maps_config, ('brocade-maps', 'maps-config')],
        #     [self._dashboard_rule, ('brocade-maps', 'dashboard-rule')],
        #     [self._fc_interface, ('brocade-interface', 'fibrechannel')],
        #     [self._fc_statistics, ('brocade-interface', 'fibrechannel-statistics')],
        #     [self._media_rdp, ('brocade-media', 'media-rdp')],
        #     [self._fdmi_hba, ('brocade-fdmi', 'hba')],
        #     [self._fdmi_port, ('brocade-fdmi', 'port')],
        #     [self._fc_nameserver, ('brocade-name-server', 'fibrechannel-name-server')]
        #     ]
        

        self._vf_unique_containers = [
            [self._fabric_switch, ('brocade-fabric', 'fabric-switch')],
            [self._fc_switch, ('brocade-fibrechannel-switch', 'fibrechannel-switch')],
            [self._maps_policy, ('brocade-maps', 'maps-policy')],
            [self._maps_config, ('brocade-maps', 'maps-config')],
            [self._dashboard_rule, ('brocade-maps', 'dashboard-rule')],
            [self._fc_interface, ('brocade-interface', 'fibrechannel')],
            [self._fc_statistics, ('brocade-interface', 'fibrechannel-statistics')],
            [self._media_rdp, ('brocade-media', 'media-rdp')]
            ]
        
        with httpx.Client(verify=False) as client:
        
            # vf mode value is not retrieved
            if self._vf_enabled is None:
                # ch_container_error = BrocadeSwitchTelemetry._get_container_error_message(self._chassis)
                for container, _ in self._vf_unique_containers:
                    container[-2] = SwitchTelemetryRequest.VF_MODE_RETRIEVE_ERROR
                    container[-2]['status-code'] = None
                    container[-2]['date'] = datetime.now().strftime("%d/%m/%Y")
                    container[-2]['time'] = datetime.now().strftime("%H:%M:%S")
                    
                    # container[-2] = self._chassis
                    SwitchTelemetryRequest._get_container_error_message(container[-2])
            
            # vf mode disabled
            elif not self._vf_enabled:
                for container, (module_name, module_type) in self._vf_unique_containers:
                    container[-1] = self._get_sw_telemetry(client, module_name, module_type)
                    SwitchTelemetryRequest._get_container_error_message(container[-1])
            
            # vf mode is enabled but vf ids was not extracted
            elif self._vfid_lst is None:
                # fc_logical_sw_container_error = BrocadeSwitchTelemetry._get_container_error_message(self._fc_logical_switch)
                for container, _ in self._vf_unique_containers:
                    container[-3] = SwitchTelemetryRequest.VF_ID_RETRIEVE_ERROR
                    container[-3]['status-code'] = None
                    container[-3]['date'] = datetime.now().strftime("%d/%m/%Y")
                    container[-3]['time'] = datetime.now().strftime("%H:%M:%S")
                    # container[-3] = self._fc_logical_switch
                    SwitchTelemetryRequest._get_container_error_message(container[-3])
                
            # vf mode is enabled with single virtual switch
            elif self._vfid_lst and len(self._vfid_lst) == 1:
                vf_id = self._vfid_lst[0]
                for container, (module_name, module_type) in self._vf_unique_containers:
                    container[vf_id] = self._get_sw_telemetry(client, module_name, module_type)
                    SwitchTelemetryRequest._get_container_error_message(container[vf_id])
                
            # vf mode is enabled with multiple virtual switches   
            elif self._vfid_lst and len(self._vfid_lst) > 1:
                
                for vf_id in self._vfid_lst:
                    for container, (module_name, module_type) in self._vf_unique_containers:
                        container[vf_id] = self._get_sw_telemetry(client, module_name, module_type, vf_id)
                        SwitchTelemetryRequest._get_container_error_message(container[vf_id])


    def _get_sw_telemetry(self, client: httpx.Client, module_name: str, module_type: str, vf_id: int=None) -> dict:
        """Funtion retrieves switch telemetry of the module_name and module_type for the vf_id.

        Args:
            client (httpx.Client): client to connect to the switch.
            module_name (str): module to request (for example brocade-fru)
            module_type (str): sub-module in a module tree to request (for example fan or power-supply)
            vf_id (int, optional): virtual fabric id for the VF dependent modules. Defaults to None.

        Returns:
            dict: switch telemetry of the module_name and module_type for the vf_id.
        """

        url = self._create_restapi_url(module_name, module_type)
        params = {'vf-id': vf_id} if vf_id else {}
        
        try:
            response = client.get(url, 
                                    auth=HTTPBasicAuth(self.username, self.password),
                                    params=params,
                                    headers=SwitchTelemetryRequest.HEADERS,
                                    timeout=31)
            current_telemetry = response.json()
            current_telemetry['status-code'] = response.status_code
            current_telemetry['date'] = datetime.now().strftime("%d/%m/%Y")
            current_telemetry['time'] = datetime.now().strftime("%H:%M:%S")
            if not response.status_code in SwitchTelemetryRequest.VALID_STATUS_CODES:
                print(module_name, module_type, 'corrupted request')
                self.corrupted_request = True    
            print(module_name, module_type, response.status_code)
            return current_telemetry
        
        except (Exception) as error:
            current_telemetry ={'errors': {'error': [{'error-message': str(error)}]}}
            current_telemetry['status-code'] = None
            current_telemetry['date'] = datetime.now().strftime("%d/%m/%Y")
            current_telemetry['time'] = datetime.now().strftime("%H:%M:%S")
            print(module_name, module_type, str(error))
            self.corrupted_request = True
            return current_telemetry
        

    def _create_restapi_url(self, module_name: str, module_type: str) -> str:
        """Function generates REST API url to request module data.

        Args:
            module_name (str): module to request (for example brocade-fru)
            module_type (str): sub-module in a module tree to request (for example fan or power-supply)

        Returns:
            str: REST API url to request module data.
        """
        
        login_protocol = ('https' if self.secure_access else 'http') + r'://'
        url = login_protocol + self.sw_ipaddress + '/rest/running/' + module_name + '/' + module_type
        return url
    

    
    def _check_vfmode_on(self) -> bool:
        """
        Function extracts 'vf-enabled' leaf value from the chassis container.
        
        Returns:
            bool: True if 'vf-enabled' leaf value is True, False otherwise.
        """
        
        if self.chassis.get('Response'):
            return self.chassis['Response']['chassis']['vf-enabled']
        
    
    def _get_vfid_list(self) -> List[Optional[int]]:
        """Function gets list of virtual fabric ids configured on the switch.

        Returns:
            List[Optional[int]]: list of vf_id.
        """
        
        if self.fc_logical_switch.get('Response'):
            vfid_lst = []
            container = self.fc_logical_switch['Response']['fibrechannel-logical-switch']
            for logical_sw in container:
                vfid_lst.append(logical_sw['fabric-id'])
            return vfid_lst    


    @staticmethod
    def _get_container_error_message(container):
        """Function extracts error messages from the container, join them and adds it to the container
        under 'error-message' key.

        Args:
            container(dict): class container to extract error messages from.
        """
   
        if 'errors' in container:
            errors_lst = container['errors']['error']
            errors_msg_lst = [error.get('error-message') for error in errors_lst if error.get('error-message')]
            if errors_msg_lst:
                container['error-message'] = ', '.join(errors_msg_lst)
            else:
                container['error-message'] = 'No error message found'
        else:
            container['error-message'] = None    


    def __repr__(self):
        return f"{self.__class__.__name__} ip_address: {self.sw_ipaddress}"


    @property
    def sw_ipaddress(self):
        return str(self._sw_ipaddress)
    
    
    @property
    def username(self):
        return self._username


    @property
    def password(self):
        return self._password


    @property
    def secure_access(self):
        return self._secure_access    


    @property
    def corrupted_request(self):
        return self._corrupted_request
    
    @corrupted_request.setter
    def corrupted_request(self, value):
        self._corrupted_request = value



    @property
    def chassis(self):
        """The complete details of the chassis."""
        return self._chassis
    

    @property
    def fabric_switch(self):
        """The list of configured switches in the fabric."""
        return self._fabric_switch
    

    @property
    def fc_switch(self):
        """Switch state parameters."""
        return self._fc_switch
    
    
    @property
    def fc_logical_switch(self):
        """The logical switch state parameters of all configured logical switches."""
        return self._fc_logical_switch
    

    @property
    def ts_timezone(self):
        """The time zone parameters."""
        return self._ts_timezone
    
    
    @property
    def clock_server(self):
        """The NTP colck server parameters."""
        return self._clock_server
    
    
    @property
    def fru_ps(self):
        """The details about the power supply units."""
        return self._fru_ps
    

    @property
    def fru_fan(self):
        """The details about the fan units"""
        return self._fru_fan
    

    @property
    def fru_sensor(self):
        return self._fru_sensor
    

    @property
    def ssp_report(self):
        """The Switch Status Policy report container. 
        The SSP report provides the overall health status of the switch."""
        return self._ssp_report
    

    @property
    def system_resources(self):
        """The system resources (such as CPU, RAM, and flash memory usage) container. 
        Note that usage is not real time and may be delayed up to 2 minutes."""
        return self._system_resources
    

    @property
    def maps_policy(self):
        """The MAPS policy container.
        This container enables you to view monitoring policies.
        A MAPS policy is a set of rules that define thresholds for measures and actions to take when a threshold is triggered.
        When you enable a policy, all of the rules in the policy are in effect. A switch can have multiple policies."""
        return self._maps_policy
    

    @property
    def maps_config(self):
        """The MAPS configuration container (MAPS actions)."""
        return self._maps_config
    

    @property
    def dashboard_rule(self):
        """A list of dashboards container. 
        The dashboard enables you to view the events or rules triggered 
        and the objects on which the rules were triggered over a specified period of time.
        You can view a triggered rules list for the last 7 days."""
        return self._dashboard_rule
    

    @property
    def sw_license(self):
        """The container for licenses installed on the switch."""
        return self._sw_license
    

    @property
    def fc_interface(self):
        """FC interface-related configuration and operational state."""
        return self._fc_interface
    

    @property
    def fc_statistics(self):
        """Statistics for all FC interfaces on the device."""
        return self._fc_statistics
    

    @property
    def media_rdp(self):
        """SFP transceivers media data container. 
        The summary includes information that describes the SFP capabilities, 
        interfaces, manufacturer, and other information."""
        return self._media_rdp
    

    @property
    def fdmi_hba(self):
        """A detailed view of the Fabric Device Management Interface (FDMI).
        List of HBA attributes registered with FDMI."""
        return self._fdmi_hba
    

    @property
    def fdmi_port(self):
        """A detailed view of the Fabric Device Management Interface (FDMI).
        A list of HBA port attributes registered with FDMI."""
        return self._fdmi_port
    
    
    @property 
    def fc_nameserver(self):
        """Name Server container"""
        return self._fc_nameserver
    
    
    @property 
    def vf_enabled(self):
        """Virtual Fabrics mode enabled flag"""
        return self._vf_enabled
    
    
    @property 
    def vfid_lst(self):
        """List of Virtual Fabric IDs"""
        return self._vfid_lst