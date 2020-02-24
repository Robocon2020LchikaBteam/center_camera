import cv2
from math import atan2, degrees
import numpy as np
from debug import logger


class CarMonitor:
    """
    
    Args:
        back_color_hsv (list): [[min], [max]] e.g. [[20,30,0], [40,255,255]]
    
    """
    INVALID_DEGREE = 360
    DETECT_AREA_SIZE = 1000
    WINDOW_X = 2304
    WINDOW_Y = 1536
    STATION_POINT = [WINDOW_X / 2, 1200]
    INVALID_DEGREE = 360
    INVALID_DISTANCE = -1
    cap = cv2.VideoCapture(1)
    
    def __init__(self, back_color_hsv):
        logger().debug('CarMonitor init() start')
        self._back_color_hsv = back_color_hsv
        logger().debug('CarMonitor init() end')
    
    def get_car_dests(self, save_img=False, path='img'):
        """
        
        calculate angle between car and station entrance
        
        Args:
            save_img (bool): True -> save intermediate picture as png file (debug function)
            path (string): directory path to save image
            
        Returns:
            float: angle[degree]
            float: distance
        
        """
        readable, img = self._get_img()
        if save_img:
            cv2.imwrite(path + '/origin.png', img)
        hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv_img, np.array(self._back_color_hsv[0]), np.array(self._back_color_hsv[1]))
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
        trim_mask = np.zeros_like(img)
        convex_hull_list = []
        for contour in contours:
            approx = cv2.approxPolyDP(contour, 0.01 * cv2.arcLength(contour, True), True)
            # 四角形に近い形のみ扱う
            if 3 < len(approx) < 10:
                M = cv2.moments(approx)
                if M['m00'] > CarMonitor.DETECT_AREA_SIZE:
                    convex_hull_list.append({'approx': approx, 'moment': M})
                    cv2.fillConvexPoly(trim_mask, approx, color=(255, 255, 255))
        
        if save_img:
            cv2.imwrite(path + '/trim_mask.png', trim_mask)
        bg_color = (255, 255, 255)
        bg_img = np.full_like(img, bg_color)
        trim_img = np.where(trim_mask == 255, img, bg_img)
    
        marker_mask = cv2.inRange(trim_img, np.array([0, 0, 0]), np.array([255, 255, 100]))
        if save_img:
            cv2.imwrite(path + '/marker_mask.png', marker_mask)
        marker_contours, _ = cv2.findContours(marker_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        m_convex_hull_list = []
        for contour in marker_contours:
            approx = cv2.approxPolyDP(contour, 0.01 * cv2.arcLength(contour, True), True)
            # 四角形に近い形のみ扱う
            if 3 < len(approx) < 10:
                M = cv2.moments(approx)
                if M['m00'] > CarMonitor.DETECT_AREA_SIZE / 20:
                    m_convex_hull_list.append({'approx': approx, 'moment': M})

                    cx = int(M['m10'] / M['m00'])
                    cy = int(M['m01'] / M['m00'])
                    self._draw_marker(trim_img, cx, cy, (0, 0, 255))

        p1 = [-1, -1]
        p2 = [-1, -1]
        if len(m_convex_hull_list) > 1:
            m_convex_hull_list.sort(key=lambda x: x['moment']['m00'], reverse=True)
            p1 = [int(m_convex_hull_list[0]['moment']['m10'] / m_convex_hull_list[0]['moment']['m00']),
                  int(m_convex_hull_list[0]['moment']['m01'] / m_convex_hull_list[0]['moment']['m00'])]
            p2 = [int(m_convex_hull_list[1]['moment']['m10'] / m_convex_hull_list[1]['moment']['m00']),
                  int(m_convex_hull_list[1]['moment']['m01'] / m_convex_hull_list[1]['moment']['m00'])]
            logger().debug('p1: {}, p2: {}'.format(p1, p2))
            degree_car = degrees(atan2(p2[1] - p1[1], p1[0] - p2[0]))
            degree_station = degrees(atan2(((p1[1] + p2[1]) / 2) - CarMonitor.STATION_POINT[1],
                                           CarMonitor.STATION_POINT[0] - ((p1[0] + p2[0]) / 2)))
            degree = self._compress_degree_in_180(degree_car - degree_station, 360)
            a = np.array([CarMonitor.STATION_POINT[0], CarMonitor.STATION_POINT[1]])
            b = np.array([(p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2])
            u = b - a
            distance = np.linalg.norm(u)
        else:
            degree = CarMonitor.INVALID_DEGREE
            distance = CarMonitor.INVALID_DISTANCE
        
        if save_img:
            cv2.imwrite(path + '/result_mask.png', trim_img)
            self._draw_marker(img, CarMonitor.STATION_POINT[0], CarMonitor.STATION_POINT[1], (255, 0, 0))
            if p1[0] != -1:
                self._draw_marker(img, (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2, (255, 0, 0))
                cv2.line(img, tuple(p1), tuple(p2), color=(0, 0, 255), thickness=2)
                cv2.line(img, (int((p1[0] + p2[0]) / 2), int((p1[1] + p2[1]) / 2)),
                    (int(CarMonitor.STATION_POINT[0]), int(CarMonitor.STATION_POINT[1])), color=(0, 255, 0), thickness=2)
                cv2.putText(img, 'angle[deg]: ' + str(degree), (30, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), thickness=2)
                cv2.putText(img, 'distance: ' + str(distance), (30, 150), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), thickness=2)
            cv2.imwrite(path + '/result.png', img)
   
        return degree, distance

    def _get_img(self):
        if not CarMonitor.cap.isOpened():
            return False, None
        
        return CarMonitor.cap.read()
    
    # @brief 十字マーカーを描画する
    # @param x 十字マーカーのx座標
    # @param y 十字マーカーのy座標
    # @param marker_color 十字マーカーの色
    def _draw_marker(self, img, x, y, marker_color, size=10):
        x = int(x)
        y = int(y)
        cv2.line(img, (x - size, y), (x + size, y), color=(255, 255, 255), thickness=4)
        cv2.line(img, (x, y - size), (x, y + size), color=(255, 255, 255), thickness=4)
        cv2.line(img, (x - size, y), (x + size, y), color=marker_color, thickness=2)
        cv2.line(img, (x, y - size), (x, y + size), color=marker_color, thickness=2)

    # 無駄に半周以上しないように角度を調整
    def _compress_degree_in_180(self, degree, one_round_value):
        if abs(degree) > (one_round_value / 2):
            return degree - (degree / abs(degree) * one_round_value)
        return degree
