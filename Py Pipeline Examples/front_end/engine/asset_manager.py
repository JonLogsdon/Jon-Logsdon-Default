import wx
import os
import win32clipboard
import json
import ast

import ctg.ae2.core.ae_common_operations
import ctg.ae2.ui.const
import ctg.ae2.ui.lister
import ctg.ae2.ui.node

import ctg.ae2.node_graph.ae_blend_tree_editor
import ctg.ae2.node_graph.ae_state_machine_editor
import ctg.ae2.node_graph.ae_blend_tree_nodes
import ctg.ae2.node_graph.ae_state_machine_nodes

import ctg.ae2.ui.events

import ctg.lister_lib.const

import vlib.data_enum
import vlib.debug
import vlib.ui.lister_lib.node
import vlib.ui.lister_lib2
import vlib.ui.node_graph.document
import vlib.ui.node_graph.node_variable
import vlib.types
import vlib.ui.lister_lib.core

import xml.etree.cElementTree

import _resourcelib

import AnimationEditor
import GUILib
import param_types

# COMMAND CONSTANTS

CMD_ID_STATE_CREATE				= wx.NewId()
CMD_ID_STATE_DELETE				= wx.NewId()

CMD_ID_ACTION_CREATE				= wx.NewId()
CMD_ID_ACTION_DELETE				= wx.NewId()

CMD_ID_GROUP_CREATE				= wx.NewId()
CMD_ID_GROUP_DELETE				= wx.NewId()
CMD_ID_GROUP_RENAME				= wx.NewId()
CMD_ID_GROUP_CLONE				= wx.NewId()

CMD_ID_SET_RENAME 				= wx.NewId()
CMD_ID_SET_DEL						= wx.NewId()
CMD_ID_SET_NEW						= wx.NewId()
CMD_ID_SET_NEW_CHILD				= wx.NewId()
CMD_ID_SET_ADD_GROUP				= wx.NewId()

CMD_ID_GROUP_REMOVE				= wx.NewId()

CMD_ID_DISPLAY_FLAT_SETS		= wx.NewId()
CMD_ID_DISPLAY_FLAT_GROUPS		= wx.NewId()
CMD_ID_DISPLAY_INVALID_GROUPS	= wx.NewId()
CMD_ID_DISPLAY_ISOLATED_SET	= wx.NewId()

CMD_ID_DISPLAY_ITEMS_ALL		= wx.NewId()
CMD_ID_DISPLAY_ITEMS_USED		= wx.NewId()
CMD_ID_DISPLAY_ITEMS_UNUSED	= wx.NewId()

CMD_ID_ITEM_PACKAGE = wx.NewId( )

CMD_ID_EXPAND_ALL					= wx.NewId()
CMD_ID_COLLAPSE_ALL				= wx.NewId()
CMD_ID_SELECT_ALL					= wx.NewId()

CMD_ID_CREATE_NEW 				= wx.NewId()
CMD_ID_CREATE_NEW_CHILD 		= wx.NewId()
CMD_ID_RENAME						= wx.NewId()
CMD_ID_DELETE						= wx.NewId()
CMD_ID_ADD_TO_CATALOG			= wx.NewId()
CMD_ID_REMOVE_FROM_CATALOG		= wx.NewId()
CMD_ID_ADD_GROUP_TO_SET			= wx.NewId()

CMD_ID_COPY_CLIP_PROPERTIES	= wx.NewId()
CMD_ID_PASTE_CLIP_PROPERTIES	= wx.NewId()
CMD_ID_CLEAR_CLIP_PROPERTIES  = wx.NewId()

CMD_ID_CRUNCH_CLIP   = wx.NewId()
CMD_ID_GENERATE_FOOTSTEP_TRIGGERS	= wx.NewId()

CMD_DELTA 				= wx.NewId()
CMD_CAP 					= wx.NewId()
CMD_ADD 					= wx.NewId()
CMD_LINEAR 				= wx.NewId()

CMD_ID_COPY_RAD  = wx.NewId( )
CMD_ID_PASTE_RAD  = wx.NewId( )

NUMBER_CONTROL 		= 'Number'
BOOL_CONTROL 			= 'Bool'

CMD_ID_DELETE_RIG_AUX_DATA		   = wx.NewId()
CMD_ID_CREATE_RIG_AUX_DATA       = wx.NewId( )
CMD_ID_RENAME_RIG_AUX_DATA       = wx.NewId( )

CMD_ID_ADD_MODIFIER       = wx.NewId( )
CMD_ID_DELETE_MODIFIER    = wx.NewId( )
CMD_ID_RENAME_MODIFIER    = wx.NewId( )


ICON_OBJSET_ADD				= ctg.ui.util.get_project_image( 'outliner_objset_add_16.png', as_bitmap = True )
ICON_OBJSET_DEL				= ctg.ui.util.get_project_image( 'outliner_objset_delete_16.png', as_bitmap = True )

TEST_LISTER = 'TEST_LISTER'


HELP_URL = ur"onenote:http://vsp/projects/ctg/CTG%20OneNote/CTG/Tools/User%20Documentation/CTG%20Editor/Animation%20Editor/General.one#section-id={866BB17A-1B64-4D66-AB0E-17AA3344AEA0}&end"


def anim_clip_modified( doc, clip_name, new_name ):
	"""
	Called by a callback defined in \ctg\startup\setup_anim_ed_plugin.py

	TO DO:
	Determine by way of the arguments which operation has occurred in the undo/redo
	"""
	if doc:
		item = None

		# update clip collection
		doc.clip_collection.update_collection( )

		# get the clip item
		item = doc.clip_collection.get_item_by_name( clip_name )

		# post event
		doc.event_manager.post_clip_update_event( [ item ] )


def anim_clip_added(doc, clip_name):
	if doc:
		item = None

		# update clip collection
		doc.clip_collection.update_collection( )


def anim_tag_modified( doc, old_name, new_name ):
	"""
	Called by a callback defined in \ctg\startup\setup_anim_ed_plugin.py

	TO DO:
	Determine by way of the arguments which operation has occurred in the undo/redo
	"""
	if doc:
		# Set current item to None
		item = None
		tag_name = None

		# Update both tag collections
		doc.action_tag_collection.update_collection( )
		doc.state_tag_collection.update_collection( )

		if old_name and new_name:

			# Tag has been Deleted
			if new_name == '':
				tag_name = old_name

			# Tag has been Renamed or Moved
			elif old_name != new_name or old_name == new_name:
				tag_name = new_name

		# Redo operation for a Tag that has been Deleted
		elif not old_name and new_name:
			if new_name != '':
				tag_name = new_name

		# Undo operation for a Tag that has been Deleted
		elif not new_name and old_name:
			if old_name != '':
				tag_name = old_name

		# Determine if the tag is a state or action tag
		if doc.anim_tag_is_state( tag_name ):
			item = doc.state_tag_collection.get_item_by_name( tag_name )
		else:
			item = doc.action_tag_collection.get_item_by_name( tag_name )

		# post event
		doc.event_manager.post_tag_modified_event( [ item ] )


def blend_tree_modified( doc, old_name, new_name ):
	"""
	Handle Undo/Redo operations pertaining the state machines being modified
	Called by a callback defined in \ctg\startup\setup_anim_ed_plugin.py

	TO DO:
	Determine by way of the arguments which operation has occurred in the undo/redo
	"""
	if doc:
		print 'Blend Tree: {0}'.format( doc.get_blend_tree_names( ) )

		if old_name == new_name:

			# XML modification
			ctg.ae2.node_graph.ae_node_graph_panel.handle_blend_tree_modified( doc, old_name, new_name )

		# Undo/Redo Operation to Rename a State Machine
		elif old_name and new_name:

			# Rename Blend Tree
			doc.node_graph_panel.handle_node_graph_rename( old_name, new_name )
			doc.blend_tree_collection.update_collection(  )
			doc.node_graph_tree_collection.update_collection(  )
			item = doc.blend_tree_collection.get_item_by_name( new_name )
			doc.event_manager.post_blend_tree_renamed_event( [ item ], old_name = old_name, new_name = new_name )

		# Undo operation for a Blend Tree that has been Deleted
		elif not old_name and new_name:

			# Create Blend Tree
			doc.blend_tree_collection.update_collection( )
			doc.node_graph_tree_collection.update_collection( )
			item = doc.blend_tree_collection.get_item_by_name( new_name )
			doc.event_manager.post_blend_tree_created_event( [ item ] )

		# Redo operation to delete a Blend Tree
		elif not new_name and old_name:

			# Delete a Blend Tree
			doc.node_graph_panel.handle_node_graph_delete( old_name )
			delete_item = doc.blend_tree_collection.get_item_by_name( old_name )
			doc.blend_tree_collection.update_collection( )
			doc.node_graph_tree_collection.update_collection( )
			doc.event_manager.post_blend_tree_deleted_event( [ delete_item ] )

		else:
			# Force Update
			doc.event_manager.post_blend_tree_renamed_event( [ None ], old_name = old_name, new_name = new_name )


