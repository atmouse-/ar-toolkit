#!/usr/bin/python

import os
import configparser
import string
from collections import OrderedDict
from os import linesep

class IniSettings:
    def __init__(self, filename, case_sensitive=1):
        self.filename = os.path.abspath(filename)
        if not os.path.isfile(filename):
            raise Exception("file not found")
        self.case_sensitive = case_sensitive
        self.settings = self.__loadConfig()

    def __loadConfig(self):
        config = OrderedDict()
        cp = configparser.SafeConfigParser()
        if self.case_sensitive:
            # case-sensitive
            cp.optionxform = str
        else:
            pass
        cp.read(self.filename)
        for name in cp.sections():
            settings = OrderedDict()
            for opt in cp.options(name):
                settings[opt] = cp.get(name, opt).strip()
            config[name] = settings
        return config

    def reload(self):
        self.__loadConfig()

    def save(self):
        inifile = open(self.filename, 'wb')
        for group in self.settings.keys():
            inifile.write("".join([linesep, "[", group, "]", linesep]).encode("utf-8"))
            for key in self.settings[group].keys():
                inifile.write("".join([key, "=", self.settings[group][key], linesep]).encode("utf-8"))

    def set(self, group, key, value):
        if self.case_sensitive:
            pass
        else:
            key = key.lower()
        if not group in self.settings:
            self.settings[group] = {}
        self.settings[group][key] = value
        return True

    def get(self, group, key):
        if self.case_sensitive:
            pass
        else:
            key = key.lower()
        if not group in self.settings:
            return None
        return self.settings[group][key]

    def pop(self, group, key=''):
        assert group
        if not group in self.settings:
            return True
        if key:
            if not key in self.settings[group]:
                return True
            self.settings[group].pop(key)
        else:
            self.settings.pop(group)
        return True

    def set_dict(self, dict):
        for group in dict.keys():
            for key in dict[group].keys():
                self.settings[group][key] = dict[group][key]

class OguriConfig:
    def __init__(self):
        self.CONF_PATH = os.path.join(
            os.path.expanduser("~"),
            ".config/oguri/config",
            )
        self.conf = IniSettings(self.CONF_PATH, case_sensitive=1)

    def get_output_image(self, output):
        return self.conf.get("output {}".format(output), "image")

    def set_output_image(self, output, imagepath):
        self.conf.set("output {}".format(output), "image", imagepath)
        self.conf.save()
