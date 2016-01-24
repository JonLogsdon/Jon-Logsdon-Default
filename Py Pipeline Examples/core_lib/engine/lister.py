import wx
import cPickle
import pprint
import re

import ctg.ae2.ui.const
import ctg.ae2.ui.dialogs
import ctg.ae2.ui.events
import ctg.prefs
import ctg.ae2.core.ae_common_operations
import ctg.lister_lib.core
import ctg.ui.dialogs

import vlib.ui.lister_lib
import vlib.ui.lister_lib.column
import vlib.ui.lister_lib.const
import vlib.ui.lister_lib.node
import vlib.ui.lister_lib2
import vlib.ui.lister_lib2.data

import AnimationEditor
import param_types
import _resourcelib


# TODO: Cleanup color chooser stuff (I don't like it)

#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# Filter Classes
#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

class Item_Filter( object ):
	def __init__( self, filter_id = None, is_enabled = True ):
		if filter_id is None:
			filter_id = str( uuid.uuid4( ) )
		self._id = filter_id
		self._is_enabled = is_enabled


	def get_enabled( self ):
		return self._is_enabled


	def set_enabled( self, val ):
		self._is_enabled = val


	def check_item_passes( self, item, accessor ):
		# OVERRIDE
		if self.get_enabled( ):
			return True

		return True


class Filter_String_Value( Item_Filter ):
	QUO_STR = '\"'
	AND_STR = '+'
	NOT_STR = '-'
	OR_STR = '|'
	STARTSWITH_STR = '>'
	ENDSWITH_STR = '<'

	SEARCH_DEF = { \
	   AND_STR	: [ ],
	   NOT_STR	: [ ],
	   OR_STR	: [ ],
	   QUO_STR  : [ ],
	   STARTSWITH_STR  : [ ],
	   ENDSWITH_STR : [ ],
	}

	def __init__( self, filter_id = vlib.ui.lister_lib2.const.FILTER_ID_STRING ):
		Item_Filter.__init__( self, filter_id = filter_id )
		self.val = ''
		self.is_using_or_mode = vlib.ui.widgets.text_controls.get_search_mode_pref( )
		self.search_strings_dict = self.SEARCH_DEF


	def set_string_value( self, val ):
		val = val.lower( )

		mode_changed = False
		new_or_mode = vlib.ui.widgets.text_controls.get_search_mode_pref( )

		if new_or_mode != self.is_using_or_mode:
			self.is_using_or_mode = new_or_mode
			mode_changed = True

		# Early out here
		if not mode_changed and val == self.val:
			return False

		self.val = val.lower( )
		self.parse_string( )
		return True


	def parse_string( self ):
		# Make sure our string isn't empty
		if self.val:
			# Setup some temp values for later
			base_str = self.val
			base_list = [ ]
			and_list = [ ]
			not_list = [ ]
			or_list = [ ]
			startswith_list = [ ]
			endswith_list = [ ]

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
					# For search type >, add quote to STARTSWITH list
					elif type_str == self.STARTSWITH_STR:
						open_idx = type_idx
						startswith_list.append( quote_str )
					# For search type <, add quote to ENDSWITH list
					elif type_str == self.ENDSWITH_STR:
						open_idx = type_idx
						endswith_list.append( quote_str )
					# For no search type, add quote to OR list
					else:
						or_list.append( quote_str )

				# Remove entire quote from base string
				base_str = base_str[ :open_idx ] + base_str[ ( close_idx + 1 ): ]

				# Find next open quote in base string
				open_idx = base_str.find( self.QUO_STR )

			# Split remaining string at whitespaces
			base_list = base_str.split( )

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
				# For search type >, add string to STARTSWITH list
				elif type_str == self.STARTSWITH_STR:
					base_str = base_str [ 1: ]
					if base_str:
						startswith_list.append( base_str )
				# For search type <, add string to ENDSWITH list
				elif type_str == self.ENDSWITH_STR:
					base_str = base_str[ 1: ]
					if base_str:
						endswith_list.append( base_str )
				# For no search type, add string to OR list
				else:
					or_list.append( base_str )

			# Populate search dict with results
			self.search_strings_dict =	{ \
			   self.AND_STR	: and_list,
			   self.NOT_STR	: not_list,
			   self.OR_STR		: or_list,
			   self.STARTSWITH_STR   : startswith_list,
			   self.ENDSWITH_STR   : endswith_list,
			}

		# If string is empty, default search dict
		else:
			self.search_strings_dict = self.SEARCH_DEF


	def check_item_passes_internal( self, item, accessor ):
		if self.get_enabled( ) and self.val:
			# Make sure our string isn't empty

			# Get display name in lowercase
			name = str( accessor.get_display_value( item ) ).lower( )

			and_vals = list( self.search_strings_dict[ self.AND_STR ] )
			or_vals = list( self.search_strings_dict[ self.OR_STR ] )
			startswith_vals = list( self.search_strings_dict[ self.STARTSWITH_STR ] )
			endswith_vals = list( self.search_strings_dict[ self.ENDSWITH_STR ] )

			if not self.is_using_or_mode:
				# Treat it all as AND
				and_vals.extend( or_vals )
				and_vals = list( set( and_vals ) )
				or_vals = [ ]

			# Loop through AND list and make sure ALL are found
			for and_str in and_vals:
				if name.find( and_str ) == -1:
					return False

			# Loop through NOT list and make sure NONE are found
			for not_str in self.search_strings_dict[ self.NOT_STR ]:
				if name.find( not_str ) > -1:
					return False

			# Loop through STARTSWITH list and make sure NONE are found
			for startswith_str in self.search_strings_dict[ self.STARTSWITH_STR ]:
				if not name.startswith( str( startswith_str ) ):
					return False

			# Loop through ENDSWITH list and make sure NONE are found
			for endswith_str in self.search_strings_dict[ self.ENDSWITH_STR ]:
				if not name.endswith( str( endswith_str ) ):
					return False

			# Loop through OR list and make sure at least ONE is found
			if or_vals:
				for or_str in or_vals:
					if name.find( or_str ) > -1:
						return True
				return False

		return True


	def check_item_passes( self, item, accessor ):
		passes = self.check_item_passes_internal( item, accessor )

		# Ensure none of the children pass ( since this is a tree )
		if not passes:
			for c in accessor.get_children( item ):
				child_passes = self.check_item_passes( c, accessor )

				if child_passes:
					return True

		return passes


class Filter_String_Value_Multi_Accessor( Filter_String_Value ):
	"""
	A string filter that searches across multiple accessors.
	"""

	def __init__( self, accessors, *args, **kwargs ):
		Filter_String_Value.__init__( self, *args, **kwargs )
		self.accessors = accessors


	def check_item_passes( self, item, accessor ):
		for accessor in self.accessors:
			passes = self.check_item_passes_internal( item, accessor )
			if passes:
				return True

		return False


