#!/usr/bin/python

import os
import gi
gi.require_version('Secret', '1')
from gi.repository import Secret
import socket

def get_xdg_runtime_dir():
    return "/run/user/1000"

SOCKET_OTP_UINPUT = os.path.join(get_xdg_runtime_dir(), "otp-uinput")

GENOTP_SCHEMA = Secret.Schema.new("org.mock.type.Store.genotp",
    Secret.SchemaFlags.NONE,
    {
        "scheme": Secret.SchemaAttributeType.STRING,
        "name": Secret.SchemaAttributeType.STRING,
    }
)

def on_password_stored(source, result, unused):
    Secret.password_store_finish(result)
    # ... do something now that the password has been stored

def secret_password_store(attributes, label, password):
    Secret.password_store_sync(GENOTP_SCHEMA, attributes, Secret.COLLECTION_DEFAULT,
                        label, password, None)

def secret_password_lookup(attributes):
    return Secret.password_lookup_sync(GENOTP_SCHEMA, attributes, None)

def __keyin_uinput(k):
    k = "aaaa\r\n{}".format(k)
    client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    client.connect(SOCKET_OTP_UINPUT)
    client.send(k.encode('utf-8'))
    client.close()

def keyin_uinput_otp(otp):
    for k in otp:
        __keyin_uinput(k)
