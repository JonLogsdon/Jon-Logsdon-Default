
#module imports
import os
import wx
import AnimationEditor
import ctg.ae2.ui.const
import ctg.ae2.core.ae_common_operations
import ctg.ui.dialogs
import vlib.debug
import re
import _resourcelib
import P4
import vlib.perforce

import vlib.data_enum
import vlib.enumerations
import vlib.ui.reflection
import vlib.reflection
import vlib.os
import vlib.prettyxml
import vlib.ui.widgets.panel
import xml.etree
from xml.etree import cElementTree



#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
## Generic Collection ##
#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

class Collection( object ):
	"""
	A generic collection construct.

	*Arguments:*
		* ``doc`` <animation_editor_doc> document

	*Keyword Arguments:*
		* ``none``
	"""

	def __init__( self, doc ):
		self.doc = doc
		self._item_dict = { }
		self.is_dirty = False
		self.update_collection( )
		pass



	def _gather_item_names( self ):
		"""
		Method to gather all of the item key names directly from the document (for updating the collection)
		This should be overridden.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``result`` <Set> All item names.
		"""

		return set( )


	def _create_item( self, name, **kwrgs ):
		"""
		Method to construct an item.
		This should be overridden.

		*Arguments:*
			* ``name`` `str` The name of the item

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``result`` <item> Created item

		*Examples:* ::
			return Item_Class( self.doc, name )
		"""

		return None


	def update_collection( self, clear_items = False ):
		"""
		Updates the collection by accessing the document data and adding/removing entries from the collection where necessary.

		This method is written in a way that will preserve the originally created items;
		Should items ever be displayed in tree form, this will play nice with lister_lib's node expand state caching.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``result`` <Dict> name (key) / item (value)
		"""

		if clear_items:
			self._item_dict.clear( )

		existing_items = set( self._item_dict.keys( ) )
		all_items = self._gather_item_names( )

		if not all_items:
			return {}

		# Remove pre-existing entries
		item_names = all_items.difference( existing_items )

		# Create new items as needed
		new_items_dict = { }
		for name in item_names:
			item_object = self._create_item( name )
			if item_object:
				new_items_dict[ name ] = item_object

		# items = [ self._create_item( name ) for name in item_names ]
		# Combine to dictionary
		# new_items_dict = dict( zip( item_names, items ) )

		# ######
		# possibly move this to _add_items method commented out above this method

		# Determine any clips that need to be removed from existing clip dictionary
		removed_items = existing_items.difference( all_items )

		for c in removed_items:
			if c in self._item_dict:
				self._item_dict.pop( c )

		# Update existing with new entries
		self._item_dict.update( new_items_dict )
		self.is_dirty = True

		return self._item_dict

		#return self._add_items( item_names, items, all_items )


	def get_items( self, use_cached = True ):
		"""
		Retrieves all Clip_Items in the collection.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``use_cached`` 	<Bool> Use cached results or get latest from document

		*Returns:*
			* ``result`` 		<List> All the Clip_Items in the collection
		"""

		if not use_cached:
			self.update_collection( )

		return self._item_dict.values( )


	def get_item_names( self, use_cached = True ):
		"""
		Retrieves a list of all the key names.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``use_cached`` 	<Bool> Use cached results or get latest from document

		*Returns:*
			* ``result`` 		<List> Key names
		"""

		if not use_cached:
			self.update_collection( )

		return self._item_dict.keys( )


	def get_item_by_name( self, name, use_cached = True ):
		"""
		Retrieves an item from the collection by name.

		*Arguments:*
			* ``name`` 			<String> Key name of the item to lookup.

		*Keyword Arguments:*
			* ``use_cached`` 	<Bool> Use cached results or get latest from document

		*Returns:*
			* ``result`` 		<item> or <None>
		"""

		if not use_cached:
			self.update_collection( )

		item = None
		#new_selection = [ data_obj for data_obj in data_objs if data_obj.get_name( ) in self.active_bookmarks ]
		items = [ value for key, value in self._item_dict.items( ) if name.lower( ) == key.lower( ) ]
		if items:
			if len( items ) > 0:
				item = items[0]

		return item


	def check_name_existance( self, name ):
		"""
		Check if the name exists, in the collection.

		*Arguments:*
			* ``name`` -Name to be check for its existance

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``bool`` -Returns True if the name exists, otherwise False
		"""

		if name in list( self.get_item_names() ):
			return True

		return False


	def get_unique_name( self, name ):
		"""
		Checks if the name exists in the collection, if the name exists adds an
		index and return it as new name, if the name does not exists in the
		collection, return the name.

		*Arguments:*
			* ``name`` -The initial name

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``unique name`` -The current unique name
		"""

		unique_name = name
		index = 1

		while self.check_name_existance( unique_name ):
			unique_name = '{0}{1}'.format( name, index )
			index += 1

		return unique_name


	def validate_name_pattern( self, name, pattern = set('$,;:/":.\`|@%&^*#)(!+-~=?><][}{') ):
		"""
		Checks the name for invalid characters.

		*Arguments:*
			* ``name`` -The name to be validated

		*Keyword Arguments:*
			* ``pattern`` -Set of characters, to check if they exists in the name.

		*Returns:*
			* ``bool`` -Returns True indicating the name is valid, otherwise False.
		"""

		s_char = "'"

		if any((char in pattern) for char in name) or s_char in name:
			return False
		else:
			return True


	def validate_name( self, name ):
		"""
		This Method checks the name for invalid characters, also checks if
		the name exists in the collection.

		*Arguments:*
			* ``name`` -name to be validated

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``bool`` -True indicates the name is valid, and False the name is not valid.
		"""

		if name == '':
			return False

		valid_name = self.validate_name_pattern( name )
		if valid_name:
			exists = self.check_name_existance( name )
			if not exists:
				return True
			else:
				return False
		else:
			return False

class Enumeration_Collection( Collection ):
	"""
	A Collection that comes from the Enum_Types.  This is the interface
	that lines up with the 'Collection' concept used elsewhere.  The
	difference is that we provide an enumeration string that we
	query from vlib.enumerations.  Enumerations of course sit on
	top of data_enum Data Providers.

	**Arguments:**

		:``doc``: 					`AnimationEditor.doc` The Animation Editor Doc
		:``enumeration_id``: 	`str` A string to the enumerations

	**Keyword Arguments:**

		:``Keyword Argument``: `Type` Description
	"""
	def __init__( self, doc, enumeration_id ):
		self.enumeration_id = enumeration_id
		self._virtual_item_dict = { }

		super( Enumeration_Collection, self ).__init__( doc )


	def _create_item( self, name, virtual = False ):
		new_item = super( Enumeration_Collection, self )._create_item( name, virtual = virtual )


	def get_virtual_items( self ):
		"""
		In the AE virtual items are those that have never been saved yet but
		are still being worked with. The purpose of this is for glueing the
		Resource Data Providers to the 'virtual resources'.

		:rtype : dict[str:Any]
		"""
		return self._virtual_item_dict.values( )


	# def _gather_virtual_infos( self ):
	# 	"""
	# 	OVERRIDE THIS per Custom Collection that
	# 	supports virtual things.
	# 	:rtype: set
	# 	"""
	# 	print( 'please override this for <{0}>'.format( self.__class__ ) )
	# 	return set( )


	def get_items( self, use_cache = True ):

		if not use_cache:
			self.update_collection( )

		# real_items = self._item_dict.values( )
		# virtual_items = self._virtual_item_dict.values( )
		# all_items = real_items + virtual_items # dict( real_items.items( ) + virtual_items.items( ) )

		# testing: since all self._virtual_item_dict will exist in self._item_dict we only
		# need to return the one list
		return self._item_dict.values( )


	def update_collection( self, clear_items = False ):
		"""
		Updates the collection, and handles sorting out the difference between
		new items ( virtual ) and existing items that are real.

		**Arguments:**

			None

		**Keyword Arguments:**

			:``clear_items``: `bool` clears the dictionaries first

		**Returns:**

			:``real+virtual``: `dict` The new things
		:type clear_items: bool
		:rtype : dict[str:Any]
		"""

		if clear_items:
			self._item_dict.clear( )
			self._virtual_item_dict.clear( )

		all_item_infos = self._gather_item_infos( )

		if not all_item_infos and not self._item_dict:
			return { }

		# run through the items, and split them into
		# virtual and real.  Virtual as in only in
		# memory.
		virtual_item_dict = { }
		real_item_dict = { }
		all_items = set( )
		# TODO : Completely wasteful _create_item.  We already created them so why not use the existing stuff?
		for item in all_item_infos:
			all_items.add( item.datum_label )
			# the Virtual Provider attaches this tag onto all items
			v_tag = vlib.data_enum.Enumerated_Data_Provider_Virtual.VIRTUAL_TAG
			if hasattr( item, v_tag ) and getattr( item, v_tag ):
				created_item = self._create_item( item.datum_label, virtual = True )
				virtual_item_dict[ item.datum_label ] = created_item
			else:
				created_item = self._create_item( item.datum_label )
				real_item_dict[ item.datum_label ] = created_item

		# if items are removed we need to punt them from the list.  .update will not
		# remove things.
		all_item_keys = set( real_item_dict.keys( ) ).union( set( virtual_item_dict.keys( ) ) )
		removed_items = set( self._item_dict.keys( ) ).difference( all_item_keys )

		# clean up the deleted items from the list
		for key in removed_items:
			if key in self._item_dict:
				del( self._item_dict[ key ] )
			if key in self._virtual_item_dict:
				del( self._virtual_item_dict[ key ] )

		# now apply updates
		self._item_dict.update( real_item_dict )
		self._item_dict.update( virtual_item_dict )
		self._virtual_item_dict.update( virtual_item_dict )

		self.is_dirty = True

		return  self._item_dict


	def _gather_item_infos( self ):
		"""
		Gather up the Enum_Types raw data.  These will be
		objects, not just strings.  Typical Enumerated_Datums

		**Arguments:**

			None

		**Keyword Arguments:**

			None

		**Returns:**

			:``datums``: `list[vlib.data_enum.Enumerated_Datum]` A list of the raw datums

		:rtype: list[vlib.data_enum.Enumerated_Datum]
		"""
		item_infos = [ ]
		if vlib.enumerations.has_enum_type( self.enumeration_id ):
			enum = vlib.enumerations.get_enum_type( self.enumeration_id )
			item_infos.extend( enum.get_refl_enum_values( ) )

		return item_infos


	def _gather_item_names( self ):
		"""
		Gather up the Enum_Types display names.

		**Arguments:**

			None

		**Keyword Arguments:**

			None

		**Returns:**

			:``datums``: `list[str]` A list of the display names

		:rtype: list[str]
		"""
		item_names = [ ]
		infos = self._gather_item_infos( )
		if infos:
			item_names = [ info.datum_label for info in infos ]

		return item_names



class Provider_Collection( Collection ):
	"""
	WIP Designed to connect to the data_enum Providers directly
	UPDATE: Only used for clips right now.  Still keeping the
	class in case we move away from the Enum_Types
	"""
	def __init__( self, doc, provider_id, data_set_id ):
		self.provider_id = provider_id
		self.data_set_it = data_set_id

		self._virtual_item_dict = { }

		super( Provider_Collection, self ).__init__( doc )


	def _create_item( self, name, virtual = False ):
		new_item = super( Provider_Collection, self )._create_item( name )


	def _gather_item_names( self ):

		items = vlib.data_enum.get_enumerated_data( self.provider_id, self.data_set_it )
		item_names = [ item.datum_label for item in items ]
		return item_names


	def get_virtual_items( self ):
		return self._virtual_item_dict.values( )


	def get_items( self, use_cache = True ):

		if not use_cache:
			self.update_collection( )

		real_items = self._item_dict.values( )
		virtual_items = self._virtual_item_dict.values( )
		all_items = real_items + virtual_items # dict( real_items.items( ) + virtual_items.items( ) )

		return all_items


#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
## Clip Data ##
#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