class Item_Accessor( object ):
	"""
	This class is designed to allow communication with the data; this is generally regarding a single attribute of the data.
	Item_Accessors are also transposed into columns when in a Grid style view; so additional KWARGS dictate behavior when represented as a column.

	The class attribute VALIDATION_METHODS is a list that you append methods too.  Those methods will be specifically
	run on any item that is dropped onto this Item_Accessor.  By default, not having these validation Methods is
	fine and the Accessor will return True.

	*Arguments:*
		* <none>

	*Keyword Arguments:*
		* ``label``						<String> Display Name
		* ``id_string``				<String> Unique ID
		* ``data_type``				<Enum> 	Data Type Id ( for default value renderers )
		* ``can_edit``					<Bool> 	Allow set_value to be called ( also controls value editing popup in Grid )
		* ``editor_class``			<Item_Editor> 	Class of the Item_Editor to be instantiated ( only valid if can_edit == True )
		* ``column_can_hide``		<Bool> 	Can the column representation be hidden ( or is it required to be shown )
		* ``column_can_move``		<Bool>	Can column representation be re-ordered by drag
		* ``column_is_shown``		<Bool>	Default column representation hidden state
		* ``column_category``		<String> This allows for logical groupings when creating a column choosing UI
		* ``column_width_min``		<Int>		0 for auto header/content
		* ``column_width_default``	<Int> 	Default width to initialize column at
		* ``column_to_resize``		<Item_Accessor> Item Accessor instance to use for resizing instead of this one ( for fixed-width columns )
		* ``column_width_auto``		<Bool>	Stretch this column to fit in the space provided ( only applies to column in last position )
	"""

	CLASS_LABEL = '- no label -'

	def __init__( self,
	              label = None,
	              id_string = None,
	              data_type = vlib.ui.lister_lib2.const.DATA_TYPE_STRING,
	              can_edit = False,				# Allow set_value to be called ( also controls value editing popup in Grid )
	              editor_class = None,
	              editor_widget_kwargs = None,
	              column_can_hide = True,		# Can the column representation be hidden ( or is it required to be shown )
	              column_can_move = True,		# Can the column representation be moved
	              column_is_shown = True,		# Is the column representation shown by default
	              column_category = None,		# This allows for logical groupings when creating a column choosing UI
	              column_width_min = 50,		# Minimum allowed width for column representation
	              column_width_default = 50,	# Starting width for column representation
	              column_to_resize = None,		# The column to redirect resizing behavior to; used to make fixed-width columns
	              column_width_auto = False	# If in the last position, should the column expand to fill the window
	              ):

		if label is None:
			label = self.CLASS_LABEL

		self.label			= label
		self.data_type		= data_type
		self.can_edit		= can_edit
		self.editor_class	= editor_class
		self.editor_widget_kwargs = editor_widget_kwargs

		if id_string is None:
			# Provide a unique identifier if none is provided
			id_string = str( uuid.uuid4( ) )
		self.id_string = id_string

		#=====================================================================
		# Column related attributes
		self.column_can_hide		= column_can_hide
		self.column_can_move		= column_can_move
		self.column_is_shown		= column_is_shown
		self.column_category		= column_category
		self.column_to_resize	= column_to_resize
		self.column_width_auto	= column_width_auto

		# If neither is an auto size, ensure default is >= min.
		if ( column_width_min > 0 ) and ( column_width_default > 0 ):
			column_width_default = max( column_width_default, column_width_min )

		self.column_width_default = column_width_default
		self.column_width_min = column_width_min
		#=====================================================================

	def get_editor_class_for_item( self, item, for_renderer = False ):
		return None


	def get_editor_widget_kwargs_for_item( self, item, widget_class = None ):
		return self.editor_widget_kwargs


	def get_accessor_label( self ):
		return self.label


	def get_accessor_id( self ):
		return self.id_string


	def get_accessor_data_type( self ):
		return self.data_type


	#=====================================================================
	# Sorting

	def _sort_children( self, items ):
		sort_list = sorted( items, key = lambda item: str( self.get_display_value( item ) ).lower( ) )

		return sort_list


	def get_sorted_items( self, items ):
		sorted_items = [ ]
		sorted_items.extend( self._sort_children( items ) )

		return sorted_items

	#=====================================================================
	# Gets

	def get_value( self, item ):
		value = item
		return value


	def get_values( self, item ):
		return [ ] # Majorily used by enum editors


	def get_display_value( self, item ):
		value = ''

		try:
			if hasattr( item, 'display_name' ):
				value = item.display_name
			else:
				value = str( self.get_value( item ) )
		except TypeError:
			value = vlib.ui.lister_lib2.const.LABEL_MISSING

		return value


	#=====================================================================
	# Sets

	def set_value( self, item, value ):
		"""
		OVERWRITE THIS

		This is how the accessor should edit the item.  It takes the item
		and will assign the value to that item.  It should be custom built
		for your data type

		**Arguments:**

			:``item``: `Any` Your custom data that you are going to edit with this new value
			:``value``: `Any` Your custom value to be assigned to the item

		**Keyword Arguments:**

			None

		**Returns:**

			None

		:type item: Any
		:type value: Any
		"""
		if self.can_edit:
			# Not implemented
			pass


	def set_column_to_resize( self, item_accessor ):
		"""
		Set the passed in item accessor as the column to resize instead of this column.
		Will effectively make this column fixed-width.

		*Arguments:*
			* ``item_accessor`` The item accessor (column) to resize instead of this
		"""

		self.column_to_resize = item_accessor


	def is_expandable( self, item ):
		"""
		determine whether an item can have child items

		*Arguments:*
			* ``item`` the item to check

		*Keyword Arguments:*
			* <none>

		*Returns:*
			* ``bool`` True if the item can have children, False otherwise
		"""

		if isinstance( item, vlib.types.Base_Parent ):
			return item.has_children( )
		return False


	def get_parent( self, item ):
		parent = None

		try:
			if isinstance( item, vlib.types.Base_Parent ):
				parent = item.get_parent( )
		except AttributeError:
			# Not an instance of vlib.types.Base_Child;  and that is ok.
			pass

		return parent


	def get_parents_recursive( self, item ):
		parents = [ ]

		if isinstance( item, vlib.types.Base_Parent ):
			parent = self.get_parent( item )
			if parent:
				parents.append( parent )
				parents.extend( self.get_parents_recursive( parent ) )

		return parents


	def get_children( self, item ):
		children = [ ]

		try:
			if isinstance( item, vlib.types.Base_Parent ):
				children = item.get_children( )
		except AttributeError:
			# Not an instance of vlib.types.Base_Child;  and that is ok.
			pass

		return children


	def get_children_recursive( self, item ):
		children = [ ]

		for child in self.get_children( item ):
			children.append( child )
			children.extend( self.get_children_recursive( child ) )

		return children


	def validate_item( self, item, *args, **kwrgs ):
		"""
		OVERRIGHT this

		This runs the item and a possible set of args to see
		if the validators pass. This method should be overwritten
		in your Accessor.  You can make it as complex as you like
		but be sure that you handle the args and kwrgs.

		**Arguments:**

			:``item``: `Unknown` An item from Lister

		**Keyword Arguments:**

			None

		**Returns:**

			:``Bool``: `Bool` Did this item pass all validation

		@type item: Any
		"""
		return True


class Tree_Item_Accessor( Item_Accessor ):
	def _sort_children( self, items ):
		"""
		Method for sorting a group of items that are to be displayed as siblings.

		*Arguments:*
			* ``items`` list of sibling items

		*Keyword Arguments:*
			* <none>

		*Returns:*
			* ``sort_list`` a sorted list of items
		"""

		sort_list = sorted( items, key = lambda item: vlib.string.natsort_key( self.get_display_value( item ).lower( ) ) )

		return sort_list


	def get_parent( self, item ):
		"""
		Get the parent of the input item

		*Arguments:*
			* ``item`` the item that you're looking at

		*Keyword Arguments:*
			* <none>

		*Returns:*
			* ``parent`` the parent of the input item
		"""

		parent = None

		try:
			parent = item.get_parent( )
		except AttributeError:
			# Not an instance of vlib.types.Base_Child, this is fine
			pass

		return parent


	def get_parents_recursive( self, item ):
		"""
		Get all parents of item, recursively

		*Arguments:*
			* ``item`` the item for which to get parents

		*Keyword Arguments:*
			* <none>

		*Returns:*
			* ``parents`` sequence of parents, in order by proximity to item
		"""

		parents = [ ]

		parent = self.get_parent( item )
		if parent:
			parents.append( parent )
			parents.extend( self.get_parents_recursive( parent ) )

		return parents


	def get_children( self, item ):
		"""
		Get all children of an input item

		*Arguments:*
			* ``item`` the item for which to get children

		*Keyword Arguments:*
			* <none>

		*Returns:*
			* ``children`` Children of item, if it has any.
		"""

		children = [ ]

		try:
			children = item.get_children( )
		except AttributeError:
			# Not an instance of vlib.types.Base_Parent;  and that is ok.
			pass

		return children


	def get_children_recursive( self, item ):
		"""
		Get all items that are hierarchically descendended from item (below it in
		the data tree).

		*Arguments:*
			* ``item`` the node in the tree at which to start looking for children

		*Keyword Arguments:*
			* <none>

		*Returns:*
			* ``children`` a list of all child/grand-child/[great]*n-grand-child nodes to item
		"""

		children = [ ]

		for child in self.get_children( item ):
			children.append( child )
			children.extend( self.get_children_recursive( child ) )

		return children


class Item_Collection( object ):
	"""
	No pre-existing comment here, so leaving information on arg that I added
	Tyler Good, tyler.good@volition-inc.com, 1/15/2014 10:05:48 AM,

	``item_accessor_class`` : A class that can be instantiated to create an item accessor for this collection, if one is not provided in the arguments.
	:``filter_with_all_columns``:	`bool` Set this to True to use all columns in the column collection to filter the item collection
	"""
	def __init__( self, item_accessor_or_collection = None, items = None, filters = None, sort_accessor = None,
	              item_accessor_class = Item_Accessor, filter_with_all_columns = False ):

		self._filters = [ ]

		if items is None:
			items = [ ]

		if filters is None:
			filters = [ ]

		self.filter_with_all_columns = filter_with_all_columns

		item_accessor = None
		item_accessor_collection = None

		# Firstly, did we get a collection?
		if isinstance( item_accessor_or_collection, Item_Accessor_Collection ):
			item_accessor_collection = item_accessor_or_collection

			# If so, the default item accessor may already be within
			item_accessor = item_accessor_collection.default_accessor

		elif isinstance( item_accessor_or_collection, Item_Accessor ):
			item_accessor = item_accessor_or_collection

		# If we still don't have an item accessor, it is time to make one from the supplied class
		if item_accessor is None:
			item_accessor = item_accessor_class( )

		# Still no item accessor collection? make one.
		if item_accessor_collection is None:
			item_accessor_collection = Item_Accessor_Collection( default_accessor = item_accessor, sort_accessor = sort_accessor )

		else:
			# Ensure the default & sort accessors are in the Item_Accessor_Collection and marked accordingly
			# TODO: Sort accessor? does this make sense? resolve to perhaps instantiate a collection and nothing else
			item_accessor_collection.default_accessor = item_accessor
			item_accessor_collection.sort_accessor = sort_accessor
			item_accessor_collection.add_accessors( [ item_accessor, sort_accessor ] )

		self._items_raw = [ ]
		self._item_accessor = item_accessor
		self._item_accessor_collection = item_accessor_collection
		self.set_filters( filters )
		self.string_filter = None

		for f in filters:
			if isinstance( f, Filter_String_Value ):
				self.string_filter = f
				break

		self.dict_last_item = { } #
		self.dict_items_expanded = { } # { item	: bool, ... }
		self.dict_items_child_count = { } # { item	: child_count }
		self.rebuild_queue = set( )
		self.recount_queue = set( )
		self.set_items( items )

		self.sort_state = 0 # Sort A-Z, 0-10, etc...
		self.sort_accessor = sort_accessor or self._item_accessor


	def get_item_accessor_collection( self ):
		return self._item_accessor_collection


	def _flatten_item_list( self, items ):
		flat_list = [ ]
		idx = 0
		last_idx = len( items ) - 1

		if self.filter_with_all_columns:
			filter_accessors = self._item_accessor_collection.get_accessors( )
		else:
			filter_accessors = [ self._item_accessor ]

		for i in items:
			can_display = True

			for f in [ item_filter for item_filter in self._filters if item_filter.get_enabled( ) ]:
				can_display = any( f.check_item_passes( i, accessor ) for accessor in filter_accessors )
				if not can_display:
					break

			self.dict_last_item[ i ] = ( idx == last_idx )

			if can_display:
				flat_list.append( i )

				expandable = self._item_accessor.is_expandable( i )

				if expandable:
					if self.get_or_set_item_expanded( i ):
						item_children = self._item_accessor.get_children( i )

						flat_list.extend( self._flatten_item_list( item_children ) )

			idx += 1

		return flat_list


