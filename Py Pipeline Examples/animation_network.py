
import time
import os
import win32gui
import sys
import inspect
import copy

import wx
import wx.lib.buttons

import GUILib
import AnimationEditor
import param_types

import ctg.callbacks
import ctg.ui.dialogs
import ctg.ui.widgets
import ctg.ui.panel
import ctg.ui.util
import ctg.prefs

import ctg.ae2.core.input

import ctg.ae2.ui.const
import ctg.ae2.ui.dialogs
import ctg.ae2.ui.lister
import ctg.ae2.ui.node

import vlib.ui.lister_lib
import vlib.ui.lister_lib.node
import vlib.ui.widgets.slider

CMD_ID_RENAME							= wx.NewId()
CMD_ID_DELETE							= wx.NewId()
CMD_ID_CREATE_NEW						= wx.NewId()
CMD_ID_CREATE_NEW_BLEND_TREE		= wx.NewId()
CMD_ID_CREATE_NEW_STATE_MACHINE	= wx.NewId()

DEBUG 					= False
DEBUG_SELECTION 		= True

FLOAT_DATA_TYPE 	= 'float'
INT_DATA_TYPE 		= 'int'
BOOL_DATA_TYPE 	= 'bool'
ANGLE_DATA_TYPE	= 'angle'
STRING_CRC_DATA_TYPE = 'string_crc'


def build_control_dict( ):
	"""
	build a dictionary of valid control objects

	*Returns:*
		* ``control_dict`` dictionary of controls objects and operation strings

	*Author:*
		* Jon Logsdon, jon.logsdon@dsvolition.com
	"""

	doc = AnimationEditor.get_active_document()
	if not doc:
		return

	control_dict = {
	   'create_new'					: ctg.ae2.ui.dialogs.Generic_Text_Control( ),
	   'create_new_blend_tree'		: ctg.ae2.ui.dialogs.Generic_Text_Control( ),
	   'create_new_state_machine'	: ctg.ae2.ui.dialogs.Generic_Text_Control( ),
	   'delete'							: ctg.ae2.ui.dialogs.Generic_Label_Control( ),
	   'rename'							: ctg.ae2.ui.dialogs.Generic_Text_Control( )
	}

	return control_dict



class Floater_Dialog( vlib.ui.lister_lib.core.Floater_Input_Dialog_Base ):
	"""
	Floating Dialog to handle context menu operations

	*Author:*
		* Jon Logsdon, jon.logsdon@dsvolition.com
	"""


	def __init__( self, parent, id_string, display_name, label_text, position, node_type_id, data_obj = None, filter_type = None):
		"""
		Setup the floating dialog

		*Arguments:*
			* ``parent`` Parent of the floating dialog
			* ``id_string`` Identifier for the operation the dialog with handle
			* ``display_name`` String that will be displayed on the dialog
			* ``label_text``   String the will be diplayed on the dialog label
			* ``position``     Where the dialog should be positioned
			* ``node_type_id`` Identifier for the given node

		*Keyword Arguments:*
			* ``data_obj``    The data that the dialog will operate on
			* ``filter_type`` The filtering identifier

		*Author:*
			* Jon Logsdon, jon.logsdon@dsvolition.com
		"""

		self.display_name 	= display_name
		self.label_text 		= label_text
		self.control 			= build_control_dict()[ id_string ]
		self.id_string 		= id_string
		self.node_type_id 	= node_type_id
		self.grid 				= parent
		self.filter_type 		= filter_type
		self.data_obj 			= data_obj

		vlib.ui.lister_lib.core.Floater_Input_Dialog_Base.__init__( self, parent, position )

		self.disable_editor_window( True )


	def set_initial_value( self ):
		"""
		Set the initial value for the control being created

		*Arguments:*
			* ``event`` Ok button pressed event

		*Author:*
			* Jon Logsdon, jon.logsdon@dsvolition.com
		"""
		if isinstance( self.ctrl, wx.StaticText ):
			self.ctrl.SetLabelText( self.display_name )
		else:
			self.ctrl.SetValue( self.display_name )


	def setup_controls( self ):
		"""
		Handle setting up the controls for the dialog

		*Author:*
			* Jon Logsdon, jon.logsdon@dsvolition.com
		"""

		if self.id_string == 'delete':
			self.ctrl = self.control.create_control( self, self.display_name )
		else:
			self.ctrl = self.control.create_control( self )


		label = wx.StaticText( self, -1, self.label_text )
		self.error_label = wx.StaticText( self, -1, 'Name is too long ( max length {0} )'.format( ctg.ae2.ui.const.MAX_NAME_LENGTH )  )
		self.error_label.Show( False )

		label.SetFont( wx.Font( 8, 70, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, wx.EmptyString ) )
		self.sizer_inner.Add( label, 0, wx.EXPAND | wx.ALL, 4 )
		self.sizer_inner.Add( self.error_label, 0, wx.EXPAND | wx.ALL, 4 )
		self.sizer_inner.Add( self.ctrl, 1, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 2 )


		self.set_initial_value()


	def on_ok_pressed( self, event ):
		"""
		Handle the operation when ok button is pressed

		*Arguments:*
			* ``event`` Ok button pressed event

		*Author:*
			* Jon Logsdon, jon.logsdon@dsvolition.com
		"""

		destroy_dialog = True
		if isinstance( self.ctrl, wx.StaticText ):
			val = self.ctrl.GetLabelText()
		else:
			val = self.ctrl.GetValue( )

		if self.id_string == 'delete':
			self.grid.delete( self.data_obj )
		else:

			if len( val ) <= ctg.ae2.ui.const.MAX_NAME_LENGTH:
				if self.id_string == 'create_new_blend_tree':
					self.grid.create( ctg.ae2.ui.const.NODE_TYPE_BLEND_TREE, val )

				elif self.id_string == 'create_new_state_machine':
					self.grid.create( ctg.ae2.ui.const.NODE_TYPE_STATE_MACHINE, val )

				elif self.id_string == 'rename':
					self.grid.rename( self.data_obj, val )

			else:
				self.error_label.Show( True )
				self.sizer_inner.Layout( )
				self.sizer.Layout( )
				self.SetSize( ( -1, 124 ))
				self.Layout( )
				self.Refresh( )

				destroy_dialog = False

		if destroy_dialog:
			self.disable_editor_window( False )
			self.Show( False )
			self.Destroy( )


	def on_cancel_pressed( self, event ):
		"""
		Handle the operation when cancel button is pressed

		*Arguments:*
			* ``event`` Cancel button pressed event

		*Author:*
			* Jon Logsdon, jon.logsdon@dsvolition.com
		"""
		self.disable_editor_window( False )
		self.Show( False )
		self.Destroy( )


	def disable_editor_window( self, value ):
		"""
		Disable the editor when the dialog is active, modal

		*Arguments:*
			* ``value`` Boolean to put the editor in modal mode

		*Author:*
			* Jon Logsdon, jon.logsdon@dsvolition.com
		"""
		ctg.ui.util.set_editor_modal( value )



class Context_Menu( wx.Menu ):
	"""
	Context menu for the Node Graph Tree

	*Author:*
		* Jon Logsdon, jon.logsdon@dsvolition.com
	"""

	def __init__( self, grid, column, row, menu_title, grid_cell_found, node_type_id ):
		"""
		Setup the context menu for the Node Graph Tree

		*Arguments:*
			* ``grid``            ListerLib grid
			* ``column``          Active column in the grid
			* ``row``             Active row in the grid
			* ``menu_title``      Title string that the menu will be given
			* ``grid_cell_found`` Bool if a grid cell is active
			* ``node_type_id``    Identifier for the node type

		*Author:*
			* Jon Logsdon, jon.logsdon@dsvolition.com
		"""

		wx.Menu.__init__( self )
		self.grid 				= grid
		self.data_obj			= None
		self.menu_title 		= menu_title
		self.node_type_id 	= node_type_id

		if grid_cell_found:
			# set the label
			self.label = self.grid.get_column_collection( ).column_order[ column ].label

			# set the display name
			if row >= 0:
				self.data_obj = self.grid.get_row_as_node( row ).get_data_obj( )
				if self.data_obj:
					self.display_name = self.data_obj.get_name( )

			# node types that can have valid operations
			valid_node_types = [ ctg.ae2.ui.const.NODE_TYPE_STATE_MACHINE, ctg.ae2.ui.const.NODE_TYPE_BLEND_TREE ]

			if self.node_type_id in valid_node_types:
				item = wx.MenuItem( self, CMD_ID_RENAME, u'Rename', wx.EmptyString, wx.ITEM_NORMAL )
				item.SetBitmap( ctg.ui.util.get_project_image( 'editAttributes_16.png', as_bitmap = True ), wx.BITMAP_TYPE_ANY )
				item.Enable( True )
				self.AppendItem( item )

				item = wx.MenuItem( self, CMD_ID_DELETE, u'Delete', wx.EmptyString, wx.ITEM_NORMAL )
				item.SetBitmap( ctg.ui.util.get_project_image( 'outliner_objset_delete_16.png', as_bitmap = True ), wx.BITMAP_TYPE_ANY )
				item.Enable( True )
				self.AppendItem( item )

				self.AppendSeparator( )

		# Create Menu Items
		item = wx.MenuItem( self, CMD_ID_CREATE_NEW_BLEND_TREE, u'Create Blend Tree', wx.EmptyString, wx.ITEM_NORMAL )
		item.SetBitmap( ctg.ui.util.get_project_image( 'outliner_objset_add_16.png', as_bitmap = True ), wx.BITMAP_TYPE_ANY )
		self.AppendItem( item )

		item = wx.MenuItem( self, CMD_ID_CREATE_NEW_STATE_MACHINE, u'Create State Machine', wx.EmptyString, wx.ITEM_NORMAL )
		item.SetBitmap( ctg.ui.util.get_project_image( 'outliner_objset_add_16.png', as_bitmap = True ), wx.BITMAP_TYPE_ANY )
		self.AppendItem( item )

		# Set the Menu Title
		if self.GetMenuItemCount( ) > 0:
			self.SetTitle( self.menu_title )

		self.Bind( wx.EVT_MENU_RANGE, self.on_colum_context )


	def on_colum_context( self, event ):
		"""
		Handle the selected context menu selection
		- This may mean creating an additonal floater dialog for creation or renaming

		*Arguments:*
			* ``event`` Context menu selection event

		*Author:*
			* Jon Logsdon, jon.logsdon@dsvolition.com
		"""

		sender = event.GetId( )

		# Create New
		if sender == CMD_ID_CREATE_NEW_BLEND_TREE:
			win = Floater_Dialog( self.grid, 'create_new_blend_tree', 'New Blend Tree', 'Create New Blend Tree', wx.GetMouseState( ).GetPosition( ), self.node_type_id )
			win.Show()

		elif sender == CMD_ID_CREATE_NEW_STATE_MACHINE:
			win = Floater_Dialog( self.grid, 'create_new_state_machine', 'New State Machine', 'Create New State Machine', wx.GetMouseState( ).GetPosition( ), self.node_type_id )
			win.Show()

		# Rename
		elif sender == CMD_ID_RENAME:
			win = Floater_Dialog( self.grid, 'rename', self.display_name,'Rename {0}'.format( self.menu_title ), wx.GetMouseState( ).GetPosition( ), self.node_type_id, data_obj = self.data_obj )
			win.Show()

		# Delete
		elif sender == CMD_ID_DELETE:
			win = Floater_Dialog( self.grid, 'delete', self.display_name , 'Delete {0}'.format( self.menu_title ), wx.GetMouseState( ).GetPosition( ), self.node_type_id, data_obj = self.data_obj )
			win.Show()

		else:
			pass