# Individual Clip data object
class Clip_Item( object ):
	"""
	Class for the Individual Clip data object.
	Clip is an animation clip

	*Arguments:*
		* ``doc``  -Active animation document
		* ``name`` -name of the clip data object

	*Keyword Arguments:*
		None
	"""

	def __init__( self, doc, name ):
		self.doc 		= doc
		self.name 		= name
		self.p4_api 	= P4.P4( )
		self.selected_triggers 		= [ ]
		self.active_trigger_view 	= ctg.ae2.ui.const.ANIMATION_TRIGGER


	def get_name( self ):
		"""
		This method returns the clip data name.
		"""
		return self.name


	def get_node_type( self ):
		"""
		This method returns the node type constant.
		"""
		return ctg.ae2.ui.const.NODE_TYPE_ANIM_CLIP


	def get_file_name_and_ext( self ):
		"""
		This method adds the '.animx' extension to the clip item name.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``filename`` -return clip name with '.animx' extension.
		"""

		file_extension = '.anim.fbx'
		file_name = '{0}{1}'.format( self.get_name( ), file_extension )

		return file_name


	def get_file_info( self ):
		"""
		This method gets and returns resource file information for the animation
		clip if the information exists, otherwise returns None.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``file information`` -Resource file information if it exists, otherwise None.
		"""

		try:
			resource = _resourcelib.get_file_info( self.get_file_name_and_ext( ) )
		except RuntimeError:
			resource = None

		return resource


	def get_workspace_package( self ):
		"""
		Returns the current workspace package the clip item lives in.

		**Arguments:**

			:``None``:

		**Keyword Arguments:**

			:``None``:

		**Returns:**

			:``data\\<workspace_package>``:	`str` The shortened workspace package value.

		**Examples:** ::

			>>> doc = AnimationEditor.get_active_document( )
         >>> clip = doc.selection_manager.get_selected_objects( )
			>>> if isinstance( clip, ctg.ae2.core.data.Clip_Item ):
			>>>	 clip.get_workspace_package( )
         'data\\aom_agents'
		"""

		#Get the workspace directory, and the normpath of that
		workspace_dir = vlib.user.settings[ 'project_workspace_dir' ]
		current_workspace = os.path.basename( os.path.normpath ( workspace_dir ) )
		resource_workspace = workspace_dir + 'data\\'
		workspace_packages = vlib.package.get_package_info_dict( workspace_path = workspace_dir )

		#Lowercase the path
		resource_workspace = resource_workspace.lower( )

		#Get the file info on the item
		try:
			resource = _resourcelib.get_file_info( self.get_file_name_and_ext( ) )
		except RuntimeError:
			resource = None

		#If the package it is checking against is in the workspace packages that exist, and is in the full filename of the item, return that matching package
		if resource:
			for package in workspace_packages.keys( ):
				if package in resource.full_local_filename:
					resource_package = package
					return workspace_packages, resource_package

		return None


	#@vlib.debug.Debug_Timing( 'is_clip_resource_synced', precision = 4 )
	def is_resource_synced( self ):
		"""
		This method checks if the animation clip resource is synced, returns True
		if not synced returns False, returns None if there is no resource file
		information found.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``bool or None`` -Returns True if file is synced, False if not
			* ``none`` -If no resource file information found.
		"""

		resource = self.get_file_info( )

		if resource:

			self.p4_api.connect( )

			resource_synced = self.p4_api.run_fstat( resource.full_local_filename )

			self.p4_api.disconnect( )

			if resource_synced[ 0 ][ 'haveRev' ] == resource_synced[ 0 ][ 'headRev' ]:
				return True
			else:
				return False

		return None


	#@vlib.debug.Debug_Timing( 'sync_file', precision = 4 )
	def sync_file( self ):
		"""
		This method checks if the resource file information, and if the file is
		synced,if not synced try syncing and return a bool True or False if
		the operation was successful.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``bool`` -Indicating whether syncing was successful
		"""

		resource = self.get_file_info( )
		synced 	= self.is_resource_synced( )

		if synced == False:
			if resource:
				#_resourcelib.sync_file( self.get_file_name_and_ext( ) )
				vlib.perforce.sync( [self.get_file_name_and_ext( )] )
				synced 	= self.is_resource_synced( )


		return synced


	def get_properties( self ):
		"""
		This method gets and returns clip properties object.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``Value`` -Clip Properties object
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return None

		props = doc.get_clip_properties( self.get_name( ) )

		return props


	def get_clip_length( self ):
		doc   = AnimationEditor.get_active_document()
		props = doc.get_clip_properties( self.get_name( ) )

		#round to the nearest interger
		frames = int( round( props.get_clip_length() * 30, 0 ))

		return frames


	def get_anim_triggers( self ):
		"""
		This method gets and returns a list of animation trigger objects.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``list`` -List of animation trigger objects.
		"""

		props = self.get_properties( )

		return list( props.get_anim_triggers( ) )


	def get_trigger_types( self, triggers ):
		"""
		Returns all trigger types associated with a given clip as a list.

		**Arguments:**

			:``triggers``:	`list` A list of all triggers on the current clip

		**Keyword Arguments:**

			:``None``

		**Returns:**

			:``trigger_types``:	`list` A list of the trigger types

		**Examples:** ::

			>>> doc = AnimationEditor.get_active_document( )
			>>> selection = doc.selection_manager.get_selected_objects( )
			>>> selection[0].get_trigger_types( selection[0].get_anim_triggers( ) )
			[ 'VFX', 'Audio', 'Design', 'Programming' ]
		"""

		trigger_types = [ trig.get_type( ) for trig in triggers if trig.get_type( ) ]
		return trigger_types


	def get_trigger_approvals( self, triggers ):
		"""
		Returns all trigger approvals associated with a given clip as a list.

		**Arguments:**

			:``triggers``:	`list` A list of all triggers on the current clip

		**Keyword Arguments:**

			:``None``

		**Returns:**

			:``trigger_approvals``:	`list` A list of the trigger approvals

		**Examples:** ::

			>>> doc = AnimationEditor.get_active_document( )
			>>> selection = doc.selection_manager.get_selected_objects( )
			>>> selection[0].get_trigger_approvals( selection[0].get_anim_triggers( ) )
			[ 'Technical Artist' ]
		"""

		trigger_approvals = [ ]
		for trig in triggers:
			if trig.get_approver( ):
				for approval in trig.get_approver( ):
					trigger_approvals.append( approval )

		return trigger_approvals


	def get_audio_trigger_data( self, trigger ):
		compared_sounds = [ ]

		soundbanks = self.get_soundbanks( )
		if trigger:
			if trigger.get_payload_name( ) == 'gml_sound_trigger_payload':
				payload_xml = trigger.get_payload_xml( )
				if payload_xml:
					strings = payload_xml.split( '\n\t' )
					for node in strings:
						if 'm_wwise_event' in node:
							for key, value in soundbanks.iteritems():
								if key in node:
									compared_sounds.append( value )

		return compared_sounds


	def set_flag( self, flag, val ):
		"""
		This method set flags on a clip property object and updates the document.
		It returns a bool indicating whether the modification was successful
		or not.

		*Arguments:*
			* ``flag`` -name of the flag, a string
			* ``val``  -value of the flag, a bool.

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``bool`` -Returns a bool indicating whether the modification	was successful.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		props = self.get_properties( )
		props.set_flag( flag, val )

		return doc.undoable_modify_clip_properties( props )


	def get_active_flags( self ):
		"""
		This method gets and returns the active flags for a clip property
		object.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``List`` -List of active clip property flags
		"""

		props = self.get_properties( )

		return list( props.get_active_flags( ) )


	def get_flag( self, flag ):
		"""
		This method checks if a flag is in a list of active flags for a clip
		property.

		*Arguments:*
			* ``flag`` -name of flags to be checked.

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``bool`` -bool indicating is in a list of active flags or not.
		"""

		return flag in self.get_active_flags( )


	def get_length( self ):
		"""
		This method returns the length of an animation clip

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``length`` -length of an animation clip

		*Todo:*
			* This needs to be changed so that when a clip item is selected, it
			* preloads so that we get the actual clip length, the 1.0 returns here
			* is just a temp value.
		"""

		return self.get_clip_length( )


	def is_used( self ):
		"""
		This method checks if the animation clip is used in tag association.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``bool`` -bool indicating if clip is used or not.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return False

		if doc.tag_association_collection:
			tag_items = doc.tag_association_collection.get_item_by_clip_name( self.get_name( ) )
			if tag_items:
				if len( tag_items ) > 0:
					return True

		return False


	def set_animation_triggers( self, triggers = [] ):
		"""
		This method set and updates animation trigger objects on a clip property
		object.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``triggers`` -List of trigger objects.

		*Returns:*
			* ``bool`` -bool indicating whether the modification was successful or not.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		props = self.get_properties()

		for trigger in triggers:
			props.set_anim_trigger( trigger )

		return doc.undoable_modify_clip_properties( props )


	def add_animation_triggers( self, num_of_triggers = 1, name="New Trigger", category=None, start_frame = 0, end_frame = 1 ):
		"""
		This method adds animation trigger objects to add to a clip property object
		and returns a tuple containing a bool and a list a list of new trigger uids.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``number_of_triggers`` -Numbers of triggers to add.

		*Returns:*
			* ``tuple`` -Tuple containing a bool and a list of new trigger uids
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		props = self.get_properties()
		new_uid_list = [ ]

		for i in xrange( num_of_triggers ):
			new_uid = doc.get_new_uid()
			new_uid_list.append( new_uid )
			props.create_anim_trigger_from_uid( new_uid )

			new_trigger = props.get_anim_trigger( new_uid )
			new_trigger.set_frame( int( start_frame ) )
			new_trigger.set_end_frame( int( end_frame ) )

			if name:
				new_trigger.set_name( name )

			if category:
				new_trigger.set_category( category )

			props.set_anim_trigger( new_trigger )

		return ( doc.undoable_modify_clip_properties( props ), new_uid_list )


	def delete_triggers( self, triggers = [ ], mark_dirty = True):
		"""
		The method deletes triggers from a clip property object.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``triggers`` -List of triggers to be deleted.

		*Returns:*
			* ``bool`` -Indication whether the operation was successful or not.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return False

		props = self.get_properties()

		for trigger in triggers:
			props.delete_trigger( trigger.get_uid() )

		if mark_dirty:
			return doc.undoable_modify_clip_properties( props )

		return True



	def delete_triggers_by_uids( self, triggers_uids = [ ], mark_dirty = True ):
		"""
		The method deletes triggers from a clip property object.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``triggers`` -List of triggers to be deleted.

		*Returns:*
			* ``bool`` -Indication whether the operation was successful or not.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return False

		props = self.get_properties()

		for tiggers_uid in triggers_uids:
			props.delete_trigger( tiggers_uid )

		if mark_dirty:
			return doc.undoable_modify_clip_properties( props )

		return True


	def clear_all_triggers( self ):
		"""
		This method deletes all triggers from a clip property object.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``bool`` -Indicating the operation was successful or not.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return False

		props = self.get_properties()
		props.delete_triggers()

		return doc.undoable_modify_clip_properties( props )


	def clear_all_properties( self ):
		"""
		This method clears all animation clip properties.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``bool`` -bool indication whether the operation was successful.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return False

		props = self.get_properties()
		props.delete_triggers()

		for flag in self.get_active_flags():
			props.set_flag( flag, False )

		return doc.undoable_modify_clip_properties( props )


	#@vlib.debug.Debug_Timing( 'paste_properties', precision = 4 )
	def paste_properties( self, data_dict ):
		"""
		This method clears all clip properties and pastes new properties.

		*Arguments:*
			* ``data_dict`` -Dictionary containing clip properties data.

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``bool`` -bool indicating the operation was sucessful or not.
		"""

		success = False
		cleared = self.clear_all_properties()

		if cleared:
			for key, data in data_dict.iteritems():
				if key == ctg.ae2.ui.const.ANIMATION_TRIGGER:

					anim_success, anim_uids = self.add_animation_triggers( len( data ) )
					if anim_success:
						triggers = self.get_anim_triggers_from_uids( anim_uids )
						success 	= self.set_anim_trigger_data( triggers, data )

				elif key == ctg.ae2.ui.const.FLAGS:

					for flag in data:
						success = self.set_flag( flag, True )


		return success


	def set_triggers_frame( self, triggers, frame ):
		"""
		This method data on ik triggers.

		*Arguments:*
			* ``triggers``  -List of Triggers
			* ``data_list`` -List of data to be set on triggers

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``bool`` -bool indicating whether the operation was successful or not.
		"""

		success = False
		for trigger in triggers:
			trigger.set_frame( int( frame ) )

		if self.active_trigger_view == ctg.ae2.ui.const.ANIMATION_TRIGGER:
			success = self.set_animation_triggers( triggers )

		return success


	def set_anim_trigger_data( self, triggers, data_list, category = None, set_properties = False ):
		"""
		This method data on animation triggers.

		*Arguments:*
			* ``triggers``  -List of Triggers
			* ``data_list`` -List of data to be set on triggers

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``bool`` -bool indicating whether the operation was successful or not.
		"""

		index = 0
		for trigger in triggers:
			if set_properties:
				data = data_list[ 0 ]
			else:
				data = data_list[ index ]
			trigger.set_name( str( data[0] ) )
			trigger.set_frame( int( data[1] ) )
			trigger.set_end_frame( int( data[2] ) )
			trigger.set_payload_name( str( data[3] ) )
			trigger.set_payload_xml( str( data[4] ) )
			category_name = data[5]
			if category:
				category_name = category

			trigger.set_category( str( category_name ) )

			index += 1

		return self.set_animation_triggers( triggers )



	def set_trigger_value( self, prop_id_string, value, trigger, trigger_type = ctg.ae2.ui.const.ANIMATION_TRIGGER):
		"""
		This method sets up initial value for the control.

		*Arguments:*
			* ``prop_id_string`` -property id string
			* ``value`` 			-value to be set on trigger for the prop_id_string.
			* ``trigger`` 			-trigger on which to set the value for the prop_id_string.
			* ``trigger_type`` 	-the type of trigger.

		*Keyword Arguments:*
			* <none>

		*Returns:*
			* ``boolean`` 			-a boolean indicating whether the operation was successiful or not.
		"""
		success = False

		if trigger:
			#make sure the prop_id_string is in lower case
			prop_id_string = prop_id_string.lower()
			if prop_id_string == 'start_frame':
				trigger.set_frame( int( value ) )
			elif prop_id_string  == 'end_frame':
				trigger.set_end_frame( int( value ) )
			elif prop_id_string == 'name':
				trigger.set_name( value )
			elif prop_id_string == 'payload_name':
				trigger.set_payload_name( value )
				trigger.set_payload_xml("")
			elif prop_id_string == 'payload_xml':
				trigger.set_payload_xml( value )
			elif prop_id_string == 'category':
				trigger.set_category( value )

			#after setting the value on the trigger, we have to tell the clip property object to
			#update the triggers who's value we just changed.
			if trigger_type == ctg.ae2.ui.const.ANIMATION_TRIGGER:
				success = self.set_animation_triggers( [ trigger ] )

		return success


	def set_triggers_category( self, triggers, category_name ):

		for trigger in triggers:
			trigger.set_category( category_name )

		success = self.set_animation_triggers( triggers )

		return success


	def get_anim_trigger_from_uid( self, uid ):
		"""
		This method gets animation trigger from the clip property object by uid.

		*Arguments:*
			* ``uid`` -Trigger uid

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``trigger object`` -Trigger object with the same uid provided.
		"""

		props = self.get_properties()

		return props.get_anim_trigger( uid )


	def get_anim_triggers_from_uids( self, uids ):
		"""
		This method gets animation triggers from the clip property object by uids.

		*Arguments:*
			* ``uids`` -list of uids

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``list`` -Trigger objects with the same uids provided.
		"""

		triggers = [ ]
		props = self.get_properties()

		for uid in uids:
			triggers.append( props.get_anim_trigger( uid ) )

		return triggers

	def get_selected_triggers( self ):
		return self.get_anim_triggers_from_uids( self.selected_triggers )


	def get_clip_prop_data( self ):
		"""
		This method gets all clip property objects data and returns it as a
		dictionary.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``dictionary`` -Diactionary containing clip property data.
		"""

		clip_data_dict = { }

		clip_data_dict[ ctg.ae2.ui.const.FLAGS ] 					= self.get_active_flags( )
		clip_data_dict[ ctg.ae2.ui.const.ANIMATION_TRIGGER ] 	= self.get_anim_triggers_data( self.get_anim_triggers( ) )

		return clip_data_dict


	def get_anim_triggers_data( self, triggers ):
		"""
		This method gets animation triggers data and returns it a list.

		*Arguments:*
			* ``triggers`` -List of triggers objects

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``list`` -List containing a lists of triggers data
		"""

		anim_triggers_data = [ ]

		for trigger in triggers:
			anim_triggers_data.append([ trigger.get_name( ), trigger.get_frame( ), trigger.get_end_frame( ), trigger.get_payload_name( ), trigger.get_payload_xml( ), trigger.get_category( ) ])

		return anim_triggers_data


	def get_soundbanks( self ):
		events = vlib.data_enum.get_enumerated_data( 'wwiseEvents', '' )
		soundbanks = { }
		for e in events:
			# Split the event label by the '>' character, as the name comes after that
			event_name = e.datum_label.split( '>' )[ 1 ].strip( )
			# Store the event id
			soundbanks[ str( e.datum_id ) ] = str( event_name )

		return soundbanks


	def get_trigger_payloads( self, triggers ):
		doc = AnimationEditor.get_active_document( )
		audio_events = []

		if not triggers:
			return ''
		else:
			payloads = []
			for trigger in triggers:
				if not trigger.get_payload_name( ):
					payloads.append( 'No Name' )
				else:
					payloads.append( trigger.get_payload_name() )

			return payloads


	def get_payload_type( self, trigger ):
		PAYLOAD_TYPE_SOUND = 'gml_sound_trigger_payload'
		PAYLOAD_TYPE_PROP = 'gml_prop_trigger_payload'
		PAYLOAD_TYPE_NO_INTER_ANIM = 'anim_no_interpolate_trigger_payload'

		payload_xml = trigger.get_payload_xml( )
		if payload_xml:
			strings = payload_xml.split( '\n\t' )
			for node in strings:
				if 'm_wwise_event' in node:
					for key, value in self.get_soundbanks().iteritems():
						if key in node:
							return PAYLOAD_TYPE_SOUND
				elif 'm_wwise_event' not in node and 'prop' in node:
					return PAYLOAD_TYPE_PROP
				else:
					payload_name = trigger.get_payload_name()
					if 'sound_trigger' in payload_name:
						return PAYLOAD_TYPE_SOUND
					elif 'prop_trigger' in payload_name:
						return PAYLOAD_TYPE_PROP
					elif 'anim_no_interpolate' in payload_name:
						return PAYLOAD_TYPE_NO_INTER_ANIM
					else:
						pass
		else:
			payload_name = trigger.get_payload_name()
			if 'sound_trigger' in payload_name:
				return PAYLOAD_TYPE_SOUND
			elif 'prop_trigger' in payload_name:
				return PAYLOAD_TYPE_PROP
			elif 'anim_no_interpolate' in payload_name:
				return PAYLOAD_TYPE_NO_INTER_ANIM

		return None


	def get_trigger_payload_classes( self ):
		return ctg.ae2.core.ae_common_operations.get_payload_classes( )


	def get_trigger_payload_event_value( self, item ):
		if isinstance( item, AnimationEditor.ae_animation_trigger ):
			data_obj = item
		else:
			data_obj = item.get_container( )

		payload_xml = data_obj.get_payload_xml( )
		if payload_xml:
			wwise_events = []

			strings = payload_xml.split( '\n\t' )
			for node in strings:
				if 'm_wwise_event' in node:
					for key, value in self.get_soundbanks().iteritems():
						if key in node:
							wwise_events.append( value )

			return wwise_events


	def get_anim_triggers_data_from_uids( self, trigger_uids ):
		"""
		This method gets animation triggers data from uids and returns it a list.

		*Arguments:*
			* ``trigger_uids`` -List of trigger uids

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``list`` -List containing a lists of triggers data
		"""

		anim_triggers_data = [ ]

		for uid in trigger_uids:
			trigger = self.get_anim_trigger_from_uid( uid )
			if trigger:
				anim_triggers_data.append([ trigger.get_name( ), trigger.get_frame( ), trigger.get_end_frame( ), trigger.get_payload_name( ), trigger.get_payload_xml( ), trigger.get_category( ) ])

		return anim_triggers_data


	def get_anim_triggers_data_dict( self, triggers ):
		"""
		This method gets animation triggers data and returns it a list.

		*Arguments:*
			* ``triggers`` -List of triggers objects

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``list`` -List containing a lists of triggers data
		"""

		anim_triggers_data_dict = { }
		trigger_start_frames    = [ ]
		trigger_names 	         = [ ]
		trigger_end_frames      = [ ]
		trigger_payload_names   = [ ]
		trigger_payload_xmls    = [ ]
		trigger_category_names  = [ ]
		trigger_approvals = [ ]

		for trigger in triggers:
			trigger_name 	      = trigger.get_name( )
			trigger_start_frame 	= trigger.get_frame( )
			trigger_end_frame 	= trigger.get_end_frame( )
			trigger_payload_name	= trigger.get_payload_name( )
			trigger_payload_xml	= trigger.get_payload_xml( )
			trigger_category_name = trigger.get_category( )

			if trigger_start_frame not in trigger_start_frames:
				trigger_start_frames.append( trigger_start_frame )

			if trigger_end_frame not in trigger_end_frames:
				trigger_end_frames.append( trigger_end_frame )

			if trigger_payload_name not in trigger_payload_names:
				trigger_payload_names.append( trigger_payload_name )

			if trigger_payload_xml not in trigger_payload_xmls:
				trigger_payload_xmls.append( trigger_payload_xml )

			if trigger_name not in trigger_names:
				trigger_names.append( trigger_name )

			if trigger_category_name not in trigger_category_names:
				trigger_category_names.append( trigger_category_name )

			else:
				trigger_approvals.append( '' )

		anim_triggers_data_dict[ "name" ] 	         = trigger_names
		anim_triggers_data_dict[ "start_frame" ] 	   = trigger_start_frames
		anim_triggers_data_dict[ "end_frame" ] 	   = trigger_end_frames
		anim_triggers_data_dict[ "payload_name" ]    = trigger_payload_names
		anim_triggers_data_dict[ "payload_xml" ]     = trigger_payload_xmls
		anim_triggers_data_dict[ "category" ]        = trigger_category_names
		anim_triggers_data_dict[ "approvals" ] 	= trigger_approvals

		return anim_triggers_data_dict


	def get_trigger_value( self, prop_id_string, trigger ):
		"""
		This method gets and returns a value from specified data object.

		*Arguments:*
		   * ``prop_id_string`` -property string name.
			* ``trigger`` -trigger to get data from.

		*Keyword Arguments:*
			* <none>

		*Returns:*
			* ``value`` -trigger value based on the prop_id_string value.
		"""
		value = None
		if not trigger:
			return value

		if prop_id_string == 'start_frame':
			value = trigger.get_frame( )
		elif prop_id_string == 'end_frame':
			value = trigger.get_end_frame( )
		elif prop_id_string == 'name':
			value = trigger.get_name( )
		elif prop_id_string == 'payload_name':
			value = trigger.get_payload_name( )
		elif prop_id_string == 'payload_xml':
			value = trigger.get_payload_xml( )
		elif prop_id_string == 'category':
			value = trigger.get_category( )


		return value


	def get_anim_triggers_count( self ):
		"""
		This method gets the numbers of animation triggers for the clip property.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``int`` -Number of animation triggers on the clip property object.
		"""

		return len( self.get_anim_triggers() )
		
		
	def generateFootstepTriggers( self ):
	
		props = self.get_properties( )
		props.generate_anim_footstep_triggers( )


# Clip data collection
class Clip_Collection( Provider_Collection ):
#class Clip_Collection( Collection ):
	"""
	Clip collections object

	*Arguments:*
		* ``doc`` -Active animation document.
		* ``provider_id`` string of the data provider id
		* ``data_set_id`` string of the data set id in the provider

	*Keyword Arguments:*
		* ``none``
	"""

	def _gather_item_names( self ):
		"""
		Gathers and returns a set of clip names from the active animation document.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``set`` -Containing animation clip names.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		# NAT Trying to get data from the enumeration
		resource_clips = vlib.data_enum.get_enumerated_data( self.provider_id, self.data_set_it )
		names = [ vlib.os.split_ext( resource_clip.datum_id )[ 0 ] for resource_clip in resource_clips ]

		return set( doc.get_clip_names( ) )


	def _create_item( self, name ):
		"""
		This method creates Clip_Item with a specified name.

		*Arguments:*
			* ``name`` -name for the clip item.

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``Clip_Item`` -Newly created Clip_Item.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		return Clip_Item( doc, name )


	def get_node_type( self ):
		"""
		This method gets and returns Clip_Item node type constant.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``node type constant`` -Node type constant.
		"""

		return ctg.ae2.ui.const.NODE_TYPE_ANIM_CLIP


	def get_all_triggers( self ):
		"""
		Returns all triggers currently stored on the doc.

		**Arguments:**

			:``None``

		**Keyword Arguments:**

			:``None``

		**Returns:**

			:``triggers``:	`list` A list of all animation triggers from every clip the doc knows about.

		**Examples:** ::

			>>> doc = AnimationEditor.get_active_document( )
			>>> doc.clip_collection.get_all_triggers( )
		"""

		doc =AnimationEditor.get_active_document( )
		if not doc:
			return

		triggers = [ ]

		# Troll through all of the clips and store the triggers in a master list to be returned
		for clip in doc.clip_collection.get_items( ):
			for trigger in clip.get_anim_triggers( ):
				if trigger not in triggers:
					triggers.append( trigger )

		return triggers

	def get_trigger_by_name( self, trigger_name ):
		"""
		Returns a single trigger based on the name passed in.

		**Arguments:**

			:``trigger_name`` : ``str`` The name of the trigger you are looking for.

		**Keyword Arguments:**

			:``None``

		**Returns:**

			:``anim_trigger``:	`AnimationEditor.ae_animation_trigger` The trigger item matching the name you are looking for

		**Examples:** ::

			>>> doc = AnimationEditor.get_active_document( )
			>>> doc.clip_collection.get_all_triggers( )
		"""

		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		if trigger_name:
			for clip in doc.clip_collection.get_items( ):
				for anim_trigger in clip.get_anim_triggers( ):
					if anim_trigger.get_name( ) == trigger_name:
						return anim_trigger

		return None


#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
## Set Data ##
#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# Individual Set data object
class Set_Item( object ):
	"""
	Class for the Individual Set data object

	*Arguments:*
		* ``doc``  -Active animation document
		* ``name`` -name of the animation set object

	*Keyword Arguments:*
		* ``none``
	"""

	def __init__( self, doc, name ):
		self.doc = doc
		self.name = name
		self.group_collection = Group_Collection( doc, name )


	def get_name( self ):
		"""
		This method gets and returns Set_Item Name

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``name`` -Name of the Set_Item
		"""

		return self.name


	def get_node_type( self ):
		"""
		This method gets and returns Set_Item node type constant.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``node type constant`` -Node type constant.
		"""

		return ctg.ae2.ui.const.NODE_TYPE_ANIM_SET_TREE


	def get_parent( self ):
		"""
		This method gets and return Animation Set parent.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``parent`` -Animation Set parent Item
		"""

		parent = None
		doc = AnimationEditor.get_active_document()
		if not doc:
			return parent

		parent_name = doc.get_anim_set_parent_name( self.get_name( ) )

		if parent_name:
			parent = doc.set_collection.get_item_by_name( parent_name )

		return parent


	def has_children( self ):
		"""
		This method checks if animation set has children.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``bool`` -Indicating whether animation set has children or not.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return False

		return bool( doc.get_anim_set_children_names( self.get_name( ) ) )


	def get_children( self ):
		"""
		This method gets and returns a list Animation Set children.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``children`` -List of animation Set children.
		"""
		children = [ ]
		doc = AnimationEditor.get_active_document()
		if not doc:
			return children

		child_names = set( doc.get_anim_set_children_names( self.get_name( ) ) )

		child_names.intersection_update( doc.set_collection.get_item_names( ) )

		for name in child_names:
			children.append( doc.set_collection.get_item_by_name( name ) )

		return children


	def get_prop_num( self ):
		doc = AnimationEditor.get_active_document()
		if not doc:
			return 0

		return doc.get_num_anim_set_props( self.get_name( ) )


	def get_groups( self, use_cached = True ):
		"""
		This method get and returns a list of group items.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``used_cached`` -Use cached results or get latest from document.

		*Returns:*
			* ``groups`` -list of groups items
		"""

		groups = self.group_collection.get_items( use_cached = use_cached )

		return groups


	def get_group_names( self, use_cached = True ):
		"""
		This method gets and returns a list of group items names.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``group_names`` -List of groups names
		"""

		group_names = [ ]
		for group in self.get_groups( use_cached = use_cached ):
			group_names.append( group.get_name( ) )

		return group_names


	def get_group_by_name( self, name, use_cached = True ):
		"""
		This method gets and returns a group item by name.

		*Arguments:*
			* ``name`` 			-group name

		*Keyword Arguments:*
			* ``use_cached`` 	-Use cached results or get latest from document.

		*Returns:*
			* ``group item``  -Group_Item associated with the group name.
		"""

		return self.group_collection.get_item_by_name( name, use_cached = use_cached )


	def get_group_default( self ):
		"""
		This method gets and returns group default item.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``Group_Item`` -Default Group_Item
		"""

		return self.get_group_by_name( 'Default' )


	def add_group( self, group_name ):
		"""
		This method adds a animation group to animation set.

		*Arguments:*
			* ``group_name`` -animation group name to be added to animation set.

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``bool`` -indicating whether the operation was successful or not.
		"""

		did_add = False
		doc = AnimationEditor.get_active_document()
		if not doc:
			return did_add

		if group_name:
			did_add = doc.undoable_add_anim_group_to_anim_set( group_name, self.name, "" )
			if did_add:
				self.get_groups( use_cached = False )
				item = doc.anim_group_collection.get_item_by_name( group_name )
				doc.event_manager.post_group_created_event( [ item ], group_name, self.name )

		print 'Added: {0} Group: {1} to Anim Set: {2} '.format( did_add, group_name, self.name )
		return did_add


	def remove_group( self, group_name ):
		"""
		This method removes animation group from animation set.

		*Arguments:*
			* ``group_name`` -animation group name to be removed from animation set.

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``bool`` -indicating whether the operation was successful or not.
		"""
		doc = AnimationEditor.get_active_document()
		did_remove = False
		if not doc:
			return did_remove

		if group_name:
			did_remove = doc.undoable_remove_anim_group_from_anim_set( group_name, self.name )
			if did_remove:
				self.get_groups( use_cached = False )
				doc.event_manager.post_group_deleted_event( [ self ], group_name = group_name, set_name = self.name )

		print 'Removed: {0} Group: {1} from Anim Set: {2} '.format( did_remove, group_name, self.name )
		return did_remove


	def create( self, new_name = u'New_Anim_Set', parent_name = "" ):
		"""
		This creates a new animation set.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``new_name`` 	-Animation set name
			* ``parent_name`` -Animation set parent name

		*Returns:*
			* ``bool`` -indicating whether the operation was successful or not.
		"""

		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		valid = self.validate_name( new_name )

		did_create = False
		if valid:
			did_create = doc.undoable_create_anim_set( new_name, parent_name )
			if did_create:
				doc.set_collection.update_collection( clear_items = True)
				self.get_groups( use_cached = False )
				item = doc.set_collection.get_item_by_name( new_name )
				doc.event_manager.post_set_created_event( [ item ] )

		print 'Create Anim Set: {0}  Name:{1} Parent:{2}'.format( did_create, new_name, parent_name )
		doc.animation_sets_pane.refresh_ui( )
		return did_create


	def rename( self, new_name ):
		"""
		This method renames a Animation set.

		*Arguments:*
			* ``new_name`` -new animation set name.

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``bool`` -indicating whether the operation was successful or not.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		old_name = self.get_name( )
		valid = self.validate_name( new_name )

		if valid:
			did_rename = doc.undoable_rename_anim_set( self.get_name( ), new_name )
			if did_rename:
				doc.set_collection.update_collection( )
				set_item = doc.set_collection.get_item_by_name( new_name )
				doc.event_manager.post_set_renamed_event( [ set_item ], old_name = old_name )

		print 'Rename Anim Set: {0}  From:{1} To:{2}'.format( did_rename, old_name, new_name )
		if getattr( doc, 'animation_sets_pane', None ):
			doc.animation_sets_pane.refresh_ui( )
		return did_rename


	def delete( self ):
		"""
		This method deletes animation set.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``bool`` -indicating whether the operation was successful or not.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		#clear = False
		item_name = self.get_name( )
		did_delete = doc.undoable_delete_anim_set( self.get_name( ) )
		if did_delete:
			doc.set_collection.update_collection( clear_items=True)
			doc.event_manager.post_set_deleted_event( [ None ] )
			if getattr( doc, 'animation_sets_pane', None ):
				doc.animation_sets_pane.refresh_ui( )

		print 'Delete: {0} Anim Set: {1}'.format( did_delete, item_name )
		return did_delete


	def get_set_clip_path( self ):
		"""
		This method gets and returns animation set clip path.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``Path`` -Animation set clip path.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		return doc.get_anim_set_clip_path( self.get_name( ) )


	def get_set_preview_rig( self ):
		"""
		This method gets and returns animation set preview rig.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``rig`` -animation set preview rig.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		return doc.get_anim_set_preview_rig( self.get_name( ) )


	def get_set_preview_mesh( self ):
		"""
		This method gets and returns animation set preview mesh.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``mesh`` -animation set preview mesh.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		return doc.get_anim_set_preview_mesh( self.get_name( ) )


	def get_set_preview_prop(self, index):
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		return doc.get_anim_set_prop_mesh( self.get_name( ), index)

	def get_set_preview_prop_attach_tag(self, index):
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		return doc.get_anim_set_prop_tag( self.get_name( ), False, index )

	def get_set_preview_character_attach_tag(self, index):
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		return doc.get_anim_set_prop_tag( self.get_name( ), True, index )

	def get_parent_name( self ):
		"""
		This method gets and returns animation set parent name.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``parent name`` -Animation set parent name.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		return doc.get_anim_set_parent_name( self.get_name( ) )


	def set_clip_path( self, new_path ):
		"""
		This method sets animation set's clip path.

		*Arguments:*
			* ``new_path`` -clip path to be set to animation set.

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``bool`` -Bool indicating the operation was successful or not.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		return doc.undoable_set_anim_set_clip_path( self.get_name( ), new_path )


	def set_preview_rig( self, new_rig ):
		"""
		This method sets animation set's preview rig.

		*Arguments:*
			* ``new_rig`` -rig to be set to animation set.

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``bool`` -Bool indicating the operation was successful or not.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		return doc.undoable_set_anim_set_preview_rig( self.get_name( ), new_rig )


	def set_preview_mesh( self, new_mesh ):
		"""
		This method sets animation set's preview mesh.

		*Arguments:*
			* ``new_mesh`` -mesh to be set to animation set.

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``bool`` -Bool indicating the operation was successful or not.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		return doc.undoable_set_anim_set_preview_mesh( self.get_name( ), new_mesh )

	def set_prop_mesh(self, prop_mesh, index):
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		return doc.undoable_set_anim_set_prop_mesh(self.get_name( ), prop_mesh, index)

	def set_prop_attach_tag(self, tag, index):
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		return doc.undoable_set_anim_set_prop_tag(self.get_name( ), tag, False, index)

	def set_character_attach_tag(self, tag, index):
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		return doc.undoable_set_anim_set_prop_tag(self.get_name( ), tag, True, index)

	def reparent_set( self, new_parent ):
		"""
		This method sets animation set's preview parent.

		*Arguments:*
			* ``new_parent`` -parent name to be set to animation set.

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``bool`` -Bool indicating the operation was successful or not.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		return doc.undoable_reparent_anim_set( self.get_name( ), new_parent )


	def validate_name( self, name ):
		"""
		This Method checks the name for invalid characters, also checks if
		the name exists in sets collection.

		*Arguments:*
			* ``name`` -name to be validated

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``bool`` -True indicates the name is valid, and False the name is not valid.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		if name == '':
			return False

		valid_name = doc.set_collection.validate_name_pattern( name )
		if valid_name:
			exists = doc.set_collection.check_name_existance( name )
			if not exists:
				return True
			else:
				if self.get_name().lower() != name.lower():
					return False
				else:
					return True
		else:
			return False


	def get_unique_name( self, name ):
		"""
		Checks if the name exists in sets collection, if the name exists adds an
		index and return it as new name, if the name does not exists in the
		collection, return the name.

		*Arguments:*
			* ``name`` -The initial name

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``unique name`` -The current unique name
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		return doc.set_collection.get_unique_name( name )