class Anim_Lister_Base( ctg.lister_lib.core.Lister_Base ):
	def __init__( self, *args, **kwargs ):
		self.color_chooser = None

		kwargs.update( { 'column_chooser_size' : ( 240, 300 ) } )

		ctg.lister_lib.core.Lister_Base.__init__( self, *args, **kwargs )

		self.SetDefaultCellBackgroundColour( wx.Colour( 150, 150, 150 ) )
		self.SetDoubleBuffered( True )
		self.active_popup_message = None

		doc = AnimationEditor.get_active_document( )
		if doc:
			doc.event_manager.register_control( self )

		self.callback_dict = { \
			'ae doc closing'	: self.on_document_close,
		}

		#bind clip events
		self.Bind( ctg.ae2.ui.events.EVT_AE_CLIP_SELECT, 						self.on_active_clip_changed )
		self.Bind( ctg.ae2.ui.events.EVT_AE_CLIP_UPDATE, 						self.on_active_clip_update )

		#bind tag undo/redo event
		self.Bind( ctg.ae2.ui.events.EVT_AE_TAG_MODIFIED, 						self.on_tag_modified )

		#bind state tag events
		self.Bind( ctg.ae2.ui.events.EVT_AE_STATE_TAG_SELECT, 				self.on_active_state_tag_changed )
		self.Bind( ctg.ae2.ui.events.EVT_AE_STATE_TAG_CREATED, 				self.on_state_tag_created )
		self.Bind( ctg.ae2.ui.events.EVT_AE_STATE_TAG_RENAMED, 				self.on_state_tag_renamed )
		self.Bind( ctg.ae2.ui.events.EVT_AE_STATE_TAG_DELETED, 				self.on_state_tag_deleted )

		#bind action tag events
		self.Bind( ctg.ae2.ui.events.EVT_AE_ACTION_TAG_SELECT, 				self.on_active_action_tag_changed )
		self.Bind( ctg.ae2.ui.events.EVT_AE_ACTION_TAG_CREATED, 				self.on_action_tag_created )
		self.Bind( ctg.ae2.ui.events.EVT_AE_ACTION_TAG_RENAMED, 				self.on_action_tag_renamed )
		self.Bind( ctg.ae2.ui.events.EVT_AE_ACTION_TAG_DELETED, 				self.on_action_tag_deleted )

		#bind control filter events
		self.Bind( ctg.ae2.ui.events.EVT_AE_CONTROL_FILTER_SELECT, 			self.on_active_control_filter_changed )
		self.Bind( ctg.ae2.ui.events.EVT_AE_CONTROL_FILTER_CREATED, 		self.on_control_filter_created )
		self.Bind( ctg.ae2.ui.events.EVT_AE_CONTROL_FILTER_RENAMED, 		self.on_control_filter_renamed )
		self.Bind( ctg.ae2.ui.events.EVT_AE_CONTROL_FILTER_DELETED, 		self.on_control_filter_deleted )
		self.Bind( ctg.ae2.ui.events.EVT_AE_CONTROL_FILTER_MODIFIED, 		self.on_control_filter_modified )

		#bind control parameter events
		self.Bind( ctg.ae2.ui.events.EVT_AE_CONTROL_PARAMETER_SELECT, 		self.on_active_control_parameter_changed )
		self.Bind( ctg.ae2.ui.events.EVT_AE_CONTROL_PARAMETER_CREATED, 	self.on_control_parameter_created )
		self.Bind( ctg.ae2.ui.events.EVT_AE_CONTROL_PARAMETER_RENAMED, 	self.on_control_parameter_renamed )
		self.Bind( ctg.ae2.ui.events.EVT_AE_CONTROL_PARAMETER_DELETED, 	self.on_control_parameter_deleted )
		self.Bind( ctg.ae2.ui.events.EVT_AE_CONTROL_PARAMETER_MODIFIED, 	self.on_control_parameter_modified )

		#bine node graph events
		self.Bind( ctg.ae2.ui.events.EVT_AE_NODE_GRAPH_DEPENDENTS_MODIFIED, self.on_node_graph_dependents_modified )

		#bind state machine events
		self.Bind( ctg.ae2.ui.events.EVT_AE_STATE_MACHINE_SELECT, 			self.on_active_state_machine_changed )
		self.Bind( ctg.ae2.ui.events.EVT_AE_STATE_MACHINE_CREATED, 			self.on_state_machine_created )
		self.Bind( ctg.ae2.ui.events.EVT_AE_STATE_MACHINE_RENAMED, 			self.on_state_machine_renamed )
		self.Bind( ctg.ae2.ui.events.EVT_AE_STATE_MACHINE_DELETED, 			self.on_state_machine_deleted )
		self.Bind( ctg.ae2.ui.events.EVT_AE_STATE_MACHINE_MODIFIED, 		self.on_state_machine_modified )

		#bind blend tree events
		self.Bind( ctg.ae2.ui.events.EVT_AE_BLEND_TREE_SELECT, 				self.on_active_blend_tree_changed )
		self.Bind( ctg.ae2.ui.events.EVT_AE_BLEND_TREE_CREATED, 				self.on_blend_tree_created )
		self.Bind( ctg.ae2.ui.events.EVT_AE_BLEND_TREE_RENAMED, 				self.on_blend_tree_renamed )
		self.Bind( ctg.ae2.ui.events.EVT_AE_BLEND_TREE_DELETED, 				self.on_blend_tree_deleted )
		self.Bind( ctg.ae2.ui.events.EVT_AE_BLEND_TREE_MODIFIED, 			self.on_blend_tree_modified )

		#bind group events
		self.Bind( ctg.ae2.ui.events.EVT_AE_GROUP_SELECT, 						self.on_active_group_changed )
		self.Bind( ctg.ae2.ui.events.EVT_AE_GROUP_CREATED,						self.on_anim_group_created )
		self.Bind( ctg.ae2.ui.events.EVT_AE_GROUP_RENAMED,						self.on_anim_group_renamed )
		self.Bind( ctg.ae2.ui.events.EVT_AE_GROUP_DELETED,						self.on_anim_group_renamed )

		#bind set events
		self.Bind( ctg.ae2.ui.events.EVT_AE_SET_SELECT, 						self.on_active_set_changed )
		self.Bind( ctg.ae2.ui.events.EVT_AE_SET_CREATED,						self.on_anim_set_created )
		self.Bind( ctg.ae2.ui.events.EVT_AE_SET_RENAMED, 						self.on_anim_set_renamed )
		self.Bind( ctg.ae2.ui.events.EVT_AE_SET_DELETED, 						self.on_anim_set_renamed )
		self.Bind( ctg.ae2.ui.events.EVT_AE_SET_MODIFIED, 						self.on_anim_set_modified )

		#bind tag association events
		self.Bind( ctg.ae2.ui.events.EVT_AE_TAG_ASSOCIATION_CREATED,		self.on_tag_association_created )
		self.Bind( ctg.ae2.ui.events.EVT_AE_TAG_ASSOCIATION_MODIFIED, 		self.on_tag_association_modified )
		self.Bind( ctg.ae2.ui.events.EVT_AE_TAG_ASSOCIATION_UPDATED, 		self.on_tag_association_updated )
		self.Bind( ctg.ae2.ui.events.EVT_AE_TAG_ASSOCIATION_DELETED, 		self.on_tag_association_deleted )

		#named value events
		self.Bind( ctg.ae2.ui.events.EVT_AE_NAMED_VALUED_SELECT, 			self.on_named_value_changed )
		self.Bind( ctg.ae2.ui.events.EVT_AE_NAMED_VALUED_CREATED,			self.on_named_value_created )
		self.Bind( ctg.ae2.ui.events.EVT_AE_NAMED_VALUED_RENAMED,			self.on_named_value_renamed )
		self.Bind( ctg.ae2.ui.events.EVT_AE_NAMED_VALUED_DELETED,			self.on_named_value_deleted )
		self.Bind( ctg.ae2.ui.events.EVT_AE_NAMED_VALUED_MODIFIED,			self.on_named_value_modified )

		#rig bone events
		self.Bind( ctg.ae2.ui.events.EVT_AE_RIG_BONE_SELECT, 			      self.on_rig_bone_selected )
		self.Bind( ctg.ae2.ui.events.EVT_AE_RIG_BONE_MODIFIED,			   self.on_rig_bone_modified )

		self._register_callbacks( )
		self.setup_column_prefs( )
		self.update_table( get_selection = True, get_objects = True )
		self.SetDefaultRowSize( 22 )

		#bind on colunm resize
		self.Bind( wx.grid.EVT_GRID_COL_SIZE, self.on_column_resize_save_col_prefs )


	def fade_popup( self ):
		if self.active_popup_message:
			self.active_popup_message.start_fade( )


	def popup_message( self, *args, **kwargs ):
		if isinstance( self.active_popup_message, ctg.ui.util.popup_message ):
			self.active_popup_message.close( )
		self.active_popup_message = ctg.ui.util.popup_message( self, *args, **kwargs )


	def crunch( self, objs, message = False ):
		import _resourcelib
		filename			= None
		filenames 		= [ ]

		doc = AnimationEditor.get_active_document( )
		if not doc:
			return

		# Get only valid clips to crunch
		for obj in objs:
			if isinstance( obj, ctg.ae2.core.data.Clip_Item ):
				if doc.is_clip( obj.get_name( ) ):
					filenames.append( ( obj.get_name( ) + '.anim.fbx' ) )

		if len( filenames ) > 0:
			wx.SetCursor( wx.StockCursor( wx.CURSOR_WAIT ) )

			# Display a message over the viewport
			if message:
				if isinstance( self.active_popup_message, ctg.ui.util.popup_message ):
					self.active_popup_message.close( )
				self.parent.self.active_popup_message = ctg.ui.util.popup_message( message = 'Crunching:  "{0}"'.format( filenames ), fade_out_time = 300 )

			# Crunch
			_resourcelib.crunch_files( filenames, False )

			wx.SetCursor( wx.StockCursor( wx.CURSOR_ARROW ) )

			# Close the message
			if message:
				self.fade_popup( )


	def on_column_resize_save_col_prefs( self, event ):
		#save column pref on rezise
		self.save_column_prefs( )

		if event:
			event.Skip( )


	def get_pane_callback_id( self ):
		return ctg.ae2.ui.const.PANE_LISTENER_CALLBACK_ID


	def _init_renderer( self ):
		self._renderer = ctg.ae2.ui.renderer.Default_Renderer( self )


	def on_tag_association_created( self, event ):
		event.Skip( )


	def on_tag_association_modified( self, event ):
		event.Skip( )


	def on_tag_association_updated( self, event ):
		event.Skip( )


	def on_tag_association_deleted( self, event ):
		event.Skip( )


	def on_active_clip_changed( self, event ):
		#print( 'EVT_AE_CLIP_SELECT: \'{0}\' received by object {1}'.format( event.get_data_obj( ).get_name( ), self ) )
		event.Skip( )


	def on_active_clip_update( self, event ):
		#print( 'EVT_AE_CLIP_SELECT: \'{0}\' received by object {1}'.format( event.get_data_obj( ).get_name( ), self ) )
		event.Skip( )


	def on_active_control_filter_changed( self, event ):
		#print( 'EVT_AE_CONTROL_FILTER_SELECT: \'{0}\' received by object {1}'.format( event.get_data_obj( ), self ) )
		event.Skip( )


	def on_control_filter_created( self, event ):
		#print( 'EVT_AE_CONTROL_FILTER_CREATED: \'{0}\' received by object {1}'.format( event.get_data_obj( ), self ) )
		event.Skip( )


	def on_control_filter_renamed( self, event ):
		#print( 'EVT_AE_CONTROL_FILTER_RENAMED: \'{0}\' received by object {1}'.format( event.get_data_obj( ), self ) )
		event.Skip( )


	def on_control_filter_modified( self, event ):
		#print( 'EVT_AE_CONTROL_FILTER_modified: \'{0}\' received by object {1}'.format( event.get_data_obj( ), self ) )
		event.Skip( )


	def on_control_filter_deleted( self, event ):
		#print( 'EVT_AE_CONTROL_FILTER_DELETED: \'{0}\' received by object {1}'.format( event.get_data_obj( ), self ) )
		event.Skip( )


	def on_active_control_parameter_changed( self, event ):
		#print( 'EVT_AE_CONTROL_PARAMETER_SELECT: \'{0}\' received by object {1}'.format( event.get_data_obj( ), self ) )
		event.Skip( )


	def on_control_parameter_created( self, event ):
		#print( 'EVT_AE_CONTROL_PARAMETER_CREATED: \'{0}\' received by object {1}'.format( event.get_data_obj( ), self ) )
		event.Skip( )


	def on_control_parameter_renamed( self, event ):
		#print( 'EVT_AE_CONTROL_PARAMETER_RENAMED: \'{0}\' received by object {1}'.format( event.get_data_obj( ), self ) )
		event.Skip( )


	def on_control_parameter_deleted( self, event ):
		#print( 'EVT_AE_CONTROL_PARAMETER_DELETED: \'{0}\' received by object {1}'.format( event.get_data_obj( ), self ) )
		event.Skip( )


	def on_control_parameter_modified( self, event ):
		#print( 'EVT_AE_CONTROL_PARAMETER_Modified: \'{0}\' received by object {1}'.format( event.get_data_obj( ), self ) )
		event.Skip( )


	def on_node_graph_dependents_modified( self, event ):
		event.Skip( )


	def on_active_state_machine_changed( self, event ):
		#print( 'EVT_AE_STATE_MACHINE_SELECT: \'{0}\' received by object {1}'.format( event.get_data_obj( ), self ) )
		event.Skip( )


	def on_state_machine_modified( self, event ):
		#print( 'EVT_AE_STATE_MACHINE_MODIFIED: \'{0}\' received by object {1}'.format( event.get_data_obj( ), self ) )
		event.Skip( )


	def on_state_machine_created( self, event ):
		#print( 'EVT_AE_STATE_MACHINE_SELECT: \'{0}\' received by object {1}'.format( event.get_data_obj( ), self ) )
		event.Skip( )


	def on_state_machine_renamed( self, event ):
		#print( 'EVT_AE_STATE_MACHINE_SELECT: \'{0}\' received by object {1}'.format( event.get_data_obj( ), self ) )
		event.Skip( )


	def on_state_machine_deleted( self, event ):
		#print( 'EVT_AE_STATE_MACHINE_SELECT: \'{0}\' received by object {1}'.format( event.get_data_obj( ), self ) )
		event.Skip( )


	def on_active_blend_tree_changed( self, event ):
		#print( 'EVT_AE_BLEND_TREE_SELECT: \'{0}\' received by object {1}'.format( event.get_data_obj( ), self ) )
		event.Skip( )


	def on_blend_tree_created( self, event ):
		#print( 'EVT_AE_BLEND_TREE_SELECT: \'{0}\' received by object {1}'.format( event.get_data_obj( ), self ) )
		event.Skip( )


	def on_blend_tree_renamed( self, event ):
		#print( 'EVT_AE_BLEND_TREE_SELECT: \'{0}\' received by object {1}'.format( event.get_data_obj( ), self ) )
		event.Skip( )


	def on_blend_tree_deleted( self, event ):
		#print( 'EVT_AE_BLEND_TREE_SELECT: \'{0}\' received by object {1}'.format( event.get_data_obj( ), self ) )
		event.Skip( )


	def on_blend_tree_modified( self, event ):
		#print( 'EVT_AE_BLEND_TREE_Modified: \'{0}\' received by object {1}'.format( event.get_data_obj( ), self ) )
		event.Skip( )


	def on_active_state_tag_changed( self, event ):
		#print( 'EVT_AE_STATE_TAG_SELECT: \'{0}\' received by object {1}'.format( event.get_data_obj( ), self ) )
		event.Skip( )


	def on_tag_modified( self, event ):
		#print( 'EVT_AE_TAG_MODIFIED: \'{0}\' received by object {1}'.format( event.get_data_obj( ), self ) )
		event.Skip( )


	def on_state_tag_created( self, event ):
		#print( 'EVT_AE_STATE_TAG_CREATED: \'{0}\' received by object {1}'.format( event.get_data_obj( ), self ) )
		event.Skip( )


	def on_state_tag_renamed( self, event ):
		#print( 'EVT_AE_STATE_TAG_RENAMED: \'{0}\' received by object {1}'.format( event.get_data_obj( ), self ) )
		event.Skip( )


	def on_state_tag_deleted( self, event ):
		#print( 'EVT_AE_STATE_TAG_DELETED: \'{0}\' received by object {1}'.format( event.get_data_obj( ), self ) )
		event.Skip( )


	def on_active_action_tag_changed( self, event ):
		#print( 'EVT_AE_ACTION_TAG_SELECT: \'{0}\' received by object {1}'.format( event.get_data_obj( ), self ) )
		event.Skip( )


	def on_action_tag_created( self, event ):
		#print( 'EVT_AE_ACTION_TAG_CREATED: \'{0}\' received by object {1}'.format( event.get_data_obj( ), self ) )
		event.Skip( )


	def on_action_tag_renamed( self, event ):
		#print( 'EVT_AE_ACTION_TAG_RENAMED: \'{0}\' received by object {1}'.format( event.get_data_obj( ), self ) )
		event.Skip( )


	def on_action_tag_deleted( self, event ):
		#print( 'EVT_AE_ACTION_TAG_DELETED: \'{0}\' received by object {1}'.format( event.get_data_obj( ), self ) )
		event.Skip( )


	def on_active_group_changed( self, event ):
		#print( 'EVT_AE_GROUP_SELECT: \'{0}\' received by object {1}'.format( event.get_data_obj( ), self ) )
		event.Skip( )


	def on_anim_group_created( self, event, operation = None ):
		#print( 'EVT_AE_GROUP_CREATED: \'{0}\' received by object {1}'.format( event.get_data_obj( ), self ) )
		event.Skip( )


	def on_anim_group_renamed( self, event, operation = None ):
		#print( 'EVT_AE_GROUP_RENAMED: \'{0}\' received by object {1}'.format( event.get_data_obj( ), self ) )
		event.Skip( )


	def on_active_set_changed( self, event ):
		#print( 'EVT_AE_SET_SELECT: \'{0}\' received by object {1}'.format( event.get_data_obj( ), self ) )
		event.Skip( )


	def on_anim_set_created( self, event ):
		#print( 'EVT_AE_SET_CREATED: \'{0}\' received by object {1}'.format( event.get_data_obj( ), self ) )
		event.Skip( )


	def on_anim_set_renamed( self, event ):
		#print( 'EVT_AE_SET_RENAMED: \'{0}\' received by object {1}'.format( event.get_data_obj( ), self ) )
		event.Skip( )

	def on_anim_set_modified( self, event ):
		#print( 'EVT_AE_SET_MODIFIED: \'{0}\' received by object {1}'.format( event.get_data_obj( ), self ) )
		event.Skip( )


	def on_named_value_changed( self, event ):
		#print( 'EVT_AE_NAMED_VALUE_SELECT: \'{0}\' received by object {1}'.format( event.get_data_obj( ), self ) )
		event.Skip( )


	def on_named_value_created( self, event ):
		#print( 'EVT_AE_NAMED_VALUE_CREATED: \'{0}\' received by object {1}'.format( event.get_data_obj( ), self ) )
		event.Skip( )


	def on_named_value_renamed( self, event ):
		#print( 'EVT_AE_NAMED_VALUE_RENAMED: \'{0}\' received by object {1}'.format( event.get_data_obj( ), self ) )
		event.Skip( )


	def on_named_value_deleted( self, event ):
		#print( 'EVT_AE_NAMED_VALUE_DELETED: \'{0}\' received by object {1}'.format( event.get_data_obj( ), self ) )
		event.Skip( )

	def on_named_value_modified( self, event ):
		#print( 'EVT_AE_NAMED_VALUE_MODIFIED: \'{0}\' received by object {1}'.format( event.get_data_obj( ), self ) )
		event.Skip( )


	def on_rig_bone_selected( self, event ):
		#print( 'EVT_AE_RIG_BONE_SELECT: \'{0}\' received by object {1}'.format( event.get_data_obj( ), self ) )
		event.Skip( )

	def on_rig_bone_modified( self, event ):
		#print( 'EVT_AE_RIG_BONE_MODIFIED: \'{0}\' received by object {1}'.format( event.get_data_obj( ), self ) )
		event.Skip( )




	def on_key_down( self, event ):
		"""
		Event handler for key presses - here to intercept important doc-wide commands.

		*Arguments:*
			* ``event`` The event.
		"""

		key_code = event.GetKeyCode( )
		shift_down = event.ShiftDown( )
		alt_down = event.AltDown( )
		control_down = event.ControlDown( )

		# Only call up the chain if we haven't caught the event.
		result = ctg.ae2.util.handle_common_key_down_event( key_code, control_down, alt_down, shift_down )
		if result:
			event.Skip( )
		else:
			super( Anim_Lister_Base, self ).on_key_down( event )


	def _register_callbacks( self ):
		"""
		Registers pane callbacks.
		"""

		callback_id = self.get_pane_callback_id( )

		ctg.CALLBACK_SYSTEM.unregister_callbacks( callback_id )

		for callback, method in self.callback_dict.items( ):
			ctg.CALLBACK_SYSTEM.register_callback( callback_id, callback, method )


	def setup_column_prefs( self ):
		"""
		Set the default column preferences

		*Arguments:*
			* ``None`` Enter a description for the argument here.

		*Keyword Arguments:*
			* ``None`` Enter a description for the keyword argument here.

		*Returns:*
			* ``None`` If any, enter a description for the return value here.
		"""

		pass


	def get_column_prefs_widths_dict( self ):
		"""
		Get the column widths from the prefs

		*Arguments:*
			* ``None`` Enter a description for the argument here.

		*Keyword Arguments:*
			* ``None`` Enter a description for the keyword argument here.

		*Returns:*
			* ``Dict`` Dict of column ids/widths
		"""

		return {}


	def save_column_prefs( self ):
		"""
		Save the column widths

		*Arguments:*
			* ``None`` Enter a description for the argument here.

		*Keyword Arguments:*
			* ``None`` Enter a description for the keyword argument here.

		*Returns:*
			* ``None`` If any, enter a description for the return value here.
		"""

		if not ctg.prefs.user.get( 'global.animation_editor.package_choose', 'Any' ) or ctg.prefs.user.get( 'global.animation_editor.package_choose', 'Any' ) == 'Any':
			dlg = wx.MessageDialog( None, "Please choose a package in the ribbon for your work to be saved to.", caption = "Choose A Package", style = wx.OK | wx.ICON_INFORMATION )
			ctg.ui.dialogs.show_dialog_modal( dlg )
			dlg.Destroy( )


	def record_column_order( self ):
		"""
		Save the columns order

		*Arguments:*
			* ``None`` Enter a description for the argument here.

		*Keyword Arguments:*
			* ``None`` Enter a description for the keyword argument here.

		*Returns:*
			* ``None`` If any, enter a description for the return value here.
		"""

		pass


	def on_document_close( self, doc ):
		"""
		Handle operations when the document has closed

		*Arguments:*
			* ``doc`` The current document

		*Keyword Arguments:*
			* ``None`` Enter a description for the keyword argument here.

		*Returns:*
			* ``None`` If any, enter a description for the return value here.
		"""

		pass


	def create_color_chooser( self ):
		return ctg.ae2.ui.dialogs.Chooser_Dialog( self )


	def show_color_chooser( self, event = None, position = ( 0, 0 ), offset = ( 0, 0 ) ):
		"""
		Method for showing the color chooser.

		*Arguments:*
			* <none>

		*Keyword Arguments:*
			* ``event``			<event>
			* ``position``		<wxPoint> Position to spawn the Color Chooser Dialog at
			* ``offset``		<wxPoint> Offset to apply to the Color Chooser Dialog spawn position

		*Returns:*
			* <none>
		"""

		if self.color_chooser == None:
			win = self.create_color_chooser( )
			win.SetPosition( position )
			self.color_chooser = win
			win.Center( wx.CENTER_ON_SCREEN )
			win.Show( )
		else:
			self.color_chooser.SetFocus( )


	def hide_color_chooser( self, event = None ):
		"""
		Method for hiding the color chooser.

		*Arguments:*
			* <none>

		*Keyword Arguments:*
			* ``event``			<event>

		*Returns:*
			* <none>
		"""

		if self.color_chooser != None:
			self.color_chooser.on_close( None )


	def toggle_color_chooser( self, event = None, position = ( 0, 0 ), offset = ( 0, 0 ) ):
		"""
		Method for toggling the show/hide state of the color chooser.

		*Arguments:*
			* <none>

		*Keyword Arguments:*
			* ``event``			<event>
			* ``position``		<wxPoint> Position to spawn the Color Chooser Dialog at
			* ``offset``		<wxPoint> Offset to apply to the Color Chooser Dialog spawn position

		*Returns:*
			* <none>
		"""

		if self.color_chooser == None:
			self.show_color_chooser( position = position, offset = offset )
		else:
			self.hide_color_chooser( None )


	def on_color_chooser_hide( self, event = None ):
		"""
		Post color chooser hidden method.

		*Arguments:*
			* <none>

		*Keyword Arguments:*
			* ``event``		<event> Color Chooser Dialog closed event

		*Returns:*
			* <none>
		"""

		self.color_chooser = None



	def copy( self, data, node_type ):
		"""
		Copy's data to the clipboard with a specified type constant.

		*Arguments:*
			* ``data``				- data to copy to clipboard
			* ``node_type``		- node type constant

		*Keyword Arguments:*
			* none

		*Returns:*
			* none
		"""

		return ctg.ae2.core.ae_common_operations.copy( data, node_type )


	def get_data_from_clipboard( self, node_type ):
		"""
		Gets data from the clipboard for a specified type constant.

		*Arguments:*
			* ``node_type``		- node type constant

		*Keyword Arguments:*
			* none

		*Returns:*
			* none
		"""

		return ctg.ae2.core.ae_common_operations.get_data_from_clipboard( node_type )


	def hit_test( self, x_pos, y_pos ):
		'''
		This method gets the mouse hit position then returns a tuple of row and column
		indexes based on that position.(-1, -1) means there is not row or column the
		grid is empty.
		'''
		x, y = self.CalcUnscrolledPosition( x_pos, y_pos)
		col = self.XToCol( x )
		row = self.YToRow( y )

		return ( row, col )



	def refresh_properties_pane( self ):
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		if hasattr( doc, 'animation_properties_pane' ):
			doc.animation_properties_pane.refresh_ui()




