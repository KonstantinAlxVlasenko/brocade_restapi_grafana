from infinisdk import InfiniBox
from prometheus_client import start_http_server, Gauge
import time
from capacity import * 

# Подключение к Infinibox
# system = InfiniBox('ibox2512-ost.dtln.ru',auth=("exporter", "22"),use_ssl=False)
system = InfiniBox('ibox1159-nord.dtln.ru',auth=("exporter", "22"),use_ssl=False)

# Определение метрик 
gauge_info_InfiniBox = Gauge('name_Infinibox', 'Name and version Infinibox', ['InfiniBox_name'])
gauge_node_status = Gauge('node_status', 'node status Infinibox', ['node_name'])

gauge_drive_status = Gauge('drive_status', 'drive status Infinibox', ['enclosure_drive_serial', 'status'])
gauge_total_physical_capacity = Gauge('infinibox_total_physical_capacity', 'Total physical capacity of the Infinibox system', ['InfiniBox_name'])
gauge_free_physical_capacity = Gauge('infinibox_free_physical_capacity', 'Free physical capacity of the Infinibox system', ['InfiniBox_name'])

gauge_pool_physical_capacity = Gauge('infinibox_pool_physical_capacity', 'Physical capacity of pool on Infinibox', ['pool_name'])
gauge_pool_free_physical_capacity = Gauge('infinibox_pool_free_physical_capacity', 'Free physical capacity of pool on Infinibox', ['pool_name'])

gauge_pool_virtual_capacity = Gauge('infinibox_pool_virtual_capacity', 'Virtual capacity of pool on Infinibox', ['pool_name'])
gauge_pool_free_virtual_capacity = Gauge('infinibox_pool_free_virtual_capacity', 'Free Virtual capacity of pool on Infinibox', ['pool_name'])

gauge_volume_size = Gauge('infinibox_volume_size', 'Size of volumes on Infinibox', ['volume_name'])
gauge_volume_used_size = Gauge('infinibox_volume_used_size', 'Used size of volumes on Infinibox', ['volume_name'])

# Сбор метрик
def collect_metrics():
    system.login()

    # Имя и версия Infinibox
    InfiniBox_name = system.get_name()
    gauge_info_InfiniBox.labels(InfiniBox_name).set(1)  # Пример установки метки в 1

#статус Ноды

    for node in system.components.nodes:
        node_name = node.get_name()
        node_status = node.get_state()
    
        if node_status == 'ACTIVE':
         node_status = 1.0
        elif node_status == 'is not in ACTIVE!!!':
         node_status = 0.0
    
        gauge_node_status.labels(node_name).set(node_status)

#статус дисков
    # Получаем все доступные enclosure
    for enclosure in system.components.enclosures:
        enclosure_number = enclosure.get_index()
        for drive in enclosure.get_drives():
            drive_name = drive.get_index()
            drive_status = drive.get_state()
            drive_serial_number = drive.get_serial_number()

            # Генерируем уникальный идентификатор, объединяя enclosure, drive и serial_number
            unique_id = f"{enclosure_number}_{drive_name}"

            # Определяем статус диска и присваиваем значение соответствующей метке
            if drive_status == 'ACTIVE':
                status_value = 1.0
                status_label = 'active'
            elif drive_status in ['FAILED', 'MISSING', 'READY']:
                status_value = 0.0
                status_label = 'inactive'
            else:
                status_value = 0.0
                status_label = 'unknown'

            gauge_drive_status.labels(enclosure_drive_serial=unique_id, status=status_label).set(status_value)



#Total Physical Papacity

    total_capacity = system.capacities.get_total_physical_capacity()
    gauge_total_physical_capacity.labels(InfiniBox_name).set(total_capacity // GiB)

#Free Physical Papacity

    free_physical_capacity = system.capacities.get_free_physical_capacity()
    gauge_free_physical_capacity.labels(InfiniBox_name).set(free_physical_capacity // GiB)

#Физическое место на pool
    for pool in system.pools:
        pool_name = pool.get_name()
        pool_physical_capacity = pool.get_physical_capacity()
        gauge_pool_physical_capacity.labels(pool_name).set(pool_physical_capacity // GiB)

# Свободное физическое место на pool
    for pool in system.pools:
        pool_name = pool.get_name()
        pool_free_physical_capacity = pool.get_free_physical_capacity()
        gauge_pool_free_physical_capacity.labels(pool_name).set(pool_free_physical_capacity // GiB)

# Виртуальное место на pool
    for pool in system.pools:
        pool_name = pool.get_name()
        pool_virtual_capacity = pool.get_virtual_capacity()
        gauge_pool_virtual_capacity.labels(pool_name).set(pool_virtual_capacity // GiB)

# Свободное вирутальное место на pool
    for pool in system.pools:
        pool_name = pool.get_name()
        pool_free_virtual_capacity = pool.get_free_virtual_capacity()
        gauge_pool_free_virtual_capacity.labels(pool_name).set(pool_free_virtual_capacity // GiB)

# Размер Volume
    for volume in system.volumes:
        volume_name = volume.get_name()
        volume_size = volume.get_size()
        gauge_volume_size.labels(volume_name).set(volume_size // GiB)

# Использованное место на volume
    for volume in system.volumes:
        volume_name = volume.get_name()
        volume_used_size = volume.get_used_size()
        gauge_volume_used_size.labels(volume_name).set(volume_used_size // GiB)

# Запуск экспортера
if __name__ == '__main__':
    start_http_server(13053)
    # collect_metrics()
    while True:
        collect_metrics()
        time.sleep(60)