def state_machine_modified( doc, old_name, new_name ):
	"""
	Handle Undo/Redo operations pertaining the state machines being modified
	Called by a callback defined in \ctg\startup\setup_anim_ed_plugin.py

	TO DO:
	Determine by way of the arguments which operation has occurred in the undo/redo
	"""
	if doc:
		#print 'State Machines: {0}'.format( doc.get_state_machine_names( ) )

		if old_name == new_name:

			# XML modification
			ctg.ae2.node_graph.ae_node_graph_panel.handle_state_machine_modified( doc, old_name )

		# Undo/Redo Operation to Rename a State Machine
		elif old_name and new_name:

			# Rename State Machine
			doc.node_graph_panel.handle_node_graph_rename( old_name, new_name )
			doc.state_machine_collection.update_collection( )
			doc.node_graph_tree_collection.update_collection( )
			item = doc.state_machine_collection.get_item_by_name( new_name )
			doc.event_manager.post_state_machine_renamed_event( [ item ], old_name = old_name, new_name = new_name )

		# Undo operation for a State Machine that has been Deleted
		elif not old_name and new_name:

			# Create State Machine
			doc.state_machine_collection.update_collection( )
			doc.node_graph_tree_collection.update_collection( )
			item = doc.state_machine_collection.get_item_by_name( new_name )
			doc.event_manager.post_state_machine_created_event( [ item ] )

		# Redo operation to Delete a State Machine
		elif not new_name and old_name:

			# Delete a State Machine
			doc.node_graph_panel.handle_node_graph_delete( old_name )
			delete_item = doc.state_machine_collection.get_item_by_name( old_name )
			doc.state_machine_collection.update_collection( )
			doc.node_graph_tree_collection.update_collection( )
			doc.event_manager.post_state_machine_deleted_event( [ delete_item ] )

		else:
			# Force Update
			doc.event_manager.post_state_machine_renamed_event( [ None ], old_name = old_name, new_name = new_name )


def control_filter_modified( doc, old_name, new_name ):
	"""
	Called by a callback defined in \ctg\startup\setup_anim_ed_plugin.py

	TO DO:
	Determine by way of the arguments which operation has occurred in the undo/redo
	"""
	if doc:
		print 'Control Filters: {0}'.format( doc.get_control_filter_names( ) )

		if old_name and new_name:

			# Control Filter has been Deleted
			if new_name == '':
				doc.control_filter_collection.update_collection( )
				item = doc.control_filter_collection.get_item_by_name( old_name )
				doc.event_manager.post_control_filter_renamed_event( [ item ], old_name = old_name )

			# Control Filter has been Renamed or Moved
			elif old_name != new_name or old_name == new_name:
				doc.control_filter_collection.update_collection( )
				item = doc.control_filter_collection.get_item_by_name( new_name )
				doc.event_manager.post_control_filter_renamed_event( [ item ], old_name = old_name )

			else:
				# Force Update
				doc.event_manager.post_control_filter_renamed_event( [ None ], old_name = old_name )

		elif not old_name and new_name:

			# Redo operation for a Control Filter that has been Deleted
			if new_name != '':
				doc.control_filter_collection.update_collection( )
				item = doc.control_filter_collection.get_item_by_name( new_name )
				doc.event_manager.post_control_filter_renamed_event( [ item ], old_name = old_name )

		elif not new_name and old_name:

			# Undo operation for a Control Filter that has been Deleted
			if old_name != '':
				doc.control_filter_collection.update_collection( )
				item = doc.control_filter_collection.get_item_by_name( old_name )
				doc.event_manager.post_control_filter_renamed_event( [ item ], old_name = old_name )

		else:
			# Force Update
			doc.event_manager.post_control_filter_renamed_event( [ None ], old_name = old_name )


def control_parameter_modified( doc, old_name, new_name ):
	"""
	Called by a callback defined in \ctg\startup\setup_anim_ed_plugin.py

	TO DO:
	Determine by way of the arguments which operation has occurred in the undo/redo
	"""
	if doc:
		print 'Control Parameters: {0}'.format( doc.get_control_parameter_names( ) )

		if old_name and new_name:

			# Control Parameter has been Deleted
			if new_name == '':
				doc.control_parameter_collection.update_collection( )
				item = doc.control_parameter_collection.get_item_by_name( old_name )
				doc.event_manager.post_control_parameter_renamed_event( [ item ], old_name = old_name )

			# Control Parameter has been Renamed or Moved
			elif old_name != new_name or old_name == new_name:
				doc.control_parameter_collection.update_collection( )
				item = doc.control_parameter_collection.get_item_by_name( new_name )
				doc.event_manager.post_control_parameter_renamed_event( [ item ], old_name = old_name )

			else:
				# Force Update
				doc.event_manager.post_control_parameter_renamed_event( [ None ], old_name = old_name )

		elif not old_name and new_name:

			# Redo operation for a Control Parameter that has been Deleted
			if new_name != '':
				doc.control_parameter_collection.update_collection( )
				item = doc.control_parameter_collection.get_item_by_name( new_name )
				doc.event_manager.post_control_parameter_renamed_event( [ item ], old_name = old_name )

		elif not new_name and old_name:

			# Undo operation for a Control Parameter that has been Deleted
			if old_name != '':
				doc.control_parameter_collection.update_collection( )
				item = doc.control_parameter_collection.get_item_by_name( old_name )
				doc.event_manager.post_control_parameter_renamed_event( [ item ], old_name = old_name )

		else:
			# Force Update
			doc.event_manager.post_control_parameter_renamed_event( [ None ], old_name = old_name )



class Generic_Text_Control( object ):
	def __init__( self, *args, **kwargs ):
		pass

	def create_control( self, parent, display_name ):
		# Create the control
		self.control = wx.TextCtrl(parent, -1, display_name, size=(200, -1))
		self.control.display_name = display_name

		return self.control


class Generic_Label_Control( object ):
	def __init__( self, *args, **kwargs ):
		pass

	def create_control( self, parent, display_name ):
		# Create the control
		self.control = wx.StaticText( parent, -1, display_name, size=(200, -1))
		self.control.display_name = display_name
		#self.control.GetLabelText

		return self.control


def build_control_dict():

	control_dict = {
	   #for the menu
	   ctg.ae2.ui.const.ASSET_LABEL_CREATE			: Generic_Text_Control(	),
	   ctg.ae2.ui.const.ASSET_LABEL_CREATE_CHILD	: Generic_Text_Control(	),
	   ctg.ae2.ui.const.ASSET_LABEL_RENAME			: Generic_Text_Control(	),
	   ctg.ae2.ui.const.ASSET_LABEL_DELETE			: Generic_Label_Control( )
	}

	return control_dict


class Floater_Dialog( vlib.ui.lister_lib.core.Floater_Input_Dialog_Base ):
	def __init__( self, parent, data_objs, operation, position, id_string = 'Nothing', display_name = 'Display Name', label_text = 'Label Text', node_type = None ):
		self.view 				= parent
		self.operation 		= operation
		self.display_name 	= display_name
		self.operation_type	= ctg.ae2.ui.const.ASSET_OPERATIONS_DICT.get( operation )
		self.label_text		= label_text
		self.data_objs 		= None
		self.data_obj 			= None
		self.node_type			= node_type

		# handle the objects we will operate on
		if len( data_objs ) == 0:
			self.data_objs = [ ]
			self.data_obj = None
		elif len( data_objs ) == 1:
			self.data_objs = data_objs
			self.data_obj = data_objs[0]
		elif len( data_objs ) > 1:
			self.data_objs = data_objs
			self.data_obj = data_objs[0]
			self.display_name	= 'multiple'

		# get control
		self.control = build_control_dict()[ self.operation_type ]
		vlib.ui.lister_lib.core.Floater_Input_Dialog_Base.__init__( self, parent, position )

		self.MakeModal( True )


	def setup_controls( self ):
		self.ctrl = self.control.create_control( self, self.display_name )

		label = wx.StaticText( self, -1, self.label_text )
		self.error_label = wx.StaticText( self, -1, 'Name is too long ( max length {0} )'.format( ctg.ae2.ui.const.MAX_NAME_LENGTH )  )
		self.error_label.Show( False )

		label.SetFont( wx.Font( 8, 70, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, wx.EmptyString ) )
		self.sizer_inner.Add( label, 0, wx.EXPAND | wx.ALL, 4 )
		self.sizer_inner.Add( self.error_label, 0, wx.EXPAND | wx.ALL, 4 )
		self.sizer_inner.Add( self.ctrl, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 2 )

		self.set_initial_value()


	def on_ok_pressed( self, event ):
		self.MakeModal( False )

		# get the document
		doc = AnimationEditor.get_active_document( )
		if not doc:
			return

		# get the dialog value
		if isinstance( self.ctrl, wx.StaticText ):
			input_name = self.ctrl.GetLabelText()
		else:
			input_name = self.ctrl.GetValue( )

		# perform the operation
		update_doc     = False
		destroy_dialog = True



		if self.operation is ctg.ae2.ui.const.ASSET_OPERATION_DELETE:
			do_update = False
			doc.selection_manager.set_selected_object(None)
			doc.animation_properties_pane.refresh_ui()
			for data_obj in self.data_objs:
				do_update = data_obj.delete( )
				if do_update:
					update_doc = True
		else:
			if len( input_name ) <= ctg.ae2.ui.const.MAX_NAME_LENGTH:
				if self.operation is ctg.ae2.ui.const.ASSET_OPERATION_CREATE:
					print("create: ", self.view.active_collection )
					update_doc = self.view.active_collection.create( new_name = input_name )

				elif self.operation is ctg.ae2.ui.const.ASSET_OPERATION_CREATE_CHILD:
					update_doc = self.data_obj.create( new_name = input_name, parent_name = self.data_obj.get_name( ) )

				elif self.operation is ctg.ae2.ui.const.ASSET_OPERATION_CREATE_DELTA:
					update_doc = self.view.active_collection.create( new_name = input_name, filter_type = ctg.ae2.ui.const.DELTA_MULTIPLIER )

				elif self.operation is ctg.ae2.ui.const.ASSET_OPERATION_CREATE_LINEAR:
					update_doc = self.view.active_collection.create( new_name = input_name, filter_type = ctg.ae2.ui.const.LINEAR_MAP )

				elif self.operation is ctg.ae2.ui.const.ASSET_OPERATION_CREATE_CAP:
					update_doc = self.view.active_collection.create( new_name = input_name, filter_type = ctg.ae2.ui.const.CAP )

				elif self.operation is ctg.ae2.ui.const.ASSET_OPERATION_CREATE_ADD:
					update_doc = self.view.active_collection.create( new_name = input_name, filter_type = ctg.ae2.ui.const.ADD )

				elif self.operation is ctg.ae2.ui.const.ASSET_OPERATION_RENAME:
					update_doc = self.data_obj.rename( input_name )

			else:
				self.error_label.Show( True )
				self.sizer_inner.Layout( )
				self.sizer.Layout( )
				self.SetSize( ( -1, 124 ))
				self.Layout( )
				self.Refresh( )

				destroy_dialog = False

		if update_doc:
			self.view.GetParent( ).set_status_message( )
			self.view.GetParent( ).refresh_ui( clear_items = True )

		if destroy_dialog:
			self.Show( False )
			self.Destroy( )


	def on_cancel_pressed( self, event ):
		self.MakeModal( False )
		self.Show( False )
		self.Destroy( )


	def set_initial_value( self ):
		if isinstance( self.ctrl, wx.StaticText ):
			self.ctrl.SetLabelText( self.display_name )
		else:
			self.ctrl.SetValue( self.display_name )



