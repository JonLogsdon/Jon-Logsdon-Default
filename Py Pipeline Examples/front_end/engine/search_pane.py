import wx
import ast
import param_types

import ctg.ae2.ui.const
import ctg.ae2.ui.lister
import ctg.ae2.ui.node
import ctg.ae2.ui.filter
import ctg.ae2.ui.panes.tag_associations
import ctg.ae2.core.data
import vlib.debug
import vlib.ui.lister_lib.node

import AnimationEditor
import GUILib

HELP_URL = ur"onenote:http://vsp/projects/ctg/CTG%20OneNote/CTG/Tools/User%20Documentation/CTG%20Editor/Animation%20Editor/General.one#section-id={866BB17A-1B64-4D66-AB0E-17AA3344AEA0}&end"


class Filter_String_Value( ctg.ae2.ui.filter.Node_Filter ):
	"""
	ListerLib -
	Custom String Filter, that will ensure children and parent nodes will be displayed

	*Author:*
		* Randall Hess, randall.hess@volition-inc.com, 4/30/2013 9:36:38 AM
	"""

	QUO_STR = '\"'
	AND_STR = '+'
	NOT_STR = '-'
	OR_STR = '|'
	IS_STR = ' '
	MENU_OR_STR = ' '

	SEARCH_DEF = { \
		AND_STR	: [ ],
		NOT_STR	: [ ],
		OR_STR	: [ ],
	}

	def __init__( self, **kwargs ):
		"""
		Setup the string filter

		*Author:*
			* Randall Hess, randall.hess@volition-inc.com, 4/30/2013 9:37:26 AM
		"""

		ctg.ae2.ui.filter.Node_Filter.__init__( self, **kwargs )
		self.val = ''
		self.shelf_or = None
		self.search_strings_dict = self.SEARCH_DEF


	def set_string_value( self, val ):
		"""
		Set the string value

		*Arguments:*
			* ``val`` Incoming string

		*Returns:*
			* ``Bool`` If the string is parsed based on the incoming value

		*Author:*
			* Randall Hess, randall.hess@volition-inc.com, 4/30/2013 9:37:50 AM
		"""

		val = val.lower( )
		if val == self.val:
			return False
		self.val = val.lower( )
		self.parse_string( val )
		return True


	def parse_string( self, value=None ):
		"""
		ListerLib -
		This is basically the same parse_string method in the base String Filter

		Determine if the text and tokens in the string will display the given node
		Set the search_strings_dict based on the findings, that will be used to determine
		if a node can be displayed

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``none`` self.search_strings_dict will be updated

		*Author:*
			* Randall Hess, randall.hess@volition-inc.com, 4/30/2013 8:54:51 AM
		"""

		# Make sure our string isn't empty
		if self.val:
			doc = AnimationEditor.get_active_document( )

			# Setup some temp values for later
			base_str = self.val
			base_list = [ ]
			and_list = [ ]
			not_list = [ ]
			or_list = [ ]
			is_list = [ ]
			menu_or_list = [ ]

			or_mode = None

			# Loop as long as we keep finding open quotes
			open_idx = base_str.find( self.QUO_STR )
			while open_idx > -1:

				# Replace open quote with a pipe so we can find more
				base_str = base_str.replace( base_str[ open_idx ], '|', 1 )

				# Find close quote, if none, remove open quote and bail
				close_idx = base_str.find( self.QUO_STR )
				if close_idx == -1:
					base_str = base_str[ :open_idx ] + base_str[ ( open_idx + 1 ): ]
					break

				# Grab quote without quotation marks, check for blank string
				quote_str = base_str[ ( open_idx + 1 ):close_idx ]
				if quote_str:

					# Grab search type, if possible
					type_idx = open_idx - 1
					type_str = ''
					if type_idx > -1:
						type_str = base_str[ type_idx ]

					# For search type +, add quote to AND list
					if type_str == self.AND_STR:
						open_idx = type_idx
						and_list.append( quote_str )
					# For search type -, add quote to NOT list
					elif type_str == self.NOT_STR:
						open_idx = type_idx
						not_list.append( quote_str )
					# For no search type, add quote to OR list
					else:
						or_list.append( quote_str )

				# Remove entire quote from base string
				base_str = base_str[ :open_idx ] + base_str[ ( close_idx + 1 ): ]

				# Find next open quote in base string
				open_idx = base_str.find( self.QUO_STR )

			# Split remaining string at whitespaces
			base_list = base_str.split( )

			menu_item = ctg.ae2.ui.filter.get_search_mode_pref( )
			if menu_item:
				or_mode = True
			else:
				or_mode = False

			# Loop through list of remaining strings
			for base_str in base_list:

				# Grab search type from string
				type_str = base_str[ 0 ]

				# For search type +, add string to AND list
				if type_str == self.AND_STR:
					base_str = base_str[ 1: ]
					if base_str:
						and_list.append( base_str )
				# For search type -, add string to NOT list
				elif type_str == self.NOT_STR:
					base_str = base_str[ 1: ]
					if base_str:
						not_list.append( base_str )
				# For no search type, add string to OR list
				elif type_str == self.OR_STR:
					or_list.append( base_str )
				else:
					if or_mode:
						menu_or_list.append( str( base_str ) )
						self.shelf_or = True
					else:
						is_list.append( str( base_str ) )
						self.shelf_or = None

			if and_list or not_list or or_list:
				# Populate search dict with results
				self.search_strings_dict =	{ \
					self.AND_STR	: and_list,
					self.NOT_STR	: not_list,
					self.OR_STR		: or_list,
				}
			else:
				self.search_strings_dict = { \
				   self.IS_STR  : str( value ),
				   self.MENU_OR_STR  : str( value ),
				}

		# If string is empty, default search dict
		else:
			self.search_strings_dict = self.SEARCH_DEF


	def check_value( self, node ):
		"""
		Check the value of a node
		return True if it matches the conditions we are looking for

		*Arguments:*
			* ``node`` Lister node

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``bool`` If the node/data obj has the name in the active bookmarks list

		*Author:*
			* Randall Hess, randall.hess@volition-inc.com, 4/30/2013 8:50:30 AM
		"""

		doc = AnimationEditor.get_active_document( )
		node_type = node.get_node_type( )
		valid_node_types = self.get_node_types( )
		if ( not valid_node_types ) or ( node_type in self.get_node_types( ) ):
			if doc.search_type == 'Audio':
				node_type = ctg.ae2.ui.const.SOUND_TRIGGER
				data_obj = node.data_obj
				if data_obj:
					if isinstance( data_obj.get_data_obj( ), ctg.ae2.core.data.Tag_Association_Item ):
						clip = data_obj.get_data_obj( ).get_clip_item( )
						#if clip and not isinstance( clip, ctg.ae2.core.data.State_Machine_Item ):
						# Unsure about this change, but Clip_Item is the ONLY one with the method .get_anim_triggers
						if clip and isinstance( clip, ctg.ae2.core.data.Clip_Item ):
							triggers = clip.get_anim_triggers( )
							if triggers:
								for trigger in triggers:
									return clip.get_audio_trigger_data( trigger )

				return None

			else:
				# Get node name in lowercase
				name = node.get_value( ).lower( )

				# Loop through AND list and make sure ALL are found
				if self.AND_STR in self.search_strings_dict:
					for and_str in self.search_strings_dict[ self.AND_STR ]:
						if name.find( and_str ) == -1:
							return False

				# Loop through NOT list and make sure NONE are found
				elif self.NOT_STR in self.search_strings_dict:
					for not_str in self.search_strings_dict[ self.NOT_STR ]:
						if name.find( not_str ) > -1:
							return False

				# Loop through OR list and make sure at least ONE is found
				elif self.OR_STR in self.search_strings_dict:
					for or_str in self.search_strings_dict[ self.OR_STR ]:
						if name.find( or_str ) > -1:
							return True

				else:
					for value in self.search_strings_dict.values( ):
						if self.shelf_or:
							if value in name:
								return True
							else:
								return None
						else:
							if value in name:
								return True
							else:
								return None

		return None


	def can_display_node( self, node ):
		"""
		ListerLib -
		Main check to determine if we should display this node in the filter

		*Arguments:*
			* ``node`` ListerLib node

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``bool`` If the node can be displayed based on the filter

		*Author:*
			* Randall Hess, randall.hess@volition-inc.com, 4/30/2013 8:52:27 AM
		"""

		# Make sure our string isn't empty
		if self.val:

			node_type = node.get_node_type( )
			valid_node_types = self.get_node_types( )
			if ( not valid_node_types ) or ( node_type in self.get_node_types( ) ):

				# Check the string value on the node itself first
				valid = self.check_value( node )
				if not valid is None:
					return valid

				## Check any recursive children node names if they have the string then this node is valid
				#children = node.get_children_recursive( )
				#if len( children ) > 0:
					#for child in children:
						#valid = self.check_value( child )
						#if valid:
							#return True

				## Check any recursive parent node names if they have the string then this node is valid
				#if node.has_parent( ):
					#for parent in node.get_parents_recursive( ):
						#valid = self.check_value( parent )
						#if valid:
							#return True

				return False

		return False


