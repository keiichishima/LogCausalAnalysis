#!/usr/bin/env python
# coding: utf-8

import sys
import os
import datetime
import logging
import collections
import ConfigParser

DEFAULT_CONFIG_NAME = "/".join((os.path.dirname(__file__),
        "config.conf.sample"))

class ExtendedConfigParser(ConfigParser.SafeConfigParser):

    def __init__(self, noopterror=True, defaults=None,
            dict_type=collections.OrderedDict, allow_no_value=False):
        self._conf = ConfigParser.SafeConfigParser(defaults = defaults,
                dict_type = dict_type, allow_no_value = allow_no_value)
        self._noopt = noopterror

    def _no_option(self, err = None):
        if self._noopt:
            raise err
        else:
            return None

    def _call_method(self, method_name, section, name):
        method = getattr(self._conf, method_name)
        try:
            ret = method(section, name)
        except ConfigParser.NoOptionError as err:
            return self._no_option(err)
        except ValueError as err:
            return self._no_option(err)
        else:
            return ret

    def set(self, section, name, value):
        return getattr(self._conf, sys._getframe().f_code.co_name)(
                section, name, value)

    def read(self, fn):
        if not os.path.exists(fn):
            raise IOError("{0} not found".format(fn))
        else:
            return self._conf.read(fn)

    def write(self, fn):
        return self._conf.write(fn)

    def sections(self):
        return getattr(self._conf, sys._getframe().f_code.co_name)()

    def options(self, section):
        return getattr(self._conf, sys._getframe().f_code.co_name)(section)

    def get(self, section, name):
        return self._call_method(sys._getframe().f_code.co_name, section, name)

    def getint(self, section, name):
        return self._call_method(sys._getframe().f_code.co_name, section, name)

    def getfloat(self, section, name):
        return self._call_method(sys._getframe().f_code.co_name, section, name)

    def getboolean(self, section, name):
        return self._call_method(sys._getframe().f_code.co_name, section, name)

    def gettuple(self, section, name):
        try:
            ret = self._conf.get(section, name)
        except ConfigParser.NoOptionError as err:
            return self._no_option(err)
        else:
            return tuple(e.strip() for e in ret.split(",")
                    if not e.strip() == "")

    def getlist(self, section, name):
        try:
            ret = self._conf.get(section, name)
        except ConfigParser.NoOptionError as err:
            return self._no_option(err)
        else:
            if ret == "":
                return self._no_option()
            else:
                return [e.strip() for e in ret.split(",")
                        if not e.strip() == ""]

    def getdt(self, section, name):
        try:
            ret = self._conf.get(section, name)
        except ConfigParser.NoOptionError as err:
            return self._no_option(err)
        else:
            if ret == "":
                return self._no_option()
            else:
                return datetime.datetime.strptime(ret.strip(),
                        "%Y-%m-%d %H:%M:%S")

    def getterm(self, section, name):
        try:
            ret = self._conf.get(section, name)
        except ConfigParser.NoOptionError as err:
            return self._no_option(err)
        else:
            if ret == "":
                return self._no_option()
            else:
                return tuple(datetime.datetime.strptime(e.strip(),
                        "%Y-%m-%d %H:%M:%S") for e in ret.split(","))

    def getdur(self, section, name):
        try:
            ret = self._conf.get(section, name)
        except ConfigParser.NoOptionError as err:
            return self._no_option(err)
        else:
            if ret == "":
                return self._no_option()
            else:
                return str2dur(ret)