class Anim_Asset_Context_Menu( vlib.ui.lister_lib2.core.Tree_Context_Menu ):
	def _setup_menu_custom( self ):
		self.node_type = self.view.GetParent( ).active_node_type

		self.menu_title				= ctg.ae2.ui.const.NODE_TYPE_STRING_DICT[ self.node_type ]
		self.add_group_dict			= {}
		self.remove_group_dict		= {}
		self.display_name				= ''
		self.nodes						= None
		self.data_objs = []
		self.data_obj					= None
		self.clipboard_data			= []
		self.selected_items = self.view.get_selection_manager( ).get_selection( )
		self.display_name = self.menu_title

		for item in self.selected_items:
			self.data_objs.append( item.data_obj )

		# set the name for the active node type
		self.node_name	= ctg.ae2.ui.const.NODE_TYPE_STRING_DICT[ self.node_type ]

		# set up data
		if len( self.data_objs ) > 0:
			self.clipboard_data	= self.view.get_data_from_clipboard( self.node_type )

		if len( self.data_objs ) == 1:
			self.data_obj = self.data_objs[0]
			self.display_name = self.data_objs[0].get_name( )
			if not self.display_name or len( self.display_name ) == 0:
				self.display_name = ''

		elif len( self.data_objs ) > 1:
			self.display_name = 'multiple'


		# build the menu
		# get the document
		doc = AnimationEditor.get_active_document( )

		# Determine what items to put into the menu
		if not self.node_type is ctg.ae2.ui.const.NODE_TYPE_ANIM_CLIP:
			if self.node_type == ctg.ae2.ui.const.NODE_TYPE_RIG_AUX_DATA:
				# Create new/Rename/Delete
				item = wx.MenuItem( self, CMD_ID_CREATE_NEW, u'Create {0}'.format( '' ), wx.EmptyString, wx.ITEM_NORMAL )
				item.SetBitmap( ctg.ui.util.get_project_image( 'outliner_objset_add_16.png', as_bitmap = True ), wx.BITMAP_TYPE_ANY )
				item.Enable( True )
				self.AppendItem( item )

				self.AppendSeparator( )

				item = wx.MenuItem( self, CMD_ID_COPY_RAD, 'Copy', wx.EmptyString, wx.ITEM_NORMAL )
				item.SetBitmap( ctg.ui.util.get_project_image( 'copy_16.png', as_bitmap = True ), wx.BITMAP_TYPE_ANY )
				item.Enable( True )
				self.AppendItem( item )

				item = wx.MenuItem( self, CMD_ID_PASTE_RAD, u'Paste', wx.EmptyString, wx.ITEM_NORMAL )
				item.SetBitmap( ctg.ui.util.get_project_image( 'paste_16.png', as_bitmap = True ), wx.BITMAP_TYPE_ANY )
				item.Enable( True )
				self.AppendItem( item )

				if self.selected_items:
					self.AppendSeparator( )

			elif self.node_type == ctg.ae2.ui.const.NODE_TYPE_CONTROL_FILTER:
				add_control_filter_menu = wx.Menu( )
				item = wx.MenuItem( self, CMD_DELTA, u'Delta Multiplier', wx.EmptyString, wx.ITEM_NORMAL )
				item.SetBitmap( ctg.ui.util.get_project_image( 'outliner_objset_add_16.png', as_bitmap = True ), wx.BITMAP_TYPE_ANY )
				add_control_filter_menu.AppendItem( item )

				item = wx.MenuItem( self, CMD_LINEAR, u'Linear Map', wx.EmptyString, wx.ITEM_NORMAL )
				item.SetBitmap( ctg.ui.util.get_project_image( 'outliner_objset_add_16.png', as_bitmap = True ), wx.BITMAP_TYPE_ANY )
				add_control_filter_menu.AppendItem( item )

				item = wx.MenuItem( self, CMD_CAP, u'Cap', wx.EmptyString, wx.ITEM_NORMAL )
				item.SetBitmap( ctg.ui.util.get_project_image( 'outliner_objset_add_16.png', as_bitmap = True ), wx.BITMAP_TYPE_ANY )
				add_control_filter_menu.AppendItem( item )

				item = wx.MenuItem( self, CMD_ADD, u'Add', wx.EmptyString, wx.ITEM_NORMAL )
				item.SetBitmap( ctg.ui.util.get_project_image( 'outliner_objset_add_16.png', as_bitmap = True ), wx.BITMAP_TYPE_ANY )
				add_control_filter_menu.AppendItem( item )

				self.AppendSubMenu( add_control_filter_menu, u'Create' )
				#item.SetBitmap( ctg.ui.util.get_project_image( 'outliner_objset_add_16.png', as_bitmap = True ), wx.BITMAP_TYPE_ANY )


			else:
				# Create new/Rename/Delete
				item = wx.MenuItem( self, CMD_ID_CREATE_NEW, u'Create {0}'.format( '' ), wx.EmptyString, wx.ITEM_NORMAL )
				item.SetBitmap( ctg.ui.util.get_project_image( 'outliner_objset_add_16.png', as_bitmap = True ), wx.BITMAP_TYPE_ANY )
				item.Enable( True )
				self.AppendItem( item )

			if len( self.data_objs ) > 0:
				if self.node_type is ctg.ae2.ui.const.NODE_TYPE_ANIM_SET_TREE or self.node_type is ctg.ae2.ui.const.NODE_TYPE_ANIM_GROUP_TREE:
					item = wx.MenuItem( self, CMD_ID_CREATE_NEW_CHILD, u'Create Child {0}'.format( '' ), wx.EmptyString, wx.ITEM_NORMAL )
					item.SetBitmap( ctg.ui.util.get_project_image( 'outliner_objset_add_16.png', as_bitmap = True ), wx.BITMAP_TYPE_ANY )
					item.Enable( True )
					self.AppendItem( item )

				item = wx.MenuItem( self, CMD_ID_RENAME, u'Rename {0}'.format( '' ), wx.EmptyString, wx.ITEM_NORMAL )
				item.SetBitmap( ctg.ui.util.get_project_image( 'editAttributes_16.png', as_bitmap = True ), wx.BITMAP_TYPE_ANY )
				item.Enable( False )

				# Can't rename more than one item
				if len( self.data_objs ) == 1:
					item.Enable( False )

				item = wx.MenuItem( self, CMD_ID_DELETE, u'Delete {0}'.format(	'' ), wx.EmptyString, wx.ITEM_NORMAL )
				item.SetBitmap( ctg.ui.util.get_project_image( 'outliner_objset_delete_16.png', as_bitmap = True ), wx.BITMAP_TYPE_ANY )
				item.Enable( True )
				if len( self.data_objs ) > 0:
					self.AppendItem( item )


		# Create display sub-menu
		elif self.node_type is ctg.ae2.ui.const.NODE_TYPE_ANIM_CLIP:

			if self.selected_items:
				if isinstance( self.data_obj, ctg.ae2.core.data.Clip_Item ):
					workspace_dir = vlib.user.settings[ 'project_workspace_dir' ]
					current_workspace = os.path.basename( os.path.normpath ( workspace_dir ) )
					resource_workspace = workspace_dir + 'data\\'
					workspace_packages = vlib.package.get_package_info_dict( workspace_path = workspace_dir )

					resource_workspace = resource_workspace.lower( )

					try:
						resource = _resourcelib.get_file_info( self.data_obj.get_file_name_and_ext( ) )
					except RuntimeError:
						resource = None

					if resource:
						for package in workspace_packages.keys( ):
							if package in resource.full_local_filename:
								resource_package = package

					item_package_menu = wx.Menu( )
					item = wx.MenuItem( self, CMD_ID_ITEM_PACKAGE, str( resource_package ), wx.EmptyString, wx.ITEM_NORMAL )
					item.Enable( True )
					self.AppendItem( item )

					self.AppendSeparator( )

			if len( self.data_objs ) > 0:
				item = wx.MenuItem( self, CMD_ID_COPY_CLIP_PROPERTIES, u'Copy Properties', wx.EmptyString, wx.ITEM_NORMAL )
				item.SetBitmap( ctg.ui.util.get_project_image( 'outliner_objset_add_16.png', as_bitmap = True ), wx.BITMAP_TYPE_ANY )
				self.AppendItem( item )
				item.Enable( False )

				# Can't copy properties from more than one item
				if len( self.data_objs ) == 1:
					item.Enable( True )

				paste_item = wx.MenuItem( self, CMD_ID_PASTE_CLIP_PROPERTIES, u'Paste Properties', wx.EmptyString, wx.ITEM_NORMAL )
				paste_item.SetBitmap( ctg.ui.util.get_project_image( 'editAttributes_16.png', as_bitmap = True ), wx.BITMAP_TYPE_ANY )
				self.AppendItem( paste_item )
				paste_item.Enable( False )


				if self.clipboard_data:
					if len( self.clipboard_data ) > 0:
						paste_item.Enable( True )

				clear_item = wx.MenuItem( self, CMD_ID_CLEAR_CLIP_PROPERTIES, u'Clear All Properties', wx.EmptyString, wx.ITEM_NORMAL )
				clear_item.SetBitmap( ctg.ui.util.get_project_image( 'editAttributes_16.png', as_bitmap = True ), wx.BITMAP_TYPE_ANY )
				clear_item.Enable( True )
				self.AppendItem( clear_item )


		if self.node_type is ctg.ae2.ui.const.NODE_TYPE_ANIM_SET_TREE:

			# ADD GROUP MENU
			add_group_menu = wx.Menu( )
			self.add_group_dict = { }

			# only add groups that aren't in the animation set
			if self.data_obj:
				set_groups = self.data_obj.get_group_names( )
				sorted_group_names = sorted( doc.anim_group_collection.get_item_names( ) )
				for group_name in sorted_group_names:
					if not group_name in set_groups:
						group_index = wx.NewId( )
						item = wx.MenuItem( self, group_index, group_name, group_name )
						add_group_menu.AppendItem( item )
						self.add_group_dict[group_index] = group_name

				# only add the menu if there are items in it
				if len( self.add_group_dict ) > 0:
					self.AppendSeparator( )
					self.AppendSubMenu( add_group_menu, 'Add Group to Set' )

				# REMOVE GROUP MENU
				remove_group_menu = wx.Menu( )
				self.remove_group_dict = { }

				# only add groups that are in the animation set
				set_groups = self.data_obj.get_group_names( )
				sorted_group_names = sorted( doc.anim_group_collection.get_item_names( ) )
				for group_name in sorted_group_names:
					if group_name in set_groups:
						if group_name != 'Default':
							group_index = wx.NewId( )
							item = wx.MenuItem( self, group_index, group_name, group_name )
							remove_group_menu.AppendItem( item )
							self.remove_group_dict[group_index] = group_name

				# only add the menu if there are items in it
				if len( self.remove_group_dict ) > 0:
					self.AppendSubMenu( remove_group_menu, 'Remove Group from Set' )

		# Create Tag Association Item
		add_types = [ ctg.ae2.ui.const.NODE_TYPE_ANIM_CLIP, ctg.ae2.ui.const.NODE_TYPE_TAG_ACTION, ctg.ae2.ui.const.NODE_TYPE_TAG_STATE ]
		if self.node_type in add_types:
			if len( self.data_objs ) > 0:

				if self.node_type is ctg.ae2.ui.const.NODE_TYPE_ANIM_CLIP:
					self.AppendSeparator( )
					item = wx.MenuItem( self, CMD_ID_CRUNCH_CLIP, u'Crunch', wx.EmptyString, wx.ITEM_NORMAL )
					item.SetBitmap( ctg.ui.util.get_project_image( 'crunch_16.png', as_bitmap = True ), wx.BITMAP_TYPE_ANY )
					item.Enable( True )
					self.AppendItem( item )
					item = wx.MenuItem( self, CMD_ID_GENERATE_FOOTSTEP_TRIGGERS, u'Generate Footstep Triggers', wx.EmptyString, wx.ITEM_NORMAL )
					item.Enable( True )
					self.AppendItem( item )

				self.AppendSeparator( )
				item = wx.MenuItem( self, CMD_ID_ADD_TO_CATALOG, u'Add to Catalog', wx.EmptyString, wx.ITEM_NORMAL )
				item.SetBitmap( ctg.ui.util.get_project_image( 'outliner_objset_add_16.png', as_bitmap = True ), wx.BITMAP_TYPE_ANY )
				item.Enable( True )
				self.AppendItem( item )

				item = wx.MenuItem( self, CMD_ID_REMOVE_FROM_CATALOG, u'Remove from Catalog', wx.EmptyString, wx.ITEM_NORMAL )
				item.SetBitmap( ctg.ui.util.get_project_image( 'outliner_objset_delete_16.png', as_bitmap = True ), wx.BITMAP_TYPE_ANY )
				item.Enable( True )
				self.AppendItem( item )

			if self.GetMenuItemCount( ) != 0:
				self.AppendSeparator( )

			display_styles_menu = wx.Menu( )
			item = wx.MenuItem( self, CMD_ID_DISPLAY_ITEMS_ALL, u'All {0}s'.format( self.node_name ), wx.EmptyString, wx.ITEM_CHECK )
			display_styles_menu.AppendItem( item )
			item.Check( self.view.active_display_type == ctg.ae2.ui.const.DISPLAY_TYPE_ALL )

			item = wx.MenuItem( self, CMD_ID_DISPLAY_ITEMS_USED, u'Used {0}s'.format( self.node_name ), wx.EmptyString, wx.ITEM_CHECK )
			display_styles_menu.AppendItem( item )
			item.Check( self.view.active_display_type == ctg.ae2.ui.const.DISPLAY_TYPE_USED )

			item = wx.MenuItem( self, CMD_ID_DISPLAY_ITEMS_UNUSED, u'Unused {0}s'.format( self.node_name ), wx.EmptyString, wx.ITEM_CHECK )
			display_styles_menu.AppendItem( item )
			item.Check( self.view.active_display_type == ctg.ae2.ui.const.DISPLAY_TYPE_UNUSED )

			self.AppendSubMenu( display_styles_menu, 'Display' )

		self.AppendSeparator( )
		if self.GetMenuItemCount( ) > 0:
			self.SetTitle( self.display_name )


	def on_menu_clicked( self, event ):
		handled = super( Anim_Asset_Context_Menu, self ).on_menu_clicked( event )
		sender = event.GetId( )
		mouse_pos = wx.GetMouseState( ).GetPosition( )

		# get the document
		doc = AnimationEditor.get_active_document( )
		if not doc:
			return

		# Create New
		if sender == CMD_ID_CREATE_NEW:
			win = Floater_Dialog( self.view, self.data_objs, ctg.ae2.ui.const.ASSET_OPERATION_CREATE, mouse_pos,
			                      display_name = 'New {0}'.format( self.menu_title ), label_text = 'Create {0}'.format( self.menu_title ), node_type = self.node_type )
			win.Show()

		# Create New Child
		elif sender == CMD_ID_CREATE_NEW_CHILD:
			win = Floater_Dialog( self.view, self.data_objs, ctg.ae2.ui.const.ASSET_OPERATION_CREATE_CHILD, mouse_pos,
			                      display_name = 'New {0}'.format( self.menu_title ), label_text = 'Create Child {0}'.format( self.menu_title ), node_type = self.node_type )
			win.Show()

		elif sender == CMD_DELTA:
			win = Floater_Dialog( self.view, self.data_objs, ctg.ae2.ui.const.ASSET_OPERATION_CREATE_DELTA, mouse_pos,
			                      display_name = 'New {0}'.format( self.menu_title ), label_text = 'Create {0}'.format( self.menu_title ), node_type = self.node_type )
			win.Show()

		# Create New control filter Linear
		elif sender == CMD_LINEAR:
			win = Floater_Dialog( self.view, self.data_objs, ctg.ae2.ui.const.ASSET_OPERATION_CREATE_LINEAR, mouse_pos,
			                      display_name = 'New {0}'.format( self.menu_title ), label_text = 'Create {0}'.format( self.menu_title ), node_type = self.node_type )
			win.Show()

		# Create New control filter Cap
		elif sender == CMD_CAP:
			win = Floater_Dialog( self.view, self.data_objs, ctg.ae2.ui.const.ASSET_OPERATION_CREATE_CAP, mouse_pos,
				                   display_name = 'New {0}'.format( self.menu_title ), label_text = 'Create {0}'.format( self.menu_title ), node_type = self.node_type )
			win.Show()

		# Create New control filter Cap
		elif sender == CMD_ADD:
			win = Floater_Dialog( self.view, self.data_objs, ctg.ae2.ui.const.ASSET_OPERATION_CREATE_ADD, mouse_pos,
				                   display_name = 'New {0}'.format( self.menu_title ), label_text = 'Create {0}'.format( self.menu_title ), node_type = self.node_type )
			win.Show()

		# Rename
		elif sender == CMD_ID_RENAME:
			win = Floater_Dialog( self.view, self.data_objs, ctg.ae2.ui.const.ASSET_OPERATION_RENAME, mouse_pos,
			                      display_name = self.data_objs[0].get_name( ), label_text = 'Rename {0}'.format( self.menu_title ), node_type = self.node_type )
			win.Show()

		# Delete
		elif sender == CMD_ID_DELETE:
			win = Floater_Dialog( self.view, self.data_objs, ctg.ae2.ui.const.ASSET_OPERATION_DELETE, mouse_pos,
			                      display_name = self.data_objs[0].get_name( ), label_text = 'Delete {0}'.format( self.menu_title ), node_type = self.node_type )
			win.Show()

		elif sender == CMD_ID_COPY_RAD:
			if len( self.selected_items ):
				#Copy the data from the RAD const type
				copied_dict = { self.selected_items[ 0 ].data_obj.get_name( ) : self.selected_items[ 0 ].data_obj.get_xml( ) }
				ctg.ae2.core.ae_common_operations.copy( copied_dict,  ctg.ae2.ui.const.RIG_AUX )

		elif sender == CMD_ID_PASTE_RAD:
			#Get the copied data from clipboard based on the same RAD const type
			bones_list = [ ]
			stored_xmls = { }
			pasted_items = ctg.ae2.core.ae_common_operations.get_data_from_clipboard( ctg.ae2.ui.const.RIG_AUX )

			#Get the old item that was copied from the pasted data
			if pasted_items:
				old_item_name = pasted_items.keys( )[ 0 ]
				old_item = doc.rig_aux_data_collection.get_item_by_name( old_item_name )

				#Update the old item to make sure we are up-to-date before beginning
				old_item.update_rig_aux_data( old_item.get_rig_aux_data( ) )
				if old_item:
					#Get the old RAD item's xml, and create the new one
					old_item_data_xml = old_item.get_xml( )
					success, new_name = doc.rig_aux_data_collection.create( )

					#If it is successful at creating the new one, get the item itself and update it
					if success:
						new_aux_item = doc.rig_aux_data_collection.get_item_by_name( new_name )
						new_aux_item.update_rig_aux_data( new_aux_item.get_rig_aux_data( ) )

						#Create the list of bones we need to add to the new item
						for name in old_item_data_xml.keys( ):
							bones_list.append( name )

						#Add the bone to the new RAD item
						if bones_list:
							for bone in bones_list:
								new_aux_item.add_bone_by_name( bone )

								#Get the matching bone from the old and new RAD items
								new_bone = new_aux_item.get_bone( bone )
								old_bone = old_item.get_bone( bone )

								#Set the name of the bone to match (if you don't, it won't find the bone to add data to)
								new_bone.set_bone_name( old_bone.get_bone_name( ) )

								#Get all of the aux data from the old bone and add it to the matching bone on the new item bone
								for data in old_item.get_bone_aux_data( old_bone ):
									if old_bone.get_bone_name( ) == new_bone.get_bone_name( ):
										new_bone.add_bone_aux_data( data )
										stored_xmls[ data.get_name( ) ] = data.get_bone_aux_xml( )

										#Run the undoable to make sure the changes are pushed to the bone
										doc.undoable_modify_rig_aux_bone( new_aux_item.get_name( ), new_bone )

								#Iterate through the xml of the old item, and add the xml to the appropriate bone on the new RAD item
								if old_item_data_xml:
									for name, xml_string in old_item_data_xml.iteritems( ):
										for stored_bone, data in stored_xmls.iteritems( ):
											if stored_bone.lower( ) == name.lower( ) and stored_bone.lower( ) == str( new_bone.get_bone_name( ) ).lower( ):
												new_aux_data_obj = new_bone.get_bone_aux_data_list( )
												new_aux_data_obj[ 0 ].set_bone_aux_xml( data )
												new_aux_item.get_all_bones_aux_data( )[ name ] = data

						#Update the new RAD item for good measure
						new_aux_item.update_rig_aux_data( new_aux_item.get_rig_aux_data( ) )

						#Update all the views
						doc.rig_aux_data_collection.update_collection( )
						self.view.update_data_list( )
						doc.rig_bone_collection.update_collection( )
						doc.rig_bones_pane.refresh_ui( )

		elif sender == CMD_ID_COPY_CLIP_PROPERTIES:

			if self.data_objs:
				if len( self.data_objs ) == 1:
					data = self.data_objs[0].get_clip_prop_data( )
					self.view.copy( data, self.node_type  )

		elif sender == CMD_ID_PASTE_CLIP_PROPERTIES:
			if self.data_objs:
				pasted = False
				for obj in self.data_objs:
					pasted = obj.paste_properties( self.clipboard_data )

				if pasted:
					doc.event_manager.update_properties_pane( )


		elif sender == CMD_ID_CLEAR_CLIP_PROPERTIES:
			if self.data_objs:
				cleared = False
				for obj in self.data_objs:
					cleared = obj.clear_all_properties( )

				if cleared:
					doc.event_manager.update_properties_pane( )

		# Crunch the clip
		elif sender == CMD_ID_CRUNCH_CLIP:

			if self.data_objs:
					self.view.crunch( self.data_objs )


		# Auto generate footstep triggers for the clips
		elif sender == CMD_ID_GENERATE_FOOTSTEP_TRIGGERS:
		
			if self.data_objs:
				for obj in self.data_objs:
					obj.generateFootstepTriggers(  )

					
		# Command to Remove TAG or CLIP from the Active Animation Set/Group, Create Tag Association
		elif sender == CMD_ID_REMOVE_FROM_CATALOG:
			print 'Remove tag Association: {0}'.format( sender )

			if self.data_objs:
				#for obj in sel_objs:
				doc.event_manager.post_tag_association_deleted_event( self.data_objs )


		# Command to Add TAG or CLIP to the Active Animation Set/Group, Create Tag Association
		elif sender == CMD_ID_ADD_TO_CATALOG:
			print 'Create tag Association: {0}'.format( sender )

			# get the selected data objects
			if self.data_objs:

				# set the current tag type
				active_tag_tab = doc.active_tag_type

				# determine which tag association tab to open based on the whether it is a tag action or state
				if self.node_type is ctg.ae2.ui.const.NODE_TYPE_TAG_STATE:
					active_tag_tab = ctg.ae2.ui.const.NODE_TYPE_TAG_STATE
				elif self.node_type is ctg.ae2.ui.const.NODE_TYPE_TAG_ACTION:
					active_tag_tab = ctg.ae2.ui.const.NODE_TYPE_TAG_ACTION

				#for obj in sel_objs:
				# post the event for each object
				doc.event_manager.post_tag_association_created_event( self.data_objs, active_tag_type = active_tag_tab, add_to_catelog = True )

		elif sender in self.add_group_dict:
			event_obj = event.GetEventObject( )
			if event_obj:
				# set the new selection
				group_name = self.add_group_dict.get( sender )
				update_doc = event_obj.data_obj.add_group( group_name )
				if update_doc:
					#Make sure there is a lister tree for the animation sets, as well as the pane
					animation_sets_pane = ctg.ae2.ui.panes.animation_sets.Anim_Sets_Lister_Tree( doc.animation_sets_pane )
					if animation_sets_pane and doc.animation_sets_pane:
						#Updates to animation sets pane as well
						doc.animation_sets_pane.refresh_ui( )
						self.view.update_data_list( )
						doc.set_collection.update_collection( )

		elif sender in self.remove_group_dict:
			event_obj = event.GetEventObject( )
			if event_obj:
				# update the selection
				group_name = self.remove_group_dict.get( sender )
				update_doc = event_obj.data_obj.remove_group( group_name )
				if update_doc:
					#Make sure there is a lister tree for the animation sets, as well as the pane
					animation_sets_pane = ctg.ae2.ui.panes.animation_sets.Anim_Sets_Lister_Tree( doc.animation_sets_pane )
					if animation_sets_pane and doc.animation_sets_pane:
						#Updates to animation sets pane as well
						doc.animation_sets_pane.refresh_ui( )
						self.view.update_data_list( )
						doc.set_collection.update_collection( )

		elif sender == CMD_ID_DISPLAY_ITEMS_ALL:
			event_obj = event.GetEventObject( )
			if event_obj:
				self.view.set_display_type( ctg.ae2.ui.const.DISPLAY_TYPE_ALL )

		elif sender == CMD_ID_DISPLAY_ITEMS_USED:
			event_obj = event.GetEventObject( )
			if event_obj:
				self.view.set_display_type( ctg.ae2.ui.const.DISPLAY_TYPE_USED )

		elif sender == CMD_ID_DISPLAY_ITEMS_UNUSED:
			event_obj = event.GetEventObject( )
			if event_obj:
				self.view.set_display_type( ctg.ae2.ui.const.DISPLAY_TYPE_UNUSED )

		else:
			pass