#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# Main UI - Lister/Tree
#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
class Search_Filter_Manager( ctg.ae2.ui.filter.Node_Filter_Manager ):
	"""
	ListerLib filter manager
	Handles displaying lister nodes using various filters

	*Author:*
		* Randall Hess, randall.hess@volition-inc.com, 4/30/2013 9:34:10 AM
	"""

	def __init__( self, grid, filters = [ ], string_filter = None ):
		"""
		Setup the filter manager

		*Arguments:*
			* ``grid`` The lister that will be filtered

		*Keyword Arguments:*
			* ``filters``        List of filters that will be used
			# ``string_filter``  String filter that will be used

		*Author:*
			* Randall Hess, randall.hess@volition-inc.com, 4/30/2013 9:34:55 AM
		"""

		ctg.ae2.ui.filter.Node_Filter_Manager.__init__( self, grid, filters, string_filter )

		# Set the node_types for the String Filter
		node_types = [ ctg.ae2.ui.const.NODE_TYPE_ANIM_CLIP, ctg.ae2.ui.const.NODE_TYPE_TAG_STATE, ctg.ae2.ui.const.NODE_TYPE_TAG_ACTION, ctg.ae2.ui.const.SOUND_TRIGGER, ctg.ae2.ui.const.NODE_TYPE_SEARCH_CATALOG, ctg.ae2.ui.const.NODE_TYPE_SEARCH_NETWORK ]
		self.get_string_filter( ).set_node_types( node_types )


	def is_active( self ):
		"""
		Method to determine if the filter is active

		*Returns:*
			* ``Bool`` If the filter is active

		*Author:*
			* Randall Hess, randall.hess@volition-inc.com, 4/30/2013 9:33:09 AM
		"""

		if hasattr( self.grid.settings_collection, 'option_filter' ):
			return self.grid.settings_collection.option_filter
		return False


	def can_display_node( self, node ):
		"""
		ListerLib -
		Main check to determine if we should display this node in the filter

		*Arguments:*
			* ``node`` ListerLib node

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``bool`` If the node can be displayed based on the filter

		*Author:*
			* Randall Hess, randall.hess@volition-inc.com, 4/30/2013 8:52:27 AM
		"""

		try:
			for node_filter in self.filters:
				if not node_filter.can_display_node( node ):
					return False

			return True

		except TypeError:
			# Object has been deleted
			return False


class Anim_Search_Status_Bar( wx.StatusBar ):
	"""
	Status Bar for the Search Window

	*Author:*
		* Randall Hess, randall.hess@volition-inc.com, 4/30/2013 9:26:40 AM
	"""

	def __init__( self, parent ):
		"""
		Construct the Search Status Bar

		*Arguments:*
			* ``parent`` Pane that will contain this lister

		*Author:*
			* Randall Hess, randall.hess@volition-inc.com, 4/30/2013 9:28:20 AM
		"""

		wx.StatusBar.__init__( self, parent, -1, style = wx.STB_SHOW_TIPS | wx.STB_ELLIPSIZE_END | wx.FULL_REPAINT_ON_RESIZE )

		self.SetFieldsCount( 2 )
		self.SetDoubleBuffered( True )

		self.SetStatusWidths( [ -1, 20 ] )
		self.size_changed = False
		self.Bind( wx.EVT_SIZE, self.OnSize )
		self.Bind( wx.EVT_IDLE, self.OnIdle )

		self.helplink = wx.HyperlinkCtrl( self, wx.ID_ANY, u'Help', HELP_URL, wx.DefaultPosition, wx.DefaultSize, wx.HL_DEFAULT_STYLE )
		self.helplink.SetFont( wx.Font( 7, 70, 90, 90, True, wx.EmptyString ) )

		# set the initial position of the progress bar and the help link
		self.Reposition( )
		self.clear_status( )


	def OnSize( self, event ):
		"""
		Handle pane sizing

		*Arguments:*
			* ``evt`` Wx Size event

		*Keyword Arguments:*
			* ``None``

		*Returns:*
			* ``None``

		*Examples:* ::

			Enter code examples here. (optional field)

		*Todo:*
			* Enter thing to do. (optional field)

		*Author:*
			* Randall Hess, randall.hess@volition-inc.com, 10/1/2013 8:21:39 AM
		"""

		self.Reposition( )
		self.size_changed = True


	def OnIdle( self, event ):
		"""
		Wx Idle update, to handle sizing and positioning

		*Arguments:*
			* ``event`` WxIdle event

		*Keyword Arguments:*
			* ``None``

		*Returns:*
			* ``None``

		*Examples:* ::

			Enter code examples here. (optional field)

		*Todo:*
			* Enter thing to do. (optional field)

		*Author:*
			* Randall Hess, randall.hess@volition-inc.com, 10/1/2013 8:22:33 AM
		"""

		if self.size_changed:
			self.Reposition( )


	def Reposition( self ):
		"""
		Reposition the statusbar link

		*Arguments:*
			* ``None``

		*Keyword Arguments:*
			* ``None``

		*Returns:*
			* ``None``

		*Examples:* ::

			Enter code examples here. (optional field)

		*Todo:*
			* Enter thing to do. (optional field)

		*Author:*
			* Randall Hess, randall.hess@volition-inc.com, 10/1/2013 8:23:38 AM
		"""

		# HelpLink
		rect = self.GetFieldRect( 1 )
		self.helplink.SetPosition( ( rect.x + 2, rect.y + 4 ) )

		self.size_changed = False


	def set_status( self, msg ):
		"""
		Set the text of the status bar

		*Arguments:*
			* ``msg`` String of the text to be set

		*Keyword Arguments:*
			* ``None``

		*Returns:*
			* ``None``

		*Examples:* ::

			Enter code examples here. (optional field)

		*Todo:*
			* Enter thing to do. (optional field)

		*Author:*
			* Randall Hess, randall.hess@volition-inc.com, 10/1/2013 8:24:21 AM
		"""

		self.SetStatusText( msg, 0 )


	def clear_status( self ):
		"""
		Set the status bar to an empty string

		*Arguments:*
			* ``None``

		*Keyword Arguments:*
			* ``None``

		*Returns:*
			* ``None``

		*Examples:* ::

			Enter code examples here. (optional field)

		*Todo:*
			* Enter thing to do. (optional field)

		*Author:*
			* Randall Hess, randall.hess@volition-inc.com, 10/1/2013 8:25:11 AM
		"""

		self.set_status( u'' )



