import websocket
import _thread
import time
from debug import logger


# Callback functions
def on_message(ws, message):
    logger().info('Received:{}'.format(message))

 
def on_error(ws, error):
    logger().info('Error:{}'.format(error))

 
def on_close(ws):
    logger().info('Close')


def on_open_1(ws):
    def run(*args):
        logger().info('Open')
        while(True):
        # for i in range(1):
            time.sleep(0.1)
            message = ''
            with open('./data/message_1.json') as f:
                message = f.read()
            ws.send(message)
            logger().debug('Sent:{}'.format(message))
        ws.close()
        logger().info('Thread terminating...')
    _thread.start_new_thread(run, ())


def on_open_2(ws):
    def run(*args):
        logger().info('Open')
        while(True):
        # for i in range(1):
            time.sleep(0.1)
            message = ''
            with open('./data/message_2.json') as f:
                message = f.read()
            ws.send(message)
            logger().debug('Sent:{}'.format(message))
        ws.close()
        logger().info('Thread terminating...')
    _thread.start_new_thread(run, ())


def run_socket_1():
    websocket.enableTrace(False)
    # websocket.enableTrace(False)
    ws = websocket.WebSocketApp("ws://192.168.100.122:9001",
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.on_open = on_open_1
    ws.run_forever()


def run_socket_2():
    websocket.enableTrace(False)
    # websocket.enableTrace(False)
    ws = websocket.WebSocketApp("ws://192.168.100.125:9001",
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.on_open = on_open_2
    ws.run_forever()


# Main
if __name__ == "__main__":
    websocket.enableTrace(False)
    # websocket.enableTrace(False)
    ws = websocket.WebSocketApp("ws://192.168.100.122:9001",
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.on_open = on_open_1
    ws.run_forever()
