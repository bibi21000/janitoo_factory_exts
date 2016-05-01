# -*- coding: utf-8 -*-

"""Unittests for Janitoo-common.
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

import warnings
warnings.filterwarnings("ignore")

import sys, os
import time
import unittest
import threading
import logging
from pkg_resources import iter_entry_points
import mock
import ConfigParser
from ConfigParser import RawConfigParser

sys.path.insert(0,os.path.dirname(__name__))

from janitoo_nosetests import JNTTBase
from janitoo_nosetests.values import JNTTFactory, JNTTFactoryCommon, JNTTFactoryPollCommon, JNTTFactoryConfigCommon

from janitoo.runner import Runner, jnt_parse_args
from janitoo.server import JNTServer
from janitoo.options import JNTOptions

class TestBlinkValue(JNTTFactory, JNTTFactoryPollCommon):
    """Test the value factory
    """
    entry_name='blink'
    led = None

    def blink_off_cb(self, node_uuid=None, index=None):
        self.led = False

    def blink_on_cb(self, node_uuid=None, index=None):
        self.led = True

    def test_011_value_entry_poll(self, **kwargs):
        JNTTFactoryPollCommon.test_011_value_entry_poll(self, blink_off_cb=self.blink_off_cb, blink_on_cb=self.blink_on_cb)

    def test_101_value_entry_poll(self):
        self.led = None
        node_uuid='test_node'
        main_value = self.get_main_value(
            node_uuid=node_uuid,
            blink_off_cb=self.blink_off_cb,
            blink_on_cb=self.blink_on_cb
        )
        self.assertFalse(main_value.is_writeonly)
        print main_value
        poll_value = main_value.create_poll_value()
        print poll_value
        main_value._set_poll(node_uuid, 0, 0)
        self.assertEqual(0, main_value._get_poll(node_uuid, 0))
        main_value._set_poll(node_uuid, 0, 5)
        self.assertEqual(5, main_value._get_poll(node_uuid, 0))
        self.assertEqual(5, main_value.poll_delay)
        self.assertEqual(True, main_value.is_polled)
        main_value._set_poll(node_uuid, 0, 0)
        self.assertEqual(0, main_value._get_poll(node_uuid, 0))
        self.assertEqual(0, main_value.poll_delay)
        self.assertEqual(False, main_value.is_polled)

    def test_110_blink(self):
        self.led = None
        node_uuid='test_node'
        main_value = self.get_main_value(
            node_uuid=node_uuid,
            blink_off_cb=self.blink_off_cb,
            blink_on_cb=self.blink_on_cb,
            blink_on_delay=2,
            blink_off_delay=2,
        )
        try:
            main_value.set_blink(node_uuid=node_uuid, data='blink')
            self.assertNotEqual(main_value.timer, None)
            self.assertEqual(main_value.data, 'blink')
            time.sleep(1)
            self.assertEqual(self.led, True)
            time.sleep(2)
            self.assertEqual(self.led, False)
            time.sleep(2)
            self.assertEqual(self.led, True)
            main_value.set_blink(node_uuid=node_uuid, data='off')
            self.assertEqual(main_value.timer, None)
            self.assertEqual(main_value.data, 'off')
            self.assertEqual(self.led, False)
        finally:
            main_value.stop()
            #~ pass

class TestIpPing(JNTTFactory, JNTTFactoryConfigCommon, JNTTFactoryPollCommon):
    """Test the value factory
    """
    entry_name='ip_ping'

    def test_100_value_entry_config(self):
        node_uuid='test_node'
        main_value = self.get_main_value(node_uuid=node_uuid)
        print main_value
        config_value = main_value.create_config_value()
        print config_value
        main_value.set_config(node_uuid, 0, '127.0.0.1')
        self.assertEqual('127.0.0.1', main_value.get_config(node_uuid, 0))
        self.assertTrue(main_value.ping_ip(node_uuid, 0))
        main_value.set_config(node_uuid, 0, '192.168.24.5')
        self.assertEqual('192.168.24.5', main_value.get_config(node_uuid, 0))
        self.assertFalse(main_value.ping_ip(node_uuid, 0))

