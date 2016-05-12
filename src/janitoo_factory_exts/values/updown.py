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
COMMAND_UPDOWN = 0x3204

assert(COMMAND_DESC[COMMAND_UPDOWN] == 'COMMAND_UPDOWN')
assert(COMMAND_DESC[COMMAND_BLINK] == 'COMMAND_BLINK')
assert(COMMAND_DESC[COMMAND_BASIC] == 'COMMAND_BASIC')
assert(COMMAND_DESC[COMMAND_CONFIGURATION] == 'COMMAND_CONFIGURATION')
assert(COMMAND_DESC[COMMAND_SENSOR_BINARY] == 'COMMAND_SENSOR_BINARY')
assert(COMMAND_DESC[COMMAND_SENSOR_MULTILEVEL] == 'COMMAND_SENSOR_MULTILEVEL')
##############################################################

def make_updown(**kwargs):
    return JNTValueUpDown(**kwargs)

class JNTValueUpDown(JNTValueFactoryEntry):
    """
    """
    def __init__(self, entry_name="updown", **kwargs):
        self.updown_up_cb = kwargs.pop('updown_up_cb', None)
        self.updown_down_cb = kwargs.pop('updown_down_cb', None)
        self.updown_value_cb = kwargs.pop('updown_value_cb', None)
        if self.updown_up_cb is None or self.updown_down_cb is None:
            raise RuntimeError("You must define updown_up_cb and updown_down_cb parameters")
        help = kwargs.pop('help', 'Up/Down')
        default = kwargs.pop('default', 0)
        label = kwargs.pop('label', 'Up/Down')
        index = kwargs.pop('index', 0)
        list_items = kwargs.pop('list_items', ['up', 'down', '#val'])
        cmd_class = kwargs.pop('cmd_class', COMMAND_UPDOWN)
        JNTValueFactoryEntry.__init__(self, entry_name=entry_name, help=help, label=label,
            set_data_cb=self.set_updown,
            index=index, cmd_class=cmd_class,
            default=default,
            genre=0x01, type=0x05,
            is_writeonly=False, is_readonly=False, **kwargs)

    def create_poll_value(self, **kwargs):
        """
        """
        default = kwargs.pop('default', 300)
        return self._create_poll_value(default=default, **kwargs)

    def set_updown(self, node_uuid=None, index=None, data = None):
        """
        """
        if self._data is None:
            self._data = self.default
        if data == 'up':
            self._data += 1
            self.updown_up_cb(node_uuid=node_uuid, index=index)
        elif data == 'down':
            self._data -= 1
            self.updown_down_cb(node_uuid=node_uuid, index=index)
        elif self.updown_value_cb is not None:
            self.updown_value_cb(node_uuid=node_uuid, index=index, data = data)
            self._data = int(data)
        else:
            logger.warning('[%s] - set_blink invalid data %s', self.__class__.__name__, data)
