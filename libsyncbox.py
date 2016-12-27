#-*- coding:utf-8 -*-

"""
This file is part of OpenSesame.

OpenSesame is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

OpenSesame is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with OpenSesame.  If not, see <http://www.gnu.org/licenses/>.
"""

from libopensesame.py3compat import *
from libopensesame.exceptions import osexception
from libopensesame import debug
from time import sleep

import serial
import os

class libsyncbox(object):

	"""
	desc: |
		If you insert the syncbox plugin at the start of your experiment, an
		instance of SYNCBOX automatically becomes part of the experiment
		object and can be accessed within an inline_script item as SYNCBOX.

		__Important note 1:__

		If you do not specify a device, the plug-in will try to autodetect the
		SynBox port. However, on some systems this freezes the experiment, so
		it is better to explicitly specify a device.

		__Important note 2:__

		You need to call [syncbox.start] to put the SyncBox in sending mode,
		before calling [syncbox.get_button_press] to collect a button press.

		__Example:__

		~~~ .python
		t0 = clock.time()
		syncbox.start()
		button, t1 = syncbox.get_button_press(allowed_buttons=[1,2],
			require_state_change=True)
		if button == 1:
			response_time = t1 - t0
			print('Button 1 was pressed in %d ms!' % response_time)
		syncbox.stop()
		~~~

		[TOC]
	"""

	# The PST sr box only supports five buttons, but some of the VU boxes use
	# higher button numbers
	BUTTON1 = int('11111110', 2)
	BUTTON2 = int('11111101', 2)
	BUTTON3 = int('11111011', 2)
	BUTTON4 = int('11110111', 2)
	BUTTON5 = int('11101111', 2)
	BUTTON6 = int('11011111', 2)
	BUTTON7 = int('10111111', 2)
	BUTTON8 = int('01111111', 2)
	BYTEMASKS = [BUTTON1, BUTTON2, BUTTON3, BUTTON4, BUTTON5, BUTTON6, BUTTON7,
		BUTTON8]

	def __init__(self, experiment, dev=None):

		"""
		desc:
			Constructor. An SYNCBOX object is created automatically by the
			SYNCBOX plug-in, and you do not generally need to call the
			constructor yourself.

		arguments:
			experiment:
				desc:	An Opensesame experiment.
				type:	experiment

		keywowrds:
			dev:
				desc:	The syncbox device port or `None` for auto-detect.
				type:	[str, unicode, NoneType]
		"""

		self.experiment = experiment
		self._syncbox = None
		self._started = False
		self._baudrate = 57600
		self._syncboxResponse = None

		# If a device has been specified, use it
		# 57600 is the baudrate for the NNL SyncBox
		if dev not in (None, "", "autodetect"):
			try:
				self._syncbox = serial.Serial(dev, timeout=0, baudrate=self._baudrate)
			except Exception as e:
				raise osexception(
					"Failed to open device port '%s' in libsyncbox: '%s'" \
					% (dev, e))

		else:
			# Else determine the common name of the serial devices on the
			# platform and find the first accessible device. On Windows,
			# devices are labeled COM[X], on Linux there are labeled /dev/tty[X]
			if os.name == "nt":
				for i in range(1, 256):
					try:
						dev = "COM%d" % i
						self._syncbox = serial.Serial(dev, timeout=0,
							baudrate=self._baudrate)
						break
					except Exception as e:
						self._syncbox = None
						pass

			elif os.name == "posix":
				for path in os.listdir("/dev"):
					if path[:3] == "tty":
						try:
							dev = "/dev/%s" % path
							self._syncbox = serial.Serial(dev, timeout=0,
								baudrate=self._baudrate)
							break
						except Exception as e:
							self._syncbox = None
							pass
			else:
				raise osexception(
					"libsyncbox does not know how to auto-detect the SyncBox on your platform. Please specify a device.")

		if self._syncbox is None:
			raise osexception(
				"libsyncbox failed to auto-detect an SyncBox. Please specify a device.")
		debug.msg("using device %s" % dev)
		# Turn off all lights
	#	if self._syncbox is not None:
	#		self._syncbox.write(b'\x60')

#	def send(self, ch):
#
#		"""
#		desc:
#			Sends a single character to the SynBox.
#			Send '\x60' to turn off all lights, '\x61' for light 1 on, '\x62' for light 2 on,'\x63' for lights 1 and 2 on etc.
#
#		arguments:
#			ch:
#				desc:	The character to send.
#				type:	str
#		"""
#
#		self._syncbox.write(ch)

	def start(self):

		"""
		desc:
			Turns on sending mode, so that the SyncBox starts to send output.
			The SyncBox may be needed to be set in sending mode when you call
			[syncbox.get_button_press].
		"""

		if self._started:
			return
		# Write the start byte
		self._syncbox.flushOutput()
		self._syncbox.flushInput()
	#	self._syncbox.write(b'\xA0')
		self._started = True

	def stop(self):

		"""
		desc:
			Turns off sending mode, so that the SyncBox stops giving output.
		"""

		if not self._started:
			return
		# Write the stop byte and flush the input
		self._syncbox.flushOutput()
		self._syncbox.flushInput()
#		self._syncbox.write(b'\x20')
		self._started = False


	def get_button_press(self, SbResponse, timeout=None):
		#	def get_button_press(self, allowed_buttons=None, timeout=None,
		#		require_state_change=False):

		"""
		desc: |
			Waits for sync trigger, comming on the serial port from the MRI scanner or hardware trigger box.

		keywords:
			SbResponse:
				desc:	An expected symbol from the sync box.
				type:	[char, byte]
			timeout:
				desc:	A timeout value in milliseconds or `None` for no
						timeout.
				type:	[int, float, NoneType]

		returns:
			desc:	A respone char, timestamp tuple.
			type:	tuple
		"""

		self._syncboxResponse = SbResponse

		if not self._started:
			raise osexception(
				u'Please call syncbox.start() before syncbox.get_button_press()')
#		t0 = self.experiment.time()

		inputbyte0 = None
		inputchar = b''

		while inputchar != self._syncboxResponse:
			inputchar = self._syncbox.read(1).decode('UTF-8')
		#	print("[{}]: expected <{}>, got <{}>".format(self.experiment.time(), self._syncboxResponse, inputchar))

		t1 = self.experiment.time()
	#	print("[{}]: \t got <{}>".format(t1, inputchar))
		return inputchar, t1


	def close(self):

		"""
		desc:
			Closes the connection to the srbox. This is done automatically by
			the SRBOX plugin when the experiment finishes.
		"""

		self._syncbox.close()
		self._started = False