class Anim_Tree( Anim_Lister_Base ):
	def __init__( self, *args, **kwargs ):
		tree_kwargs = { \
		   'lister_style'	: vlib.ui.lister_lib.const.STYLE_TREE,
		}
		kwargs.update( tree_kwargs )

		Anim_Lister_Base.__init__( self, *args, **kwargs )

		self.SetDefaultRenderer( ctg.ae2.ui.node.Node_Renderer( ) )

		self._node_buttons = [ vlib.ui.lister_lib.node.Node_Button_Expand( ) ]


	def on_selection_changed( self, event ):
		event.Skip( )


	def on_cell_double_click( self, event ):
		self.SetFocus( )
		row = event.GetRow( )
		shift_down = event.ShiftDown( )
		node = self.get_row_as_node( row )
		state = not node.is_expanded( )

		if shift_down:
			self.set_nodes_expanded_recursively( [ node ], state )
		else:
			self.set_node_expanded( node, state )

		event.Skip( False )



class Anim_Grid( Anim_Lister_Base ):
	def __init__( self, *args, **kwargs ):
		Anim_Lister_Base.__init__( self, *args, **kwargs )


class AE_Lister_Handler_Selection_Move( vlib.ui.lister_lib2.input.Handler_Selection_Move ):
	def setup_bindings( self ):
		super( AE_Lister_Handler_Selection_Move, self ).setup_bindings( )
		self.Bind( wx.EVT_LEFT_DCLICK, self.on_dclick_event )

	def on_dclick_event( self, event ):
		doc = AnimationEditor.get_active_document( )
		sel_objs = self.view.get_selection_manager( ).get_selection( )
		if sel_objs:

			# only post an event if the items are different
			data_obj = sel_objs[0].data_obj

			# post load event
			if isinstance( data_obj, ctg.ae2.core.data.State_Machine_Item ):
				doc.event_manager.post_state_machine_load_event( [ data_obj ], owner = ctg.ae2.ui.const.PANE_ID_ANIM_ASSET_MANAGER )

			elif isinstance( data_obj, ctg.ae2.core.data.Blend_Tree_Item ):
				doc.event_manager.post_blend_tree_load_event( [ data_obj ], owner = ctg.ae2.ui.const.PANE_ID_ANIM_ASSET_MANAGER )

		event.Skip( )