class Asset_Manager_Status_Bar( wx.StatusBar ):
	def __init__( self, parent ):
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


	def OnSize( self, evt ):
		self.Reposition( )
		self.size_changed = True


	def OnIdle( self, evt ):
		if self.size_changed:
			self.Reposition( )


	def Reposition( self ):
		# HelpLink
		rect = self.GetFieldRect( 1 )
		self.helplink.SetPosition( ( rect.x + 2, rect.y + 4 ) )

		self.size_changed = False


	def set_status( self, msg ):
		self.SetStatusText( msg, 0 )


	def clear_status( self ):
		self.set_status( u'' )


class Parent_Item( vlib.types.Base_Parent ):
	def __init__( self, data_obj, children = [ ] ):
		self.needs_recollect = False
		super( Parent_Item, self ).__init__( self, children = children )
		self.data_obj = data_obj

		if isinstance( data_obj, AnimationEditor.ae_animation_trigger ):
			self.display_name = '{0} ({1})'.format( data_obj.get_name( ), data_obj.get_clip_name( ) )

		else:
			self.display_name = data_obj.get_name( )

	def _get_item_name( self, item ):
		if isinstance( item, Parent_Item ):
			val = item.data_obj.get_name( ).lower( )
		else:
			val = item.get_name( ).lower( )

		return val

	def _sort_compare( self, a, b ):
		a_name = self._get_item_name( a )
		b_name = self._get_item_name( b )

		result = cmp( a_name, b_name )

		return result

	def get_display_name( self ):
		return self.data_obj.get_name( ).lower( )


