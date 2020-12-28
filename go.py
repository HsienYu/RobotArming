from WordPath.WordPath import WordInformation, WriteWord, CleanWord, draw_circle
import HRSS.HRSDK as SDK
import cv2
import time
import numpy as np
import math
import sys
import traceback

SEPARATE_CHAR = '^%'
FONT_SIZE = 180
FONT = r"Font/en-US/normal/georgia.ttf"
POINT_TO_MM = 0.32577778

# 寫完一行字 位移距離
height_add = 230

# 畫圓 參數
circle_x = 1046           # 圓心 x座標
circle_y = 193              # 圓心 y座標
circle_r = 70              # 小圓半徑 (mm)

# 畫手臂 縮放比例
shape_0 = 1.7
shape_1 = 1.7

# 手臂回 Home            
def robot_home(robot):
    standby_point_home = SDK.Joint(0, 72.000, -39.500, 0.000, -122, 0.000)    #610

    robot.SystemCommand.set_override_ratio(25)
    robot.CoordinateCommand.set_base_number(0)
    robot.MotionCommand.ptp_axis(SDK.SmoothMode.Smooth.value, standby_point_home)
    while True:
        check_state = robot.MotionCommand.get_motion_state()
        time.sleep(0.3)
        if check_state == 1:
            break 
    time.sleep(1)       

# 寫字 "初始" 點           
def write_start_point(robot):
    robot.SystemCommand.set_override_ratio(10)
    robot.CoordinateCommand.set_base_number(10)
    
    zero_point = SDK.Joint(-0.000, 71.000, -39.500, 0.000, 30.000, 0.000) 
    time.sleep(0.1) 
    while True:
        robot.MotionCommand.ptp_axis(SDK.SmoothMode.Smooth.value, zero_point)
        if(robot.MotionCommand.get_command_count() == 0):
            break;
        time.sleep(0.1) 

    start_point = SDK.Joint(-61.000, 18.000, 0.000, -26.000, 60.000, 72.000) 
    time.sleep(0.1) 
    while True:
        robot.MotionCommand.lin_axis(SDK.SmoothMode.Smooth.value, 1, start_point)
        if(robot.MotionCommand.get_command_count() == 0):
            break;
        time.sleep(0.1)  
 
# 畫圓 "初始" 點
def circle_start_point(robot):
    zero_point = SDK.Joint(53.000, 42.000, -27.500, 27.000, 63.000, -63.000) 
    robot.MotionCommand.ptp_axis(SDK.SmoothMode.Smooth.value, zero_point)
    time.sleep(0.1) 
    while True:
        check_state = robot.MotionCommand.get_motion_state()
        if check_state == 1:
            break  

# 板擦 "初始" 點           
def clean_start_point(robot):
    
    clean_start_point = SDK.Joint(-63.000, 4.000, 29.800, 50.700, -87.800, -47.600)
    robot.SystemCommand.set_override_ratio(20)
    robot.CoordinateCommand.set_base_number(10)

    while True:
        robot.MotionCommand.lin_axis(SDK.SmoothMode.Smooth.value,1, clean_start_point)
        if(robot.MotionCommand.get_command_count() == 0):
            break;
        time.sleep(0.1) 

