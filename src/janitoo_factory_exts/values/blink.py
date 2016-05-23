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

def make_blink(**kwargs):
    return JNTValueBlink(**kwargs)

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
                except Exception:
                    delay = 0
                    logger.exception('[%s] - Exception when timer_change', self.__class__.__name__)
                if delay > 0:
                    self.timer = threading.Timer(delay, self.timer_change, args=(False,))
                    self.timer.start()
            else:
                self.blink_off_cb(node_uuid=self.node_uuid)
                try:
                    delay = self.delays[self._data]['on']
                except Exception:
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