class Asset_Manager_Lister_Tree( ctg.ae2.ui.lister.Anim_Lister_Tree_Base ):
	def __init__( self, *args, **kwargs ):
		self.node_type             = ctg.ae2.ui.const.NODE_TYPE_ANIM_CLIP
		self.active_display_type   = ctg.ae2.ui.const.DISPLAY_TYPE_ALL

		super( Asset_Manager_Lister_Tree, self ).__init__(  *args, **kwargs )

		self.Bind( vlib.ui.lister_lib2.events.EVT_SELECT_MODIFIED, self.on_item_selection_changed )

		self.active_collection = None
		self.parent            = self.GetParent( )
		self.selected_items    = [ ]


	def on_context_menu( self, click_pos, item ):
		menu = Anim_Asset_Context_Menu( self, item )
		self.PopupMenu( menu )
		menu.Destroy( )

	def set_display_type( self, val ):
		self.active_display_type = val
		self.update_data_list( )


	def can_display_node( self, item ):

		can_display = True
		if self.node_type in [ ctg.ae2.ui.const.NODE_TYPE_ANIM_CLIP, ctg.ae2.ui.const.NODE_TYPE_TAG_ACTION, ctg.ae2.ui.const.NODE_TYPE_TAG_STATE ]:
			if item:
				can_display =  True
				if self.active_display_type == ctg.ae2.ui.const.DISPLAY_TYPE_USED:
					if not item.is_used( ):
						can_display =  False

				elif self.active_display_type == ctg.ae2.ui.const.DISPLAY_TYPE_UNUSED:
					if item.is_used( ):
						can_display =  False

		return can_display


	def on_item_selection_changed( self, event ):
		doc = AnimationEditor.get_active_document( )

		sel_objs = self.get_selection_manager( ).get_selection( )
		if sel_objs:
			self.post_item_select_event( [ sel_objs[0].data_obj ] )


	def get_items_from_data_objs( self, items ):
		items = [ ]
		if self.active_collection:
			for item in self.selected_items:
				node = self.active_collection.get_item_by_name( item.get_name( ) )
				if node and node not in items:
					items.append( node )

		return items


	def update_selection( self ):
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		data_objs = doc.selection_manager.get_selected_objects( )
		if data_objs:
			data_obj = data_objs[0]
			collection = self.get_item_collection( ).get_items_flat( )
			sel = None
			for obj in collection:
				if obj.data_obj == data_objs[0]:
					sel = obj

			if sel:
				self.restore_selection( [sel], post_event = False )


	def update_data_list( self, new_items=None, clear_items = False ):
		doc = AnimationEditor.get_active_document( )
		self.active_collection = self.get_active_collection( )
		if new_items:
			if isinstance( new_items[0], AnimationEditor.ae_named_value ):
				self.active_collection = doc.named_values_collection
			elif isinstance( new_items[0], AnimationEditor.ae_animation_trigger ):
				self.active_collection = new_items

		items             = [ ]
		restore_sel_items = [ ]
		if self.active_collection:
			if hasattr( self.active_collection, 'update_collection' ):
				self.active_collection.update_collection( clear_items = clear_items )
				objs = self.active_collection.get_items( )

			if new_items:
				objs = set( new_items )

			if objs:
				for obj in objs:
					if self.can_display_node( obj ):
						obj_parent = Parent_Item( obj, children = [] )

						if self.selected_items:
							for item in self.selected_items:
								if item and item.get_name( ) == obj.get_name( ):
									restore_sel_items.append( obj_parent )

						items.append( obj_parent )

		#if new_items:
		#	items = new_items

		self.set_item_collection( items, use_timer = False, sort=True, immediate = True )
		#restore selection
		self.restore_selection( restore_sel_items )


	def post_item_select_event( self, data_objs ):

		# get the document
		doc = AnimationEditor.get_active_document( )

		self.selected_items = data_objs

		if isinstance( data_objs[0], ctg.ae2.core.data.Clip_Item ):
			doc.event_manager.post_clip_select_event( data_objs )

		elif isinstance( data_objs[0], AnimationEditor.ae_animation_trigger ):
			clips = [ obj.get_clip_name( ) for obj in data_objs ]
			data_objs = [ doc.clip_collection.get_item_by_name( clip ) for clip in clips ]
			doc.event_manager.post_clip_select_event( data_objs )

		elif isinstance( data_objs[0], ctg.ae2.core.data.Set_Item ):
			doc.event_manager.post_set_select_event( data_objs, owner = ctg.ae2.ui.const.PANE_ID_ANIM_ASSET_MANAGER )

		elif isinstance( data_objs[0], ctg.ae2.core.data.Group_Item ):
			doc.event_manager.post_group_select_event( data_objs, owner = ctg.ae2.ui.const.PANE_ID_ANIM_ASSET_MANAGER )

		elif isinstance( data_objs[0], ctg.ae2.core.data.State_Tag_Item ):
			doc.event_manager.post_state_tag_select_event( data_objs )

		elif isinstance( data_objs[0], ctg.ae2.core.data.Action_Tag_Item ):
			doc.event_manager.post_action_tag_select_event( data_objs )

		elif isinstance( data_objs[0], ctg.ae2.core.data.State_Machine_Item ):
			doc.event_manager.post_state_machine_select_event( data_objs )

		elif isinstance( data_objs[0], ctg.ae2.core.data.Blend_Tree_Item ):
			doc.event_manager.post_blend_tree_select_event( data_objs )

		elif isinstance( data_objs[0], ctg.ae2.core.data.Control_Filter_Item ):
			doc.event_manager.post_control_filter_select_event( data_objs )

		elif isinstance( data_objs[0], ctg.ae2.core.data.Control_Parameter_Item ):
			doc.event_manager.post_control_parameter_select_event( data_objs )

		elif isinstance( data_objs[0], ctg.ae2.core.data.Modifier_Item ):
			doc.event_manager.post_modifier_select_event( data_objs )

		elif isinstance( data_objs[0], ctg.ae2.core.data.Rig_Aux_Data_Item ):
			doc.event_manager.post_rig_aux_data_select_event( data_objs )

		self.parent.set_status_message( )


	def get_active_collection( self ):

		collection = None
		# get the document
		doc = AnimationEditor.get_active_document( )
		if self.node_type == ctg.ae2.ui.const.NODE_TYPE_ANIM_CLIP:
			collection = doc.clip_collection
		elif self.node_type == ctg.ae2.ui.const.NODE_TYPE_TAG_STATE:
			collection = doc.state_tag_collection
		elif self.node_type == ctg.ae2.ui.const.NODE_TYPE_TAG_ACTION:
			collection = doc.action_tag_collection
		elif self.node_type == ctg.ae2.ui.const.NODE_TYPE_ANIM_SET_TREE:
			collection = doc.set_collection
		elif self.node_type == ctg.ae2.ui.const.NODE_TYPE_ANIM_GROUP_TREE:
			collection = doc.anim_group_collection
		elif self.node_type == ctg.ae2.ui.const.NODE_TYPE_STATE_MACHINE:
			collection = doc.state_machine_collection
		elif self.node_type == ctg.ae2.ui.const.NODE_TYPE_BLEND_TREE:
			collection = doc.blend_tree_collection
		elif self.node_type == ctg.ae2.ui.const.NODE_TYPE_CONTROL_FILTER:
			collection = doc.control_filter_collection
		elif self.node_type == ctg.ae2.ui.const.NODE_TYPE_CONTROL_PARAMETER:
			collection = doc.control_parameter_collection
		elif self.node_type == ctg.ae2.ui.const.NODE_TYPE_MODIFIER:
			collection = doc.modifier_collection
		elif self.node_type == ctg.ae2.ui.const.NODE_TYPE_RIG_AUX_DATA:
			collection = doc.rig_aux_data_collection

		return collection


	def on_active_clip_update( self, event ):
		# set the tabs to anim clip
		if not self.GetParent( ).tabs.Selection is 0:

			# set the current node_type to anim clip
			self.node_type = ctg.ae2.ui.const.NODE_TYPE_ANIM_CLIP

			# set the proper tab
			self.GetParent( ).tabs.SetSelection( 0 )

		self.update_selected_items_from_event( event )

		event.Skip( )


	def set_display_type( self, val ):
		self.active_display_type = val
		# refresh the lister
		self.update_data_list( )


	def restore_selection( self, items, post_event = True ):
		self.get_selection_manager( ).set_selection( self, items, post_event = post_event )
		if items:
			self.scroll_to_item( items[-1] )


	def on_anim_set_renamed( self, event ):

		if self.node_type is ctg.ae2.ui.const.NODE_TYPE_ANIM_SET_TREE:
			self.update_selected_items_from_event( event )

		event.Skip( )


	def update_selected_items_from_event( self, event ):
		doc = AnimationEditor.get_active_document( )
		if not doc or not event:
			return

		self.selected_items = event.get_data_objs( )

		# refresh the lister
		self.update_data_list( )


	def on_anim_set_created( self, event ):
		if self.node_type is ctg.ae2.ui.const.NODE_TYPE_ANIM_SET_TREE:
			self.update_selected_items_from_event( event )

		event.Skip( )


	def on_anim_group_created( self, event ):

		if self.node_type is ctg.ae2.ui.const.NODE_TYPE_ANIM_GROUP_TREE:
			self.update_selected_items_from_event( event )

		event.Skip( )


	def on_anim_group_renamed( self, event ):

		if self.node_type is ctg.ae2.ui.const.NODE_TYPE_ANIM_GROUP_TREE:
			self.update_selected_items_from_event( event )

		event.Skip( )


	def on_action_tag_created( self, event ):

		if self.node_type is ctg.ae2.ui.const.NODE_TYPE_TAG_ACTION:
			self.update_selected_items_from_event( event )

		event.Skip( )


	def on_action_tag_renamed( self, event ):

		if self.node_type is ctg.ae2.ui.const.NODE_TYPE_TAG_ACTION:
			self.update_selected_items_from_event( event )

		event.Skip( )


	def on_state_tag_created( self, event ):

		if self.node_type is ctg.ae2.ui.const.NODE_TYPE_TAG_STATE:
			self.update_selected_items_from_event( event )

		event.Skip( )


	def on_state_tag_renamed( self, event ):
		if self.node_type is ctg.ae2.ui.const.NODE_TYPE_TAG_STATE:
			self.update_selected_items_from_event( event )

		event.Skip( )


	def on_tag_modified( self, event ):

		if self.node_type is ctg.ae2.ui.const.NODE_TYPE_TAG_STATE or self.node_type is ctg.ae2.ui.const.NODE_TYPE_TAG_ACTION:
			self.update_selected_items_from_event( event )

		event.Skip( )


	def on_state_machine_created( self, event ):
		self.update_selected_items_from_event( event )

		event.Skip( )


	def on_state_machine_renamed( self, event ):
		self.update_selected_items_from_event( event )

		event.Skip( )


	def on_state_machine_deleted( self, event ):
		self.update_selected_items_from_event( event )

		event.Skip( )


	def on_blend_tree_created( self, event ):
		self.update_selected_items_from_event( event )

		event.Skip( )


	def on_blend_tree_renamed( self, event ):
		self.update_selected_items_from_event( event )

		event.Skip( )


	def on_blend_tree_deleted( self, event ):
		self.update_selected_items_from_event( event )

		event.Skip( )


	def on_control_filter_renamed( self, event ):
		self.update_selected_items_from_event( event )

		event.Skip( )


	def on_control_parameter_renamed( self, event ):
		self.update_selected_items_from_event( event )

		event.Skip( )