# 畫圖騰前 思考
def think(robot):
    time.sleep(1)
    robot.CoordinateCommand.set_base_number(10)
    robot.SystemCommand.set_override_ratio(15)

    think_point_first = SDK.Point(1047.000, 198.000, 135.500, 180.000, -62.000, -91.000) 
    robot.MotionCommand.lin_pos(SDK.SmoothMode.Smooth.value,1, think_point_first)

    think_point_first.x = think_point_first.x + 210
    robot.MotionCommand.lin_pos(SDK.SmoothMode.Smooth.value,1, think_point_first)
    think_point_first.x = think_point_first.x - 420
    robot.MotionCommand.lin_pos(SDK.SmoothMode.Smooth.value,1, think_point_first)
    think_point_first.x = think_point_first.x + 210
    robot.MotionCommand.lin_pos(SDK.SmoothMode.Smooth.value,1, think_point_first)
    think_point_first.y = think_point_first.y - 210
    robot.MotionCommand.lin_pos(SDK.SmoothMode.Smooth.value,1, think_point_first)
    think_point_first.y = think_point_first.y + 420
    robot.MotionCommand.lin_pos(SDK.SmoothMode.Smooth.value,1, think_point_first)
    think_point_first.y = think_point_first.y - 210
    robot.MotionCommand.lin_pos(SDK.SmoothMode.Smooth.value,1, think_point_first)
    time.sleep(1) 
    while True:
        check_state = robot.MotionCommand.get_motion_state()
        if check_state == 1:
            break  
    # 畫錯 擦掉
    robot.SystemCommand.set_override_ratio(20)
    
    draw_error_point = SDK.Point(1258.000, 210.000, 83.500, 180.000, -62.000, -90.000) 
    robot.MotionCommand.lin_pos(SDK.SmoothMode.Smooth.value,1, draw_error_point)
    draw_error_point = SDK.Point(1258.000, 210.000, 0.500, 180.000, -62.000, -90.000) 
    robot.MotionCommand.lin_pos(SDK.SmoothMode.Smooth.value,1, draw_error_point)
    draw_error_point = SDK.Point(1120.000, 300.000, 0.500, 180.000, -62.000, -90.000) 
    robot.MotionCommand.lin_pos(SDK.SmoothMode.Smooth.value,1, draw_error_point)
    while True:
        check_state = robot.MotionCommand.get_motion_state()
        if check_state == 1:
            break  
    robot.SystemCommand.set_override_ratio(70)   
    draw_error_point = SDK.Point(1120.000, 300.000, 88.500, 180.000, -62.000, -90.000) 
    robot.MotionCommand.lin_pos(SDK.SmoothMode.Smooth.value,1, draw_error_point)
    while True:
        check_state = robot.MotionCommand.get_motion_state()
        if check_state == 1:
            break  
    time.sleep(1)
    # 擦
    robot.SystemCommand.set_override_ratio(100)
    clearn_error_point = SDK.Joint(63.300, 14.300, 6.500, -51.100, -79.700, 58.300) 
    robot.MotionCommand.lin_axis(SDK.SmoothMode.Smooth.value,1, clearn_error_point)
    while True:
        check_state = robot.MotionCommand.get_motion_state()
        if check_state == 1:
            break  
    robot.SystemCommand.set_override_ratio(40)
    clearn_error_point = SDK.Point(1302.500, 108.300, -42.000, 180.000, 30.000, -90.000) 
    robot.MotionCommand.lin_pos(SDK.SmoothMode.Smooth.value,1, clearn_error_point)
    clearn_error_point = SDK.Point(1043.000, 217.000, -42.000, 180.000, 30.000, -90.000) 
    robot.MotionCommand.lin_pos(SDK.SmoothMode.Smooth.value,1, clearn_error_point)

    clearn_error_point = SDK.Joint(55.000, 39.000, -17.500, -49.000, -72.000, 53.000) 
    robot.MotionCommand.lin_axis(SDK.SmoothMode.Smooth.value,1, clearn_error_point)
    while True:
        check_state = robot.MotionCommand.get_motion_state()
        if check_state == 1:
            break  

# 畫圖騰後 指向圖騰 開心
def happy(robot):

    robot.CoordinateCommand.set_base_number(10)
    robot.SystemCommand.set_override_ratio(30)
    
    happy_point = SDK.Point(832.000, 351.000, 53.500, 180.000, -62.000, -91.000) 
    robot.MotionCommand.lin_pos(SDK.SmoothMode.Smooth.value,1, happy_point)
    happy_point = SDK.Point(832.000, 351.000, 0.000, 180.000, -62.000, -91.000) 
    robot.MotionCommand.lin_pos(SDK.SmoothMode.Smooth.value,1, happy_point)
    time.sleep(0.1) 
    while True:
        check_state = robot.MotionCommand.get_motion_state()
        if check_state == 1:
            break
    happy_point = SDK.Point(832.000, 351.000, 53.500, 180.000, -62.000, -91.000) 
    robot.MotionCommand.lin_pos(SDK.SmoothMode.Smooth.value,1, happy_point)
    time.sleep(0.1) 
    while True:
        check_state = robot.MotionCommand.get_motion_state()
        if check_state == 1:
            break