class Filter_Bookmarked_Nodes( vlib.ui.lister_lib.filter.Node_Filter ):
	"""
	ListerLib -
	Custom Filter, that will display a list of nodes and ensure children and parent nodes will be displayed

	*Author:*
		* Jon Logsdon, jon.logsdon@dsvolition.com
	"""

	def __init__( self, grid ):
		"""
		Setup the bookmark filter

		*Arguments:*
			* ``grid`` The lister that will be filtered

		*Author:*
			* Jon Logsdon, jon.logsdon@dsvolition.com
		"""

		vlib.ui.lister_lib.filter.Node_Filter.__init__( self, node_types = [ ctg.ae2.ui.const.NODE_TYPE_NODE_GRAPH, ] )
																								#ctg.ae2.ui.const.NODE_TYPE_NODE_GRAPH_TREE_ITEM,
													#ctg.ae2.ui.const.NODE_TYPE_STATE_MACHINE,
													#ctg.ae2.ui.const.NODE_TYPE_BLEND_TREE,
													#ctg.ae2.ui.const.NODE_TYPE_ANIM_CLIP,
													#ctg.ae2.ui.const.NODE_TYPE_ANIM_ACTION,
													#ctg.ae2.ui.const.NODE_TYPE_ANIM_STATE,
													#ctg.ae2.ui.const.NODE_TYPE_CONTROL_FILTER,
													#ctg.ae2.ui.const.NODE_TYPE_CONTROL_PARAMETER,] )
		self.grid = grid


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
			* Jon Logsdon, jon.logsdon@dsvolition.com
		"""

		# make sure this is a valid node type
		node_type = node.get_node_type( )
		valid_node_types = self.get_node_types( )
		if ( not valid_node_types ) or ( node_type in self.get_node_types( ) ):

			# see if the obj name matches an active bookmark
			data_obj = node.get_data_obj( )
			if data_obj:
				if data_obj.get_name( ) in self.grid.active_bookmarks:
					return True
				else:
					return False

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
			* Jon Logsdon, jon.logsdon@dsvolition.com
		"""

		# make sure this is a valid node type
		node_type = node.get_node_type( )
		valid_node_types = self.get_node_types( )
		if ( not valid_node_types ) or ( node_type in self.get_node_types( ) ):

			# only check this if bookmarks are active
			if not self.grid.active_bookmarks is None:

				# Check the string value on the node itself first
				node_valid = self.check_value( node )
				if node_valid:
					#node.set_expanded_recursive( True )
					return True

				# Check any recursive children node names if they have the string then this node is valid
				children = node.get_children_recursive( )
				if len( children ) > 0:
					for child in children:
						valid = self.check_value( child )
						if valid:
							return True

				# Check any recursive parent node names if they have the string then this node is valid
				parents = node.get_parents_recursive( )
				if len( parents ) > 0:
					for parent in parents:
						valid = self.check_value( parent )
						if valid:
							return True

				return False

			else:
				return True

		return True



class Filter_Node_Graph_String_Value( ctg.vlib.ui.lister_lib.filter.Node_Filter ):
	"""
	ListerLib -
	Custom String Filter, that will ensure children and parent nodes will be displayed

	*Author:*
		* Jon Logsdon, jon.logsdon@dsvolition.com
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
			* Jon Logsdon, jon.logsdon@dsvolition.com
		"""

		ctg.vlib.ui.lister_lib.filter.Node_Filter.__init__( self, **kwargs )
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
			* Jon Logsdon, jon.logsdon@dsvolition.com
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
			* Jon Logsdon, jon.logsdon@dsvolition.com
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
			* Jon Logsdon, jon.logsdon@dsvolition.com
		"""

		node_type = node.get_node_type( )
		valid_node_types = self.get_node_types( )
		if ( not valid_node_types ) or ( node_type in self.get_node_types( ) ):

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
			* Jon Logsdon, jon.logsdon@dsvolition.com
		"""

		# Make sure our string isn't empty
		if self.val:

			node_type = node.get_node_type( )
			valid_node_types = self.get_node_types( )
			if ( not valid_node_types ) or ( node_type in self.get_node_types( ) ):

				# Check the string value on the node itself first
				valid = self.check_value( node )
				if valid:
					return valid

				# Check any recursive children node names if they have the string then this node is valid
				children = node.get_children_recursive( )
				if len( children ) > 0:
					for child in children:
						valid = self.check_value( child )
						if valid:
							return True

				# Check any recursive parent node names if they have the string then this node is valid
				if node.has_parent( ):
					for parent in node.get_parents_recursive( ):
						valid = self.check_value( parent )
						if valid:
							return True

				return False

		return True



#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# Main UI - Lister/Tree
#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
class Node_Graph_Filter_Manager( vlib.ui.lister_lib.filter.Node_Filter_Manager ):
	"""
	ListerLib filter manager
	Handles displaying lister nodes using various filters

	*Author:*
		* Jon Logsdon, jon.logsdon@dsvolition.com
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
			* Jon Logsdon, jon.logsdon@dsvolition.com
		"""

		vlib.ui.lister_lib.filter.Node_Filter_Manager.__init__( self, grid, filters, string_filter )

		# Set the node_types for the String Filter
		self.get_string_filter( ).set_node_types( [ ctg.ae2.ui.const.NODE_TYPE_NODE_GRAPH, ] )
										#ctg.ae2.ui.const.NODE_TYPE_NODE_GRAPH_TREE_ITEM,
										#ctg.ae2.ui.const.NODE_TYPE_STATE_MACHINE,
										#ctg.ae2.ui.const.NODE_TYPE_BLEND_TREE,
										#ctg.ae2.ui.const.NODE_TYPE_ANIM_CLIP,
										#ctg.ae2.ui.const.NODE_TYPE_ANIM_ACTION,
										#ctg.ae2.ui.const.NODE_TYPE_ANIM_STATE,
										#ctg.ae2.ui.const.NODE_TYPE_CONTROL_FILTER,
										#ctg.ae2.ui.const.NODE_TYPE_CONTROL_PARAMETER] )


	def is_active( self ):
		"""
		Method to determine if the filter is active

		*Returns:*
			* ``Bool`` If the filter is active

		*Author:*
			* Jon Logsdon, jon.logsdon@dsvolition.com
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
			* Jon Logsdon, jon.logsdon@dsvolition.com
		"""

		try:
			for node_filter in self.filters:
				if not node_filter.can_display_node( node ):
					return False

			return True

		except TypeError:
			# Object has been deleted
			return False



class Column_Name( vlib.ui.lister_lib.column.Column ):
	"""
	Column object for the node graph tree

	*Author:*
		* Jon Logsdon, jon.logsdon@dsvolition.com
	"""

	def __init__( self ):
		"""
		Construct the column

		*Author:*
			* Jon Logsdon, jon.logsdon@dsvolition.com
		"""

		vlib.ui.lister_lib.column.Column.__init__( self, 'Name', 'id_name', param_types.STRING, can_hide = False, can_move = False, is_shown = True )


	def get_value( self, node ):
		"""
		Return the value of the node in this column

		*Arguments:*
			* ``none`` Listerlib node

		*Returns:*
			* ``string`` The display name of the node

		*Author:*
			* Jon Logsdon, jon.logsdon@dsvolition.com
		"""

		return node.display_name



