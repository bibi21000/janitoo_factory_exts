# -*- coding: utf-8 -*-
"""The value

"""

__license__ = """
    This file is part of Janitoo.

    Janitoo is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Janitoo is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Janitoo. If not, see <http://www.gnu.org/licenses/>.

"""
__author__ = 'Sébastien GALLET aka bibi21000'
__email__ = 'bibi21000@gmail.com'
__copyright__ = "Copyright © 2013-2014-2015-2016 Sébastien GALLET aka bibi21000"

# Set default logging handler to avoid "No handler found" warnings.
import os
import threading
import logging
logger = logging.getLogger(__name__)

from janitoo.classes import GENRE_DESC, VALUE_DESC
from janitoo.utils import json_dumps
from janitoo.value import JNTValue
from janitoo.value_factory import JNTValueFactoryEntry
from janitoo_factory.values.config import JNTValueConfigString

##############################################################
#Check that we are in sync with the official command classes
#Must be implemented for non-regression
from janitoo.classes import COMMAND_DESC

COMMAND_CONFIGURATION = 0x0070
COMMAND_SENSOR_BINARY = 0x0030
COMMAND_SENSOR_MULTILEVEL = 0x0031
COMMAND_BASIC = 0x0020
COMMAND_BLINK = 0x3203

assert(COMMAND_DESC[COMMAND_BLINK] == 'COMMAND_BLINK')
assert(COMMAND_DESC[COMMAND_BASIC] == 'COMMAND_BASIC')
assert(COMMAND_DESC[COMMAND_CONFIGURATION] == 'COMMAND_CONFIGURATION')
assert(COMMAND_DESC[COMMAND_SENSOR_BINARY] == 'COMMAND_SENSOR_BINARY')
assert(COMMAND_DESC[COMMAND_SENSOR_MULTILEVEL] == 'COMMAND_SENSOR_MULTILEVEL')
##############################################################

def make_ip_ping(**kwargs):
    return JNTValueIpPing(**kwargs)

def make_value_rread(**kwargs):
    return JNTValueRRead(**kwargs)

def make_value_rwrite(**kwargs):
    return JNTValueRWrite(**kwargs)

def make_blink(**kwargs):
    return JNTValueBlink(**kwargs)

class JNTValueIpPing(JNTValueFactoryEntry):
    """
    """
    def __init__(self, entry_name="ip_ping", **kwargs):
        help = kwargs.pop('help', 'Ping an IP address')
        label = kwargs.pop('label', 'Ping')
        get_data_cb = kwargs.pop('get_data_cb', self.ping_ip)
        index = kwargs.pop('index', 0)
        cmd_class = kwargs.pop('cmd_class', COMMAND_SENSOR_BINARY)
        JNTValueFactoryEntry.__init__(self, entry_name=entry_name, help=help, label=label,
            get_data_cb=get_data_cb, set_data_cb=None,
            index=index, cmd_class=cmd_class, genre=0x02, type=0x01, is_writeonly=False, is_readonly=True, **kwargs)

    def create_config_value(self, **kwargs):
        """
        """
        help = kwargs.pop('help', 'The IP to ping')
        return self._create_config_value(type=0x21, help=help)

    def create_poll_value(self, **kwargs):
        """
        """
        default = kwargs.pop('default', 30)
        return self._create_poll_value(default=default, **kwargs)

    def ping_ip(self, node_uuid=None, index=None):
        """
        """
        try:
            if node_uuid is None:
                node_uuid = self.node_uuid
            if index is None:
                index = self.index
            if index not in self.instances or self.instances[index]['config'] is None:
                logger.warning('[%s] - Pinging an unknown instance %s on node %s', self.__class__.__name__, index, node_uuid)
                return False
            if os.system('ping -c 2 -w 2 ' + self.instances[index]['config'] + '> /dev/null 2>&1'):
                self.instances[index]['data'] = False
                return False
            self.instances[index]['data'] = True
            return True
        except :
            logger.exception('[%s] - Exception when pinging (%s)', self.__class__.__name__, self.instances[index]['config'])
            return False

