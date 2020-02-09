# coding: UTF-8

from multiprocessing import Process
from debug import logger
# import monitor_main
import socket_main

if __name__ == '__main__':
    logger().info('main line')

    # p_monitor = Process(target=monitor_main.run, args=())
    p_socket_1 = Process(target=socket_main.run_socket_1, args=())
    p_socket_2 = Process(target=socket_main.run_socket_2, args=())
    
    # p_monitor.start()
    # logger().info('p_monitor started')
    p_socket_1.start()
    logger().info('p_socket_1 started')
    p_socket_2.start()
    logger().info('p_socket_2 started')

    # p_monitor.join()
    p_socket_1.join()
    p_socket_2.join()