class GroupDef():

    """
    Define grouping by external text
    Rules:
        description after # in a line will be recognized as comment
        line "[GROUP_NAME]" will change group to set
        other lines add elements in group set with GROUP_NAME line
    """

    def __init__(self, fn, default_val = None):
        self.gdict = {}
        self.rgdict = {}
        self.default = default_val
        if fn is None or fn == "":
            pass
        else:
            self.open_def(fn)

    def open_def(self, fn):
        group = None
        with open(fn, 'r') as f:
            for line in f:
                # ignore after comment sygnal
                line = line.strip().partition("#")[0]
                if line == "":
                    continue
                elif line[0] == "#":
                    continue
                elif line[0] == "[" and line[-1] == "]":
                    group = line[1:].strip("[]")
                else:
                    if group is None:
                        raise ValueError("no group definition before value")
                    val = line 
                    self.gdict.setdefault(group, []).append(val)
                    self.rgdict.setdefault(val, []).append(group)

    def setdefault(self, group):
        self.default = group

    def groups(self):
        return self.gdict.keys()

    def values(self):
        return self.rgdict.keys()

    def ingroup(self, group, val):
        if self.rgdict(val):
            return val in self.rgdict[val]
        else:
            return False

    def get_group(self, val):
        if self.rgdict.has_key(val):
            return self.rgdict[val]
        else:
            return []

    def get_value(self, group):
        if self.gdict.has_key(group):
            return self.gdict[group]
        else:
            return []

    def iter_def(self):
        for group, l_val in self.gdict.iteritems():
            for val in l_val:
                yield group, val


def str2dur(string):
    if "s" in string:
        num = int(string.partition("s")[0])
        return datetime.timedelta(seconds = num)
    elif "m" in string:
        num = int(string.partition("m")[0])
        return datetime.timedelta(minutes = num)
    elif "h" in string:
        num = int(string.partition("h")[0])
        return datetime.timedelta(hours = num)
    elif "d" in string:
        num = int(string.partition("d")[0])
        return datetime.timedelta(days = num)
    else:
        raise ValueError("Duration string invalid")


## singleton config instance, to be shared in whole system
#_fn = DEFAULT_CONFIG_NAME
#if os.path.exists(_fn):
#    _config = ExtendedConfigParser(noopterror = False)
#    _config.read(_fn)
#
#def common_config():
#    if os.path.exists(_fn):
#        return _config
#    else:
#        raise IOError("common configuration file {0} not found".format(_fn))

def open_config(fn, noopterror = False):
    conf = ExtendedConfigParser(noopterror = noopterror)
    conf.read(fn)
    return conf


# common objects for logging
def set_common_logging(conf, logger = None, l_logger_name = None):
    fn = conf.get("general", "info_log")
    fmt = logging.Formatter(
            fmt = "%(asctime)s %(levelname)s (%(threadName)s) %(message)s",
            datefmt = "%Y-%m-%d %H:%M:%S")
    lv = logging.INFO
    if fn is None:
        ch = logging.StreamHandler()
    else:
        ch = logging.FileHandler(fn)
    ch.setFormatter(fmt)
    ch.setLevel(lv)
    if logger is not None:
        logger.setLevel(lv)
        logger.addHandler(ch)
    if l_logger_name is not None:
        for ln in l_logger_name:
            temp = logging.getLogger(ln)
            temp.setLevel(lv)
            temp.addHandler(ch)
    return ch


def release_common_logging(ch, logger = None, l_logger_name = None):
    if logger is not None:
        logger.removeHandler(ch)
    if l_logger_name is not None:
        for ln in l_logger_name:
            temp = logging.getLogger(ln)
            temp.removeHandler(ch)


def overwrite_config(conf_fn1, conf_fn2, output):
    conf1 = open_config(conf_fn1) # conf1 as basis
    conf2 = open_config(conf_fn2) # overwrite with conf2
    for section in conf2.sections():
        if section in conf1.sections():
            for option in conf2.options(section):
                value = conf2.get(section, option)
                if option in conf1.options(section):
                    conf1.set(section, option, value)
    with open(output, 'w') as f:
        conf1.write(f)


if __name__ == "__main__":
    # import old config, merge it with new default config, and output
    if len(sys.argv) < 3:
        sys.exit("usage : {0} config output".format(sys.argv[0]))
    default_conf = DEFAULT_CONFIG_NAME
    conf = sys.argv[1]
    output = sys.argv[2]
    overwrite_config(default_conf, conf, output) 

