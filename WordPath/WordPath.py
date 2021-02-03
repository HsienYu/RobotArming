import cv2
import pygame
import numpy 
import numpy as np
from PIL import Image
import time
import os
import HRSS.HRSDK as SDK
import matplotlib.pyplot as plt
pygame.init()

class WordInformation:

    def __init__(self, font_size, font_path, pixel_size):
        self.font_size = font_size 
        self.font_path = font_path
        self.pixel_size = pixel_size

        self.word_image = None
        self.contours = None
        self.all_font_text_pygame = []
        self.all_font_text_opencv = []

    def create_text_by_lines(self, lines):
        write_font = pygame.font.Font(self.font_path, self.font_size)
        write_font.set_underline(False)
        write_font.set_bold(False)
        sum_height = 0
        max_width = 0
        for i in range(len(lines)):
            text_image = write_font.render(lines[i], False, (255, 255, 255), (0, 0, 0))
            max_width = max(max_width, text_image.get_width())
            sum_height = sum_height + text_image.get_height()
            self.all_font_text_pygame.append(text_image)

        # region 根據pygame 產生的單行圖片 轉換成全部的 opencv
        root = pygame.Surface((max_width, sum_height))
        root.fill((0, 0, 0))
        start_height = 0
        for ftext in self.all_font_text_pygame:
            root.blit(ftext, (0, start_height))
            start_height = start_height + ftext.get_height()
        pil_string_image = pygame.image.tostring(root, "RGB", False)
        image_pil = Image.frombytes("RGB", (root.get_width(), root.get_height()), pil_string_image)
        self.word_image = cv2.cvtColor(numpy.asarray(image_pil), cv2.COLOR_BGR2GRAY)

        # endregion

        # region 將單行的圖片轉換成單行的opencv
        for ftext in self.all_font_text_pygame:
            pil_string_image = pygame.image.tostring(ftext, "RGB", False)
            image_pil = Image.frombytes("RGB", (ftext.get_width(), ftext.get_height()), pil_string_image)        
            self.all_font_text_opencv.append(cv2.cvtColor(numpy.asarray(image_pil), cv2.COLOR_BGR2GRAY))

        # endregion

        return self.word_image ,self.all_font_text_opencv 

    def thinning(self, image, contour_info):
        """
        一次做一行
        :param image:
        :return:
        """

        _, threshold = cv2.threshold(image, 200, 255, type=cv2.THRESH_BINARY)
        thin = cv2.ximgproc.thinning(threshold, thinningType=cv2.ximgproc.THINNING_GUOHALL)
        if(contour_info == "detail"):
            contours, hierarchy = cv2.findContours(thin, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)       # 寫字時使用所有輪廓
        else:
            contours, hierarchy = cv2.findContours(thin, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)   # 畫圖只顯示外輪廓 
        self.contours = contours
        return self.contours

    def sort_contours(self, method="left-to-right"):
        reverse = False
        i = 0
        if method == "right-to-left" or method == "bottom-to-top":
            reverse = True
        if method == "top-to-bottom" or method == "bottom-to-top":
            i = 1
        bounding_boxes = [cv2.boundingRect(c) for c in self.contours]
        (self.contours, bounding_boxes) = zip(*sorted(zip(self.contours, bounding_boxes), key=lambda b: b[1][i],
                                                      reverse=reverse))
        return bounding_boxes

    def display(self, width,height):
        display = np.zeros((width, height), np.uint8)
        for contour in self.contours:
            if contour.size > 1:
                for j in range(0, len(contour)):
                    display[contour[j][0][1]][contour[j][0][0]] = 255
                    display[contour[j][0][1]][contour[j][0][0]+1] = 255
                    display[contour[j][0][1]][contour[j][0][0]-1] = 255
                    display[contour[j][0][1]+1][contour[j][0][0]] = 255
                    display[contour[j][0][1]-1][contour[j][0][0]] = 255
                    cv2.imshow("Contour path", display)
                    cv2.waitKey(5)
                    time.sleep(0.001)
                        

