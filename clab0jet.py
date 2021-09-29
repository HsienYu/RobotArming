# -*- coding: UTF-8 -*-
import HRSS.HRSDK as SDK
import cv2
import time
import numpy as np
import math
import sys
import traceback
import os


POINT_TO_MM = 0.32577778


# 手臂回 Home
def robot_home(robot):
    standby_point_home = SDK.Joint(0, 72.000, -39.500, 0.000, -122, 0.000)  # 610

    robot.SystemCommand.set_override_ratio(25)
    robot.CoordinateCommand.set_base_number(0)
    robot.MotionCommand.ptp_axis(SDK.SmoothMode.Smooth.value, standby_point_home)
    while True:
        check_state = robot.MotionCommand.get_motion_state()
        time.sleep(0.3)
        if check_state == 1:
            break
    time.sleep(1)




# 思考


def think(robot):
    time.sleep(1)
    robot.CoordinateCommand.set_base_number(10)
    robot.SystemCommand.set_override_ratio(15)

    think_point_first = SDK.Point(1047.000, 198.000, 135.500, 180.000, -62.000, -91.000)
    robot.MotionCommand.lin_pos(SDK.SmoothMode.Smooth.value, 1, think_point_first)

    think_point_first.x = think_point_first.x + 210
    robot.MotionCommand.lin_pos(SDK.SmoothMode.Smooth.value, 1, think_point_first)
    think_point_first.x = think_point_first.x - 420
    robot.MotionCommand.lin_pos(SDK.SmoothMode.Smooth.value, 1, think_point_first)
    think_point_first.x = think_point_first.x + 210
    robot.MotionCommand.lin_pos(SDK.SmoothMode.Smooth.value, 1, think_point_first)
    think_point_first.y = think_point_first.y - 210
    robot.MotionCommand.lin_pos(SDK.SmoothMode.Smooth.value, 1, think_point_first)
    think_point_first.y = think_point_first.y + 420
    robot.MotionCommand.lin_pos(SDK.SmoothMode.Smooth.value, 1, think_point_first)
    think_point_first.y = think_point_first.y - 210
    robot.MotionCommand.lin_pos(SDK.SmoothMode.Smooth.value, 1, think_point_first)
    time.sleep(1)
    while True:
        check_state = robot.MotionCommand.get_motion_state()
        if check_state == 1:
            break
            # 畫錯 擦掉
    robot.SystemCommand.set_override_ratio(20)

    draw_error_point = SDK.Point(1258.000, 210.000, 83.500, 180.000, -62.000, -90.000)
    robot.MotionCommand.lin_pos(SDK.SmoothMode.Smooth.value, 1, draw_error_point)
    draw_error_point = SDK.Point(1258.000, 210.000, 0.500, 180.000, -62.000, -90.000)
    robot.MotionCommand.lin_pos(SDK.SmoothMode.Smooth.value, 1, draw_error_point)
    draw_error_point = SDK.Point(1120.000, 300.000, 0.500, 180.000, -62.000, -90.000)
    robot.MotionCommand.lin_pos(SDK.SmoothMode.Smooth.value, 1, draw_error_point)
    while True:
        check_state = robot.MotionCommand.get_motion_state()
        if check_state == 1:
            break
    robot.SystemCommand.set_override_ratio(70)
    draw_error_point = SDK.Point(1120.000, 300.000, 88.500, 180.000, -62.000, -90.000)
    robot.MotionCommand.lin_pos(SDK.SmoothMode.Smooth.value, 1, draw_error_point)
    while True:
        check_state = robot.MotionCommand.get_motion_state()
        if check_state == 1:
            break
    time.sleep(1)
    # 擦
    robot.SystemCommand.set_override_ratio(100)
    clearn_error_point = SDK.Joint(63.300, 14.300, 6.500, -51.100, -79.700, 58.300)
    robot.MotionCommand.lin_axis(SDK.SmoothMode.Smooth.value, 1, clearn_error_point)
    while True:
        check_state = robot.MotionCommand.get_motion_state()
        if check_state == 1:
            break
    robot.SystemCommand.set_override_ratio(40)
    clearn_error_point = SDK.Point(1302.500, 108.300, -42.000, 180.000, 30.000, -90.000)
    robot.MotionCommand.lin_pos(SDK.SmoothMode.Smooth.value, 1, clearn_error_point)
    clearn_error_point = SDK.Point(1043.000, 217.000, -42.000, 180.000, 30.000, -90.000)
    robot.MotionCommand.lin_pos(SDK.SmoothMode.Smooth.value, 1, clearn_error_point)

    clearn_error_point = SDK.Joint(55.000, 39.000, -17.500, -49.000, -72.000, 53.000)
    robot.MotionCommand.lin_axis(SDK.SmoothMode.Smooth.value, 1, clearn_error_point)
    while True:
        check_state = robot.MotionCommand.get_motion_state()
        if check_state == 1:
            break