class JNTValueRRead(JNTValueConfigString):
    """Should be extend to a SensorString + config (as value_factory) to avoid use of get cache, ...
    """
    def __init__(self, entry_name="rread_value", **kwargs):
        help = kwargs.pop('help', 'A read value located on a remote node')
        label = kwargs.pop('label', 'Remote')
        #We will update
        JNTValueConfigString.__init__(self, entry_name=entry_name, help=help, label=label, **kwargs)
        self._cache = {}

    def get_cache(self, node_uuid=None, index=None):
        """
        """
        if index is None:
            index = self.index
        if index in self._cache:
            return self._cache[index]
        return None

    def set_cache(self, node_uuid=None, index=None, data = None):
        """
        """
        if index is None:
            index = self.index
        self._cache[index] = data

    def get_value_config(self, node_uuid=None, index=None):
        """
        conf = switch|0
        """
        try:
            if node_uuid is None:
                node_uuid = self.node_uuid
            if index is None:
                index = self.index
            data = self._get_data(node_uuid, index)
            #~ print data
            if data is None:
                return None
            data = data.split('|')
            #~ print ' length', len(data)
            if len(data) == 1:
                return [ data[0], '0' ]
            if len(data) > 2:
                return None
            return data
        except :
            logger.exception('[%s] - Exception when reading (%s)', self.__class__.__name__, self.instances[index]['data'])
            return None

class JNTValueRWrite(JNTValueConfigString):
    """Should be extend to a SensorString + config (as value_factory) to avoid use of get cache, ...
    """
    def __init__(self, entry_name="rwrite_value", **kwargs):
        help = kwargs.pop('help', 'A write value located on a remote node')
        label = kwargs.pop('label', 'Rwrite')
        #We will update
        JNTValueConfigString.__init__(self, entry_name=entry_name, help=help, label=label, **kwargs)
        self._cache = {}

    def get_cache(self, node_uuid=None, index=None):
        """
        """
        if index is None:
            index = self.index
        if index in self._cache:
            return self._cache[index]
        return None

    def set_cache(self, node_uuid=None, index=None, data = None):
        """
        """
        if index is None:
            index = self.index
        self._cache[index] = data

    def get_value_config(self, node_uuid=None, index=None):
        """
        conf = switch|0|0x0025|1|0
        """
        try:
            if node_uuid is None:
                node_uuid = self.node_uuid
            #~ print "node_uuid ", node_uuid
            if index is None:
                index = self.index
            #~ print "index ", index
            data = self._get_data(node_uuid, index)
            #~ print "data ", data
            if data is None:
                return None
            data = data.split('|')
            #~ print ' length', len(data)
            if len(data) != 5:
                return None
            return data
        except :
            logger.exception('[%s] - Exception when reading (%s)', self.__class__.__name__, self.instances[index]['data'])
            return None