def set_colors( view ):

	renderer = view.get_renderer( )

	renderer.color_bg_border 				 = wx.Colour( 130, 130, 130 )
	renderer.color_bg_default 				 = wx.Colour( 105, 105, 105 )
	renderer.color_bg_default_odd 		 = wx.Colour( 85, 85, 85 )
	renderer.color_bg_selected 			 = wx.Colour( 35, 135, 0 )
	renderer.color_bg_selected_odd 		 = wx.Colour( 35, 135, 0 )
	renderer.color_tree_connections  	 = wx.Colour( 68, 68, 68 )
	renderer.color_txt_static				 = wx.Colour( 0, 130, 130 )
	renderer.color_view_color_top 		 = wx.Colour( 150, 150, 150 )
	renderer.color_view_color_bottom 	 = wx.Colour( 150, 150, 150 )
	renderer.pen_item_bg					    = wx.Pen( renderer.color_bg_border, 1 )



class Anim_Lister_Tree_Base( vlib.ui.lister_lib2.core.Tree ):
	def __init__( self, *args, **kwargs ):
		self.search_filter    = Filter_String_Value( )

		super( Anim_Lister_Tree_Base, self ).__init__( filters=[ self.search_filter ], *args, **kwargs )

		self.active_popup_message = None

		doc = AnimationEditor.get_active_document( )
		if doc:
			doc.event_manager.register_control( self )

		self.callback_dict = { }
		set_colors( self )

		self.search_keywords = [ '+', '>', '<', '%', '-' ]

		#bind clip events
		self.Bind( ctg.ae2.ui.events.EVT_AE_CLIP_SELECT, 						self.on_active_clip_changed )
		self.Bind( ctg.ae2.ui.events.EVT_AE_CLIP_UPDATE, 						self.on_active_clip_update )

		#bind keyword help event
		self.Bind( ctg.ae2.ui.events.EVT_AE_KEYWORD_DISPLAY,   self.on_display_keywords_help )

		#bind tag undo/redo event
		self.Bind( ctg.ae2.ui.events.EVT_AE_TAG_MODIFIED, 						self.on_tag_modified )

		#bind state tag events
		self.Bind( ctg.ae2.ui.events.EVT_AE_STATE_TAG_SELECT, 				self.on_active_state_tag_changed )
		self.Bind( ctg.ae2.ui.events.EVT_AE_STATE_TAG_CREATED, 				self.on_state_tag_created )
		self.Bind( ctg.ae2.ui.events.EVT_AE_STATE_TAG_RENAMED, 				self.on_state_tag_renamed )
		self.Bind( ctg.ae2.ui.events.EVT_AE_STATE_TAG_DELETED, 				self.on_state_tag_deleted )

		#bind action tag events
		self.Bind( ctg.ae2.ui.events.EVT_AE_ACTION_TAG_SELECT, 				self.on_active_action_tag_changed )
		self.Bind( ctg.ae2.ui.events.EVT_AE_ACTION_TAG_CREATED, 				self.on_action_tag_created )
		self.Bind( ctg.ae2.ui.events.EVT_AE_ACTION_TAG_RENAMED, 				self.on_action_tag_renamed )
		self.Bind( ctg.ae2.ui.events.EVT_AE_ACTION_TAG_DELETED, 				self.on_action_tag_deleted )

		#bind control filter events
		self.Bind( ctg.ae2.ui.events.EVT_AE_CONTROL_FILTER_SELECT, 			self.on_active_control_filter_changed )
		self.Bind( ctg.ae2.ui.events.EVT_AE_CONTROL_FILTER_CREATED, 		self.on_control_filter_created )
		self.Bind( ctg.ae2.ui.events.EVT_AE_CONTROL_FILTER_RENAMED, 		self.on_control_filter_renamed )
		self.Bind( ctg.ae2.ui.events.EVT_AE_CONTROL_FILTER_DELETED, 		self.on_control_filter_deleted )
		self.Bind( ctg.ae2.ui.events.EVT_AE_CONTROL_FILTER_MODIFIED, 		self.on_control_filter_modified )

		#bind control parameter events
		self.Bind( ctg.ae2.ui.events.EVT_AE_CONTROL_PARAMETER_SELECT, 		self.on_active_control_parameter_changed )
		self.Bind( ctg.ae2.ui.events.EVT_AE_CONTROL_PARAMETER_CREATED, 	self.on_control_parameter_created )
		self.Bind( ctg.ae2.ui.events.EVT_AE_CONTROL_PARAMETER_RENAMED, 	self.on_control_parameter_renamed )
		self.Bind( ctg.ae2.ui.events.EVT_AE_CONTROL_PARAMETER_DELETED, 	self.on_control_parameter_deleted )
		self.Bind( ctg.ae2.ui.events.EVT_AE_CONTROL_PARAMETER_MODIFIED, 	self.on_control_parameter_modified )

		#bine node graph events
		self.Bind( ctg.ae2.ui.events.EVT_AE_NODE_GRAPH_DEPENDENTS_MODIFIED, self.on_node_graph_dependents_modified )

		#bind state machine events
		self.Bind( ctg.ae2.ui.events.EVT_AE_STATE_MACHINE_SELECT, 			self.on_active_state_machine_changed )
		self.Bind( ctg.ae2.ui.events.EVT_AE_STATE_MACHINE_CREATED, 			self.on_state_machine_created )
		self.Bind( ctg.ae2.ui.events.EVT_AE_STATE_MACHINE_RENAMED, 			self.on_state_machine_renamed )
		self.Bind( ctg.ae2.ui.events.EVT_AE_STATE_MACHINE_DELETED, 			self.on_state_machine_deleted )
		self.Bind( ctg.ae2.ui.events.EVT_AE_STATE_MACHINE_MODIFIED, 		self.on_state_machine_modified )

		#bind blend tree events
		self.Bind( ctg.ae2.ui.events.EVT_AE_BLEND_TREE_SELECT, 				self.on_active_blend_tree_changed )
		self.Bind( ctg.ae2.ui.events.EVT_AE_BLEND_TREE_CREATED, 				self.on_blend_tree_created )
		self.Bind( ctg.ae2.ui.events.EVT_AE_BLEND_TREE_RENAMED, 				self.on_blend_tree_renamed )
		self.Bind( ctg.ae2.ui.events.EVT_AE_BLEND_TREE_DELETED, 				self.on_blend_tree_deleted )
		self.Bind( ctg.ae2.ui.events.EVT_AE_BLEND_TREE_MODIFIED, 			self.on_blend_tree_modified )

		#bind group events
		self.Bind( ctg.ae2.ui.events.EVT_AE_GROUP_SELECT, 						self.on_active_group_changed )
		self.Bind( ctg.ae2.ui.events.EVT_AE_GROUP_CREATED,						self.on_anim_group_created )
		self.Bind( ctg.ae2.ui.events.EVT_AE_GROUP_RENAMED,						self.on_anim_group_renamed )
		self.Bind( ctg.ae2.ui.events.EVT_AE_GROUP_DELETED,						self.on_anim_group_renamed )

		#bind set events
		self.Bind( ctg.ae2.ui.events.EVT_AE_SET_SELECT, 						self.on_active_set_changed )
		self.Bind( ctg.ae2.ui.events.EVT_AE_SET_CREATED,						self.on_anim_set_created )
		self.Bind( ctg.ae2.ui.events.EVT_AE_SET_RENAMED, 						self.on_anim_set_renamed )
		self.Bind( ctg.ae2.ui.events.EVT_AE_SET_DELETED, 						self.on_anim_set_renamed )
		self.Bind( ctg.ae2.ui.events.EVT_AE_SET_MODIFIED, 						self.on_anim_set_modified )

		#bind tag association events
		self.Bind( ctg.ae2.ui.events.EVT_AE_TAG_ASSOCIATION_CREATED,		self.on_tag_association_created )
		self.Bind( ctg.ae2.ui.events.EVT_AE_TAG_ASSOCIATION_MODIFIED, 		self.on_tag_association_modified )
		self.Bind( ctg.ae2.ui.events.EVT_AE_TAG_ASSOCIATION_UPDATED, 		self.on_tag_association_updated )
		self.Bind( ctg.ae2.ui.events.EVT_AE_TAG_ASSOCIATION_DELETED, 		self.on_tag_association_deleted )

		#named value events
		self.Bind( ctg.ae2.ui.events.EVT_AE_NAMED_VALUED_SELECT, 			self.on_named_value_changed )
		self.Bind( ctg.ae2.ui.events.EVT_AE_NAMED_VALUED_CREATED,			self.on_named_value_created )
		self.Bind( ctg.ae2.ui.events.EVT_AE_NAMED_VALUED_RENAMED,			self.on_named_value_renamed )
		self.Bind( ctg.ae2.ui.events.EVT_AE_NAMED_VALUED_DELETED,			self.on_named_value_deleted )
		self.Bind( ctg.ae2.ui.events.EVT_AE_NAMED_VALUED_MODIFIED,			self.on_named_value_modified )

		#rig bone events
		self.Bind( ctg.ae2.ui.events.EVT_AE_RIG_BONE_SELECT, 			      self.on_rig_bone_selected )
		self.Bind( ctg.ae2.ui.events.EVT_AE_RIG_BONE_MODIFIED,			   self.on_rig_bone_modified )

		#rig aux data events
		self.Bind( ctg.ae2.ui.events.EVT_AE_RIG_AUX_DATA_SELECT, 			self.on_rig_aux_data_selected )
		self.Bind( ctg.ae2.ui.events.EVT_AE_RIG_AUX_DATA_MODIFIED,			self.on_rig_aux_data_modified )
		self.Bind( ctg.ae2.ui.events.EVT_AE_RIG_AUX_DATA_DELETED,			self.on_rig_aux_data_deleted )

		#modifier events
		self.Bind( ctg.ae2.ui.events.EVT_AE_MODIFIER_SELECT, 			      self.on_modifier_selected )
		self.Bind( ctg.ae2.ui.events.EVT_AE_MODIFIER_DELETED, 			   self.on_modifier_deleted )

		self._register_callbacks( )


	def _init_input_handlers( self ):

		# Add Input Handlers; Must be in reverse order ( last added runs first )
		self.drag_handler = AE_Lister_Handler_Selection_Move( self )

		if self.show_column_headers:
			self.column_handler = vlib.ui.lister_lib2.input.Handler_Column_Headers( self )
		else:
			self.column_handler = None

		self.button_handler = vlib.ui.lister_lib2.input.Handler_Buttons( self )


	def strip_keywords_from_search( self, value ):
		new_value = ''
		results_value = { }

		for i in range( len( self.search_keywords ) ):
			if self.search_keywords[ i ] in value:
				results_value[ i ] = self.search_keywords[ i ]
				new_value = value.replace( self.search_keywords[ i ], ',' )

	def update_search_filter( self, event ):
		special_keywords = [ ]

		#if '>' in event.get_value( ):
			#special_keywords.append( '>' )

		#if '<' in event.get_value( ):
			#special_keywords.append( '<' )

		self.search_filter.set_string_value( event.get_value( ).lower( ) )
		self.update_item_collection( immediate = True )
		event.Skip( )

	def crunch( self, objs, message = False ):

		filename			= None
		filenames 		= [ ]

		doc = AnimationEditor.get_active_document( )
		if not doc:
			return

		# Get only valid clips to crunch
		for obj in objs:
			if isinstance( obj, ctg.ae2.core.data.Clip_Item ):
				if doc.is_clip( obj.get_name( ) ):
					filenames.append( ( obj.get_name( ) + '.anim.fbx' ) )

		if len( filenames ) > 0:
			wx.SetCursor( wx.StockCursor( wx.CURSOR_WAIT ) )

			# Display a message over the viewport
			if message:
				if isinstance( self.active_popup_message, ctg.ui.util.popup_message ):
					self.active_popup_message.close( )
				self.parent.active_popup_message = ctg.ui.util.popup_message( message = 'Crunching:  "{0}"'.format( filenames ), fade_out_time = 300 )

			# Crunch
			_resourcelib.crunch_files( filenames, False )

			wx.SetCursor( wx.StockCursor( wx.CURSOR_ARROW ) )

			# Close the message
			if message:
				self.fade_popup( )


	def get_pane_callback_id( self ):
		return ctg.ae2.ui.const.PANE_LISTENER_CALLBACK_ID


	def on_tag_association_created( self, event ):
		event.Skip( )


	def on_tag_association_modified( self, event ):
		event.Skip( )


	def on_tag_association_updated( self, event ):
		event.Skip( )


	def on_tag_association_deleted( self, event ):
		event.Skip( )


	def on_active_clip_changed( self, event ):
		#print( 'EVT_AE_CLIP_SELECT: \'{0}\' received by object {1}'.format( event.get_data_obj( ).get_name( ), self ) )
		event.Skip( )


	def on_active_clip_update( self, event ):
		#print( 'EVT_AE_CLIP_SELECT: \'{0}\' received by object {1}'.format( event.get_data_obj( ).get_name( ), self ) )
		event.Skip( )


	def on_display_keywords_help( self, event ):
		event.Skip( )


	def on_active_control_filter_changed( self, event ):
		#print( 'EVT_AE_CONTROL_FILTER_SELECT: \'{0}\' received by object {1}'.format( event.get_data_obj( ), self ) )
		event.Skip( )


	def on_control_filter_created( self, event ):
		#print( 'EVT_AE_CONTROL_FILTER_CREATED: \'{0}\' received by object {1}'.format( event.get_data_obj( ), self ) )
		event.Skip( )


	def on_control_filter_renamed( self, event ):
		#print( 'EVT_AE_CONTROL_FILTER_RENAMED: \'{0}\' received by object {1}'.format( event.get_data_obj( ), self ) )
		event.Skip( )


	def on_control_filter_modified( self, event ):
		#print( 'EVT_AE_CONTROL_FILTER_modified: \'{0}\' received by object {1}'.format( event.get_data_obj( ), self ) )
		event.Skip( )


	def on_control_filter_deleted( self, event ):
		#print( 'EVT_AE_CONTROL_FILTER_DELETED: \'{0}\' received by object {1}'.format( event.get_data_obj( ), self ) )
		event.Skip( )


	def on_active_control_parameter_changed( self, event ):
		#print( 'EVT_AE_CONTROL_PARAMETER_SELECT: \'{0}\' received by object {1}'.format( event.get_data_obj( ), self ) )
		event.Skip( )


	def on_control_parameter_created( self, event ):
		#print( 'EVT_AE_CONTROL_PARAMETER_CREATED: \'{0}\' received by object {1}'.format( event.get_data_obj( ), self ) )
		event.Skip( )


	def on_control_parameter_renamed( self, event ):
		#print( 'EVT_AE_CONTROL_PARAMETER_RENAMED: \'{0}\' received by object {1}'.format( event.get_data_obj( ), self ) )
		event.Skip( )


	def on_control_parameter_deleted( self, event ):
		#print( 'EVT_AE_CONTROL_PARAMETER_DELETED: \'{0}\' received by object {1}'.format( event.get_data_obj( ), self ) )
		event.Skip( )


	def on_control_parameter_modified( self, event ):
		#print( 'EVT_AE_CONTROL_PARAMETER_Modified: \'{0}\' received by object {1}'.format( event.get_data_obj( ), self ) )
		event.Skip( )


	def on_node_graph_dependents_modified( self, event ):
		event.Skip( )


	def on_active_state_machine_changed( self, event ):
		#print( 'EVT_AE_STATE_MACHINE_SELECT: \'{0}\' received by object {1}'.format( event.get_data_obj( ), self ) )
		event.Skip( )


	def on_state_machine_modified( self, event ):
		#print( 'EVT_AE_STATE_MACHINE_MODIFIED: \'{0}\' received by object {1}'.format( event.get_data_obj( ), self ) )
		event.Skip( )


	def on_state_machine_created( self, event ):
		#print( 'EVT_AE_STATE_MACHINE_SELECT: \'{0}\' received by object {1}'.format( event.get_data_obj( ), self ) )
		event.Skip( )


	def on_state_machine_renamed( self, event ):
		#print( 'EVT_AE_STATE_MACHINE_SELECT: \'{0}\' received by object {1}'.format( event.get_data_obj( ), self ) )
		event.Skip( )


	def on_state_machine_deleted( self, event ):
		#print( 'EVT_AE_STATE_MACHINE_SELECT: \'{0}\' received by object {1}'.format( event.get_data_obj( ), self ) )
		event.Skip( )


	def on_active_blend_tree_changed( self, event ):
		#print( 'EVT_AE_BLEND_TREE_SELECT: \'{0}\' received by object {1}'.format( event.get_data_obj( ), self ) )
		event.Skip( )


	def on_blend_tree_created( self, event ):
		#print( 'EVT_AE_BLEND_TREE_SELECT: \'{0}\' received by object {1}'.format( event.get_data_obj( ), self ) )
		event.Skip( )


	def on_blend_tree_renamed( self, event ):
		#print( 'EVT_AE_BLEND_TREE_SELECT: \'{0}\' received by object {1}'.format( event.get_data_obj( ), self ) )
		event.Skip( )


	def on_blend_tree_deleted( self, event ):
		#print( 'EVT_AE_BLEND_TREE_SELECT: \'{0}\' received by object {1}'.format( event.get_data_obj( ), self ) )
		event.Skip( )


	def on_blend_tree_modified( self, event ):
		#print( 'EVT_AE_BLEND_TREE_Modified: \'{0}\' received by object {1}'.format( event.get_data_obj( ), self ) )
		event.Skip( )


	def on_active_state_tag_changed( self, event ):
		#print( 'EVT_AE_STATE_TAG_SELECT: \'{0}\' received by object {1}'.format( event.get_data_obj( ), self ) )
		event.Skip( )


	def on_tag_modified( self, event ):
		#print( 'EVT_AE_TAG_MODIFIED: \'{0}\' received by object {1}'.format( event.get_data_obj( ), self ) )
		event.Skip( )


	def on_state_tag_created( self, event ):
		#print( 'EVT_AE_STATE_TAG_CREATED: \'{0}\' received by object {1}'.format( event.get_data_obj( ), self ) )
		event.Skip( )


	def on_state_tag_renamed( self, event ):
		#print( 'EVT_AE_STATE_TAG_RENAMED: \'{0}\' received by object {1}'.format( event.get_data_obj( ), self ) )
		event.Skip( )


	def on_state_tag_deleted( self, event ):
		#print( 'EVT_AE_STATE_TAG_DELETED: \'{0}\' received by object {1}'.format( event.get_data_obj( ), self ) )
		event.Skip( )


	def on_active_action_tag_changed( self, event ):
		#print( 'EVT_AE_ACTION_TAG_SELECT: \'{0}\' received by object {1}'.format( event.get_data_obj( ), self ) )
		event.Skip( )


	def on_action_tag_created( self, event ):
		#print( 'EVT_AE_ACTION_TAG_CREATED: \'{0}\' received by object {1}'.format( event.get_data_obj( ), self ) )
		event.Skip( )


	def on_action_tag_renamed( self, event ):
		#print( 'EVT_AE_ACTION_TAG_RENAMED: \'{0}\' received by object {1}'.format( event.get_data_obj( ), self ) )
		event.Skip( )


	def on_action_tag_deleted( self, event ):
		#print( 'EVT_AE_ACTION_TAG_DELETED: \'{0}\' received by object {1}'.format( event.get_data_obj( ), self ) )
		event.Skip( )


	def on_active_group_changed( self, event ):
		#print( 'EVT_AE_GROUP_SELECT: \'{0}\' received by object {1}'.format( event.get_data_obj( ), self ) )
		event.Skip( )


	def on_anim_group_created( self, event, operation = None ):
		#print( 'EVT_AE_GROUP_CREATED: \'{0}\' received by object {1}'.format( event.get_data_obj( ), self ) )
		event.Skip( )


	def on_anim_group_renamed( self, event, operation = None ):
		#print( 'EVT_AE_GROUP_RENAMED: \'{0}\' received by object {1}'.format( event.get_data_obj( ), self ) )
		event.Skip( )


	def on_active_set_changed( self, event ):
		#print( 'EVT_AE_SET_SELECT: \'{0}\' received by object {1}'.format( event.get_data_obj( ), self ) )
		event.Skip( )


	def on_anim_set_created( self, event ):
		#print( 'EVT_AE_SET_CREATED: \'{0}\' received by object {1}'.format( event.get_data_obj( ), self ) )
		event.Skip( )


	def on_anim_set_renamed( self, event ):
		#print( 'EVT_AE_SET_RENAMED: \'{0}\' received by object {1}'.format( event.get_data_obj( ), self ) )
		event.Skip( )

	def on_anim_set_modified( self, event ):
		#print( 'EVT_AE_SET_MODIFIED: \'{0}\' received by object {1}'.format( event.get_data_obj( ), self ) )
		event.Skip( )


	def on_named_value_changed( self, event ):
		#print( 'EVT_AE_NAMED_VALUE_SELECT: \'{0}\' received by object {1}'.format( event.get_data_obj( ), self ) )
		event.Skip( )


	def on_named_value_created( self, event ):
		#print( 'EVT_AE_NAMED_VALUE_CREATED: \'{0}\' received by object {1}'.format( event.get_data_obj( ), self ) )
		event.Skip( )


	def on_named_value_renamed( self, event ):
		#print( 'EVT_AE_NAMED_VALUE_RENAMED: \'{0}\' received by object {1}'.format( event.get_data_obj( ), self ) )
		event.Skip( )


	def on_named_value_deleted( self, event ):
		#print( 'EVT_AE_NAMED_VALUE_DELETED: \'{0}\' received by object {1}'.format( event.get_data_obj( ), self ) )
		event.Skip( )

	def on_named_value_modified( self, event ):
		#print( 'EVT_AE_NAMED_VALUE_MODIFIED: \'{0}\' received by object {1}'.format( event.get_data_obj( ), self ) )
		event.Skip( )


	def on_rig_bone_selected( self, event ):
		#print( 'EVT_AE_RIG_BONE_SELECT: \'{0}\' received by object {1}'.format( event.get_data_obj( ), self ) )
		event.Skip( )

	def on_rig_bone_modified( self, event ):
		#print( 'EVT_AE_RIG_BONE_MODIFIED: \'{0}\' received by object {1}'.format( event.get_data_obj( ), self ) )
		event.Skip( )

	def on_rig_aux_data_selected( self, event ):
		#print( 'EVT_AE_RIG_AUX_DATA_SELECT: \'{0}\' received by object {1}'.format( event.get_data_obj( ), self ) )
		event.Skip( )

	def on_rig_aux_data_deleted( self, event ):
		#print( 'EVT_AE_RIG_AUX_DATA_DELETED: \'{0}\' received by object {1}'.format( event.get_data_obj( ), self ) )
		event.Skip( )

	def on_rig_aux_data_modified( self, event ):
		#print( 'EVT_AE_RIG_AUX_DATA_MODIFIED: \'{0}\' received by object {1}'.format( event.get_data_obj( ), self ) )
		event.Skip( )

	def on_modifier_selected( self, event ):
		#print( 'EVT_AE_MODIFIER_SELECT: \'{0}\' received by object {1}'.format( event.get_data_obj( ), self ) )
		event.Skip( )

	def on_modifier_deleted( self, event ):
		#print( 'EVT_AE_MODIFIER_DELETED: \'{0}\' received by object {1}'.format( event.get_data_obj( ), self ) )
		event.Skip( )


	def on_key_down( self, event ):
		"""
		Event handler for key presses - here to intercept important doc-wide commands.

		*Arguments:*
			* ``event`` The event.
		"""

		key_code = event.GetKeyCode( )
		shift_down = event.ShiftDown( )
		alt_down = event.AltDown( )
		control_down = event.ControlDown( )

		# Only call up the chain if we haven't caught the event.
		result = ctg.ae2.util.handle_common_key_down_event( key_code, control_down, alt_down, shift_down )
		if result:
			event.Skip( )
		else:
			super( Anim_Lister_Tree_Base, self ).on_key_down( event )


	def _register_callbacks( self ):
		"""
		Registers pane callbacks.
		"""

		callback_id = self.get_pane_callback_id( )

		ctg.CALLBACK_SYSTEM.unregister_callbacks( callback_id )

		for callback, method in self.callback_dict.items( ):
			ctg.CALLBACK_SYSTEM.register_callback( callback_id, callback, method )



	def copy( self, data, node_type ):
		"""
		Copy's data to the clipboard with a specified type constant.

		*Arguments:*
			* ``data``				- data to copy to clipboard
			* ``node_type``		- node type constant

		*Keyword Arguments:*
			* none

		*Returns:*
			* none
		"""

		return ctg.ae2.core.ae_common_operations.copy( data, node_type )


	def get_data_from_clipboard( self, node_type ):
		"""
		Gets data from the clipboard for a specified type constant.

		*Arguments:*
			* ``node_type``		- node type constant

		*Keyword Arguments:*
			* none

		*Returns:*
			* none
		"""

		return ctg.ae2.core.ae_common_operations.get_data_from_clipboard( node_type )


	def hit_test( self, x_pos, y_pos ):
		'''
		This method gets the mouse hit position then returns a tuple of row and column
		indexes based on that position.(-1, -1) means there is not row or column the
		grid is empty.
		'''
		x, y = self.CalcUnscrolledPosition( x_pos, y_pos)
		col = self.XToCol( x )
		row = self.YToRow( y )

		return ( row, col )



	def refresh_properties_pane( self ):
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		if hasattr( doc, 'animation_properties_pane' ):
			doc.animation_properties_pane.refresh_ui()