class Column_Group( vlib.ui.lister_lib.column.Column ):
	"""
	Column object for anim group

	*Arguments:*
		* ``Column`` ListerLib column object

	*Keyword Arguments:*
		* ``None``

	*Examples:* ::

		Enter code examples here. (optional field)

	*Todo:*
		* Enter thing to do. (optional field)

	*Author:*
		* Randall Hess, randall.hess@volition-inc.com, 9/26/2013 9:51:11 AM
	"""

	def __init__( self ):
		"""
		Construct the Column Group

		*Arguments:*
			* ``None``

		*Keyword Arguments:*
			* ``None``

		*Returns:*
			* ``None``

		*Examples:* ::

			Enter code examples here. (optional field)

		*Todo:*
			* Enter thing to do. (optional field)

		*Author:*
			* Randall Hess, randall.hess@volition-inc.com, 9/26/2013 10:21:58 AM
		"""
		vlib.ui.lister_lib.column.Column.__init__( self, 'Group', 'search_group', param_types.STRING, can_hide = True, can_move = True, is_shown = True )


	def get_value( self, node ):
		"""
		Get the specific value of the item in this particular column

		*Arguments:*
			* ``node`` ctg.ae2.node

		*Keyword Arguments:*
			* ``None``

		*Returns:*
			* ``String`` name of the tag association tag value

		*Examples:* ::

			Enter code examples here. (optional field)

		*Todo:*
			* Enter thing to do. (optional field)

		*Author:*
			* Randall Hess, randall.hess@volition-inc.com, 9/26/2013 10:19:20 AM
		"""

		return node.get_data_obj( ).get_data_obj( ).get_group_name( )



class Column_Set( vlib.ui.lister_lib.column.Column ):
	"""
	Column object for anim sets

	*Arguments:*
		* ``Column`` ListerLib column object

	*Keyword Arguments:*
		* ``None``

	*Examples:* ::

		Enter code examples here. (optional field)

	*Todo:*
		* Enter thing to do. (optional field)

	*Author:*
		* Randall Hess, randall.hess@volition-inc.com, 9/26/2013 9:51:11 AM
	"""

	def __init__( self ):
		"""
		Construct the Column Set

		*Arguments:*
			* ``None``

		*Keyword Arguments:*
			* ``None``

		*Returns:*
			* ``None``

		*Examples:* ::

			Enter code examples here. (optional field)

		*Todo:*
			* Enter thing to do. (optional field)

		*Author:*
			* Randall Hess, randall.hess@volition-inc.com, 9/26/2013 10:21:58 AM
		"""
		vlib.ui.lister_lib.column.Column.__init__( self, 'Set', 'search_set', param_types.STRING, can_hide = True, can_move = True, is_shown = True )


	def get_value( self, node ):
		"""
		Get the specific value of the item in this particular column

		*Arguments:*
			* ``node`` ctg.ae2.node

		*Keyword Arguments:*
			* ``None``

		*Returns:*
			* ``String`` name of the tag association tag value

		*Examples:* ::

			Enter code examples here. (optional field)

		*Todo:*
			* Enter thing to do. (optional field)

		*Author:*
			* Randall Hess, randall.hess@volition-inc.com, 9/26/2013 10:19:20 AM
		"""

		return node.get_data_obj( ).get_data_obj( ).get_set_name( )



class Column_Clip( vlib.ui.lister_lib.column.Column ):
	"""
	Column object for clip objects

	*Arguments:*
		* ``Column`` ListerLib column object

	*Keyword Arguments:*
		* ``None``

	*Examples:* ::

		Enter code examples here. (optional field)

	*Todo:*
		* Enter thing to do. (optional field)

	*Author:*
		* Randall Hess, randall.hess@volition-inc.com, 9/26/2013 9:51:11 AM
	"""

	def __init__( self ):
		"""
		Construct the Column Tag

		*Arguments:*
			* ``None``

		*Keyword Arguments:*
			* ``None``

		*Returns:*
			* ``None``

		*Examples:* ::

			Enter code examples here. (optional field)

		*Todo:*
			* Enter thing to do. (optional field)

		*Author:*
			* Randall Hess, randall.hess@volition-inc.com, 9/26/2013 10:21:58 AM
		"""
		vlib.ui.lister_lib.column.Column.__init__( self, 'Clip', 'search_clip', param_types.STRING, can_hide = True, can_move = False, is_shown = True )


	def get_value( self, node ):
		"""
		Get the specific value of the item in this particular column

		*Arguments:*
			* ``node`` ctg.ae2.node

		*Keyword Arguments:*
			* ``None``

		*Returns:*
			* ``String`` name of the tag association tag value

		*Examples:* ::

			Enter code examples here. (optional field)

		*Todo:*
			* Enter thing to do. (optional field)

		*Author:*
			* Randall Hess, randall.hess@volition-inc.com, 9/26/2013 10:19:20 AM
		"""

		return node.get_data_obj( ).get_data_obj( ).get_clip_name( )



class Column_Tag( vlib.ui.lister_lib.column.Column ):
	"""
	Column object for clip objects

	*Arguments:*
		* ``Column`` ListerLib column object

	*Keyword Arguments:*
		* ``None``

	*Examples:* ::

		Enter code examples here. (optional field)

	*Todo:*
		* Enter thing to do. (optional field)

	*Author:*
		* Randall Hess, randall.hess@volition-inc.com, 9/26/2013 9:51:11 AM
	"""

	def __init__( self ):
		"""
		Construct the Column Tag

		*Arguments:*
			* ``None``

		*Keyword Arguments:*
			* ``None``

		*Returns:*
			* ``None``

		*Examples:* ::

			Enter code examples here. (optional field)

		*Todo:*
			* Enter thing to do. (optional field)

		*Author:*
			* Randall Hess, randall.hess@volition-inc.com, 9/26/2013 10:21:58 AM
		"""

		vlib.ui.lister_lib.column.Column.__init__( self, 'Tag', 'search_tag', param_types.STRING, can_hide = True, can_move = False, is_shown = True )


	def get_value( self, node ):
		"""
		Get the specific value of the item in this particular column

		*Arguments:*
			* ``node`` ctg.ae2.node

		*Keyword Arguments:*
			* ``None``

		*Returns:*
			* ``String`` name of the tag association tag value

		*Examples:* ::

			Enter code examples here. (optional field)

		*Todo:*
			* Enter thing to do. (optional field)

		*Author:*
			* Randall Hess, randall.hess@volition-inc.com, 9/26/2013 10:19:20 AM
		"""

		return node.get_data_obj( ).get_data_obj( ).get_tag_name( )


class Column_Triggers_Count( vlib.ui.lister_lib.column.Column ):
	"""
	Column within the search pane for the audio triggers count that is associated with a clip.

	**Arguments:**

		:``vlib.ui.lister_lib.column.Column``:	`vlib.ui.lister_lib.column.Column` Column item within the search pane results

	**Keyword Arguments:**

		:``None``:

	**Author:**

		Jon Logsdon, jon.logsdon@dsvolition.com, 3/4/2015 9:50:50 AM
	"""

	def __init__( self ):
		vlib.ui.lister_lib.column.Column.__init__( self, 'Anim Triggers Count', 'search_trigger_count', param_types.STRING, can_hide = True, can_move = False, is_shown = True )


	def get_value( self, node ):
		"""
		Returns the length of the value of the audio triggers, listed in the search pane.

		**Arguments:**

			:``node``:	`Search_Pane_Item` A search item listed in the columns

		**Keyword Arguments:**

			:``None``:

		**Returns:**

			:``Trigger Payloads``:	`list` Returns the payloads associated with the search item

		**Examples:** ::

			Enter code examples here. (optional field)

		**Todo:**

			Enter thing to do. (optional field)

		**Author:**

			Jon Logsdon, jon.logsdon@dsvolition.com, 3/4/2015 9:52:32 AM
		"""

		if not isinstance( node.get_data_obj( ).get_data_obj( ), ctg.ae2.core.data.State_Tag_Item ) and not isinstance( node.get_data_obj( ).get_data_obj( ), ctg.ae2.core.data.Action_Tag_Item ):
			if node.get_data_obj( ).get_data_obj( ).get_clip_item( ) and not isinstance( node.get_data_obj( ).get_data_obj( ).get_clip_item( ), ctg.ae2.core.data.State_Machine_Item ) and not isinstance( node.get_data_obj( ).get_data_obj( ).get_clip_item( ), ctg.ae2.core.data.Blend_Tree_Item ):
				triggers = 	node.get_data_obj( ).get_data_obj( ).get_clip_item( ).get_anim_triggers( )

				return len( triggers )

			else:
				return 0