def update_graph_parameters(doc, graphs, old_param, new_param):
	if doc == None or len(graphs) <= 0:
		return

	doc.set_hide_file_locked_messages(True)

	obj_server =  vlib.ui.node_graph.document.Node_Graph_Object_Manager_Server()

	# vlib.enumerations.get_enum_type( "resource:animation_control_parameter" ).clear_choices( )
	vlib.enumerations.get_enum_type( "animation_control_parameters: " ).clear_choices( )
	# vlib.enumerations.get_enum_type( "resource:animation_control_filter" ).clear_choices( )
	vlib.enumerations.get_enum_type( "animation_control_filters: " ).clear_choices( )
	# vlib.enumerations.get_enum_type( "resource:animation_control_filter,animation_control_parameter" ).clear_choices( )
	vlib.enumerations.get_enum_type( "animation_controls: " ).clear_choices( )

	# get graph editors here and pass in
	state_machine_graph = ctg.ae2.node_graph.ae_state_machine_editor.AE_State_Machine_Graph(doc.node_graph_panel.state_machine, obj_server)
	blend_tree_graph = ctg.ae2.node_graph.ae_blend_tree_editor.AE_Blend_Tree_Graph(doc.node_graph_panel.blend_tree, obj_server)

	progressMax = len(graphs)
	dialog = wx.ProgressDialog("Renaming Controls", "Time remaining", progressMax, style=wx.PD_ELAPSED_TIME | wx.PD_REMAINING_TIME )
	count = 0
	dialog.Update(count)

	for node_graph_name in graphs:

		doc.node_graph_panel.blend_tree.set_disable_undo(True)
		doc.node_graph_panel.state_machine.set_disable_undo(True)

		state_machine_graph.clear_scene_state()
		blend_tree_graph.clear_scene_state()

		ae_node_graph_obj = doc.get_node_graph( node_graph_name )
		graph_string = ae_node_graph_obj.get_graph_json()

		if graph_string == "":
			continue

		root_el = xml.etree.cElementTree.fromstring( graph_string )

		graph_type = ae_node_graph_obj.get_node_graph_type()
		mark_dirty = True
		if graph_type == ctg.ae2.node_graph.constants.BLEND_TREE_TYPE:
			blend_tree_graph.create_and_add_objects_from_string(graph_string)
			blend_tree_graph.name = node_graph_name

			# find and replace old param with new one
			for node in blend_tree_graph.get_nodes( ):
				if isinstance( node, vlib.ui.node_graph.node_variable.Enum_Node ):
					if node.name == 'Control' and node.get_value():
						if node.get_value( ) == old_param:
							node.set_value(new_param)
				elif isinstance( node, ctg.ae2.node_graph.ae_blend_tree_nodes.Control_Parameter_Node ):
					if node.name == old_param:
						node.name = new_param
						control_param = node.get_child_object( name = 'Control', recursive = True )
						control_param.set_value(new_param)

			blend_tree_graph.regenerate_dependencies_for_editor_side()


			graph_state = blend_tree_graph.get_graph_state_string( )
			ae_node_graph_obj.set_graph_json( graph_state )

			references = doc.get_node_graph_references(node_graph_name)
			export_root, export_errors = ctg.ae2.node_graph.export.export_blend_tree_reflection_xml( blend_tree_graph, references)
			export_xml = vlib.prettyxml.tostringpretty( export_root, method = 'text' )
			ae_node_graph_obj.set_modified(True)

			doc.set_node_graph_saved_and_export_xml(node_graph_name, graph_state, export_xml, export_errors, True)
			#blend_tree_modified(doc, node_graph_name, node_graph_name)

		elif graph_type == ctg.ae2.node_graph.constants.STATE_MACHINE_TYPE:
			state_machine_graph.create_and_add_objects_from_string(graph_string)
			state_machine_graph.name = node_graph_name

			# find and replace old param with new one
			for node in state_machine_graph.get_nodes( ):
				if isinstance( node, vlib.ui.node_graph.node_variable.String_Node ):
					if node.name == "Conditional Expression":
						expression = doc.replace_parameter_in_expression( new_param, old_param, node.get_value() )
						node.set_value(expression)

					if node.name == "Cancel Conditional Expression":
						expression = doc.replace_parameter_in_expression( new_param, old_param, node.get_value() )
						node.set_value(expression)

			state_machine_graph.regenerate_dependencies_for_editor_side()

			graph_state = state_machine_graph.get_graph_state_string( )

			ae_node_graph_obj.set_graph_json( graph_state )
			ae_node_graph_obj.set_modified(True)

			references = doc.get_node_graph_references(node_graph_name)
			export_root, export_errors = ctg.ae2.node_graph.export.export_state_machine_reflection_xml( state_machine_graph, references)
			export_xml = vlib.prettyxml.tostringpretty( export_root, method = 'text' )
			ae_node_graph_obj.set_modified(True)

			doc.set_node_graph_saved_and_export_xml(node_graph_name, graph_state, export_xml, export_errors, True)
			#state_machine_modified(doc, node_graph_name, node_graph_name)

		count = count + 1
		#dialog.Update(count)

	if doc.control_is_filter(new_param):
		control_filter_modified(doc, new_param, new_param)
	elif doc.control_is_parameter(new_param):
		control_parameter_modified(doc, new_param, new_param)


	doc.node_graph_panel.blend_tree.set_disable_undo(False)
	doc.node_graph_panel.state_machine.set_disable_undo(False)

	#dialog.Destroy()
	doc.set_hide_file_locked_messages(False)


