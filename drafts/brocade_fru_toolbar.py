from brocade_base_gauge import BrocadeGauge

from switch_telemetry_httpx_cls import BrocadeSwitchTelemetry

class BrocadeFRUToolbar:
    """
    Class to create field replaceable units (FRU) toolbar.
    FRU Toolbar is a set of prometheus gauges:
    fan state, fan speed, ps state, sensor state, sensor temperature.
    Each unique ps identified by chassis wwn, unit-number.
    Each unique fan identified by chassis wwn, unit-number, airflow-direction.
    Each unique sensor identified by chassis wwn, unit-number, slot-number, index.

    Attributes:
        sw_telemetry: set of switch telemetry retrieved from the switch
    """

    fru_id_keys  =  ['chassis-wwn', 'unit-number']
    fan_id_keys = fru_id_keys + ['airflow-direction']
    sensor_keys = fru_id_keys + ['slot-number', 'index']


    def __init__(self, sw_telemetry: BrocadeSwitchTelemetry):

        self._sw_telemetry: BrocadeSwitchTelemetry = sw_telemetry

        # fan state gauge
        # 0 - 'absent', 1 - 'ok', 2 - 'below minimum', 3 - 'above maximum', 4- 'unknown', 5 -'not ok', 6 - 'faulty'
        self._gauge_fan_state = BrocadeGauge(name='fan_state', description='Status of each fan in the system', 
                                             label_keys=BrocadeFRUToolbar.fan_id_keys, metric_key='operational-state-id')
        # fan speed gauge
        self._gauge_fan_speed = BrocadeGauge(name='fan_speed', description='Speed of each fan in the system', 
                                             label_keys=BrocadeFRUToolbar.fan_id_keys, metric_key='speed')
        # ps state gauge
        # 0 - 'absent', 1 - 'ok', 2 - 'predicting failure', 3 - 'unknown', 4 - 'try reseating unit', 5 - 'faulty'
        self._gauge_ps_state = BrocadeGauge(name='ps_state', description='Status of the switch power supplies', 
                                             label_keys=BrocadeFRUToolbar.fru_id_keys, metric_key='operational-state-id')
        # sensor state gauge
        # 0 - 'absent', 1 - 'ok'
        self._gauge_sensor_state = BrocadeGauge(name='sensor_state', description='The current operational state of the sensor', 
                                             label_keys=BrocadeFRUToolbar.sensor_keys, metric_key='operational-state-id')
        # sensor temperature gauge
        self._gauge_sensor_temp = BrocadeGauge(name='sensor_temp', description='Sensor temperature', 
                                             label_keys=BrocadeFRUToolbar.sensor_keys, metric_key='temperature')


    def __repr__(self):
        return f"{self.__class__.__name__} ip_address: {self.sw_telemetry.sw_ipaddress}"


    @property
    def sw_telemetry(self):
        return self._sw_telemetry


    @property
    def gauge_fan_state(self):
        return self._gauge_fan_state
    

    @property
    def gauge_fan_speed(self):
        return self._gauge_fan_speed
    

    @property
    def gauge_ps_state(self):
        return self._gauge_ps_state


    @property
    def gauge_sensor_state(self):
        return self._gauge_sensor_state


    @property
    def gauge_sensor_temp(self):
        return self._gauge_sensor_temp