class WriteWord:
    def __init__(self, robot_handle, modify_z):
        self.robot_handle = robot_handle
        self.modify_z = modify_z
        self.contour_up = 30

    def writing_twice(self,word_information, height_add, bound, modify_x, modify_y):
        for contour in word_information.contours:
            if contour.size >= 1:
                a_word_first_time = True
                for j in range(0, len(contour), 8):
                    if j <= len(contour):
                        x = (contour[j][0][0]) * word_information.pixel_size + bound
                        y = (contour[j][0][1] + height_add) * word_information.pixel_size + bound
                        p_contour = SDK.Point(x + modify_x, y + modify_y, self.modify_z, 180, -62, -90)  # 610 : (0,50,-90)
                        # 到該點上方
                        if a_word_first_time:
                            p_contour.z = p_contour.z + self.contour_up
                            a_word_first_time = False                       
                            self.robot_handle.MotionCommand.lin_pos(SDK.LinSmoothMode.CloseSmooth.value,1, p_contour)
                        if contour.size <= 20:
                            # 點少 到該點，開始寫，容易被插補吃掉
                            p_contour = SDK.Point(x + modify_x, y + modify_y, self.modify_z, 180, -62, -90)
                            self.robot_handle.MotionCommand.lin_pos(SDK.LinSmoothMode.CloseSmooth.value,1, p_contour)
                        else:
                            # 點多 到該點，開始寫
                            p_contour = SDK.Point(x + modify_x, y + modify_y, self.modify_z, 180, -62, -90)
                            self.robot_handle.MotionCommand.lin_pos(SDK.LinSmoothMode.BezierCurveRadius.value,1, p_contour)

                # 一個contour結束，抬起來換下一個contour
                p_finish_contour = SDK.Point(x + modify_x, y + modify_y, self.modify_z + self.contour_up, 180, -62, -90)
                self.robot_handle.MotionCommand.lin_pos(SDK.LinSmoothMode.Smooth.value, 1, p_finish_contour)


class CleanWord:
    def __init__(self, robot_handle):
        self.robot_handle = robot_handle
        self.base_x = -30 #-35
        self.base_y = 0
        self.base_z = -160 #-46
        self.offset_x = 1300       # 往左位移距離
        self.offset_y = 80        # 往下位移距離
        self.offset_clean = 10    # 次數

    def clean_start(self,clean_base):
        self.robot_handle.SystemCommand.set_override_ratio(30)
        self.robot_handle.CoordinateCommand.set_base_number(clean_base)

       
        clean_point_1 = SDK.Point(self.base_x, self.base_y -50 , self.base_z, 180, 30, -90)
        clean_point_2 = SDK.Point(self.base_x + self.offset_x, self.base_y - 50, self.base_z, 180, 30, -90)    
        
        clean_point_3 = SDK.Point(self.base_x + self.offset_x, self.base_y+50 , self.base_z, 180, 30, -90)
        
        clean_point_4 = SDK.Point(self.base_x, self.base_y+50 , self.base_z, 180, 30, -90)
        clean_point_5 = SDK.Point(self.base_x, self.base_y + 150 , self.base_z, 180, 30, -90)
        clean_point_6 = SDK.Point(self.base_x + self.offset_x, self.base_y + 150 , self.base_z, 180, 30, -90)

        clean_point_7 = SDK.Point(self.base_x + self.offset_x, self.base_y +250 , self.base_z, 180, 30, -90)
        clean_point_8 = SDK.Point(self.base_x, self.base_y + 250 , self.base_z, 180, 30, -90)
        clean_point_9 = SDK.Point(self.base_x, self.base_y + 350 , self.base_z, 180, 30, -90)

        clean_point_10 = SDK.Point(self.base_x + self.offset_x, self.base_y + 350 , self.base_z, 180, 30, -90)
        clean_point_11 = SDK.Point(self.base_x + self.offset_x, self.base_y + 450 , self.base_z, 180, 30, -90)
        clean_point_12 = SDK.Point(self.base_x , self.base_y + 450 , self.base_z, 180, 30, -90)
        
        clean_point_13 = SDK.Point(self.base_x, self.base_y + 550 , self.base_z, 180, 30, -90)
        clean_point_14 = SDK.Point(self.base_x + self.offset_x, self.base_y + 550 , self.base_z, 180, 30, -90)
        clean_point_15 = SDK.Point(self.base_x + self.offset_x, self.base_y + 650 , self.base_z, 180, 30, -90)

        clean_point_16 = SDK.Point(self.base_x , self.base_y + 650 , self.base_z, 180, 30, -90)
        clean_point_17 = SDK.Point(self.base_x , self.base_y + 720 , self.base_z, 180, 30, -90)
        clean_point_18 = SDK.Point(self.base_x + self.offset_x, self.base_y + 720 , self.base_z, 180, 30, -90)

        # 回到安全點
        clean_point_19 = SDK.Point(self.base_x + self.offset_x, self.base_y + 720 , self.base_z + 150, 180, 30, -90)

        clearn_point_list = [clean_point_1,clean_point_2,clean_point_3,clean_point_4,clean_point_5,clean_point_6,clean_point_7,clean_point_8,clean_point_9,clean_point_10,clean_point_11,clean_point_12,clean_point_13,clean_point_14,clean_point_15,clean_point_16,clean_point_17,clean_point_18,clean_point_19]

        # 點位輪巡
        for i in clearn_point_list:
            self.robot_handle.MotionCommand.lin_pos(SDK.LinSmoothMode.CloseSmooth.value,1, i)

        while True:
            check_state = self.robot_handle.MotionCommand.get_motion_state()
            if check_state == 1:
                break    
        '''
        clean_point_pass = SDK.Point(clean_point_2.x, clean_point_2.y + self.offset_y, clean_point_2.z, 180, 30, -90)
        
        count = 1
        while True:
            if(self.robot_handle.MotionCommand.get_command_count()<100):
                self.robot_handle.MotionCommand.lin_pos(SDK.LinSmoothMode.CloseSmooth.value,1, clean_point_1)
                self.robot_handle.MotionCommand.lin_pos(SDK.LinSmoothMode.CloseSmooth.value,1, clean_point_2)   
                self.robot_handle.MotionCommand.lin_pos(SDK.LinSmoothMode.CloseSmooth.value,1, clean_point_pass)      
                clean_point_1.y = clean_point_1.y + self.offset_y
                clean_point_2.y = clean_point_2.y + self.offset_y
                clean_point_pass.y = clean_point_pass.y + self.offset_y
                count += 1

                if count > self.offset_clean:
                    while True:
                        check_state = self.robot_handle.MotionCommand.get_motion_state()
                        if check_state == 1:
                            break   
                    break
                    
        # 擦完後回安全點
        clearn_home = SDK.Point(1265, 700.000, 95.000, 180.000, 30, -90.000)    #610
        self.robot_handle.SystemCommand.set_override_ratio(5)
        self.robot_handle.MotionCommand.lin_pos(SDK.LinSmoothMode.CloseSmooth.value,1, clearn_home)
        while True:       
            if(self.robot_handle.MotionCommand.get_command_count() == 0):
                break;        
        '''