# Set data collection
class Set_Collection( Collection ):
	"""
	Set collections object

	*Arguments:*
		* ``doc`` -Active animation document.

	*Keyword Arguments:*
		* ``none``
	"""

	def _gather_item_names( self ):
		"""
		Gathers and returns a set of animation set names from the active animation document.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``set`` -Containing animation set names.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		return set( doc.get_anim_set_names( ) )


	def _create_item( self, name ):
		"""
		This method creates Set_Item with a specified name.

		*Arguments:*
			* ``name`` -name for the set item.

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``Set_Item`` -Newly created Set_Item.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		return Set_Item( doc, name )


	def get_node_type( self ):
		"""
		This method gets and returns Set_Item node type constant.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``node type constant`` -Node type constant.
		"""

		return ctg.ae2.ui.const.NODE_TYPE_ANIM_SET_TREE


	def create( self, new_name = 'New_Anim_Set', parent_name = '' ):
		"""
		This creates a new animation set.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``new_name`` 	-Animation set name
			* ``parent_name`` -Animation set parent name

		*Returns:*
			* ``bool`` -indicating whether the operation was successful or not.
		"""

		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		valid = self.validate_name( new_name )

		success = False
		if valid:

			success = doc.undoable_create_anim_set( new_name, parent_name )
			if success:
				self.update_collection( clear_items= True )
				item = doc.set_collection.get_item_by_name( new_name )
				#doc.active_set = item.get_name( )
				doc.event_manager.post_set_created_event( [ item ] )
				if getattr( doc, 'animation_sets_pane', None ):
					doc.animation_sets_pane.refresh_ui( )

		return success



#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
## Group Data ##
#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# Individual Group data object
class Group_Item( object ):
	def __init__( self, doc, name, set_name = None, master_group = None ):
		self.doc = doc
		self.name = name
		self.set_name = set_name
		self.master_group = master_group


	def get_name( self ):
		"""
		This method gets and returns Group_Item Object name.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``name`` -Group_Item object name.
		"""

		return self.name


	def get_node_type( self ):
		"""
		This method gets and returns Group_Item node type constant.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``node type constant`` -Node type constant.
		"""

		return ctg.ae2.ui.const.NODE_TYPE_ANIM_GROUP_TREE


	def get_set_name( self ):
		"""
		This method gets and return set name.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``set_name`` -animation set to which the animation group belongs.
		"""

		return self.set_name


	def get_tag_associations( self ):
		"""
		This method gets and returns tag asociation object for animation group.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``tag association object`` -tag association object if it exists, otherwise None.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return None

		if self.set_name:
			return doc.get_anim_set_tag_associations( self.get_set_name( ), self.get_name( ) )

		return None


	def create( self, new_name = u'New_Anim_Group', parent_name = "Default" ):
		"""
		This creates a new animation set.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``new_name`` 	-Animation group name
			* ``parent_name`` -Animation group parent name

		*Returns:*
			* ``bool`` -indicating whether the operation was successful or not.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		valid = self.validate_name( new_name )

		did_create = False
		if valid:
			did_create = doc.undoable_create_anim_group( new_name, parent_name )
			if did_create:
				doc.anim_group_collection.update_collection( clear_items = True )
				item = doc.anim_group_collection.get_item_by_name( new_name )
				doc.event_manager.post_group_created_event( [ item ] )

		print 'Create Anim Group: {0}  Name:{1} Parent:{2}'.format( did_create, new_name, parent_name )
		return did_create


	def rename( self, new_name ):
		"""
		This method renames a Animation group.

		*Arguments:*
			* ``new_name`` -new animation set name.

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``bool`` -indicating whether the operation was successful or not.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		old_name = self.get_name( )
		valid = self.validate_name( new_name )

		did_rename = False
		if valid:
			did_rename = doc.undoable_rename_anim_group( self.get_name( ), new_name )
			if did_rename:
				doc.anim_group_collection.update_collection( clear_items = True )
				group_item = doc.anim_group_collection.get_item_by_name( new_name )
				doc.event_manager.post_group_renamed_event( [ group_item ], old_name = old_name )

		print 'Rename Anim Group: {0}  From:{1} To:{2}'.format( did_rename, old_name, new_name )
		return did_rename


	def delete( self ):
		"""
		This method deletes animation group.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``bool`` -indicating whether the operation was successful or not.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		item_name = self.get_name( )
		did_delete = doc.undoable_delete_anim_group( self.get_name( ) )
		if did_delete:
			doc.anim_group_collection.update_collection( clear_items = True )
			doc.event_manager.post_group_deleted_event( [ None ], group_name = item_name )

		print 'Delete Anim Group: {0}'.format( item_name )
		return did_delete


	def get_group_parent_name( self ):
		"""
		This method gets and returns animation group parent name.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``group parent name`` -group parent name.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		return doc.get_anim_group_parent_name( self.get_name( ) )


	def get_group_clip_path( self ):
		"""
		This method gets and return group clip path.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``path`` -group clip path
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		return doc.get_anim_group_clip_path( self.get_name( ) )


	def reparent_group( self, new_parent ):
		"""
		This method reparents animation group.

		*Arguments:*
			* ``new_parent`` -new parent name.

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``bool`` -bool indicating the operation was successful or not.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		return doc.undoable_reparent_anim_group( self.get_name( ), new_parent )


	def set_group_clip_path( self, new_path ):
		"""
		This method sets animation group clip path.

		*Arguments:*
			* ``new_path`` -new group clip path

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``bool`` -bool indicating the operation was successful or not.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		return doc.undoable_set_anim_group_clip_path( self.get_name( ), new_path )


	def validate_name( self, value ):
		"""
		This Method checks the name for invalid characters, also checks if
		the name exists in sets collection.

		*Arguments:*
			* ``name`` -name to be validated

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``bool`` -True indicates the name is valid, and False the name is not valid.

		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		if value == '':
			return False

		valid_name = doc.anim_group_collection.validate_name_pattern( value )
		if valid_name:
			exists = doc.anim_group_collection.check_name_existance( value )
			if not exists:
				return True
			else:
				if self.get_name().lower() != value.lower():
					return False
				else:
					return True
		else:
			return False


	def get_unique_name( self, name ):
		"""
		Checks if the name exists in groups collection, if the name exists adds an
		index and return it as new name, if the name does not exists in the
		collection, return the name.

		*Arguments:*
			* ``name`` -The initial name

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``unique name`` -The current unique name
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		return doc.anim_group_collection.get_unique_name( name )




# Group data collection
class Group_Collection( Collection ):
	def __init__( self, doc, set_name ):
		self.set_name = set_name
		Collection.__init__( self, doc )


	def _gather_item_names( self ):
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		return set( doc.get_anim_set_group_names( self.set_name ) )


	def _create_item( self, name ):
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		master_group = doc.anim_group_collection.get_item_by_name( name )

		return Group_Item( doc, name, self.set_name, master_group = master_group )


	def get_node_type( self ):
		return ctg.ae2.ui.const.NODE_TYPE_ANIM_GROUP_TREE

	def create( self, new_name = 'New_Anim_Group', parent_name = '' ):
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		valid = self.validate_name( new_name )

		success = False
		if valid:
			success = doc.undoable_create_anim_group( new_name, parent_name )
			if success:
				self.update_collection( clear_items= True )

		return success



class Anim_Group_Collection( Collection ):
	def _gather_item_names( self ):
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		return set( doc.get_anim_group_names( ) )


	def _create_item( self, name ):
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		return Group_Item( doc, name, None )


	def get_node_type( self ):
		return ctg.ae2.ui.const.NODE_TYPE_ANIM_GROUP_TREE


	def create( self, new_name = 'New_Anim_Group', parent_name = '' ):
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		valid = self.validate_name( new_name )

		success = False
		if valid:
			success = doc.undoable_create_anim_group( new_name, parent_name )
			if success:
				self.update_collection( clear_items= True )
				item = doc.anim_group_collection.get_item_by_name( new_name )
				doc.event_manager.post_group_created_event( [ item ] )


		return success




#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
## Control filter Data ##
#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

# Individual Control Filter data object
class Control_Filter_Item( object ):
	"""
	Class for the Individual control filter data object

	*Arguments:*
		* ``doc``  -Active animation document
		* ``name`` -name of the animation control filter object

	*Keyword Arguments:*
		* ``none``
	"""

	def __init__( self, doc, name ):
		self.doc = doc
		self.name = name


	def get_name( self ):
		"""
		This method gets and returns Control_Filter_Item name.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``name`` -Control_Filter_Item name
		"""

		return self.name


	def get_node_type( self ):
		"""
		This method gets and returns Control_Filter_Item node type constant.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``node type constant`` -Node type constant.
		"""

		return ctg.ae2.ui.const.NODE_TYPE_CONTROL_FILTER


	def create( self, new_name = 'New_Control_Filter', filter_type =None ):
		"""
		This method creates a new control filter object.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``new_name`` 	-Control filter name
			* ``filter_type`` -Control filter type

		*Returns:*
			* ``bool`` -Indicating the operation was successful or not.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		valid = self.validate_name( new_name )

		success = False
		if valid:

			success = doc.undoable_create_control_filter( new_name, filter_type )
			if success:
				doc.control_filter_collection.update_collection( )
				cf_item = doc.control_filter_collection.get_item_by_name( new_name )
				doc.event_manager.post_control_filter_renamed_event( [ cf_item ], old_name = new_name )

		return success


	def validate_name( self, value ):
		"""
		This Method checks the name for invalid characters, also checks if
		the name exists in control filter collection.

		*Arguments:*
			* ``name`` -name to be validated

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``bool`` -True indicates the name is valid, and False the name is not valid.

		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		if value == '':
			return False

		valid_name = doc.control_filter_collection.validate_name_pattern( value )
		if valid_name:
			exists = doc.control_filter_collection.check_name_existance( value )
			if not exists:
				return True
			else:
				if self.get_name().lower() != value.lower():
					return False
				else:
					return True
		else:
			return False


	def delete( self, ):
		"""
		This method deletes control filters items.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``delete_items`` -list of control filter items to be deleted.

		*Returns:*
			* ``bool`` -indicating the operation was successful.
		"""

		success = False
		doc = AnimationEditor.get_active_document()
		if not doc:
			return success

		did_delete = False

		success = doc.undoable_delete_control_filter( self.get_name( ))
		if success:
			did_delete = True

		if did_delete:
			doc.control_filter_collection.update_collection( )
			doc.event_manager.post_control_filter_deleted_event( [ None ] )

		return did_delete


	def get_unique_name( self, name ):
		"""
		Checks if the name exists in control filter collection, if the name exists adds an
		index and return it as new name, if the name does not exists in the
		collection, return the name.

		*Arguments:*
			* ``name`` -The initial name

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``unique name`` -The current unique name
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		return doc.control_filter_collection.get_unique_name( name )


	def control_is_filter( self ):
		"""
		This method check if the name provided is a animation control filter or not.

		*Arguments:*
			* ``name`` -name to be checked if it is a control filter or not.

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``bool`` -indicating whether the name provided is animation control filter or not.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		return doc.control_is_filter( self.get_name( ) )


	def get_control_filter( self ):
		"""
		This method gets and returns control filter object.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``control filter object`` -animation control filter object.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		return doc.get_control_filter( self.get_name( ) )


	def get_cap_max( self ):
		"""
		This method gets and returns control filter cap max.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``control filter cap max`` -control filter cap max.
		"""

		c_filter = self.get_control_filter( )
		return c_filter.get_cap_max( )


	def get_cap_min( self ):
		"""
		This method gets and returns control filter cap min.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``control filter cap min`` -control filter cap min.
		"""

		c_filter = self.get_control_filter( )
		return c_filter.get_cap_min( )


	def get_input_min( self ):
		"""
		This method gets and returns control filter input min.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``control filter input min`` -control filter input min.
		"""

		c_filter = self.get_control_filter( )
		return c_filter.get_input_min( )


	def get_input_max( self ):
		"""
		This method gets and returns control filter input max.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``control filter input max`` -control filter input max.
		"""

		c_filter = self.get_control_filter( )
		return c_filter.get_input_max( )


	def get_output_min( self ):
		"""
		This method gets and returns control filter output min.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``control filter output min`` -control filter output min.
		"""

		c_filter = self.get_control_filter( )
		return c_filter.get_output_min( )


	def get_output_max( self ):
		"""
		This method gets and returns control filter output max.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``control filter output max`` -control filter output max.
		"""

		c_filter = self.get_control_filter( )
		return c_filter.get_output_max( )


	def get_multiplier( self ):
		"""
		This method gets and returns control filter multiplier.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``control filter multiplier`` -control filter multiplier.
		"""

		c_filter = self.get_control_filter( )
		return c_filter.get_multiplier( )


	def get_addend( self ):
		"""
		This method gets and returns control addend.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``control filter addend`` -control filter addend.
		"""

		c_filter = self.get_control_filter( )
		return c_filter.get_addend( )


	def get_source_name( self ):
		"""
		This method gets and returns control filter source name.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``control filter source name`` -control filter source name.
		"""

		c_filter = self.get_control_filter( )
		return c_filter.get_source_name( )


	def get_type( self ):
		"""
		This method gets and returns control filter type.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``control filter type`` -control filter type.
		"""

		c_filter = self.get_control_filter( )
		return c_filter.get_type( )


	def get_valid_source_names( self ):
		"""
		This method gets and returns control filter valid source names.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``list`` -control filter valid source names.
		"""

		c_filter = self.get_control_filter( )
		return list( c_filter.get_valid_source_names( )	)


	def set_cap_max( self, cap_max ):
		"""
		This method sets control filter cap max.

		*Arguments:*
			* ``cap_max`` -cap max to be set on animation control filter.

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``bool`` -indicating whether operation was successful or not.
		"""

		c_filter = self.get_control_filter( )
		c_filter.set_cap_max( str( cap_max ) )

		return self.modify_update_filter_colle( c_filter )


	def set_cap_min( self, cap_min ):
		"""
		This method sets control filter cap min.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``bool`` -indicating whether operation was successful or not.
		"""

		c_filter = self.get_control_filter( )
		c_filter.set_cap_min( str(cap_min) )

		return self.modify_update_filter_colle( c_filter )



	def set_input_min( self, input_min ):
		"""
		This method sets control filter input min.

		*Arguments:*
			* ``input_min`` -input min to be set on animation control filter.

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``bool`` -indicating whether operation was successful or not.
		"""

		c_filter = self.get_control_filter( )
		c_filter.set_input_min( str( input_min ) )

		return self.modify_update_filter_colle( c_filter )


	def set_input_max( self, input_max ):
		"""
		This method sets control filter input max.

		*Arguments:*
			* ``input_max`` -input min to be set on animation control filter.

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``bool`` -indicating whether operation was successful or not.
		"""

		c_filter = self.get_control_filter( )
		c_filter.set_input_max( str( input_max ) )

		return self.modify_update_filter_colle( c_filter )


	def set_output_min( self, output_min ):
		"""
		This method sets control filter output min.

		*Arguments:*
			* ``output_min`` -output min to be set on animation control filter.

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``bool`` -indicating whether operation was successful or not.
		"""

		success = False
		c_filter = self.get_control_filter( )
		c_filter.set_output_min( str( output_min ) )

		return self.modify_update_filter_colle( c_filter )



	def set_output_max( self, output_max ):
		"""
		This method sets control filter output max.

		*Arguments:*
			* ``output_max`` -output max to be set on animation control filter.

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``bool`` -indicating whether operation was successful or not.
		"""

		c_filter = self.get_control_filter( )
		c_filter.set_output_max( str( output_max ) )

		return self.modify_update_filter_colle( c_filter )


	def set_multiplier( self, multiplier ):
		"""
		This method sets control filter multiplier.

		*Arguments:*
			* ``multiplier`` -multiplier to be set on animation control filter.

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``bool`` -indicating whether operation was successful or not.
		"""

		c_filter = self.get_control_filter( )
		c_filter.set_multiplier( str( multiplier ) )

		return self.modify_update_filter_colle( c_filter )


	def set_addend( self, addend ):
		"""
		This method sets control filter addend.

		*Arguments:*
			* ``addend`` -addend to be set on animation control filter.

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``bool`` -indicating whether operation was successful or not.
		"""

		c_filter = self.get_control_filter( )
		c_filter.set_addend( str( addend ) )

		return self.modify_update_filter_colle( c_filter )


	def set_source_name( self, source_name ):
		"""
		This method sets control filter source name.

		*Arguments:*
			* ``source_name`` -source_name to be set on animation control filter.

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``bool`` -indicating whether operation was successful or not.
		"""

		c_filter = self.get_control_filter( )
		c_filter.set_source_name( str( source_name ) )

		return self.modify_update_filter_colle( c_filter )


	def set_type( self, filter_type ):
		"""
		This method sets control filter type.

		*Arguments:*
			* ``filter_type`` -filter type to be set on animation control filter.

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``bool`` -indicating whether operation was successful or not.
		"""

		c_filter = self.get_control_filter( )
		c_filter.set_type( str( filter_type ) )

		return self.modify_update_filter_colle( c_filter )


	def rename( self, new_name ):
		"""
		This method sets control filter name.

		*Arguments:*
			* ``filter_type`` -name to be set on animation control filter.

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``bool`` -indicating whether operation was successful or not.
		"""
		success = False

		doc = AnimationEditor.get_active_document()
		if not doc:
			return success

		valid = self.validate_name( new_name )
		if valid:

			success = doc.undoable_rename_control_filter( self.get_name( ), new_name )
			if success:
				doc.control_filter_collection.update_collection( )
				cf_item = doc.control_filter_collection.get_item_by_name( new_name )
				doc.event_manager.post_control_filter_renamed_event( [ cf_item ], new_name )

		return success


	def modify_update_filter_colle( self, c_filter ):
		"""
		This method updates control filter object ans updates the control filter
		collection.

		*Arguments:*
			* ``c_filter`` -animation control filter object

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``bool`` -indicating operation was successful or not.
		"""

		success = False
		doc = AnimationEditor.get_active_document()
		if not doc:
			return success

		success = doc.undoable_modify_control_filter( c_filter )
		if success:
			doc.control_filter_collection.update_collection( )

		return success



# Control Filter data collection
class Control_Filter_Collection( Collection ):
	"""
	Control filter collections object

	*Arguments:*
		* ``doc`` -Active animation document.

	*Keyword Arguments:*
		* ``none``
	"""

	def _gather_item_names( self ):
		"""
		Gathers and returns a set of control filter names from the active animation document.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``set`` -Containing animation control filter names.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		return set( doc.get_control_filter_names( ) )


	def _create_item( self, name ):
		"""
		This method creates Control_Filter_Item with a specified name.

		*Arguments:*
			* ``name`` -name for the control filter item.

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``Control_Filter_Item`` -Newly created Control_Filter_Item.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		return Control_Filter_Item( doc, name )


	def get_node_type( self ):
		"""
		This method gets and returns Control_Filter_Collection node type constant.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``node type constant`` -Node type constant.
		"""

		return ctg.ae2.ui.const.NODE_TYPE_CONTROL_FILTER


	def create( self, new_name = 'New_Control_Filter', filter_type = None ):
		"""
		This method creates a new control filter object.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``new_name`` 	-Control filter name
			* ``filter_type`` -Control filter type

		*Returns:*
			* ``bool`` -Indicating the operation was successful or not.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		valid = self.validate_name( new_name )

		success = False
		if valid:
			if filter_type:

				success = doc.undoable_create_control_filter( new_name, filter_type )
				if success:
					self.update_collection( )
					item = self.get_item_by_name( new_name )
					doc.event_manager.post_control_filter_created_event( [ item ] )

		return success


	def get_control_filter( self, name ):
		"""
		This method gets and returns control filter object by name.

		*Arguments:*
			* ``name`` -animation control filter name

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``control filter object`` -animation control filter object.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		return doc.get_control_filter( name )


	def control_is_filter( self, name ):
		"""
		This method check if the name provided is a animation control filter or not.

		*Arguments:*
			* ``name`` -name to be checked if it is a control filter or not.

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``bool`` -indicating whether the name provided is animation control filter or not.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		return doc.control_is_filter( name )



#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
## Control Parameter Data ##
#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

