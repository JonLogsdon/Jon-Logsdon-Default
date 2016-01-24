import time
import re
import threading
import subprocess
import warnings
import getpass
import ConfigParser
import io
import ctypes
import ctypes.wintypes
import stat
import platform
import signal
import fnmatch
import urllib
import urlparse


import _winreg
import win32pdhutil
import win32file
import win32api
import win32con
import win32pdh
import win32process
import win32com.client
import win32com.shell.shell
import win32com.shell.shellcon
import win32clipboard
import win32gui
import pythoncom
import pywintypes

import vlib
import vlib.user



class WatchDirectory(object):
	def __init__(self, provider_to_watch, bufferSize=1024 ):
		self.provider_to_watch = provider_to_watch
		self.changeList = []
		self.bufferSize = bufferSize

		# Constants for making win32file stuff readable
		self.ACTIONS = {
		   1 : WATCHER_ACTION_CREATED,
		   2 : WATCHER_ACTION_DELETED,
		   3 : WATCHER_ACTION_MODIFIED,
		   4 : WATCHER_ACTION_RENAMED_TO,
		   5 : WATCHER_ACTION_RENAMED_FROM
		}

		# Start watching in a separate thread
		self.thread = threading.Thread(target=self._checkInThread).start()

	def _checkInThread(self):
		"""
		Watch for changes in specified directory.  Designed to be run in a
		separate thread, since ReadDirectoryChangesW is a blocking call.
		Don't call this directly.

		*Arguments:*
			* <none>

		*Keyword Arguments:*
			* <none>

		*Returns:*
			None

		*Examples:* ::

			# Start watching in a separate thread
			self.thread = threading.Thread(target=self._checkInThread).start()

		*Author:*
			* Jon Logsdon, jon.logsdon@dsvolition.com
		"""

		FILE_LIST_DIRECTORY = 0x0001

		hDir = win32file.CreateFile (
		   self.provider_to_watch,
		   FILE_LIST_DIRECTORY,
		   win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE | win32con.FILE_SHARE_DELETE,
		   None,
		   win32con.OPEN_EXISTING,
		   win32con.FILE_FLAG_BACKUP_SEMANTICS,
		   None
		)

		while (1):
			# The following is a blocking call.  Which is why we run this in its own thread.
			newChanges = win32file.ReadDirectoryChangesW (
			   hDir,													# Previous handle to directory
			   self.bufferSize,									# Buffer to hold results
			   win32con.FILE_NOTIFY_CHANGE_FILE_NAME |	# What to watch for
			   win32con.FILE_NOTIFY_CHANGE_DIR_NAME |
			   win32con.FILE_NOTIFY_CHANGE_ATTRIBUTES |
			   win32con.FILE_NOTIFY_CHANGE_SIZE |
			   win32con.FILE_NOTIFY_CHANGE_LAST_WRITE |
			   win32con.FILE_NOTIFY_CHANGE_SECURITY,
			   None,
			   None
			)

			# Changes found, process them
			finalChanges = []
			oldFilename = None

			for change in newChanges:
				if (change[0] == 4):			# renamed to something
					oldFilename = os.path.split(change[1])[1]
					pass
				else:
					file = os.path.join(self.provider_to_watch, change[1])
					skip = False

					if (not skip):		# passed checks, so use it
						action = self.ACTIONS.get (change[0], "Unknown")

						if (change[0] == 5):		# renamed from something
							# Insert old filename, prior to being renamed
							action = action % (oldFilename)
							oldFilename = None

						# Add change tuple to list
						finalChanges.append((file, action))

			# Add processed changes to running list
			self.changeList += finalChanges

	def check(self):
		"""
		Fetches list of changes our watcher thread has accumulated.

		*Arguments:*
			* <none>

		*Keyword Arguments:*
			* <none>

		*Returns:*
			* ``changes`` Returns a list of changes

		*Author:*
			* Jon Logsdon, jon.logsdon@dsvolition.com
		"""
		changes = self.changeList
		self.changeList =	[]		# clear changeList

		return changes