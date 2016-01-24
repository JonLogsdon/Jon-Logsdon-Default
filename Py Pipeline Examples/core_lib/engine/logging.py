import os

import AnimationEditor
import ctg.ae2.ui.const

import vlib.ui.node_graph.constants



class AE_Event_Log:
	"""
	Event log for AE elements. This outputs to the CTG log.

	**Arguments:**

		:``doc``:	`object` Animation Editor document
		:``msg``: `str` The message being passed to the logger

	**Keyword Arguments:**

		:``ctg_log``:	`bool` Does this get logged in the CTG logger
		:``error``:	`bool` Is this an error log
		:``warning``:	`bool` Is this a warning log
		:``display_in_output``:	`bool` Should we display this in the python output window
		:``extra``:	`bool` Is there extra info needed in this log

	**Examples:** ::

		>>> doc = AnimationEditor.get_active_document( )
		>>> ctg.ae2.core.data.AE_Event_Log( doc, 'This is a test!' )

	**Todo:**

		Create log file resource to reference for certain operations we are logging.

	**Author:**

		Jon Logsdon, jon.logsdon@dsvolition.com, 9/10/2015 10:45:44 AM
	"""

	def __init__( self,
	              doc,
	              msg,
	              ctg_log = True,
	              error = False,
	              warning = False,
	              extra = None ):

		self.doc = doc
		self.msg = msg
		self.ctg_log = ctg_log
		self.error = error
		self.warning = warning
		self.extra = extra


	def _gather_logs( self, database, timespan ):
		"""
		Grabs all logs generated from a given time period, and stores them.

		**Arguments:**

			:``database``:	`SQL database` SQL database where logs will be stored
			:``timespan``:  `time` The timespan on when to grab the logs since

		**Keyword Arguments:**

			:``None``

		**Returns:**

			:``log_files``:	`list` The log file(s) for the given time

		**Examples:** ::

			Enter code examples here. (optional field)

		**Todo:**

			Gather all of the logs here, and store them to get ready for delivery to users
			Utilize SQL database to grab logs

		**Author:**

			Jon Logsdon, jon.logsdon@dsvolition.com, 9/24/2015 11:06:15 AM
		"""

		if not self.doc:
			return

		pass


	def distribute_logs( self, pane=None, email=None ):
		"""
		Distributes the gathered logs into email and panels for users to grab.

		**Arguments:**

			:``None``

		**Keyword Arguments:**

			:``pane``:	`wx.Panel` Is there a pane to use for queries of the log files?
			:``email``:  `email client` Is this going out to email users of these logs?

		**Returns:**

			:``True/False``:	`bool` Did it succeed?

		**Examples:** ::

			Enter code examples here. (optional field)

		**Todo:**

			Distribute the logs out for all event that have happened

		**Author:**

			Jon Logsdon, jon.logsdon@dsvolition.com, 9/24/2015 11:06:23 AM
		"""

		if not self.doc:
			return

		pass


	def write_to_log( self, display_in_output = False):
		"""
		Enter a description of the function here.

		**Arguments:**

			:``None``

		**Keyword Arguments:**

			:``None``

		**Returns:**

			:``None``

		**Examples:** ::

			>>> doc = AnimationEditor.get_active_document( )
			>>> ctg.ae2.core.data.AE_Event_Log( doc, 'This is a test!' ).write_to_log( )

		**Author:**

			Jon Logsdon, jon.logsdon@dsvolition.com, 9/10/2015 10:51:14 AM
		"""

		# Check if there is a valid document passed in
		if not self.doc:
			return

		# Is this going to be logged in the CTG logger, if so, store it thusly
		if self.ctg_log:
			kwargs = { }

			# If there is extra info passed in, add it to a kwargs dict
			if self.extra:
				kwargs[ 'extra' ] = self.extra

			# Check the type of log this is, and log it correctly with the CTG logger
			if self.error:
				ctg.log.error( self.msg, **kwargs )
			elif self.warning:
				ctg.log.warning( self.msg, **kwargs )
			else:
				ctg.log.info( self.msg, **kwargs )

		# If it is going to be show in the python output of the editor, print the message passed in
		if display_in_output or vlib.ui.node_graph.constants.DISPLAY_LOG_MESSAGES_IN_OUTPUT:
			if self.error:
				import sys
				print >> sys.stderr, self.msg

			else:
				print self.msg