# 畫手臂前 思考 下不了手
def think_robot(robot):
    robot.CoordinateCommand.set_base_number(10)
    robot.SystemCommand.set_override_ratio(50)

    think_robot_point = SDK.Point(636.000, 10.000, 130.500, 180.000, -62.000, -91.000) 
    robot.MotionCommand.lin_pos(SDK.SmoothMode.Smooth.value,1, think_robot_point)
    while True:
        check_state = robot.MotionCommand.get_motion_state()
        if check_state == 1:
            break
    time.sleep(2)

    robot.SystemCommand.set_override_ratio(20)
    think_point = SDK.Joint(-10.000, 47.000, -15.500, -25.000, -43.000, -0.000) 
    robot.MotionCommand.ptp_axis(SDK.SmoothMode.Smooth.value, think_point)
    while True:
        check_state = robot.MotionCommand.get_motion_state()
        if check_state == 1:
            break
    time.sleep(0.5)
    think_point = SDK.Joint(10.000, 47.000, -15.500, 25.000, -43.000, -0.000) 
    robot.MotionCommand.ptp_axis(SDK.SmoothMode.Smooth.value, think_point)
    while True:
        check_state = robot.MotionCommand.get_motion_state()
        if check_state == 1:
            break
    time.sleep(0.5)
    think_point = SDK.Joint(-10.000, 47.000, -15.500, -25.000, -43.000, -0.000) 
    robot.MotionCommand.ptp_axis(SDK.SmoothMode.Smooth.value, think_point)
    while True:
        check_state = robot.MotionCommand.get_motion_state()
        if check_state == 1:
            break
    time.sleep(0.5)
    think_point = SDK.Joint(10.000, 47.000, -15.500, 25.000, -43.000, -0.000) 
    robot.MotionCommand.ptp_axis(SDK.SmoothMode.Smooth.value, think_point)
    while True:
        check_state = robot.MotionCommand.get_motion_state()
        if check_state == 1:
            break
    time.sleep(0.5)
    think_point = SDK.Joint(-10.000, 47.000, -15.500, -25.000, -43.000, -0.000) 
    robot.MotionCommand.ptp_axis(SDK.SmoothMode.Smooth.value, think_point)
    while True:
        check_state = robot.MotionCommand.get_motion_state()
        if check_state == 1:
            break
    time.sleep(0.5)
    think_point = SDK.Joint(10.000, 47.000, -15.500, 25.000, -43.000, -0.00) 
    robot.MotionCommand.ptp_axis(SDK.SmoothMode.Smooth.value, think_point)
    while True:
        check_state = robot.MotionCommand.get_motion_state()
        if check_state == 1:
            break
    time.sleep(0.5)
    think_point = SDK.Joint(-10.000, 47.000, -15.500, -25.000, -43.000, -0.000) 
    robot.MotionCommand.ptp_axis(SDK.SmoothMode.Smooth.value, think_point)
    while True:
        check_state = robot.MotionCommand.get_motion_state()
        if check_state == 1:
            break
    time.sleep(0.5)
    think_point = SDK.Joint(10.000, 47.000, -15.500, 25.000, -43.000, -0.00) 
    robot.MotionCommand.ptp_axis(SDK.SmoothMode.Smooth.value, think_point)

    time.sleep(0.5)

    while True:
        check_state = robot.MotionCommand.get_motion_state()
        if check_state == 1:
            break  

    robot.SystemCommand.set_override_ratio(75)
    think_point = SDK.Joint(0.000, 47.000, -15.500, 0.000, 30.000, -0.000) 
    robot.MotionCommand.ptp_axis(SDK.SmoothMode.Smooth.value, think_point)
    
    think_point = SDK.Joint(9.275, 47.000, -15.500, 0.000, 65.000, -0.000) 
    robot.MotionCommand.ptp_axis(SDK.SmoothMode.Smooth.value, think_point)
    think_point = SDK.Joint(9.275, 39.000, -1.500, 0.000, 59.000, -0.000) 
    robot.MotionCommand.ptp_axis(SDK.SmoothMode.Smooth.value, think_point)
    think_point = SDK.Joint(9.275, 47.000, -15.500, 0.000, 65.000, -0.000) 
    robot.MotionCommand.ptp_axis(SDK.SmoothMode.Smooth.value, think_point)
    think_point = SDK.Joint(9.275, 39.000, -1.500, 0.000, 59.000, -0.000) 
    robot.MotionCommand.ptp_axis(SDK.SmoothMode.Smooth.value, think_point)
    think_point = SDK.Joint(-19.000, 47.000, -15.500, 0.000, 65.000, -0.000) 
    robot.MotionCommand.ptp_axis(SDK.SmoothMode.Smooth.value, think_point)
    think_point = SDK.Joint(-19.000, 39.000, -1.500, 0.000, 59.000, -0.000) 
    robot.MotionCommand.ptp_axis(SDK.SmoothMode.Smooth.value, think_point)
    think_point = SDK.Joint(-19.000, 47.000, -15.500, 0.000, 65.000, -0.000) 
    robot.MotionCommand.ptp_axis(SDK.SmoothMode.Smooth.value, think_point)
    think_point = SDK.Joint(-19.000, 39.000, -1.500, 0.000, 59.000, -0.000) 
    robot.MotionCommand.ptp_axis(SDK.SmoothMode.Smooth.value, think_point)
    while True:
        check_state = robot.MotionCommand.get_motion_state()
        if check_state == 1:
            break  