# Individual Parameter Filter data object
class Control_Parameter_Item( object ):
	"""
	Class for the Individual control parameter data object

	*Arguments:*
		* ``doc``  -Active animation document
		* ``name`` -name of the animation control parameter object

	*Keyword Arguments:*
		* ``none``
	"""

	def __init__( self, doc, name ):
		self.doc = doc
		self.name = name


	def get_name( self ):
		"""
		This method gets and returns Control_Parameter_Item name.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``name`` -Control_Parameter_Item name
		"""

		return self.name


	def get_node_type( self ):
		"""
		This method gets and returns Control_Parameter_Item node type constant.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``node type constant`` -Node type constant.
		"""

		return ctg.ae2.ui.const.NODE_TYPE_CONTROL_PARAMETER


	def create( self, new_name = 'New_Control_Parameter' ):
		"""
		This method creates a new control parameter object.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``new_name`` -Control parameter name

		*Returns:*
			* ``bool`` -Indicating the operation was successful or not.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		valid = self.validate_name( new_name )

		success = False
		if valid:
			success = doc.undoable_create_control_parameter( new_name )
			if success:
				doc.control_parameter_collection.update_collection( )
				cp_item = doc.control_parameter_collection.get_item_by_name( new_name )
				doc.event_manager.post_control_parameter_renamed_event( [ cp_item ], old_name = new_name )

		return success



	def validate_name( self, name ):
		"""
		This Method checks the name for invalid characters, also checks if
		the name exists in control parameter collection.

		*Arguments:*
			* ``name`` -name to be validated

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``bool`` -True indicates the name is valid, and False the name is not valid.

		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		if name == '':
			return False

		valid_name = doc.control_parameter_collection.validate_name_pattern( name )
		if valid_name:
			exists = doc.control_parameter_collection.check_name_existance( name )
			if not exists:
				return True
			else:
				if self.get_name().lower() != name.lower():
					return False
				else:
					return True
		else:
			return False


	def get_unique_name( self, name ):
		"""
		Checks if the name exists in control parameter collection, if the name exists adds an
		index and return it as new name, if the name does not exists in the
		collection, return the name.

		*Arguments:*
			* ``name`` -The initial name

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``unique name`` -The current unique name
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		return doc.control_parameter_collection.get_unique_name( name )



	def delete( self, ):
		"""
		This method deletes control parameter items.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``delete_items`` -list of control parameter items to be deleted.

		*Returns:*
			* ``bool`` -indicating the operation was successful.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		do_update = False
		success = False
		success = doc.undoable_delete_control_parameter( self.get_name( ) )
		if success:
			do_update = True

		if do_update:
			doc.control_parameter_collection.update_collection( clear_items=True )
			doc.event_manager.post_control_parameter_renamed_event( [ None ], self.get_name( ) )

		return success


	def control_is_parameter( self ):
		"""
		This methed checks if name provided is animation control parameter or not.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``bool`` -indicating whether name is control parameter or not.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		return doc.control_is_parameter( self.get_name( ) )


	def get_control_parameter( self ):
		"""
		This method gets and returns animation control parameter object.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``control parameter object`` -animation control parameter object
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		return doc.get_control_parameter( self.get_name( ) )


	def get_data_type( self ):
		"""
		This method gets and returns control parameter data type.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``data type`` -control parameter object data type
		"""

		c_parameter = self.get_control_parameter( )
		return c_parameter.get_data_type( )


	def get_default_value( self ):
		"""
		This method gets and returns control parameter object default value.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``default value`` -control parameter object default value.
		"""

		c_parameter = self.get_control_parameter( )
		return c_parameter.get_default_value( )


	def get_min_value( self ):
		"""
		This method gets and returns control parameter object min value.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``min value`` -control parameter object min value.
		"""

		c_parameter = self.get_control_parameter( )
		return c_parameter.get_min_value( )


	def get_max_value( self ):
		"""
		This method gets and returns control parameter object max value.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``max value`` -control parameter object max value.
		"""

		c_parameter = self.get_control_parameter( )
		return c_parameter.get_max_value( )

	def get_is_momentary( self ):
		"""
		This method gets and returns control parameter's is_momentary flag.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``is_momentary`` -is it momentary?
		"""

		c_parameter = self.get_control_parameter( )
		return c_parameter.get_is_momentary( )

	def get_is_random( self ):
		"""
		This method gets and returns control parameter's is_random flag.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``is_random`` -is it random?
		"""

		c_parameter = self.get_control_parameter( )
		return c_parameter.get_is_random( )


	def get_float_track_src( self ):
		"""
		This method gets and returns control parameter's float_track_src.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``float_track_src`` -the thing you're asking for
		"""

		c_parameter = self.get_control_parameter( )
		return c_parameter.get_float_track_src( )

	def get_string_crc_src( self ):
		"""
		This method gets and returns control parameter's string_crc_src.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``string_crc_src`` -the thing you're asking for
		"""

		c_parameter = self.get_control_parameter( )
		return c_parameter.get_string_crc_src( )

	def set_data_type( self, data_type ):
		"""
		This method sets control parameter object data type.

		*Arguments:*
			* ``data_type`` - data type to be set oncontrol parameter object.

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``bool`` -indicating operation was successful or not.
		"""

		c_parameter = self.get_control_parameter( )
		c_parameter.set_data_type( str( data_type ))

		return self.modify_update_parameter_colle( c_parameter )


	def set_default_value( self, default_value ):
		"""
		This method sets control parameter object default value.

		*Arguments:*
			* ``default_value`` - default value to be set oncontrol parameter object.

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``bool`` -indicating operation was successful or not.
		"""

		c_parameter = self.get_control_parameter( )
		c_parameter.set_default_value( str( default_value ).lower(), False )

		return self.modify_update_parameter_colle( c_parameter )


	def set_min_value( self, min_value ):
		"""
		This method sets control parameter object min value.

		*Arguments:*
			* ``min_value`` - min value to be set oncontrol parameter object.

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``bool`` -indicating operation was successful or not.
		"""

		c_parameter = self.get_control_parameter( )
		c_parameter.set_min_value( str( min_value ))

		return self.modify_update_parameter_colle( c_parameter )


	def set_max_value( self, max_value ):
		"""
		This method sets control parameter object max value.

		*Arguments:*
			* ``max_value`` - max value to be set oncontrol parameter object.

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``bool`` -indicating operation was successful or not.
		"""

		c_parameter = self.get_control_parameter( )
		c_parameter.set_max_value( str( max_value ) )

		return self.modify_update_parameter_colle( c_parameter )

	def set_is_momentary( self, momentary ):
		"""
		This method sets control parameter object momentary flag.

		*Arguments:*
			* ``momentary`` - momentary flag to be set on control parameter object.

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``bool`` -indicating operation was successful or not.
		"""

		c_parameter = self.get_control_parameter( )
		c_parameter.set_is_momentary( str( momentary ) )

		return self.modify_update_parameter_colle( c_parameter )

	def set_is_random( self, random_value ):
		"""
		This method sets control parameter object random flag.

		*Arguments:*
			* ``random_value`` - random flag to be set oncontrol parameter object.

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``bool`` -indicating operation was successful or not.
		"""

		c_parameter = self.get_control_parameter( )
		c_parameter.set_is_random( str( random_value ) )

		return self.modify_update_parameter_colle( c_parameter )


	def set_float_track_src( self, float_track_src ):
		"""
		This method sets control parameter's float track src name.

		*Arguments:*
			* ``float_track_src`` - Name of the float track to use as src.

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``bool`` -indicating operation was successful or not.
		"""

		c_parameter = self.get_control_parameter( )
		c_parameter.set_float_track_src( float_track_src )

		return self.modify_update_parameter_colle( c_parameter )

	def set_string_crc_src( self, string_crc_src ):
		"""
		This method sets control parameter's string crc src name.

		*Arguments:*
			* ``string_crc_src`` - Name of the string to use as the crc source

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``bool`` -indicating operation was successful or not.
		"""

		c_parameter = self.get_control_parameter( )
		c_parameter.set_string_crc_src( string_crc_src )

		return self.modify_update_parameter_colle( c_parameter )


	def rename( self, new_name ):
		"""
		This sets name on animation state machine object.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``bool`` -indicating the operation was successful
		"""
		success = False

		doc = AnimationEditor.get_active_document()
		if not doc:
			return success

		valid = self.validate_name( new_name )
		if valid:

			success = doc.undoable_rename_control_parameter( self.get_name( ), new_name )
			if success:
				doc.control_parameter_collection.update_collection( )
				cp_item = doc.control_parameter_collection.get_item_by_name( new_name )
				doc.event_manager.post_control_parameter_renamed_event( [ cp_item ], new_name )

		return success


	def modify_update_parameter_colle( self, c_parameter ):
		"""
		This method updates control parameter object ans updates the control parameter
		collection.

		*Arguments:*
			* ``c_parameter`` -animation control parameter object

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``bool`` -indicating operation was successful or not.
		"""
		success = False

		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		success = doc.undoable_modify_control_parameter( c_parameter )
		if success:
			doc.control_parameter_collection.update_collection( )

		return success



# Control Parameter data collection
class Control_Parameter_Collection( Collection ):
	"""
	Control parameter collections object

	*Arguments:*
		* ``doc`` -Active animation document.

	*Keyword Arguments:*
		* ``none``
	"""

	def _gather_item_names( self ):
		"""
		Gathers and returns a set of control parameter names from the active animation document.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``set`` -Containing animation control parameter names.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		return set( doc.get_control_parameter_names( ) )


	def _create_item( self, name ):
		"""
		This method creates Control_Parameter_Item with a specified name.

		*Arguments:*
			* ``name`` -name for the control parameter item.

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``Control_Parameter_Item`` -Newly created Control_Parameter_Item.
		"""

		return Control_Parameter_Item( self.doc, name )


	def get_node_type( self ):
		"""
		This method gets and returns Control_Parameter_Collection node type constant.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``node type constant`` -Node type constant.
		"""

		return ctg.ae2.ui.const.NODE_TYPE_CONTROL_PARAMETER


	def create( self, new_name = 'New_Control_Parameter' ):
		"""
		This method creates a new control parameter object.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``new_name`` -Control parameter name

		*Returns:*
			* ``bool`` -Indicating the operation was successful or not.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		valid = self.validate_name( new_name )

		success = False
		if valid:
			success = doc.undoable_create_control_parameter( new_name )
			if success:
				self.update_collection( )
				item = self.get_item_by_name( new_name )
				doc.event_manager.post_control_parameter_created_event( [ item ] )
			else:
				print 'Document could not create this control parameter: {0}'.format( new_name )
		else:
			print 'This control parameter name is not valid: {0}'.format( new_name )

		return success


	def control_is_parameter( self, name ):
		"""
		This methed checks if name provided is animation control parameter or not.

		*Arguments:*
			* ``name`` -name to be check if it is control parameter or not.

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``bool`` -indicating whether name is control parameter or not.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		return doc.control_is_parameter( name )


	def get_control_parameter( self, name ):
		"""
		This method gets and returns animation control parameter object by name.

		*Arguments:*
			* ``name`` -animation control parameter name.

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``control parameter object`` -animation control parameter object
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return None

		return doc.get_control_parameter( name )


	def get_cond_expression_params( self, expression ):
		"""
		This method gets and returns condtional expression for animation control
		parameters.

		*Arguments:*
			* ``expression`` -control parameter expression.

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``condtional expression`` -animation parameters condtional expression
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		return doc.get_conditional_expression_parameters( expression )



#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
## State Machine Data ##
#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

# Individual State Machine data object
class State_Machine_Item( object ):
	"""
	Class for the Individual state machine data object

	*Arguments:*
		* ``doc``  -Active animation document
		* ``name`` -name of the animation state machine object

	*Keyword Arguments:*
		* ``none``
	"""

	def __init__( self, doc, name ):
		self.doc = doc
		self.name = name
		self.node_graph = None


	def get_name( self ):
		"""
		This method gets and returns State_Machine_Item name.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``name`` -State_Machine_Item name
		"""

		return self.name


	def get_node_type( self ):
		"""
		This method gets and returns State_Machine_Item node type constant.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``node type constant`` -Node type constant.
		"""

		return ctg.ae2.ui.const.NODE_TYPE_STATE_MACHINE


	def create( self, new_name = 'New_State_Machine' ):
		"""
		This method creates a new state machine object.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``new_name`` -State machine name

		*Returns:*
			* ``bool`` -Indicating the operation was successful or not.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		valid = self.validate_name( new_name )

		success = False
		if valid:
			create = doc.undoable_create_state_machine( new_name )
			if create:
				doc.state_machine_collection.update_collection( )
				doc.node_graph_tree_collection.update_collection( )
				item = doc.state_machine_collection.get_item_by_name( new_name )
				if item:
					doc.event_manager.post_state_machine_created_event( [ item ] )
					success = True

		return success


	def validate_name( self, name ):
		"""
		This Method checks the name for invalid characters, also checks if
		the name exists in state machine collection.

		*Arguments:*
			* ``name`` -name to be validated

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``bool`` -True indicates the name is valid, and False the name is not valid.

		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		if name == '':
			return False

		valid_name = doc.state_machine_collection.validate_name_pattern( name )
		if valid_name:
			exists = doc.state_machine_collection.check_name_existance( name )
			if not exists:
				return True
			else:
				if self.get_name().lower() != name.lower():
					return False
				else:
					return True
		else:
			return False


	def delete( self, ):
		"""
		This method deletes state machine items.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``delete_items`` -list of state machine items to be deleted.

		*Returns:*
			* ``bool`` -indicating the operation was successful.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		# Need to update if any deletes are successful
		should_update = False

		old_name = self.get_name( )
		success = doc.undoable_delete_state_machine( old_name )
		if success:
			doc.node_graph_panel.handle_node_graph_delete( old_name )
			should_update = True

		if should_update:
			doc.state_machine_collection.update_collection( clear_items = True  )
			doc.node_graph_tree_collection.update_collection( clear_items = True  )
			doc.event_manager.post_state_machine_deleted_event( [ self ] )

		return should_update


	def get_unique_name( self, name ):
		"""
		Checks if the name exists in state machine collection, if the name exists adds an
		index and return it as new name, if the name does not exists in the
		collection, return the name.

		*Arguments:*
			* ``name`` -The initial name

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``unique name`` -The current unique name
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		return doc.state_machine_collection.get_unique_name( name )


	def get_state_machine( self ):
		"""
		This method gets and returns animation state machine object.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``state machine object`` -animation state machine object.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		return doc.get_node_graph( self.get_name( ) )


	def rename( self, new_name ):
		"""
		This sets name on animation state machine object.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``bool`` -indicating the operation was successful
		"""
		success = False

		doc = AnimationEditor.get_active_document()
		if not doc:
			return success

		valid = self.validate_name( new_name )
		if valid:

			old_name = self.get_name( )

			success = doc.undoable_rename_state_machine( old_name, new_name )
			if success:
				doc.node_graph_panel.handle_node_graph_rename( old_name, new_name )
				doc.state_machine_collection.update_collection( )
				doc.node_graph_tree_collection.update_collection( )
				state_item = doc.state_machine_collection.get_item_by_name( new_name )
				doc.event_manager.post_state_machine_renamed_event( [ state_item ], old_name = old_name, new_name = new_name )

		return success


	def get_node_graph( self ):
		"""
		Get the node graph object for the node graph name.
		This is only necessary if we intend to get the dependencies.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``node_graph`` The actual node graph object for this item

		*Examples:* ::

			Enter code examples here. (optional field)

		*Todo:*
			* Enter thing to do. (optional field)
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		self.node_graph = doc.get_node_graph( self.name )
		return self.node_graph



# State Machine data collection
# class State_Machine_Collection( Collection ):
class State_Machine_Collection( Enumeration_Collection ):
	"""
	State machine collections object

	*Arguments:*
		* ``doc`` -Active animation document.

	*Keyword Arguments:*
		* ``none``
	{0}
	"""

	def _gather_item_names( self ):
		"""
		Gathers and returns a set of state machine names from the active animation document.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``set`` -Containing animation state machine names.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		state_machines = self._gather_item_infos( )

		return set( state_machines )
		#return set( doc.get_state_machine_names( ) )


	# def _gather_virtual_infos( self ):
	# 	return [ item for item in self.doc.get_state_machine_infos( ) if isinstance( item, AnimationEditor.ae_object_info ) and not item.exists_on_disk( ) ]


	def _create_item( self, name, virtual = False ):
		"""
		This method creates State_Machine_Item with a specified name.

		*Arguments:*
			* ``name`` -name for the state machine item.

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``State_Machine_Item`` -Newly created State_Machine_Item.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		return State_Machine_Item( doc, name )


	def get_node_type( self ):
		"""
		This method gets and returns State_Machine_Item node type constant.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``node type constant`` -Node type constant.
		"""

		return ctg.ae2.ui.const.NODE_TYPE_STATE_MACHINE


	def create( self, new_name = 'New_State_Machine' ):
		"""
		This method creates a new state machine object.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``new_name`` -state machine name

		*Returns:*
			* ``bool`` -Indicating the operation was successful or not.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		valid = self.validate_name( new_name )

		success = False
		if valid:
			created = doc.undoable_create_state_machine( new_name )
			if created:
				self.update_collection( clear_items = True )
				doc.node_graph_tree_collection.update_collection( clear_items = True )
				item = doc.state_machine_collection.get_item_by_name( new_name )
				if item:
					doc.event_manager.post_state_machine_created_event( [ item ] )
					success = True

		return success



#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
## Blend Tree Data ##
#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

# Individual Blend Tree data object
class Blend_Tree_Item( object ):
	"""
	Class for the Individual blend tree data object

	*Arguments:*
		* ``doc``  -Active animation document
		* ``name`` -name of the animation blend tree object

	*Keyword Arguments:*
		* ``virtual`` Bool as to whether this is a fake file or not
	"""

	def __init__( self, doc, name, virtual = False ):
		self.doc = doc
		self.name = name
		self.virtual = virtual
		self.node_graph = None


	def get_name( self ):
		"""
		This method gets and returns Blend_Tree_Item name.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``name`` -Blend_Tree_Item name
		"""

		return self.name


	def get_node_type( self ):
		"""
		This method gets and returns Blend_Tree_Item node type constant.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``node type constant`` -Node type constant.
		"""

		return ctg.ae2.ui.const.NODE_TYPE_BLEND_TREE


	def create( self, new_name = 'New_Blend_Tree' ):
		"""
		This method creates a new blend tree object.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``new_name`` -Blend tree name

		*Returns:*
			* ``bool`` -Indicating the operation was successful or not.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		valid = self.validate_name( new_name )

		success = False
		if valid:
			create = doc.undoable_create_blend_tree( new_name )
			if create:
				doc.blend_tree_collection.update_collection( clear_items = True )
				doc.node_graph_tree_collection.update_collection( clear_items = True )
				item = doc.blend_tree_collection.get_item_by_name( new_name )
				if item:
					doc.event_manager.post_blend_tree_created_event( [ item ] )
					success = True

		return success


	def validate_name( self, name ):
		"""
		This Method checks the name for invalid characters, also checks if
		the name exists in blend tree collection.

		*Arguments:*
			* ``name`` -name to be validated

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``bool`` -True indicates the name is valid, and False the name is not valid.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		if name == '':
			return False

		valid_name = doc.blend_tree_collection.validate_name_pattern( name )
		if valid_name:
			exists = doc.blend_tree_collection.check_name_existance( name )
			if not exists:
				return True
			else:
				if self.get_name().lower() != name.lower():
					return False
				else:
					return True
		else:
			return False


	def delete( self, ):
		"""
		This method deletes blend tree items.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``delete_items`` -list of blend tree items to be deleted.

		*Returns:*
			* ``bool`` -indicating the operation was successful.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		# Need to update if any deletes are successful
		should_update = False

		old_name = self.get_name( )
		success = doc.undoable_delete_blend_tree( old_name )
		if success:
			doc.node_graph_panel.handle_node_graph_delete( old_name )
			should_update = True

		if should_update:
			doc.blend_tree_collection.update_collection( clear_items = True )
			doc.node_graph_tree_collection.update_collection( clear_items = True )
			doc.event_manager.post_blend_tree_deleted_event(  [ self ]  )

		return should_update


	def get_unique_name( self, name ):
		"""
		Checks if the name exists in blend tree collection, if the name exists adds an
		index and return it as new name, if the name does not exists in the
		collection, return the name.

		*Arguments:*
			* ``name`` -The initial name

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``unique name`` -The current unique name
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		return doc.blend_tree_collection.get_unique_name( name )


	def get_blend_tree( self ):
		"""
		This method gets and returns animation blend tree object.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``blend tree object`` -animation blend tree object
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		return doc.get_node_graph( self.get_name( ) )


	def get_export_xml( self ):
		"""
		This method gets and returns animation blend tree object export xml.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``blend tree export xml`` -animation blend tree object export xml.
		"""

		b_tree = self.get_blend_tree( )
		return b_tree.get_export_xml( )


	def get_source_xml( self ):
		"""
		This method get and returns animation blend tree source xml.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``blend tree source xml`` -Animation blend tree object source xml.
		"""

		b_tree = self.get_blend_tree( )
		return b_tree.get_source_xml( )


	def set_export_xml( self, export_xml ):
		"""
		This sets export xml on animation blend tree object.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``bool`` -indicating the operation was successful
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		b_tree = self.get_blend_tree( )
		b_tree.set_export_xml( export_xml )

		return doc.undoable_modify_blend_tree( b_tree )


	def set_source_xml( self, source_xml ):
		"""
		This sets source xml on animation blend tree object.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``bool`` -indicating the operation was successful
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		b_tree = self.get_blend_tree( )
		b_tree.set_source_xml( source_xml )

		return doc.undoable_modify_blend_tree( b_tree )


	def rename( self, new_name ):
		"""
		This sets name on animation blend tree object.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``bool`` -indicating the operation was successful
		"""
		success = False

		doc = AnimationEditor.get_active_document()
		if not doc:
			return success

		valid = self.validate_name( new_name )
		if valid:
			old_name = self.get_name( )
			success = doc.undoable_rename_blend_tree( old_name, new_name )
			if success:
				doc.node_graph_panel.handle_node_graph_rename( old_name, new_name )
				doc.blend_tree_collection.update_collection( )
				doc.node_graph_tree_collection.update_collection( )
				bt_item = doc.blend_tree_collection.get_item_by_name( new_name )
				doc.event_manager.post_blend_tree_renamed_event( [ bt_item ], old_name = old_name, new_name = new_name )

		return success


	def get_node_graph( self ):
		"""
		Get the node graph object for the node graph name.
		This is only necessary if we intend to get the dependencies.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``node_graph`` The actual node graph object for this item

		*Examples:* ::

			Enter code examples here. (optional field)

		*Todo:*
			* Enter thing to do. (optional field)
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		self.node_graph = doc.get_node_graph( self.name )
		return self.node_graph



