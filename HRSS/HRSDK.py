import os
import enum
import socket
#import zugbruecke as ctypes
from ctypes import *
from HRSS.Log.Log import Log,Level
CURRENT_FILE_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
HRSDK_DLL_PATH = os.path.join(CURRENT_FILE_DIRECTORY, "HRSDK.dll")


class AlarmCode(enum.Enum):
    ExecuteFail = -1
    UnAuthorized = 100
    UnableToExecute = 2000
    ParameterError = 2004
    CommandExecuteError = 2005
    UnableToAcceptCommand = 2006
    ModeProhibit = 4000
    ServerMotorProhibit = 4001
    MotionRegisterProhibited = 4003
    FileExecutionSettingError = 4010
    FileExecutionExecuteError = 4011
    FileExecutionNameError = 4012
    FileExecutionTaskError = 4013
    FunctionError = 9999

    @classmethod
    def check_value_exists(cls, value):
        return value not in (val.value for val in cls.__members__.values())


class ConnectionLevel(enum.Enum):
    operation_mode = 1
    monitor_mode = 0
    no = -1


class OperationMode(enum.Enum):
    manual_mode = 0
    auto_mode = 1


class CoordinateType(enum.Enum):
    Cartesian = 0
    Joint = 1
    Tool = 2


class SmoothMode(enum.Enum):
    CloseSmooth = 0
    Smooth = 1


class LinSmoothMode(enum.Enum):
    CloseSmooth = 0
    BezierCurve = 1
    BezierCurveRadius = 2
    Smooth = 3


class Point:
    def __init__(self, x, y, z, a, b, c):
        self.x = x
        self.y = y
        self.z = z
        self.a = a
        self.b = b
        self.c = c


class Joint:
    def __init__(self, a1, a2, a3, a4, a5, a6):
        self.a1 = a1
        self.a2 = a2
        self.a3 = a3
        self.a4 = a4
        self.a5 = a5
        self.a6 = a6


