#!/usr/bin/python

import json
import struct
import socket
import os


RUN_COMMAND = 0    # Runs the payload as sway commands
GET_WORKSPACES = 1    # Get the list of current workspaces
SUBSCRIBE = 2    # Subscribe the IPC connection to the events listed in the pay‐load
GET_OUTPUTS = 3    # Get the list of current outputs
GET_TREE = 4    # Get the node layout tree
GET_MARKS = 5    # Get the names of all the marks currently set
GET_BAR_CONFIG = 6    # Get the specified bar config or a list of bar config names
GET_VERSION = 7    # Get the version of sway that owns the IPC socket
GET_BINDING_MODES = 8    # Get the list of binding mode names
GET_CONFIG = 9    # Returns the config that was last loaded
SEND_TICK = 10    # Sends a tick event with the specified payload
SYNC = 11    # Replies failure object for i3 compatibility
GET_INPUTS = 100    # Get the list of input devices
GET_SEATS = 101    # Get the list of seats
    

class Sway:
    def __init__(self):
        socket = self.sway_get_socketpath()
        if socket:
            self.socket = socket
            return
        socket = self.sway_get_socketpath_v2()
        if socket:
            self.socket = socket
            return
        raise(Exception("Not sway instance exist!"))

    def sway_get_socketpath(self):
        try:
            return os.environ["SWAYSOCK"]
        except:
            return ""

    def sway_get_socketpath_v2(self):
        import psutil
        from systemd import login
        try:
            uid = login.uids()[0]
            sway_pid = [p.info for p in psutil.process_iter(attrs=['pid', 'name']) if 'sway' == p.info['name']][0]['pid']
            SWAYSOCK = "/run/user/{uid}/sway-ipc.{uid}.{sway_pid}.sock".format(uid=uid, sway_pid=sway_pid)
            return SWAYSOCK
        except:
            return ""

    def sway_get_window_focus(self):
        output = self.sway_get_tree()
        j = json.loads(output)
        for w in j['nodes']:
            for _w in w['nodes']:
                # print("{}".format(_w["name"]))
                try:
                    for __w in _w['nodes']:
                        if __w['focused']:
                            return __w["name"]
                except:
                    pass
        return ""

    def sway_get_outputs(self):
        response = self.sway_ipc(payload_type = GET_OUTPUTS)
        j = json.loads(response)
        return j

    def get_output_stats(self, model):
        for m in self.sway_get_outputs():
            if m["model"] == model:
                return m["active"]
        raise Exception("model not found")

    def set_output_stats(self, output, stats):
        if stats is True:
            cmd = 'output "{}" enable'.format(output).encode("utf-8")
        else:
            cmd = 'output "{}" disable'.format(output).encode("utf-8")
        response = self.sway_ipc(payload_type=RUN_COMMAND, payload=cmd)
        j = json.loads(response)
        return j

    def toggle_output(self, model, output):
        if self.get_output_stats(model):
            self.set_output_stats(output, False)
        else:
            self.set_output_stats(output, True)

    def sway_get_tree(self):
        GET_TREE = 4
        SWAY_SOCKET = self.socket
        try:
            MSG_MAGIC = b"i3-ipc"
            MSG_PAYLOAD_TYPE = struct.pack("i", GET_TREE)
            MSG_PAYLOAD = b""
            MSG_PAYLOAD_LENGTH = struct.pack("i", len(MSG_PAYLOAD))

            message = MSG_MAGIC + MSG_PAYLOAD_LENGTH + MSG_PAYLOAD_TYPE + MSG_PAYLOAD

            client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            client.connect(SWAY_SOCKET)
            client.send(message)
            _sway_ipc_header = client.recv(len(MSG_MAGIC) + 4 + len(MSG_PAYLOAD_TYPE))
            output = client.recv(1024 * 512)
            client.close()
            output = output.decode("utf-8")
            return output
        except Exception as e:
            print("err: {}".format(e.__str__()))

    def sway_set_bg(self, wallpaper):
        RUN_COMMAND = 0
        MSG_TYPE = RUN_COMMAND
        SWAY_SOCKET = self.socket
        try:
            command = "output \"*\" bg {} fill".format(wallpaper)
            MSG_MAGIC = b"i3-ipc"
            MSG_PAYLOAD_TYPE = struct.pack("i", MSG_TYPE)
            MSG_PAYLOAD = command.encode("utf-8")
            MSG_PAYLOAD_LENGTH = struct.pack("i", len(MSG_PAYLOAD))

            message = MSG_MAGIC + MSG_PAYLOAD_LENGTH + MSG_PAYLOAD_TYPE + MSG_PAYLOAD

            client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            client.connect(SWAY_SOCKET)
            client.send(message)
            _sway_ipc_header = client.recv(len(MSG_MAGIC) + 4 + len(MSG_PAYLOAD_TYPE))
            output = client.recv(1024 * 512)
            client.close()
            output = output.decode("utf-8")
            return output
        except Exception as e:
            print("err: {}".format(e.__str__()))

    def sway_ipc(self, payload_type, payload=b""):
        SWAY_SOCKET = self.sway_get_socketpath()
        # print(SWAY_SOCKET)
        try:
            MSG_MAGIC = b"i3-ipc"
            MSG_PAYLOAD_TYPE = struct.pack("i", payload_type)
            MSG_PAYLOAD = payload
            MSG_PAYLOAD_LENGTH = struct.pack("i", len(MSG_PAYLOAD))

            message = MSG_MAGIC + MSG_PAYLOAD_LENGTH + MSG_PAYLOAD_TYPE + MSG_PAYLOAD

            client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            client.connect(SWAY_SOCKET)
            client.send(message)
            _sway_ipc_header = client.recv(len(MSG_MAGIC) + 4 + len(MSG_PAYLOAD_TYPE))
            output = client.recv(1024 * 512)
            client.close()
            output = output.decode("utf-8")
            return output
        except Exception as e:
            print("err: {}".format(e.__str__()))