def process_graph_rename(doc, graphs, old_name, new_name):
	if doc == None or len(graphs) <= 0:
		return

	doc.set_hide_file_locked_messages(True)

	#clear enums of graphs so it gets updated list
	# vlib.enumerations.get_enum_type( "resource:animation_blend_trees" ).clear_choices( )
	vlib.enumerations.get_enum_type( "animation_blend_trees: " ).clear_choices( )
	# vlib.enumerations.get_enum_type( "resource:animation_state_machine" ).clear_choices( )
	vlib.enumerations.get_enum_type( "animation_state_machines: " ).clear_choices( )
	# vlib.enumerations.get_enum_type( "resource:animation_blend_tree,animation_state_machine" ).clear_choices( )
	vlib.enumerations.get_enum_type( "animation_node_graphs: " ).clear_choices( )

	current_graph = doc.node_graph_panel.get_active_node_graph_name( )
	obj_server =  vlib.ui.node_graph.document.Node_Graph_Object_Manager_Server()

	# get graph editors here and pass in
	state_machine_graph = ctg.ae2.node_graph.ae_state_machine_editor.AE_State_Machine_Graph(doc.node_graph_panel.state_machine, obj_server)
	blend_tree_graph = ctg.ae2.node_graph.ae_blend_tree_editor.AE_Blend_Tree_Graph(doc.node_graph_panel.blend_tree, obj_server)

	progressMax = len( graphs )
	#dialog = wx.ProgressDialog("Renaming graph", "Time remaining", progressMax, style=wx.PD_ELAPSED_TIME | wx.PD_REMAINING_TIME)
	#count = 0
	#dialog.Update(count)

	for node_graph_name in graphs:

		doc.node_graph_panel.blend_tree.set_disable_undo(True)
		doc.node_graph_panel.state_machine.set_disable_undo(True)

		state_machine_graph.clear_scene_state()
		blend_tree_graph.clear_scene_state()

		ae_node_graph_obj = doc.get_node_graph( node_graph_name )
		graph_string = ae_node_graph_obj.get_graph_json()

		if graph_string == "":
			continue

		graph_type = ae_node_graph_obj.get_node_graph_type()
		mark_dirty = True
		if graph_type == ctg.ae2.node_graph.constants.BLEND_TREE_TYPE:
			blend_tree_graph.create_and_add_objects_from_string(graph_string)
			blend_tree_graph.name = node_graph_name

			# find and replace old param with new one
			for node in blend_tree_graph.get_nodes( ):
				if node.name == "Node Graph":
					if node.get_value() == old_name:
						node.set_value(new_name)

			blend_tree_graph.regenerate_dependencies_for_editor_side()

			graph_state = blend_tree_graph.get_graph_state_string( )
			ae_node_graph_obj.set_graph_json( graph_state )

			references = doc.get_node_graph_references(node_graph_name)
			export_root, export_errors = ctg.ae2.node_graph.export.export_blend_tree_reflection_xml( blend_tree_graph, references)
			export_xml = vlib.prettyxml.tostringpretty( export_root, method = 'text' )
			ae_node_graph_obj.set_modified(True)

			doc.set_node_graph_saved_and_export_xml(node_graph_name, graph_state, export_xml, export_errors, True)
			#blend_tree_modified(doc, node_graph_name, node_graph_name)

		elif graph_type == ctg.ae2.node_graph.constants.STATE_MACHINE_TYPE:
			state_machine_graph.create_and_add_objects_from_string(graph_string)
			state_machine_graph.name = node_graph_name

			# find and replace old param with new one
			for node in state_machine_graph.get_nodes( ):
				if node.name == "Child Node Graph":
					if node.get_value() == old_name:
						node.set_value(new_name)

			state_machine_graph.regenerate_dependencies_for_editor_side()

			graph_state = state_machine_graph.get_graph_state_string( )
			ae_node_graph_obj.set_graph_json( graph_state )
			ae_node_graph_obj.set_modified(True)

			references = doc.get_node_graph_references(node_graph_name)
			export_root, export_errors = ctg.ae2.node_graph.export.export_state_machine_reflection_xml( state_machine_graph, references)
			export_xml = vlib.prettyxml.tostringpretty( export_root, method = 'text' )
			ae_node_graph_obj.set_modified(True)

			doc.set_node_graph_saved_and_export_xml( node_graph_name, graph_state, export_xml, export_errors, True )
			#state_machine_modified(doc, node_graph_name, node_graph_name)

		#count = count + 1
		#dialog.Update(count)

	if doc.is_blend_tree(old_name):
		blend_tree_modified(doc, old_name, new_name)
	elif doc.is_state_machine(old_name):
		state_machine_modified(doc, old_name, new_name)

	if doc.node_graph_panel.blend_tree_name != '' and doc.node_graph_panel.blend_tree_name != None:
		doc.node_graph_panel.load_node_graph( doc.node_graph_panel.blend_tree_name )

	if doc.node_graph_panel.state_machine_name != '' and doc.node_graph_panel.state_machine_name != None:
			doc.node_graph_panel.load_node_graph( doc.node_graph_panel.state_machine_name )

	if old_name == current_graph:
		doc.node_graph_panel.load_node_graph( new_name )

	if current_graph in graphs:
		doc.node_graph_panel.load_node_graph( current_graph )

	doc.node_graph_panel.blend_tree.set_disable_undo(False)
	doc.node_graph_panel.state_machine.set_disable_undo(False)

	#dialog.Destroy()
	doc.set_hide_file_locked_messages(False)