# Blend Tree data collection
class Blend_Tree_Collection( Enumeration_Collection ):
	"""
	Blend tree collections object

	*Arguments:*
		* ``doc`` -Active animation document.

	*Keyword Arguments:*
		* ``none``
	"""

	def _gather_item_names( self ):
		"""
		Gathers and returns a set of blend tree names from the active animation document.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``set`` -Containing animation blend tree names.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		#blend_trees = vlib.data_enum.get_enumerated_data( 'animation_blend_trees', '' )
		#blend_trees = vlib.data_enum.get_enumerated_data( self.provider_id, self.data_set_it )
		blend_trees = super( Blend_Tree_Collection, self )._gather_item_names( )
		#blend_tree_infos = doc.get_blend_tree_infos( )

		return set( blend_trees )
		# Old way
		#return set( doc.get_blend_tree_names( ) )


	# def _gather_virtual_infos( self ):
	# 	return [ item for item in self.doc.get_blend_tree_infos( ) if isinstance( item, AnimationEditor.ae_object_info ) and item.exists_on_disk( ) ]


	def _create_item( self, name, virtual = False ):
		"""
		This method creates Blend_Tree_Item with a specified name.

		*Arguments:*
			* ``name`` -name for the blend tree item.

		*Keyword Arguments:*
			* ``virtual`` Bool is this a fake object?

		*Returns:*
			* ``Blend_Tree_Item`` -Newly created Blend_Tree_Item.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		return Blend_Tree_Item( doc, name, virtual = virtual )


	def get_node_type( self ):
		"""
		This method gets and returns Blend_Tree_Item node type constant.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``node type constant`` -Node type constant.
		"""

		return ctg.ae2.ui.const.NODE_TYPE_BLEND_TREE



	def create( self, new_name = 'New_Blend_Tree' ):
		"""
		This method creates a new blend tree object.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``new_name`` -Blend tree name.

		*Returns:*
			* ``bool`` -Indicating the operation was successful or not.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		valid = self.validate_name( new_name )

		success = False
		if valid:
			created = doc.undoable_create_blend_tree( new_name )
			if created:
				self.update_collection( )
				doc.node_graph_tree_collection.update_collection( )
				item = doc.blend_tree_collection.get_item_by_name( new_name )
				if item:
					doc.event_manager.post_blend_tree_created_event( [ item ] )
					success = True

		return success




#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
## Action Tag Data ##
#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# Individual Action Tag data object
class Action_Tag_Item( object ):
	"""
	Class for the Individual action tag data object

	*Arguments:*
		* ``doc``  -Active animation document
		* ``name`` -name of the animation action tag object

	*Keyword Arguments:*
		* ``temporary``

	"""

	def __init__( self, doc, name, temporary = False ):
		self.doc = doc
		self.name 		= name
		self.temporary = temporary


	def get_name( self ):
		"""
		This method gets and returns Action_Tag_Item name.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``name`` -Action_Tag_Item name.
		"""

		return self.name


	def get_node_type( self ):
		"""
		This method gets and returns Action_Tag_Item node type constant.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``node type constant`` -Node type constant.
		"""

		return ctg.ae2.ui.const.NODE_TYPE_ANIM_ACTION


	def is_used( self ):
		"""
		This method checks if action tag is used or not.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``bool`` -indicating whether action tag is used or not.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		tag_items = doc.tag_association_collection.get_item_by_tag_name( self.get_name( ) )
		if tag_items:
			if len( tag_items ) > 0:
				return True

		return False


	def create( self, new_name = u'New_Action_Tag' ):
		"""
		This method creates a new action tag object.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``new_name`` -Action tag name

		*Returns:*
			* ``bool`` -Indicating the operation was successful or not.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		did_create = False

		# make sure the name is valid
		valid = self.validate_name( new_name )
		if valid:

			# make sure the name is not used as a state tag name
			if new_name not in doc.get_state_names( ):

				did_create = doc.undoable_create_anim_tag( new_name, True, self.temporary )
				if did_create:
					doc.action_tag_collection.update_collection( )
					tag_item = doc.action_tag_collection.get_item_by_name( new_name )
					doc.event_manager.post_action_tag_created_event( [ tag_item ] )

			else:
				dlg = wx.MessageDialog( None, 'The given entry name already exists as a state tag name.\nAction tag names must be unique to state tag names.\n\nExisting State Tag: {0}'.format( new_name ), caption = 'Entry Invalid', style = wx.OK | wx.ICON_INFORMATION )
				ctg.ui.dialogs.show_dialog_modal( dlg )
				dlg.Destroy( )

		return did_create


	def rename( self, new_name ):
		"""
		This method renames animation action tag.

		*Arguments:*
			* ``new_name`` -new action tag name

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``bool`` -indicating operation was successful.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		did_rename = False
		old_name = self.get_name( )

		valid = self.validate_name( new_name )
		if valid:

			# make sure the name is not used as a state tag name
			if new_name not in doc.get_state_names( ):

				did_rename = doc.undoable_rename_anim_tag( self.get_name( ), new_name, True )
				if did_rename:
					doc.action_tag_collection.update_collection( )
					tag_item = doc.action_tag_collection.get_item_by_name( new_name )
					doc.event_manager.post_tag_modified_event( [ tag_item ] )

			else:
				dlg = wx.MessageDialog( None, 'The given entry name already exists as a state tag name.\nAction tag names must be unique to state tag names.\n\nExisting State Tag: {0}'.format( new_name ), caption = 'Entry Invalid', style = wx.OK | wx.ICON_INFORMATION )
				ctg.ui.dialogs.show_dialog_modal( dlg )
				dlg.Destroy( )

		return did_rename


	def delete( self ):
		"""
		This method deletes animation action tag.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``bool`` -indicating operation was successful.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		item_name = self.get_name( )

		did_delete = doc.undoable_delete_anim_tag( self.get_name( ), True, self.temporary )
		if did_delete:
			doc.action_tag_collection.update_collection( clear_items=True )
			doc.event_manager.post_action_tag_delete_event( None )

		print 'Delete: {0} Action Tag: {1}'.format( did_delete, item_name )
		return did_delete


	def validate_name( self, name ):
		"""
		This Method checks the name for invalid characters, also checks if
		the name exists in action tag collection.

		*Arguments:*
			* ``name`` -name to be validated

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``bool`` -True indicates the name is valid, and False the name is not valid.

		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		if name == '':
			return False

		valid_name = doc.action_tag_collection.validate_name_pattern( name )
		if valid_name:
			exists = doc.action_tag_collection.check_name_existance( name )
			if not exists:
				return True
			else:
				if self.get_name().lower() != name.lower():
					return False
				else:
					return True
		else:
			return False


	def get_unique_name( self, name ):
		"""
		Checks if the name exists in action tag collection, if the name exists adds an
		index and return it as new name, if the name does not exists in the
		collection, return the name.

		*Arguments:*
			* ``name`` -The initial name

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``unique name`` -The current unique name
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		return doc.action_tag_collection.get_unique_name( name )



class Action_Tag_Collection( Collection ):
	"""
	Aaction tag collections object

	*Arguments:*
		* ``doc`` -Active animation document.

	*Keyword Arguments:*
		* ``none``
	"""

	def _gather_item_names( self ):
		"""
		Gathers and returns a set of action tag names from the active animation document.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``set`` -Containing animation action tag names.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		return set( doc.get_anim_tags_actions( ) )


	def _create_item( self, name ):
		"""
		This method creates Action_Tag_Item with a specified name.

		*Arguments:*
			* ``name`` -name for the action tag item.

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``Action_Tag_Item`` -Newly created Action_Tag_Item.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		return Action_Tag_Item( doc, name )


	def get_node_type( self ):
		"""
		This method gets and returns Action_Tag_Item node type constant.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``node type constant`` -Node type constant.
		"""

		return ctg.ae2.ui.const.NODE_TYPE_ANIM_ACTION


	def create( self, new_name = 'New_Action_tag' ):
		"""
		This method creates a new action tag object.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``new_name`` -Action tag name

		*Returns:*
			* ``bool`` -Indicating the operation was successful or not.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		did_create = False

		# make sure the name is valid
		valid = self.validate_name( new_name )
		if valid:

			# make sure the entry name doesn't already exist as a state tag name
			if new_name not in doc.get_state_names( ):

				did_create = doc.undoable_create_anim_tag( new_name, True, False )
				if did_create:
					self.update_collection( clear_items= True )
					tag_item = self.get_item_by_name( new_name )
					doc.event_manager.post_action_tag_created_event( [ tag_item ] )

			else:
				dlg = wx.MessageDialog( None, 'The given entry name already exists as a state tag name.\nAction tag names must be unique to state tag names.\n\nExisting State Tag: {0}'.format( new_name ), caption = 'Entry Invalid', style = wx.OK | wx.ICON_INFORMATION )
				ctg.ui.dialogs.show_dialog_modal( dlg )
				dlg.Destroy( )

		return did_create


	def validate_name( self, name ):
		"""
		This Method checks the name for invalid characters, also checks if
		the name exists in action tag collection.

		*Arguments:*
			* ``name`` -name to be validated

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``bool`` -True indicates the name is valid, and False the name is not valid.

		"""
		if name == '':
			return False

		valid_name = self.validate_name_pattern( name )
		if valid_name:
			exists = self.check_name_existance( name )
			if not exists:
				return True
			else:
				return False
		else:
			return False



#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
## State Tag Data ##
#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# Individual State Tag data object
class State_Tag_Item( object ):
	"""
	Class for the Individual state tag data object

	*Arguments:*
		* ``doc``  -Active animation document
		* ``name`` -name of the animation state tag object

	*Keyword Arguments:*
		* ``temporary``
	"""

	def __init__( self, doc, name, temporary = False ):
		self.doc = doc
		self.name = name
		self.temporary = temporary


	def get_name( self ):
		"""
		This method gets and returns State_Tag_Item name.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``name`` -State_Tag_Item name.
		"""

		return self.name


	def get_node_type( self ):
		"""
		This method gets and returns a state tag note type constant

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``node type constant`` -node type constant
		"""

		return ctg.ae2.ui.const.NODE_TYPE_ANIM_STATE


	def is_used( self ):
		"""
		This method checks if state tag is used or not.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``bool`` -indicating whether state tag is used or not.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		tag_items = doc.tag_association_collection.get_item_by_tag_name( self.get_name( ) )
		if tag_items:
			if len( tag_items ) > 0:
				return True

		return False


	def create( self, new_name = u'New_State_Tag' ):
		"""
		This method creates a new state tag object.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``new_name`` -New state tag name.

		*Returns:*
			* ``bool`` -Indicating whether the operation was successful.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		did_create = False

		# make sure the name is valid
		valid = self.validate_name( new_name )
		if valid:

			# make sure the name is not used as an action tag name
			if new_name not in doc.get_action_names( ):

				did_create = doc.undoable_create_anim_tag( new_name, False, self.temporary )
				if did_create:
					doc.state_tag_collection.update_collection( )
					tag_item = doc.state_tag_collection.get_item_by_name( new_name )
					doc.event_manager.post_state_tag_created_event( [ tag_item ] )

			else:
				dlg = wx.MessageDialog( None, 'The given entry name already exists as an action tag name.\nState tag names must be unique to action tag names.\n\nExisting Action Tag: {0}'.format( new_name ), caption = 'Entry Invalid', style = wx.OK | wx.ICON_INFORMATION )
				ctg.ui.dialogs.show_dialog_modal( dlg )
				dlg.Destroy( )

		return did_create


	def rename( self, new_name ):
		"""
		This method renames animation state tag name.

		*Arguments:*
			* ``new_name`` -new state tag name.

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``bool`` -indicating the operation was successful.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		did_rename = False
		old_name = self.get_name( )

		valid = self.validate_name( new_name )
		if valid:

			# make sure the name is not used as an action tag name
			if new_name not in doc.get_action_names( ):

				did_rename = doc.undoable_rename_anim_tag( self.get_name( ), new_name, True )
				if did_rename:
					doc.state_tag_collection.update_collection( )
					tag_item = doc.state_tag_collection.get_item_by_name( new_name )
					doc.event_manager.post_tag_modified_event( [ tag_item ] )

			else:
				dlg = wx.MessageDialog( None, 'The given entry name already exists as an action tag name.\nState tag names must be unique to action tag names.\n\nExisting Action Tag: {0}'.format( new_name ), caption = 'Entry Invalid', style = wx.OK | wx.ICON_INFORMATION )
				ctg.ui.dialogs.show_dialog_modal( dlg )
				dlg.Destroy( )

		return did_rename


	def delete( self ):
		"""
		This method deletes animation state tag.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``bool`` -indicating the operation was successful.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		item_name = self.get_name( )

		did_delete = doc.undoable_delete_anim_tag( self.get_name( ), False, self.temporary )
		if did_delete:
			doc.state_tag_collection.update_collection( clear_items=True )
			doc.event_manager.post_state_tag_delete_event( [ None ] )

		print 'Delete: {0} State Tag: {1}'.format( did_delete, item_name )
		return did_delete


	def validate_name( self, name ):
		"""
		This Method checks the name for invalid characters, also checks if
		the name exists in state tag collection.

		*Arguments:*
			* ``name`` -name to be validated

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``bool`` -True indicates the name is valid, and False the name is not valid.

		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		if name == '':
			return False

		valid_name = doc.state_tag_collection.validate_name_pattern( name )
		if valid_name:
			exists = doc.state_tag_collection.check_name_existance( name )
			if not exists:
				return True
			else:
				if self.get_name().lower() != name.lower():
					return False
				else:
					return True
		else:
			return False


	def get_unique_name( self, name ):
		"""
		Checks if the name exists in state tag collection, if the name exists adds an
		index and return it as new name, if the name does not exists in the
		collection, return the name.

		*Arguments:*
			* ``name`` -The initial name

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``unique name`` -The current unique name
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		return doc.state_tag_collection.get_unique_name( name )



class State_Tag_Collection( Collection ):
	"""
	State tag collections object

	*Arguments:*
		* ``doc`` -Active animation document.

	*Keyword Arguments:*
		* ``none``
	"""

	def _gather_item_names( self ):
		"""
		Gathers and returns a set of state tag names from the active animation document.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``set`` -Containing animation state tag names.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		return set( doc.get_anim_tags_states( ) )


	def _create_item( self, name ):
		"""
		This method creates State_Tag_Item with a specified name.

		*Arguments:*
			* ``name`` -name for the state tag item.

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``State_Tag_Item`` -Newly created State_Tag_Item.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		return State_Tag_Item( doc, name )


	def get_node_type( self ):
		"""
		This method gets and returns State_Tag_Collection node type constant.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``node type constant`` -Node type constant.
		"""

		return ctg.ae2.ui.const.NODE_TYPE_ANIM_STATE


	def create( self, new_name = 'New_State_Tag' ):
		"""
		This method creates a new state tag object.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``new_name`` -New state tag name.

		*Returns:*
			* ``bool`` -Indicating whether the operation was successful.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		did_create = False

		# make sure the name is valid
		valid = self.validate_name( new_name )
		if valid:

			# make sure the entry name doesn't already exist as an action tag name
			if new_name not in doc.get_action_names( ):

				did_create = doc.undoable_create_anim_tag( new_name, False, False )
				if did_create:
					self.update_collection( clear_items= True)
					tag_item = self.get_item_by_name( new_name )
					doc.event_manager.post_state_tag_created_event( [ tag_item ] )
			else:
				dlg = wx.MessageDialog( None, 'The given entry name already exists as an action tag name.\nState tag names must be unique to action tag names.\n\nExisting Action Tag: {0}'.format( new_name ), caption = 'Entry Invalid', style = wx.OK | wx.ICON_INFORMATION )
				ctg.ui.dialogs.show_dialog_modal( dlg )
				dlg.Destroy( )

		return did_create


	def validate_name( self, name ):
		"""
		This Method checks the name for invalid characters, also checks if
		the name exists in state tag collection.

		*Arguments:*
			* ``name`` -name to be validated

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``bool`` -True indicates the name is valid, and False the name is not valid.

		"""

		if name == '':
			return False

		valid_name = self.validate_name_pattern( name )
		if valid_name:
			exists = self.check_name_existance( name )
			if not exists:
				return True
			else:
				return False
		else:
			return False


#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
## Tag Association Data ##
#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# Individual Action Tag data object
class Tag_Association_Item( object ):
	"""
	Class for the Individual tag association data object

	*Arguments:*
		* ``doc``  -Active animation document
		* ``tag``  -animation tag association object

	*Keyword Arguments:*
		* ``set_name`` - Name of the associated animation set
		* ``group_name`` - Name of the associated animation group
	"""

	def __init__( self, doc, tag, set_name = None, group_name = None ):
		self.doc = doc
		self.name 				= tag.get_tag_name( )
		self.tag 				= tag
		self.is_state 			= tag.is_state
		self.set_name 			= set_name
		self.group_name 		= group_name
		self._is_clip_valid 	= True
		self.category = 'Default'
		self.actions = [ ]
		self.states  = [ ]
		self.update_states_and_actions( )



	def is_tag_valid( self ):
		doc = AnimationEditor.get_active_document( )
		if self.tag.is_action():
			if self.get_tag_name( ) in self.actions:
				return True
		elif self.tag.is_state( ):
			if self.get_tag_name( ) in self.states:
				return True

		return False


	def is_used( self ):
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		tag_items = doc.tag_association_collection.get_item_by_tag_name( self.get_name( ) )
		if tag_items:
			if len( tag_items ) > 0:
				return True

		return False


	def get_modifier_value( self, index ):
		tag_modifiers = list( set( self.tag.get_modifiers( ) ) )
		if tag_modifiers:
			for tag in tag_modifiers:
				if tag == ' ':
					tag_modifiers.remove( tag )

			try:
				return tag_modifiers[ index ]
			except IndexError:
				return None

		return None


	def get_tag_modifiers( self ):
		return self.tag.get_modifiers( )


	def set_tag_modifiers( self, modifier_string_list ):
		doc = AnimationEditor.get_active_document( )
		self.tag.set_modifiers( modifier_string_list )

		return doc.undoable_modify_anim_tag_association( self.set_name, self.group_name, self.get_uid( ), self.tag )


	def get_tag_influenced_length( self, val ):
		doc = AnimationEditor.get_active_document( )

		clip = self.get_clip_name( )
		clip_item = self.get_clip_item( )
		tag_items = doc.tag_association_collection.get_item_by_clip_name( clip )

		clip_length = clip_item.get_length( )

		new_length = val * clip_length

		return new_length


	def update_states_and_actions( self ):
		doc = AnimationEditor.get_active_document( )
		self.actions  = list( doc.get_action_names( ) )
		self.states   = list( doc.get_state_names( ) )


	def get_tag_name( self ):
		"""
		This method gets and returns tag association object name.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``tag name`` -tag association object name.
		"""

		return self.tag.get_tag_name( )


	def get_category( self ):
		"""
		This method gets and returns tag association object name.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``tag name`` -tag association object name.
		"""
		self.category = self.tag.get_category( )
		if self.category == '':
			self.category = 'Default'
			#self.set_category( self.category )

		return self.category

	def set_category( self, value ):
		"""
		This method gets and returns tag association object name.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``tag name`` -tag association object name.
		"""
		self.tag.set_category( value )
		self.update_tag( self.tag )


	def get_node_type( self ):
		"""
		This method gets and returns Tag_Association_Item node type constant.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``node type constant`` -Node type constant.
		"""

		return ctg.ae2.ui.const.NODE_TYPE_TAG_ASSOCIATION


	def get_clip_name( self ):
		"""
		This method gets and return animation clip name associated with animation
		tag association object.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``clip name`` -animation clip name
		"""

		return self.tag.get_clip_name( )


	def is_clip_valid( self ):
		"""
		This method checks to see if animation clip name associated with tag
		association object is valid or not.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``bool`` -indicating whether the animation clip is valid or not.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		if self.get_clip_name( ) is 'MISSING_CLIP':
			return False
		else:
			if self.get_clip_name( ).lower( ) in doc.get_properties( ):
				return True

		return False


	def get_clip_item( self ):
		"""
		This method gets and returns Clip_Item associated with tag association object.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``Clip_Item`` -Clip_Item object.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		clip_item = None
		if self.is_clip_valid( ):
			clip_name = self.get_clip_name( )

			# check to see if the reference is an actual clip
			if doc.is_clip( clip_name ):
				clip_item = doc.clip_collection.get_item_by_name( clip_name )

			# check to see if the reference is a node graph
			elif doc.is_node_graph( clip_name ):

				# state machine
				if doc.is_state_machine( clip_name ):
					clip_item = doc.state_machine_collection.get_item_by_name( clip_name )

				# blend tree
				elif doc.is_blend_tree( clip_name ):
					clip_item = doc.blend_tree_collection.get_item_by_name( clip_name )

			if clip_item:
				return clip_item

		return clip_item


	def is_preloaded( self ):
		"""
		This method checks if the animation clip associated with tag association
		object is preloaded or not.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``bool`` -indicating whether animation clip is preloaded or not.
		"""

		value = False
		clip_item = self.get_clip_item( )
		if clip_item:
			if isinstance( clip_item, ctg.ae2.core.data.Clip_Item ):
				value = clip_item.get_flag( u'Preloaded' )

		return value


	def set_preloaded( self, state ):
		"""
		This sets preload flag value on animation clip associated with tag association
		object.

		*Arguments:*
			* ``state`` -preload value to be set on animation clip.

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``bool`` -indicating whether operation was successful or not.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		set_preloaded = False
		if self.is_clip_valid( ):
			clip_item = doc.clip_collection.get_item_by_name( self.get_clip_name( ) )
			if clip_item:
				set_preloaded = clip_item.set_flag( u'Preloaded', state )

		return set_preloaded


	def get_name( self, tag = None ):
		if tag:
			return self.get_tag_name( )
		else:
			if self.get_tag_name != u'':
				return self.get_tag_name( )
			else:
				return self.get_clip_name( )


	def get_uid( self ):
		"""
		This method gets and returns tag association uid.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``uid`` -tag association uid
		"""

		return self.tag.get_uid( )


	def get_speed_multiplier( self ):
		"""
		This method gets and returns tag association speed_multiplier.

		Modification: Updated from length to speed multiplier
		                   -Cole Ingram, cole.ingram@dsvolition.com 5/18/2015

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``length`` -tag association length.
		"""

		return ( '%.2f' % self.tag.get_speed_multiplier( ) )


	def get_mirrored_flag( self ):
		"""
		This method gets and returns tag association mirrored flag.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``mirrored flag`` -tag association mirrored flag.
		"""

		return self.tag.get_mirrored_flag( )


	def get_reverse_flag( self ):
		"""
		This method gets and returns tag association reverse flag.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``reverse flag`` -tag association reverse flag.
		"""

		return self.tag.get_reverse_flag( )


	def get_set_name( self ):
		"""
		This method gets and returns animation set name associated with tag association.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``set name`` -animation set name
		"""

		return self.set_name


	def get_group_name( self ):
		"""
		This method gets and returns animation group name associated with tag association.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``group name`` -animation group name
		"""

		return self.group_name


	def get_tag( self ):
		"""
		This method and returns tag assciation object.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``tag`` -tag association object.
		"""

		return self.tag


	def set_uid( self, uid ):
		"""
		This method sets uid for tag association object.

		*Arguments:*
			* ``uid`` -uid to be set on tag association.

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``bool`` -indicating the operation was successful or not.
		"""
		success = False
		doc = AnimationEditor.get_active_document()
		if not doc:
			return False

		tag = self.get_tag( )
		if tag:
			tag.set_uid( int( uid ) )
			success = self.update_tag( tag )
			if success:
				doc.tag_association_collection.update_collection( )

		return success


	def set_speed_multiplier( self, speed_multiplier ):
		"""
		This method sets length for the tag association.

		Modification: Updated from length to speed multiplier
		                   -Cole Ingram, cole.ingram@dsvolition.com 5/18/2015

		*Arguments:*
			* ``speed_multiplier`` -speed multiplier to be set on tag association object.

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``bool`` -indicating the operation was successful or not.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		success = False
		tag = self.get_tag( )
		if tag:
			tag.set_speed_multiplier( float( speed_multiplier ) )
			success = self.update_tag( tag )
			if success:
				doc.tag_association_collection.update_collection( )

		return success


	def set_mirrored_flag( self, mirrored_flag ):
		"""
		This method sets rag association mirrored flag.

		*Arguments:*
			* ``mirrored_flag`` -mirrored flag to be set on tag association object.

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``bool`` -indicating the operation was successful or not.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		success = False
		tag = self.get_tag( )
		if tag:
			tag.set_mirrored_flag( bool( mirrored_flag ) )
			success = self.update_tag( tag )
			if success:
				doc.tag_association_collection.update_collection( )

		return success


	def set_reverse_flag( self, reverse_flag ):
		"""
		This method sets tag association reverse flag.

		*Arguments:*
			* ``reverse_flag`` -reverse flag to be set on tag association object.

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``bool`` -indicating the operation was successful or not.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		success = False
		tag = self.get_tag( )
		if tag:
			tag.set_reverse_flag( bool( reverse_flag ) )
			success = self.update_tag( tag )
			if success:
				doc.tag_association_collection.update_collection( )

		return success


	def set_clip_name( self, clip_name ):
		"""
		This method sets tag association clip name.

		*Arguments:*
			* ``clip_name`` -clip name to be set on tag association object.

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``bool`` -indicating the operation was successful or not.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		success = False
		tag = self.get_tag( )
		if tag:
			tag.set_clip_name( str( clip_name ) )
			success = self.update_tag( tag )
			if success:
				doc.tag_association_collection.update_collection( )

		return success


	def set_tag_name( self, tag_name ):
		"""
		This method sets tag association clip name.

		*Arguments:*
			* ``clip_name`` -clip name to be set on tag association object.

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``bool`` -indicating the operation was successful or not.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		success = False
		tag = self.get_tag( )
		if tag:
			tag.set_tag_name( str( tag_name ) )
			success = self.update_tag( tag )
			if success:
				doc.tag_association_collection.update_collection( )


		return success


	def is_action( self ):
		"""
		This method checks if the tag association is action tag or not.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``bool`` -indicating whether tag asoociation object is action tag or not.
		"""

		return self.tag.is_action()


	def is_state( self ):
		"""
		This method checks if the tag association is state tag or not.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``bool`` -indicating whether tag asoociation object is state tag or not.
		"""

		return self.tag.is_state()


	def update_tag( self, tag ):
		"""
		This method updates tag association.

		*Arguments:*
			* ``tag`` -tag association to update.

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``bool`` -indicating operation was successful or not.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		set_name = self.get_set_name()
		group_name = self.get_group_name()
		if not set_name:
			set_items = doc.selection_manager.get_recent_sel_sets( )
			if set_items:
				if set_items[0]:
					set_name = set_items[0].get_name( )

		current_set = doc.set_collection.get_item_by_name( set_name )

		if not group_name:
			groups = set_items[0].get_group_names( )
			if groups:
				for group in groups:
					if group == 'Default':
						group_name = group
			else:
				groups = doc.anim_group_collection.get_item_names( )
				for group in groups:
					if group == 'Default':
						current_set.add_group( group )
						group_name = group

		self.update_states_and_actions( )

		return doc.undoable_modify_anim_tag_association( set_name, group_name, self.get_uid( ), tag )


	def modify( self, tag_name ):
		"""
		This method updates tag association and tag association collection.

		*Arguments:*
			* ``tag_name`` -name of the tag association to update.

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``bool`` -indicating operation was successful or not.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		valid = self.validate_name( tag_name )

		did_modify = False
		if valid:
			did_modify = self.update_tag( self.tag )
			if did_modify:
				doc.tag_association_collection.update_collection( )

		print 'Modify Tag Association: {0}  From:{1} To:{2}'.format( did_modify )
		return did_modify


	def delete( self ):
		"""
		This method deletes animation tag object.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``bool`` -Indicating whether the operation was successful or not.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		did_delete = doc.undoable_delete_anim_tag_association( self.set_name, self.group_name, self.get_uid( ) )
		if did_delete:
			doc.tag_association_collection.update_collection( )

		print 'Delete: {0} Tag Association: {1}'.format( did_delete, self.name )
		return did_delete


	def validate_name( self, name ):
		"""
		This Method checks the name for invalid characters, also checks if
		the name exists in tag association collection.

		*Arguments:*
			* ``name`` -name to be validated

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``bool`` -True indicates the name is valid, and False the name is not valid.

		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		if name == '':
			return False

		if doc.tag_association_collection:
			valid_name = doc.tag_association_collection.validate_name_pattern( name )
			if valid_name:
				exists = doc.tag_association_collection.check_name_existance( name )
				if not exists:
					return True
				else:
					if self.get_name().lower() != name.lower():
						return False
					else:
						return True
			else:
				return False


	def get_unique_name( self, name ):
		"""
		Checks if the name exists in sets collection, if the name exists adds an
		index and return it as new name, if the name does not exists in the
		collection, return the name.

		*Arguments:*
			* ``name`` -The initial name

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``unique name`` -The current unique name
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		return doc.tag_association_collection.get_unique_name( name )


	def get_tag_data( self ):
		"""
		This method gets and returns a dictionary containing tag associations object.


		Modification: Updated from length to speed multiplier
		                   -Cole Ingram, cole.ingram@dsvolition.com 5/18/2015


		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``dictionary`` - tag association data dictionary.
		"""

		data_dict = { }

		data_dict[ 'set_clip_name' ] 			= self.tag.get_clip_name( )
		data_dict[ 'set_speed_multiplier' ]	= self.tag.get_speed_multiplier( )
		data_dict[ 'set_mirrored_flag' ]		= self.tag.get_mirrored_flag( )
		data_dict[ 'set_reverse_flag' ]		= self.tag.get_reverse_flag( )
		data_dict[ 'set_tag_name' ] 			= self.tag.get_tag_name( )
		data_dict[ 'set_uid' ]					= self.tag.get_uid( )
		data_dict[ 'set_category' ]			= self.tag.get_category( )
		data_dict[ 'set_tag_modifiers' ]			= list( set( self.tag.get_modifiers( ) ) )
		if self.tag.is_action( ):
			tag_type = ctg.ae2.ui.const.NODE_TYPE_TAG_ACTION
		else:
			tag_type = ctg.ae2.ui.const.NODE_TYPE_TAG_STATE

		data_dict[ 'tag_type' ]	= tag_type

		return data_dict


	def set_preview_tag_association( self ):
		doc = AnimationEditor.get_active_document( )
		if not doc:
			return

		return doc.set_preview_tag_association( int( self.get_uid( ) ) )