class draw_circle:
    def __init__(self, robot_handle):
        self.robot_handle = robot_handle
        self.base_z = 0
        self.contour_up = 50

    def draw(self, x, y, r):
        
        # 1.圓半徑
        r = r
        # 2.圓心座標
        a, b = (x, y)

        # 參數方程
        theta = np.arange(0, 2*np.pi, 0.01)
        x = a + r * np.cos(theta)
        y = b + r * np.sin(theta)
        
        a_word_first_time = True
        for j in range(0, len(x), 5):
            if a_word_first_time:
                # 先到該點上方   
                p_contour = SDK.Point(x[j], y[j], self.base_z, 180, -62, -90)  # 610 : (180,-62,-90)
                p_contour.z = p_contour.z + self.contour_up
                a_word_first_time = False
                self.robot_handle.MotionCommand.lin_pos(SDK.LinSmoothMode.BezierCurveRadius.value,1, p_contour)

            p_contour = SDK.Point(x[j], y[j], self.base_z, 180, -62, -90)  # 610 : (180,-62,-90)
            #p_contour = SDK.Point(x[j], y[j], self.base_z, 180, 0, -90)  # 605 : (180,0,-90)
            self.robot_handle.MotionCommand.lin_pos(SDK.LinSmoothMode.BezierCurveRadius.value,1, p_contour)
        
        while True:
            if(self.robot_handle.MotionCommand.get_command_count() == 0):
                break;
            time.sleep(0.1)

        # 畫完一個圓就起來
        p_contour = SDK.Point(x[j], y[j], self.base_z + self.contour_up, 180, -62, -90)  # 605 : (180,0,-90)
        self.robot_handle.MotionCommand.lin_pos(SDK.LinSmoothMode.BezierCurveRadius.value,1, p_contour)
        time.sleep(0.5)
        while True:
            if(self.robot_handle.MotionCommand.get_command_count() == 0):
                break;
            time.sleep(0.1)  

        '''
        step = 0.01         # 每一步走多長
        a, b = (x, y)       # 圓心
        count = count       # 我要畫多少圈，也不是真的多少圈啦
        dist = dist         # 每圈的間距

        theta = np.arange(0, count*np.pi, step)
        x = a + dist * theta * np.cos(theta)
        y = b + dist * theta * np.sin(theta)
        
        for j in range(0, count, 1):
            # 到該點，開始寫
            p_contour = SDK.Point(x[j], y[j], self.base_z, -180, 0, -90)
            self.robot_handle.MotionCommand.lin_pos(SDK.LinSmoothMode.BezierCurveRadius.value,1, p_contour)

        while True:
            if(self.robot_handle.MotionCommand.get_command_count() == 0):
                break;
            time.sleep(0.1)     
        '''


        