# 畫手臂後 鞠躬三次
def bow_robot(robot):
    bow_point = SDK.Joint(0.000, 60.000, -24.500, 0.000, 30.000, 0.000) 
    robot.MotionCommand.ptp_axis(SDK.SmoothMode.Smooth.value, bow_point)
    time.sleep(0.1) 
    while True:
        check_state = robot.MotionCommand.get_motion_state()
        if check_state == 1:
            break  

    robot.SystemCommand.set_override_ratio(30)
    bow_point = SDK.Joint(30.000, 68.000, -61.500, 35.000, -122.000, 0.000) 
    robot.MotionCommand.ptp_axis(SDK.SmoothMode.Smooth.value, bow_point)
    bow_point = SDK.Joint(00.000, 60.000, -24.500, 0.000, 30.000, 0.000)
    robot.MotionCommand.ptp_axis(SDK.SmoothMode.Smooth.value, bow_point)

    # 另一向
    bow_point = SDK.Joint(-50.000, 68.000, -61.500, -35.000, -122.000, 0.000) 
    robot.MotionCommand.ptp_axis(SDK.SmoothMode.Smooth.value, bow_point)
    bow_point = SDK.Joint(-0.000, 60.000, -24.500, 0.000, 30.000, 0.000) 
    robot.MotionCommand.ptp_axis(SDK.SmoothMode.Smooth.value, bow_point)
   
    time.sleep(0.1) 
    while True:
        check_state = robot.MotionCommand.get_motion_state()
        if check_state == 1:
            break  