class Tag_Association_Collection( Collection ):
	"""
	Tag association collections object

	*Arguments:*
		* ``doc`` -Active animation document.

	*Keyword Arguments:*
		* ``none``
	"""

	def _gather_item_names( self ):
		"""
		Gathers and returns a set of tag associations from the active animation document's
		active animation set and group.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``set`` -Containing animation set's active tag association.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		tag_association_items = [ ]
		if doc.active_set and doc.active_group:
			tag_association_items = set( doc.get_anim_set_tag_associations( doc.active_set, doc.active_group ) )

		return tag_association_items


	def _create_item( self, tag_obj ):
		"""
		This method creates a new tag association item object.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``tag_obj`` -animation tag association object.

		*Returns:*
			* ``Tag_Association_Item`` -newly created Tag_Association_Item.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return


		tag = Tag_Association_Item( doc, tag_obj, set_name = doc.active_set, group_name = doc.active_group )

		return tag


	def get_node_type( self ):
		"""
		This method gets and returns Tag_Association_Collection node type constant.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``node type constant`` -Node type constant.
		"""
		return ctg.ae2.ui.const.NODE_TYPE_TAG_ASSOCIATION



	def get_item_by_clip_name( self, name, use_cached = True ):
		"""
		Retrieves an item from the collection by name.

		*Arguments:*
			* ``name`` 			<String> Key name of the item to lookup.

		*Keyword Arguments:*
			* ``use_cached`` 	<Bool> Use cached results or get latest from document

		*Returns:*
			* ``result`` 		<items> or ``none``
		"""

		if not use_cached:
			self.update_collection( )

		items = [item for item in self.get_items( ) if item.get_clip_name( ) == name ]
		return items


	def get_item_by_tag_name( self, name, not_uid = None, use_cached = False ):
		"""
		Retrieves an item from the collection by name.

		*Arguments:*
			* ``name`` 			<String> Key name of the item to lookup.

		*Keyword Arguments:*
		    * ``not_uid``     <Int> Uid integer that we want to check against, make sure the item does not have this uid
			* ``use_cached`` 	<Bool> Use cached results or get latest from document

		*Returns:*
			* ``items`` 		<items> or ``none``
		"""

		if not use_cached:
			self.update_collection( )

		if not not_uid is None:
			items = [item for item in self.get_items( ) if item.get_tag_name( ) == name and item.get_uid( ) != not_uid ]
		else:
			items = [item for item in self.get_items( ) if item.get_tag_name( ) == name ]
		return items


	def get_item_by_uid( self, uid, use_cached = True ):
		"""
		Retrieves an item from the collection by name.

		*Arguments:*
			* ``name`` 			<String> Key name of the item to lookup.

		*Keyword Arguments:*
			* ``use_cached`` 	<Bool> Use cached results or get latest from document

		*Returns:*
			* ``result`` 		<items> or ``none``
		"""

		if not use_cached:
			self.update_collection( )

		items = [item for item in self.get_items( ) if item.get_uid( ) == uid ]
		return items


	def get_items_from_uids( self, uids, use_cached = True ):
		if not use_cached:
			self.update_collection( )

		items = [item for item in self.get_items( ) if item.get_uid( ) in uids ]
		return items


	def check_tag_existance( self, data_obj ):
		"""
		This method checks is the tag exists or not from a data object.

		*Arguments:*
			* ``data_obj`` -data object to be checked for tag association existance.

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``bool`` -indicating whether tag association exists or not.
		"""

		tag_exists = False

		if isinstance( data_obj, ctg.ae2.core.data.Tag_Association_Item ):
			tag_exists = self.get_item_by_tag_name( data_obj.get_tag_name( ) )
		elif isinstance( data_obj, ctg.ae2.core.data.State_Tag_Item ):
			tag_exists = self.get_item_by_tag_name( data_obj.get_name( ) )
		elif isinstance( data_obj, ctg.ae2.core.data.Action_Tag_Item ):
			tag_exists = self.get_item_by_tag_name( data_obj.get_name( ) )

		if tag_exists and len( tag_exists ) > 0:
			return True
		else:
			return False


	def create_new_tag_by_obj( self, data_obj = None, data = None, undo_able_modify = False ):
		"""
		This method creates a ne tag association object.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``data_obj``
			* ``data``

		*Returns:*
			* ``new tag association`` -new tag association object.
		"""
		doc = AnimationEditor.get_active_document()

		new_tag = AnimationEditor.ae_tag_association( )

		#try:
		#new_tag = AnimationEditor.ae_tag_association( )
		#except:
			#return None

		if data:
			# call unbound functions with their associated values in the dict
			for key, value in data.iteritems():
				if value is None:
					result = getattr( new_tag, key )( )
				else:
					result = getattr( new_tag, key )( value )

		elif isinstance( data_obj, ctg.ae2.core.data.Tag_Association_Item ):
			if data_obj.is_state( ):
				new_tag.set_type_state( )
				new_tag.set_tag_name( 'TEMP_STATE_TAG' )
			else:
				new_tag.set_type_action( )
				new_tag.set_tag_name( 'TEMP_ACTION_TAG' )

			new_tag.set_tag_name( data_obj.get_tag_name( ) )
			new_tag.set_clip_name( data_obj.get_clip_name( ) )

		elif isinstance( data_obj, ctg.ae2.core.data.State_Tag_Item ):
			new_tag.set_type_state( )
			new_tag.set_tag_name( data_obj.get_name( ) )
			new_tag.set_clip_name( 'MISSING_CLIP' )

		elif isinstance( data_obj, ctg.ae2.core.data.Action_Tag_Item ):
			new_tag.set_type_action( )
			new_tag.set_tag_name( data_obj.get_name( ) )
			new_tag.set_clip_name( 'MISSING_CLIP' )

		elif isinstance( data_obj, ctg.ae2.core.data.Clip_Item ):
			if doc.active_tag_type == ctg.ae2.ui.const.NODE_TYPE_TAG_STATE:
				new_tag.set_type_state( )
				new_tag.set_tag_name( 'TEMP_STATE_TAG' )
			elif doc.active_tag_type == ctg.ae2.ui.const.NODE_TYPE_TAG_ACTION:
				new_tag.set_type_action( )
				new_tag.set_tag_name( 'TEMP_ACTION_TAG' )
			new_tag.set_clip_name( data_obj.get_name( ) )

		else:
			if doc.active_tag_type == ctg.ae2.ui.const.NODE_TYPE_TAG_STATE:
				new_tag.set_type_state( )
				new_tag.set_tag_name( 'TEMP_STATE_TAG' )
			elif doc.active_tag_type == ctg.ae2.ui.const.NODE_TYPE_TAG_ACTION:
				new_tag.set_type_action( )
				new_tag.set_tag_name( 'TEMP_ACTION_TAG' )

			new_tag.set_clip_name( 'MISSING_CLIP' )

		# set the new uid
		new_uid = doc.get_new_uid( )

		new_tag.set_uid( new_uid )
		self.change_name_on_tag_existance( new_tag )
		if undo_able_modify:
			doc.undoable_create_anim_tag_association( doc.active_set, doc.active_group, new_tag )

		return new_tag


	def clone_tags( self, tag_objs ):
		doc = AnimationEditor.get_active_document( )
		tags_cloned = False

		tags_uids = [ ]

		for tag in tag_objs:
			new_tag = AnimationEditor.ae_tag_association( )
			new_tag_uid = doc.get_new_uid( )
			new_tag.set_uid( new_tag_uid )

			if new_tag_uid not in tags_uids:
				tags_uids.append( new_tag_uid )


			if tag.is_state():
				new_tag.set_type_state( )
			elif tag.is_action( ):
				new_tag.set_type_action( )

			new_tag.set_tag_name( tag.get_tag_name( ) )
			new_tag.set_clip_name( tag.get_clip_name( ) )
			new_tag.set_category( tag.get_category( ) )
			new_tag.set_reverse_flag( tag.get_reverse_flag( ) )
			new_tag.set_mirrored_flag( tag.get_mirrored_flag( ) )
			new_tag.set_speed_multiplier( tag.get_speed_multiplier( ) )

			self.change_name_on_tag_existance( new_tag )
			tags_cloned = doc.undoable_create_anim_tag_association( doc.active_set, doc.active_group, new_tag )

		cloned_tags = [ ]
		if tags_cloned:
			self.update_collection( clear_items= True )
			for uid in tags_uids:
				tag_item = self.get_item_by_uid( uid )
				if tag_item:
					cloned_tags.extend( tag_item )

		return tags_cloned, tags_uids, cloned_tags


	def create_new_tag( self, tag_type, clip_name=None, category_name = 'Default', is_clip=True ):
		doc = AnimationEditor.get_active_document( )
		tag_clip_name = 'MISSING_CLIP'
		if clip_name not in [ None, '' ] and is_clip:
			tag_clip_name = clip_name

		new_tag = AnimationEditor.ae_tag_association( )
		new_tag.set_uid( doc.get_new_uid( ) )
		new_tag.set_clip_name( tag_clip_name )
		new_tag.set_category( category_name )

		if tag_type == ctg.ae2.ui.const.NODE_TYPE_TAG_STATE:
			new_tag.set_type_state( )

			tag_name = 'TEMP_STATE_TAG'
			if clip_name not in [ None, '' ] and not is_clip:
				tag_name = clip_name

			new_tag.set_tag_name( tag_name )
		elif tag_type == ctg.ae2.ui.const.NODE_TYPE_TAG_ACTION:
			new_tag.set_type_action( )

			tag_name = 'TEMP_ACTION_TAG'
			if clip_name not in [ None, '' ] and not is_clip:
				tag_name = clip_name

			new_tag.set_tag_name( tag_name )

		self.change_name_on_tag_existance( new_tag )
		tag_created = doc.undoable_create_anim_tag_association( doc.active_set, doc.active_group, new_tag )

		tag_item = None
		if tag_created:
			self.update_collection( clear_items= True )
			tag_item = self.get_item_by_uid( new_tag.get_uid( ) )

			if not tag_item:
				tag_item = [ ctg.ae2.core.data.Tag_Association_Item( doc, new_tag ) ]

		doc.tag_association_collection.update_collection( )

		return [ new_tag, tag_created, tag_item ]


	def paste_tags( self, data_list = None, category = None, update_collection = True ):

		tag_created = False
		tag_uids = [ ]
		if data_list:
			for data in data_list:
				doc = AnimationEditor.get_active_document()
				new_tag = AnimationEditor.ae_tag_association( )
				new_uid = doc.get_new_uid( )
				new_tag.set_uid( new_uid )

				if new_uid not in tag_uids:
					tag_uids.append( new_uid )

				for key, value in data.iteritems():
					if value == ctg.ae2.ui.const.NODE_TYPE_TAG_STATE:
						new_tag.set_type_state( )
					elif value == ctg.ae2.ui.const.NODE_TYPE_TAG_ACTION:
						new_tag.set_type_action( )
					elif key != 'set_uid' and key != 'set_tag_modifiers':
						result = getattr( new_tag, key )( value )

				if category != None:
					new_tag.set_category( str( category ) )

				self.change_name_on_tag_existance( new_tag )
				tag_created = doc.undoable_create_anim_tag_association( doc.active_set, doc.active_group, new_tag )

		tag_items = [ ]
		if tag_created and update_collection:
			self.update_collection( )
			tag_items = self.get_items_from_uids( tag_uids )

		return tag_created, tag_uids, tag_items


	def change_name_on_tag_existance( self, tag ):
		name_change = False

		self.update_collection( )

		doc = AnimationEditor.get_active_document( )

		# Make sure the name doesnt exist as a tag already
		tag_name = tag.get_tag_name( )
		tag_exists = False

		# Check if the name exists on a group level
		if doc:
			current_set = doc.set_collection.get_item_by_name( doc.active_set )
			if current_set:
				for group in current_set.get_groups( ):
					for existing_tag in group.get_tag_associations( ):
						if tag_name == existing_tag.get_tag_name( ):
							tag_exists = True

		# Increment the tag name if it already exists
		while tag_exists:
			tag_name = ctg.ae2.core.ae_common_operations.increment_string( tag_name )
			tag_exists = bool( self.get_item_by_tag_name( tag_name ) )

		# If we have a tag name set it to the new tag
		if tag_name:
			tag.set_tag_name( tag_name )
			name_change = True

		return name_change


	def create( self, data_obj, data = None ):
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		create_tag = False
		#tag_exists = False
		#tag_name = None

		# Create a new tag association object
		new_tag = self.create_new_tag( data_obj, data = data)[0]

		self.change_name_on_tag_existance( new_tag )

		create_tag = doc.undoable_create_anim_tag_association( doc.active_set, doc.active_group, new_tag )
		if create_tag:
			self.update_collection( )

			# get the newly created tag association item
			print( 'New Tag UID: {0}'.format( new_tag.get_uid( ) ) )
			new_tag_items = self.get_item_by_uid( new_tag.get_uid( ) )
			if len( new_tag_items ) > 0:
				doc.selection_manager.recent_sel_tag_associations = new_tag_items

		else:
			print('A tag already exists with the same tag name: {0}'.format( data_obj.get_name( ) ) )

		return create_tag


	def modify( self, data_obj ):
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		did_modify = False
		tag_name = None
		tag_exists = False

		new_tag = self.create_new_tag_by_obj( data_obj )

		if doc.tag_association_tag_value:
			new_tag.set_tag_name( doc.tag_association_tag_value )
			doc.tag_association_tag_value = None

		elif doc.tag_association_clip_value:
			new_tag.set_clip_name( doc.tag_association_clip_value )
			doc.tag_association_clip_value = None

		if new_tag:
			tag_name = new_tag.get_tag_name( )
			item_tags = self.get_item_by_tag_name( tag_name, not_uid = data_obj.get_uid( ) )
			if item_tags:
				tag_exists = True

				# Increment the tag name if it already exists
				while tag_exists:
					tag_name = ctg.ae2.core.ae_common_operations.increment_string( tag_name )
					tag_exists = bool( self.get_item_by_tag_name( tag_name, not_uid = data_obj.get_uid( ) ) )


			new_tag.set_tag_name( tag_name )
			# setting the new tag uid to the existing tag uid
			new_tag.set_uid( data_obj.get_uid( ) )
			did_modify = doc.undoable_modify_anim_tag_association( data_obj.set_name, data_obj.group_name, data_obj.get_uid( ), new_tag )
			if did_modify:
				self.update_collection( )

				# get the newly created tag association item
				print( 'Modified Tag UID: {0}  New Tag UID: {1}'.format( data_obj.get_uid( ), new_tag.get_uid( ) ) )
				new_tag_items = self.get_item_by_uid( new_tag.get_uid( ) )
				if len( new_tag_items ) > 0:
					doc.selection_manager.recent_sel_tag_associations = new_tag_items


		return did_modify


	def delete( self, data_obj ):
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		did_delete = False
		tags = None

		# remove a tag item or locate tags containing the data_obj name
		if isinstance( data_obj, ctg.ae2.core.data.Tag_Association_Item ):
			did_delete = doc.undoable_delete_anim_tag_association( data_obj.set_name, data_obj.group_name, data_obj.get_uid( ) )
			if did_delete:
				self.update_collection( )
				return did_delete

		elif isinstance( data_obj, ctg.ae2.core.data.State_Tag_Item ):
			tags = self.get_item_by_tag_name( data_obj.get_name( ) )

		elif isinstance( data_obj, ctg.ae2.core.data.Action_Tag_Item ):
			tags = self.get_item_by_tag_name( data_obj.get_name( ) )

		elif isinstance( data_obj, ctg.ae2.core.data.Clip_Item ):
			tags = self.get_item_by_clip_name( data_obj.get_name( ) )

		if tags:
			for tag in tags:
				did_delete = doc.undoable_delete_anim_tag_association( tag.set_name, tag.group_name, tag.get_uid( ) )

			doc.selection_manager.recent_sel_tag_associations = tags
			self.update_collection( )

		return did_delete



#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
## Node Graph Data ##
#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

# Individual Node Graph data object
class Node_Graph_Tree_Item( object ):
	"""
	Class for the Individual Node Graph Tree data object

	*Arguments:*
		* ``doc``  -Active animation document
		* ``name`` -name of the node graph object
		* ``handle`` - unique identifier for a node graph hierarchy item
		* ``data_obj`` - actual data object for the node graph tree item

	*Keyword Arguments:*
		* ``is_node_graph`` - bool whether this is an actual node graph or dependency
		* ``node_children`` - list of node_graph dependency node_graph references
		* ``dependencies`` - list of node_graph dependency references
	"""

	def __init__( self, doc, name, data_obj, is_node_graph = False, virtual = False ):
		self.doc = doc
		self.name = name
		self.is_root = False
		self.data_obj = data_obj
		self.is_node_graph = is_node_graph
		self.virtual = virtual # TODO Maybe use the raw object to determine this.  It would have to store it... so maybe not

		self.node_graph = None
		self.dependency_graphs_collection	= None
		self.dependency_items_collection		= None


	def get_name( self ):
		"""
		This method gets and returns State_Machine_Item name.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``name`` -State_Machine_Item name
		"""
		return self.data_obj.get_name( )


	def get_data_obj( self ):
		"""
		As this item is just a container for the actual data obj we need to get the actual data_obj

		*Arguments:*
			* ``Argument`` Enter a description for the argument here.

		*Keyword Arguments:*
			* ``Argument`` Enter a description for the keyword argument here.

		*Returns:*
			* ``Value`` If any, enter a description for the return value here.
		"""

		return self.data_obj


	def set_data_obj( self, data_obj ):
		"""
		Set the actual data_obj for this item
		When renaming occurs to keep updating the node graph tree at a minimum I want to reuse existing items

		*Arguments:*
			* ``Argument`` Enter a description for the argument here.

		*Keyword Arguments:*
			* ``Argument`` Enter a description for the keyword argument here.

		*Returns:*
			* ``Value`` If any, enter a description for the return value here.
		"""

		self.data_obj = data_obj


	def get_node_type( self ):
		"""
		This method gets and returns Node_Graph_Item node type constant.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``node type constant`` -Node type constant.
		"""

		return ctg.ae2.ui.const.NODE_TYPE_NODE_GRAPH_TREE_ITEM


	def get_node_graph( self ):
		"""
		Get the node graph object for the node graph name.
		This is only necessary if we intend to get the dependencies.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``node_graph`` The actual node graph object for this item
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		self.node_graph = doc.get_node_graph( self.get_name( ) )
		return self.node_graph


	def get_dependency_items( self ):
		"""
		This method gets and returns a Node_Graph_Dependency collection.
		The child dependencies ( clips, tags, control filters, control parameters )

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``node type constant`` -Node type constant.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		if not self.node_graph:
			self.node_graph = self.get_node_graph( )

		if self.node_graph:
			self.dependency_items_collection = None
			self.dependency_items_collection = Node_Graph_Dependency_Items_Collection( doc, self.node_graph )


	def get_dependency_graphs( self ):
		"""
		This method gets and returns a Node_Graph_Dependencts collection.
		The child node graphs

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``node type constant`` -Node type constant.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		if not self.node_graph:
			self.node_graph = self.get_node_graph( )

		if self.node_graph:
			self.dependency_graphs_collection = None
			self.dependency_graphs_collection = Node_Graph_Dependency_Graphs_Collection( doc, self.node_graph )


	def update_all_dependencies( self ):
		self.node_graph = self.get_node_graph( )
		self.dependency_items_collection = None
		self.get_dependency_items( )

		self.dependency_graph_collection = None
		self.get_dependency_graphs( )



# Node Graph data collection
class Node_Graph_Tree_Collection( Enumeration_Collection ):
	"""
	Node Graph collections object

	*Arguments:*
		* ``doc`` -Active animation document.

	*Keyword Arguments:*
		* ``none``
	"""
	# def __init__( self, doc ):
	# 	self.doc = doc
	# 	self._item_dict = { }
	# 	Collection.__init__( self, doc )

	def _get_root_node_graphs( self ):
		"""
		Construct and return the node graph heirarchy.

		*Arguments:*
			* ``Argument`` Enter a description for the argument here.

		*Keyword Arguments:*
			* ``Argument`` Enter a description for the keyword argument here.

		*Returns:*
			* ``Value`` If any, enter a description for the return value here.
		"""
		doc = AnimationEditor.get_active_document( )
		if not doc:
			return

		root_node_graphs = [ ]

		# get all the node graph names and construct the hierarchy
		for node_graph_name in doc.get_node_graph_names( ):

			# check for node graph dependents( parents )
			dependents = doc.get_node_graph_dependents( ctg.ae2.ui.const.NODE_GRAPH_DEPENDENCIES[ "type" ], node_graph_name )
			if len( dependents ) == 0:
				# set this node graph as a root node graph
				root_node_graphs.append( node_graph_name )

		return root_node_graphs


	# def _gather_virtual_infos( self ):
	#
	# 	items = [ item for item in self._gather_item_infos( ) if hasattr( item, vlib.data_enum.Enumerated_Data_Provider_Virtual.VIRTUAL_TAG ) ]
	# 	return items


	def _gather_item_names( self ):
		"""
		Gathers and returns a set of node graph names from the active animation document.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``set`` -Containing animation state machine names.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		items = super( Node_Graph_Tree_Collection, self )._gather_item_names( )
		root_graphs = self._get_root_node_graphs( )

		return set( items )


	def _create_item( self, name, virtual = False ):
		"""
		This method returns an existing State_Machine_Item or Blend_Tree_Item with a specified name.

		*Arguments:*
			* ``name`` -name for the state machine item.

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``State_Machine_Item`` -Newly created State_Machine_Item.
			* ``Blend_Tree_Item`` -Newly created Blend_Tree_Item.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		new_item = None

		# Nathan Turner : 10/9/2015
		# NOTE : Because this Collection is based on a newly created Provider
		# we should assume the provider is giving us accurate data so another
		# check for if the 'name' is a real thing is invalid.  However the code
		# is going to stay in here in such a way that we can see those items
		# that have not had their display name edited to be the true 'user name'
		# that code for checking will be below this block comment.

		# NAT: 10/9/2015 a helpful warning for users that the display still needs to be altered
		# to match the User name.  See Nathan Turner for more information.
		if not doc.blend_tree_collection.get_item_by_name( name ) and not doc.state_machine_collection.get_item_by_name( name ):
			message = 'new_item, based on "{0}", should be either a Blend Tree or State Machine.  Please inspect the provider for SM and BT for'.format( name )
			ctg.log.warn( message )
			print( message )

		state = doc.state_machine_collection.get_item_by_name( name )
		blend = doc.blend_tree_collection.get_item_by_name( name )
		if state:
			node_found = state
		elif blend:
			node_found = blend
		else:
			raise EnvironmentError, 'name {0} was not found in either Statemachine or BlendTree Collection'.format( name )

		tag = vlib.data_enum.Enumerated_Data_Provider_Virtual.VIRTUAL_TAG
		if hasattr( node_found, tag ) and getattr( node_found, tag ):
			node = Node_Graph_Tree_Item( doc, name, node_found, is_node_graph = True, virtual = True )
		else:
			node = Node_Graph_Tree_Item( doc, name, node_found, is_node_graph = True )
		return node


	def get_node_type( self ):
		"""
		This method gets and returns Node_Graph_Tree_Item node type constant.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``node type constant`` -Node type constant.
		"""

		return ctg.ae2.ui.const.NODE_TYPE_NODE_GRAPH_TREE_ITEM



#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
## Node Graph Dependency ##
#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

# Individual Node Graph Dependency data object
class Node_Graph_Dependency_Item( object ):
	"""
	Class for the Individual node graph dependency data object

	*Arguments:*
		* ``doc``  -Active animation document
		* ``name`` -name of the animation state machine object

	*Keyword Arguments:*
		* ``none``
	"""

	def __init__( self, doc, name ):
		self.doc = doc
		self.name = name


	def get_name( self ):
		"""
		This method gets and returns State_Machine_Item name.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``name`` -State_Machine_Item name
		"""

		return self.name


	def get_node_type( self ):
		"""
		This method gets and returns Node_Graph_Item node type constant.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``node type constant`` -Node type constant.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		if doc.is_clip( self.name ):
			return ctg.ae2.ui.const.NODE_TYPE_ANIM_CLIP
		else:
			if doc.anim_tag_is_state( self.name ):
				return ctg.ae2.ui.const.NODE_TYPE_ANIM_STATE

			elif doc.anim_tag_is_action( self.name ):
				return ctg.ae2.ui.const.NODE_TYPE_ANIM_STATE



