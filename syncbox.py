#-*- coding:utf-8 -*-

"""
@author: Eugenius Januškevičius, eugenijus.januskevicius@vgtu.lt

@version: 0.1b 

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
from libopensesame import debug
from libopensesame.base_response_item import base_response_item
from libqtopensesame.items.qtautoplugin import qtautoplugin
from openexp.keyboard import keyboard
import libsyncbox


class syncbox(base_response_item):

	"""
	desc:
		A plug-in for using the serial response and sync box.
	"""

	process_feedback = True

	def reset(self):

		"""See item."""

		self.var.timeout = u'infinite'
		#self.var.lights = u''
		self.var.dev = u'autodetect'
		#self.var._dummy = u'no'
		#self.var.require_state_change = u'no'
		self.var.syncboxResponse = u''

	def validate_response(self, response):

		"""See base_response_item."""

#		try:
#			response = int(response)
#		except:
#			return False
#		return response >= 0 or response <= 255
		return response

	def process_response(self, response_args):

		"""See base_response_item."""

		response, t1 = response_args
	#	if isinstance(response, list):
	#		response = response[0]
		base_response_item.process_response(self, (response, t1) )

	def _get_button_press(self):

		"""
		desc:
			Calls syncbox.get_button_press() with the correct arguments.
		"""

		return self.experiment.syncbox.get_button_press(
			SbResponse=self.syncboxResponse,
			timeout=self._timeout
			)

	def prepare_response_func(self):

		"""See base_response_item."""

#		self._keyboard = keyboard(self.experiment,
#			keylist=self._allowed_responses, timeout=self._timeout)
	#	if self.var._dummy == u'yes':
	#		return self._keyboard.get_key
		# Prepare the device string
		dev = self.var.dev
		if dev == u"autodetect":
			dev = None
		# Dynamically create an srbox instance
		if not hasattr(self.experiment, "syncbox"):
			self.experiment.syncbox = libsyncbox.libsyncbox(self.experiment, dev)
			self.experiment.cleanup_functions.append(self.close)
			self.python_workspace[u'syncbox'] = self.experiment.syncbox
		# Prepare the light byte
#		s = "010" # Control string
#		for i in range(5):
#			if str(5 - i) in str(self.var.lights):
#				s += "1"
#			else:
#				s += "0"
#		self._lights = chr(int(s, 2))
#		debug.msg(u"lights string set to %s (%s)" % (s, self.var.lights))
#		if self._allowed_responses is not None:
#			self._allowed_responses = [int(r) for r in self._allowed_responses]
#		self._require_state_change = self.var.require_state_change == u'yes'
		return self._get_button_press

	def run(self):

		"""See item."""

	#	self._keyboard.flush()
		self.experiment.syncbox.start()
		self.experiment.syncbox.waitsync(self.syncboxResponse, self._timeout)
		#base_response_item.run(self)
		self.experiment.syncbox.stop()

	def close(self):

		"""
		desc:
			Neatly close the connection to the srbox.
		"""

		if not hasattr(self.experiment, "syncbox") or \
			self.experiment.syncbox is None:
				debug.msg("no active syncbox")
				return
		try:
			self.experiment.syncbox.close()
			self.experiment.syncbox = None
			debug.msg("syncbox closed")
		except:
			debug.msg("failed to close syncbox")


class qtsyncbox(syncbox, qtautoplugin):

	def __init__(self, name, experiment, script=None):

		syncbox.__init__(self, name, experiment, script)
		qtautoplugin.__init__(self, __file__)