class Node_Graph_Tree( ctg.ae2.ui.lister.Anim_Tree ):
	"""
	ListerLib -
	A lister lib tree grid
	A hierarchy view of node graphs( state machines and blend trees )

	*Author:*
		* Jon Logsdon, jon.logsdon@dsvolition.com
	"""

	def __init__( self, parent ):
		"""
		Construct the ListerLib Node Graph Tree

		*Arguments:*
			* ``parent`` Pane that will contain this lister

		*Author:*
			* Jon Logsdon, jon.logsdon@dsvolition.com
		"""

		self.selected_items				= [ ]
		self.is_tree						= True
		self.show_tree_connections		= True
		self.expand_margin				= True
		self.node_type_id					= None
		self.active_bookmarks 			= None
		self.active_event_objs			= None

		ctg.ae2.ui.lister.Anim_Tree.__init__( self, parent,
		                                      draggable_columns = False,
		                                      show_column_headers = False,
		                                      adjustable_columns = False,
		                                      multi_row_select = True,
		                                      )

		self.button_items = ctg.ae2.ui.node.Node_Button_Node_Graph_Type( )
		self._node_buttons = [ vlib.ui.lister_lib.node.Node_Button_Expand( ), ctg.ae2.ui.node.Node_Button_Node_Graph_Type( ), ] #ctg.ae2.ui.node.Node_Button_Active( ), ]

		self.refresh_manager = self.get_refresh_manager( )
		self.get_node_filter_manager( ).get_string_filter( ).set_node_types( [ ctg.ae2.ui.const.NODE_TYPE_NODE_GRAPH ] )

		# bind node graph load events
		self.Bind( ctg.ae2.ui.events.EVT_AE_BLEND_TREE_LOAD,		self.on_blend_tree_load )
		self.Bind( ctg.ae2.ui.events.EVT_AE_STATE_MACHINE_LOAD,	self.on_state_machine_load )

		self.GetGridWindow( ).Bind( wx.EVT_RIGHT_DOWN, self.on_grid_window_context_menu )


	def _init_node_filter_manager( self ):
		"""
		ListerLib -
		Setup the ListerLib filter manager

		*Author:*
			* Jon Logsdon, jon.logsdon@dsvolition.com
		"""
		self._node_filter_manager = Node_Graph_Filter_Manager( self, filters = [ Filter_Bookmarked_Nodes( self ) ], string_filter = Filter_Node_Graph_String_Value( ) )


	def _init_root_node( self ):
		"""
		ListerLib -
		Setup the ListerLib root_node

		*Author:*
			* Jon Logsdon, jon.logsdon@dsvolition.com
		"""

		self._root_node = ctg.ae2.ui.node.Anim_Node_Generic( None, ctg.ae2.ui.const.NODE_TYPE_ROOT, None, expanded = True )


	def _init_column_collection( self ):
		"""
		ListerLib
		Setup the column collection for the lister

		*Author:*
			* Jon Logsdon, jon.logsdon@dsvolition.com
		"""

		name_column = Column_Name( )

		# Create our collection
		self._column_collection = vlib.ui.lister_lib.column.Column_Collection( [ name_column ], grid = self )
		self._column_collection.sort_column		= self._column_collection.sort_column_default = name_column


	def _collect_item_dependencies( self, doc, item, parent,	item_node = None, visit_list = [] ):
		"""
		Recursive method called when collecting node graph tree items

		*Arguments:*
			* ``doc`` Active Animation Editor document
			* ``item`` Current data_obj that we are collecting children for
			* ``parent`` Node that will be the parent of the current item_node we are creating

		*Keyword Arguments:*
			* ``item_node`` If this is being passed in will we use that node instead of generating one from the item

		*Author:*
			* Jon Logsdon, jon.logsdon@dsvolition.com
		"""

		if doc.is_node_graph( item.get_name( ) ):

			# create the node
			if not item_node:
				item_node = ctg.ae2.ui.node.Node_Graph_Node( parent, ctg.ae2.ui.const.NODE_TYPE_NODE_GRAPH, item, display_name = item.get_name( ), expanded = False )

				# see if the new item node is not a root node,
				# make sure an item with the same name doesn't exist as a root node
				#if not parent is self._root_node:
					## remove the root node with the same name that exists in the root of the tree
					#root_item = doc.node_graph_tree_collection.get_item_by_name( item.get_name( ) )
					#if root_item:
						#self.refresh_grid()
						#root_item_node = self._node_collection.get_data_obj_as_node( root_item )
						#if root_item_node:
							#self.get_refresh_manager( ).add_delete_event( [ root_item_node ] )

			# update the item dependents( child node graphs )
			if item.dependency_graphs_collection is None or item.dependency_graphs_collection.is_dirty:
				item.get_dependency_graphs( )
				item.dependency_graphs_collection.is_dirty = False

			# create dependent nodes (and check for loops)
			for dep in item.dependency_graphs_collection.get_items( ):
				if dep:
					if dep.name in visit_list:
						dlg = wx.MessageDialog( None, "Dependency loop detectected in graph '" + item.name + "'. Please fix.", caption = "Error", style = wx.OK )
						ctg.ui.dialogs.show_dialog_modal( dlg )
						dlg.Destroy( )
					else:
						# make a copy so we don't modify the list further up (because multiple nodes can reference the same child graph).
						copy_visit_list = copy.copy( visit_list )
						copy_visit_list.append( item.name )
						self._collect_item_dependencies( doc, dep, item_node, visit_list = copy_visit_list )

			# update the item dependencies( node graphs, clips, tags, control parameters, control filters )
			if item.dependency_items_collection is None or item.dependency_items_collection.is_dirty:
				item.get_dependency_items( )
				item.dependency_items_collection.is_dirty = False

			# create item dependency nodes
			for child in item.dependency_items_collection.get_items( ):
				if child:
					child_node = ctg.ae2.ui.node.Node_Graph_Node( item_node, child.get_data_obj( ).get_node_type( ), child, display_name = child.get_data_obj( ).get_name( ), expanded = False )


	def collect_objects( self ):
		"""
		ListerLib -
		Main method to create all the lister nodes derived from data_objects
		Populate the lister grid

		*Author:*
			* Jon Logsdon, jon.logsdon@dsvolition.com
		"""

		doc = AnimationEditor.get_active_document( )
		if not doc:
			return None

		root_node = self.get_root_node( )

		# Only update if the collections have been modified
		if doc.node_graph_tree_collection.is_dirty:

			# reset the dirty flag
			doc.node_graph_tree_collection.is_dirty = False

			# kill all root_node children
			root_node.destroy_children( notify = False )

			root_nodes = 0
			for item in doc.node_graph_tree_collection.get_items( ):
				# get the item/data_obj dependencies
				self._collect_item_dependencies( doc, item, root_node )
				root_nodes += 1

			#print 'Root Nodes: {0}'.format( len( root_node.child_nodes ) )

			root_node.sort_children_recursive( )
			self.update_grid_object_collection( )

		return self.grid_object_collection


	def on_cell_selected( self, event ):
		"""
		ListerLib -
		Process cell select/click.

		*Author:*
			* Jon Logsdon, jon.logsdon@dsvolition.com
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

			if shift_down == True:
				nodes.extend( self.get_selected_nodes( ) )
				nodes = list( set( nodes ) )

			did_click = False

			for node_button in self.get_registered_node_buttons( ):
				if node_button.can_draw( self, node, row, col ):
					did_click = node_button.on_click( self, wx.Rect( *full_rect ), node, click_pos, nodes )
					if did_click == True:
						break

			if did_click != True:
				if shift_down == True:
					self.select_range( current_pos, row, add_to_selection = ctrl_down, post_event = False, visible_only = True )

				elif ( ctrl_down == True ) and ( is_selected == True ):
					self.DeselectRow( row )
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


	def load_node_graph( self, data_obj ):
		"""
		Load the node graph of the given data_obj

		*Arguments:*
			* ``data_obj`` ListerLib node graph item( StateMachine Item or BlendTree Item )

		*Keyword Arguments:*
			* ``None``

		*Returns:*
			* ``None``

		*Examples:* ::

			Enter code examples here. (optional field)

		*Todo:*
			* Enter thing to do. (optional field)

		*Author:*
			* Jon Logsdon, jon.logsdon@dsvolition.com
		"""
		doc = AnimationEditor.get_active_document( )
		if not doc:
			return

		# handle refreshing the grid
		refresh = True

		# post load state machine event
		if isinstance( data_obj, ctg.ae2.core.data.State_Machine_Item ):
			doc.event_manager.post_state_machine_load_event( [ data_obj ], owner = ctg.ae2.ui.const.PANE_ID_NODE_GRAPH_TREE )

		# post load blend tree event
		elif isinstance( data_obj, ctg.ae2.core.data.Blend_Tree_Item ):
			doc.event_manager.post_blend_tree_load_event( [ data_obj ], owner = ctg.ae2.ui.const.PANE_ID_NODE_GRAPH_TREE )

		else:
			refresh = False

		if refresh:
			self.refresh_manager.post_refresh_request( full_refresh = False, immediate = True )


	def on_key_down( self, event ):

		key = event.GetKeyCode( )

		if ( key == wx.WXK_RETURN ):
			selected_node = None
			selected_nodes = self.get_selected_nodes( )
			if selected_nodes:
				if issubclass( selected_nodes[ 0 ].__class__, vlib.ui.lister_lib.node.Node ):
					selected_node = selected_nodes[ 0 ]

			if selected_node:
				data_obj = self.get_node_as_data_obj( selected_node )

				# since the top level data_obj is just a container for the real data_obj
				r_data_obj = data_obj.get_data_obj( )
				self.load_node_graph( r_data_obj )

		super(Node_Graph_Tree, self).on_key_down( event )


	def on_cell_double_click( self, event ):
		"""
		Handle selection and loading of a node graph when double-clicking a node

		*Arguments:*
			* ``event`` Double-click event

		*Author:*
			* Jon Logsdon, jon.logsdon@dsvolition.com
		"""
		col = event.GetCol( )
		row = event.GetRow( )

		# Skip event only if we have an editor for this column
		column_object = self.get_column_collection( ).column_order[ col ]

		node = self.get_row_as_node( row )
		if node:
			data_obj = self.get_node_as_data_obj( node )

			# since the top level data_obj is just a container for the real data_obj
			r_data_obj = data_obj.get_data_obj( )
			self.load_node_graph( r_data_obj )

		has_editor = False
		if column_object and column_object.data_type != param_types.BOOL:
			has_editor = bool( column_object.get_column_editor( ) )

		event.Skip( has_editor )


	def on_cell_context_menu( self, event ):
		"""
		ListerLib -
		Create a context window when right-clicking on a grid cell

		*Arguments:*
			* ``event`` right-click event on a background

		*Author:*
			* Jon Logsdon, jon.logsdon@dsvolition.com
		"""
		col = event.GetCol( )
		row = event.GetRow( )

		# update the selection on right-click
		node = self.get_row_as_node( row )
		if node:
			data_obj = node.get_data_obj( )
			if self.selected_items != [data_obj]:
				self.post_item_select_event( [ node.get_data_obj( ) ] )
				self.restore_selection( True )

			# get the selected node and type to pass into the menu
			node_name = node.get_data_obj( ).get_name( )
			node_type = node.get_data_obj( ).get_data_obj( ).get_node_type( )
			menu = Context_Menu( self, col, row, node_name, True, node_type )
			self.PopupMenu( menu )
			menu.Destroy( )


	def on_grid_window_context_menu( self, event ):
		"""
		ListerLib -
		Create a context window when not right-clicking on a grid cell

		*Arguments:*
			* ``event`` right-click event on a background

		*Todo:*
			* Enable the menu

		*Author:*
			* Jon Logsdon, jon.logsdon@dsvolition.com
		"""

		row, col = self.hit_test( event.GetX(), event.GetY() )
		node_type_name = 'Node Graph'

		if row < 0 or col < 0:
			menu = Context_Menu( self, col, row, node_type_name, False, self.node_type_id )
			self.PopupMenu( menu )
			menu.Destroy( )

		event.Skip( )


	def select_active_bookmarks( self ):
		"""
		Called externally to the lister this will select nodes with the active bookmark names

		*Author:*
			* Jon Logsdon, jon.logsdon@dsvolition.com
		"""

		#get data_objs from name list
		if self.active_bookmarks:
			if len( self.active_bookmarks ) > 0:

				# get the data_objs with the bookmark names
				nodes = self.get_node_collection( ).nodes
				data_objs = self.get_nodes_as_data_objs( nodes )
				new_selection = [ data_obj for data_obj in data_objs if data_obj.get_name( ) in self.active_bookmarks ]

				# set the lister selection
				if len( new_selection ) > 0:

					# override current selection
					self.selected_items = new_selection

					# expand relevant nodes
					nodes = self.get_node_collection( ).get_data_objs_as_nodes( self.selected_items )
					for node in nodes:
						node.set_expanded( True )
						for parent in node.get_parents_recursive( ):
							parent.set_expanded( True )

					# select the nodes
					self.select_nodes( nodes, post_event = False )

					# update the properties pane
					doc = AnimationEditor.get_active_document( )
					doc.event_manager.update_sel_obj_and_prop_pane( self.selected_items )

		# update the lister
		self.refresh_manager.filter_changed = True
		self.refresh_manager.post_refresh_request( full_refresh = False, immediate = True )


	def refresh_grid( self ):
		"""
		Post a full refresh call to the lister.
		Collect all objects agains

		*Author:*
			* Jon Logsdon, jon.logsdon@dsvolition.com
		"""

		self.refresh_manager.post_refresh_request( full_refresh = True, immediate = True )


	def create( self, node_type_id, name ):
		"""
		Handle creating a new Blend Tree or State Machine from the context menu

		*Arguments:*
			* ``node_type_id`` Type of Node Graph to Create
			* ``name``			 Name of the Node Graph

		*Author:*
			* Jon Logsdon, jon.logsdon@dsvolition.com
		"""
		doc = AnimationEditor.get_active_document( )
		if not doc:
			return

		# create a new blend tree
		if node_type_id == ctg.ae2.ui.const.NODE_TYPE_BLEND_TREE:
			doc.blend_tree_collection.create( new_name = name )

		# create a new state machine
		elif node_type_id == ctg.ae2.ui.const.NODE_TYPE_STATE_MACHINE:
			doc.state_machine_collection.create( new_name = name )


	def delete( self, data_obj ):
		"""
		Handle deleting a data_obj from the context menu

		*Arguments:*
			* ``data_obj`` The Node Graph Tree Item that is being deleted

		*Keyword Arguments:*
			* ``Argument`` Enter a description for the keyword argument here.

		*Author:*
			* Jon Logsdon, jon.logsdon@dsvolition.com
		"""
		doc = AnimationEditor.get_active_document( )
		if not doc:
			return

		# get the real data_obj from the Node_Graph_Tree_Item
		r_data_obj = data_obj.get_data_obj( )
		if r_data_obj:
			successful 	= r_data_obj.delete( )


	def rename( self, data_obj, new_name ):
		"""
		Handle renaming data_obj from the context menu

		*Arguments:*
			* ``data_obj`` The Node Graph Tree Item that is being renamed
			* ``new_name`` The string that will be the new name for the data_obj

		*Keyword Arguments:*
			* ``Argument`` Enter a description for the keyword argument here.

		*Author:*
			* Jon Logsdon, jon.logsdon@dsvolition.com
		"""
		doc = AnimationEditor.get_active_document( )
		if not doc:
			return

		if doc.node_graph_panel.blend_tree != None:
			errors = doc.node_graph_panel.blend_tree.save_and_export()
			if errors != '':
				dlg = wx.MessageDialog( self, 'Graph contains export errors "{0}" stoping rename.'.format( doc.node_graph_panel.blend_tree_name ), 'Error', wx.OK | wx.ICON_INFORMATION )
				dlg.ShowModal()
				dlg.Destroy()
				return


		if doc.node_graph_panel.state_machine != None:
			errors = doc.node_graph_panel.state_machine.save_and_export()
			if errors != '':
				dlg = wx.MessageDialog( self, 'Graph contains export errors "{0}" stoping rename.'.format( doc.node_graph_panel.state_machine_name ), 'Error', wx.OK | wx.ICON_INFORMATION )
				dlg.ShowModal()
				dlg.Destroy()
				return


		# get the real data_obj from the Node_Graph_Tree_Item
		r_data_obj = data_obj.get_data_obj( )
		if r_data_obj:
			successful 	= r_data_obj.rename( new_name )


	def print_selection( self, data_obj ):
		"""
		Print the dependents of the selected node graph.  This is
		for debugging purposes.

		*Arguments:*
			* ``data_obj`` The selected node graph item

		*Keyword Arguments:*
			* ``Argument`` Enter a description for the keyword argument here.

		*Returns:*
			* ``Value`` If any, enter a description for the return value here.

		*Author:*
			* Jon Logsdon, jon.logsdon@dsvolition.com
		"""

		doc = AnimationEditor.get_active_document( )
		if not doc:
			return

		# print hierarchy details on the selected node graph
		if DEBUG_SELECTION:
			node_graph_name = data_obj.get_name( )

			# print dependents
			if doc.is_node_graph( node_graph_name ):

				# doc.is_node_graph is crashing still doing this just in case
				if node_graph_name in doc.get_node_graph_names( ):

					dependents = doc.get_node_graph_dependents( ctg.ae2.ui.const.NODE_GRAPH_DEPENDENCIES[ "type" ], node_graph_name )
					print( 'Selection Dependents: {0}'.format( dependents ) )

					# print dependencies
					node_graph = doc.get_node_graph( node_graph_name )
					if node_graph:
						dependency_list = [ ]

						# node graph dependencies
						ng_dependencies = node_graph.get_dependencies( ctg.ae2.ui.const.NODE_GRAPH_DEPENDENCIES[ "type" ] )
						if ng_dependencies:
							dependency_list.extend( list( ng_dependencies ) )

						# all other dependencies
						dependencies = [ ]
						for dependency in ctg.ae2.ui.const.DEPENDENCY_TYPES:
							dependency_names = node_graph.get_dependencies( dependency[ 'type' ] )
							if dependency_names:
								dependencies.extend( list( dependency_names ) )

						if dependencies:
							dependency_list.extend( dependencies )

						if dependency_list:
							dependency_list = list( set( dependency_list ) )
							dependency_list.sort( )
							print( 'Selection Dependencies: {0}'.format( dependency_list ) )
						else:
							print( 'Selection Dependencies: []' )



	def on_selection_changed( self, event ):
		"""
		ListerLib - Handle selections changing

		*Arguments:*
			* ``event`` selection event

		*Author:*
			* Jon Logsdon, jon.logsdon@dsvolition.com
		"""
		data_objs = self.get_selected_data_objs( )
		if data_objs:
			self.post_item_select_event( data_objs )

		event.Skip( )


	def post_item_select_event( self, data_objs ):
		"""
		Handle selections changing

		*Arguments:*
			* ``event`` selection event

		*Author:*
			* Jon Logsdon, jon.logsdon@dsvolition.com
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		if data_objs:

			# only post an event if the items are different
			if data_objs != self.selected_items:
				self.selected_items = data_objs

				refresh = True
				self.refresh_manager.filter_changed = False

				# get the real data objs
				r_data_objs = [ ]
				for data_obj in data_objs:
					r_data_obj = data_obj.get_data_obj( )
					if not r_data_obj in r_data_objs:
						r_data_objs.append( r_data_obj )

				# post selection event
				if isinstance( r_data_objs[0], ctg.ae2.core.data.State_Machine_Item ):
					doc.event_manager.post_state_machine_select_event( r_data_objs )

				elif isinstance( r_data_objs[0], ctg.ae2.core.data.Blend_Tree_Item ):
					doc.event_manager.post_blend_tree_select_event( r_data_objs )

				else:
					# make sure we aren't playing clips before selecting clips
					doc.preview_pane.on_stop( None )
					# update properties pane
					doc.event_manager.update_sel_obj_and_prop_pane( r_data_objs )
					refresh = False

				# update the grid
				if refresh:

					# expand the selected nodes
					nodes = self.get_data_objs_as_nodes( data_objs )
					for node in nodes:
						# rebuild the node
						if not node.is_expanded( ):
							node.set_expanded( True )
							self.refresh_manager.filter_changed = True

					# update the table
					if self.refresh_manager.filter_changed:
						self.refresh_manager.post_refresh_request( full_refresh = False, immediate = True )


	def restore_selection( self, post_event = False ):
		"""
		ListerLib -
		After the lister has been updated the selection may have been lost due to nodes changing
		This will be called afterwards to re-select the proper nodes

		*Keyword Arguments:*
			* ``post_event`` Will an event need to be posted

		*Author:*
			* Jon Logsdon, jon.logsdon@dsvolition.com
		"""

		# select data_objs passed through an event that needed to refresh the node_collection
		if self.active_event_objs:
			self.select_node_graphs( self.active_event_objs )
			self.active_event_objs = None

		elif self.selected_items:
			nodes = self.get_node_collection( ).get_data_objs_as_nodes( self.selected_items )
			self.select_nodes( nodes, post_event = False )

		# scroll to the selection
		if self.selected_items:
			self.scroll_to_object( self.selected_items[0] )

		self.restore_scroll_state( )


	def on_refresh( self, event = None ):
		"""
		ListerLib -
		Handle updating the lister

		*Keyword Arguments:*
			* ``event`` refresh event

		*Author:*
			* Jon Logsdon, jon.logsdon@dsvolition.com
		"""

		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		if not self.skip_callbacks:
			self.BeginBatch( )

			refresh_manager = self.get_refresh_manager( )
			node_collection = self.get_node_collection( )

			## Record exapansion states before we actually do the update
			if refresh_manager.full_refresh:
				self.record_expanded_states( )

				## Issue full refresh or do specific refreshes (else)
				if refresh_manager.full_refresh:
					# Clear these queues as they are invalidated by a full rebuild
					self.update_table( get_selection = True, get_objects = True )
					refresh_manager.reset_refresh_values( )

			else:
				# Store some flags to determine what changes took place
				did_modify = False
				needs_full_update = False
				depth_update_nodes = [ ]

				delete_queue = vlib.ui.lister_lib.node.remove_nested_child_nodes( refresh_manager.get_delete_events( ) )
				rebuild_queue = vlib.ui.lister_lib.node.remove_nested_child_nodes( refresh_manager.get_rebuild_events( ) )
				sort_queue = list( set( refresh_manager.get_sort_events( ) ) )
				expand_queue = vlib.ui.lister_lib.node.remove_nested_child_nodes( refresh_manager.get_expand_events( ) )
				collapse_queue = vlib.ui.lister_lib.node.remove_nested_child_nodes( refresh_manager.get_collapse_events( ) )

				## Do deleting
				if delete_queue:
					# Delete is causing all items to go away
					did_modify = True
					child_removal_lists = [ rebuild_queue, sort_queue ]
					removal_lists = [ self.grid_object_collection ] + child_removal_lists
					node_collection.remove_nodes_from_collection( delete_queue, is_batched = True )

					for node in delete_queue:
						# Remove from other lists/queues
						vlib.ui.lister_lib.node.remove_node_from_lists( node, removal_lists )

						# Also remove children from grid_object_collection
						child_nodes = node.get_children_recursive( )

						node_collection.remove_nodes_from_collection( child_nodes, is_batched = True )

						for child_node in node.get_children_recursive( ):
							vlib.ui.lister_lib.node.remove_node_from_lists( child_node, child_removal_lists )
							del child_node

						# Remove and destroy
						node.remove_from_parent( )
						del node

					refresh_manager.clear_delete_events( )

				# Record this AFTER the deletes
				self.record_expanded_states( only_visible = True )

				## Do rebuilding
				if rebuild_queue:
					did_modify = True
					needs_full_update = True

					for node in rebuild_queue:
						# Remove from delete_queue
						data_obj = node.get_data_obj( )
						r_data_obj = data_obj.get_data_obj( )

						# If the object is an object set and this is coming on the heels of a cross-layer object set move. This is leaving the child items destroyed.
						node.destroy_children( notify = False )

						# Do narrow data collection on queue items
						if isinstance(r_data_obj, ctg.ae2.core.data.State_Machine_Item ) or isinstance( r_data_obj, ctg.ae2.core.data.Blend_Tree_Item ):

							# update the node graph and the dependent collections
							data_obj.update_all_dependencies( )

							# update the parent's dependency collection that contains this node
							parent_node = node.get_parent( )
							if not parent_node is self._root_node:
								print 'Parent Before'
								print parent_node.get_data_obj( ).dependency_graphs_collection.get_item_names( )
								parent_node.get_data_obj( ).get_dependency_graphs( ) #dependency_graphs_collection.update_collection( )
								print 'Parent After'
								print parent_node.get_data_obj( ).dependency_graphs_collection.get_item_names( )

							# rebuild the node
							self._collect_item_dependencies( doc, data_obj, parent_node, item_node = node )

						depth_update_nodes.append( node )

					refresh_manager.clear_rebuild_events( )


				## Do sorting
				if sort_queue:
					did_modify = True
					needs_full_update = True

					for node in sort_queue:
						if node:
							node.sort_children( )
							depth_update_nodes.append( node )

					refresh_manager.clear_sort_events( )

				## Do expand/ccllapse
				if expand_queue or collapse_queue:
					did_modify = True

					nodes = expand_queue + collapse_queue
					for node in nodes:
						# Find the original item
						try:
							start_index = self.grid_object_collection.index( node ) + 1
						except ValueError:
							# May have been deleted already
							continue

						end_index = None
						sibling = node.get_next_sibling( )

						if sibling:
							while sibling and not end_index:
								try:
									end_index = self.grid_object_collection.index( sibling )
								except ValueError:
									end_index = None

								sibling = sibling.get_next_sibling( )

						if not end_index:
							self.grid_object_collection = self.grid_object_collection[ :start_index ]

						else:
							delete_indices = range( start_index, end_index )
							delete_indices.reverse( )
							for i in delete_indices:
								self.grid_object_collection.pop( i )

						if node in expand_queue:
							child_nodes = self.get_node_collection( ).get_node_child_lists_recursive( node, only_visible = self.is_tree )[ 1 ]

							self.grid_object_collection[ start_index:start_index ] = child_nodes

						self.grid_object_collection_sorted = self.grid_object_collection

				# Update any node depth values if running in tree mode
				if depth_update_nodes:
					depth_update_nodes = list( set( depth_update_nodes ) )

					for node in vlib.ui.lister_lib.node.remove_nested_child_nodes( depth_update_nodes ):
						node.notify_children( event = vlib.ui.lister_lib.node.Node.EVT_PARENT_SET, force = True )

				if did_modify:
					node_collection.update_dictionaries( )

					if refresh_manager.filter_changed or needs_full_update:
						self.update_grid_object_collection( full_update = True )

					self.update_table( get_selection = False, get_objects = False )

					# Clear the refresh queues
					refresh_manager.reset_refresh_values( )
					self.clear_refresh_queues( )

				elif refresh_manager.filter_changed:
					self.update_grid_object_collection( full_update = False )
					self.update_table( get_selection = False, get_objects = False )

				else:
					# We didn't make any changes, so we assume this was just a select event.
					if refresh_manager.has_expand_events( ) or refresh_manager.has_collapse_events( ):
						refresh_manager.post_refresh_request( immediate = True )
					else:
						self.restore_selection( )

				self.restore_scroll_state( )

			self.EndBatch( )


	def select_node_graphs( self, select_objs ):
		"""
		Select node graph tree nodes from given data_objs

		*Arguments:*
			* ``select_objs`` Data_objs that I will use to make the lister selection

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``selected_node_graphs`` List of node_graph_tree_items that have been selected

		*Examples:* ::

			Enter code examples here. (optional field)

		*Todo:*
			* Enter thing to do. (optional field)

		*Author:*
			* Jon Logsdon, jon.logsdon@dsvolition.com
		"""

		selected_node_graphs = [ ]

		select_obj = select_objs[0]
		if select_obj:

			# get the existing nodes and data_objs
			nodes = self.get_node_collection( ).nodes
			data_objs = self.get_nodes_as_data_objs( nodes )

			# get the nodes with the select_obj name
			select_objs = [ data_obj for data_obj in data_objs if data_obj.get_name( ) == select_obj.get_name( ) ]
			if select_objs and len( select_objs ) > 0:

				# set the loaded node graph to be selected
				if self.selected_items != select_objs:

					# get the relevant nodes
					select_nodes = self.get_data_objs_as_nodes( select_objs )

					# expand the relevant nodes
					for node in select_nodes:
						node.set_expanded( True )

						for parent in node.get_parents_recursive( ):
							parent.set_expanded( True )

					# set the selected items
					self.selected_items = select_objs

					# update the lister
					self.refresh_manager.filter_changed = True
					self.refresh_manager.post_refresh_request( full_refresh = False, immediate = True )

				else:
					self.restore_scroll_state( )

		return selected_node_graphs


	def on_blend_tree_load( self, event ):
		"""
		Handle selection of a blend tree load event

		*Arguments:*
			* ``event`` load event

		*Author:*
			* Jon Logsdon, jon.logsdon@dsvolition.com
		"""

		if not event.owner is ctg.ae2.ui.const.PANE_ID_NODE_GRAPH_TREE:
			# get the data obj being loaded
			event_objs = event.data_objs
			if event_objs:
				self.select_node_graphs( event_objs )

		event.Skip( )


	def on_state_machine_load( self, event ):
		"""
		Handle selection of a state machine load event

		*Arguments:*
			* ``event`` load event

		*Author:*
			* Jon Logsdon, jon.logsdon@dsvolition.com
		"""

		if not event.owner is ctg.ae2.ui.const.PANE_ID_NODE_GRAPH_TREE:
			# get the data obj being loaded
			event_objs = event.data_objs
			if event_objs:
				self.select_node_graphs( event_objs )

		event.Skip( )


	def get_node_type_id( self ):
		"""
		ListerLib -
		Return the node type id of the lister

		*Returns:*
			* ``node_type_id`` lister node type

		*Author:*
			* Jon Logsdon, jon.logsdon@dsvolition.com
		"""

		return self.node_type_id


	def on_blend_tree_created( self, event ):
		"""
		Handle the updating and selection of a blend tree that has been created

		*Arguments:*
			* ``event`` create event

		*Todo:*
			* Properly handle node creation and selection when the created event is due to an undo
			* Add a rebuild event when the blend tree is a dependency of an existing node graph
			* Add a create event when the blend tree is a root node graph

		*Author:*
			* Jon Logsdon, jon.logsdon@dsvolition.com
		"""

		# post a full table refresh
		self.active_event_objs = event.data_objs
		self.refresh_grid( )

		event.Skip( )


	def on_state_machine_created( self, event ):
		"""
		Handle the updating and selection of a state machine that has been created

		*Arguments:*
			* ``event`` create event

		*Todo:*
			* Properly handle node creation and selection when the created event is due to an undo
			* Add a rebuild event when the blend tree is a dependency of an existing node graph
			* Add a create event when the blend tree is a root node graph

		*Author:*
			* Jon Logsdon, jon.logsdon@dsvolition.com
		"""

		# post a full table refresh
		self.active_event_objs = event.data_objs
		self.refresh_grid( )

		event.Skip( )


	def remove_node_graph_nodes( self, event ):
		"""
		Common method to handle removing node graphs nodes from the node graph tree

		*Arguments:*
			* ``event`` event

		*Todo:*
			* Properly handle node deletion and selection when the delete event is due to an undo

		*Author:*
			* Jon Logsdon, jon.logsdon@dsvolition.com
		"""

		doc = AnimationEditor.get_active_document( )
		if not doc:
			return

		# get the existing nodes and data_objs
		nodes = self.get_node_collection( ).nodes
		data_objs = self.get_nodes_as_data_objs( nodes )

		# get the old_named objs
		update_objs = [ data_obj for data_obj in data_objs if event.data_objs and data_obj.get_data_obj( ) == event.data_objs[0] ]
		if update_objs:

			# update the nodes for these data_objs
			update_nodes = self.get_data_objs_as_nodes( update_objs )

			# post the rebuild node event
			self.get_refresh_manager( ).add_delete_event( update_nodes )


	def on_blend_tree_deleted( self, event ):
		"""
		Handle the updating and selection of a blend tree that has been deleted

		*Arguments:*
			* ``event`` delete event

		*Todo:*
			* Properly handle node deletion and selection when the delete event is due to an undo

		*Author:*
			* Jon Logsdon, jon.logsdon@dsvolition.com
		"""
		self.remove_node_graph_nodes( event )
		event.Skip( )


	def on_state_machine_deleted( self, event ):
		"""
		Handle the updating and selection of a state machine that has been deleted

		*Arguments:*
			* ``event`` delete event

		*Todo:*
			* Properly handle node deletion and selection when the delete event is due to an undo

		*Author:*
			* Jon Logsdon, jon.logsdon@dsvolition.com
		"""
		self.remove_node_graph_nodes( event )
		event.Skip( )


	def on_blend_tree_renamed( self, event ):
		"""
		Handle the updating and selection of a blend tree that has been renamed

		*Arguments:*
			* ``event`` rename event

		*Todo:*
			* Properly handle node creation and selection when the renamed event is due to an undo

		*Author:*
			* Jon Logsdon, jon.logsdon@dsvolition.com
		"""

		doc = AnimationEditor.get_active_document( )
		if not doc:
			return

		# get the existing nodes and data_objs
		nodes = self.get_node_collection( ).nodes
		data_objs = self.get_nodes_as_data_objs( nodes )

		# get the renamed data obj
		new_data_objs = event.data_objs
		if new_data_objs and len( new_data_objs ) > 0 and new_data_objs[ 0 ]:
			new_data_obj = new_data_objs[0]
			new_data_name = new_data_obj.get_name( )

		# make sure this is a valid rename
		if event.old_name and event.new_name:

			# get the old_named objs
			old_name_objs = [ data_obj for data_obj in data_objs if data_obj.get_name( ) == event.old_name ]
			if old_name_objs:

				# get the renamed data obj
				if new_data_obj:

					# update the real_data_obj for the node graph tree items
					for data_obj in old_name_objs:
						data_obj.set_data_obj( new_data_obj )

					# update the nodes for these data_objs
					update_nodes = self.get_data_objs_as_nodes( old_name_objs )

					# set the display name for each node to the new name
					for node in update_nodes:
						node.display_name = event.new_name

						# expand the nodes
						if not node.is_expanded( ):
							node.set_expanded( True )
							self.refresh_manager.filter_changed = True

						# expand the parents
						for parent in node.get_parents_recursive( ):
							if not parent.is_expanded( ):
								parent.set_expanded( True )
								self.refresh_manager.filter_changed = True

					# post the rebuild node event
					self.get_refresh_manager( ).add_rebuild_event( update_nodes )
					self.get_refresh_manager( ).add_sort_event( update_nodes )

					# set the selected items
					if self.selected_items != old_name_objs:
						self.selected_items = old_name_objs
						doc.event_manager.post_blend_tree_select_event( old_name_objs )

		# this is a delete event
		elif event.old_name and not event.new_name:

			# get the old_named objs
			old_name_objs = [ data_obj for data_obj in data_objs if data_obj.get_name( ) == event.old_name ]
			if old_name_objs:

				# update the nodes for these data_objs
				update_nodes = self.get_data_objs_as_nodes( old_name_objs )

				# post the rebuild node event
				self.get_refresh_manager( ).add_delete_event( update_nodes )

		# this is an undo delete event or ( re-create )
		else:
			self.refresh_grid( )

		event.Skip( )


	def on_state_machine_renamed( self, event ):
		"""
		Handle the updating and selection of a state machine that has been renamed

		*Arguments:*
			* ``event`` rename event

		*Todo:*
			* Properly handle node creation and selection when the renamed event is due to an undo

		*Author:*
			* Jon Logsdon, jon.logsdon@dsvolition.com
		"""
		doc = AnimationEditor.get_active_document( )
		if not doc:
			return

		# get the existing nodes and data_objs
		nodes = self.get_node_collection( ).nodes
		data_objs = self.get_nodes_as_data_objs( nodes )

		# make sure this is a valid rename
		if event.old_name and event.new_name:

			# get the old_named objs
			old_name_objs = [ data_obj for data_obj in data_objs if data_obj.get_name( ) == event.old_name ]
			if old_name_objs:

				# get the renamed data obj
				new_data_obj = event.data_objs[0]
				if new_data_obj:

					# update the real_data_obj for the node graph tree items
					for data_obj in old_name_objs:
						data_obj.set_data_obj( new_data_obj )

					# update the nodes for these data_objs
					update_nodes = self.get_data_objs_as_nodes( old_name_objs )

					# set the display name for each node to the new name
					for node in update_nodes:
						node.display_name = event.new_name

						# expand the nodes
						if not node.is_expanded( ):
							node.set_expanded( True )
							self.refresh_manager.filter_changed = True

						# expand the parents
						for parent in node.get_parents_recursive( ):
							if not parent.is_expanded( ):
								parent.set_expanded( True )
								self.refresh_manager.filter_changed = True

					# post the rebuild node event
					self.get_refresh_manager( ).add_rebuild_event( update_nodes )
					self.get_refresh_manager( ).add_sort_event( update_nodes )

					# set the selected items
					if self.selected_items != old_name_objs:
						self.selected_items = old_name_objs
						doc.event_manager.post_state_machine_select_event( old_name_objs )

		# this is a delete event
		elif event.old_name and not event.new_name:
			# get the old_named objs
			old_name_objs = [ data_obj for data_obj in data_objs if data_obj.get_name( ) == event.old_name ]
			if old_name_objs:

				# update the nodes for these data_objs
				update_nodes = self.get_data_objs_as_nodes( old_name_objs )

				# post the rebuild node event
				self.get_refresh_manager( ).add_delete_event( update_nodes )

		# this is likely an undo of a deletion( re-create )
		else:
			self.refresh_grid( )

		event.Skip( )


	def update_node_graph_item( self ):
		"""
		Enter a description of the function here.

		*Arguments:*
			* ``Argument`` Enter a description for the argument here.

		*Keyword Arguments:*
			* ``Argument`` Enter a description for the keyword argument here.

		*Returns:*
			* ``Value`` If any, enter a description for the return value here.

		*Examples:* ::

			Enter code examples here. (optional field)

		*Todo:*
			* Enter thing to do. (optional field)

		*Author:*
			* Jon Logsdon, jon.logsdon@dsvolition.com
		"""
		# post a rebuild to all data_objs with this name
		node_graph_name = event.new_name
		if node_graph_name:

			# get the dependency items first and update those, as the original ones may have changed
			dependents = doc.get_node_graph_dependents( ctg.ae2.ui.const.NODE_GRAPH_DEPENDENCIES[ "type" ], node_graph_name )

			# get data objs with the modified node_graph_name
			nodes = self.get_node_collection( ).nodes
			data_objs = self.get_nodes_as_data_objs( nodes )

			# get the current dependency items
			delete_items = [ ]
			all_dependencies = [ ]
			node_graph_item = doc.node_graph_tree_collection.get_item_by_name( node_graph_name )
			if node_graph_item:

				# check the new dependencies
				dependencies = doc.get_node_graph_dependents( ctg.ae2.ui.const.NODE_GRAPH_DEPENDENCIES[ "type" ], node_graph_name )
				if dependencies:
					for dep in dependencies:
						all_dependencies.append( dep )

				# check old dependencies
				dependency_graphs_collection = node_graph_item.dependency_graphs_collection
				if dependency_graphs_collection:
					old_dependencies = node_graph_item.dependency_graphs_collection.get_item_names( )
					if old_dependencies:
						for dependency in old_dependencies:
							all_dependencies.append( dependency )

				if len( all_dependencies ) > 0:
					dependency_item = None
					if doc.is_blend_tree( dependency ):
						dependency_item = doc.blend_tree_collection.get_item_by_name( dependency )
					elif doc.is_state_machine( dependency ):
						dependency_item = doc.state_machine_collection.get_item_by_name( dependency )
					if dependency_item:
						delete_items.append( dependency_item )


			# add delete events for node graphs
			if len( delete_items ) > 0:
				nodes = self.get_data_objs_as_nodes( delete_items )
				self.get_refresh_manager( ).add_delete_event( nodes )
				self.get_refresh_manager( ).add_sort_event( nodes )

			# do this if we didnt find dependencies
			update_objs = [ data_obj for data_obj in data_objs if data_obj.get_name( ) == node_graph_name ]

			# update the collection
			#doc.node_graph_tree_collection.update_collection( )

			# get data objs with the modified node_graph_name
			#nodes = self.get_node_collection( ).nodes
			#data_objs = self.get_nodes_as_data_objs( nodes )
			#update_objs = [ data_obj for data_obj in data_objs if data_obj.get_name( ) == node_graph_name ]

			# post a rebuild event for each node
			if update_objs:
				nodes = self.get_data_objs_as_nodes( update_objs )
				self.get_refresh_manager( ).add_rebuild_event( nodes )
				self.get_refresh_manager( ).add_sort_event( nodes )

			# get the last loaded node graph
			node_graph_tree_item = doc.selection_manager.get_recent_sel_node_graph_loaded( )

			# change the selection to the modified node graph
			if node_graph_tree_item:
				if self.selected_items != [ node_graph_tree_item ]:
					self.selected_items = [ node_graph_tree_item ]

					# post selection event
					#if isinstance( node_graph_tree_item.get_data_obj( ), ctg.ae2.core.data.State_Machine_Item ):
						#doc.event_manager.post_state_machine_select_event( self.selected_items )

					#elif isinstance( node_graph_tree_item.get_data_obj( ), ctg.ae2.core.data.Blend_Tree_Item ):
						#doc.event_manager.post_state_machine_select_event( self.selected_items )

					doc.event_manager.post_node_graph_dependents_modified_event( node_graph_name )

			#self.refresh_grid()


	def on_node_graph_dependents_modified( self, event ):
		"""
		Handle the updating and selection of a node graph that has been modified

		*Arguments:*
			* ``event`` modified event

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``none``

		*Examples:* ::

			Enter code examples here. (optional field)

		*Todo:*
			* nothing

		*Author:*
			* Jon Logsdon, jon.logsdon@dsvolition.com
		"""
		doc = AnimationEditor.get_active_document( )
		if not doc:
			return

		# post a rebuild to all data_objs with this name
		node_graph_name = event.new_name
		if node_graph_name:

			# get data objs with the modified node_graph_name
			nodes = self.get_node_collection( ).nodes
			data_objs = self.get_nodes_as_data_objs( nodes )

			# post a rebuild event for each node
			update_objs = [ data_obj for data_obj in data_objs if data_obj.get_name( ) == node_graph_name ]
			if update_objs:
				nodes = self.get_data_objs_as_nodes( update_objs )
				self.get_refresh_manager( ).add_rebuild_event( nodes )
				self.get_refresh_manager( ).add_sort_event( nodes )

			# get the last loaded node graph
			node_graph_tree_item = doc.selection_manager.get_recent_sel_node_graph_loaded( )

			# change the selection to the modified node graph
			if node_graph_tree_item:
				if self.selected_items != [ node_graph_tree_item ]:
					self.selected_items = [ node_graph_tree_item ]
					doc.event_manager.post_node_graph_dependents_modified_event( node_graph_name )

			#self.refresh_grid()

		event.Skip( )