class Asset_Manager_Pane( wx.Panel ):
	PANE_ID 		= ctg.ae2.ui.const.PANE_ID_ANIM_ASSET_MANAGER
	PANE_TITLE 	= ctg.ae2.ui.const.PANE_TITLE_ANIM_ASSET_MANAGER

	def __init__( self, parent ):
		wx.Panel.__init__( self, parent )

		# BUILD UI
		#================================
		self.main_sizer 		  = wx.BoxSizer( wx.VERTICAL )
		sizer_toolbar 	        = wx.BoxSizer( wx.HORIZONTAL )
		sizer_tabs 		        = wx.BoxSizer( wx.HORIZONTAL )
		self.active_node_type  = ctg.ae2.ui.const.NODE_TYPE_ANIM_CLIP

		self.parent = parent

		self.statusbar = Asset_Manager_Status_Bar( self )
		self.lister = Asset_Manager_Lister_Tree( self, item_height = 20 )

		# Search Field
		self.search_ctrl_toolbar = vlib.ui.widgets.text_controls.Search_Control( self, width = 300 )
		self.keyword_help_toolbar = vlib.ui.widgets.buttons.Bitmap_Toggle_Button(
		                                                                                         self,
		                                                                                         size=(22, 22),
		                                                                                         bitmap = ctg.icons.get_icon( 'help_16' ),
		                                                                                         press_color=None)

		sizer_toolbar.AddSpacer( 2 )
		sizer_toolbar.Add( self.search_ctrl_toolbar, 1, wx.ALIGN_CENTER_VERTICAL | wx.EXPAND, 2 )
		sizer_toolbar.AddStretchSpacer( 12 )
		sizer_toolbar.Add( self.keyword_help_toolbar, 1, wx.ALIGN_CENTER_VERTICAL | wx.EXPAND, 3 )
		sizer_toolbar.AddStretchSpacer( 15 )

		# Noteboook Tabs
		self.tab_filter_dict = { \
		   0 : [ 'Clips',					 ctg.ae2.ui.const.NODE_TYPE_ANIM_CLIP ],
		   1:  [ 'Triggers',          ctg.ae2.ui.const.NODE_TYPE_ANIM_TRIGGER ],
		   2 : [ 'States',				 ctg.ae2.ui.const.NODE_TYPE_TAG_STATE ],
		   3 : [ 'Actions',				 ctg.ae2.ui.const.NODE_TYPE_TAG_ACTION ],
		   4:  [ 'Named Values',  ctg.ae2.ui.const.NODE_TYPE_ANIM_NAMED_VALUE ],
		   5 : [ 'Sets',					 ctg.ae2.ui.const.NODE_TYPE_ANIM_SET_TREE ],
		   6 : [ 'Groups',				 ctg.ae2.ui.const.NODE_TYPE_ANIM_GROUP_TREE ],
		   7 : [ 'State Machines',		 ctg.ae2.ui.const.NODE_TYPE_STATE_MACHINE ],
		   8 : [ 'Blend Trees',			 ctg.ae2.ui.const.NODE_TYPE_BLEND_TREE ],
		   9 : [ 'Control Filters',	 ctg.ae2.ui.const.NODE_TYPE_CONTROL_FILTER ],
		   10 : [ 'Control Params',		 ctg.ae2.ui.const.NODE_TYPE_CONTROL_PARAMETER ],
		   11 : [ 'Rig Auxiliary Data', ctg.ae2.ui.const.NODE_TYPE_RIG_AUX_DATA ],
		   12 : [ 'Modifiers',         ctg.ae2.ui.const.NODE_TYPE_MODIFIER ],
		}

		self.tabs = wx.Notebook( self, -1, size = ( -1, 22 ), style = wx.BK_DEFAULT )

		for label, type_id in self.tab_filter_dict.values( ):
			self.tabs.AddPage( wx.Panel( self.tabs, -1 ), label )

		sizer_tabs.Add( self.tabs, 1, wx.EXPAND | wx.TOP | wx.LEFT, 2 )

		self.main_sizer.AddSpacer( 5 )
		self.main_sizer.Add( sizer_toolbar, 0, wx.EXPAND, 2 )
		self.main_sizer.Add( sizer_tabs, 0, wx.EXPAND, 0 )
		self.main_sizer.Add( self.lister, 1, wx.EXPAND, 0 )
		self.main_sizer.Add( self.statusbar, 0, wx.EXPAND, 0 )

		self.SetSizer( self.main_sizer )
		self.Layout( )

		bg_color = wx.SystemSettings.GetColour( wx.SYS_COLOUR_3DFACE )
		self.SetBackgroundColour( bg_color )

		self.last_position = self.GetPosition( )

		# End Interior --------------------------------------------------------------------------------------------------
		self.tabs.Bind( wx.EVT_NOTEBOOK_PAGE_CHANGED, self.on_tab_changed )
		self.keyword_help_toolbar.Bind( wx.EVT_BUTTON, self.on_display_keyword_help )
		self.Bind( vlib.ui.widgets.text_controls.EVT_SEARCH, self.lister.update_search_filter )

		#self.Bind( ctg.ae2.ui.events.EVT_AE_KEYWORD_DISPLAY, self._on_display_keyword_help )

		#self.Bind( wx.EVT_WINDOW_DESTROY, self._on_destroy )

		self.refresh_ui( )


	def on_tab_changed( self, event ):
		doc = AnimationEditor.get_active_document( )
		tab_id = event.GetSelection( )
		self.active_node_type = self.tab_filter_dict[ tab_id ][ 1 ]

		items = None

		if self.active_node_type == ctg.ae2.ui.const.NODE_TYPE_ANIM_NAMED_VALUE:
			named_values = None
			named_values_names = None

			all_sets = doc.get_anim_set_names( )
			named_values = [ ]
			named_values_names = [ ]

			for anim_set in all_sets:
				set_obj = doc.set_collection.get_item_by_name( anim_set )
				for anim_group in set_obj.get_group_names( ):
					n_val = doc.get_anim_set_named_values( anim_set, anim_group )
					for val in n_val:
						if val not in named_values and val.get_name( ) not in named_values_names:
							named_values.append( val )
							named_values_names.append( val.get_name( ) )

			items = named_values

		elif self.active_node_type == ctg.ae2.ui.const.NODE_TYPE_ANIM_TRIGGER:
			triggers = [ ]
			items = [ ]

			trigger_items = doc.clip_collection.get_all_triggers( )

			for trigger in trigger_items:
				triggers.append( trigger )

			if triggers:
				items = [ trig for trig in triggers if trig not in items ]

		self.lister.node_type = self.active_node_type
		self.lister.selected_items = [ ]
		self.lister.update_data_list( new_items= items )

		self.set_status_message( )

		self.main_sizer.Layout( )
		event.Skip( )


	def set_status_message( self ):
		# get the document
		doc = AnimationEditor.get_active_document( )
		if not doc:
			return

		data_objs = doc.selection_manager.get_selected_objects( )
		if data_objs:
			if len( data_objs ) == 1 and hasattr( data_objs[0], 'get_name' ):
				self.statusbar.set_status( 'Selected: {0}'.format( data_objs[0].get_name( ) ))
			else:
				self.statusbar.clear_status( )
		else:
			self.statusbar.clear_status( )


	def update_selection( self ):
		self.lister.update_selection( )


	def refresh_ui( self, clear_items = False ):

		tab_id = self.tabs.GetSelection()
		self.active_node_type = self.tab_filter_dict[ tab_id ][ 1 ]
		self.lister.update_data_list( clear_items = clear_items )


	def _on_destroy( self, event ):
		doc = AnimationEditor.get_active_document( )
		if not doc:
			return

		self.keyword_help_toolbar.Close( )
		self.keyword_help_toolbar.Destroy( )

		self.Unbind( ctg.ae2.ui.events.EVT_AE_KEYWORD_DISPLAY )
		doc.event_manager.unregister_control(self)

		if hasattr( doc, 'editor' ):
			del( doc.editor )

	def on_display_keyword_help( self, event ):
		if self.keyword_help_toolbar:
			dialog_info = "\n '+': This keyword is used to add a word to your search. It will make sure that \n"\
				                    "the word is taken into account when searching for the item you need. \n\n"\
				                    "'-': This keyword is used to exclude a word to your search. It will make sure \n"\
				                    "the word you are excluding is not searched for in all of the names of the items. \n\n"\
				                    "'>': This keyword is used to check if any of the items you are searching through \n"\
				                    "start with what you are including. \n \n"\
				                    "'<': This keyword is used to check if any of the items you are searching thourgh \n"\
				                    "end with what you are including. \n"

			info_panel = vlib.ui.dialog.show_suppressable_message_box( self, dialog_info, caption = 'Keywords Help', icon = vlib.ui.dialog.ICON_INFORMATION, style = wx.CLOSE )