class Column_Modifiers( vlib.ui.lister_lib.column.Column ):
	def __init__( self ):
		vlib.ui.lister_lib.column.Column.__init__( self, 'Modifiers', 'search_modifier', param_types.STRING, can_hide = True, can_move = False, is_shown = True )


	def get_value( self, node ):
		if isinstance( node.get_data_obj( ).get_data_obj( ), ctg.ae2.core.data.Tag_Association_Item ):
			tag_modifiers = list( node.get_data_obj( ).get_data_obj( ).get_tag_modifiers( ) )
			if tag_modifiers:
				return tag_modifiers
			else:
				return None

		return None


class Column_Audio_Triggers( vlib.ui.lister_lib.column.Column ):
	"""
	Column within the search pane for the audio triggers associated with a clip.

	**Arguments:**

		:``vlib.ui.lister_lib.column.Column``:	`vlib.ui.lister_lib.column.Column` Column item within the search pane results

	**Keyword Arguments:**

		:``None``:

	**Author:**

		Jon Logsdon, jon.logsdon@dsvolition.com, 3/4/2015 9:50:50 AM
	"""

	def __init__( self ):
		vlib.ui.lister_lib.column.Column.__init__( self, 'Audio Triggers', 'search_audio', param_types.STRING, can_hide = True, can_move = False, is_shown = True )


	def get_value( self, node ):
		"""
		Returns the value of the audio triggers, listed in the search pane.

		**Arguments:**

			:``node``:	`Search_Pane_Item` A search item listed in the columns

		**Keyword Arguments:**

			:``None``:

		**Returns:**

			:``Trigger Payloads``:	`list` Returns the payloads associated with the search item

		**Examples:** ::

			Enter code examples here. (optional field)

		**Todo:**

			Enter thing to do. (optional field)

		**Author:**

			Jon Logsdon, jon.logsdon@dsvolition.com, 3/4/2015 9:52:32 AM
		"""

		if not isinstance( node.get_data_obj( ).get_data_obj( ), ctg.ae2.core.data.State_Tag_Item ) and not isinstance( node.get_data_obj( ).get_data_obj( ), ctg.ae2.core.data.Action_Tag_Item ):
			if node.get_data_obj( ).get_data_obj( ).get_clip_item( ) and not isinstance( node.get_data_obj( ).get_data_obj( ).get_clip_item( ), ctg.ae2.core.data.State_Machine_Item ) and not isinstance( node.get_data_obj( ).get_data_obj( ).get_clip_item( ), ctg.ae2.core.data.Blend_Tree_Item ):
				triggers = 	node.get_data_obj( ).get_data_obj( ).get_clip_item( ).get_anim_triggers( )
				values = [ ]

				for trigger in triggers:
					values.append( node.get_data_obj( ).get_data_obj( ).get_clip_item( ).get_trigger_payload_event_value( trigger ) )

				#return node.get_data_obj( ).get_data_obj( ).get_clip_item( ).get_trigger_payloads( node.get_data_obj( ).get_data_obj( ).get_clip_item( ).get_anim_triggers( ) )
				return values


class Column_Audio_Triggers_Count( vlib.ui.lister_lib.column.Column ):
	"""
	Column within the search pane for the audio triggers count that is associated with a clip.

	**Arguments:**

		:``vlib.ui.lister_lib.column.Column``:	`vlib.ui.lister_lib.column.Column` Column item within the search pane results

	**Keyword Arguments:**

		:``None``:

	**Author:**

		Jon Logsdon, jon.logsdon@dsvolition.com, 3/4/2015 9:50:50 AM
	"""

	def __init__( self ):
		vlib.ui.lister_lib.column.Column.__init__( self, 'Audio Triggers Count', 'search_audio_count', param_types.STRING, can_hide = True, can_move = False, is_shown = True )


	def get_value( self, node ):
		"""
		Returns the length of the value of the audio triggers, listed in the search pane.

		**Arguments:**

			:``node``:	`Search_Pane_Item` A search item listed in the columns

		**Keyword Arguments:**

			:``None``:

		**Returns:**

			:``Trigger Payloads``:	`list` Returns the payloads associated with the search item

		**Examples:** ::

			Enter code examples here. (optional field)

		**Todo:**

			Enter thing to do. (optional field)

		**Author:**

			Jon Logsdon, jon.logsdon@dsvolition.com, 3/4/2015 9:52:32 AM
		"""

		if not isinstance( node.get_data_obj( ).get_data_obj( ), ctg.ae2.core.data.State_Tag_Item ) and not isinstance( node.get_data_obj( ).get_data_obj( ), ctg.ae2.core.data.Action_Tag_Item ):
			if node.get_data_obj( ).get_data_obj( ).get_clip_item( ) and not isinstance( node.get_data_obj( ).get_data_obj( ).get_clip_item( ), ctg.ae2.core.data.State_Machine_Item ) and not isinstance( node.get_data_obj( ).get_data_obj( ).get_clip_item( ), ctg.ae2.core.data.Blend_Tree_Item ):
				triggers = 	node.get_data_obj( ).get_data_obj( ).get_clip_item( ).get_anim_triggers( )
				values = [ ]

				for trigger in triggers:
					if node.get_data_obj( ).get_data_obj( ).get_clip_item( ).get_payload_type( trigger ) == 'gml_sound_trigger_payload':
						values.append( node.get_data_obj( ).get_data_obj( ).get_clip_item( ).get_trigger_payload_event_value( trigger ) )

				#return node.get_data_obj( ).get_data_obj( ).get_clip_item( ).get_trigger_payloads( node.get_data_obj( ).get_data_obj( ).get_clip_item( ).get_anim_triggers( ) )
				return len( values )

			else:
				return 0


class Column_NodeGraph( vlib.ui.lister_lib.column.Column ):
	"""
	Column object for nodegraph objects

	*Arguments:*
		* ``Column`` ListerLib column object

	*Keyword Arguments:*
		* ``None``

	*Examples:* ::

		Enter code examples here. (optional field)

	*Todo:*
		* Enter thing to do. (optional field)

	*Author:*
		* Randall Hess, randall.hess@volition-inc.com, 9/26/2013 9:51:11 AM
	"""

	def __init__( self ):
		"""
		Construct the Column NodeGraph

		*Arguments:*
			* ``None``

		*Keyword Arguments:*
			* ``None``

		*Returns:*
			* ``None``

		*Examples:* ::

			Enter code examples here. (optional field)

		*Todo:*
			* Enter thing to do. (optional field)

		*Author:*
			* Randall Hess, randall.hess@volition-inc.com, 9/26/2013 10:21:58 AM
		"""

		vlib.ui.lister_lib.column.Column.__init__( self, 'NodeGraph', 'search_nodegraph', param_types.STRING, can_hide = True, can_move = False, is_shown = False )


	def get_value( self, node ):
		"""
		Get the specific value of the item in this particular column

		*Arguments:*
			* ``node`` ctg.ae2.node

		*Keyword Arguments:*
			* ``None``

		*Returns:*
			* ``String`` name of the tag association tag value

		*Examples:* ::

			Enter code examples here. (optional field)

		*Todo:*
			* Enter thing to do. (optional field)

		*Author:*
			* Randall Hess, randall.hess@volition-inc.com, 9/26/2013 10:19:20 AM
		"""

		return node.get_data_obj( ).get_nodegraph_name( )



class Column_NodeGraph_Node( vlib.ui.lister_lib.column.Column ):
	"""
	Column object for nodegraph objects

	*Arguments:*
		* ``Column`` ListerLib column object

	*Keyword Arguments:*
		* ``None``

	*Examples:* ::

		Enter code examples here. (optional field)

	*Todo:*
		* Enter thing to do. (optional field)

	*Author:*
		* Randall Hess, randall.hess@volition-inc.com, 9/26/2013 9:51:11 AM
	"""

	def __init__( self ):
		"""
		Construct the Column NodeGraph

		*Arguments:*
			* ``None``

		*Keyword Arguments:*
			* ``None``

		*Returns:*
			* ``None``

		*Examples:* ::

			Enter code examples here. (optional field)

		*Todo:*
			* Enter thing to do. (optional field)

		*Author:*
			* Randall Hess, randall.hess@volition-inc.com, 9/26/2013 10:21:58 AM
		"""

		vlib.ui.lister_lib.column.Column.__init__( self, 'Tag/Clip', 'search_node', param_types.STRING, can_hide = True, can_move = False, is_shown = False )


	def get_value( self, node ):
		"""
		Get the specific value of the item in this particular column

		*Arguments:*
			* ``node`` ctg.ae2.node

		*Keyword Arguments:*
			* ``None``

		*Returns:*
			* ``String`` name of the tag association tag value

		*Examples:* ::

			Enter code examples here. (optional field)

		*Todo:*
			* Enter thing to do. (optional field)

		*Author:*
			* Randall Hess, randall.hess@volition-inc.com, 9/26/2013 10:19:20 AM
		"""

		return node.get_data_obj( ).get_name( )