class Node_Graph_Tree_Pane( wx.Panel ):
	"""
	The Panel that will contain the Node Graph Tree lister

	*Author:*
		* Jon Logsdon, jon.logsdon@dsvolition.com
	"""

	PANE_ID 		= ctg.ae2.ui.const.PANE_ID_NODE_GRAPH_TREE
	PANE_TITLE 	= ctg.ae2.ui.const.PANE_TITLE_NODE_GRAPH_TREE

	def __init__( self, parent ):
		"""
		Setup the Node Graph Tree Pane
		- Setup the lister
		- Setup the bookmarks toolbar

		*Arguments:*
			* ``parent`` The panel object that will house this Pane

		*Author:*
			* Jon Logsdon, jon.logsdon@dsvolition.com
		"""

		wx.Panel.__init__( self, parent )
		self.lister = Node_Graph_Tree( self )

		self.bookmark_names = None
		self.active_bookmark = None

		main_sizer 			   = wx.BoxSizer( wx.VERTICAL )
		search_sizer 		   = wx.BoxSizer( wx.HORIZONTAL )
		bookmark_sizer 	   = wx.BoxSizer( wx.HORIZONTAL )

		# add search field
		self.search_field = vlib.ui.lister_lib.filter.Search_Control( self, self.lister )
		search_sizer.Add( self.search_field, 1, wx.ALIGN_CENTER_HORIZONTAL, 0)

		# add bookmarks toolbar
		self.btn_add			= wx.Button( self, label='+', size=( 20, -1 ) )
		self.btn_del			= wx.Button( self, label='-', size=( 20, -1 ) )
		self.bookmarks 		= wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, ( 224, -1 ), '' , 0 )
		self.btn_bookmark		= wx.ToggleButton( self, label='.', size=( 25, -1 ) )
		self.btn_bookmarks	= wx.ToggleButton( self, label='...', size=( 25, -1 ) )

		# Sizer Layout
		bookmark_sizer.AddSpacer( 3 )
		bookmark_sizer.Add( self.btn_add, 0, wx.LEFT, 1 )
		bookmark_sizer.AddSpacer( 3 )
		bookmark_sizer.Add( self.btn_del, 0, wx.LEFT, 1 )
		bookmark_sizer.AddSpacer( 5 )
		bookmark_sizer.Add( self.bookmarks, 1, wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, 0 )
		bookmark_sizer.AddSpacer( 3 )
		bookmark_sizer.Add( self.btn_bookmark, 0, wx.LEFT, 3 )
		bookmark_sizer.AddSpacer( 3 )
		bookmark_sizer.Add( self.btn_bookmarks, 0, wx.LEFT, 3 )
		bookmark_sizer.AddSpacer( 3 )

		# add lister
		self.sub_sizer = wx.BoxSizer( wx.HORIZONTAL )
		self.sub_sizer.Add( self.lister, 1, wx.EXPAND, 0 )

		main_sizer.Add( search_sizer, 0, wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, 0 )
		main_sizer.Add( bookmark_sizer, 0, wx.EXPAND, 0 )
		main_sizer.Add( self.sub_sizer, 1, wx.EXPAND, 0 )

		self.SetSizer( main_sizer )
		self.Layout( )

		self.lister.Bind( wx.EVT_SCROLLWIN, self.on_scroll )
		self.btn_add.Bind( wx.EVT_BUTTON, self.on_button_add )
		self.btn_del.Bind( wx.EVT_BUTTON, self.on_button_delete )
		self.btn_bookmark.Bind( wx.EVT_TOGGLEBUTTON, self.on_bookmark_toggle )
		self.btn_bookmarks.Bind( wx.EVT_TOGGLEBUTTON, self.on_bookmarks_toggle )
		self.bookmarks.Bind( wx.EVT_CHOICE, self.on_bookmarks_changed  )

		# update the pane bookmark controls
		self.update_controls( )

		doc = AnimationEditor.get_active_document()
		setattr( doc, 'anim_node_graph_tree_pane', self )

	def _save_bookmarks( self ):
		"""
		Save the bookmarks list to the preferences

		*Author:*
			* Jon Logsdon, jon.logsdon@dsvolition.com
		"""

		ctg.prefs.user["session.node_graph_tree_bookmark_names"] = self.bookmark_names


	def _get_bookmarks( self ):
		"""
		Retrieve the bookmarks list from the preferences

		*Author:*
			* Jon Logsdon, jon.logsdon@dsvolition.com
		"""
		self.bookmark_names = list( ctg.prefs.user.setdefault( "session.node_graph_tree_bookmark_names", [ ] ) )


	def on_scroll( self, event ):
		"""
		Handle scrolling within the pane

		*Arguments:*
			* ``event`` Scrolling event

		*Author:*
			* Jon Logsdon, jon.logsdon@dsvolition.com
		"""

		self.lister.SetDoubleBuffered( False )
		wx.CallLater( 500, self.lister.SetDoubleBuffered, True )
		event.Skip( )


	def refresh_ui( self ):
		"""
		Update specific controls to the Node Graph Tree Pane

		*Author:*
			* Jon Logsdon, jon.logsdon@dsvolition.com
		"""

		self.update_controls( )


	def on_button_delete( self, event ):
		"""
		Handle bookmark deletion
		- Updating the bookmarks list
		- Updating the preferences

		*Arguments:*
			* ``event`` Delete button pressed event

		*Author:*
			* Jon Logsdon, jon.logsdon@dsvolition.com
		"""

		# Remove the active bookmark selection
		self.bookmark_names.remove( self.bookmark_names[ self.bookmarks.Selection ] )

		# Set an active bookmark
		if len( self.bookmark_names ) > 0:
			self.active_bookmark = self.bookmark_names[ 0 ]
			ctg.prefs.user["session.node_graph_tree_active_bookmark"] = self.active_bookmark

		# Add the names to CTG Prefs
		self._save_bookmarks( )

		# Update the Interface
		self.update_controls( post_refresh = True )


	def on_button_add( self, event ):
		"""
		Handle bookmark addition
		- Updating the bookmarks list
		- Updating the preferences

		*Arguments:*
			* ``event`` Add button pressed event

		*Author:*
			* Jon Logsdon, jon.logsdon@dsvolition.com
		"""
		# Get the active selections from the lister
		update_controls = False

		# Add new bookmarks
		data_objs = self.lister.get_selected_data_objs( )
		if data_objs:
			for data_obj in data_objs:
				r_data_obj = data_obj.get_data_obj( )
				if isinstance( r_data_obj, ctg.ae2.core.data.State_Machine_Item ) or isinstance( r_data_obj, ctg.ae2.core.data.Blend_Tree_Item ):
					if not data_obj.get_name( ) in self.bookmark_names:
						self.bookmark_names.append( data_obj.get_name( ) )
						self.active_bookmark = data_obj.get_name( )
						update_controls = True

		# Add the names to CTG Prefs
		self._save_bookmarks( )

		# Update the Interface
		if update_controls:
			ctg.prefs.user["session.node_graph_tree_active_bookmark"] = self.active_bookmark
			self.update_controls( post_refresh = True )


	def on_bookmark_toggle( self, event ):
		"""
		Handle activating single bookmark filtering

		*Arguments:*
			* ``event`` Button checked event

		*Author:*
			* Jon Logsdon, jon.logsdon@dsvolition.com
		"""
		# update the filtered items if bookmark button is active
		if event.Checked( ):
			self.btn_bookmarks.SetValue( False )
			self.lister.active_bookmarks = [ self.bookmarks.Items[ self.bookmarks.Selection ] ]
			ctg.prefs.user["session.node_graph_tree_bookmarks"] = ctg.ae2.ui.const.NODE_GRAPH_BOOKMARK_ACTIVE
		else:
			self.lister.active_bookmarks = None
			ctg.prefs.user["session.node_graph_tree_bookmarks"] = ctg.ae2.ui.const.NODE_GRAPH_BOOKMARKS_INACTIVE

		self.lister.select_active_bookmarks( )


	def on_bookmarks_toggle( self, event ):
		"""
		Handle activating and filtering all the bookmarks

		*Arguments:*
			* ``event`` Button checked event

		*Author:*
			* Jon Logsdon, jon.logsdon@dsvolition.com
		"""
		# update the filtered items if bookmark button is active
		if event.Checked( ):
			self.btn_bookmark.SetValue( False )
			self.lister.active_bookmarks = self.bookmark_names
			ctg.prefs.user["session.node_graph_tree_bookmarks"] = ctg.ae2.ui.const.NODE_GRAPH_BOOKMARKS_ACTIVE
		else:
			self.lister.active_bookmarks = None
			ctg.prefs.user["session.node_graph_tree_bookmarks"] = ctg.ae2.ui.const.NODE_GRAPH_BOOKMARKS_INACTIVE

		self.lister.select_active_bookmarks( )


	def on_bookmarks_changed( self, event ):
		"""
		Handle activating and filtering the active bookmark in the list

		*Arguments:*
			* ``event`` List changed event

		*Author:*
			* Jon Logsdon, jon.logsdon@dsvolition.com
		"""
		# update the filtered items if bookmark button is active
		self.btn_bookmarks.SetValue( False )
		self.btn_bookmark.SetValue( True )
		bookmark_name = self.bookmarks.Items[ event.GetSelection( ) ]
		self.active_bookmark = bookmark_name
		ctg.prefs.user["session.node_graph_tree_bookmarks"] = ctg.ae2.ui.const.NODE_GRAPH_BOOKMARK_ACTIVE
		ctg.prefs.user["session.node_graph_tree_active_bookmark"] = bookmark_name

		self.update_controls( post_refresh = True )


	def update_controls( self, post_refresh = False ):
		"""
		Function to update how the controls are displayed

		*Keyword Arguments:*
			* ``post_refresh`` Refresh the lister if needed

		*Author:*
			* Jon Logsdon, jon.logsdon@dsvolition.com
		"""

		doc = AnimationEditor.get_active_document( )
		if not doc:
			return

		# Get Starting Prefs bookmarked names and toggles
		if not self.bookmark_names:
			self._get_bookmarks( )

			# set a default selection
			if len( self.bookmark_names ) > 0:
				self.active_bookmark = self.bookmark_names[0]

			# get/set the bookmarks toggle
			toggle = ctg.prefs.user.setdefault( "session.node_graph_tree_bookmarks", ctg.ae2.ui.const.NODE_GRAPH_BOOKMARK_TOGGLE )
			if toggle:
				if toggle == ctg.ae2.ui.const.NODE_GRAPH_BOOKMARKS_ACTIVE:
					self.btn_bookmarks.SetValue( True )
					post_refresh = True
				elif toggle == ctg.ae2.ui.const.NODE_GRAPH_BOOKMARK_ACTIVE:
					self.btn_bookmark.SetValue( True )
					post_refresh = True

			# get/set a default bookmark selection
			active = ctg.prefs.user.setdefault( "session.node_graph_tree_active_bookmark", ctg.ae2.ui.const.NODE_GRAPH_ACTIVE_BOOKMARK )
			if active:
				if not active == ctg.ae2.ui.const.NODE_GRAPH_ACTIVE_BOOKMARK:
					self.active_bookmark = active

		# update button toggles and bookmarks list
		if len( self.bookmark_names ) > 0:

			self.bookmark_names.sort( )
			self.bookmarks.SetItems( self.bookmark_names )
			self.btn_bookmark.Enable( True )
			self.btn_bookmarks.Enable( True )
			self.bookmarks.Enable( True )
			self.btn_del.Enable( True )

			if self.active_bookmark:
				self.bookmarks.SetStringSelection( self.active_bookmark )
				self.active_bookmark = None

			if self.btn_bookmark.GetValue( ):
				self.btn_bookmarks.SetValue( False )
				self.lister.active_bookmarks = [ self.bookmarks.Items[ self.bookmarks.Selection ] ]

			elif self.btn_bookmarks.GetValue( ):
				self.btn_bookmark.SetValue( False )
				self.lister.active_bookmarks = self.bookmark_names

		else:
			self.btn_bookmark.SetValue( False )
			self.btn_bookmarks.SetValue( False )
			self.btn_bookmark.Enable( False )
			self.btn_bookmarks.Enable( False )
			self.bookmarks.Enable( False )
			self.btn_del.Enable( False )

			self.bookmarks.SetItems( [ ] )
			self.lister.active_bookmarks = None

		# refresh the lister
		if post_refresh:
			self.lister.select_active_bookmarks( )