# Node Graph data collection
class Node_Graph_Dependency_Items_Collection( Collection ):
	"""
	Node Graph collections object

	*Arguments:*
		* ``doc`` -Active animation document.

	*Keyword Arguments:*
		* ``none``
	"""

	def __init__( self, doc, node_graph ):
		self.doc = doc
		self._item_dict = { }
		self._node_graph = node_graph

		Collection.__init__( self, doc )



	def _gather_item_names( self ):
		"""
		Gathers and returns a set of node graph dependency names from the active animation document.
		Clips, Tags, Control Filters, Control Parameters

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``set`` -Containing animation state machine names.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		item_names = [ ]
		for dependency in ctg.ae2.ui.const.DEPENDENCY_TYPES:
			dependency_names = self._node_graph.get_dependencies( dependency[ 'type' ] )
			if dependency_names:
				item_names.extend( list( dependency_names ) )

		return set( item_names )


	def _create_item( self, name ):
		"""
		This method returns an existing State_Machine_Item or Blend_Tree_Item with a specified name.

		*Arguments:*
			* ``name`` -name for the state machine item.

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``State_Machine_Item`` -Newly created State_Machine_Item.
			* ``Blend_Tree_Item`` -Newly created Blend_Tree_Item.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		data_obj = None

		# Anim Clip
		if doc.is_clip( name ):
			valid_obj = doc.clip_collection.get_item_by_name( name )
			if valid_obj:
				data_obj = Node_Graph_Tree_Item( doc, valid_obj.get_name, data_obj = valid_obj )

		# State Tag
		elif doc.anim_tag_is_state( name ):
			valid_obj = doc.state_tag_collection.get_item_by_name( name )
			if valid_obj:
				data_obj = Node_Graph_Tree_Item( doc, valid_obj.get_name, data_obj = valid_obj )

		# Action Tag
		elif doc.anim_tag_is_action( name ):
			valid_obj = doc.action_tag_collection.get_item_by_name( name )
			if valid_obj:
				data_obj = Node_Graph_Tree_Item( doc, valid_obj.get_name, data_obj = valid_obj )

		# Control Filter
		elif doc.control_is_filter( name ):
			valid_obj = doc.control_filter_collection.get_item_by_name( name )
			if valid_obj:
				data_obj = Node_Graph_Tree_Item( doc, valid_obj.get_name, data_obj = valid_obj )

		# Control Parameter
		elif doc.control_is_parameter( name ):
			valid_obj = doc.control_parameter_collection.get_item_by_name( name )
			if valid_obj:
				data_obj = Node_Graph_Tree_Item( doc, valid_obj.get_name, data_obj = valid_obj )

		# If a valid data object is found use that or create a dependency item
		if data_obj:
			return data_obj
		else:
			message = '"{0}" was not found to be a real thing in _create_item'.format( name )
			print( message )
			ctg.log.warning( message )
			return None



	def get_node_type( self ):
		"""
		This method gets and returns State_Machine_Item node type constant.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``node type constant`` -Node type constant.
		"""

		return ctg.ae2.ui.const.NODE_TYPE_NODE_GRAPH_TREE_ITEM



class Node_Graph_Dependency_Graphs_Collection( Collection ):

	def __init__( self, doc, node_graph ):
		self.doc = doc
		self._item_dict = { }
		self._node_graph = node_graph

		Collection.__init__( self, doc )


	def _gather_item_names( self ):
		"""
		Gathers and returns a set of node graph names from the active animation document.
		Child node graph dependencies

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``set`` -Containing animation state machine names.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		item_names = [ ]
		node_dependencies = self._node_graph.get_dependencies( ctg.ae2.ui.const.NODE_GRAPH_DEPENDENCIES[ "type" ] )
		if node_dependencies:
			node_list = list( node_dependencies )
			item_names = list( set( node_list ) )

		return set( item_names )


	def _create_item( self, name ):
		"""
		This method returns an existing State_Machine_Item or Blend_Tree_Item with a specified name.

		*Arguments:*
			* ``name`` -name for the state machine item.

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``State_Machine_Item`` -Newly created State_Machine_Item.
			* ``Blend_Tree_Item`` -Newly created Blend_Tree_Item.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		# State Machine
		if doc.is_state_machine( name ):
			valid_obj = doc.state_machine_collection.get_item_by_name( name )
			if valid_obj:
				return Node_Graph_Tree_Item( doc, name, valid_obj, is_node_graph = True )

		# Blend Tree
		elif doc.is_blend_tree( name ):
			valid_obj = doc.blend_tree_collection.get_item_by_name( name )
			if valid_obj:
				return Node_Graph_Tree_Item( doc, name, valid_obj, is_node_graph = True)

		return None


	def get_node_type( self ):
		"""
		This method gets and returns State_Machine_Item node type constant.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``node type constant`` -Node type constant.
		"""

		return ctg.ae2.ui.const.NODE_TYPE_NODE_GRAPH_TREE_ITEM



#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
## Search Data ##
#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# Individual Search data object
class Search_Item( object ):
	"""
	Class for the Individual search data object
	Handles a couple data types
	Catalog - Tag_Association_Item
	Network - Clip_Item, Action_Item, State_Item

	*Arguments:*
		* ``doc``  -Active animation document
		* ``name`` -name of the node graph dependency object
		* ``node_graph`` -node graph object
		* ``data_obj`` - The listerlib data_obj for this item

	*Keyword Arguments:*
		* ``is_clip`` -is the dependency object a clip
		* ``is_tag_action`` - is the dependency object an action tag
		* ``is_tag_state`` - is the dependency object a state tag
	"""

	def __init__( self, doc, data_obj, name = None, node_graph_name = None, is_catalog = False, is_network = False, is_clip = False, is_tag_action = False, is_tag_state = False ):
		self.doc = doc
		self.name = name
		self.data_obj = data_obj
		self.nodegraph = None
		self.nodegraph_name = node_graph_name
		self.is_catalog = is_catalog
		self.is_network = is_network
		self.is_clip = is_clip
		self.is_tag_action = is_tag_action
		self.is_tag_state	= is_tag_state


	def get_name( self ):
		"""
		This method gets and returns Search_Network_Item name.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``name`` -Search_Network_Item name.
		"""

		return self.name


	def get_data_obj( self ):
		"""
		As this item is just a container for the actual data obj we need to get the actual data_obj

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``data_obj`` ListerLib data object

		*Examples:* ::

			Enter code examples here. (optional field)

		*Todo:*
			* Enter thing to do. (optional field)
		"""
		return self.data_obj


	def get_nodegraph( self ):
		"""
		Get the node graph for this Search_Network_Item

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``nodegraph`` NodeGraph object
		"""
		doc = AnimationEditor.get_active_document( )
		if not doc:
			return

		if not self.nodegraph:
			if self.nodegraph_name:
				if doc.is_state_machine( self.nodegraph_name ):
					data_obj = doc.state_machine_collection.get_item_by_name( self.nodegraph_name )
					if data_obj:
						node_graph = data_obj

				# Blend Tree
				elif doc.is_blend_tree( self.nodegraph_name ):
					data_obj = doc.blend_tree_collection.get_item_by_name( self.nodegraph_name )
					if data_obj:
						node_graph = data_obj

				if node_graph:
					self.nodegraph = node_graph

		return self.nodegraph


	def get_nodegraph_name( self ):
		"""
		Get the node graph name for this Search_Network_Item

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``nodegraph_name`` NodeGraph string name
		"""
		return self.nodegraph_name


	def get_data_type( self ):
		"""
		Get the network dependency type
		Clip/Tag

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``String`` Name of the dependency type
		"""
		if self.is_clip:
			return ctg.ae2.ui.const.NODE_TYPE_ANIM_CLIP
		elif self.is_tag_action:
			return ctg.ae2.ui.const.NODE_TYPE_TAG_ACTION
		elif self.is_tag_state:
			return ctg.ae2.ui.const.NODE_TYPE_TAG_STATE


	def get_node_type( self ):
		"""
		Item is either a Catalog or Network Search Type

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``search_type`` String of the search item type
		"""
		if self.is_catalog:
			return ctg.ae2.ui.const.NODE_TYPE_SEARCH_CATALOG
		else:
			return ctg.ae2.ui.const.NODE_TYPE_SEARCH_NETWORK



# Search data collection
class Search_Catalog_Collection( Collection ):
	"""
	Search Catalog collections object

	*Arguments:*
		* ``doc`` -Active animation document.

	*Keyword Arguments:*
		* ``none``
	"""
	def __init__( self, doc ):
		self.doc = doc
		self._item_dict = { }
		self.set_group_tags_map = { }
		Collection.__init__( self, doc )


	def _gather_item_names( self ):
		"""
		Gathers and returns a set of search names from the active animation document.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``set`` -Containing tag association objects.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		all_tag_associations = [ ]

		# get all tag_association objects
		for anim_set in doc.get_anim_set_names( ):
			for anim_group in doc.get_anim_group_names( ):
				tag_associations = doc.get_anim_set_tag_associations( anim_set, anim_group )
				if tag_associations:
					# set up the set/group mapping for each tag association object
					for tag in tag_associations:
						self.set_group_tags_map[ tag ] = [ anim_set, anim_group ]

					all_tag_associations.extend( tag_associations )

		return set( all_tag_associations )


	def _create_item( self, tag_obj ):
		"""
		This method creates Search_Catalog_Item with a specified name.

		*Arguments:*
			* ``tag_obj`` - AE Tag Association Object

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``Tag_Association_Item`` - Newly created Tag_Association_Item.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		data_obj = Tag_Association_Item( doc, tag_obj, set_name = self.set_group_tags_map[ tag_obj ][0], group_name = self.set_group_tags_map[ tag_obj ][1] )
		return Search_Item( doc, data_obj, name = tag_obj.get_tag_name( ), is_catalog = True )


	def get_node_type( self ):
		"""
		This method gets and returns Search_Catalog_Item node type constant.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``node type constant`` -Node type constant.
		"""

		return ctg.ae2.ui.const.NODE_TYPE_SEARCH_CATALOG



# Node Graph data collection
class Search_Network_Collection( Collection ):
	"""
	Search Network collections object

	*Arguments:*
		* ``doc`` -Active animation document.

	*Keyword Arguments:*
		* ``none``
	"""

	def __init__( self, doc ):
		self.doc = doc
		Collection.__init__( self, doc )


	def _gather_item_names( self ):
		"""
		Gathers and returns a set of node graph dependency names from the active animation document.
		Clips, Tags, Control Filters, Control Parameters

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``set`` -Containing animation state machine names.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		item_names = [ ]
		for node_graph_name in doc.get_node_graph_names( ):
			node_graph = doc.get_node_graph( node_graph_name )
			if node_graph:
				dependency_list = [ ]
				# node graph dependencies
				clip_deps = node_graph.get_dependencies( ctg.ae2.ui.const.CLIP_DEPENDENCIES[ 'type' ] )
				if clip_deps:
					for dep in clip_deps:
						item_names.append( node_graph_name + ':clip:' + dep )

				tag_deps  = node_graph.get_dependencies( ctg.ae2.ui.const.TAG_DEPENDENCIES[ 'type' ] )
				if tag_deps:
					for dep in tag_deps:
						item_names.append( node_graph_name + ':tag:' + dep )

		return set( item_names )


	def _create_item( self, full_name ):
		"""
		This method returns an existing State_Machine_Item or Blend_Tree_Item with a specified name.

		*Arguments:*
			* ``full_name`` -name for the state machine item.

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``State_Machine_Item`` -Newly created State_Machine_Item.
			* ``Blend_Tree_Item`` -Newly created Blend_Tree_Item.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		data_obj = None

		# split the incoming name into usable pieces
		node_graph_name, dep_type, name = full_name.split( ':' )

		# Anim Clip
		if doc.is_clip( name ):
			valid_obj = doc.clip_collection.get_item_by_name( name )
			if valid_obj:
				data_obj = Search_Item( doc, valid_obj, name = name, node_graph_name = node_graph_name, is_network = True, is_clip = True )

		# State Tag
		elif doc.anim_tag_is_state( name ):
			valid_obj = doc.state_tag_collection.get_item_by_name( name )
			if valid_obj:
				data_obj = Search_Item( doc, valid_obj, name = name, node_graph_name = node_graph_name, is_network = True, is_tag_state = True )

		# Action Tag
		elif doc.anim_tag_is_action( name ):
			valid_obj = doc.action_tag_collection.get_item_by_name( name )
			if valid_obj:
				data_obj = Search_Item( doc, valid_obj, name = name, node_graph_name = node_graph_name, is_network = True, is_tag_action = True )

		# If a valid data object is found use that or create a dependency item
		if data_obj:
			return data_obj
		else:
			print( '{0} did not fall into state, action, or clip'.format( full_name ) )
			return None


	def get_node_type( self ):
		"""
		This method gets and returns State_Machine_Item node type constant.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``node type constant`` -Node type constant.
		"""

		return ctg.ae2.ui.const.NODE_TYPE_SEARCH_NETWORK



#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
## Animation Named Value Data ##
#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# Individual Named value data object
class Anim_Named_Value_Item( object ):
	"""
	Class for the Individual named value data object

	*Arguments:*
		* ``doc``  -Active animation document
		* ``named_value_obj``  -named value object

	*Keyword Arguments:*
		* ``set_name`` - Name of the associated animation set
		* ``group_name`` - Name of the associated animation group
	"""

	def __init__( self, doc, named_value_obj, set_name = None, group_name = None ):
		self.doc = doc
		self.name 				= named_value_obj.get_name( )
		self.named_value_obj = named_value_obj
		self.set_name 			= set_name
		self.group_name 		= group_name



	def get_name( self ):
		"""
		This method gets and returns named value object name.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``named value name`` -named value object object name.
		"""
		self.name = self.named_value_obj.get_name( )
		return self.name


	def get_node_type( self ):
		"""
		This method gets and returns Anim_Named_Value_Item node type constant.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``node type constant`` -Node type constant.
		"""

		return ctg.ae2.ui.const.NODE_TYPE_ANIM_NAMED_VALUE


	def get_uid( self ):
		"""
		This method gets named value object uid.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``clip name`` -animation clip name
		"""

		return self.named_value_obj.get_uid( )


	def get_named_obj_value( self, prop_id_string, named_value_obj ):
		"""
		This method gets and returns a value from specified data object.

		*Arguments:*
			* ``prop_id_string`` -property string name.
			* ``named_value_obj`` -named_value_obj to get data from.

		*Keyword Arguments:*
			* <none>

		*Returns:*
			* ``value`` -named_value_obj value based on the prop_id_string value.
		"""
		value = None
		if not named_value_obj:
			return value

		if prop_id_string == 'uid':
			value = named_value_obj.get_uid( )
		elif prop_id_string == 'named_value':
			value = named_value_obj.get_value( )
		elif prop_id_string == 'name':
			value = named_value_obj.get_name( )

		return value


	def get_set_name( self ):
		return self.set_name

	def get_group_name( self ):
		return self.group_name

	def get_value( self ):
		return self.named_value_obj.get_value( )


	def get_name_value_obj( self ):
		"""
		This method and returns tag assciation object.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``tag`` -tag association object.
		"""

		return self.named_value_obj



	def set_value( self, prop_id_string, value, named_value_obj ):
		"""
		This method sets up initial value for the control.

		*Arguments:*
			* ``prop_id_string`` -property id string
			* ``value`` 			-value to be set on named_value_obj for the prop_id_string.
			* ``named_value_obj``-named_value_obj on which to set the value for the prop_id_string.


		*Keyword Arguments:*
			* <none>

		*Returns:*
			* ``boolean`` 			-a boolean indicating whether the operation was successiful or not.
		"""
		success = False
		if named_value_obj:
			#make sure the prop_id_string is in lower case

			prop_id_string = prop_id_string.lower()
			if prop_id_string == 'uid':
				named_value_obj.set_uid( int(value) )
			elif prop_id_string  == 'named_value':
				named_value_obj.set_value( float(value) )
			elif prop_id_string == 'name':
				named_value_obj.set_named_value_name( value )


			success = self.update_named_value( named_value_obj )

		return success


	def set_value_by_prop_id_string( self, prop_id_string, value ):

		success = False
		prop_id_string = prop_id_string.lower()
		named_value_obj = self.get_name_value_obj( )
		if prop_id_string == 'uid':
			named_value_obj.set_uid( int(value) )
		elif prop_id_string  == 'named_value':
			named_value_obj.set_value( float(value) )
		elif prop_id_string == 'name':
			named_value_obj.set_name( value )


		success = self.update_named_value( named_value_obj )

		return success



	def set_named_value_name( self, name ):
		self.named_value_obj.set_name( str( name ) )
		success = self.update_named_value( self.named_value_obj )

		return success


	def set_named_value( self, value ):
		self.named_value_obj.set_value( float( value )  )
		success = self.update_named_value( self.named_value_obj )

		return success



	def set_uid( self, uid ):
		"""
		This method sets uid for named value object.

		*Arguments:*
			* ``uid`` -uid to be set on named value.

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``bool`` -indicating the operation was successful or not.

		"""
		success = False
		doc = AnimationEditor.get_active_document()
		if not doc:
			return False

		if self.named_value_obj:
			self.named_value_obj.set_uid( int( uid ) )
			success = self.update_named_value( self.named_value_obj )
			if success:
				doc.named_values_collection.update_collection( )

		return success


	def update_named_value( self, named_value_obj ):
		"""
		This method updates named value.

		*Arguments:*
			* ``named_value_obj`` -named_value_obj association to update.

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``bool`` -indicating operation was successful or not.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc or not named_value_obj:
			return

		return doc.undoable_modify_anim_named_value( self.get_set_name( ), self.get_group_name( ), named_value_obj.get_uid( ), named_value_obj )


	def delete( self ):
		"""
		This method deletes named value object.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``bool`` -Indicating whether the operation was successful or not.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		did_delete = doc.undoable_delete_anim_named_value( self.set_name, self.group_name, self.get_uid( ) )
		if did_delete:
			doc.named_values_collection.update_collection( )

		return did_delete


	def validate_name( self, name ):
		"""
		This Method checks the name for invalid characters, also checks if
		the name exists in named value collection.

		*Arguments:*
			* ``name`` -name to be validated

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``bool`` -True indicates the name is valid, and False the name is not valid.

		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		if name == '':
			return False

		valid_name = doc.named_values_collection.validate_name_pattern( name )
		if valid_name:
			exists = doc.named_values_collection.check_name_existance( name )
			if not exists:
				return True
			else:
				if self.get_name().lower() != name.lower():
					return False
				else:
					return True
		else:
			return False


	def get_unique_name( self, name ):
		"""
		Checks if the name exists in sets collection, if the name exists adds an
		index and return it as new name, if the name does not exists in the
		collection, return the name.

		*Arguments:*
			* ``name`` -The initial name

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``unique name`` -The current unique name
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		return doc.named_values_collection.get_unique_name( name )


	def get_named_value_data( self ):
		"""
		This method gets and returns a dictionary containing named value data.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``dictionary`` - named valuen data dictionary.
		"""

		data_dict = { }

		data_dict[ 'name' ] 		= self.get_name( )
		data_dict[ 'value' ] 	= self.get_value( )

		return data_dict