if __name__ == "__main__":
    print("Robot connecting..............")

    robot = SDK.InstanceRobot()
    #robot.ConnectionCommand.find_device()

    try:
        #robot.ConnectionCommand.open_connection(ip='192.168.6.50')
        robot.ConnectionCommand.open_connection(ip='127.0.0.1')
        robot.ControlerCommand.set_operation_mode(SDK.OperationMode.auto_mode.value)  # 高速
        robot.ConnectionCommand.set_connection_level(1)
    except:
        print("手臂連線異常，請重新連線！")

    write = WriteWord(robot_handle=robot,modify_z= 0)       # 寫字
    clean = CleanWord(robot_handle=robot)                   # 板擦
    draw_circle = draw_circle(robot_handle=robot)           # 畫圓


    # 啟動回 home
    robot_home(robot)
    print("Robot connect successful..............")
    print("====================================================")
    # # 清理
    print("開始擦玻璃..............")
    clean_start_point(robot)
    clean.clean_start(10)
    print("擦玻璃結束..............")
    robot_home(robot)


    # # 無限迴圈
    # while True:
    #     robot_home(robot)
    #     # region 開始寫字
    #
    #     print("開始寫字..............")
    #     word = WordInformation(FONT_SIZE, FONT, POINT_TO_MM)    # 文字資訊
    #
    #     robot.SystemCommand.set_override_ratio(30)
    #     # 寫字起始點
    #     write_start_point(robot)
    #     time.sleep(0.1)
    #     while True:
    #         check_state = robot.MotionCommand.get_motion_state()
    #         if check_state == 1:
    #             break
    #     message = "r = 210^%a, b = (1046, 193)^%PI = 3.14^%θ = np.arange(0, 2*PI, 0.01)^%X = a + r * np.cos(θ)^%Y = b + r * np.sin(θ)^%robot.open_connection(ip='192.168.0.2')^%for i in range(0, len(X), 1):^%    point = SDK.Point(X[i], Y[i], Z, A, B, C)^%    robot.Motion.lin_pos(SDK.Mode,1, point)"
    #     show_text = message.split(SEPARATE_CHAR)
    #     word_image , all_font_text_opencv = word.create_text_by_lines(show_text)
    #     #cv2.imshow('all', word_image)
    #     #cv2.waitKey(1)
    #
    #     height = 0
    #
    #     robot.CoordinateCommand.set_base_number(10)
    #     robot.SystemCommand.set_override_ratio(50)
    #
    #     for i in range(len(word.all_font_text_opencv)):
    #         word.thinning(word.all_font_text_opencv[i],"detail")
    #         word.sort_contours()
    #         #word.display(word.all_font_text_opencv[i].shape[0],word.all_font_text_opencv[i].shape[1])
    #         write.writing_twice(word_information=word, height_add=height, bound=0, modify_x=0, modify_y=0)
    #         height = height + height_add
    #
    #         while True:
    #             check_state = robot.MotionCommand.get_motion_state()
    #             if check_state == 1:
    #                 break
    #             time.sleep(0.1)
    #
    #     # 寫完後回安全點
    #     write_safe_point = SDK.Point(1142, 687.000, 175.000, 180.000, -62, -90.000)    #610
    #     robot.CoordinateCommand.set_base_number(10)
    #     robot.SystemCommand.set_override_ratio(15)
    #     robot.MotionCommand.lin_pos(SDK.LinSmoothMode.CloseSmooth.value,1, write_safe_point)
    #     while True:
    #         check_state = robot.MotionCommand.get_motion_state()
    #         if check_state == 1:
    #             break
    #     print("寫字結束..............")
    #     #endregion
    #
    #
    #     # region 開始畫圖騰
    #     print("開始圖騰..............")
    #     robot.CoordinateCommand.set_base_number(10)
    #     robot.SystemCommand.set_override_ratio(55)
    #
    #     circle_start_point(robot)
    #
    #     # 畫圖騰前 先在圖騰前思考
    #     think(robot)
    #     circle_start_point(robot)
    #
    #     robot.SystemCommand.set_override_ratio(55)
    #     draw_circle.draw(x = circle_x, y = circle_y, r = circle_r *3)                           # 最外層大圓，因此半徑乘三
    #
    #     draw_circle.draw(x = circle_x - circle_r, y = circle_y, r = circle_r )                  # (2) -X軸上圓1
    #     draw_circle.draw(x = circle_x - 2*circle_r, y = circle_y, r = circle_r )                # (3) -X軸上圓2
    #     draw_circle.draw(x = circle_x + circle_r, y = circle_y, r = circle_r )                  # (4) +X軸上圓1
    #     draw_circle.draw(x = circle_x + 2*circle_r, y = circle_y, r = circle_r )                # (5) +X軸上圓2
    #
    #     draw_circle.draw(x = circle_x, y = circle_y - circle_r*math.sqrt(3), r = circle_r )     # (6) -Y軸上圓1
    #     draw_circle.draw(x = circle_x, y = circle_y + circle_r*math.sqrt(3), r = circle_r )     # (7) +Y軸上圓1
    #     draw_circle.draw(x = circle_x + circle_r, y = circle_y - circle_r*math.sqrt(3), r = circle_r )     # (8) -Y面 三點1
    #     draw_circle.draw(x = circle_x - circle_r, y = circle_y - circle_r*math.sqrt(3), r = circle_r )     # (9) -Y面 三點3
    #     draw_circle.draw(x = circle_x + circle_r, y = circle_y + circle_r*math.sqrt(3), r = circle_r )     # (10) +Y面 三點1
    #     draw_circle.draw(x = circle_x - circle_r, y = circle_y + circle_r*math.sqrt(3), r = circle_r )     # (11) +Y面 三點3
    #
    #     draw_circle.draw(x = circle_x + 3/2*circle_r, y = circle_y - 1/2*circle_r*math.sqrt(3), r = circle_r )     # (12) -Y面 四點1
    #     draw_circle.draw(x = circle_x + 1/2*circle_r, y = circle_y - 1/2*circle_r*math.sqrt(3), r = circle_r )     # (13) -Y面 四點2
    #     draw_circle.draw(x = circle_x - 1/2*circle_r, y = circle_y - 1/2*circle_r*math.sqrt(3), r = circle_r )     # (14) -Y面 四點3
    #     draw_circle.draw(x = circle_x - 3/2*circle_r, y = circle_y - 1/2*circle_r*math.sqrt(3), r = circle_r )     # (15) -Y面 四點4
    #
    #     draw_circle.draw(x = circle_x + 3/2*circle_r, y = circle_y + 1/2*circle_r*math.sqrt(3), r = circle_r )     # (16) +Y面 四點1
    #     draw_circle.draw(x = circle_x + 1/2*circle_r, y = circle_y + 1/2*circle_r*math.sqrt(3), r = circle_r )     # (17) +Y面 四點2
    #     draw_circle.draw(x = circle_x - 1/2*circle_r, y = circle_y + 1/2*circle_r*math.sqrt(3), r = circle_r )     # (18) +Y面 四點3
    #     draw_circle.draw(x = circle_x - 3/2*circle_r, y = circle_y + 1/2*circle_r*math.sqrt(3), r = circle_r )     # (19) +Y面 四點4
    #
    #     draw_circle.draw(x = circle_x, y = circle_y, r = circle_r)                              # (1) 中心小圓
    #
    #     # 畫完回到安全點
    #
    #     circle_start_point(robot)
    #
    #     # 畫圖騰後 指向圖騰 開心
    #     happy(robot)
    #
    #     robot_home(robot)
    #     print("圖騰結束..............")
    #     time.sleep(10)
    #     # endregion
    #
    #
    #     # 清理
    #     print("開始擦玻璃..............")
    #     clean_start_point(robot)
    #     clean.clean_start(10)
    #     print("擦玻璃結束..............")
    #     robot_home(robot)
    #
    #     # region 畫手臂
    #     print("開始畫手臂..............")
    #     robot.CoordinateCommand.set_base_number(10)
    #     robot.SystemCommand.set_override_ratio(65)
    #
    #
    #     zero_point = SDK.Joint(-0.000, 71.000, -39.500, 0.000, 30.000, 0.000)
    #     time.sleep(0.1)
    #     while True:
    #         robot.MotionCommand.ptp_axis(SDK.SmoothMode.Smooth.value, zero_point)
    #         if(robot.MotionCommand.get_command_count() == 0):
    #             break;
    #
    #     # 畫手臂前 思考 下不了手
    #     think_robot(robot)
    #
    #     robot.SystemCommand.set_override_ratio(65)
    #     height = 0
    #     image = cv2.imread("robot_t.png",cv2.IMREAD_GRAYSCALE)
    #
    #     # 影像等比縮放
    #     image = cv2.resize(image, (int(image.shape[1] * shape_1), int(image.shape[0] * shape_0)), interpolation=cv2.INTER_CUBIC)
    #
    #     #cv2.imshow('all', image)
    #     #cv2.waitKey(1)
    #
    #     word.thinning(image,"detail")
    #     word.sort_contours(method="top-to-bottom")
    #     #word.display(image.shape[0],image.shape[1])
    #
    #     write.writing_twice(word_information=word,height_add=height,bound=0, modify_x=300 , modify_y = -20)
    #     while True:
    #         if(robot.MotionCommand.get_command_count() == 0):
    #             break;
    #         time.sleep(0.1)
    #
    #     # 寫完後回安全點
    #     write_safe_point = SDK.Point(887, 818.000, 113.000, 180.000, -62, -90.000)    #610
    #     robot.CoordinateCommand.set_base_number(10)
    #     robot.SystemCommand.set_override_ratio(25)
    #     robot.MotionCommand.ptp_pos(SDK.LinSmoothMode.CloseSmooth.value, write_safe_point)
    #     while True:
    #         check_state = robot.MotionCommand.get_motion_state()
    #         if check_state == 1:
    #             break
    #
    #     # 開始寫型號
    #     word2 = WordInformation(FONT_SIZE, FONT, POINT_TO_MM)    # 文字資訊
    #     print("開始寫手臂型號..............")
    #     message = "RA610-1672-GB"
    #     show_text = message.split(SEPARATE_CHAR)
    #
    #     word_image , all_font_text_opencv = word2.create_text_by_lines(show_text)
    #     #cv2.imshow('all', word_image)
    #     #cv2.waitKey(1)
    #
    #     height = 0
    #
    #     robot.CoordinateCommand.set_base_number(10)
    #     robot.SystemCommand.set_override_ratio(55)
    #
    #     for i in range(len(word2.all_font_text_opencv)):
    #         word2.thinning(word2.all_font_text_opencv[i],"detail")
    #         word2.sort_contours()
    #
    #         #word.display(word.all_font_text_opencv[i].shape[0],word.all_font_text_opencv[i].shape[1])
    #
    #         write.writing_twice(word_information=word2, height_add=height, bound=0, modify_x=208, modify_y=647)
    #         height = height + height_add
    #
    #         while True:
    #             check_state = robot.MotionCommand.get_motion_state()
    #             if check_state == 1:
    #                 break
    #             time.sleep(0.1)
    #
    #     # 寫完後回安全點
    #     write_safe_point = SDK.Point(643, 713.000, 112.000, 180.000, -62, -90.000)    #610
    #     robot.SystemCommand.set_override_ratio(25)
    #     robot.MotionCommand.ptp_pos(SDK.LinSmoothMode.CloseSmooth.value, write_safe_point)
    #     while True:
    #         check_state = robot.MotionCommand.get_motion_state()
    #         if check_state == 1:
    #             break
    #     print("畫手臂與型號結束..............")
    #
    #     # 最後鞠躬 3 次
    #     bow_robot(robot)
    #
    #     robot_home(robot)
    #
    #     # endregion
    #
    #
    #     # 清理
    #     print("開始擦玻璃..............")
    #
    #     clean_start_point(robot)
    #     clean.clean_start(10)
    #     robot_home(robot)
    #
    #     print("擦玻璃結束..............")
    #     print("====================================================")