class Column_Trigger_Approvals( vlib.ui.lister_lib.column.Column ):
	def __init__( self ):
		vlib.ui.lister_lib.column.Column.__init__( self, 'Approvals', 'search_approvals', param_types.STRING, can_hide = True, can_move = False, is_shown = True )


	def get_value( self, node ):
		approval_list = [ ]
		tag = node.get_data_obj( ).get_data_obj( )
		if isinstance( tag, ctg.ae2.core.data.Tag_Association_Item ):
			clip = tag.get_clip_item( )
			if clip:
				triggers = clip.get_anim_triggers( )

				for trigger in triggers:
					if trigger.get_approver( ):
						if trigger.get_approver( ) not in approval_list:
							for app in trigger.get_approver( ):
								approval_list.append( app )

				if approval_list:
					return ( str( approval_list ).strip( "[ ]" ) )
				else:
					return None

		return None


class Column_Trigger_Types( vlib.ui.lister_lib.column.Column ):
	def __init__ ( self ):
		vlib.ui.lister_lib.column.Column.__init__( self, 'Trigger Types', 'search_trig_type', param_types.STRING, can_hide=True, can_move=False, is_shown=True )


	def get_value( self, node ):
		types_list = [ ]
		tag = node.get_data_obj( ).get_data_obj( )
		if isinstance( tag, ctg.ae2.core.data.Tag_Association_Item ):
			clip = tag.get_clip_item( )
			if clip:
				triggers = clip.get_anim_triggers( )

				for trigger in triggers:
					if trigger.get_type( ):
						if trigger.get_type( ) not in types_list:
							types_list.append( trigger.get_type( ) )

				if types_list:
					return ( str( types_list ).strip( "[ ]" ) )
				else:
					return None

		return None