class Controls_Pane( wx.lib.scrolledpanel.ScrolledPanel ):
	PANE_ID 		= ctg.ae2.ui.const.PANE_ID_CONTROLS
	PANE_TITLE 	= u'Controls'

	def __init__( self, parent ):
		wx.lib.scrolledpanel.ScrolledPanel.__init__( self, parent, style=wx.BORDER_SUNKEN )

		self.SetDoubleBuffered(True)
		doc = AnimationEditor.get_active_document()
		if doc:
			setattr( doc, 'network_preview_controls', self )

		#initialize attributes
		self.controls_enabled_check_boxes = {}
		self.control_parameter_inputs     = {}
		self.playback_started             = False
		self.reseted_value          = False
		self.current_time           = time.time()
		self.current_frame          = 1
		self.next_frame             = None
		self.current_pressed_button = None
		self.clip_preview_data_ctrl =  None
		self.controls_dict          = { }


		#callbacks
		self.callback_string = 'animation_preview_network_controls_callbacks'
		self.callback_preview_string = 'clip_preview_network_controls_callbacks'
		#ae preview updated
		self.callback_string_toggle_value = 'animation_preview_network_controls_callbacks_toggle'
		ctg.CALLBACK_SYSTEM.register_callback( self.callback_string, 'ae network playback start', self.setup_network_preview_controls )
		ctg.CALLBACK_SYSTEM.register_callback( self.callback_string, 'ae network playback stop', self.setup_network_preview_controls )
		ctg.CALLBACK_SYSTEM.register_callback( self.callback_string, 'ae network live update', self.live_update_controls )
		ctg.CALLBACK_SYSTEM.register_callback( self.callback_preview_string, 'ae preview updated', self.clip_preview_data_update )

		ctg.CALLBACK_SYSTEM.register_callback( self.callback_string, 'ae network process control inputs', self.process_control_parameter_inputs )
		ctg.CALLBACK_SYSTEM.register_callback( self.callback_string_toggle_value, 'ae network process control inputs', self.process_button_inputs )

		#bind on resize event
		self.Bind( wx.EVT_SIZE, self.on_resize )
		self.Bind( wx.EVT_WINDOW_DESTROY, self._on_destroy )


	def _on_destroy( self, event ):
		if event.GetWindow( ) is self:
			ctg.CALLBACK_SYSTEM.unregister_callbacks( self.callback_string )
			ctg.CALLBACK_SYSTEM.unregister_callbacks( self.callback_preview_string )
			ctg.CALLBACK_SYSTEM.unregister_callbacks( self.callback_string_toggle_value )

		event.Skip( )


	def on_resize( self, event ):
		#update panel height
		self.update_height(  )

		if event:
			event.Skip( )


	def clip_preview_data_update( self, doc ):
		if hasattr( doc, 'preview_pane' ):
			if not ( doc.preview_pane.is_clip_playing() and self.playback_started ):
				return

			preview_clip_data = doc.get_preview_clip_data()
			preview_text = ""

			space = "   "
			data_list = [ ]

			if preview_clip_data:

				for clip in preview_clip_data:
					base_name = os.path.basename( clip.get_clip_name() )

					#add data to a list
					data_list.append( str( os.path.splitext(base_name)[0]) )
					data_list.append( space + str( clip.get_looping() ) )
					data_list.append( space + str( clip.get_frame_num() ) )
					data_list.append( space + str( clip.get_length() ) )
					data_list.append( space + str( '%.2f' % round( clip.get_mix_percent(),  ) ) )
					data_list.append( space + str( clip.get_speed_multiplier() ) )
					data_list.append( space + str( clip.get_priority() ) )
					data_list.append( "\n" )

			float_track_data = doc.get_preview_float_track_data( )
			if float_track_data:
				data_list.append( "\nFloat Tracks:\n" )

				for track in float_track_data:
					data_list.append( track.get_name( ) )
					data_list.append( space + str( track.get_value( ) ) )
					data_list.append( space + str( '%.2f' % round( track.get_weight( ),  ) ) )
					data_list.append( space + track.get_priority( ) )
					data_list.append( "\n" )

			#set clip preiview as a value on clip preview text control
			if self.clip_preview_data_ctrl:
				#join data as a single string
				preview_text = "".join( data_list )

				#set preview data as value on clip preview control
				self.clip_preview_data_ctrl.SetValue( preview_text )

				#update panel height
				self.update_height( )


	def update_height( self ):

		#get number of lines for the clip preview data controls
		if self.clip_preview_data_ctrl:
			num_ctrl_lines      = self.clip_preview_data_ctrl.GetNumberOfLines( ) + 1
			total_ctrl_height   = num_ctrl_lines * 10
			number_of_controls  = len( self.controls_dict.keys( ) )

			#set default number of controls to 1 if we dont have any parameter controls
			if number_of_controls < 1:
				number_of_controls = 1

			#add up the total control height
			total_ctrl_height += number_of_controls * 55
			current_height     = self.GetVirtualSize( )[1]

			#update the height of the main control pane if current height is less total controls height
			if current_height < total_ctrl_height:

				self.Freeze( )
				#set panel height
				self.SetVirtualSize( ( self.MaxWidth, total_ctrl_height ) )
				self.Thaw( )


	def refresh_ui( self ):
		pass


	#@vlib.debug.Debug_Timing( 'setup_network_preview_controls', precision = 4 )
	def setup_network_preview_controls( self, doc, started = True ):

		self.Freeze( )

		self.playback_started = started
		self.DestroyChildren( )
		self.controls_dict = { }
		self.controls_enabled_check_boxes = { }
		self.clip_preview_data_ctrl =  None

		#load control parameter modules if a controller is connected
		if doc.is_controller_connected():
			self.load_control_parameter_modules( doc )

		#get and create preview network controls
		sorted_param_objs_list = [ ]
		param_objs 		= list( doc.get_preview_network_controls( ) )
		if param_objs:
			#sort the param objects
			sorted_param_objs_list = sorted( param_objs, key=lambda param_obj: param_obj.get_name( ) )

		#create and set main sizer
		main_sizer 		= wx.BoxSizer( wx.VERTICAL )

		if sorted_param_objs_list:
			#create clip preview data sizer
			clip_preview_data_label_box 	= wx.StaticBox( self, -1, "Previewing Clips:" )
			clip_preview_data_label_box.SetFont( wx.Font( 8, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.BOLD ) )
			clip_preview_data_sizer 	= wx.StaticBoxSizer( clip_preview_data_label_box, wx.HORIZONTAL )

		#set up and create controls
		for param_obj in sorted_param_objs_list:
			toggle_button = None

			param_type 				= param_obj.get_type( )
			param_name 				= param_obj.get_name( )

			control_label_box 	= wx.StaticBox( self, -1, "{0}:".format( param_name ) )
			control_label_box.SetFont( wx.Font( 8, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.BOLD ) )
			control_label_sizer 	= wx.StaticBoxSizer( control_label_box, wx.HORIZONTAL )
			inner_control_label_sizer 	= wx.BoxSizer( wx.HORIZONTAL )

			control_label_sizer.AddSpacer( 5 )

			if param_type == FLOAT_DATA_TYPE:
				min_v 			= param_obj.get_min_value_float( )
				max_v 			= param_obj.get_max_value_float( )
				default_value 	= param_obj.get_default_value_float( )

			elif param_type == ANGLE_DATA_TYPE:
				min_v = -180
				max_v = 180
				default_value = param_obj.get_default_value_angle( )

			elif param_type == INT_DATA_TYPE:
				min_v 			= param_obj.get_min_value_int( )
				max_v 			= param_obj.get_max_value_int( )
				default_value 	= param_obj.get_default_value_int( )

			elif param_type == BOOL_DATA_TYPE:
				default_value 	= param_obj.get_default_value_bool( )

			elif param_type == STRING_CRC_DATA_TYPE:
				default_value = str( param_obj.get_default_value_int( ) )

			if param_type in [ INT_DATA_TYPE, FLOAT_DATA_TYPE, ANGLE_DATA_TYPE ]:
				if param_type == INT_DATA_TYPE:
					decimals = 0
				else:
					decimals = 2

				param_control   = ctg.ui.widgets.misc.Float_Slider_Control( self, -1, default_value, min_value=min_v, max_value=max_v, decimals=decimals, val_label_size=( 55, -1) )
				param_control.Bind( ctg.ui.widgets.misc.EVT_FLOAT_SLIDER, self.on_value_change )
			elif param_type == STRING_CRC_DATA_TYPE:
				param_control = ctg.ae2.ui.widgets.text_control.Text_Control(self, -1,'', size = (100, -1), style = wx.TE_PROCESS_ENTER, wait_time = 0, delay = 0, initial_delay = 0)
				param_control.Bind(ctg.ae2.ui.widgets.text_control.EVT_TEXT_CHANGED, self.on_value_change)

			elif param_type == BOOL_DATA_TYPE:
				param_control 	= wx.CheckBox(self, -1, "")
				param_control.SetValue( default_value )
				param_control.Bind( wx.EVT_CHECKBOX, self.on_value_change )

				#this button toggle a param control bool value for a frame
				toggle_button = wx.Button( self, -1, "T", size=(20, 20) )
				toggle_button.Bind( wx.EVT_LEFT_DOWN, self.on_left_down )
				toggle_button.Bind( wx.EVT_LEFT_UP, self.on_left_up )
				toggle_button.name = param_name
				toggle_button.param_obj = param_obj
				toggle_button.initial_v = default_value

			if param_name in self.control_parameter_inputs.values():
				#this control allows user to either change the values with mouse or controller
				enabled_checkbox = wx.CheckBox( self, -1, "")
				enabled_checkbox.SetValue( False )
				enabled_checkbox.name = param_name
				enabled_checkbox.Bind( wx.EVT_CHECKBOX, self.on_enable_change )

				self.controls_enabled_check_boxes[ param_name ] = enabled_checkbox
				inner_control_label_sizer.Add( enabled_checkbox, 0, wx.ALIGN_CENTRE_VERTICAL)
				param_control.Disable()

			#add name and type attribute to the control
			param_control.name			= param_name
			param_control.param_type 	= param_type

			#save controls and there associated names parameter name in a dictionary
			self.controls_dict[ param_name ] 	= param_control

			#add to sizers
			inner_control_label_sizer.Add( param_control, 1, wx.EXPAND )
			control_label_sizer.Add( inner_control_label_sizer, 1, wx.EXPAND )

			#add toggle button
			if toggle_button:
				control_label_sizer.Add( toggle_button, 0, wx.TOP )

			main_sizer.AddSpacer( 5 )
			main_sizer.Add( control_label_sizer, 0, wx.EXPAND )

		#create and add clip preview data control to sizer
		if sorted_param_objs_list:
			self.clip_preview_data_ctrl = wx.TextCtrl( self, -1, "", size=(125, -1), style=wx.TE_MULTILINE | wx.TE_NO_VSCROLL )
			self.clip_preview_data_ctrl.Enable( False )
			clip_preview_data_sizer.Add( self.clip_preview_data_ctrl, 1, wx.EXPAND )

			#add clip preview sizer to main sizer
			main_sizer.AddSpacer( 5 )
			main_sizer.Add( clip_preview_data_sizer, 1, wx.EXPAND | wx.ALL, 0 )

		main_sizer.Layout( )
		self.SetSizer( main_sizer )

		#force layout and setup scrolling
		self.Layout( )
		self.SetAutoLayout( 1 )
		self.SetupScrolling( )

		self.Thaw( )


	def load_control_parameter_modules(self, doc):
		self.control_parameter_inputs.clear()
		scripts = list(doc.get_control_parameter_module_names())

		if scripts:
			for mod in scripts:
				path = os.path.dirname(mod)
				mod_name = os.path.basename(mod)
				sys.path.append(path)
				#is this module already loaded? reload it incase changes were made
				if sys.modules.has_key(mod_name):
					module = reload(sys.modules.get(mod_name))
				else:
					module = __import__(mod_name)

				for cls in dir(module):
					cls=getattr(module,cls)
					if inspect.isclass(cls)and inspect.getmodule(cls)==module and issubclass(cls,ctg.ae2.core.input.Input_To_Parameter):
						self.control_parameter_inputs[cls()] = cls().control_param

				sys.path.pop()


	def process_control_parameter_inputs(self, doc):

		for control_input in self.control_parameter_inputs.keys():
			control_input.process()


	def process_button_inputs( self, doc ):
		if self.playback_started and not self.reseted_value:
			if self.current_pressed_button:
				param_control = self.controls_dict.get(self.current_pressed_button.name)

				self.current_frame += 1
				if not self.next_frame:
					self.next_frame = self.current_frame + 1

				if self.current_frame > self.next_frame:
					doc.preview_set_control_param_bool( self.current_pressed_button.name, bool( self.current_pressed_button.initial_v ) )
					self.reseted_value = True
					if param_control:
						param_control.SetValue(self.current_pressed_button.initial_v)


	def on_left_up(self, event):

		if self.current_pressed_button:
			#reset attribute values
			self.current_pressed_button = None
			self.reseted_value = False
			self.current_frame = 0
			self.next_frame = None

		if event:
			event.Skip()


	def on_enable_change(self, event):
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		value  			= event.GetEventObject().GetValue( )
		name  			= event.GetEventObject().name
		param_control  =  self.controls_dict.get(name)

		if value == True:
			if param_control:
				param_control.Enable()
		else:
			if param_control:
				param_control.Disable()


	def on_value_change( self, event ):
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		value  			= event.GetEventObject().GetValue( )
		name  			= event.GetEventObject().name
		param_type 		= event.GetEventObject().param_type

		if param_type == FLOAT_DATA_TYPE or param_type == ANGLE_DATA_TYPE:
			doc.preview_set_control_param_float( name, float( value ) )
		elif param_type == INT_DATA_TYPE:
			doc.preview_set_control_param_int( name, int( value ) )
		elif param_type == BOOL_DATA_TYPE:
			doc.preview_set_control_param_bool( name, bool( value ) )
		elif param_type == STRING_CRC_DATA_TYPE:
			doc.preview_set_control_param_string(name, value)


	def on_left_down( self, event ):

		doc = AnimationEditor.get_active_document()
		name  = event.GetEventObject().name
		param_control = self.controls_dict.get( name )
		if param_control:

			self.current_pressed_button = event.GetEventObject()
			self.current_pressed_button.initial_v = doc.preview_get_control_param_bool( name )
			value  = not self.current_pressed_button.initial_v

			param_control.SetValue( value )
			doc.preview_set_control_param_bool( name, bool( value ) )
			self.current_time = time.time()

		if event:
			event.Skip()


	def live_update_controls( self, doc ):

		param_objs 		= list( doc.get_preview_network_controls( ) )

		if len(param_objs) == 0 and len( self.controls_dict ) > 0:
			self.setup_network_preview_controls(doc, True)
			return

		for param_obj in param_objs:

			if param_obj.get_name( ) not in self.controls_dict:
				self.setup_network_preview_controls(doc, True)
				return

			param_control   =  self.controls_dict[ param_obj.get_name( ) ]
			param_type 		 = param_obj.get_type( )

			#types changed on this control param... reload all the controls
			if param_control.param_type != param_type:
				self.setup_network_preview_controls(doc, True)
				return

			if param_type == FLOAT_DATA_TYPE:
				min_v 			= param_obj.get_min_value_float( )
				max_v 			= param_obj.get_max_value_float( )
				default_value 	= param_obj.get_default_value_float( )

			elif param_type == ANGLE_DATA_TYPE:
				min_v 			= -180
				max_v 			= 180
				default_value 	= param_obj.get_default_value_angle( )

			elif param_type == INT_DATA_TYPE:
				min_v 			= param_obj.get_min_value_int( )
				max_v 			= param_obj.get_max_value_int( )
				default_value 	= param_obj.get_default_value_int( )

			elif param_type == BOOL_DATA_TYPE:
				default_value 	= param_obj.get_default_value_bool( )

			if param_type in [ INT_DATA_TYPE, FLOAT_DATA_TYPE, ANGLE_DATA_TYPE ]:
				current_value = param_control.GetValue( )

				if current_value < min_v:
					current_value = min_v
				elif current_value > max_v:
					current_value = max_v

				param_control.SetRange(min_v, max_v)
				param_control.SetValue(current_value)


			elif param_type == BOOL_DATA_TYPE:
				param_control.SetValue( default_value )


	def change_value(self, control, value):
		if not self.controls_dict:
			return

		if control not in self.controls_dict:
			return

		enable_control = self.controls_enabled_check_boxes.get(control)
		if not enable_control:
			return

		# if the control is enabled then we shouldn't be setting it based on input, just return
		if enable_control.GetValue():
			return

		param_control   =  self.controls_dict.get(control)
		if param_control:
			param_control.SetValue(value)

			#set bools because for some reason disabled checkboxes don't call on_value_changed
			if param_control.param_type == BOOL_DATA_TYPE:
				doc = AnimationEditor.get_active_document()
				if not doc:
					return
				doc.preview_set_control_param_bool( control, bool( value ) )


	def get_min_value(self, control):
		if not self.controls_dict:
			return 0.0

		if control not in self.controls_dict:
			return 0.0

		param_control   =  self.controls_dict.get(control)

		if param_control:
			return param_control.GetMin()

	def get_max_value(self, control):
		if not self.controls_dict:
			return 0.0

		if control not in self.controls_dict:
			return 0.0

		param_control   =  self.controls_dict.get(control)

		if param_control:
			return param_control.GetMax()

	def get_current_value(self, control):
		if not self.controls_dict:
			return 0.0

		if control not in self.controls_dict:
			return 0.0

		param_control   =  self.controls_dict.get(control)

		if param_control:
			return param_control.GetValue()
