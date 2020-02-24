import time
from car_monitor import CarMonitor
import json
from debug import logger


def get_message_dict(degree, distance, wait):
    message_dict = {}
    message_dict['type'] = 'guide_info'
    message_dict['degree'] = int(degree)
    message_dict['distance'] = int(distance)
    message_dict['wait'] = wait
    return message_dict


def run():
    logger().info('run')
    # 黄色
    car_monitor = CarMonitor([[20, 10, 180], [50, 255, 255]])
    # 緑
    car_monitor_2 = CarMonitor([[60, 50, 90], [100, 255, 255]])
    while(True):
    # for i in range(1):
        #time.sleep(0.1)
        degree, distance = car_monitor.get_car_dests(False)
        degree_2, distance_2 = car_monitor_2.get_car_dests(False)
        logger().info('degree, distance: {}, {}'.format(degree, distance))
        logger().info('degree_2, distance_2: {}, {}'.format(degree_2, distance_2))
        message_dict_1 = get_message_dict(degree, distance,
                                          (degree_2 != CarMonitor.INVALID_DEGREE))
        with open('./data/message_1.json', 'w') as f:
            json.dump(message_dict_1, f)
        message_dict_2 = get_message_dict(degree_2, distance_2, False)
        with open('./data/message_2.json', 'w') as f:
            json.dump(message_dict_2, f)
    logger().info('Thread terminating...')


# Main
if __name__ == "__main__":
    run()