class Catalog_Search_Tree( ctg.ae2.ui.lister.Anim_Grid ):
	"""
	ListerLib -
	A lister lib tree grid
	A hierarchy view of resulting Tag and Clip relative to Sets and Groups

	*Author:*
		* Randall Hess, randall.hess@volition-inc.com, 4/30/2013 9:26:40 AM
	"""


	def __init__( self, parent ):
		"""
		Construct the ListerLib Anim Search Tree

		*Arguments:*
			* ``parent`` Pane that will contain this lister

		*Author:*
			* Randall Hess, randall.hess@volition-inc.com, 4/30/2013 9:28:20 AM
		"""
		self.node_type             = ctg.ae2.ui.const.NODE_TYPE_ANIM_CLIP
		self.search_mode				= ctg.ae2.ui.const.AE_SEARCH_MODE_CATALOG
		self.selected_items        = [0]
		self.parent                = parent
		self.status_message        = 'None'
		self.multi_row_select      = True
		self.catalog_columns			= [ ]
		self.network_columns			= [ ]
		self.root_id_dict				= { }

		self.node_types = [ \
		   ctg.ae2.ui.const.NODE_TYPE_ANIM_CLIP,
		   ctg.ae2.ui.const.NODE_TYPE_TAG_STATE,
		   ctg.ae2.ui.const.NODE_TYPE_TAG_ACTION,
		   ctg.ae2.ui.const.SOUND_TRIGGER,
		   ctg.ae2.ui.const.MODIFIER,
		   ctg.ae2.ui.const.NODE_TYPE_NODE_GRAPH,
			ctg.ae2.ui.const.NODE_TYPE_SEARCH_CATALOG,
			ctg.ae2.ui.const.NODE_TYPE_SEARCH_NETWORK,]

		ctg.ae2.ui.lister.Anim_Grid.__init__( self, parent, multi_row_select = False )

		self.refresh_manager = self.get_refresh_manager( )
		self.get_node_filter_manager( ).get_string_filter( ).set_node_types( self.node_types )

		# bind for right-click menu
		#self.GetGridWindow( ).Bind( wx.EVT_RIGHT_DOWN, self.on_grid_window_context_menu )

		self.redraw( )


	def _init_node_filter_manager( self ):
		"""
		ListerLib -
		Setup the ListerLib filter manager

		*Author:*
			* Randall Hess, randall.hess@volition-inc.com, 4/30/2013 9:20:23 AM
		"""
		self._node_filter_manager = Search_Filter_Manager( self, filters = [ ], string_filter = Filter_String_Value( ) ) #filters = [ Filter_Bookmarked_Nodes( self ) ]


	def _init_root_node( self ):
		"""
		ListerLib -
		Setup the ListerLib root_node

		*Author:*
			* Randall Hess, randall.hess@volition-inc.com, 4/30/2013 9:20:23 AM
		"""
		# get the document
		doc = AnimationEditor.get_active_document( )
		if not doc:
			return

		self.root_catalog						= ctg.ae2.ui.node.Anim_Node_Generic( None, ctg.ae2.ui.const.NODE_TYPE_ROOT, None, expanded = True )
		self.root_catalog.collection		= doc.search_catalog_collection
		self.root_catalog.node_type_id	= ctg.ae2.ui.const.NODE_TYPE_SEARCH_CATALOG
		self.root_catalog.display_name	= 'Root_Catalog'

		self.root_network						= ctg.ae2.ui.node.Anim_Node_Generic( None, ctg.ae2.ui.const.NODE_TYPE_ROOT, None, expanded = True )
		self.root_network.collection		= doc.search_network_collection
		self.root_network.node_type_id 	= ctg.ae2.ui.const.NODE_TYPE_SEARCH_NETWORK
		self.root_network.display_name	= 'Root_Network'

		roots = [ self.root_catalog, self.root_network ]
		self.root_id_dict = dict( [ ( r.node_type_id, r ) for r in roots ] )

		self._root_node = self.root_catalog


	def _init_column_collection( self ):
		"""
		ListerLib
		Setup the column collection for the lister

		*Author:*
			* Randall Hess, randall.hess@volition-inc.com, 4/30/2013 9:19:34 AM
		"""
		doc = AnimationEditor.get_active_document( )

		set_column		= Column_Set( )
		group_column	= Column_Group( )
		tag_column		= Column_Tag( )
		clip_column		= Column_Clip( )
		nodegraph_column 	= Column_NodeGraph( )
		node_column			= Column_NodeGraph_Node( )
		anim_triggers_column = Column_Triggers_Count( )
		audio_trig_column	=	Column_Audio_Triggers( )
		audio_trigger_count_column = Column_Audio_Triggers_Count( )
		modifier_coluimn = Column_Modifiers( )
		trigger_approval_column = Column_Trigger_Approvals( )
		trigger_type_column = Column_Trigger_Types( )

		if doc.search_type is ctg.ae2.ui.const.AE_SEARCH_TYPE_APPROVAL:
			columns = [
			  set_column,
			  tag_column,
			  clip_column,
			  anim_triggers_column,
			  trigger_approval_column,
			  trigger_type_column ]

		else:
			columns = [
				set_column,
				group_column,
				tag_column,
				clip_column,
				nodegraph_column,
				node_column,
				modifier_coluimn,
				anim_triggers_column ]

		if doc.search_type is ctg.ae2.ui.const.AE_SEARCH_TYPE_AUDIO:
			columns.append( audio_trig_column )
			columns.append( audio_trigger_count_column )

		column_default_order = [ col.get_id( ) for col in columns ]

		# store off columns for hiding based on search mode
		self.network_columns = [ nodegraph_column.get_id( ), node_column.get_id( ) ]
		self.catalog_columns = [ set_column.get_id( ),
		                         group_column.get_id( ),
		                         tag_column.get_id( ),
		                         clip_column.get_id( ),
		                         audio_trig_column.get_id( ),
		                         trigger_approval_column.get_id( ) ]

		# get the column order from the prefs
		#column_id_list = ctg.prefs.user.get( "global.animation_editor.search_column_order", [ ] )
		#if not column_id_list:
		column_id_list = column_default_order

		# Dictionary of id(keys) & Column(values)
		column_id_dict = dict( [ ( col.get_id( ), col ) for col in columns ] )
		column_order_list = [ column_id_dict.get( id_string ) for id_string in column_id_list ]
		column_order_list = [ col for col in column_order_list if col ] # Remove None entries

		# Flag columns visible
		for col in column_order_list:
			col.is_shown = True

		# Set the column order from the preference string;  { 0 : Column, 1 : Column, ... }
		column_order_dict = dict( zip( range( len( column_id_list ) ), column_order_list ) )

		# Now create the column collection using all the gathered values
		column_set = vlib.ui.lister_lib.column.Column_Collection( columns, grid = self )
		column_set.set_widths_from_dict( self.get_column_prefs_widths_dict( ) )
		column_set.sort_column = column_set.sort_column_default = column_order_dict[ 0 ]
		column_set.column_order = column_order_dict

		self._column_collection = column_set


	def set_root_node_by_id( self, root_id, do_refresh = False ):
		"""
		Handle changing the Asset Manager lister items by node type.
		The node type dictates which root node to use in the lister.
		This root node contains all the children items for the given node type.

		*Arguments:*
			* ``root_id`` root_node identifier

		*Keyword Arguments:*
			* ``do_refresh`` perform a full table refresh including collect_objects

		*Returns:*
			* ``None``

		*Examples:* ::

			Enter code examples here. (optional field)

		*Todo:*
			* Enter thing to do. (optional field)

		*Author:*
			* Randall Hess, randall.hess@volition-inc.com, 9/26/2013 3:37:45 PM
		"""

		new_root = self.root_id_dict.get( root_id )
		if new_root:
			self.node_type = root_id
			self._root_node = new_root


	def update_visible_columns( self ):
		"""
		Show/Hide specific columns based on the search mode
		Catalog/Network

		*Arguments:*
			* ``None``

		*Keyword Arguments:*
			* ``None``

		*Returns:*
			* ``None``

		*Examples:* ::

			Enter code examples here. (optional field)

		*Todo:*
			* Enter thing to do. (optional field)

		*Author:*
			* Randall Hess, randall.hess@volition-inc.com, 9/26/2013 2:17:27 PM
		"""
		doc = AnimationEditor.get_active_document( )

		# Catalog Mode
		if self.search_mode is ctg.ae2.ui.const.AE_SEARCH_MODE_CATALOG:
			if doc.search_type is ctg.ae2.ui.const.AE_SEARCH_TYPE_AUDIO:
				if Column_Audio_Triggers( ) not in self._column_collection.columns and Column_Audio_Triggers_Count( ) not in self._column_collection.columns:
					self._column_collection.columns.append( Column_Audio_Triggers( ) )
					self._column_collection.columns.append( Column_Audio_Triggers_Count( ) )
			elif doc.search_type is ctg.ae2.ui.const.AE_SEARCH_TYPE_APPROVAL:
				if Column_Trigger_Approvals( ) not in self._column_collection.columns:
					self._column_collection.columns.append( Column_Trigger_Approvals( ) )

			for column in self._column_collection.columns:
				if column.get_id( ) in self.catalog_columns:
					self._column_collection.show_column( column )
				elif column.get_id( ) in self.network_columns:
					self._column_collection.hide_column( column )

		# Network Mode
		else:
			for column in self._column_collection.columns:
				if column.get_id( ) in self.network_columns:
					self._column_collection.show_column( column )
				elif column.get_id( ) in self.catalog_columns:
					self._column_collection.hide_column( column )

		self._column_collection.sort_column = self._column_collection.column_order[0]
		self.update_table( get_objects = True, update_sorting = False )


	def setup_column_prefs( self ):
		"""
		Set the default column preferences

		*Arguments:*
			* ``None`` Enter a description for the argument here.

		*Keyword Arguments:*
			* ``None`` Enter a description for the keyword argument here.

		*Returns:*
			* ``None`` If any, enter a description for the return value here.

		*Examples:* ::

			Enter code examples here. (optional field)

		*Todo:*
			* Enter thing to do. (optional field)

		*Author:*
			* Randall Hess, randall.hess@volition-inc.com, 9/23/2013 12:52:21 PM
		"""

		ctg.prefs.user.setdefault( "global.animation_editor.search_column_order", [ 'tag_assoc_set', 'tag_assoc_group', 'tag_assoc_tag', 'tag_assoc_clip' ] )


	def get_column_prefs_widths_dict( self ):
		"""
		Get the column widths from the prefs

		*Arguments:*
			* ``None`` Enter a description for the argument here.

		*Keyword Arguments:*
			* ``None`` Enter a description for the keyword argument here.

		*Returns:*
			* ``Dict`` Dict of column ids/widths

		*Examples:* ::

			Enter code examples here. (optional field)

		*Todo:*
			* Enter thing to do. (optional field)

		*Author:*
			* Randall Hess, randall.hess@volition-inc.com, 9/23/2013 12:52:21 PM
		"""

		width_prefs_dict = { }
		try:
			width_prefs = ctg.prefs.user[ 'global.animation_editor.search_width_prefs' ]
			if width_prefs:
				# convert string dict to proper dict
				widths_dict = ast.literal_eval( width_prefs )
				if isinstance( widths_dict, dict ):
					width_prefs_dict = widths_dict

		except KeyError:
			pass

		return width_prefs_dict


	def save_column_prefs( self ):
		"""
		Save the column widths

		*Arguments:*
			* ``None`` Enter a description for the argument here.

		*Keyword Arguments:*
			* ``None`` Enter a description for the keyword argument here.

		*Returns:*
			* ``None`` If any, enter a description for the return value here.

		*Examples:* ::

			Enter code examples here. (optional field)

		*Todo:*
			* Enter thing to do. (optional field)

		*Author:*
			* Randall Hess, randall.hess@volition-inc.com, 9/23/2013 12:52:21 PM
		"""

		widths_dict = self.get_column_collection( ).get_widths_dict( )
		ctg.prefs.user[ 'global.animation_editor.search_width_prefs' ] = str( widths_dict )


	def record_column_order( self ):
		"""
		Save the columns order to the prefs

		*Arguments:*
			* ``None`` Enter a description for the argument here.

		*Keyword Arguments:*
			* ``None`` Enter a description for the keyword argument here.

		*Returns:*
			* ``None`` If any, enter a description for the return value here.

		*Examples:* ::

			Enter code examples here. (optional field)

		*Todo:*
			* Enter thing to do. (optional field)

		*Author:*
			* Randall Hess, randall.hess@volition-inc.com, 9/23/2013 12:52:21 PM
		"""

		column_list = [ ]
		column_collection = self.get_column_collection( )
		for col in range( self.GetNumberCols( ) ):
			label = self.GetColLabelValue( col )
			# Record new column order -------------------
			column_collection.column_order[ col ] = column_collection.label_dict[ label ]
			column_list.append( column_collection.column_order[ col ].id_string )

		ctg.prefs.user[ "global.animation_editor.search_column_order" ] = column_list


	def get_pane_callback_id( self ):
		"""
		This method gets and returns search pane callback id constant.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``string`` search pane callback id constant.

		*Author:*
			* Randall Hess, randall.hess@volition-inc.com, 4/30/2013 9:19:34 AM
		"""
		return ctg.ae2.ui.const.PANE_LISTENER_SEARCH_CALLBACK_ID


	def _collect_root_node( self, root_node ):
		"""
		Collect all the node type items for a given root node

		*Arguments:*
			* ``root_node`` ListerLib root_node

		*Keyword Arguments:*
			* ``None``

		*Returns:*
			* ``None``

		*Examples:* ::

			Enter code examples here. (optional field)

		*Todo:*
			* Enter thing to do. (optional field)

		*Author:*
			* Randall Hess, randall.hess@volition-inc.com, 9/26/2013 3:41:41 PM
		"""

		root_node.destroy_children( notify = False )

		# set the node type
		node_type = ctg.ae2.ui.const.NODE_TYPE_SEARCH_CATALOG
		if not self.search_mode is ctg.ae2.ui.const.AE_SEARCH_MODE_CATALOG:
			node_type = ctg.ae2.ui.const.NODE_TYPE_SEARCH_NETWORK

		for idx, item in enumerate( root_node.collection.get_items( ) ):
			if item:
				ctg.ae2.ui.node.Search_Node( root_node, node_type, item, display_name = item.get_name( ), expanded = True )

		root_node.sort_children_recursive( )


	#@vlib.debug.Debug_Timing( 'Collect Objects' )
	def collect_objects( self ):
		"""
		ListerLib -
		Main method to create all the lister nodes derived from data_objects
		Populate the lister grid

		*Arguments:*
			* ``None``

		*Keyword Arguments:*
			* ``None``

		*Returns:*
			* ``grid_collection`` ListerLib object containing all grid items

		*Examples:* ::

			Enter code examples here. (optional field)

		*Todo:*
			* Enter thing to do. (optional field)

		*Author:*
			* Randall Hess, randall.hess@volition-inc.com, 9/26/2013 3:46:20 PM
		"""
		root_node = self.get_root_node( )

		# if the root node doesn't yet have children it likely hasn't been opened yet
		# once the tab has been opened the root node should populate with items and will be faster on the next load
		# also if a collection has been updated it will be flagged as dirty and need to be refreshed
		#print 'Collection: {0} Is_Dirty: {1}'.format( root_node.collection, root_node.collection.is_dirty )
		if not root_node.has_children( ) or root_node.collection.is_dirty:
			self._collect_root_node( root_node )
			root_node.collection.is_dirty = False

		# set the mult_row_select flag for the specific tab/root_node type
		#self.multi_row_select = root_node.multi_select

		# update the grid collection
		self.update_grid_object_collection( )
		return self.grid_object_collection


	def set_search_mode( self, search_mode ):
		"""
		Called from the pane when the search mode has been changed.
		Catalog or Network

		*Arguments:*
			* ``search_mode`` The search mode based on the active Pane tab

		*Keyword Arguments:*
			* ``None``

		*Returns:*
			* ``None``

		*Examples:* ::

			Enter code examples here. (optional field)

		*Todo:*
			* Enter thing to do. (optional field)

		*Author:*
			* Randall Hess, randall.hess@volition-inc.com, 9/26/2013 1:14:57 PM
		"""

		doc = AnimationEditor.get_active_document( )
		if not doc:
			return

		if not search_mode is self.search_mode:

			# Change the lister search mode
			self.search_mode = search_mode

			# Change to Network Root
			if self.search_mode is ctg.ae2.ui.const.AE_SEARCH_MODE_CATALOG:
				self.set_root_node_by_id( ctg.ae2.ui.const.NODE_TYPE_SEARCH_CATALOG )

			# Change to Catalog Root
			else:
				self.set_root_node_by_id( ctg.ae2.ui.const.NODE_TYPE_SEARCH_NETWORK )

			# Turn on/off specific columns
			self.update_visible_columns( )


	def on_cell_selected( self, event ):
		"""
		Process cell select/click.

		*Author:*
			* Andrew Dour, andrew.dour@volition-inc.com, 5/18/2012 1:30:00 PM
		"""
		doc = AnimationEditor.get_active_document( )

		self.SetFocus( )
		row = event.GetRow( )
		col = event.GetCol( )
		ctrl_down = event.ControlDown( )
		shift_down = event.ShiftDown( )
		alt_down = event.AltDown( )
		current_pos = self.GetGridCursorRow( )
		is_selected = self.IsInSelection( row, col )
		column_collection = self.get_column_collection( )
		column_object = column_collection.get_column( col )

		# See if we got an interpretted position from the row/column movers
		click_pos = event.GetClientData( )
		if not click_pos:
			click_pos = vlib.ui.lister_lib.input.convert_to_grid_click_position( self, event.GetPosition( ) )
			#click_pos = event.GetPosition( )

		# Translate the hit by the column label height
		col_win = self.GetGridColLabelWindow( )
		if col_win.IsShown( ):
			click_pos.y -= col_win.GetSize( )[ 1 ]

		post_selection_event = False

		node = self.get_row_as_node( row )

		if node:
			data_obj = node.get_data_obj( )
			node_type = node.get_node_type( )

			full_rect = self.CellToRect( row, col )

			self.BeginBatch( )

			nodes = [ node ]

			#if shift_down == True:
				#nodes.extend( self.get_selected_nodes( ) )
				#nodes = list( set( nodes ) )

			did_click = False

			set_bool = False
			bool_value = None

			if did_click != True:
				if shift_down == True:
					self.select_range( current_pos, row, add_to_selection = ctrl_down, post_event = False, visible_only = True )

				elif ( ctrl_down == True ) and ( is_selected == True ):
					self.DeselectRow( row )
					set_bool = False
				else:
					if not self.multi_row_select:
						self.ClearSelection( )

					self.SelectRow( row, addToSelected = ctrl_down )
					self.SetGridCursor( row, col )

				post_selection_event = True

			# Fix some column sizing issues if needed.
			wx.PostEvent( self, wx.SizeEvent( self.GetSize( ) ) )

			self.EndBatch( )

			if post_selection_event == True:
				self.is_selection_internal = True
				wx.PostEvent( self, vlib.ui.lister_lib.core.Event_Select( add_to_selection = ( shift_down or ctrl_down ), column_object = column_object ) )


		event.Skip( False )


	def on_cell_double_click( self, event ):
		"""
		ListerLib -
		Handle doubleclick of a search item

		*Arguments:*
			* ``event`` The wx double-click event

		*Keyword Arguments:*
			* ``None``

		*Returns:*
			* ``None``

		*Examples:* ::

			Enter code examples here. (optional field)

		*Todo:*
			* Enter thing to do. (optional field)

		*Author:*
			* Randall Hess, randall.hess@volition-inc.com, 9/30/2013 9:10:39 AM
		"""

		doc = AnimationEditor.get_active_document( )
		if not doc:
			return

		col = event.GetCol( )
		row = event.GetRow( )

		# Skip event only if we have an editor for this column
		column_object = self.get_column_collection( ).column_order[ col ]

		node = self.get_row_as_node( row )
		if node:
			# only post an event if the items are different
			data_obj = self.get_node_as_data_obj( node )

			# track if we need to change layout
			current_layout = ctg.prefs.user[ "global.animation_editor.selected_view_layout" ]
			active_layout = None

			# SELECT TAG ASSOCIATION
			if self.search_mode is ctg.ae2.ui.const.AE_SEARCH_MODE_CATALOG:
				# set the active tag_association column by the search filter clip/tag
				if doc.search_type is ctg.ae2.ui.const.AE_SEARCH_TYPE_TAG:
					use_clip_column = False
				elif doc.search_type is ctg.ae2.ui.const.AE_SEARCH_TYPE_AUDIO:
					use_clip_column = False
				else:
					use_clip_column = True

				# select set/group/tag association
				set_group = data_obj.get_data_obj( ).get_set_name( ) + '|' + data_obj.get_data_obj( ).get_group_name( )
				if set_group:
					tag_uid = data_obj.get_data_obj( ).get_uid( )
					if tag_uid:
						ctg.ae2.ui.panes.tag_associations.anim_tag_association_modified( doc, set_group, tag_uid, use_clip_column = use_clip_column )
						active_layout = ctg.ae2.ui.const.CATALOG_VIEW_LAYOUT


			# SELECT AND LOAD NETWORK
			else:
				if data_obj.nodegraph_name:
					# load the child node graph
					if doc.is_node_graph( data_obj.nodegraph_name ):
						# StateMachine
						if doc.is_state_machine( data_obj.nodegraph_name ):
							node_graph = doc.state_machine_collection.get_item_by_name( data_obj.nodegraph_name )
							if node_graph:
								doc.event_manager.post_state_machine_load_event( [ node_graph ], owner = ctg.ae2.ui.const.PANE_ID_SEARCH )
						# BlendTree
						elif doc.is_blend_tree( data_obj.nodegraph_name ):
							node_graph = doc.blend_tree_collection.get_item_by_name( data_obj.nodegraph_name )
							if node_graph:
								doc.event_manager.post_blend_tree_load_event( [ node_graph ], owner = ctg.ae2.ui.const.PANE_ID_SEARCH )

						# update the selection manager and breadcrumbs
						if node_graph:
							active_layout = ctg.ae2.ui.const.NETWORK_VIEW_LAYOUT

			# Handle Catalog/Network View Switching
			if not current_layout is active_layout:

				#stop the previewed animation if it is playing.
				#if hasattr( doc, 'preview_pane' ):
				#	doc.preview_pane.layout_view_changed( )

					# change the layout
					if active_layout is ctg.ae2.ui.const.CATALOG_VIEW_LAYOUT:
						doc.select_catalog_layout( )
					else:
						doc.select_network_layout( )

					# set the new prefs
					ctg.prefs.user["global.animation_editor.selected_view_layout"] = active_layout


		event.Skip( False )