# 畫圖騰後 指向圖騰 開心


def happy(robot):
    robot.CoordinateCommand.set_base_number(10)
    robot.SystemCommand.set_override_ratio(30)

    happy_point = SDK.Point(832.000, 351.000, 53.500, 180.000, -62.000, -91.000)
    robot.MotionCommand.lin_pos(SDK.SmoothMode.Smooth.value, 1, happy_point)
    happy_point = SDK.Point(832.000, 351.000, 0.000, 180.000, -62.000, -91.000)
    robot.MotionCommand.lin_pos(SDK.SmoothMode.Smooth.value, 1, happy_point)
    time.sleep(0.1)
    while True:
        check_state = robot.MotionCommand.get_motion_state()
        if check_state == 1:
            break
    happy_point = SDK.Point(832.000, 351.000, 53.500, 180.000, -62.000, -91.000)
    robot.MotionCommand.lin_pos(SDK.SmoothMode.Smooth.value, 1, happy_point)
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
    robot.MotionCommand.lin_pos(SDK.SmoothMode.Smooth.value, 1, think_robot_point)
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
    # robot.ConnectionCommand.find_device()

    try:
        #robot.ConnectionCommand.open_connection(ip='192.168.6.50')
        robot.ConnectionCommand.open_connection(ip='127.0.0.1')
        robot.ControlerCommand.set_operation_mode(SDK.OperationMode.auto_mode.value)  # 高速
        robot.ConnectionCommand.set_connection_level(1)
    except:
        print("手臂連線異常，請重新連線！")


    #啟動回 home
    robot_home(robot)
    print("Robot connect successful..............")
    print("====================================================")
    

    # 無限迴圈
    while True:
        robot_home(robot)
        #init word method

\
        # region 畫手臂
        print("開始畫手臂..............")
        robot.CoordinateCommand.set_base_number(10)
        robot.SystemCommand.set_override_ratio(65)


        zero_point = SDK.Joint(-0.000, 71.000, -39.500, 0.000, 30.000, 0.000)
        time.sleep(0.1)
        while True:
            robot.MotionCommand.ptp_axis(SDK.SmoothMode.Smooth.value, zero_point)
            if(robot.MotionCommand.get_command_count() == 0):
                break;

        # 畫手臂前 思考 下不了手
        think_robot(robot)

        robot.SystemCommand.set_override_ratio(65)




        robot.CoordinateCommand.set_base_number(10)
        robot.SystemCommand.set_override_ratio(55)


        # 寫完後回安全點
        write_safe_point = SDK.Point(643, 713.000, 112.000, 180.000, -62, -90.000)    #610
        robot.SystemCommand.set_override_ratio(25)
        robot.MotionCommand.ptp_pos(SDK.LinSmoothMode.CloseSmooth.value, write_safe_point)
        while True:
            check_state = robot.MotionCommand.get_motion_state()
            if check_state == 1:
                break
        print("畫手臂與型號結束..............")

        # 最後鞠躬 3 次
        bow_robot(robot)

        robot_home(robot)

        # endregion