class Anim_Named_Value_Collection( Collection ):
	"""
	Named Value collections object

	*Arguments:*
		* ``doc`` -Active animation document.

	*Keyword Arguments:*
		* ``none``
	"""

	def _gather_item_names( self ):
		"""
		Gathers and returns a set of named values from the active animation document's
		active animation set and group.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``set`` -Containing animation set's active named values.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		named_values_items = [ ]
		if doc.active_set and doc.active_group:
			named_values_items = set( doc.get_anim_set_named_values( doc.active_set, doc.active_group ) )

		return named_values_items


	def _create_item( self, named_value_obj ):
		"""
		This method creates a new tag association item object.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``named_value_obj`` -named value object.

		*Returns:*
			* ``Anim_Named_Value_Item`` -newly created Anim_Named_Value_Item.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		return Anim_Named_Value_Item( doc, named_value_obj, set_name = doc.active_set, group_name = doc.active_group )


	def get_node_type( self ):
		"""
		This method gets and returns Anim_Named_Value_Collection node type constant.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``node type constant`` -Node type constant.
		"""
		return ctg.ae2.ui.const.NODE_TYPE_ANIM_NAMED_VALUE


	def get_item_by_name( self, name, use_cached = True ):
		"""
		Retrieves an item from the collection by name.

		*Arguments:*
			* ``name`` 			<String> Key name of the item to lookup.

		*Keyword Arguments:*
			* ``use_cached`` 	<Bool> Use cached results or get latest from document

		*Returns:*
			* ``items`` 		<items> or ``none``
		"""

		if not use_cached:
			self.update_collection( )

		items = [ item for item in self.get_items( ) if item.get_name( ) == name ]

		return items


	def get_item_by_uid( self, uid, use_cached = True ):
		"""
		Retrieves an item from the collection by name.

		*Arguments:*
			* ``uid`` 			<int> Key uid of the item to lookup.

		*Keyword Arguments:*
			* ``use_cached`` 	<Bool> Use cached results or get latest from document

		*Returns:*
			* ``result`` 		<items> or ``none``
		"""

		if not use_cached:
			self.update_collection( )

		items = [ item for item in self.get_items( ) if item.get_uid( ) == uid ]
		return items


	def check_named_value_existance( self, data_obj ):
		"""
		This method checks is the named values exists or not from a data object.

		*Arguments:*
			* ``data_obj`` -data object to be checked for named value existance.

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``bool`` -indicating whether named value exists or not.
		"""

		named_values = self.get_item_by_name( data_obj.get_name( ) )

		if len( named_values ) > 0:
			return True
		else:
			return False


	def create_new_named_value( self, name, data = None ):
		"""
		This method creates a new named value object.

		*Arguments:*
			* ``name`` -name for the newly created named value

		*Keyword Arguments:*
			* ``data``  -a list containing name and value to be assigned to the new named value

		*Returns:*
			* ``new named value`` -new named value object.
		"""
		doc = AnimationEditor.get_active_document()

		if not doc:
			return

		new_named_value = AnimationEditor.ae_named_value( )
		# set the new uid
		new_uid = doc.get_new_uid( )
		new_named_value.set_uid( new_uid )

		new_name = name
		value    = 0.0
		if data:
			new_name = data[0]
			value = data[1]

		new_named_value.set_value( float( value ) )
		new_named_value.set_name( new_name )

		return new_named_value


	def create( self ):
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		named_value_exists = False
		name = "New_Named_Value"

		# Make sure the name doesnt exist as a tag already
		named_value_exists = bool( self.get_item_by_name( name ) )

		# Increment the tag name if it already exists
		while named_value_exists:
			name = ctg.ae2.core.ae_common_operations.increment_string( name )
			named_value_exists = bool( self.get_item_by_name( name ) )

		# Create a new tag association object
		new_named_value = self.create_new_named_value( name )

		named_value_created = doc.undoable_create_anim_named_value( doc.active_set, doc.active_group, new_named_value )
		if named_value_created:
			self.update_collection( )

		return named_value_created


	def delete( self, data_obj ):
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		did_delete = False
		named_values = None

		# remove a tag item or locate tags containing the data_obj name
		named_values = self.get_item_by_uid( data_obj.get_uid( ) )

		if named_values:
			for named_value in named_values:
				did_delete = doc.undoable_delete_anim_named_value( named_value.set_name, named_value.group_name, named_value.get_uid( ) )

			if did_delete:
				doc.selection_manager.recent_sel_named_values = None
				self.update_collection( )

		return did_delete




# Group data collection
class Child_Bone_Collection( Collection ):
	def __init__( self, doc, parent_bone_name ):
		self.parent_bone_name = parent_bone_name
		Collection.__init__( self, doc )


	def _gather_item_names( self ):
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		parent_bone = doc.get_bone_by_name( self.parent_bone_name )
		child_bone_names = [ ]
		if parent_bone:
			child_bone_names = parent_bone.get_children_bone_names()

		return set( child_bone_names )


	def _create_item( self, name ):
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		return Rig_Bone_Item( doc, name )


	def get_node_type( self ):
		return ctg.ae2.ui.const.NODE_TYPE_RIG_BONE



#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
## Action Tag Data ##
#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# Individual Action Tag data object
class Rig_Bone_Item( object ):
	"""
	Class for the Individual action tag data object

	*Arguments:*
		* ``doc``  -Active animation document
		* ``name`` -name of the animation action tag object

	*Keyword Arguments:*
		* ``temporary``

	"""

	def __init__( self, doc, name ):
		self.doc   = doc
		self.name  = name
		self.child_bones_collection = Child_Bone_Collection( doc, name )


	def get_name( self ):
		"""
		This method gets and returns Action_Tag_Item name.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``name`` -Action_Tag_Item name.
		"""

		return self.name


	def get_parent( self ):
		"""
		This method gets and return Animation Set parent.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``parent`` -Animation Set parent Item
		"""

		parent = None
		doc = AnimationEditor.get_active_document()
		if not doc:
			return parent

		parent_bone = doc.get_parent_bone( self.get_name( ) )
		if parent_bone:
			parent = doc.rig_bone_collection.get_item_by_name( parent_bone.get_bone_name( ) )

		return parent


	def get_child_bones( self, use_cached = True ):
		"""
		This method get and returns a list of group items.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``used_cached`` -Use cached results or get latest from document.

		*Returns:*
			* ``groups`` -list of groups items
		"""

		child_bones = self.child_bones_collection.get_items( use_cached = use_cached )

		return child_bones



	def get_node_type( self ):
		"""
		This method gets and returns Action_Tag_Item node type constant.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``node type constant`` -Node type constant.
		"""

		return ctg.ae2.ui.const.NODE_TYPE_RIG_BONE


	def validate_name( self, name ):
		"""
		This Method checks the name for invalid characters, also checks if
		the name exists in action tag collection.

		*Arguments:*
			* ``name`` -name to be validated

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``bool`` -True indicates the name is valid, and False the name is not valid.

		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		if name == '':
			return False

		valid_name = doc.rig_bone_collection.validate_name_pattern( name )
		if valid_name:
			exists = doc.rig_bone_collection.check_name_existance( name )
			if not exists:
				return True
			else:
				if self.get_name().lower() != name.lower():
					return False
				else:
					return True
		else:
			return False


	def get_unique_name( self, name ):
		"""
		Checks if the name exists in action tag collection, if the name exists adds an
		index and return it as new name, if the name does not exists in the
		collection, return the name.

		*Arguments:*
			* ``name`` -The initial name

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``unique name`` -The current unique name
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		return doc.rig_bone_collection.get_unique_name( name )



class Rig_Bone_Collection( Collection ):
	"""
	Aaction tag collections object

	*Arguments:*
		* ``doc`` -Active animation document.

	*Keyword Arguments:*
		* ``none``
	"""

	def _gather_item_names( self ):
		"""
		Gathers and returns a set of action tag names from the active animation document.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``set`` -Containing animation action tag names.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		bone_names = [ ]
		root_bones = doc.get_bone_heirarchy( )
		if root_bones:
			for root_bone in root_bones:
				bone_names.append( root_bone.get_bone_name( ) )

		return set( bone_names )


	def _create_item( self, name ):
		"""
		This method creates Action_Tag_Item with a specified name.

		*Arguments:*
			* ``name`` -name for the action tag item.

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``Action_Tag_Item`` -Newly created Action_Tag_Item.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		return Rig_Bone_Item( doc, name )


	def get_node_type( self ):
		"""
		This method gets and returns Action_Tag_Item node type constant.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``node type constant`` -Node type constant.
		"""

		return ctg.ae2.ui.const.NODE_TYPE_RIG_BONE


	def validate_name( self, name ):
		"""
		This Method checks the name for invalid characters, also checks if
		the name exists in action tag collection.

		*Arguments:*
			* ``name`` -name to be validated

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``bool`` -True indicates the name is valid, and False the name is not valid.
		"""
		if name == '':
			return False

		valid_name = self.validate_name_pattern( name )
		if valid_name:
			exists = self.check_name_existance( name )
			if not exists:
				return True
			else:
				return False
		else:
			return False

#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
## Action Tag Data ##
#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# Individual Modifier object
class Modifier_Item( object ):
	"""
	Class for the Individual action tag data object

	*Arguments:*
		* ``doc``  -Active animation document
		* ``name`` -name of the animation action tag object

	*Keyword Arguments:*
		* ``temporary``
	"""

	def __init__( self, doc, name ):
		self.doc   = doc
		self.name  = name


	def get_name( self ):
		"""
		This method gets and returns Action_Tag_Item name.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``name`` -Action_Tag_Item name.
		"""

		return self.name


	def get_modifier( self ):
		"""
		This method gets and returns control filter object.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``control filter object`` -animation control filter object.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		return doc.get_modifier( self.get_name( ) )


	def update_modifier( self, modifier_obj, old_name = None ):
		"""
		This method updates named value.

		*Arguments:*
			* ``named_value_obj`` -named_value_obj association to update.

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``bool`` -indicating operation was successful or not.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc or not modifier_obj:
			return
		name = None
		if old_name:
			name = old_name
		else:
			name = self.get_name( )


		return doc.undoable_modify_modifier( name , modifier_obj )



	def set_type( self, val ):
		"""
		This method gets and returns control filter object.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``control filter object`` -animation control filter object.
		"""
		doc = AnimationEditor.get_active_document()
		modifier_obj = self.get_modifier( )
		if not doc or not modifier_obj:
			return None

		modifier_obj.set_type( val )

		return self.update_modifier( modifier_obj )


	def get_type( self ):
		"""
		This method gets and returns control filter object.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``control filter object`` -animation control filter object.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		return self.get_modifier( ).get_type( )


	def set_xml( self, value ):
		"""
		This method gets and returns control filter object.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``control filter object`` -animation control filter object.
		"""
		doc = AnimationEditor.get_active_document()
		modifier_obj = self.get_modifier( )
		if not doc or not modifier_obj:
			return None

		modifier_obj.set_xml( value )

		return self.update_modifier( modifier_obj )


	def set_name( self, name ):
		"""
		This method gets and returns control filter object.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``control filter object`` -animation control filter object.
		"""
		doc = AnimationEditor.get_active_document()
		modifier_obj = self.get_modifier( )
		if not doc or not modifier_obj:
			return None

		old_name = self.get_name( )

		modifier_obj.set_name( name )
		self.name = name

		return self.update_modifier( modifier_obj, old_name=old_name )


	def get_xml( self ):
		"""
		This method gets and returns control filter object.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``control filter object`` -animation control filter object.
		"""
		doc = AnimationEditor.get_active_document()
		modifier_obj = self.get_modifier( )
		if not doc or not modifier_obj:
			return None

		return modifier_obj.get_xml( )


	def set_control_dependencies( self, dependencies ):
		"""
		This method gets and returns control filter object.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``control filter object`` -animation control filter object.
		"""
		doc = AnimationEditor.get_active_document()
		modifier_obj = self.get_modifier( )
		if not doc or not modifier_obj:
			return None

		try:
			modifier_obj.set_control_dependencies( dependencies )
			return self.update_modifier( modifier_obj )

		except TypeError:
			return None


	def get_control_dependencies( self ):
		"""
		This method gets and returns control filter object.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``control filter object`` -animation control filter object.
		"""
		doc = AnimationEditor.get_active_document()
		modifier_obj = self.get_modifier( )
		if not doc or not modifier_obj:
			return None

		return modifier_obj.get_control_dependencies( )


	def get_node_type( self ):
		"""
		This method gets and returns Action_Tag_Item node type constant.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``node type constant`` -Node type constant.
		"""

		return ctg.ae2.ui.const.NODE_TYPE_MODIFIER


	def get_modifier_data( self ):
		"""
		Gets all data relating to a modifier, and returns a dict of it's data.

		**Arguments:**

			:``None``

		**Keyword Arguments:**

			:``None``

		**Returns:**

			:``modifier_data``:	`dict` Dict of all data held by one modifier.
		"""

		modifier_data = { }

		modifier_data[ 'name' ]                   = self.get_name( )
		modifier_data[ ' modifier' ]             = self.get_modifier( )
		modifier_data[ 'type' ]						  = self.get_type( )
		modifier_data[ 'dependencies' ]      = self.get_control_dependencies( )

		return modifier_data


	def delete( self ):
		doc = AnimationEditor.get_active_document()
		did_delete = False
		if not doc:
			return did_delete


		# remove a tag item or locate tags containing the data_obj name
		did_delete = doc.undoable_delete_modifier ( self.get_name( ) )

		if did_delete:
			doc.modifier_collection.update_collection( clear_items= True )
			doc.event_manager.post_modifier_deleted_event( [ None ] )

		return did_delete


	def validate_name( self, name ):
		"""
		This Method checks the name for invalid characters, also checks if
		the name exists in action tag collection.

		*Arguments:*
			* ``name`` -name to be validated

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``bool`` -True indicates the name is valid, and False the name is not valid.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		if name == '':
			return False

		valid_name = doc.modifier_collection.validate_name_pattern( name )
		if valid_name:
			exists = doc.modifier_collection.check_name_existance( name )
			if not exists:
				return True
			else:
				if self.get_name().lower() != name.lower():
					return False
				else:
					return True
		else:
			return False


class Modifier_Collection( Collection ):
	"""
	Aaction tag collections object

	*Arguments:*
		* ``doc`` -Active animation document.

	*Keyword Arguments:*
		* ``none``
	"""

	def _gather_item_names( self ):
		"""
		Gathers and returns a set of action tag names from the active animation document.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``set`` -Containing animation action tag names.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		modifier_names = doc.get_modifier_names( )
		return set( modifier_names )


	def _create_item( self, name ):
		"""
		This method creates Action_Tag_Item with a specified name.

		*Arguments:*
			* ``name`` -name for the action tag item.

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``Action_Tag_Item`` -Newly created Action_Tag_Item.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		return Modifier_Item( doc, name )


	def get_node_type( self ):
		"""
		This method gets and returns Action_Tag_Item node type constant.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``node type constant`` -Node type constant.
		"""

		return ctg.ae2.ui.const.NODE_TYPE_MODIFIER


	def validate_name( self, name ):
		"""
		This Method checks the name for invalid characters, also checks if
		the name exists in action tag collection.

		*Arguments:*
			* ``name`` -name to be validated

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``bool`` -True indicates the name is valid, and False the name is not valid.

		"""
		if name == '':
			return False

		valid_name = self.validate_name_pattern( name )
		if valid_name:
			exists = self.check_name_existance( name )
			if not exists:
				return True
			else:
				return False
		else:
			return False


	def create_new_modifier( self, name, data = None ):
		"""
		This method creates a new named value object.

		*Arguments:*
			* ``name`` -name for the newly created named value

		*Keyword Arguments:*
			* ``data``  -a list containing name and value to be assigned to the new named value

		*Returns:*
			* ``new named value`` -new named value object.
		"""
		doc = AnimationEditor.get_active_document()

		if not doc:
			return

		# set the new uid
		created = doc.undoable_create_modifier( name )
		if created:
			self.update_collection( clear_items= True)

		return created


	def create( self, new_name=None ):
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		modifier_exists = False
		if not new_name:
			new_name = "New_Modifier"

		# Make sure the name doesnt exist as a tag already
		modifier_exists = bool( self.get_item_by_name( new_name ) )

		# Increment the tag name if it already exists
		while modifier_exists:
			new_name = ctg.ae2.core.ae_common_operations.increment_string( new_name )
			modifier_exists = bool( self.get_item_by_name( new_name ) )

		# Create a new tag association object
		modifier_created = self.create_new_modifier( new_name )

		return modifier_created


	def rename( self, modifier_obj, new_name ):
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		modifier_exists = False
		# Make sure the name doesnt exist as a tag already
		modifier_exists = bool( self.get_item_by_name( new_name ) )

		# Increment the tag name if it already exists
		while modifier_exists:
			new_name = ctg.ae2.core.ae_common_operations.increment_string( new_name )
			modifier_exists = bool( self.get_item_by_name( new_name ) )

		# Create a new tag association object
		modifier_renamed = modifier_obj.set_name( new_name )

		return modifier_renamed


	def delete( self, data_obj ):
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		did_delete = False
		# remove a tag item or locate tags containing the data_obj name
		new_modifier = doc.get_modifier( data_obj.get_name( ) )

		if new_modifier:
			did_delete = doc.undoable_delete_modifier ( data_obj.get_name( ) )

			if did_delete:
				self.update_collection( clear_items= True )
				doc.event_manager.post_modifier_deleted_event( [ None ] )

		return did_delete


# Individual Modifier object
class Rig_Aux_Data_Item( object ):
	"""
	Class for the Individual action tag data object

	*Arguments:*
		* ``doc``  -Active animation document
		* ``name`` -name of the animation action tag object

	*Keyword Arguments:*
		* ``temporary``
	"""

	def __init__( self, doc, name ):
		self.doc   = doc
		self.name  = name


	def get_name( self ):
		"""
		This method gets and returns Action_Tag_Item name.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``name`` -Action_Tag_Item name.
		"""

		return self.name


	def get_rig_aux_data( self ):
		"""
		This method gets and returns control filter object.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``control filter object`` -animation control filter object.
		"""

		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		return doc.get_rig_aux_data( self.get_name( ) )


	def add_bone( self, bone ):
		self.get_rig_aux_data( ).add_bone( bone )


	def add_bone_by_name( self, bone_name ):
		self.get_rig_aux_data( ).add_bone_by_name( bone_name )


	def get_bones( self ):
		"""
		Returns all bones associated to rig aux data item.

		**Arguments:**

			:``None``

		**Keyword Arguments:**

			:``None``

		**Returns:**

			:``self.get_rig_aux_data( ).get_bones( )``:	`list ` List of all bones
		"""

		return self.get_rig_aux_data( ).get_bones( )


	def get_bone( self, bone_name ):
		"""
		Returns bone object from rig aux item.

		**Arguments:**

			:``bone_name``:  ``str`` Name of the bone object

		**Keyword Arguments:**

			:``None``

		**Returns:**

			:``self.get_rig_aux_data( ).get_bone( bone_name )``:	`ae_rig_aux_bone object ` Bone object
		"""

		return self.get_rig_aux_data( ).get_bone( bone_name )


	def get_bone_aux_data( self, bone ):
		"""
		Returns aux data for single bone object on rig aux data.

		**Arguments:**

			:``bone``: `ae_rig_aux_bone object` Bone object

		**Keyword Arguments:**

			:``None``

		**Returns:**

			:``bone.get_bone_aux_data_list( )``:	`list ` List of all aux data for bone
		"""

		return bone.get_bone_aux_data_list( )


	def get_all_bones_aux_data( self ):
		"""
		Returns all bones associated to rig aux data item.

		**Arguments:**

			:``None``

		**Keyword Arguments:**

			:``None``

		**Returns:**

			:``bone_aux_data_dict``:	`dict ` Dict of aux data for every bone object on rig aux data.
		"""

		bone_aux_data_dict = { }

		for bone in self.get_bones( ):
			bone_aux_data_dict[ bone.get_bone_name( ) ] = bone.get_bone_aux_data_list( )

		return bone_aux_data_dict


	def update_rig_aux_data( self, rig_aux_data_obj ):
		"""
		This method updates named value.

		*Arguments:*
			* ``named_value_obj`` -named_value_obj association to update.

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``bool`` -indicating operation was successful or not.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc or not rig_aux_data_obj:
			return

		return doc.undoable_modify_rig_aux_data( self.get_name( ), rig_aux_data_obj )



	def set_name( self, name ):
		"""
		This method gets and returns control filter object.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``control filter object`` -animation control filter object.
		"""
		doc = AnimationEditor.get_active_document()
		rig_aux_data_obj = self.get_rig_aux_data( )
		if not doc or not rig_aux_data_obj:
			return

		rig_aux_data_obj.set_name( name )

		return self.update_rig_aux_data( rig_aux_data_obj )


	def get_xml( self ):
		"""
		Returns a dict of all bone xmls for a given rig_aux_data object.

		**Arguments:**

			:``None``

		**Keyword Arguments:**

			:``None``

		**Returns:**

			:``xml_dict``:	`dict` Dict of each bone name, and the xml associated with it.
		"""

		xml_dict = { }
		rig_aux_data = self.get_rig_aux_data( )

		for bone in rig_aux_data.get_bones( ):
			for data in bone.get_bone_aux_data_list( ):
				data_xml = data.get_bone_aux_xml( )

				xml_dict[ bone.get_bone_name( ) ] = data_xml

		return xml_dict


	def get_node_type( self ):
		"""
		This method gets and returns Action_Tag_Item node type constant.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``node type constant`` -Node type constant.
		"""

		return ctg.ae2.ui.const.NODE_TYPE_RIG_AUX_DATA

	def delete( self, ):
		"""
		This method deletes control filters items.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``delete_items`` -list of control filter items to be deleted.

		*Returns:*
			* ``bool`` -indicating the operation was successful.

		"""

		success = False
		doc = AnimationEditor.get_active_document()
		if not doc:
			return success

		success = doc.undoable_delete_rig_aux_data( self.get_name( ))
		if success:

			doc.rig_aux_data_collection.update_collection( clear_items= True )
			doc.event_manager.post_rig_aux_data_deleted_event( [ None ] )

		return success


	def validate_name( self, name ):
		"""
		This Method checks the name for invalid characters, also checks if
		the name exists in action tag collection.

		*Arguments:*
			* ``name`` -name to be validated

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``bool`` -True indicates the name is valid, and False the name is not valid.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		if name == '':
			return False

		valid_name = doc.rig_aux_data_collection.validate_name_pattern( name )
		if valid_name:
			exists = doc.rig_aux_data_collection.check_name_existance( name )
			if not exists:
				return True
			else:
				if self.get_name().lower() != name.lower():
					return False
				else:
					return True
		else:
			return False


class Rig_Aux_Data_Collection( Collection ):
	"""
	Aaction tag collections object

	*Arguments:*
		* ``doc`` -Active animation document.

	*Keyword Arguments:*
		* ``none``
	"""

	def _gather_item_names( self ):
		"""
		Gathers and returns a set of action tag names from the active animation document.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``set`` -Containing animation action tag names.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		rig_aux_data_names = [ ]
		rig_aux_data_list = doc.get_rig_aux_data_list()
		for rig_aux_data in rig_aux_data_list:
			name = rig_aux_data.get_name( )
			if name not in rig_aux_data_names:
				rig_aux_data_names.append( name )

		return set( rig_aux_data_names )


	def _create_item( self, name ):
		"""
		This method creates Action_Tag_Item with a specified name.

		*Arguments:*
			* ``name`` -name for the action tag item.

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``Action_Tag_Item`` -Newly created Action_Tag_Item.
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		return Rig_Aux_Data_Item( doc, name )


	def get_node_type( self ):
		"""
		This method gets and returns Action_Tag_Item node type constant.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``node type constant`` -Node type constant.
		"""

		return ctg.ae2.ui.const.NODE_TYPE_RIG_AUX_DATA


	def validate_name( self, name ):
		"""
		This Method checks the name for invalid characters, also checks if
		the name exists in action tag collection.

		*Arguments:*
			* ``name`` -name to be validated

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``bool`` -True indicates the name is valid, and False the name is not valid.
		"""
		if name == '':
			return False

		valid_name = self.validate_name_pattern( name )
		if valid_name:
			exists = self.check_name_existance( name )
			if not exists:
				return True
			else:
				return False
		else:
			return False


	def create_new_rig_aux_data( self, name, data = None ):
		"""
		This method creates a new named value object.

		*Arguments:*
			* ``name`` -name for the newly created named value

		*Keyword Arguments:*
			* ``data``  -a list containing name and value to be assigned to the new named value

		*Returns:*
			* ``new named value`` -new named value object.
		"""
		doc = AnimationEditor.get_active_document()

		if not doc:
			return

		# set the new uid
		created = doc.undoable_create_rig_aux_data( name )
		if created:
			self.update_collection( clear_items= True)

		return created


	def create( self, new_name=None ):
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		rig_aux_data_exists = False
		if not new_name:
			new_name = "New_Rig_Aux_Data"

		# Make sure the name doesnt exist as a tag already
		rig_aux_data_exists = bool( self.get_item_by_name( new_name ) )

		# Increment the tag name if it already exists
		while rig_aux_data_exists:
			new_name = ctg.ae2.core.ae_common_operations.increment_string( new_name )
			rig_aux_data_exists = bool( self.get_item_by_name( new_name ) )

		# Create a new tag association object
		rig_aux_data_created = self.create_new_rig_aux_data( new_name )

		return rig_aux_data_created, new_name



	def delete( self, data_obj ):
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		did_delete = False
		if new_modifier:
			did_delete = doc.undoable_delete_rig_aux_data( data_obj.get_name() )

			if did_delete:
				self.update_collection( clear_items= True )
				doc.event_manager.post_rig_aux_data_deleted_event( [ None ] )

		return did_delete