class InstanceRobot:
    def __init__(self, robot_ip="127.0.0.1", connection_level=ConnectionLevel.operation_mode.value,
                 password="", name="test", log=None):
        self.ip = robot_ip
        self.password = password
        self.robot_id = -1
        self.connection_level = connection_level
        self.is_connect = False
        if log is None:
            self.robot_log = Log(title="--Robot log--", path="Robot_" + name,level=Level.CRITICAL.value)
        else:
            self.robot_log = log
        #self.robot_callback_log = Log(title="--Robot log--", path="Robot_" + name+"_Callback")
        assert os.path.exists(HRSDK_DLL_PATH), \
            "HRSDK not found. Given path: {path}".format(path=HRSDK_DLL_PATH)
        self.HRSDKLib = cdll.LoadLibrary(HRSDK_DLL_PATH)
        #self.HRSDKLib = ctypes.windll.LoadLibrary(HRSDK_DLL_PATH).simple_demo_routine
        callback_type = CFUNCTYPE(None, c_uint16, c_uint16, POINTER(c_uint16), c_int)

        def callback_function(command, rlt, message, message_length):
            message_all = ""
            for i in range(message_length):
                message_all = message_all + chr(message[i])
            self.robot_log.error(message_all)

        self.callback = callback_type(callback_function)

        self.ConnectionCommand = self.ConnectionCommand(self)
        self.RegisterCommand = self.RegisterCommand(self)
        self.SystemCommand = self.SystemCommand(self)
        self.InputOutputCommand = self.InputOutputCommand(self)
        self.CoordinateCommand = self.CoordinateCommand(self)
        self.TaskCommand = self.TaskCommand(self)
        self.FileCommand = self.FileCommand(self)
        self.ControlerCommand = self.ControlerCommand(self)
        self.Jog = self.Jog(self)
        self.MotionCommand = self.MotionCommand(self)
        self.RobotInformation = self.RobotInformation(self)
        self.ConnectionCommand.get_hrsdk_version()

    class ConnectionCommand:
        def __init__(self, outer):
            self.outer = outer

        def open_connection(self, ip ):
            ip_byte = bytes(ip.encode("utf-8"))
            pass_word = bytes(self.outer.password.encode("utf-8"))
            self.outer.robot_id = self.outer.HRSDKLib.open_connection(c_char_p(ip_byte),
                                                                      c_int(self.outer.connection_level),
                                                                      self.outer.callback)
            self.outer.robot_log.info("open_connection,robot id: {%s}" % self.outer.robot_id)
            if self.outer.robot_id < 0:
                self.outer.is_connect = False
            else:
                self.outer.is_connect = True

            return self.outer.robot_id

        def close_connection(self):
            self.outer.HRSDKLib.close_connection(c_int(self.outer.robot_id))
            self.outer.robot_log.info("close_connection")
            self.outer.is_connect = False

        def set_connection_level(self, connect_level=ConnectionLevel.operation_mode.value):
            result = self.outer.HRSDKLib.set_connection_level(c_int(self.outer.robot_id), c_int(connect_level))
            if result == 0:
                self.outer.connection_level = connect_level
            self.outer.robot_log.info("set_connection_level: %s ,status: %s" % (connect_level,
                                                                                AlarmCode.check_value_exists(result)))
            return result

        def get_connection_level(self):
            result = self.outer.HRSDKLib.get_connection_level(c_int(self.outer.robot_id))
            if result is not -1 :
                self.outer.robot_log.info("get_connection_level: %s ,status: %s" % (ConnectionLevel(result),
                                                                                    AlarmCode.check_value_exists(result)))
            return ConnectionLevel(result)

        def get_hrsdk_version(self):
            version = create_string_buffer(15)
            result = self.outer.HRSDKLib.get_hrsdk_version(version)
            self.outer.robot_log.info("get_hrsdk_version,status: %s" % version.value.decode("utf-8"))
            return result, version.value.decode("utf-8")

        def find_device(self):
            class RobotBroadcast:
                def __init__(self,robot_ip,port,state,robot_id,robot_type,version):
                    self.robot_ip = robot_ip
                    self.port = port
                    self.state = state
                    self.robot_id = robot_id 
                    self.robot_type = robot_type
                    self.version = version

            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            s.settimeout(1)
            PORT = 3998
            s.bind(('192.168.0.100', PORT))
            print('Listening for broadcast at ', s.getsockname())
            s.sendto(b"Search_HRSS_Device",('<broadcast>', PORT))
            robot_list=list()
            try:
                while True:
                    data, address = s.recvfrom(65535)
                    ip = address[0]
                    port = address[1]
                    data=data.decode('utf-8')
                    if ',' in data:
                        aaaaa=data.split('{')[1].split('}')[0].split(',')
                        robot = {
                            'robot_ip':ip,
                            'port':port,
                            'state':aaaaa[0].split(':')[1].replace('\'',"").replace('\"',""),
                            'robot_id':aaaaa[1].split(':')[1].replace('\'',"").replace('\"',""),
                            'robot_type':aaaaa[2].split(':')[1].replace('\'',"").replace('\"',""),
                            'version':aaaaa[3].split(':')[1].replace('\'',"").replace('\"',"") 
                        }
                        robot_list.append(robot)
            except Exception as e:
                pass
            return robot_list
    
    class RegisterCommand:
        def __init__(self, outer):
            self.outer = outer

        def set_timer(self, index, value):
            result = self.outer.HRSDKLib.set_timer(c_int(self.outer.robot_id), c_int(index), c_int(value))
            self.outer.robot_log.info("set_timer: %s ,%s ,status: %s" % (index, value,
                                                                         AlarmCode.check_value_exists(result)))
            return result

        def get_timer(self, index):
            result = self.outer.HRSDKLib.get_timer(c_int(self.outer.robot_id), c_int(index))
            self.outer.robot_log.info("get_timer: %s ,%s ,status: %s" % (index, result,
                                                                         AlarmCode.check_value_exists(result)))
            return result

        def set_timer_start(self, index):
            result = self.outer.HRSDKLib.set_timer_start(c_int(self.outer.robot_id), c_int(index))
            self.outer.robot_log.info("set_timer_start: %s ,%s ,status: %s" % (index, result,
                                                                               AlarmCode.check_value_exists(result)))
            return result

        def set_timer_stop(self, index):
            result = self.outer.HRSDKLib.set_timer_stop(c_int(self.outer.robot_id), c_int(index))
            self.outer.robot_log.info("set_timer_stop: %s ,%s ,status: %s" % (index, result,
                                                                              AlarmCode.check_value_exists(result)))
            return result

        def set_counter(self, index, value):
            result = self.outer.HRSDKLib.set_counter(c_int(self.outer.robot_id), c_int(index), c_int(value))
            self.outer.robot_log.info("set_counter: %s ,%s ,status: %s " % (index, value,
                                                                            AlarmCode.check_value_exists(result)))
            return result

        def get_counter(self, index):
            result = self.outer.HRSDKLib.get_counter(c_int(self.outer.robot_id), c_int(index))
            self.outer.robot_log.info("get_counter: %s ,%s ,status: %s" % (index, result,
                                                                           AlarmCode.check_value_exists(result)))
            return result

        def set_pr_type(self, pr_num, coordinate_type):
            result = self.outer.HRSDKLib.set_pr_type(c_int(self.outer.robot_id), c_int(pr_num), c_int(coordinate_type))
            self.outer.robot_log.info("set_pr_type: %s ,%s ,status: %s" % (pr_num, CoordinateType(coordinate_type),
                                                                           AlarmCode.check_value_exists(result)))
            return result

        def get_pr_type(self, pr_num):
            result = self.outer.HRSDKLib.get_pr_type(c_int(self.outer.robot_id), c_int(pr_num))
            self.outer.robot_log.info("get_pr_type: %s ,%s ,status: %s" % (pr_num, result,
                                                                           AlarmCode.check_value_exists(result)))
            return result

        def set_pr_coordinate(self, pr_num, point):
            array = (c_double * 6)()
            array[0] = point.x
            array[1] = point.y
            array[2] = point.z
            array[3] = point.a
            array[4] = point.b
            array[5] = point.c
            result = self.outer.HRSDKLib.set_pr_coordinate(c_int(self.outer.robot_id), c_int(pr_num), array)
            self.outer.robot_log.info("set_pr_coordinate: %s ,{%s,%s,%s,%s,%s,%s} ,status: %s"
                                      % (pr_num, point.x, point.y, point.z, point.a, point.b, point.c,
                                         AlarmCode.check_value_exists(result)))
            return result

        def get_pr_coordinate(self, pr_num):
            array = (c_double * 6)()
            result = self.outer.HRSDKLib.get_pr_coordinate(c_int(self.outer.robot_id), c_int(pr_num), array)
            pr_point = Point(array[0], array[1], array[2], array[3], array[4], array[5])
            self.outer.robot_log.info("get_pr_coordinate: %s ,{%s,%s,%s,%s,%s,%s} ,status: %s"
                                      % (pr_num, pr_point.x, pr_point.y, pr_point.z, pr_point.a, pr_point.b, pr_point.c,
                                         AlarmCode.check_value_exists(result)))
            return result, pr_point

        def set_pr_tool_base(self, pr_num, tool, base):
            result = self.outer.HRSDKLib.set_pr_tool_base(c_int(self.outer.robot_id), c_int(pr_num),
                                                          c_int(tool), c_int(base))
            self.outer.robot_log.info("set_pr_tool_base: %s , %s, %s ,status: %s"
                                      % (pr_num, tool, base, AlarmCode.check_value_exists(result)))
            return result

        def get_pr_tool_base(self, pr_num):
            array = (c_int * 2)()
            result = self.outer.HRSDKLib.get_pr_tool_base(c_int(self.outer.robot_id), c_int(pr_num), array)
            self.outer.robot_log.info("set_pr_tool_base: %s , %s, %s ,status: %s"
                                      % (pr_num, array[0], array[1], AlarmCode.check_value_exists(result)))
            return result, array[0], array[1]

        def set_pr(self, pr_num, coordinate_type, point, tool, base):
            array = (c_double * 6)()
            array[0] = point.x
            array[1] = point.y
            array[2] = point.z
            array[3] = point.a
            array[4] = point.b
            array[5] = point.c
            result = self.outer.HRSDKLib.set_pr(c_int(self.outer.robot_id), c_int(pr_num), c_int(coordinate_type),
                                                array, c_int(tool), c_int(base))
            self.outer.robot_log.info("set_pr_tool_base: %s , %s, %s ,status: %s"
                                      % (pr_num, array[0], array[1], AlarmCode.check_value_exists(result)))
            return result, array[0], array[1]

        def get_pr(self, pr_num):
            array = (c_double * 6)()
            coor = byref(c_int())
            tool = byref(c_int())
            base = byref(c_int())
            result = self.outer.HRSDKLib.get_pr(c_int(self.outer.robot_id), c_int(pr_num), coor,
                                                array, tool, base)
            pr_point = Point(array[0], array[1], array[2], array[3], array[4], array[5])
            self.outer.robot_log.info("get_pr: %s,%s,%s,%s ,{%s,%s,%s,%s,%s,%s} ,status: %s"
                                      % (pr_num, coor._obj.value, tool._obj.value, base._obj.value,
                                         pr_point.x, pr_point.y, pr_point.z, pr_point.a, pr_point.b, pr_point.c,
                                         AlarmCode.check_value_exists(result)))
            return result, coor._obj.value, tool._obj.value, base._obj.value, pr_point

        def remove_pr(self, pr_num):
            result = self.outer.HRSDKLib.remove_pr(c_int(self.outer.robot_id), c_int(pr_num))
            self.outer.robot_log.info("remove_pr: %s ,status: %s" % (pr_num, AlarmCode.check_value_exists(result)))
            return result

    class SystemCommand:
        def __init__(self, outer):
            self.outer = outer

        def set_acc_dec_ratio(self, value):
            result = self.outer.HRSDKLib.set_acc_dec_ratio(c_int(self.outer.robot_id), c_int(value))
            self.outer.robot_log.info("set_acc_dec_ratio: %s ,%s ,status: %s" % (value, result,
                                                                                 AlarmCode.check_value_exists(result)))
            return result

        def get_acc_dec_ratio(self):
            result = self.outer.HRSDKLib.get_acc_dec_ratio(c_int(self.outer.robot_id))
            self.outer.robot_log.info("get_acc_dec_ratio: %s ,status: %s" % (result,
                                                                             AlarmCode.check_value_exists(result)))
            return result

        def set_ptp_speed(self, value):
            result = self.outer.HRSDKLib.set_ptp_speed(c_int(self.outer.robot_id), c_int(value))
            self.outer.robot_log.info("set_ptp_speed: %s ,%s ,status: %s" % (value, result,
                                                                                   AlarmCode.check_value_exists(result)))
            return result

        def get_ptp_speed(self):
            result = self.outer.HRSDKLib.get_ptp_speed(c_int(self.outer.robot_id))
            self.outer.robot_log.info("get_ptp_speed: %s ,status: %s" % (result,
                                                                               AlarmCode.check_value_exists(result)))
            return result

        def set_lin_speed(self, value):
            result = self.outer.HRSDKLib.set_lin_speed(c_int(self.outer.robot_id), c_double(value))
            self.outer.robot_log.info("set_lin_speed: %s ,%s ,status: %s" % (value, result,
                                                                             AlarmCode.check_value_exists(result)))
            return result

        def get_lin_speed(self):
            result = self.outer.HRSDKLib.get_lin_speed(c_int(self.outer.robot_id))
            self.outer.robot_log.info("get_lin_speed: %s ,status: %s" % (result, AlarmCode.check_value_exists(result)))
            return result

        def set_override_ratio(self, value):
            result = self.outer.HRSDKLib.set_override_ratio(c_int(self.outer.robot_id), c_int(value))
            self.outer.robot_log.info("set_override_ratio: %s ,%s ,status: %s" % (value, result,
                                                                                  AlarmCode.check_value_exists(result)))
            return result

        def get_override_ratio(self):
            result = self.outer.HRSDKLib.get_override_ratio(c_int(self.outer.robot_id))
            self.outer.robot_log.info("get_override_ratio: %s ,status: %s" % (result,
                                                                              AlarmCode.check_value_exists(result)))
            return result

        def set_robot_id(self, robot_id):
            c_robot_id = create_string_buffer(str.encode(robot_id), len(robot_id))
            result = self.outer.HRSDKLib.set_robot_id(c_int(self.outer.robot_id), c_robot_id)
            self.outer.robot_log.info("set_robot_id: %s, %s ,status: %s" % (robot_id, result,
                                                                            AlarmCode.check_value_exists(result)))
            return result

        def get_robot_id(self):
            c_robot_id = create_string_buffer(100)
            result = self.outer.HRSDKLib.get_robot_id(c_int(self.outer.robot_id), c_robot_id)
            self.outer.robot_log.info("set_robot_id: %s, %s ,status: %s" % (c_robot_id.value.decode("utf-8"), result,
                                                                            AlarmCode.check_value_exists(result)))
            return result, c_robot_id.value.decode("utf-8")

        def set_smooth_length(self, radius):
            result = self.outer.HRSDKLib.set_smooth_length(c_int(self.outer.robot_id), c_double(radius))
            self.outer.robot_log.info("set_smooth_length: %s, %s ,status: %s" % (radius, result,
                                                                            AlarmCode.check_value_exists(result)))
            return result

        def get_alarm_code(self):
            count = byref(c_int())
            # (c_double * 6)()
            alarm_code = (c_int64*20)()
            result = self.outer.HRSDKLib.get_alarm_code(c_int(self.outer.robot_id), count, alarm_code)
            self.outer.robot_log.info("get_alarm_code ,status: %s" % (AlarmCode.check_value_exists(result)))
            return result

        def get_error_msg(self):
            c_error = create_string_buffer(100)
            result = self.outer.HRSDKLib.get_error_msg(c_int(self.outer.robot_id), c_error)
            self.outer.robot_log.info("get_alarm_code: %s, %s ,status: %s" % (c_error.value.decode("utf-8"), result,
                                                                            AlarmCode.check_value_exists(result)))
            return result, c_error.value.decode("utf-8")

    class InputOutputCommand:
        def __init__(self, outer):
            self.outer = outer

        def get_digital_output(self, index):
            result = self.outer.HRSDKLib.get_digital_output(c_int(self.outer.robot_id), c_int(index))
            self.outer.robot_log.info("get_digital_output: %s,%s ,status: %s" % (index, result,
                                                                                 AlarmCode.check_value_exists(result)))
            return result

        def set_digital_output(self, index, value):
            result = self.outer.HRSDKLib.set_digital_output(c_int(self.outer.robot_id), c_int(index), c_bool(value))
            self.outer.robot_log.info("set_digital_output: %s,%s,%s ,status: %s" %
                                      (index, value, result, AlarmCode.check_value_exists(result)))
            return result

        def get_digital_input(self, index):
            result = self.outer.HRSDKLib.get_digital_input(c_int(self.outer.robot_id), c_int(index))
            self.outer.robot_log.info("get_digital_input: %s,%s ,status: %s" % (index, result,
                                                                                AlarmCode.check_value_exists(result)))
            return result

        def get_robot_input(self, index):
            result = self.outer.HRSDKLib.get_robot_input(c_int(self.outer.robot_id), c_int(index))
            self.outer.robot_log.info("get_digital_input: %s,%s ,status: %s" % (index, result,
                                                                                AlarmCode.check_value_exists(result)))
            return result

        def get_robot_output(self, index):
            result = self.outer.HRSDKLib.get_robot_output(c_int(self.outer.robot_id), c_int(index))
            self.outer.robot_log.info("get_robot_output: %s,%s ,status: %s" %
                                      (index, result, AlarmCode.check_value_exists(result)))
            return result

        def set_robot_output(self, index, value):
            result = self.outer.HRSDKLib.set_robot_output(c_int(self.outer.robot_id), c_int(index), c_bool(value))
            self.outer.robot_log.info("set_robot_output: %s,%s,%s ,status: %s" %
                                      (index, value, result, AlarmCode.check_value_exists(result)))
            return result

        def get_valve_output(self, index):
            result = self.outer.HRSDKLib.get_valve_output(c_int(self.outer.robot_id), c_int(index))
            self.outer.robot_log.info("get_valve_output: %s,%s ,status: %s" % (index, result,
                                                                               AlarmCode.check_value_exists(result)))
            return result

        def set_valve_output(self, index, value):
            result = self.outer.HRSDKLib.set_valve_output(c_int(self.outer.robot_id), c_int(index), c_bool(value))
            self.outer.robot_log.info("set_valve_output: %s,%s,%s ,status: %s" %
                                      (index, value, result, AlarmCode.check_value_exists(result)))
            return result

        def get_function_input(self, index):
            result = self.outer.HRSDKLib.get_function_input(c_int(self.outer.robot_id), c_int(index))
            self.outer.robot_log.info("get_function_input: %s,%s ,status: %s" % (index, result,
                                                                                 AlarmCode.check_value_exists(result)))
            return result

        def get_function_output(self, index):
            result = self.outer.HRSDKLib.get_function_output(c_int(self.outer.robot_id), c_int(index))
            self.outer.robot_log.info("get_function_output: %s,%s ,status: %s" % (index, result,
                                                                                  AlarmCode.check_value_exists(result)))
            return result

    class CoordinateCommand:
        def __init__(self, outer):
            self.outer = outer

        def set_base_number(self, index):
            result = self.outer.HRSDKLib.set_base_number(c_int(self.outer.robot_id), c_int(index))
            self.outer.robot_log.info("set_base_number: %s,%s ,status: %s" %
                                      (index, result, AlarmCode.check_value_exists(result)))
            return result

        def get_base_number(self):
            result = self.outer.HRSDKLib.get_base_number(c_int(self.outer.robot_id))
            self.outer.robot_log.info("get_base_number: %s,status: %s" %
                                      (result, AlarmCode.check_value_exists(result)))
            return result

        def define_base(self, base_num, point):
            array = (c_double * 6)()
            array[0] = point.x
            array[1] = point.y
            array[2] = point.z
            array[3] = point.a
            array[4] = point.b
            array[5] = point.c
            result = self.outer.HRSDKLib.define_base(c_int(self.outer.robot_id), c_int(base_num),array)
            self.outer.robot_log.info("define_base: %s,{%s,%s,%s,%s,%s,%s} ,status: %s" %
                                      (base_num, point.x, point.y, point.z, point.a, point.b, point.c,
                                       AlarmCode.check_value_exists(result)))
            return result

        def get_base_data(self, base_num):
            array = (c_double * 6)()
            result = self.outer.HRSDKLib.get_base_data(c_int(self.outer.robot_id), c_int(base_num), array)
            base_point = Point(array[0], array[1], array[2], array[3], array[4], array[5])
            self.outer.robot_log.info("get_base_data: %s,{%s,%s,%s,%s,%s,%s} ,status: %s" %
                                      (base_num, base_point.x, base_point.y, base_point.z, base_point.a,
                                       base_point.b, base_point.c, AlarmCode.check_value_exists(result)))
            return base_point

        def set_tool_number(self, index):
            result = self.outer.HRSDKLib.set_tool_number(c_int(self.outer.robot_id), c_int(index))
            self.outer.robot_log.info("set_tool_number: %s,%s ,status: %s" %
                                      (index, result, AlarmCode.check_value_exists(result)))
            return result

        def get_tool_number(self):
            result = self.outer.HRSDKLib.get_tool_number(c_int(self.outer.robot_id))
            self.outer.robot_log.info("get_tool_number: %s,status: %s" %
                                      (result, AlarmCode.check_value_exists(result)))
            return result

        def define_tool(self, base_num, point):
            array = (c_double * 6)()
            array[0] = point.x
            array[1] = point.y
            array[2] = point.z
            array[3] = point.a
            array[4] = point.b
            array[5] = point.c
            result = self.outer.HRSDKLib.define_tool(c_int(self.outer.robot_id), c_int(base_num),array)
            self.outer.robot_log.info("define_tool: %s,{%s,%s,%s,%s,%s,%s} ,status: %s" %
                                      (base_num, point.x, point.y, point.z, point.a, point.b, point.c,
                                       AlarmCode.check_value_exists(result)))
            return result

        def get_tool_data(self, base_num):
            array = (c_double * 6)()
            result = self.outer.HRSDKLib.get_tool_data(c_int(self.outer.robot_id), c_int(base_num), array)
            base_point = Point(array[0], array[1], array[2], array[3], array[4], array[5])
            self.outer.robot_log.info("get_tool_data: %s,{%s,%s,%s,%s,%s,%s} ,status: %s" %
                                      (base_num, base_point.x, base_point.y, base_point.z, base_point.a,
                                       base_point.b, base_point.c, AlarmCode.check_value_exists(result)))
            return base_point

    class TaskCommand:
        def __init__(self, outer):
            self.outer = outer

        def set_rsr(self, file_name, index):
            c_file_name = create_string_buffer(str.encode(file_name), len(file_name))
            result = self.outer.HRSDKLib.set_rsr(c_int(self.outer.robot_id), c_file_name, c_int(index))
            self.outer.robot_log.info("set_rsr: %s, %s ,status: %s" %
                                      (file_name, index,AlarmCode.check_value_exists(result)))
            return result

        def get_rsr_prog_name(self, index):
            c_file_name = create_string_buffer(100)
            result = self.outer.HRSDKLib.get_rsr_prog_name (c_int(self.outer.robot_id), c_int(index), c_file_name)
            self.outer.robot_log.info("get_rsr_prog_name: %s, %s ,status: %s" %
                                      (c_file_name.value.decode("utf-8"), index,AlarmCode.check_value_exists(result)))
            return c_file_name.value.decode("utf-8")

        def remove_rsr(self, index):
            result = self.outer.HRSDKLib.remove_rsr(c_int(self.outer.robot_id), c_int(index))
            self.outer.robot_log.info("remove_rsr: %s,status: %s" %
                                      (index, AlarmCode.check_value_exists(result)))
            return result

        def ext_task_start(self, mode, select):
            result = self.outer.HRSDKLib.ext_task_start(c_int(self.outer.robot_id), c_int(mode), c_int(select))
            self.outer.robot_log.info("ext_task_start: %s, %s , %s,status: %s" %
                                      (mode,select, result, AlarmCode.check_value_exists(result)))
            return result

        def task_start(self, file_name):
            c_file_name = create_string_buffer(str.encode(file_name), len(file_name))
            result = self.outer.HRSDKLib.task_start(c_int(self.outer.robot_id), c_file_name)
            self.outer.robot_log.info("task_start: %s,,status: %s" %
                                      (file_name, AlarmCode.check_value_exists(result)))
            return result

        def task_hold(self):
            result = self.outer.HRSDKLib.task_hold(c_int(self.outer.robot_id))
            self.outer.robot_log.info("task_hold,status: %s" %
                                      (AlarmCode.check_value_exists(result)))
            return result

        def task_continue(self):
            result = self.outer.HRSDKLib.task_continue(c_int(self.outer.robot_id))
            self.outer.robot_log.info("task_continue,status: %s" %
                                      (AlarmCode.check_value_exists(result)))
            return result

        def task_abort(self):
            result = self.outer.HRSDKLib.task_abort(c_int(self.outer.robot_id))
            self.outer.robot_log.info("task_abort,status: %s" %
                                      (AlarmCode.check_value_exists(result)))
            return result

        def get_execute_file_name(self):
            c_file_name = create_string_buffer(100)
            result = self.outer.HRSDKLib.get_execute_file_name(c_int(self.outer.robot_id),c_file_name)
            self.outer.robot_log.info("get_execute_file_name : %s ,status: %s" %
                                      (c_file_name.value.decode("utf-8"), AlarmCode.check_value_exists(result)))
            return result, c_file_name.value.decode("utf-8")

    class FileCommand:
        def __init__(self, outer):
            self.outer = outer

        def download_file(self, from_path, to_path):
            c_from_path = create_string_buffer(str.encode(from_path), len(from_path))
            c_to_path = create_string_buffer(str.encode(to_path), len(to_path))
            result = self.outer.HRSDKLib.download_file(c_int(self.outer.robot_id), c_from_path, c_to_path)
            self.outer.robot_log.info("download_file,status: %s" %
                                      (AlarmCode.check_value_exists(result)))
            return result

        # TODO : send_file 跳過
        def send_file(self, root_folder, from_path, to_path, opt):
            c_from_path = create_string_buffer(str.encode(from_path), len(from_path))
            c_to_path = create_string_buffer(str.encode(to_path), len(to_path))
            result = self.outer.HRSDKLib.download_file(c_int(self.outer.robot_id), c_from_path, c_to_path)
            self.outer.robot_log.info("send_file,status: %s" %
                                      (AlarmCode.check_value_exists(result)))
            return result

    class ControlerCommand:
        def __init__(self, outer):
            self.outer = outer

        def get_hrss_mode(self):
            result = self.outer.HRSDKLib.get_hrss_mode(c_int(self.outer.robot_id))
            self.outer.robot_log.info("get_hrss_mode:%s,status: %s" %
                                      (result,AlarmCode.check_value_exists(result)))
            return result

        def set_motor_state(self, state):
            result = self.outer.HRSDKLib.set_motor_state(c_int(self.outer.robot_id), c_int(state))
            self.outer.robot_log.info("set_motor_state :%s ,%s,status: %s" %
                                      (state, result, AlarmCode.check_value_exists(result)))

        def get_motor_state(self):
            result = self.outer.HRSDKLib.get_motor_state(c_int(self.outer.robot_id))
            self.outer.robot_log.info("get_motor_state :%s,status: %s" %
                                      (result, AlarmCode.check_value_exists(result)))
            return result

        def set_operation_mode(self, mode):
            result = self.outer.HRSDKLib.set_operation_mode(c_int(self.outer.robot_id),c_int(mode))
            self.outer.robot_log.info("set_operation_mode :%s,%s,status: %s" %
                                      (mode, result, AlarmCode.check_value_exists(result)))
            return result

        def get_operation_mode(self):
            result = self.outer.HRSDKLib.get_operation_mode(c_int(self.outer.robot_id))
            self.outer.robot_log.info("get_operation_mode :%s,status: %s" %
                                      (OperationMode(result), AlarmCode.check_value_exists(result)))
            return result

        def clear_alarm(self):
            result = self.outer.HRSDKLib.clear_alarm(c_int(self.outer.robot_id))
            self.outer.robot_log.info("clear_alarm :%s,status: %s" %
                                      (result, AlarmCode.check_value_exists(result)))
            return result

    class Jog:
        def __init__(self, outer):
            self.outer = outer

        def jog(self, space_type, index, direction):
            result = self.outer.HRSDKLib.jog(c_int(self.outer.robot_id), c_int(space_type),c_int(index), c_int(direction))
            self.outer.robot_log.info("jog: %s,%s,%s,%s ,status: %s" %
                                      (space_type, index, direction, result,
                                       AlarmCode.check_value_exists(result)))
            return result

        def jog_stop(self):
            result = self.outer.HRSDKLib.jog_stop(c_int(self.outer.robot_id))
            self.outer.robot_log.info("jog_stop: %s ,status: %s" %
                                      (result, AlarmCode.check_value_exists(result)))
            return result

        def jog_home(self):
            result = self.outer.HRSDKLib.jog_home(c_int(self.outer.robot_id))
            self.outer.robot_log.info("jog_home ,status: %s" %
                                      (AlarmCode.check_value_exists(result)))
            return result

    class MotionCommand:
        def __init__(self, outer):
            self.outer = outer

        def ptp_pos(self, mode, point):
            array = (c_double * 6)()
            array[0] = point.x
            array[1] = point.y
            array[2] = point.z
            array[3] = point.a
            array[4] = point.b
            array[5] = point.c
            result = self.outer.HRSDKLib.ptp_pos(c_int(self.outer.robot_id), c_int(mode), array)
            self.outer.robot_log.info("ptp_pos: %s ,{%s,%s,%s,%s,%s,%s} ,%s ,status: %s"
                                      % (mode, point.x, point.y, point.z, point.a, point.b, point.c, result,
                                         AlarmCode.check_value_exists(result)))
            return result

        def ptp_axis(self, mode, joint):
            array = (c_double * 6)()
            array[0] = joint.a1
            array[1] = joint.a2
            array[2] = joint.a3
            array[3] = joint.a4
            array[4] = joint.a5
            array[5] = joint.a6
            result = self.outer.HRSDKLib.ptp_axis(c_int(self.outer.robot_id), c_int(mode), array)
            self.outer.robot_log.info("ptp_axis: %s ,{%s,%s,%s,%s,%s,%s} ,%s ,status: %s"
                                      % (mode, joint.a1, joint.a2, joint.a3, joint.a4, joint.a5, joint.a6, result,
                                         AlarmCode.check_value_exists(result)))
            return result

        def ptp_rel_pos(self, mode, point):
            array = (c_double * 6)()
            array[0] = point.x
            array[1] = point.y
            array[2] = point.z
            array[3] = point.a
            array[4] = point.b
            array[5] = point.c
            result = self.outer.HRSDKLib.ptp_rel_pos(c_int(self.outer.robot_id), c_int(mode), array)
            self.outer.robot_log.info("ptp_rel_pos: %s ,{%s,%s,%s,%s,%s,%s} ,%s ,status: %s"
                                      % (mode, point.x, point.y, point.z, point.a, point.b, point.c, result,
                                         AlarmCode.check_value_exists(result)))
            return result

        def ptp_rel_axis(self, mode, joint):
            array = (c_double * 6)()
            array[0] = joint.a1
            array[1] = joint.a2
            array[2] = joint.a3
            array[3] = joint.a4
            array[4] = joint.a5
            array[5] = joint.a6
            result = self.outer.HRSDKLib.ptp_rel_axis(c_int(self.outer.robot_id), c_int(mode), array)
            self.outer.robot_log.info("ptp_rel_axis: %s ,{%s,%s,%s,%s,%s,%s} ,%s ,status: %s"
                                      % (mode, joint.a1, joint.a2, joint.a3, joint.a4, joint.a5, joint.a6, result,
                                         AlarmCode.check_value_exists(result)))
            return result

        def ptp_pr(self, mode, num):
            result = self.outer.HRSDKLib.ptp_pr(c_int(self.outer.robot_id), c_int(mode), c_int(num))
            self.outer.robot_log.info("ptp_pr: %s ,%s ,%s ,status: %s"
                                      % (mode, num, result,
                                         AlarmCode.check_value_exists(result)))
            return result

        def lin_pos(self, mode, smooth_value, point):
            array = (c_double * 6)()
            array[0] = point.x
            array[1] = point.y
            array[2] = point.z
            array[3] = point.a
            array[4] = point.b
            array[5] = point.c
            result = self.outer.HRSDKLib.lin_pos(c_int(self.outer.robot_id), c_int(mode), c_double(smooth_value), array)
            self.outer.robot_log.info("lin_pos: %s ,{%s,%s,%s,%s,%s,%s} ,%s ,status: %s"
                                      % (mode, point.x, point.y, point.z, point.a, point.b, point.c, result,
                                         AlarmCode.check_value_exists(result)))
            return result

        def lin_axis(self, mode, smooth_value, joint):
            array = (c_double * 6)()
            array[0] = joint.a1
            array[1] = joint.a2
            array[2] = joint.a3
            array[3] = joint.a4
            array[4] = joint.a5
            array[5] = joint.a6
            result = self.outer.HRSDKLib.lin_axis(c_int(self.outer.robot_id), c_int(mode), c_int(smooth_value), array)
            self.outer.robot_log.info("ptp_rel_axis: %s ,{%s,%s,%s,%s,%s,%s} ,%s ,status: %s"
                                      % (mode, joint.a1, joint.a2, joint.a3, joint.a4, joint.a5, joint.a6, result,
                                         AlarmCode.check_value_exists(result)))
            return result

        def lin_rel_pos(self, mode, smooth_value, point):
            array = (c_double * 6)()
            array[0] = point.x
            array[1] = point.y
            array[2] = point.z
            array[3] = point.a
            array[4] = point.b
            array[5] = point.c
            result = self.outer.HRSDKLib.lin_rel_pos(c_int(self.outer.robot_id), c_int(mode), c_int(smooth_value), array)
            self.outer.robot_log.info("lin_rel_pos: %s ,{%s,%s,%s,%s,%s,%s} ,%s ,status: %s"
                                      % (mode, point.x, point.y, point.z, point.a, point.b, point.c, result,
                                         AlarmCode.check_value_exists(result)))
            return result

        def lin_rel_axis(self, mode, smooth_value, joint):
            array = (c_double * 6)()
            array[0] = joint.a1
            array[1] = joint.a2
            array[2] = joint.a3
            array[3] = joint.a4
            array[4] = joint.a5
            array[5] = joint.a6
            result = self.outer.HRSDKLib.lin_axis(c_int(self.outer.robot_id), c_int(mode), c_int(smooth_value), array)
            self.outer.robot_log.info("lin_rel_axis: %s ,{%s,%s,%s,%s,%s,%s} ,%s ,status: %s"
                                      % (mode, joint.a1, joint.a2, joint.a3, joint.a4, joint.a5, joint.a6, result,
                                         AlarmCode.check_value_exists(result)))
            return result

        def lin_pr(self, mode, smooth_value, num):
            result = self.outer.HRSDKLib.lin_pr(c_int(self.outer.robot_id), c_int(mode), c_int(smooth_value), c_int(num))
            self.outer.robot_log.info("lin_pr: %s ,%s ,%s ,status: %s"
                                      % (mode, num, result,
                                         AlarmCode.check_value_exists(result)))
            return result

        def circ_pos(self, mode, point_start, point_end):
            array_start = (c_double * 6)()
            array_start[0] = point_start.x
            array_start[1] = point_start.y
            array_start[2] = point_start.z
            array_start[3] = point_start.a
            array_start[4] = point_start.b
            array_start[5] = point_start.c
            array_end = (c_double * 6)()
            array_end[0] = point_end.x
            array_end[1] = point_end.y
            array_end[2] = point_end.z
            array_end[3] = point_end.a
            array_end[4] = point_end.b
            array_end[5] = point_end.c
            result = self.outer.HRSDKLib.circ_pos(c_int(self.outer.robot_id), c_int(mode), array_start, array_end)
            self.outer.robot_log.info("circ_pos: %s ,status: %s"
                                      % (result, AlarmCode.check_value_exists(result)))
            return result

        def motion_hold(self):
            result = self.outer.HRSDKLib.motion_hold(c_int(self.outer.robot_id))
            self.outer.robot_log.info("motion_hold: %s ,status: %s" %
                                      (result, AlarmCode.check_value_exists(result)))
            return result

        def motion_continue(self):
            result = self.outer.HRSDKLib.motion_continue(c_int(self.outer.robot_id))
            self.outer.robot_log.info("motion_continue: %s ,status: %s" %
                                      (result, AlarmCode.check_value_exists(result)))
            return result

        def motion_abort(self):
            result = self.outer.HRSDKLib.motion_abort(c_int(self.outer.robot_id))
            self.outer.robot_log.info("motion_abort: %s ,status: %s" %
                                      (result, AlarmCode.check_value_exists(result)))
            return result

        def motion_delay(self, delay_time):
            result = self.outer.HRSDKLib.motion_delay(c_int(self.outer.robot_id), c_int(delay_time))
            self.outer.robot_log.info("motion_abort: %s ,status: %s" %
                                      (result, AlarmCode.check_value_exists(result)))
            return result

        def get_command_count(self):
            result = self.outer.HRSDKLib.get_command_count(c_int(self.outer.robot_id))
            self.outer.robot_log.info("get_command_count: %s ,status: %s" %
                                      (result, AlarmCode.check_value_exists(result)))
            return result

        def get_motion_state(self):
            result = self.outer.HRSDKLib.get_motion_state(c_int(self.outer.robot_id))
            self.outer.robot_log.info("get_motion_state: %s ,status: %s" %
                                      (result, AlarmCode.check_value_exists(result)))
            return result

        def remove_command(self, num):
            result = self.outer.HRSDKLib.remove_command(c_int(self.outer.robot_id), c_int(num))
            self.outer.robot_log.info("remove_command: %s %s,status: %s" %
                                      (num,result, AlarmCode.check_value_exists(result)))
            return result

        def remove_command_tail(self, num):
            result = self.outer.HRSDKLib.remove_command_tail(c_int(self.outer.robot_id), c_int(num))
            self.outer.robot_log.info("remove_command_tail: %s %s,status: %s" %
                                      (num, result, AlarmCode.check_value_exists(result)))
            return result

    class RobotInformation:
        def __init__(self, outer):
            self.outer = outer

        def get_encoder_count(self):
            array = (c_int32 * 6)()
            result = self.outer.HRSDKLib.get_encoder_count(c_int(self.outer.robot_id), array)
            encoder = []
            for i in range(0,6,1):
                encoder.append(array[i])
            self.outer.robot_log.info("get_encoder_count:,{%s,%s,%s,%s,%s,%s} ,%s ,status: %s"
                                      % (encoder[0], encoder[1], encoder[2], encoder[3], encoder[4], encoder[5],
                                         result, AlarmCode.check_value_exists(result)))
            return encoder

        def get_current_joint(self):
            array = (c_double * 6)()
            result = self.outer.HRSDKLib.get_current_joint(c_int(self.outer.robot_id), array)
            joint = Joint(array[0], array[1], array[2], array[3], array[4], array[5])
            self.outer.robot_log.info("get_current_joint:,{%s,%s,%s,%s,%s,%s} ,%s ,status: %s"
                                      % (joint.a1, joint.a2, joint.a3, joint.a4, joint.a5, joint.a6,
                                         result, AlarmCode.check_value_exists(result)))
            return joint

        def get_current_position(self):
            array = (c_double * 6)()
            result = self.outer.HRSDKLib.get_current_position(c_int(self.outer.robot_id), array)
            point = Point(array[0], array[1], array[2], array[3], array[4], array[5])
            self.outer.robot_log.info("get_current_position:,{%s,%s,%s,%s,%s,%s} ,%s ,status: %s"
                                      % (point.x, point.y, point.z, point.a, point.b, point.c,
                                         result, AlarmCode.check_value_exists(result)))
            return point,result

        def get_current_rpm(self):
            array = (c_double * 6)()
            result = self.outer.HRSDKLib.get_current_rpm(c_int(self.outer.robot_id), array)
            rpm=[]
            for i in range(0, 6, 1):
                rpm.append(array[i])
            self.outer.robot_log.info("get_current_rpm:,{%s,%s,%s,%s,%s,%s} ,%s ,status: %s"
                                      % (rpm[0], rpm[1], rpm[2], rpm[3], rpm[4], rpm[5],
                                         result, AlarmCode.check_value_exists(result)))
            return rpm

        def get_device_born_date(self):
            array = (c_int * 3)()
            result = self.outer.HRSDKLib.get_device_born_date(c_int(self.outer.robot_id), array)
            born = []
            for i in range(0, 3, 1):
                born.append(array[i])
            self.outer.robot_log.info("get_device_born_date:,{%s,%s,%s} ,%s ,status: %s"
                                      % (born[0], born[1], born[2],
                                         result, AlarmCode.check_value_exists(result)))
            return born

        def get_operation_time(self):
            array = (c_int * 5)()
            result = self.outer.HRSDKLib.get_operation_time(c_int(self.outer.robot_id), array)
            time = []
            for i in range(0, 5, 1):
                time.append(array[i])
            self.outer.robot_log.info("get_operation_time:,{%s,%s,%s,%s,%s} ,%s ,status: %s"
                                      % (time[0], time[1], time[2],time[3],time[4],
                                         result, AlarmCode.check_value_exists(result)))
            return time

        def get_mileage(self):
            array = (c_double * 6)()
            result = self.outer.HRSDKLib.get_mileage(c_int(self.outer.robot_id), array)
            mileage = []
            for i in range(0, 6, 1):
                mileage.append(array[i])
            self.outer.robot_log.info("get_mileage:,{%s,%s,%s,%s,%s,%s} ,%s ,status: %s"
                                      % (mileage[0], mileage[1], mileage[2], mileage[3], mileage[4], mileage[5],
                                         result, AlarmCode.check_value_exists(result)))
            return mileage

        def get_total_mileage(self):
            array = (c_double * 6)()
            result = self.outer.HRSDKLib.get_total_mileage(c_int(self.outer.robot_id), array)
            mileage = []
            for i in range(0, 6, 1):
                mileage.append(array[i])
            self.outer.robot_log.info("get_total_mileage:,{%s,%s,%s,%s,%s,%s} ,%s ,status: %s"
                                      % (mileage[0], mileage[1], mileage[2], mileage[3], mileage[4], mileage[5],
                                         result, AlarmCode.check_value_exists(result)))
            return mileage

        def get_utilization(self):
            array = (c_int * 6)()
            result = self.outer.HRSDKLib.get_utilization(c_int(self.outer.robot_id), array)
            utilization = []
            for i in range(0, 6, 1):
                utilization.append(array[i])
            self.outer.robot_log.info("get_utilization:,{%s,%s,%s,%s,%s,%s} ,%s ,status: %s"
                                      % (utilization[0], utilization[1], utilization[2], utilization[3],
                                         utilization[4], utilization[5], result, AlarmCode.check_value_exists(result)))
            return utilization

        def get_utilization_ratio(self):
            result = self.outer.HRSDKLib.get_utilization_ratio((c_int(self.outer.robot_id)))
            self.outer.robot_log.info("get_utilization_ratio: %s ,status: %s"
                                      % (result, AlarmCode.check_value_exists(result)))
            return result

        def get_motor_torque(self):
            array = (c_int * 6)()
            result = self.outer.HRSDKLib.get_motor_torque(c_int(self.outer.robot_id), array)
            torque = []
            for i in range(0, 6, 1):
                torque.append(array[i])
            self.outer.robot_log.info("get_motor_torque:,{%s,%s,%s,%s,%s,%s} ,%s ,status: %s"
                                      % (torque[0], torque[1], torque[2], torque[3],
                                         torque[4], torque[5], result, AlarmCode.check_value_exists(result)))
            return torque

        def get_hrss_version(self):
            c_version = create_string_buffer(100)
            result = self.outer.HRSDKLib.get_hrss_version(c_int(self.outer.robot_id), c_version)
            self.outer.robot_log.info("get_hrss_version %s ,status: %s" %
                                      (c_version.value.decode("utf-8"), AlarmCode.check_value_exists(result)))
            return result , c_version.value.decode("utf-8")

        def get_robot_type(self):
            c_version = create_string_buffer(100)
            result = self.outer.HRSDKLib.get_robot_type(c_int(self.outer.robot_id), c_version)
            self.outer.robot_log.info("get_robot_type %s ,status: %s" %
                                      (c_version.value.decode("utf-8"), AlarmCode.check_value_exists(result)))
            return result, c_version.value.decode("utf-8")