class JNTValueBlink(JNTValueFactoryEntry):
    """
    """
    def __init__(self, entry_name="blink", **kwargs):
        self.blink_on_cb = kwargs.pop('blink_on_cb', None)
        self.blink_off_cb = kwargs.pop('blink_off_cb', None)
        self.delays = {
            'off' : {
                'on' : kwargs.pop('off_on_delay', 0),
                'off' : kwargs.pop('off_off_delay', 1),
            },
            'blink' : {
                'on' : kwargs.pop('blink_on_delay', 0.6),
                'off' : kwargs.pop('blink_off_delay', 2.5),
            },
            'heartbeat' : {
                'on' : kwargs.pop('heartbeat_on_delay', 0.5),
                'off' : kwargs.pop('heartbeat_off_delay', 300),
            },
            'info' : {
                'on' : kwargs.pop('notify_on_delay', 0.6),
                'off' : kwargs.pop('notify_off_delay', 60),
            },
            'notify' : {
                'on' : kwargs.pop('notify_on_delay', 0.6),
                'off' : kwargs.pop('notify_off_delay', 10),
            },
            'warning' : {
                'on' : kwargs.pop('warning_on_delay', 0.6),
                'off' : kwargs.pop('warning_off_delay', 5),
            },
            'alert' : {
                'on' : kwargs.pop('alert_on_delay', 0.6),
                'off' : kwargs.pop('alert_off_delay', 1),
            },
        }
        self.timer = None
        self.timer_lock = None
        if self.blink_on_cb is None or self.blink_off_cb is None:
            raise RuntimeError("You must define blink_off_cb and blink_on_cb parameters")
        help = kwargs.pop('help', 'Blink')
        default = kwargs.pop('default', 'off')
        label = kwargs.pop('label', 'Blink')
        index = kwargs.pop('index', 0)
        list_items = kwargs.pop('list_items', ['off', 'blink', 'heartbeat', 'info', 'notify', 'warning', 'alert'])
        cmd_class = kwargs.pop('cmd_class', COMMAND_BLINK)
        JNTValueFactoryEntry.__init__(self, entry_name=entry_name, help=help, label=label,
            get_data_cb=self.get_blink, set_data_cb=self.set_blink,
            index=index, cmd_class=cmd_class,
            default=default,
            genre=0x01, type=0x05,
            is_writeonly=False, is_readonly=False, **kwargs)

    def start(self):
        """Start the value
        """
        self.start_blinking()

    def stop(self):
        """Start the value
        """
        if self.timer_lock is not None:
            self.stop_blinking()

    def create_poll_value(self, **kwargs):
        """
        """
        default = kwargs.pop('default', 300)
        return self._create_poll_value(default=default, **kwargs)

    def start_blinking(self, **kwargs):
        """
        """
        self.timer_lock = threading.Lock()
        self.timer_lock.acquire()
        try:
            if self.timer is not None:
                self.timer.cancel()
                self.timer = None
            self.timer = threading.Timer(0.1, self.timer_change, args=(True,))
            self.timer.start()
        finally:
            self.timer_lock.release()

    def timer_change(self, status):
        """
        """
        if self.timer_lock is None:
            return
        self.timer_lock.acquire()
        try:
            if self.timer is not None:
                self.timer.cancel()
                self.timer = None
            if status:
                self.blink_on_cb(node_uuid=self.node_uuid)
                try:
                    delay = self.delays[self._data]['off']
                except:
                    delay = 0
                    logger.exception('[%s] - Exception when timer_change', self.__class__.__name__)
                if delay > 0:
                    self.timer = threading.Timer(delay, self.timer_change, args=(False,))
                    self.timer.start()
            else:
                self.blink_off_cb(node_uuid=self.node_uuid)
                try:
                    delay = self.delays[self._data]['on']
                except:
                    delay = 0
                    logger.exception('[%s] - Exception when timer_change', self.__class__.__name__)
                if delay > 0:
                    self.timer = threading.Timer(delay, self.timer_change, args=(True,))
                    self.timer.start()
        finally:
            self.timer_lock.release()

    def stop_blinking(self, **kwargs):
        """
        """
        #~ print 'locking', self.timer_lock.acquire(False)
        self.timer_lock.acquire()
        try:
            if self.timer is not None:
                self.timer.cancel()
                self.timer = None
            self._data = 'off'
            self.blink_off_cb(node_uuid=self.node_uuid)
        finally:
            self.timer_lock.release()
        self.timer_lock = None

    def get_blink(self, node_uuid=None, index=None):
        """
        """
        return self._data

    def set_blink(self, node_uuid=None, index=None, data = None):
        """
        """
        if data == 'off':
            self._data = data
            self.stop_blinking(node_uuid=node_uuid, index=index, data = data)
        elif data in ['blink', 'heartbeat', 'notify', 'info', 'warning', 'alert']:
            self._data = data
            self.start_blinking(node_uuid=node_uuid, index=index, data = data)
        else:
            logger.warning('[%s] - set_blink invalid data %s', self.__class__.__name__, data)