class Anim_Search_Pane( wx.Panel ):
	"""
	The Panel that will contain the Animation Search and Results lister

	*Author:*
		* Randall Hess, randall.hess@volition-inc.com, 4/30/2013 9:49:36 AM
	"""

	PANE_ID 		= ctg.ae2.ui.const.PANE_ID_SEARCH
	PANE_TITLE 	= ctg.ae2.ui.const.PANE_TITLE_SEARCH


	def __init__( self, parent ):
		"""
		Setup the Animation Search Pane
		- Setup the lister
		- Setup the bookmarks toolbar

		*Arguments:*
			* ``parent`` The panel object that will house this Pane

		*Author:*
			* Randall Hess, randall.hess@volition-inc.com, 4/30/2013 9:50:09 AM
		"""

		wx.Panel.__init__( self, parent )

		# set the lister
		self.lister = Catalog_Search_Tree( self )

		# set the statusbar
		self.statusbar = Anim_Search_Status_Bar( self )

		# create main sizers
		main_sizer 			= wx.BoxSizer( wx.VERTICAL )
		search_sizer 		= wx.BoxSizer( wx.HORIZONTAL )
		options_sizer 		= wx.BoxSizer( wx.HORIZONTAL )

		# add search field
		self.search_field = ctg.ae2.ui.filter.Search_Control( self, self.lister )

		# populate the search type choices controls
		self.search_type_choices 	= wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, ( 125, -1 ), '' , 0 )
		search_types 	= [ ctg.ae2.ui.const.AE_SEARCH_STRING_TAG, ctg.ae2.ui.const.AE_SEARCH_STRING_CLIP, ctg.ae2.ui.const.AE_SEARCH_STRING_AUDIO, ctg.ae2.ui.const.AE_SEARCH_STRING_APPROVAL ]
		self.search_type_choices.SetItems( search_types )
		self.search_type_choices.SetStringSelection( search_types[0] )

		search_sizer.AddSpacer( 5 )
		search_sizer.Add( self.search_type_choices, 0, wx.ALIGN_CENTER_HORIZONTAL, 0 )
		search_sizer.AddSpacer( 5 )
		search_sizer.Add( self.search_field, 1, wx.EXPAND | wx.ALIGN_CENTER_HORIZONTAL, 0)
		search_sizer.AddSpacer( 5 )

		# Create the tabs section
		self.tab_filter_dict = { 0 : ctg.ae2.ui.const.AE_SEARCH_MODE_CATALOG, 1 : ctg.ae2.ui.const.AE_SEARCH_MODE_NETWORK }
		self.tabs = wx.Notebook( self, -1, size = ( -1, 22 ), style = wx.BK_DEFAULT )
		for label in self.tab_filter_dict.values( ):
			self.tabs.AddPage( wx.Panel( self.tabs, -1 ), label )

		# Add the tabs to the sizer
		tabs_toolbar = wx.BoxSizer( wx.HORIZONTAL )
		tabs_toolbar.AddSpacer( 3 )
		tabs_toolbar.Add( self.tabs, 1, wx.EXPAND | wx.TOP | wx.LEFT, 2 )

		# add lister
		self.sub_sizer = wx.BoxSizer( wx.HORIZONTAL )
		self.sub_sizer.Add( self.lister, 1, wx.EXPAND, 0 )

		# update main sizer and layout
		main_sizer.AddSpacer( 5 )
		main_sizer.Add( search_sizer, 0, wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, 0 )
		main_sizer.AddSpacer( 5 )
		main_sizer.Add( tabs_toolbar, 0, wx.EXPAND, 0 )
		main_sizer.Add( self.sub_sizer, 1, wx.EXPAND, 0 )
		main_sizer.Add( self.statusbar, 0, wx.EXPAND, 0 )
		self.SetSizer( main_sizer )
		self.Layout( )

		# set binding events
		self.lister.Bind( wx.EVT_SCROLLWIN, self.on_scroll )
		self.search_type_choices.Bind( wx.EVT_CHOICE, self.on_type_changed  )
		self.tabs.Bind( wx.EVT_NOTEBOOK_PAGE_CHANGED, self.on_tab_changed )

		bg_color = wx.SystemSettings.GetColour( wx.SYS_COLOUR_3DFACE )
		self.SetBackgroundColour( bg_color )

		self.last_position = self.GetPosition( )
		self.SetDoubleBuffered( False )


	def on_scroll( self, event ):
		"""
		Scroll event binding.

		If double buffering is OFF, we get nasty flickering all the time.
		If double buffering is ON, we get sluggish scrolling.
		So to rectify this, during scroll events we turn OFF double buffering,
		and turn double buffering ON after a slight delay via wxCallLater.

		*Author:*
			* Andrew Dour, andrew.dour@volition-inc.com, 5/18/2012 1:30:00 PM
		"""

		self.lister.SetDoubleBuffered( False )
		wx.CallLater( 500, self.lister.SetDoubleBuffered, True )
		event.Skip( )


	def on_type_changed( self, event ):
		"""
		Handle updating the lister based on the search type changing

		*Arguments:*
			* ``Event`` wx.Choice select event

		*Keyword Arguments:*
			* ``None``

		*Returns:*
			* ``None``

		*Examples:* ::

			Enter code examples here. (optional field)

		*Todo:*
			* Enter thing to do. (optional field)

		*Author:*
			* Randall Hess, randall.hess@volition-inc.com, 9/26/2013 12:18:05 PM
		"""

		doc = AnimationEditor.get_active_document( )
		if not doc:
			return

		success = False

		# set the document search type
		search_type = self.search_type_choices.GetStringSelection( )
		doc.search_type = ctg.ae2.ui.const.AE_SEARCH_TYPES[ search_type ]

		# update the lister
		self.lister.get_refresh_manager( ).post_refresh_request( full_refresh = True, immediate = True )
		self.lister._init_column_collection( )


	def set_status_message( self, msg = None ):
		"""
		Asset Manager Status Bar Updating.
		Handle changing the status bar message.

		*Arguments:*
			* ``None``

		*Keyword Arguments:*
			* ``msg`` String to set the status bar to display

		*Returns:*
			* ``None``

		*Examples:* ::

			Enter code examples here. (optional field)

		*Todo:*
			* Enter thing to do. (optional field)

		*Author:*
			* Randall Hess, randall.hess@volition-inc.com, 10/1/2013 8:27:00 AM
		"""

		if msg:
			self.statusbar.set_status( msg )
		else:
			self.statusbar.clear_status( )


	def on_tab_changed( self, event ):
		"""
		Tab Event binding.
		Handle changing the Asset Managers lister items by node type.

		*Arguments:*
			* ``event`` Wx TabChange event

		*Keyword Arguments:*
			* ``None``

		*Returns:*
			* ``None``

		*Examples:* ::

			Enter code examples here. (optional field)

		*Todo:*
			* Enter thing to do. (optional field)

		*Author:*
			* Randall Hess, randall.hess@volition-inc.com, 10/1/2013 8:26:20 AM
		"""

		doc = AnimationEditor.get_active_document( )
		if not doc:
			return

		tab_id = event.GetSelection( )
		self.lister.set_search_mode( self.tab_filter_dict[ tab_id ] )

		self.set_status_message( )

		event.Skip( )

