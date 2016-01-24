"""
Contains classes related to the Motionbuilder Anim Exporter.

*Todo:*
    *Add ability to add bones and props
"""

# Python std lib
import os
import sys
import urllib
import time
import subprocess
import datetime

# PySide
import PySide.QtCore
import PySide.QtGui
import PySide.QtUiTools
import PySide.shiboken
import pysideuic

# Motionbuilder lib
import pyfbsdk
import pyfbsdk_additions
import mbdebugger
import unbind

# Volition Mobu callbacks
import vlib.callback
import vlib.debug

# Test imports
import vlib.message
import getpass

#vmobu
import vmobu
import core
import core.const
import vmobu.const
import vmobu.decorators
import vmobu.mobu_callback
import vmobu.mobu_perforce
import vmobu.mobu_export
import vmobu.mobu_rig_versioning

#file_io
import file_io.perforce
import file_io.v_path
import file_io.v_fbx
import file_io.resource_lib
import diagnostics.dcc_logger

from vlib.dcc.python.ui.progress_dialog import V_PROGRESS_BAR

UI_FILE_PATH = os.path.abspath( os.path.join( vmobu.const.DCC_CORE_ABS, r'..\ui\anim_exporter_mobu.ui') )
ED_UI_FILE_PATH = os.path.abspath( os.path.join( vmobu.const.DCC_CORE_ABS, r'..\ui\editCollectionsDialog.ui') )
ICON_PATH = os.path.abspath( os.path.join( vmobu.const.DCC_CORE_ABS, r'..\icons\anim_exporter') )
VERSION = "8.1.5"
STATUS_TIMEOUT = 3000

# properties that the anim node MUST have to export anything.
ANIM_NODE_PROPERTIES = { 'p_anim_file': 'none',
                        'p_export_anim': 'none',
                        'p_export_rampin': 5,
                        'p_export_rampout': 5,
                        'p_export_framestart': 1,
                        'p_export_frameend': 30,
                        'p_export_framerate': 30 }

CAMERA_WEIGHT_PROPERTY = 'p_ft_camera_weight'

OPTION_USED_FOR_LOADING = False
OPTION_USED_FOR_SAVING = True
NO_LOAD_UI_DIALOG = False

if vlib.user.settings['user_type'].lower( ) == 'technical artist':
	#reload( vmobu )
	reload( vmobu.decorators )
	reload( vmobu.mobu_export )
	reload( vmobu.mobu_perforce )
	reload( vmobu.mobu_rig_versioning )


class Native_Widget_Holder( pyfbsdk.FBWidgetHolder ):
	"""
	Holder for the PySide widget.

	*Arguments:*
	  * ``FBWidgetHolder`` Mobu holder for 3rd party widgets.

	*Keyword Arguments:*
	  * ``None``
	"""

	def WidgetCreate( self, pWidgetParent ):
		"""
		Creates the widget for the anim exporter from the .ui file.

		*Arguments:*
		  * ``pWidgetParent`` The Mobu parent for the widget to cling too.

		*Returns:*
		  * ``self.pointer`` A c++ pointer to the PySide.shiboken of the anim exporter main widget.

		*Examples:* ::

		  >>> import Anim_Exporter
		  >>> native_holder = Anim_Exporter.Native_Widget_Holder().WidgetCreate()
		  >>> print native_holder.pointer
		"""

		vmobu.core.evaluate()

		loader = PySide.QtUiTools.QUiLoader( )
		self.anim_exporter_widget = loader.load( UI_FILE_PATH )
		self.pointer = PySide.shiboken.getCppPointer( self.anim_exporter_widget )[ 0 ]

		vmobu.core.evaluate()
		Anim_Exporter( self.anim_exporter_widget )
		#except AttributeError:
		#	vmobu.core.evaluate()
		#	FBMe
			#self.WidgetCreate( pWidgetParent )

		vmobu.core.evaluate()

		return self.pointer

class Native_Qt_Widget_Tool( pyfbsdk.FBTool ):
	"""
	Builds the Mobu window holder for the PySide widget.

	*Arguments:*
	  * ``FBTool`` The main function for a Mobu tool.
	"""

	def __init__( self, name ):
		pyfbsdk.FBTool.__init__( self, name )
		self.widget_holder = Native_Widget_Holder( );
		self.build_layout()
		self.StartSizeX = 801
		self.StartSizeY = 550

	def build_layout( self ):
		"""
		Builds the layout of the Mobu window holder.

		*Arguments:*
		  * ``None``

		*Keyword Arguments:*
		  * ``None``

		*Returns:*
		  * ``None``
		"""

		x = pyfbsdk.FBAddRegionParam( 0, pyfbsdk.FBAttachType.kFBAttachLeft, "" )
		y = pyfbsdk.FBAddRegionParam( 0, pyfbsdk.FBAttachType.kFBAttachTop, "" )
		w = pyfbsdk.FBAddRegionParam( 0, pyfbsdk.FBAttachType.kFBAttachRight, "" )
		h = pyfbsdk.FBAddRegionParam( 0, pyfbsdk.FBAttachType.kFBAttachBottom, "" )
		self.AddRegion( "main","main", x, y, w, h )
		self.SetControl( "main", self.widget_holder )

class Anim_Exporter( PySide.QtGui.QMainWindow ):
	"""
	Main class for Motionbuilder animation exporter data and manipulation.

	*Examples:* ::

	  >>> import mobu_anim_exporter
	  >>> anim_exporter = Anim_Exporter( )
	"""

	def __init__( self, anim_exporter_widget ):
		"""
		Call .ui file for anim_exporter, and load all aspects into Motionbuilder space.

		*Arguments:*
		  * parent

		*Returns:*
		  * UI elements
		"""

		vmobu.core.evaluate()

		self.anim_exporter_widget = anim_exporter_widget

		#Set Mobu system and scene
		self.system = pyfbsdk.FBSystem( )
		self.scene = self.system.Scene

		self.debug = False
		self.debug_email = None
		self.debug_stop = True

		self.curr_filename = pyfbsdk.FBApplication( ).FBXFileName

		super( Anim_Exporter, self ).__init__( anim_exporter_widget )

		edit_collections_loader = PySide.QtUiTools.QUiLoader( )
		self.edit_dialog_collections_widget = edit_collections_loader.load( ED_UI_FILE_PATH )

		self.cb_mgr = vmobu.mobu_callback.Callbacks_Manager()
		self.v_cb_mgr = vlib.callback.Callback_Manager()
		self.logger = vmobu.core.logger

		self._on_merge = False

		#Key bindings
		self.keys = [ PySide.QtCore.Qt.Key_Return ]
		self.catch = False

		self.filepath = None
		self.ID = None

		self.anim_node = None

		self.changelist_name = core.const.MOBU_EXPORT_CHANGELIST

		#Instance variables
		self.anim_controller = None
		self.master_node = None
		self.namespace = ""
		self.time_call_back_id = None
		self.after_new_call_back_id = None
		self.after_open_call_back_id = None
		self.after_import_call_back_id = None
		self.anim_nodes = None
		self.anim_node_exporter = None

		self.stored_anim_dir = None
		self.stored_anim_data = None
		self.stored_weightList = None

		self.bone_list = None
		self.prop_list = None

		self.anim_node_anim_property = None
		self.bone_group_name_item = None
		self.bone_group_value_item = None

		self.signal_mapper = None
		self.spin_box = None

		#Get project directory
		self.project_dir = core.const.workspace_dir

		self.auto_fix = False
		self.quiet = False

		self.before_edit = ''
		self.collection_dict = { }
		self.to_be_deleted = [ ]
		self.end_eval_time = 0

		#Connect with UI classes for animation tab
		self.last_export_label = self.anim_exporter_widget.last_export_label
		self.character_combo_ui = self.anim_exporter_widget.characterComboUI
		self.export_group_box_ui = self.anim_exporter_widget.exportGroupBox
		self.update_button_ui = self.anim_exporter_widget.updateButtonUI
		self.animx_export_sel_ui = self.anim_exporter_widget.animxExportSelUI
		self.add_animation_button_ui = self.anim_exporter_widget.addAnimationButtonUI
		self.delete_animation_button_ui = self.anim_exporter_widget.deleteAnimationButtonUI
		self.animx_copy_ui = self.anim_exporter_widget.animxCopyUI
		self.animx_paste_ui = self.anim_exporter_widget.animxPasteUI
		self.anim_list_ui = self.anim_exporter_widget.animListUI
		self.export_dir_ui = self.anim_exporter_widget.exportDirUI
		self.batch_dir = self.anim_exporter_widget.batchDir
		self.animx_browse_ui = self.anim_exporter_widget.animxBrowseUI
		self.set_timerange_button_ui = self.anim_exporter_widget.setTimerangeButtonUI
		self.batch_button = self.anim_exporter_widget.batchButton
		self.browse_button = self.anim_exporter_widget.browseButton
		self.move_up_button_ui = self.anim_exporter_widget.moveUpButtonUI
		self.move_down_button_ui = self.anim_exporter_widget.moveDownButtonUI
		self.copy_all_animation_ui = self.anim_exporter_widget.copyAllAnimationUI
		self.paste_all_animation_ui = self.anim_exporter_widget.pasteAllAnimationUI
		self.animx_export_all_ui = self.anim_exporter_widget.animxExportAllUI
		self.animx_clear_ui = self.anim_exporter_widget.animxClearUI
		self.weapon_enabled_cb = self.anim_exporter_widget.weapon_enabled_cb

		#Connect with UI classes for animated weights tab
		self.collection_combo_ui = self.anim_exporter_widget.collectionComboUI
		self.add_collection_button_ui = self.anim_exporter_widget.addCollectionButtonUI
		self.edit_collection_button_ui = self.anim_exporter_widget.editCollectionButtonUI
		self.remove_collection_button_ui = self.anim_exporter_widget.removeCollectionButtonUI
		self.bone_group_table_ui = self.anim_exporter_widget.boneGroupTableUI
		self.set_key_weight_button_ui = self.anim_exporter_widget.setKeyWeightButtonUI
		self.del_key_weight_button_ui = self.anim_exporter_widget.delKeyWeightButtonUI
		self.sel_key_weight_button_ui = self.anim_exporter_widget.selKeyWeightButtonUI

		#Connect with UI classes for rigging tab
		self.rigx_file_edit_ui = self.anim_exporter_widget.rigxFileEditUI
		self.rigx_browse_ui = self.anim_exporter_widget.rigxBrowseUI
		self.rigx_copy_ui = self.anim_exporter_widget.rigxCopyUI
		self.rigx_paste_ui = self.anim_exporter_widget.rigxPasteUI
		self.rigx_clear_ui = self.anim_exporter_widget.rigxClearUI
		self.export_rigx_ui = self.anim_exporter_widget.exportRigxUI
		self.bone_list_ui = self.anim_exporter_widget.boneListUI
		self.prop_list_ui = self.anim_exporter_widget.propListUI
		self.add_bone_button_ui = self.anim_exporter_widget.addBoneButtonUI
		self.remove_bone_button_ui = self.anim_exporter_widget.removeBoneButtonUI
		self.add_prop_button_ui = self.anim_exporter_widget.addPropButtonUI
		self.remove_prop_button_ui = self.anim_exporter_widget.removePropButtonUI
		self.anim_controller_edit_ui = self.anim_exporter_widget.animControllerEditUI
		self.pick_anim_controller_ui = self.anim_exporter_widget.pickAnimControllerUI
		self.remove_anim_controller_ui = self.anim_exporter_widget.removeAnimControllerUI

		# Connect with UI classes for properties tab
		self.camera_animation_slider_edit = self.anim_exporter_widget.slider_edit
		self.camera_animation_slider = self.anim_exporter_widget.animation_ramp_slider
		self.key_cam_animation_button = self.anim_exporter_widget.slider_button
		self.select_fcurve_button = self.anim_exporter_widget.select_fcurve_button

		self.fov_shift_edit = self.anim_exporter_widget.fov_shift_edit

		#Connect with the edit collections ui
		self.button_box = self.edit_dialog_collections_widget.buttonBox
		self.group_box = self.edit_dialog_collections_widget.groupBox
		self.collection_name_ui = self.edit_dialog_collections_widget.collectionNameUI
		self.group_box_4 = self.edit_dialog_collections_widget.groupBox_4
		self.unassigned_list_ui = self.edit_dialog_collections_widget.unassignedListUI
		self.add_group_button_ui = self.edit_dialog_collections_widget.addGroupButtonUI
		self.delete_group_button_ui = self.edit_dialog_collections_widget.deleteGroupButtonUI
		self.edit_group_button_ui = self.edit_dialog_collections_widget.editGroupButtonUI
		self.group_box_2 = self.edit_dialog_collections_widget.groupBox_2
		self.groups_list_ui = self.edit_dialog_collections_widget.groupsListUI
		self.group_box_3 = self.edit_dialog_collections_widget.groupBox_3
		self.group_bone_list_ui = self.edit_dialog_collections_widget.groupBoneListUI
		self.assign_button_ui = self.edit_dialog_collections_widget.assignButtonUI
		self.unassign_button_ui = self.edit_dialog_collections_widget.unassignButtonUI

		self.add_group_button_ui.clicked.connect( self.add_group_in_collection )
		self.edit_group_button_ui.clicked.connect( self.edit_group_name )
		self.assign_button_ui.clicked.connect( self.assign_sel_group )
		self.unassign_button_ui.clicked.connect( self.unassign_sel_group )
		self.button_box.accepted.connect( self.finish_editing_collections )
		self.button_box.rejected.connect( self.cancel_edit_collections )
		self.weapon_enabled_cb.clicked.connect(self.update_anim_nodes_list)

		#Connect with documentation classes
		self.action_debug_on = self.anim_exporter_widget.actionDebugOn
		self.action_debug_off = self.anim_exporter_widget.actionDebugOff
		self.action_animnode = self.anim_exporter_widget.actionAnim_node

		# Connect file menu
		self.action_temp_export = self.anim_exporter_widget.actionTemp_Export
		self.action_check_scene_state = self.anim_exporter_widget.actionCheck_Scene_State
		self.check_scene_button = self.anim_exporter_widget.check_scene_button

		#Grab the current take stop and start frames
		self.end_time = pyfbsdk.FBSystem( ).CurrentTake.LocalTimeSpan.GetStop( )
		self.end_frame = pyfbsdk.FBSystem( ).CurrentTake.LocalTimeSpan.GetStop( ).GetFrame( )
		self.start_time = pyfbsdk.FBSystem( ).CurrentTake.LocalTimeSpan.GetStart( )
		self.start_frame = pyfbsdk.FBSystem( ).CurrentTake.LocalTimeSpan.GetStart( ).GetFrame( )

		# Set the name column width
		self.anim_list_ui.setColumnWidth( 0, 200 )
		for i in range( 1, 5 ):
			self.anim_list_ui.setColumnWidth( i, 60 )
		# Set the take column width
		self.anim_list_ui.setColumnWidth( 6, 200 )

		self.bone_group_table_ui.setColumnWidth( 1, 70 )

		#Set connections for animation tab buttons
		self.add_animation_button_ui.clicked.connect( self.add_animation )
		self.set_timerange_button_ui.clicked.connect( self.set_current_table_timerange )
		self.batch_button.clicked.connect( self.batch_process )
		self.animx_export_sel_ui.clicked.connect( self.on_export_selected )
		self.animx_browse_ui.clicked.connect( self.browse_anim_export_dirs )
		self.update_button_ui.clicked.connect( self.refresh_anim_node )
		self.browse_button.clicked.connect( self.browse_batch_dirs )
		self.animx_copy_ui.clicked.connect( self.copy_anim_export_path )
		self.animx_paste_ui.clicked.connect( self.paste_anim_export_path )
		self.animx_clear_ui.clicked.connect( self.clear_anim_export_path )
		self.delete_animation_button_ui.clicked.connect( self.delete_animation_cell )
		self.animx_export_all_ui.clicked.connect( self.on_export_all )
		self.move_up_button_ui.clicked.connect( self.move_anim_row_up )
		self.move_down_button_ui.clicked.connect( self.move_anim_row_down )
		self.copy_all_animation_ui.clicked.connect( self.copy_all_sel_anim )
		self.paste_all_animation_ui.clicked.connect( self.paste_all_sel_anim )

		self.anim_list_ui.setUpdatesEnabled( True )

		self.edit_collection_button_ui.clicked.connect( self.edit_bone_group )
		self.delete_group_button_ui.clicked.connect( self.delete_group_from_collection )
		self.groups_list_ui.itemChanged.connect( self.get_active_weighted_bones )
		self.groups_list_ui.itemClicked.connect( self.update_group_bones )

		#Set connections for rigging tab buttons
		self.add_collection_button_ui.clicked.connect( self.add_bone_weight_collection)
		self.rigx_browse_ui.clicked.connect( self.browse_rig_export_dirs )
		self.rigx_clear_ui.clicked.connect( self.clear_rig_path )
		self.rigx_copy_ui.clicked.connect( self.copy_rig_export_path )
		self.rigx_paste_ui.clicked.connect( self.paste_rig_export_path )
		self.pick_anim_controller_ui.clicked.connect( self.pick_anim_controller )
		self.remove_bone_button_ui.clicked.connect( self.delete_bone_from_list )
		self.remove_prop_button_ui.clicked.connect( self.delete_tag_from_list )
		self.add_bone_button_ui.clicked.connect( self.add_bone )
		self.add_prop_button_ui.clicked.connect( self.add_tag )

		self.set_key_weight_button_ui.clicked.connect( self.set_key_to_weight_groups )
		self.del_key_weight_button_ui.clicked.connect( self.delete_key_to_weight_groups )
		self.sel_key_weight_button_ui.clicked.connect( self.select_bone_weight_curve )

		self.action_debug_on.triggered.connect( self.debug_on )
		self.action_debug_off.triggered.connect( self.debug_off )
		self.action_animnode.triggered.connect( self.select_anim_node )
		self.action_temp_export.triggered.connect( self.on_export_temp_anim )
		self.action_check_scene_state.triggered.connect( self.on_scene_check )

		#Set initial line edits texts to blank
		self.export_dir_ui.setText( '' )
		self.rigx_file_edit_ui.setText( '' )
		self.anim_controller_edit_ui.setText( '' )

		#Set key bindings function to the main widget
		self.anim_exporter_widget.installEventFilter( self )

		self.check_scene_button.clicked.connect( self.on_scene_check )

		#Set connection for anim_node drop-down
		self.character_combo_ui.currentIndexChanged.connect( self.repopulate_cells )

		# Set connections for the Properties tab
		self.camera_animation_slider.valueChanged.connect( self.on_camera_slider_updated )
		self.key_cam_animation_button.clicked.connect( self.on_key_camera_animation )
		self.camera_animation_slider_edit.returnPressed.connect( self.on_camera_line_edit_updated )
		self.select_fcurve_button.clicked.connect( self.on_select_camera_float_fcurve )

		# Set up the camera anim ramp
		self.setup_camera_anim_ramp( self.namespace )

		#Call the loading of the widget function
		self.load_widget( )

		self.last_selected_index = 0

		#Sets initial callbacks
		self.add_application_callbacks( )


	def get_master_node( self ):
		"""
		Get the master node associated with the current anim_node

		*Arguments:*
			* ``None``

		*Keyword Arguments:*
			* ``None``
		"""

		if self.anim_node:
			if self.namespace:
				master_node = vmobu.core.get_objects_from_wildcard( self.namespace + ":*Master", use_namespace=True, single_only = True )
				if master_node:
					self.master_node = master_node
					return self.master_node

		return None


	def check_anim_node( self ):
		"""
		Checks for the anim node in the scene, and returns if it is present or not.

		*Arguments:*
		  * ''None''

		*Keyword Arguments:*
		  * ``None``

		*Returns:*
		  * self.anim_node bool True/False

		*Examples:* ::
		  >>> import Anim_Exporter

		  >>> Anim_Exporter.Anim_Exporter().check_anim_node()
		  <True>
		"""

		vmobu.core.evaluate()
		curr_anim_node_text = str( self.character_combo_ui.currentText( ) )
		self.anim_node = vmobu.core.get_object_by_name( curr_anim_node_text, use_namespace=True, models_only=False )

		if self.anim_node:
			self.namespace = vmobu.core.get_namespace_from_obj( self.anim_node, as_string = True )

			#Validate camera stuff
			self.setup_camera_anim_ramp(self.namespace)

			return True

	def update_minus_anim(self):
		self.bone_list_ui.clear()
		self.prop_list_ui.clear()

		self.get_weight_groups()
		vmobu.core.evaluate()

		self.update_bones_list()
		self.update_tags_list()
		anim_path = self.get_anim_path()
		rig_file = vmobu.core.get_property(self.anim_node, 'p_export_rig')

		if rig_file:
			self.rigx_file_edit_ui.setText(str(rig_file))

		if anim_path:
			self.export_dir_ui.setText(str(anim_path))
		else:
			self.export_dir_ui.setText("None")

		return True


	def update_widget_for_curr_node( self ):
		"""
		Updates widget for the current anim node selected.

		*Arguments:*
		  * ``None``

		*Keyword Arguments:*
		  * ``None``

		*Returns:*
		  * ``self.character_combo_ui.currentText()``
		"""

		vmobu.core.evaluate()
		#Grab current index and anim_node from drop-down
		curr_index = self.character_combo_ui.currentIndex( )
		self.character_combo_ui.itemData( curr_index )
		curr_combo_item_string = self.character_combo_ui.currentText( )

		self.check_anim_node( )

		curr_tab_index = self.anim_exporter_widget.tabWidget.currentIndex()

		if self.anim_node:
			if curr_tab_index == 0:
				if self.anim_node.LongName == str( curr_combo_item_string ):
					for row in range( self.anim_list_ui.rowCount( ) ):
						self.anim_list_ui.removeRow( row )

			for row in range( self.bone_group_table_ui.rowCount( ) ):
				self.bone_group_table_ui.removeRow( row )

			self.bone_list_ui.clear( )
			self.prop_list_ui.clear( )

			vmobu.core.evaluate()

			self.update_minus_anim()

		return True


	def add_animation( self ):
		"""
		Adds all aspects to creating a new "animation" within the exporter.

		*Arguments:*
		  * ``None``

		*Keyword Arguments:*
		  * ``None``

		*Returns:*
		  * ``None``
		"""

		self.add_anim_row( )

	def add_anim_row( self ):
		"""
		Creates a new cell widget for the newly created animation.

		*Arguments:*
		  * ``None``

		*Keyword Arguments:*
		  * ``None``

		*Returns:*
		  * ``self.anim_list_ui.item``
		"""

		#Inserts a new animation row within the UI and runs method to populate fields of animation row
		self.anim_list_ui.insertRow( 0 )
		item = PySide.QtGui.QTableWidgetItem( )
		self.anim_list_ui.setItem( 0, 0, item )

		self.set_take_properties( )
		if not self.add_take_widget_dropdown():
			pyfbsdk.FBMessageBox( 'Anim Exporter ERROR', 'No valid anim node found', 'OK' )
			return False
		self.store_anim_takes( )
		self.anim_list_ui.selectRow(0)


	def add_take_widget_dropdown(self, row=None):
		"""
		Creates a new cell widget for the "Takes" drop-down.

		*Arguments:*
		  * ``None``

		*Keyword Arguments:*
		  * ``row`` The row where this QComboBox will be placed

		*Returns:*
		  * ``PySide.QtGui.QComboBox``
		"""
		#Ensure there is an anim node present / selected in the scene
		if not self.anim_node:
			return False

		if row is None:
			row = 0
		else:
			self.anim_list_ui.selectRow(row)
			row = self.anim_list_ui.currentRow()

		takes = []

		for take in pyfbsdk.FBSystem().Scene.Takes:
			takes.append(take.Name)

		anim_name = self.anim_list_ui.item(row, 0)

		signal_mapper = PySide.QtCore.QSignalMapper(self)
		take_drop_down = PySide.QtGui.QComboBox()
		take_drop_down.setParent(self.anim_list_ui)
		signal_mapper.setMapping(take_drop_down, str(row) + '-' + str(6))

		take_drop_down.addItems(takes)

		for prop in self.anim_node.PropertyList:
			if prop.IsUserProperty():
				if not prop.Name.startswith('wg:'):
					if not prop.Name == 'Bones':
						if prop.Name == str(anim_name.text()):
							anim_node_take_enum = prop.EnumList(0)
							anim_node_take_split = anim_node_take_enum.split(":")
							anim_node_take = anim_node_take_split[1]

							for idx in range(take_drop_down.count()):
								item_string = take_drop_down.itemText(idx)
								if item_string == anim_node_take:
									take_drop_down.setCurrentIndex(idx)
									#break
							#break

		self.anim_list_ui.setCellWidget(row, 6, take_drop_down)

		self.connect(take_drop_down, PySide.QtCore.SIGNAL("currentIndexChanged( int )"), signal_mapper,
		             PySide.QtCore.SLOT("map()"))

		signal_mapper.connect(PySide.QtCore.SIGNAL("mapped(const QString &)"), self,
		                      PySide.QtCore.SLOT("take_changed(const QString &)"))

		return take_drop_down


	@PySide.QtCore.Slot(str)
	def take_changed(self, rowCol):
		"""
		This is flagged when the take drop-down is changed. This updates the corresponding anim node property associated take

		*Arguments:*
		  * ``rowCol`` Row and column string association

		*Keyword Arguments:*
		  * ``None``

		*Returns:*
		  * ``None``
		"""

		row = int(rowCol.split('-')[0])
		col = int(rowCol.split('-')[1])

		val = self.anim_list_ui.cellWidget(row, col).currentText()

		self.remove_anim_node_properties( )

		vmobu.core.evaluate( )

		for row in range( self.anim_list_ui.rowCount( ) ):
			curr_anim_name_item_ui = self.anim_list_ui.item(row, 0)
			curr_start_frame_item_ui = self.anim_list_ui.item(row, 1)
			curr_end_frame_item_ui = self.anim_list_ui.item(row, 2)
			curr_rampin_item_ui = self.anim_list_ui.item(row, 3)
			curr_rampout_item_ui = self.anim_list_ui.item(row, 4)
			curr_framerate_item_ui = self.anim_list_ui.item(row, 5)
			curr_take_item_ui = self.anim_list_ui.item(row, 6)

			#Create new animation property in anim node with enum list for values
			self.anim_node_anim_property = self.anim_node.PropertyCreate(str(curr_anim_name_item_ui.text()),
			                                                             pyfbsdk.FBPropertyType.kFBPT_enum, "Enum", False, True,
			                                                             None)

			#Set values for enum list
			take_text = "take:" + str(val)
			start_frame_text = "startFrame:" + str(curr_start_frame_item_ui.text())
			end_frame_text = "endFrame:" + str(curr_end_frame_item_ui.text())
			ramp_in_text = "rampIn:" + str(curr_rampin_item_ui.text())
			ramp_out_text = "rampOut:" + str(curr_rampout_item_ui.text())
			framerate_text = "frameRate:" + str(curr_framerate_item_ui.text())

			#Add enum list to property
			anim_node_anim_prop_enum_list = self.anim_node_anim_property.GetEnumStringList(True)
			anim_node_anim_prop_enum_list.Add(take_text)
			anim_node_anim_prop_enum_list.Add(start_frame_text)
			anim_node_anim_prop_enum_list.Add(end_frame_text)
			anim_node_anim_prop_enum_list.Add(ramp_in_text)
			anim_node_anim_prop_enum_list.Add(ramp_out_text)
			anim_node_anim_prop_enum_list.Add(framerate_text)

			#Verify the enum list has changed to update
			self.anim_node_anim_property.NotifyEnumStringListChanged()


	def set_take_properties( self, row=None ):
		"""
		Sets the properties for the current take in the exporter.

		*Arguments:*
		  * ``row`` The row of the anim exporter Animation tab.

		*Keyword Arguments:*
		  * ``None``

		*Returns:*
		  * ``None``
		"""

		#Refresh scene and check if a row is present, and declare the selected row and column as 'row' and 'col'
		vmobu.core.evaluate()
		if row is None:
			row = 0
		else:
			row = self.anim_list_ui.currentRow( )

		#Grab current Mobu take
		curr_take = vmobu.core.get_current_take( )

		#Set the default name of newly created animation row in UI as the take name as long as it's unique
		anim_name_widget_item = PySide.QtGui.QTableWidgetItem( )
		self.anim_list_ui.setItem( row, 0, anim_name_widget_item )
		result, iteration = self.is_animation_name_unique( curr_take.Name )

		if result:
			anim_name_widget_item.setText( curr_take.Name )

		else:
			# If it's not unique, add an iterator to the end.
			anim_name_widget_item.setText( curr_take.Name + ' {0}'.format( iteration ) )

		#Grab current anim_node name from drop-down and find it in scene based on it's name
		self.check_anim_node( )

		#Grab the parent of the anim_node (the master) and set default ramp-in, ramp-out, and framerate in anim_node based off master
		#if self.get_master_node( ):
		self.get_master_node()
		rig_ramp_in = vmobu.core.get_property( self.master_node, 'p_export_rampin' )
		rig_ramp_out = vmobu.core.get_property( self.master_node, 'p_export_rampin' )
		rig_frame_rate = vmobu.core.get_property( self.master_node, 'p_export_framerate' )

		#Populate columns of UI with the ramp-in, ramp-out, and framerate values
		if rig_ramp_in:
			ramp_in_widget_item = PySide.QtGui.QTableWidgetItem( )
			self.anim_list_ui.setItem( row, 3, ramp_in_widget_item )
			ramp_in_widget_item.setText( str( rig_ramp_in ) )

		if rig_ramp_out:
			ramp_out_widget_item = PySide.QtGui.QTableWidgetItem( )
			self.anim_list_ui.setItem( row, 4, ramp_out_widget_item )
			ramp_out_widget_item.setText( str( rig_ramp_out ) )

		if rig_frame_rate:
			framerate_widget_item = PySide.QtGui.QTableWidgetItem( )
			self.anim_list_ui.setItem( row, 5, framerate_widget_item )
			framerate_widget_item.setText( str( rig_frame_rate ) )

		#Grab current take's start and end frames
		start = pyfbsdk.FBSystem( ).CurrentTake.LocalTimeSpan.GetStart( ).GetFrame( )
		end = pyfbsdk.FBSystem( ).CurrentTake.LocalTimeSpan.GetStop( ).GetFrame( )

		#Set start and end frame values in the UI
		start_frame_widget_item = PySide.QtGui.QTableWidgetItem( )
		self.anim_list_ui.setItem( row, 1, start_frame_widget_item )
		start_frame_text = start_frame_widget_item.setText( str( start ) )

		end_frame_widget_item = PySide.QtGui.QTableWidgetItem( )
		self.anim_list_ui.setItem( row, 2, end_frame_widget_item )
		end_frame_widget_item.setText( str( end ) )

		take_name_widget_item = PySide.QtGui.QTableWidgetItem()
		self.anim_list_ui.setItem(row, 6, take_name_widget_item)
		take_name_widget_item.setText(curr_take.Name)

	def is_animation_name_unique( self, text ):
		"""
		Checks if animation name in the table is unique. If not, returns the number of duplicates
		This way we do not rely on Mobu to rename the animation cells for us.

		*Arguments:*
		  * ``text`` - Name of the animation

		*Keyword Arguments:*
		  * ``none``

		*Returns:*
		  * ``Bool`` - Whether or not the animation is unique
		  * ``iterator`` - Number of duplicates for the animation
		"""

		# Start with base iteration of 0
		iteration = 0
		take_names = []

		# If there are rows in the ui
		if self.anim_list_ui.rowCount( ) > 0:
			# For each row, get the animation name and place it in the take name list
			for i in range( 0, self.anim_list_ui.rowCount( ) ):
				curr_anim_name_item_ui = self.anim_list_ui.item( i, 0 )
				take_names.append( curr_anim_name_item_ui.text( ).lower() )

		for name in take_names:
			# Is lowercase text in the take_names
			if text.lower() in name:
				# Add one to the iteration
				iteration = iteration + 1
				# If the current iteration does not exist in the take_names, that's the number we want.
				if not unicode( text.lower() + ' {0}'.format( iteration ) ) in take_names:
					break

		# If there is a value in the iteration, it must be a duplicate. Return False and the number of iterations
		if iteration:
			return False, iteration

		# If no iteration value, return True and an empty string
		return True, ''

	def set_current_table_timerange( self, row = None ):
		"""
		Sets current timerange from Motionbuilder within the exporter.

		*Arguments:*
		  * ``None``

		*Keyword Arguments:*
		  * ``row`` Rows of the animation tab in Anim Exporter

		*Returns:*
		  * ``None``
		"""

		#Refresh scene and check if a row is present, and declare the selected row and column as 'row' and 'col'
		vmobu.core.evaluate( )

		player = pyfbsdk.FBPlayerControl( )
		# Go to the end and store the frame
		altered_end   = player.GotoEnd( )
		end_frame = vmobu.core.get_frame_current( )

		# Go to start and store the frame
		altered_start = player.GotoStart( )
		start_frame = vmobu.core.get_frame_current( )

		# Go back to end
		player.GotoEnd( )

		if row is None:
			row = self.anim_list_ui.currentRow( )

		#Set start and end frame within the UI
		start_frame_widget_item = PySide.QtGui.QTableWidgetItem( )
		self.anim_list_ui.setItem( row, 1, start_frame_widget_item )
		start_frame_text = start_frame_widget_item.setText( str( start_frame ) )

		end_frame_widget_item = PySide.QtGui.QTableWidgetItem( )
		self.anim_list_ui.setItem( row, 2, end_frame_widget_item )
		end_frame_widget_item.setText( str( end_frame ) )


	@PySide.QtCore.Slot( )
	def batch_process( self ):
		"""
		Runs a batch export on all characters and takes in the scene.

		*Arguments:*
		  * ``None``

		*Keyword Arguments:*
		  * ``None``

		*Returns:*
		  * ``None``
		"""

		#Grab current row and column in ui, as well as the currently selected animation cell widget
		for node in range( self.character_combo_ui.count( ) ):
			for row in range( self.anim_list_ui.rowCount( ) ):
				if row < 1:
					self.anim_list_ui.selectRow( 0 )
					self.anim_export_batch( )
				else:
					self.anim_list_ui.selectRow( row )
					self.anim_export_batch( )


	def on_export_all( self ):
		"""
		Exports all animation of one character based off animation made in the ui

		*Arguments:*
		  * ``None``

		*Keyword Arguments:*
		  * ``None``

		*Returns:*
		  * ``None``
		"""
		vmobu.core.logger.info( 'Exporting All' )
		self.update_button_ui.click( )

		vmobu.core.evaluate( )
		character = vmobu.core.get_current_character( )
		if not character:
			return False

		self.anim_list_ui.selectAll( )
		self.on_export_selected( )

		self.update_button_ui.click( )

	def check_export_bones( self, character_name ):
		"""
		Exports all animation of one character based off animation made in the ui

		*Arguments:*
		  * ``character_name`` - name of the character we're checking ex. af001

		*Keyword Arguments:*
		  * ``None``

		*Returns:*
		  * ``True``
		"""
		for bone_name in vmobu.const.EXPORT_BONE_NAMES:
			# Find the bone by name
			bone = vmobu.core.get_object_by_name( '{0}:*_skel:{1}'.format( character_name, bone_name ) )

			# If we couldn't find the bone, we don't want to try and edit a property
			if not bone:
				continue

			# Get the property value
			export_flag = bone.PropertyList.Find( 'p_bone_export' )
			if not export_flag.Data:
				export_flag.Data = True

		vmobu.core.evaluate( )

		return True

	def check_min_boneweight_values( self ):
		"""
		Sets the minimum value of the 'p_bone_weight' property to 0.

		*Arguments:*
		  * ``None``

		*Keyword Arguments:*
		  * ``None``

		*Returns:*
		  * ``None``
		"""

		for comp in pyfbsdk.FBSystem( ).Scene.Components:
			bone_weight_prop = vmobu.core.get_property( comp, 'p_bone_weight', return_value = False )
			if bone_weight_prop:
				bone_weight_prop.SetMin( 0 )


	def check_validity_of_takes(self):
		"""
		Checks if the take in the current animation still exists in the scene.

		*Arguments:*
		  * ``None``

		*Keyword Arguments:*
		  * ``None``

		*Returns:*
		  * ``None``
		"""

		row = self.anim_list_ui.currentRow()
		curr_take = vmobu.core.get_current_take(as_string=True)

		take_name_item = self.anim_list_ui.item(row, 6)
		if not take_name_item:
			pyfbsdk.FBMessageBox( 'Anim Exporter Error', 'Please select an animation to export', 'OK' )
			return False
		take_name = str(take_name_item.text())

		scene_takes = []
		for take in pyfbsdk.FBSystem().Scene.Takes:
			scene_takes.append(take.Name)

		if take_name not in scene_takes:
			pyfbsdk.FBMessageBox('Take Error', 'The take associated with this animation does not exist in your scene.\n Would you like to use the current take?', 'Ok', None, None)
			self.anim_list_ui.item(row,6).setText(curr_take)

		return True

	def change_timerange_to_user(self):
		"""
		Sets the timerange to the user's specifications

		*Arguments:*
		  * ``None``

		*Keyword Arguments:*
		  * ``None``

		*Returns:*
		  * ``frame_start/frame_end`` time range the user specified in the UI
		"""

		row = self.anim_list_ui.currentRow()

		start_frame_item_ui = self.anim_list_ui.item(row, 1)
		end_frame_item_ui = self.anim_list_ui.item(row, 2)

		frame_start = int(start_frame_item_ui.text())
		frame_end = int(end_frame_item_ui.text())

		take_name_item = self.anim_list_ui.item(row, 6)
		take_name = str(take_name_item.text())

		for take in pyfbsdk.FBSystem().Scene.Takes:
			if take.Name == take_name:
				pyfbsdk.FBSystem().CurrentTake = take

		#pyfbsdk.FBPlayerControl().SetEditStart( pyfbsdk.FBTime( 0, 0, 0, frame_start, 0 ) )
		#pyfbsdk.FBPlayerControl().SetEditStop( pyfbsdk.FBTime( 0, 0, 0, frame_end, 0 ) )
		pyfbsdk.FBSystem().CurrentTake.LocalTimeSpan = pyfbsdk.FBTimeSpan( pyfbsdk.FBTime( 0, 0, 0, frame_start, 0 ), pyfbsdk.FBTime( 0, 0, 0, frame_end, 0))
		return frame_start, frame_end

	def check_roll_twist_bones( self, character, check = False ):
		# Make a dictionary to check if objects exist or not.
		procedural_nodes = { }
		objs_to_add = [ ]

		for name in vmobu.const.PROCEDURAL_NODES_EXTENSION:
			procedural_nodes[ name ] = None

		for extension in character.CharacterExtensions:
			# If the extension is not the procedural extension, we don't care about it
			if not extension.Name.lower( ) == 'proceduralnodesextension':
				continue

			# For each object in the extension, see if it has roll or twist bones. If it does, we retain it to compare.
			for i in range( 0, extension.GetSubObjectCount( ) ):
				obj = extension.GetSubObject( i )
				if obj.Name in procedural_nodes.keys( ):
					procedural_nodes[ obj.Name ] = obj

			for key in procedural_nodes.keys( ):
				# If the object wasnt found in the extension, we find and add it.
				if procedural_nodes[ key ] == None:
					objs_to_add.append( key )

					# If we're not just checking to see if the objs are in the set, we're going to add them.
					if not check:
						# Get the object we want to add to the scene.
						obj_to_add = vmobu.core.get_objects_from_wildcard( '{0}:*_skel:{1}'.format( character.LongName.split( ':' )[ 0 ], key ), use_namespace=True, case_sensitive=False, single_only=True, models_only=True )
						# If we didn't find the object in the scene, it must not be relevant to the rig.
						if not obj_to_add:
							continue

						# Add the obj to the character extension
						extension.AddObjectDependency( obj_to_add )

			if objs_to_add:
				vmobu.core.logger.info( 'Anim Exporter: appending roll and or twist bones.', extra = '{0}'.format( procedural_nodes ) )
				return False, objs_to_add

			else:
				return True, 'Success'

		return True, 'No extension was found to add.'

	@staticmethod
	def check_for_opc( ):
		opcs = vmobu.core.get_objects_from_wildcard( 'OPC_*', use_namespace=False, single_only=False, models_only=False, case_sensitive=True )

		# We didn't find any
		if not opcs:
			return True, None

		# Do we fail or not. set default to False
		opc_failure = False

		# Check in the list we got back from the search
		for opc in opcs:
			# If the object is a constraint, we don't really care.
			if isinstance( opc, ( pyfbsdk.FBConstraint ) ):
				continue
			if isinstance( opc, pyfbsdk.FBNamespace ):
				continue

			# If the object in the opc was a skeleton, we can't export that.
			opc_child = opc.Children
			if len( opc_child ) >= 1:
				child_object = opc_child[0]
				if isinstance( child_object, ( pyfbsdk.FBModelSkeleton ) ):
					opc_failure = True
					break

				# If the name is in our list of critical hierarchical features...
				if child_object.Name in [ 'AnimationController', 'Reference', 'Master', 'LeftHandProp', 'RightHandProp' ]:
					opc_failure = True
					break

		# Check if we found any.
		if opc_failure:
			# We found some, return False
			return False, opcs

		return True, None

	def on_scene_check( self ):
		vmobu.core.logger.info( 'Scene Check: Started')
		# Check anim node and get master node
		self.check_anim_node( )
		self.get_master_node( )

		# Refresh the UI
		self.update_button_ui.click( )

		anim_namespace = self.anim_node.LongName.split( ':' )[ 0 ]
		anim_character = vmobu.core.get_character_by_name( anim_namespace )

		results = { }

		################
		## Version and export bone check ##
		################

		# Silent check
		self.check_export_bones( anim_namespace )

		# Append version check
		results['version'] = vmobu.mobu_rig_versioning.run( anim_character )

		# Append roll bone check
		results['roll'], roll_bones_to_add = self.check_roll_twist_bones( anim_character, check=True )

		#################
		## Camera animation ##
		#################
		character_camera = None
		results['camera_anim'] = False

		# Check the camera for weighting and be sure the user wants to do this.
		for camera in vmobu.core.scene.Cameras:
			if camera.LongName.split( ':' )[ 0 ].lower( ) == anim_namespace.lower( ):
				# We found the camera
				character_camera = camera
				break
		if character_camera:
			camera_weight = character_camera.PropertyList.Find( 'p_bone_weight' ).Data
			if camera_weight != 0:
				results['camera_anim'] = True

		################
		## Check or One Point Constraints ##
		################
		results['opc'], obj_list = self.check_for_opc( )

		################
		## Consolidate results ##
		################
		result_string = ''

		if results[ 'camera_anim' ]:
			result_string = result_string + '*CAMERA ANIMATION : p_bone_weight on the camera is 100. You will be exporting camera animation. Check to be sure you want this \n'
		if not results[ 'version' ]:
			result_string = result_string + '*RIG VERSION : {0} is out of date \n'.format( anim_namespace )
		if not results[ 'opc' ]:
			result_string = result_string + '*OPC : There are One point constraint systems still left if your scene. Please resolve these before exporting. \n'
			print [ obj.Name for obj in obj_list ]
		if not results[ 'roll' ]:
			result_string = result_string + '*ROLL TWIST : The following need to be added {0} \n'.format( roll_bones_to_add )

		if not result_string:
			result_string = 'Ready for export!'
		else:
			result_string = result_string + ' \n**If you need help resolving any of the above, please contact a TA!**'
			vmobu.core.logger.info( 'Scene Check: Failed', extra = str( results ) )

		pyfbsdk.FBMessageBox( 'Animation Exporter: Export Check Results', result_string, 'OK' )
		self.logger.warning( result_string )

	@vmobu.decorators.store_and_reset_timerange
	def on_export_selected( self, from_all = False ):
		"""
		Callback that handles selection and exporting when exporting only selected animations.

		*Arguments:*
		  * ``None``

		*Keyword Arguments:*
		  * ``None``

		*Returns:*
		  * ``None``
		"""
		row_list = self.anim_list_ui.selectionModel( ).selectedRows( )
		anim_node_index = self.character_combo_ui.currentIndex( )
		self.update_button_ui.click( )
		self.character_combo_ui.setCurrentIndex( anim_node_index )
		self.get_master_node( )

		if self.debug:
			result = pyfbsdk.FBMessageBox('Animation Exporter', 'DEBUG is ON. Continue?', 'Yes', 'Cancel')
			if not result:
				return False

		if not self.check_anim_node( ):
			pyfbsdk.FBMessageBox( 'Export Error', 'Could not get the AnimNode', "OK" )
			return False, 'Anim node error'

		# Get namespaces and get the anim node and character to match
		anim_namespace =  self.anim_node.LongName.split( ':' )[ 0 ]
		anim_character = vmobu.core.get_character_by_name( anim_namespace )
		if not anim_character:
			pyfbsdk.FBMessageBox( 'Export Error', 'Character couldnt be found that matched the anim node', "OK" )
			return False, 'Charcter couldnt be found that matched the anim_node'

		#Set the character to be the matching character for the anim_node
		vmobu.core.app.CurrentCharacter = anim_character

		# Check for OPC systems.
		opc_check, obj_list = self.check_for_opc( )
		if not opc_check:
			# Get the names of the objects we found that are affected.
			name_list = [ obj.LongName for obj in obj_list ]
			pyfbsdk.FBMessageBox( 'Export Error', 'The current scene has one One Point Constraints that must be resolved before exporting. \n Affected Objs : {0} \n Contact a TA if you need assistance.'.format( name_list ), "OK" )
			vmobu.core.logger.info( 'Animation Exporter', extra = 'OPC {0}'.format( obj_list ) )
			return False

		# Check the export bones.
		self.check_export_bones( anim_namespace )

		# Check the rig version
		version_check = vmobu.mobu_rig_versioning.run( anim_character )

		# Check the characters version, if the version needs a swap, stop running the tool.
		if not version_check:
			pyfbsdk.FBMessageBox( 'Export Error', 'Your rig version for {0} is not up to date. Please perform a swap.'.format( anim_namespace ), "OK" )
			return False

		character_camera = None
		# Check the camera for weighting and be sure the user wants to do this.
		for camera in vmobu.core.scene.Cameras:
			if camera.LongName.split( ':' )[ 0 ].lower( ) == anim_namespace.lower( ):
				# We found the camera
				character_camera = camera
				break

		if character_camera:
			camera_weight = character_camera.PropertyList.Find( 'p_bone_weight' ).Data
			if camera_weight != 0:
				user_choice = pyfbsdk.FBMessageBox( 'Animation Exporter Notification!', 'You are exporting camera animation. \n Are you sure you want to export this?', 'OK', 'Cancel' )
				if user_choice == 2:
					# We exit if the user chose cancel
					vmobu.core.logger.info( 'Animation Exporter', extra = 'User cancelled export of character camera animation')
					return False

				vmobu.core.logger.info( 'Animation Exporter', extra = 'User chose to export character camera animation')

		# Here we check to be sure the rolls and twists are part of the character extensions!
		roll_result, bones_to_add = self.check_roll_twist_bones( anim_character )
		if not roll_result:
			vmobu.core.confirm_dialog( title='Export Error!', message='Your character extensions are out of date. {0} will be added to the extensions, but may behave strangely when setting the character to stance post export. \n Please swap after export to fix this issue. Please contact a TA if you ahve any other questions about this issue!'.format( bones_to_add ) )
			vmobu.core.logger.info( 'Animation Exporter Error', extra = '{0}'.format( bones_to_add ) )
			#return False

		# For every row item in the list of selected row
		result_list = [ ]
		for item in row_list:
			# Select the row
			self.anim_list_ui.selectRow( item.row( ) )

			vmobu.core.evaluate( )

			# Update the properties on the anim and master node
			self.update_properties( self.anim_node )
			self.update_properties( self.master_node )

			# Export the selected animation which was selected above
			result, message = self.export_animation_row( export_all = True, current_row = item, current_character = anim_character )
			result_list.append( result )

		list_of_success = [ success for success in result_list if success == True ]

		self.last_export_label.setText( 'Last Export : {0}/{1} \n@ {2}'.format( len( list_of_success ), len( row_list ), datetime.datetime.now( ).ctime( ) ) )

		self.update_button_ui.click( )
		self.character_combo_ui.setCurrentIndex( anim_node_index )
		if False in result_list:
			return False

		return True

	def on_export_temp_anim( self ):
		"""
		Callback that handles logic for exporting temp animations.
		"""
		# Prompt the user for their file path ( directory )
		#path = PySide.QtGui.QFileDialog.getExistingDirectory( self )
		path, selection_type = PySide.QtGui.QFileDialog.getSaveFileName( self, caption = 'Export file Location / Name', filter = 'FBX Files (*.fbx)' )
		if not path:
			return False

		# Handle the pathing.
		directory, anim_name = os.path.split( path )
		if not anim_name.endswith('.fbx'):
			anim_name = anim_name + '.fbx'
		real_path = str( os.path.realpath( os.path.join( directory, anim_name ) ) )

		# get the current character
		current_character = vmobu.core.get_current_character( )

		if not current_character:
			return False

		# We dont' want to crunch this animation so we use the export_temp_animation method
		## The message variable will sometimes return a file path we want to select in a windows explorer dialog!
		## Otherwise this method will return an error message.
		success, message = self.export_temp_anim( current_character, path )

		# If the export was successful, we prompt with a dialog
		if success:
			user_choice = pyfbsdk.FBMessageBox('Temp Export Success!', 'The export was successful!', 'Open Location', 'OK' )
			if user_choice == 1:
				# Convert the path to the abs path so we can open it in the subprocess
				file_path = os.path.abspath( message )

				# The user has chosen the directory to be opened
				subprocess.call( "explorer /select, {0}".format( file_path ), shell = True )
		else:
				# Prompt the user of the failure.
				pyfbsdk.FBMessageBox('Temp Export Failure!', 'The export has failed! {0}'.format( message ), 'OK' )

		current_character.ActiveInput = True

		return True

	def export_temp_anim( self, character, file_path ):
		"""
		Actual export functionality for exporting an animation for temporarily purposes.

		TODO: Add in filters for where files can be saved (outside of perforce!!)
		"""
		current_take = vmobu.core.get_current_take( )

		# Duplicate the current take into an export take
		temp_anim_take = pyfbsdk.FBSystem( ).CurrentTake.CopyTake( "temp_export_take" )
		vmobu.core.set_current_take( temp_anim_take )

		vmobu.core.evaluate( )

		vmobu.core.merge_all_layers( True, temp_anim_take )

		# If it's a weapon, item, or vehicle, find the master, get all skeleton nodes under the master and plot animation to them.
		master_node = self.get_master_node( )
		if master_node:
			self.determine_and_bake_asset_type( master_node, character )

		# Plot the character to the skeleton
		plot_options = pyfbsdk.FBPlotOptions( )
		plot_options.ConstantKeyReducerKeepOneKey = False
		plot_options.PlotAllTakes = False
		plot_options.PlotOnFrame = True
		vmobu.core.plot_character( character, plot_where=pyfbsdk.FBCharacterPlotWhere.kFBCharacterPlotOnSkeleton, options=plot_options, quiet=True, force=True )

		# Get the correct export selection
		vmobu.core.unselect_all_components( )
		hier = vmobu.core.get_hierarchy( master_node )
		export_selection = [ master_node ]
		for obj in hier:
			if isinstance(obj, ( pyfbsdk.FBModelNull, pyfbsdk.FBModelSkeleton, pyfbsdk.FBModelRoot ) ):
				export_selection.append( obj )

		# Get fbx options
		fbx_options = vmobu.mobu_export.mb_fbx_export.get_fbx_options( take_name= "temp_export_take", export_type='Animation' )

		# actual export
		if character:
			pyfbsdk.FBApplication( ).SaveCharacterRigAndAnimation( str( file_path ).lower( ), character, fbx_options )
		else:
			# Else, export as normal without character
			pyfbsdk.FBApplication( ).FileSave( str( file_path ).lower( ), fbx_options )

		# Delete the temp take regardless if the export was successful or not.
		vmobu.core.set_current_take( current_take )
		temp_anim_take.FBDelete( )

		vmobu.core.unselect_all_components( )

		if not os.path.exists( file_path ):
			return False, "Export failed to save properly"

		# strip namespace
		vfbx = file_io.v_fbx.FBX( file_path )
		vfbx.remove_namespace( )
		# remove_objects not needed in exported animation files
		vfbx.remove_nodes_by_names( vmobu.const.ANIMATION_CONTROLLER_NAMES )
		vfbx.remove_nodes_by_keywords( vmobu.const.ANIMATION_CONTROLLER_KEYWORDS )
		vfbx.save_scene_file( )


		return True, file_path

	@vmobu.decorators.without_callbacks_obj
	def export_animation_row( self, remove_namespace=True, export_all=False, current_row = None, current_character = None ):
		"""
		Exports animation based on the animation cell widget selected in the exporter.

		*Arguments:*
		  * ``None``

		*Keyword Arguments:*
		  * ``None``

		*Returns:*
		  * ``None``
		"""
		if not current_row:
			return False, 'No row selected'

		if not current_character:
			return False, 'No character'

		# Get the namespace
		char_namespace = current_character.LongName.split( ':' )[ 0 ]

		export_pbar = V_PROGRESS_BAR( percent= 0.0, subtitle='Exporting Animation', message='Beginning...' )

		#Refresh 3d space
		vmobu.core.evaluate( )
		selected_row = self.anim_list_ui.currentIndex( ).row( )

		export_pbar.update( percent =  0.05, message = 'Updating properties' )

		self.update_properties( self.anim_node )
		self.update_properties( self.master_node )
		self.update_weight_groups( )

		export_pbar.update( percent =  0.06, message = 'Checking take validation' )

		result = self.check_validity_of_takes( )
		if not result:
			return False, 'Takes not valid'

		# get the animation name
		name_cell = self.anim_list_ui.item( selected_row, 0 )
		take_cell = self.anim_list_ui.item( selected_row, 6 )

		anim_name = str( name_cell.text( ) )
		take_name = str( take_cell.text( ) )

		export_pbar.update( percent =  0.06, subtitle = 'Exporting Animation: {0}'.format( anim_name ), message = 'Checking take validation' )

		if not anim_name:
			pyfbsdk.FBMessageBox( 'Export Error', 'A valid animation name was not found in the selected row', "OK" )
			return False, 'Name error'

		vmobu.core.evaluate( )

		# get the take name from the animation name
		anim_take = None

		# make sure this is an actual scene take
		for take in vmobu.core.system.Scene.Takes:
			if take.Name == take_name:
				anim_take = take_name
				vmobu.core.system.CurrentTake = take
				break

		# Save the current time range
		orig_end_frame = vmobu.core.system.CurrentTake.LocalTimeSpan.GetStop( ).GetFrame( )
		orig_start_frame = vmobu.core.system.CurrentTake.LocalTimeSpan.GetStart( ).GetFrame( )

		# make sure we got a proper take name
		if not anim_take:
			pyfbsdk.FBMessageBox( 'Export Error', 'Could not get a Scene Take from the selected animation name. {0}'.format( anim_name ), "OK" )
			return False, 'Scene take error'

		export_pbar.update( percent =  0.11, message = 'Pre export checks' )
		# fix the minimum boneweight values
		self.check_min_boneweight_values( )

		if anim_name.startswith( ' ' ) or anim_name.endswith( ' ' ):
			anim_name = anim_name.strip( )

		user_start, user_end = self.change_timerange_to_user( )

		export_pbar.update( percent =  0.2, message = 'Duplicating take for export' )
		current_take = vmobu.core.get_current_take( )

		# Duplicate the current take into an export take
		temp_anim_take = pyfbsdk.FBSystem( ).CurrentTake.CopyTake("temp_export_take")
		vmobu.core.set_current_take( temp_anim_take )

		vmobu.core.evaluate( )

		export_pbar.update( percent =  0.3, message = 'Merge all layers' )
		vmobu.core.merge_all_layers( True, temp_anim_take )

		# Check to see if there's a character face, and if there is bake it down.
		self.get_and_bake_character_face( char_namespace, p_bar=export_pbar )

		# If it's a weapon, item, or vehicle, find the master, get all skeleton nodes under the master and plot animation to them.
		export_pbar.update( percent =  0.5, message = 'Getting master node' )
		master_node = self.get_master_node( )
		if master_node:
			current_character = self.determine_and_bake_asset_type( master_node, current_character )

		export_pbar.update( percent =  0.6, message = 'Baking down camera attributes' )
		# bake down the camera bone's FOV and other attributes
		camera_node = vmobu.core.get_object_by_name( '{0}:*:camera'.format( char_namespace ) , single_only = True, use_namespace = True, models_only = False, case_sensitive = False )
		if camera_node:
			vmobu.mobu_export.mb_export.bake_camera_bone_data( camera_node, fov_shift = float( self.fov_shift_edit.text( ) ) )

		export_pbar.update( percent = 0.9, message= 'Exporting...')
		# do the actual export
		export, error_message = vmobu.mobu_export.mb_fbx_export.export_animation( self.anim_node, current_character, anim_name, temp_anim_take.Name, master_node = master_node, debug = self.debug )
		if self.debug_stop:
			# We're going to stop the process right after export to see what was exported.
			return False, 'DEBUG STOPPED THE PROCESS.'

		export_pbar.update( percent = 1, message = 'Cleaning up scene' )
		vmobu.core.set_current_take( current_take )
		temp_anim_take.FBDelete( )

		vmobu.core.evaluate( )

		# update the ui, in case paths have been changed
		self.update_ui_data( )

		# Reset the time range
		pyfbsdk.FBSystem().CurrentTake.LocalTimeSpan = pyfbsdk.FBTimeSpan( pyfbsdk.FBTime( 0, 0, 0, orig_start_frame, 0 ), pyfbsdk.FBTime( 0, 0, 0, orig_end_frame, 0 ) )

		# return export
		if not export:
			pyfbsdk.FBMessageBox( "Export Error", error_message, "OK" )
			return False, 'Export error'

		else:
			if current_character:
				self.set_character_source( )

			if export_all:
				return True, 'Success'

			else:
				pyfbsdk.FBMessageBox( "Export Done", error_message, "OK" )
				return True, 'Success'

	@staticmethod
	def bake_skeleton_in_hierarchy( root_obj, obj_types = pyfbsdk.FBModelSkeleton ):
		object_hierarchy = vmobu.core.get_hierarchy( root_obj )
		relevant_objects = [ skel for skel in object_hierarchy if isinstance( skel, obj_types ) ]
		vmobu.core.plot_on_objects( relevant_objects, False )

	def get_and_bake_character_face( self, char_namespace, p_bar = None ):
		# If there's a character face in the scene for the selected character, bake it's animation down for export.
		if vmobu.core.get_object_by_name( '{0}:Character_Face'.format( char_namespace ), single_only = True, use_namespace = True, models_only = False, case_sensitive = False ):
			if p_bar:
				p_bar.update( percent =  0.4, message = 'Baking down all animation to head' )

			head_joint = vmobu.core.get_object_by_name( '{0}:*skel:Head'.format( char_namespace ), single_only = True, use_namespace = True, models_only = True, case_sensitive = False )
			self.bake_skeleton_in_hierarchy( head_joint )
			return True

		return False

	def determine_and_bake_asset_type( self, master_node, current_character ):
		asset_type = master_node.PropertyList.Find( 'p_asset_type' )
		if asset_type:
			bake_types = [ 'Weapons', 'Items', 'Vehicles' ]
			if asset_type.Data in bake_types:
				# We do not want to do a character export for our actual export later, so we detect what type the asset is and if it's a weapon/item/vehicle we will remove our knowledge of the "character"
				current_character = None
				self.bake_skeleton_in_hierarchy( master_node )

		return current_character

	def anim_export_batch( self ):
		"""
		Exports batch animation based on current characters in the scene and animations added to their anim node.

		*Arguments:*
		  * ``None``

		*Keyword Arguments:*
		  * ``None``

		*Returns:*
		  * ``None``
		"""

		#Refresh 3d space
		vmobu.core.evaluate()

		#self.refresh_anim_node( )
		self.update_properties ( self.anim_node )
		self.update_properties( self.master_node )
		self.update_anim_properties( )

		application = pyfbsdk.FBApplication( )

		#Grab current row and column in ui, as well as the currently selected animation cell widget
		row = self.anim_list_ui.currentRow( )
		anim_cell_clicked = self.anim_list_ui.cellClicked.connect( self.cell_was_clicked )

		#Get current character
		self.check_anim_node( )

		#Grab currently selected animation cell widget's name and list of characters in the scene
		anim_name = self.anim_list_ui.item( row, 0 )
		for prop in self.anim_node.PropertyList:
			if prop.Name == str( anim_name.text( ) ):
				prop_take_enum = prop.EnumList( 0 )
				prop_take_split = prop_take_enum.split( ":" )
				prop_take = prop_take_split[ 1 ]
			else:
				prop_take = 0

		selection_take = prop_take

		#Grab current character in scene, based off of Actor/Character Controls
		curr_char = application.CurrentCharacter

		# Check the characters version, if the version needs a swap, stop running the tool.
		if not vmobu.mobu_rig_versioning.run( curr_char ):
			return False

		#Set export path from the ui
		set_export_path = os.path.join( core.const.workspace_dir, self.batch_dir.text( ) )

		self.filepath = os.path.join( str( set_export_path ), str( anim_name.text( ) ) + ".anim.fbx" )
		self.filepath = self.filepath.replace( '/', '\\' )

		try:
			file_io.resource_lib._initialize_resourcelib( )
		except:
			pyfbsdk.FBMessageBox( "Export Error", "Could not initialize resourcelib!\n Quitting!", "OK" )
			return False

		for prop in self.anim_node.PropertyList:
			if prop.Name.endswith( "export_rig" ):
				rig_file = prop.Data

		if not rig_file:
			pyfbsdk.FBMessageBox( "Rig Error", "A valid rig has not been set!", "OK" )
			return False
		else:
			rig_file_info = None
			try:
				rig_file_info = file_io.resource_lib._resourcelib.get_file_info( os.path.basename( rig_file ) )
			except RuntimeError:
				pyfbsdk.FBMessageBox( "Export Error", "Rig filename is not a valid resource: {0}.".format( rig_file ), "OK" )
				return False

			if rig_file_info:
				rig_filename = rig_file_info.get_local_relative_filename( )
				for prop in self.anim_node.PropertyList:
					if prop.Name.endswith( "export_rig" ):
						prop.Data = str( rig_filename )
			else:
				pyfbsdk.FBMessageBox( "Rig Error", "A valid rig file has not been set!", "OK" )
				return False

		vmobu.core.evaluate()

		export_nodes_name = self.anim_node.PropertyList.Find( "Bones" )

		#Set export path from the ui
		set_export_path = os.path.join( core.const.workspace_dir, self.batch_dir.text( ) )

		if os.path.exists( set_export_path ):
			#Grab current character's master node
			master = vmobu.core.get_objects_from_wildcard( self.namespace + ":*Master", use_namespace=True, single_only = True )

			#Get start and end frame from selected
			start_frame_item_ui = self.anim_list_ui.item( row, 1 )
			end_frame_item_ui = self.anim_list_ui.item( row, 2 )

			#User's start and end frame based off ui animation cell widget
			user_start_frame = int( start_frame_item_ui.text( ) )
			user_end_frame = int( end_frame_item_ui.text( ) )

			master.Selected = True

			#Set our plotting to skeleton from Ctrl rig
			skeleton = pyfbsdk.FBCharacterPlotWhere.kFBCharacterPlotOnSkeleton

			#Plot to skeleton
			plot_options = pyfbsdk.FBPlotOptions( )
			plot_options.ConstantKeyReducerKeepOneKey = False
			plot_options.PlotAllTakes = True
			plot_options.PlotOnFrame = True

			#Save/export animation
			fbx_options = pyfbsdk.FBFbxOptions( False )
			fbx_options.SaveCharacter = True
			fbx_options.SaveControlSet = False
			fbx_options.SaveCharacterExtension = False
			fbx_options.ShowFileDialog = False
			fbx_options.ShowOptionsDialog = False
			fbx_options.UseASCIIFormat = True

			for take in pyfbsdk.FBSystem( ).Scene.Takes:
				if selection_take == take.Name:
					take_index = take.GetLayerCount( )
					fbx_options.SetTakeSelect( take_index, True )
				else:
					take_index = take.GetLayerCount( )
					fbx_options.SetTakeSelect( take_index, False )

			if anim_cell_clicked:
				curr_char.PlotAnimation( skeleton, plot_options )

				if not master.Selected:
					master.Selected = True

				export_file = os.path.join( str( set_export_path ), str( anim_name.text( ) ) + ".anim.fbx" )

				if export_file :
					self.get_latest( export_file )
					print "Got latest."

					self.checkout( export_file )
					print "Checked out!"
					application.SaveCharacterRigAndAnimation( export_file, curr_char, fbx_options )
					if not file_io.resource_lib.submit( export_file, 'fbx.anim' ):
						pyfbsdk.FBMessageBox( "Crunch Error", "Unable to submit export for crunch.", "OK" )
						return False
					else:
						#self.setup_attributes_for_crunch( )
						master = vmobu.core.get_objects_from_wildcard( self.namespace + ":*Master", use_namespace=True, single_only = True )
						rig_version = master.PropertyList.Find( "p_rig_version" )
						rig_version = rig_version.Data
						if not rig_version:
							print "No rig version set"

						att_dict = { 'associated_character_rig': str( rig_file ), 'rig_version': rig_version,
						             'source_asset_file': file_io.resource_lib.get_relative_filename( pyfbsdk.FBSystem( ).CurrentDirectory( ) ) }
						if not file_io.resource_lib.set_attributes( self.filepath, att_dict ):
							print "Skipping: {0}".format( self.filepath )
							return False
						if os.path.exists( export_file ):
							file_io.resource_lib.crunch( export_file )
							pyfbsdk.FBMessageBox( "Export Status", "Animation exported!\n", "OK" )
							self.set_character_source( )

							backup_file = export_file + ".bck"
							if os.path.exists( backup_file ):
								self.remove_batch_backup_folder( export_file )
							else:
								pass
				else:
					pyfbsdk.FBMessageBox( "Export Error", "No animation to export!\n", "OK" )
		else:
			pyfbsdk.FBMessageBox( "File Path Error", "The current path does not exist.", "OK" )


	def cell_was_clicked( self ):
		"""
		Checks which cell is selected at a given time in the ui.

		*Arguments:*
		  * ``Argument`` Enter a description for the argument here.

		*Keyword Arguments:*
		  * ``Argument`` Enter a description for the keyword argument here.

		*Returns:*
		  * ``Value`` If any, enter a description for the return value here.
		"""

		row = self.anim_list_ui.currentRow( )
		col = self.anim_list_ui.currentColumn( )
		item = self.anim_list_ui.itemAt( row, col )
		self.ID = item.text( )

	def browse_anim_export_dirs( self ):
		"""
		Browses directories for the animation export.

		*Arguments:*
		  * ``Argument`` Enter a description for the argument here.

		*Keyword Arguments:*
		  * ``Argument`` Enter a description for the keyword argument here.

		*Returns:*
		  * ``Value`` If any, enter a description for the return value here.
		"""

		#Make sure to get the anim node so it has the fresh anim node every time
		self.check_anim_node()

		browse_dialog = PySide.QtGui.QFileDialog( self )
		browse_dialog.setFileMode( PySide.QtGui.QFileDialog.Directory )
		browse_dialog.setOption( PySide.QtGui.QFileDialog.ShowDirsOnly )
		browse_dialog.setHistory( os.path.join( core.const.workspace_dir, str( self.export_dir_ui.text( ) ) ) )
		browse_dialog.setFileMode( PySide.QtGui.QFileDialog.ExistingFile )

		start_dir = os.path.join( core.const.workspace_dir, 'data' )
		current_path = os.path.join( core.const.workspace_dir, str( self.export_dir_ui.text( ) ) )
		if os.path.lexists( current_path ):
			start_dir = current_path

		anim_path = browse_dialog.getExistingDirectory( self, '', start_dir )
		if anim_path:
			if core.const.workspace_dir.lower( ) in anim_path.lower( ):

				# make sure the path is valid, and update the anim
				valid_anim_path, anim_path, error_message = vmobu.mobu_export.mb_export.validate_anim_path( self.anim_node, self.master_node, anim_path )
				if valid_anim_path:

					anim_path = anim_path.lower( ).replace( core.const.workspace_dir.lower( ), '' )
					self.export_dir_ui.setText( anim_path )

				else:
					pyfbsdk.FBMessageBox( 'File path error', error_message, 'OK' )
					return False

				if self.export_dir_ui.text( ) != "":
					self.animx_clear_ui.setEnabled( True )

			else:
				pyfbsdk.FBMessageBox( "File Path Error", "The current export path is not based in your project.", "OK" )
				return False

	def browse_rig_export_dirs( self ):
		"""
		Browses directories for the rig export.

		*Arguments:*
		  * ``Argument`` Enter a description for the argument here.

		*Keyword Arguments:*
		  * ``Argument`` Enter a description for the keyword argument here.

		*Returns:*
		  * ``Value`` If any, enter a description for the return value here.
		"""

		browse_dialog = PySide.QtGui.QFileDialog( )
		browse_dialog.setFileMode( PySide.QtGui.QFileDialog.Directory )
		browse_dialog.setOption( PySide.QtGui.QFileDialog.ShowDirsOnly )

		start_dir = os.path.join( core.const.workspace_dir, 'data' )
		current_path = os.path.join( core.const.workspace_dir, str( self.rigx_file_edit_ui.text( ) ) )
		if os.path.lexists( current_path ):
			start_dir = current_path

		rig_file = browse_dialog.getOpenFileName( None, 'Select a rig.fbx file', dir =start_dir, filter = 'Rig files (*.rig.fbx )' )
		if rig_file[0]:
			rig_file = rig_file[0]

			# make sure the path is valid
			valid_rig_file, return_value, error_message = vmobu.mobu_export.mb_export.validate_rig_file( self.anim_node, self.master_node, rig_file )
			if valid_rig_file:
				rig_file = return_value
				rig_file = rig_file.lower( ).replace( core.const.workspace_dir.lower( ), '' )
				self.rigx_file_edit_ui.setText( rig_file )

			else:
				pyfbsdk.FBMessageBox( 'Rig Error', error_message, 'OK' )
				return False

			if self.export_dir_ui.text( ) != "":
				self.rigx_clear_ui.setEnabled( True )

		else:
			pyfbsdk.FBMessageBox( "Rig Error", "The current export path is not based in your project.", "OK" )
			return


	def browse_batch_dirs( self ):
		"""
		Browses directories for the batch export.

		*Arguments:*
		  * ``Argument`` Enter a description for the argument here.

		*Keyword Arguments:*
		  * ``Argument`` Enter a description for the keyword argument here.

		*Returns:*
		  * ``Value`` If any, enter a description for the return value here.
		"""

		browse_dialog = PySide.QtGui.QFileDialog( self )
		browse_dialog.setFileMode( PySide.QtGui.QFileDialog.Directory )
		browse_dialog.setOption( PySide.QtGui.QFileDialog.ShowDirsOnly )
		browse_dialog.setHistory( os.path.join( core.const.workspace_dir, str( self.batch_dir.text( ) ) ) )
		browse_dialog.setFileMode( PySide.QtGui.QFileDialog.ExistingFile )

		export_path = browse_dialog.getExistingDirectory( self, '', os.path.join( core.const.workspace_dir, str( self.batch_dir.text( ) ) ) )

		if export_path:
			if core.const.workspace_dir.lower( ) in export_path.lower( ):

				# RH-TO-DO Add Package Check
				export_path = export_path.lower( ).replace( core.const.workspace_dir.lower( ), '' )
				export_path = export_path + "\\"
				self.batch_dir.setText( export_path )

				# RH-TO-DO Refresh Anim Node, Master Node paths

				if self.batch_dir.text( ) != "":
					self.animx_clear_ui.setEnabled( True )
			else:
				pyfbsdk.FBMessageBox( "File Path Error", "The current export path is not based in your project.", "OK" )
				return

	@vmobu.decorators.toggle_auto_key
	def refresh_anim_node( self, refresh_anim=True, auto_fix=False, quiet=False ):
		"""
		Refreshes the active anim node.

		*Arguments:*
		  * ``Argument`` Enter a description for the argument here.

		*Keyword Arguments:*
		  * ``Argument`` Enter a description for the keyword argument here.

		*Returns:*
		  * ``Value`` If any, enter a description for the return value here.
		"""
		# Get the old selection indices
		old_selection = self.anim_list_ui.selectionModel( ).selectedRows( )

		#Set the current index so it goes back to the current index of the anim node after refresh
		curr_index = self.character_combo_ui.currentIndex()

		#Set new project directory path
		self.project_dir = file_io.v_path.Path( core.const.workspace_dir.replace( '\\', '/' )[  :-1  ] ).splitdrive( )[
		   1  ].replace( '/projects/', '' )

		self.anim_exporter_widget.projectLineEdit.setText( str( self.project_dir ) )

		self.check_for_anim_node()
		self.check_for_master_node()

		if refresh_anim:
			# Then update everything
			self.update_properties( self.anim_node, update_path=False )
			self.update_properties( self.master_node, update_path=False )
			self.update_anim_properties()

		vmobu.core.evaluate()

		self.character_combo_ui.clear( )

		#Check the type of the anim drop-down
		if type( self.character_combo_ui ) == PySide.QtGui.QComboBox:
			try:
				self.update_anim_nodes_list()

				self.anim_exporter_widget.tabWidget.setEnabled( True )

				if not self.anim_node:
					#self.tab_widget.setEnabled( False )
					return False

			except RuntimeError, e:
				#Try to close
				self.close_event( )
				return False

		if refresh_anim:
			for row in range(self.anim_list_ui.rowCount( ) ):
				self.anim_list_ui.removeRow( row )
			# After the deletion, is there still any rows in the table?
			if self.anim_list_ui.rowCount():
				# Be sure there are no rows left
				for row in range(self.anim_list_ui.rowCount( ) ):
					self.anim_list_ui.removeRow(row)

			vmobu.core.evaluate()

			self.character_combo_ui.setCurrentIndex( curr_index )
			self.update_widget_for_curr_node( )
			self.repopulate_cells( )
			self.update_properties( self.anim_node )
			self.update_properties( self.master_node )

			vmobu.core.evaluate()

			self.update_anim_properties( )

			anim_controller = self.get_anim_controller( )
			if anim_controller:
				self.anim_controller_edit_ui.setText( anim_controller.LongName )

		elif not refresh_anim:
			self.update_ui_data()

			vmobu.core.evaluate()

		# Clear selection
		self.anim_list_ui.clearSelection()

		# Restore old selection
		for item in old_selection:
			self.anim_list_ui.selectRow( item.row() )

		return True

	def update_anim_properties( self ):
		"""
		Updates the properties of the currently selected animation in the exporter.

		*Arguments:*
		  * ``Argument`` Enter a description for the argument here.

		*Keyword Arguments:*
		  * ``Argument`` Enter a description for the keyword argument here.

		*Returns:*
		  * ``Value`` If any, enter a description for the return value here.
		"""

		if self.anim_list_ui.rowCount( ) > 0:
			self.check_anim_node( )
			row = self.anim_list_ui.currentRow( )

			#Check properties of current anim node and remove anim properties and recreate them
			self.remove_anim_node_properties()

			vmobu.core.evaluate()
			self.store_anim_takes( )

			vmobu.core.evaluate()

			indexes = self.anim_list_ui.selectionModel( ).selectedRows( )
			for index in sorted( indexes ):
				item = self.anim_list_ui.itemFromIndex( index )
				if item is None:
					pyfbsdk.FBMessageBox( "Selection Error", "Please select an animation within the UI.", "OK" )
				else:
					if self.anim_list_ui.rowCount() > 0:
						try:
							#Get user start and end frames from ui
							start_frame_item_ui = self.anim_list_ui.item( row, 1 )
							end_frame_item_ui = self.anim_list_ui.item( row, 2 )

							user_start_frame = int( start_frame_item_ui.text( ) )
							user_end_frame = int( end_frame_item_ui.text( ) )

							#Set timerange of the current take based off the ui
							for row in range( self.anim_list_ui.rowCount( ) ):
								curr_anim_name_item_ui = self.anim_list_ui.item( row, 0 )

							vmobu.core.evaluate()
						except AttributeError:
							self.logger.warning('There are no animations')

		return True

	def update_properties( self, node, update_path = True ):
		"""
		Updates the properties of the passed node based off the values in the UI.

		*Arguments:*
		  * ``Node`` Node that the properties are being placed onto

		*Keyword Arguments:*
		  * ``Argument`` Enter a description for the keyword argument here.

		*Returns:*
		  * ``Value`` If any, enter a description for the return value here.
		"""

		# Get the old selection indices
		old_selection = self.anim_list_ui.selectionModel( ).selectedRows( )

		#Check current anim node and current row and column
		if self.anim_list_ui.rowCount( ) < 0:
			return False

		vmobu.core.evaluate( )
		self.check_anim_node( )

		old_selection = self.anim_list_ui.selectionModel( ).selectedRows( )
		#self.anim_list_ui.selectAll( )

		indexes = self.anim_list_ui.selectionModel( ).selectedRows( )
		for index in sorted( indexes ):
			item = self.anim_list_ui.itemFromIndex( index )
			if item is None:
				pyfbsdk.FBMessageBox( "Selection Error", "Please select an animation within the UI.", "OK" )
			else:
				current_row = index.row( )

				#Check all items in current animation row
				curr_anim_name_item_ui = self.anim_list_ui.item( current_row, 0 )
				curr_start_frame_item_ui = self.anim_list_ui.item( current_row, 1 )
				curr_end_frame_item_ui = self.anim_list_ui.item( current_row, 2 )
				curr_ramp_in_item_ui = self.anim_list_ui.item( current_row, 3 )
				curr_ramp_out_item_ui = self.anim_list_ui.item( current_row, 4 )
				curr_framerate_item_ui = self.anim_list_ui.item( current_row, 5 )

				#Step through properties of the node and update them according to anim node properties
				if node:
					for prop in node.PropertyList:
						if prop.IsUserProperty( ):
							if prop.Name ==  "p_export_framestart":
								prop.Data = int( curr_start_frame_item_ui.text( ) )
							elif prop.Name ==  "p_export_frameend" :
								prop.Data = int( curr_end_frame_item_ui.text( ) )
							elif prop.Name == "p_export_rampin":
								prop.Data = int( curr_ramp_in_item_ui.text( ) )
							elif prop.Name == "p_export_rampout":
								prop.Data = int( curr_ramp_out_item_ui.text( ) )
							elif prop.Name == "p_export_framerate":
								prop.Data = int( curr_framerate_item_ui.text( ) )
							elif prop.Name == "p_export_anim":
								prop.Data = str( curr_anim_name_item_ui.text( ) )
				vmobu.core.evaluate( )

		#Set value of p properties in anim node based off values from UI
		if update_path:
			if node:
				prop = node.PropertyList.Find( 'p_anim_file' )
				if not prop:
					# If it's not on the master node, we need this. Add it.
					prop = vmobu.core.add_property_obj( node, 'p_anim_file', str( self.export_dir_ui.text( ) ), force = True )
				prop.Data = str( self.export_dir_ui.text( ) )

		# Clear selection
		self.anim_list_ui.clearSelection( )

		# Restore old selection
		for item in old_selection:
			self.anim_list_ui.selectRow( item.row( ) )


	def check_for_anim_node( self ):
		"""
		Checks for an anim node in the scene.

		*Arguments:*
		  * ``Argument`` Enter a description for the argument here.

		*Keyword Arguments:*
		  * ``Argument`` Enter a description for the keyword argument here.

		*Returns:*
		  * ``Value`` If any, enter a description for the return value here.
		"""

		#Check all notes in scene and verify the anim nodes
		anim_node_found = False
		for note in pyfbsdk.FBSystem( ).Scene.Notes:
			if note.Name.endswith( 'anim_node' ):
				print "------------------------------------------"
				print "Anim node " + note.LongName + " found!"
				anim_node_found = True

		if not anim_node_found:
			pyfbsdk.FBMessageBox( "WARNING:", "\n" + "There is currently no anim node, or the anim node\n" +  "in your scene is incorrectly setup.\n" +  "Please contact a TA to fix this issue.", "OK" )

		if vmobu.core.is_obj_unbound( self.anim_node ):
			self.anim_node = vmobu.core.get_object_by_name('{0}:anim_node'.format( self.namespace ), use_namespace=True,
			                                               case_sensitive=False )

	def check_for_master_node( self ):
		if vmobu.core.is_obj_unbound( self.master_node ):
			self.master_node = vmobu.core.get_object_by_name('{0}:Master'.format( self.namespace ), use_namespace=True,
			                                                 case_sensitive=False )
		return True

	def store_anim_takes( self ):
		"""
		Stores the current take within the UI to the properties of the anim node.

		*Arguments:*
		  * ``Argument`` Enter a description for the argument here.

		*Keyword Arguments:*
		  * ``Argument`` Enter a description for the keyword argument here.

		*Returns:*
		  * ``Value`` If any, enter a description for the return value here.
		"""

		#Get current index of the anim node drop-down
		curr_index = self.character_combo_ui.currentIndex( )
		self.character_combo_ui.itemData( curr_index )
		curr_combo_item_string = self.character_combo_ui.currentText( )

		preserved_anim = {}
		if not len(preserved_anim) < 1:
			preserved_anim.clear()

		#Get current take
		#curr_take = vmobu.core.get_current_take( )

		#Get current row and column from ui
		if self.anim_list_ui.rowCount() < 1:
			row = 0
			self.last_selected_index = 0
		else:
			row = self.anim_list_ui.currentRow( )
			self.last_selected_index = self.anim_list_ui.currentRow( )
		#self.remove_anim_node_properties( )

		self.check_anim_node()

		vmobu.core.evaluate()

		self.remove_anim_node_properties()
		vmobu.core.evaluate()

		#Check all notes in scene for anim nodes
		for anim_node in pyfbsdk.FBSystem( ).Scene.Notes:
			if anim_node.LongName == curr_combo_item_string:
				anim_node_parent = anim_node.Parents.Name
				for row in range( self.anim_list_ui.rowCount( ) ):
					curr_anim_name_item_ui = self.anim_list_ui.item( row, 0 )

					for prop in self.anim_node.PropertyList:
						if str( curr_anim_name_item_ui.text( ) ) == prop.Name:
							continue

					start_frame_item_ui = self.anim_list_ui.item( row, 1 )
					end_frame_item_ui = self.anim_list_ui.item( row, 2 )
					ramp_in_item_ui = self.anim_list_ui.item( row, 3 )
					ramp_out_item_ui = self.anim_list_ui.item( row, 4 )
					framerate_item_ui = self.anim_list_ui.item( row, 5 )
					take_name_item_ui = self.anim_list_ui.cellWidget( row, 6 )

					if take_name_item_ui:
						take_name_item_ui = take_name_item_ui.currentText()

					#Create new animation property in anim node with enum list for values
					self.anim_node_anim_property = anim_node.PropertyCreate( str( curr_anim_name_item_ui.text( ) ), pyfbsdk.FBPropertyType.kFBPT_enum, "Enum", False, True, None )

					#Set values for enum list
					curr_take_item_ui = "take:" + str( take_name_item_ui )
					start_frame_text = "startFrame:" + str( start_frame_item_ui.text( ) )
					end_frame_text = "endFrame:" + str( end_frame_item_ui.text( ) )

					if ramp_in_item_ui:
						ramp_in_text = "rampIn:" + str( ramp_in_item_ui.text( ) )
					else:
						ramp_in_text = "rampIn: 5"

					if ramp_out_item_ui:
						ramp_out_text = "rampOut:" + str( ramp_out_item_ui.text( ) )
					else:
						ramp_out_text = "rampOut: 5"

					if framerate_item_ui:
						framerate_text = "frameRate:" + str( framerate_item_ui.text( ) )
					else:
						framerate_text = "frameRate: 30"

					#Add enum list to property
					anim_node_anim_prop_enum_list = self.anim_node_anim_property.GetEnumStringList( True )
					anim_node_anim_prop_enum_list.Add( curr_take_item_ui )
					anim_node_anim_prop_enum_list.Add( start_frame_text )
					anim_node_anim_prop_enum_list.Add( end_frame_text )
					anim_node_anim_prop_enum_list.Add( ramp_in_text )
					anim_node_anim_prop_enum_list.Add( ramp_out_text )
					anim_node_anim_prop_enum_list.Add( framerate_text )

					#Verify the enum list has changed to update
					self.anim_node_anim_property.NotifyEnumStringListChanged( )

		del(preserved_anim)

		self.cleanup_anim_properties()

		return True


	def cleanup_anim_properties(self):
		"""
		Cleans up any duplicate animation properties on the anim node that aren't stored by the user.

		*Arguments:*
		  * ``None``

		*Keyword Arguments:*
		  * ``None``

		*Returns:*
		  * ``True``
		"""

		verified_anim_props = []
		if not self.anim_node:
			return False, 'No valid anim node found'

		#Add the animation from the exporter to the list
		for row in range(self.anim_list_ui.rowCount()):
			curr_anim_name_item_ui = self.anim_list_ui.item(row, 0)
			if str(curr_anim_name_item_ui.text()) not in verified_anim_props:
				verified_anim_props.append(str(curr_anim_name_item_ui.text()))

		#Check if the animation properties are already a match within the list, if not, delete them
		for prop in self.anim_node.PropertyList:
			if prop.IsUserProperty():
				if not prop.Name.startswith("wg"):
					if not prop.Name == "Bones":
						if not prop.Name.startswith("uid") or not prop.Name == "uid":
							if not prop.Name.startswith("p_"):
								if prop.Name not in verified_anim_props:
									self.anim_node.PropertyRemove(prop)
									vmobu.core.evaluate()

		return True


	def remove_anim_node_properties( self, second_time = False ):
		"""
		Removes animation properties to reapply them when adding new animations and updating current animations.

		*Arguments:*
		  * ``Argument`` Enter a description for the argument here.

		*Keyword Arguments:*
		  * ``Argument`` Enter a description for the keyword argument here.

		*Returns:*
		  * ``Value`` If any, enter a description for the return value here.
		"""

		#Get current anim node
		vmobu.core.evaluate()
		self.check_anim_node( )

		#Remove animation properties from anim node for new creation
		if self.anim_node:
			for prop in self.anim_node.PropertyList:
				if prop.IsUserProperty( ):
					if not prop.Name.startswith( "p_" ):
						if not prop.Name == "Bones":
							if not prop.Name.startswith( "wg" ):
								if not prop.Name.startswith("uid") or not prop.Name == "uid":
									self.anim_node.PropertyRemove( prop )

		vmobu.core.evaluate()
		if second_time:
			return True

		# Run the deletion one more time for good measure.
		self.remove_anim_node_properties( second_time=True )



	def read_apply_window_attribute_settings( self ):
		"""
		Read and applies the settings of your last session of the UI.

		*Arguments:*
		  * ``Argument`` Enter a description for the argument here.

		*Keyword Arguments:*
		  * ``Argument`` Enter a description for the keyword argument here.

		*Returns:*
		  * ``Value`` If any, enter a description for the return value here.
		"""

		#Set ui settings
		settings = PySide.QtCore.QSettings( )
		settings.beginGroup( "mainWindow" )

		#Restore the placement and dimensions of ui upon reopen
		self.restoreGeometry(settings.value( "geometry", self.saveGeometry( ) ) )
		self.restoreState(settings.value( "saveState", self.saveState( ) ) )
		self.move(settings.value( "pos", self.pos( ) ) )
		self.resize(settings.value( "size", self.size( ) ) )
		if settings.value( "maximized", self.isMaximized( ) ):
			self.showMaximized( )

		settings.endGroup( )

		self.write_window_attribute_settings( )


	def write_window_attribute_settings( self ):
		"""
		Saves the session of the UI.

		*Arguments:*
		  * ``Argument`` Enter a description for the argument here.

		*Keyword Arguments:*
		  * ``Argument`` Enter a description for the keyword argument here.

		*Returns:*
		  * ``Value`` If any, enter a description for the return value here.
		"""

		#Set window settings from the UI
		settings = PySide.QtCore.QSettings( )
		settings.beginGroup( "mainWindow" )
		settings.setValue( "geometry", self.saveGeometry( ) )
		settings.setValue( "saveState", self.saveState( ) )
		settings.setValue( "maximized", self.isMaximized( ) )
		if not self.isMaximized( ):
			settings.setValue( "pos", self.pos( ) )
			settings.setValue( "size", self.size( ) )
		else:
			settings.setValue( "pos", self.pos( ) )
			settings.setValue( "size", self.size( ) )

		settings.endGroup( )


	def copy_anim_export_path( self ):
		"""
		Copies the animation export path.

		*Arguments:*
		  * ``Argument`` Enter a description for the argument here.

		*Keyword Arguments:*
		  * ``Argument`` Enter a description for the keyword argument here.

		*Returns:*
		  * ``Value`` If any, enter a description for the return value here.
		"""

		#Store current text in export path into clipboard
		clipboard = PySide.QtGui.QApplication.clipboard( )


	def paste_anim_export_path( self ):
		"""
		Pastes the animation export path from clipboard.

		*Arguments:*
		  * ``Argument`` Enter a description for the argument here.

		*Keyword Arguments:*
		  * ``Argument`` Enter a description for the keyword argument here.

		*Returns:*
		  * ``Value`` If any, enter a description for the return value here.
		"""

		#Paste text from clipboard into export path
		clipboard = PySide.QtGui.QApplication.clipboard( )
		mime_data = clipboard.mimeData( )
		if mime_data and mime_data.hasText( ):
			# make sure the path is valid, and update the anim
			valid_anim_path, anim_path, error_message = vmobu.mobu_export.mb_export.validate_anim_path( self.anim_node, self.master_node, mime_data.text( ) )
			if valid_anim_path:

				anim_path = anim_path.lower( ).replace( core.const.workspace_dir.lower( ), '' )
				self.export_dir_ui.setText( anim_path )

			else:
				pyfbsdk.FBMessageBox( 'File path error', error_message, 'OK' )
				return False

			if self.export_dir_ui.text( ) != "":
				self.animx_clear_ui.setEnabled( True )


	def clear_anim_export_path( self ):
		"""
		Clears the animation export path from the UI.

		*Arguments:*
		  * ``Argument`` Enter a description for the argument here.

		*Keyword Arguments:*
		  * ``Argument`` Enter a description for the keyword argument here.

		*Returns:*
		  * ``Value`` If any, enter a description for the return value here.
		"""
		pass


	def update_bones_list( self ):
		"""
		Adds the bones to the bones list in the UI.

		*Arguments:*
		  * ``Argument`` Enter a description for the argument here.

		*Keyword Arguments:*
		  * ``Argument`` Enter a description for the keyword argument here.

		*Returns:*
		  * ``Value`` If any, enter a description for the return value here.
		"""

		#Check the parent (master node) of the anim node and add bones to the array
		self.check_anim_node()
		if self.anim_node:

			self.namespace = self.anim_node.LongName.split( ":" )[ 0 ]

			namespace_list = vmobu.core.get_objects_from_wildcard( "{0}:*".format( self.namespace ), use_namespace=True )
			for node in pyfbsdk.FBSystem( ).Scene.Components:
				p_bone_name = node.PropertyList.Find( 'p_bone_name' )
				if p_bone_name:
					if self.namespace.lower( ) == node.LongName.split( ':' )[ 0 ].lower( ):
						if self.weapon_enabled_cb.isChecked():
							if node.Name in vmobu.const.MOBU_CHAR_TO_LEGACY_CHARACTER_BIP.keys():
								continue
						if vmobu.core.get_property( node, 'p_bone_name' ):
							self.bone_list_ui.addItem( str( node.LongName ) )


	def update_tags_list( self ):
		"""
		Adds the tags list from your scene within the UI

		*Arguments:*
		  * ``Argument`` Enter a description for the argument here.

		*Keyword Arguments:*
		  * ``Argument`` Enter a description for the keyword argument here.

		*Returns:*
		  * ``Value`` If any, enter a description for the return value here.
		"""

		#Check the parent (master node) of the anim node and add bones to the array
		if self.anim_node:

			self.namespace = self.anim_node.LongName.split(":")[0]

			namespace_list = vmobu.core.get_objects_from_wildcard("{0}*:*".format(self.namespace), use_namespace=True)
			for node in pyfbsdk.FBSystem().Scene.Components:
				p_tag_name = node.PropertyList.Find('p_tag_name')
				if p_tag_name:
					if self.namespace in node.LongName and "tag" in node.LongName:
						self.prop_list_ui.addItem(str(node.LongName))


	def add_bone( self ):
		"""
		Adds a bone to the bone list based off if selection is a bone.

		*Arguments:*
		  * ``Argument`` Enter a description for the argument here.

		*Keyword Arguments:*
		  * ``Argument`` Enter a description for the keyword argument here.

		*Returns:*
		  * ``Value`` If any, enter a description for the return value here.
		"""

		curr_sel = pyfbsdk.FBModelList( )
		pyfbsdk.FBGetSelectedModels( curr_sel )
		for bone in curr_sel:
			#if bone and bone.ClassName( ) == "FBModelSkeleton":
			self.bone_list_ui.addItem( str( bone.LongName ) )
			for prop in bone.PropertyList:
				if not prop.Name == 'p_bone_name':
					p_bone_name_prop = bone.PropertyCreate( 'p_bone_name', pyfbsdk.FBPropertyType.kFBPT_stringlist, "String", False, True, None )
					p_bone_name_prop.Data = bone.Name


	def add_tag( self ):
		"""
		Adds a tag to the tag list based off of selection.

		*Arguments:*
		  * ``Argument`` Enter a description for the argument here.

		*Keyword Arguments:*
		  * ``Argument`` Enter a description for the keyword argument here.

		*Returns:*
		  * ``Value`` If any, enter a description for the return value here.
		"""

		curr_sel = pyfbsdk.FBModelList( )
		pyfbsdk.FBGetSelectedModels( curr_sel )
		for tag in curr_sel:
			#if tag and tag.ClassName( ) != "FBModelSkeleton":
			p_tag_name = tag.PropertyList.Find('p_tag_name')
			if p_tag_name:
				self.prop_list_ui.addItem( str( tag.LongName ) )


	def move_anim_row_down( self ):
		"""
		Moves the currently selected animation, in the ui, down.

		*Arguments:*
		  * ``Argument`` Enter a description for the argument here.

		*Keyword Arguments:*
		  * ``Argument`` Enter a description for the keyword argument here.

		*Returns:*
		  * ``Value`` If any, enter a description for the return value here.
		"""

		row = self.anim_list_ui.currentRow( )
		column = self.anim_list_ui.currentColumn( )
		if row < self.anim_list_ui.rowCount( ) - 1:
			self.anim_list_ui.insertRow( row+2 )
			for col in range( self.anim_list_ui.columnCount( ) ):
				self.anim_list_ui.setItem( row+2, col, self.anim_list_ui.takeItem( row, col ) )
				self.anim_list_ui.setCurrentCell( row+2, column )
			self.anim_list_ui.removeRow( row )


	def move_anim_row_up( self ):
		"""
		Moves the currently selected animation, in the ui, up.

		*Arguments:*
		  * ``Argument`` Enter a description for the argument here.

		*Keyword Arguments:*
		  * ``Argument`` Enter a description for the keyword argument here.

		*Returns:*
		  * ``Value`` If any, enter a description for the return value here.
		"""

		row = self.anim_list_ui.currentRow( )
		column = self.anim_list_ui.currentColumn( )
		if row > 0:
			self.anim_list_ui.insertRow( row-1 )
			for col in range( self.anim_list_ui.columnCount( ) ):
				self.anim_list_ui.setItem( row-1, col, self.anim_list_ui.takeItem( row+1, col ) )
				self.anim_list_ui.setCurrentCell( row-1, column )
			self.anim_list_ui.removeRow( row+1 )


	def copy_all_sel_anim( self ):
		"""
		Copies anim property based off the selection in the ui and creates a copied property on the necessary anim node.

		*Arguments:*
		  * ``Argument`` Enter a description for the argument here.

		*Keyword Arguments:*
		  * ``Argument`` Enter a description for the keyword argument here.

		*Returns:*
		  * ``Value`` If any, enter a description for the return value here.
		"""

		#Get current row and column of the ui
		row = self.anim_list_ui.currentRow( )
		column = self.anim_list_ui.currentColumn( )

		#Get current anim node
		self.check_anim_node( )

		#Get currently selected animation
		curr_anim = self.anim_list_ui.item( row, 0 )

		#Go through properties of anim node for the matching property
		for prop in self.anim_node.PropertyList:
			if prop.Name == str( curr_anim.text( ) ):
				#Go through the animation property, of the anim node, enum list
				anim_node_take_enum = prop.EnumList( 0 )
				anim_node_take_split = anim_node_take_enum.split( ":" )
				anim_node_take = anim_node_take_split[ 1 ]

				anim_node_start_frame_enum = prop.EnumList( 1 )
				anim_node_start_frame_split = anim_node_start_frame_enum.split( ":" )
				anim_node_start_frame = anim_node_start_frame_split[ 1 ]

				anim_node_end_frame_enum = prop.EnumList( 2 )
				anim_node_end_frame_split = anim_node_end_frame_enum.split( ":" )
				anim_node_end_frame = anim_node_end_frame_split[ 1 ]

				anim_node_ramp_in_enum = prop.EnumList( 3 )
				anim_node_ramp_in_split = anim_node_ramp_in_enum.split( ":" )
				anim_node_ramp_in = anim_node_ramp_in_split[ 1 ]

				anim_node_ramp_out_enum = prop.EnumList( 4 )
				anim_node_ramp_out_split = anim_node_ramp_out_enum.split( ":" )
				anim_node_ramp_out = anim_node_ramp_out_split[ 1 ]

				anim_node_framerate_enum = prop.EnumList( 5 )
				anim_node_framerate_split = anim_node_framerate_enum.split( ":" )
				anim_node_framerate = anim_node_framerate_split[ 1 ]

				#Create the copy animation property
				new_anim_prop_enum = self.anim_node.PropertyCreate( prop.Name, pyfbsdk.FBPropertyType.kFBPT_enum, "Enum", False, True, None )
				new_anim_prop_enum_list = new_anim_prop_enum.GetEnumStringList( True )

				#Set values for enum list
				take_name_text = "take:" + anim_node_take
				start_frame_text = "startFrame:" + anim_node_start_frame
				end_frame_text = "endFrame:" + anim_node_end_frame
				ramp_in_text = "rampIn:" + anim_node_ramp_in
				ramp_out_text = "rampOut:" + anim_node_ramp_out
				framerate_text = "frameRate:" + anim_node_framerate

				#Add enum list to property
				new_anim_prop_enum_list.Add( take_name_text )
				new_anim_prop_enum_list.Add( start_frame_text )
				new_anim_prop_enum_list.Add( end_frame_text )
				new_anim_prop_enum_list.Add( ramp_in_text )
				new_anim_prop_enum_list.Add( ramp_out_text )
				new_anim_prop_enum_list.Add( framerate_text )

				#Verify the enum list has changed to update
				new_anim_prop_enum.NotifyEnumStringListChanged( )

				for take in pyfbsdk.FBSystem( ).Scene.Takes:
					if take.Name == anim_node_take:
						take.CopyTake( "new_" + anim_node_take )


	def paste_all_sel_anim( self ):
		"""
		Pastes copied animation into the ui.

		*Arguments:*
		  * ``Argument`` Enter a description for the argument here.

		*Keyword Arguments:*
		  * ``Argument`` Enter a description for the keyword argument here.

		*Returns:*
		  * ``Value`` If any, enter a description for the return value here.
		"""

		#Check the number of animations in the ui and remove them for ui repopulation
		for row in range( self.anim_list_ui.rowCount( ) ):
			self.anim_list_ui.removeRow( row )

		self.repopulate_cells( )


	def get_anim_path( self ):
		"""
		Get the animation path from the anim_node

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``
		"""

		#Get current anim node and get it's parent (master node)
		anim_path = ''
		if self.anim_node:
			anim_path = vmobu.core.get_property( self.anim_node, 'p_anim_file', return_value=True )

			# validate and fix the anim_path
			valid_anim_path, return_value, error_message = vmobu.mobu_export.mb_export.validate_anim_path( self.anim_node, self.master_node, anim_path )
			if valid_anim_path:
				anim_path = return_value

		return anim_path


	def get_rig_path( self ):
		"""
		Grabs the rig path of the current character.

		*Arguments:*
		  * ``Argument`` Enter a description for the argument here.

		*Keyword Arguments:*
		  * ``Argument`` Enter a description for the keyword argument here.

		*Returns:*
		  * ``Value`` If any, enter a description for the return value here.
		"""

		#Get current anim node and get it's parent (master node)
		rig_file = ''
		if self.anim_node:
			rig_file = vmobu.core.get_property( self.anim_node, 'p_export_rig' )

		return rig_file


	def get_anim_controller( self ):
		"""
		Finds the anim controller for the current character.

		*Arguments:*
		  * ``Argument`` Enter a description for the argument here.

		*Keyword Arguments:*
		  * ``Argument`` Enter a description for the keyword argument here.

		*Returns:*
		  * ``Value`` If any, enter a description for the return value here.
		"""

		#Get current anim node and walk hierarchy to find Animation Controller
		anim_controller = None
		if self.anim_node:
			if not self.namespace:
				self.namespace = vmobu.core.get_namespace_from_obj( self.anim_node, as_string = True )

			anim_controller = vmobu.core.get_objects_from_wildcard( self.namespace + "*:AnimationController", use_namespace=True, single_only = True )

		return anim_controller


	def copy_rig_export_path( self ):
		"""
		Copies the export rig path.

		*Arguments:*
		  * ``Argument`` Enter a description for the argument here.

		*Keyword Arguments:*
		  * ``Argument`` Enter a description for the keyword argument here.

		*Returns:*
		  * ``Value`` If any, enter a description for the return value here.
		"""

		#Copy current text in export path to clipboard
		clipboard = PySide.QtGui.QApplication.clipboard( )


	def paste_rig_export_path( self ):
		"""
		Pastes the export rig path from clipboard.

		*Arguments:*
		  * ``Argument`` Enter a description for the argument here.

		*Keyword Arguments:*
		  * ``Argument`` Enter a description for the keyword argument here.

		*Returns:*
		  * ``Value`` If any, enter a description for the return value here.
		"""

		#Paste current text from clipboard to rig export path
		clipboard = PySide.QtGui.QApplication.clipboard( )
		mime_data = clipboard.mimeData( )
		if mime_data and mime_data.hasText( ):

			# make sure this is a valid file
			valid_rig, rig_filename, error_message = vmobu.mobu_export.mb_export.validate_rig_file( self.anim_node, self.master_node, mime_data.text( ) )
			if valid_rig:
				self.rigx_file_edit_ui.setText( rig_filename )
			else:
				pyfbsdk.FBMessageBox( 'Rig Error', error_message, 'OK' )


	def clear_rig_path( self ):
		"""
		Clears the export rig path.

		*Arguments:*
		  * ``Argument`` Enter a description for the argument here.

		*Keyword Arguments:*
		  * ``Argument`` Enter a description for the keyword argument here.

		*Returns:*
		  * ``Value`` If any, enter a description for the return value here.
		"""

		self.rigx_file_edit_ui.setText( '' )
		#self.rigx_clear_ui.setEnabled( False )

	def setup_camera_anim_ramp( self, char_namespace ):
		self.character_camera = None

		# Get the camera bone
		for camera in vmobu.core.system.Scene.Cameras:
			if camera.LongName.split(':')[ 0 ].lower( ) == char_namespace.lower( ):
				self.character_camera = camera
				break

		if not self.character_camera:
			# Set the association list to be empty.
			self.camera_property_association = []
			return False

		# Check to see if the property already is there
		prop = self.character_camera.PropertyList.Find( CAMERA_WEIGHT_PROPERTY )
		if not prop:
			# We add it if it's not there.
			prop = vmobu.core.add_property_obj( self.character_camera, prop_name= CAMERA_WEIGHT_PROPERTY, prop_value = 1.0 )
			prop.SetMin( 0, True )
			prop.SetMax( 1, True )

		# Update the camera properties association list
		self.camera_property_association = [ ( prop, self.camera_animation_slider ), ( prop, self.camera_animation_slider_edit ) ]

	def update_sliders( self ):
		try:
			for prop_tuple in self.camera_property_association:
				prop = prop_tuple[0]
				ui_element = prop_tuple[ 1 ]

				# If this ui element is a slider
				if isinstance( ui_element, PySide.QtGui.QAbstractSlider ):
					# We update the slider to be the value of the prop
					ui_element.setValue( prop.Data * 100.0 )

				if isinstance( ui_element, PySide.QtGui.QLineEdit ):
					ui_element.setText( str( '{0:.2f}'.format( prop.Data ) ) )
		except:
			self.setup_camera_anim_ramp( self.namespace )

	def on_select_camera_float_fcurve( self ):
		if not self.character_camera or vmobu.core.is_obj_unbound( self.character_camera ):
			self.setup_camera_anim_ramp( self.namespace )
			return False

		vmobu.core.unselect_all_components( )
		self.character_camera.Selected = True

		prop = self.character_camera.PropertyList.Find( CAMERA_WEIGHT_PROPERTY )
		if not prop:
			vmobu.core.logger.warning( '{0} does not have the {1} property'.format( self.character_camera.LongName, CAMERA_WEIGHT_PROPERTY ) )
			return False

		prop.SetFocus( True )
		return True

	def on_key_camera_animation( self ):
		if not self.character_camera:
			return False

		# Get the property
		prop = self.character_camera.PropertyList.Find( CAMERA_WEIGHT_PROPERTY )
		if not prop:
			vmobu.core.logger.warning( '{0} not set up properly for camera weighted animation'.format( self.character_camera.LongName ) )
			return False

		prop.Key( )

	def on_camera_line_edit_updated( self ):
		if not self.character_camera:
			return False

		raw_value = self.camera_animation_slider_edit.text( )
		try:
			float_value = float( raw_value )

		except ValueError:
			print 'Invalid value passed in to camera animation slider line edit'

		except:
			raise

		slider_value = self.camera_animation_slider.setValue( float_value * 100.0 )
		return True

	def on_camera_slider_updated( self ):
		# If the character has no camera, we don't bother.
		if not self.character_camera:
			return False

		# The camera_animation_slider has updated.
		raw_slider_value = self.camera_animation_slider.value( )
		normal_slider_value = raw_slider_value / 100.0

		# Update the line edit
		self.camera_animation_slider_edit.setText( str( '{0:.2f}'.format( normal_slider_value ) ) )

		# Update the property on the camera
		weight_prop = self.character_camera.PropertyList.Find( CAMERA_WEIGHT_PROPERTY )
		if not weight_prop:
			vmobu.core.logger.warning( 'There is no {1} property on {0}'.format( self.character_camera.LongName, CAMERA_WEIGHT_PROPERTY ) )
			return False

		weight_prop.Data = normal_slider_value
		vmobu.core.evaluate( )

	def add_bone_group_list( self ):
		"""
		Adds the bone groups list within the UI.

		*Arguments:*
		  * ``Argument`` Enter a description for the argument here.

		*Keyword Arguments:*
		  * ``Argument`` Enter a description for the keyword argument here.

		*Returns:*
		  * ``Value`` If any, enter a description for the return value here.
		"""

		self.add_bone_group_list_row( )

	def add_bone_group_list_row( self ):
		"""
		Adds a row for the each bone group within the UI.

		*Arguments:*
		  * ``Argument`` Enter a description for the argument here.

		*Keyword Arguments:*
		  * ``Argument`` Enter a description for the keyword argument here.

		*Returns:*
		  * ``Value`` If any, enter a description for the return value here.
		"""

		#Adds cell widgets for bone groups
		self.bone_group_table_ui.insertRow( 0 )
		self.bone_group_name_item = PySide.QtGui.QTableWidgetItem( )
		self.bone_group_value_item = PySide.QtGui.QTableWidgetItem( )
		self.bone_group_table_ui.setItem( 0, 0, self.bone_group_name_item )
		self.bone_group_table_ui.setItem( 0, 1, self.bone_group_value_item )


	def add_bone_weight_collection( self ):
		"""
		Adds a new weight group collection.

		*Arguments:*
		  * ``None``

		*Keyword Arguments:*
		  * ``None``

		*Returns:*
		  * ``None``
		"""

		self.collection_combo_ui.addItem( 'New Collection' )


	def collection_name_edit( self ):
		"""
		Edits the name of the current collection.

		*Arguments:*
		  * ``None``

		*Keyword Arguments:*
		  * ``None``

		*Returns:*
		  * ``None``
		"""

		self.collection_name_ui.setText( str( self.collection_combo_ui.currentText( ) ) )


	def get_collection_index( self ):
		self.bone_group_table_ui.currentIndex( )

	@vmobu.decorators.toggle_auto_key
	@PySide.QtCore.Slot( str )
	def weight_changed( self, rowCol ):
		"""
		Sets the values of the anim properties if the values have changed in the bone groups tab.

		*Arguments:*
		  * ``rowCol`` The row and column of the bone group list of the ui.

		*Keyword Arguments:*
		  * ``None``

		*Returns:*
		  * ``None``
		"""

		row = int( rowCol.split( '-' )[ 0 ] )
		col = int( rowCol.split( '-' )[ 1 ] )

		val = self.bone_group_table_ui.cellWidget( row, col ).value( )
		group = self.bone_group_table_ui.item( row, 0 ).text( )

		if not self.anim_node:
			self.logger.error_dialog( 'Could not get the anim node to update weights for!' )
			return False

		# update the anim node property
		for prop in self.anim_node.PropertyList:
			if prop.Name.startswith( "wg" ):
				if prop.Name.endswith( ':' + group ):
					prop.Data = val

		# update the actual scene objects with the associated weightgroup name and character namespace
		for comp in pyfbsdk.FBSystem( ).Scene.Components:
			#if comp.ClassName( ) == 'FBModelSkeleton':
			p_bone_name = comp.PropertyList.Find('p_bone_name')
			if p_bone_name:
				if comp.LongName.startswith( self.namespace + ':' ):
					wg_prop = vmobu.core.get_property( comp, 'p_bone_weightgroup', return_value = False )
					if wg_prop:
						if wg_prop.Data == group:
							bone_weight_prop = vmobu.core.get_property( comp, 'p_bone_weight', return_value = False )
							if bone_weight_prop:
								bone_weight_prop.Data = val

		self.bone_group_table_ui.setCurrentCell( row, col )

	@vmobu.decorators.toggle_auto_key
	def update_weight_groups(self):
		"""
		Updates the components' p_bone_weight to match that of the anim node.

		*Arguments:*
		  * ``None``

		*Keyword Arguments:*
		  * ``None``

		*Returns:*
		  * ``None``
		"""

		self.check_anim_node()

		if not self.anim_node:
			self.logger.error_dialog('Could not get the anim node to update weights for!')
			return False

		for prop in self.anim_node.PropertyList:
			if prop.Name.startswith("wg"):
				wg_name = prop.Name.split(":")[2]
				if wg_name:
					for comp in pyfbsdk.FBSystem().Scene.Components:
						p_bone_weightgroup = comp.PropertyList.Find('p_bone_weightgroup')
						if p_bone_weightgroup:
							if p_bone_weightgroup.Data == wg_name:
								p_bone_weight = comp.PropertyList.Find('p_bone_weight')
								p_bone_weight.Data = prop.Data

		return True


	def set_bone_weight_spinbox_to_red( self, row ):
		"""
		Sets spin box of weight group to a red border if weight group is keyed.

		*Arguments:*
		* ``None``

		*Keyword Arguments:*
		* ``None``

		*Returns:*
		* ``None``
		"""

		item = self.bone_group_table_ui.item( row, 1 )
		item.setBackground( PySide.QtGui.QColor( 'red' ) )


	def get_weight_groups( self ):
		"""
		Grabs the weight groups from current character.

		*Arguments:*
		  * ``Argument`` Enter a description for the argument here.

		*Keyword Arguments:*
		  * ``Argument`` Enter a description for the keyword argument here.

		*Returns:*
		  * ``Value`` If any, enter a description for the return value here.
		"""

		#Get current anim node and parent (master node)
		if not self.anim_node:
			self.anim_node = vmobu.core.get_object_by_name( str( self.character_combo_ui.currentText( ) ), use_namespace=True, models_only=False )

		if range( self.bone_group_table_ui.rowCount( ) ) > 0:
			for row in range( self.bone_group_table_ui.rowCount( ) ):
				self.bone_group_table_ui.removeRow( row )

				vmobu.core.evaluate()

				if range(self.bone_group_table_ui.rowCount()) > 0:
					self.bone_group_table_ui.removeRow(row)

		if not range( self.bone_group_table_ui.rowCount( ) ) == 0:
			for row in range( self.bone_group_table_ui.rowCount( ) ):
				self.bone_group_table_ui.removeRow( row )

		if self.anim_node:
			for anim_node_prop in self.anim_node.PropertyList:
				if anim_node_prop.Name.startswith( "wg:" ):
					weight_group_property = anim_node_prop.Name.split( ":" )[ 2 ]
					if not weight_group_property == "":
						vmobu.core.evaluate()
						self.add_bone_group_list( )
						self.bone_group_name_item.setText( str( weight_group_property ) )

			#For each row in the bone weight group list
			for row in range( self.bone_group_table_ui.rowCount( ) ):
				#Runs through all properties that aren't from asset addition
				for anim_node_prop in self.anim_node.PropertyList:
					if anim_node_prop.Name.startswith( "wg" ):
						wg_name = anim_node_prop.Name.split( ":" )[ 2 ]
						current_item = self.bone_group_table_ui.item( row, 0 )

						if wg_name == str( current_item.text( ) ):
							self.setup_spin_boxes(row, anim_node_prop)

							if anim_node_prop.IsAnimatable( ) and anim_node_prop.IsAnimated( ):
								anim_node_prop_anim = anim_node_prop.GetAnimationNode( )
								if anim_node_prop_anim:
									if len(anim_node_prop_anim.FCurve.Keys) > 0:
										self.set_bone_weight_spinbox_to_red( row )
										vmobu.core.evaluate()
							else:
								pass

			vmobu.core.evaluate()

			self.set_existing_collections( )

			return True

		return False


	def setup_spin_boxes(self, row, property):
		#Create a signal and a spin box for the values of the weight groups
		signal_mapper = PySide.QtCore.QSignalMapper(self)
		spin_box = PySide.QtGui.QSpinBox()
		spin_box.setParent(self.bone_group_table_ui)
		signal_mapper.setMapping(spin_box, str(row) + '-' + str(1))

		#self.connect( spin_box, PySide.QtCore.SIGNAL( "valueChanged( int )" ), self.update_wg_properties )
		self.connect(spin_box, PySide.QtCore.SIGNAL("valueChanged( int )"), signal_mapper,
		             PySide.QtCore.SLOT("map()"))

		spin_box.setRange(0, 100)
		spin_box.setValue(property.Data)

		self.bone_group_table_ui.setCellWidget(row, 1, spin_box)
		signal_mapper.connect(PySide.QtCore.SIGNAL("mapped(const QString &)"), self,
		                      PySide.QtCore.SLOT("weight_changed(const QString &)"))


	def get_anim_properties(self):
		"""
		Gets the animation properties and stores them in a list.

		*Arguments:*
		  * ``None``

		*Keyword Arguments:*
		  * ``None``

		*Returns:*
		  * ``self.anim_properties`` The list of the animation properties
		"""

		self.anim_properties = []
		anim_nodes = []

		for note in pyfbsdk.FBSystem().Scene.Notes:
			if note.LongName.endswith("anim_node"):
				anim_nodes.append(note)

		for anim_node in anim_nodes:
			for prop in anim_node.PropertyList:
				if prop.IsUserProperty():
					if not prop.Name.startswith("wg"):
						if not prop.Name == "Bones":
							if not prop.Name.startswith("uid") or not prop.Name == "uid":
								if not prop.Name.startswith("p_"):
									self.anim_properties.append(prop)

		return self.anim_properties


	def set_existing_collections( self ):
		"""
		Sets the collections in the drop-down of the "Animated Weights" tab.

		*Arguments:*
		  * ``None``

		*Keyword Arguments:*
		  * ``None``

		*Returns:*
		  * ``None``
		"""

		self.collection_combo_ui.clear()

		collections_array = [ ]

		for prop in self.anim_node.PropertyList:
			if prop.IsUserProperty( ):
				if prop.Name.startswith( "wg" ):
					collection_namespace = prop.Name.split( ":" )
					if collection_namespace[1] not in collections_array:
						collections_array.append( collection_namespace[1] )

		for collection in collections_array:
			self.collection_combo_ui.addItem( collection_namespace[ 1 ] )

		return True


	def set_key_to_weight_groups( self ):
		"""
		Sets key of the current weight group on the current time.

		*Arguments:*
		  * ``Argument`` Enter a description for the argument here.

		*Keyword Arguments:*
		  * ``Argument`` Enter a description for the keyword argument here.

		*Returns:*
		  * ``Value`` If any, enter a description for the return value here.
		"""

		#Get current anim node
		self.check_anim_node( )

		#Get current row and column in the ui
		row = self.bone_group_table_ui.currentRow( )

		curr_frame = pyfbsdk.FBSystem( ).LocalTime.GetFrame( )

		#All nodes components
		all_nodes_components = pyfbsdk.FBSystem( ).Scene.Components
		bones_array = [ ]

		#Check components that are skeleton nodes and set key based on matching selection in ui
		for curr_component in all_nodes_components:
			#if curr_component and curr_component.ClassName( ) == "FBModelSkeleton":
			p_bone_name = curr_component.PropertyList.Find('p_bone_name')
			if p_bone_name:
				bones_array.append( curr_component )
				for curr_comp_prop in curr_component.PropertyList:
					curr_bone_group = curr_component.PropertyList.Find( "p_bone_weightgroup" )
					if curr_bone_group.Data == str(self.bone_group_table_ui.item( row, 0 ).text( )):
						if curr_comp_prop.Name.endswith( "bone_weight" ):
							curr_comp_prop.SetAnimated( True )
							curr_comp_animation = curr_comp_prop.GetAnimationNode( )
							fcurve = curr_comp_animation.FCurve
							curr_data = self.bone_group_table_ui.item( row, 1 ).text( )
							fcurve.KeyAdd( pyfbsdk.FBTime( 0, 0, 0, curr_frame ), curr_comp_prop.Data )

		for an_prop in self.anim_node.PropertyList:
			if an_prop.Name.startswith( "wg" ):
				weight_group = an_prop.Name.split( ":" )[ 2 ]
				if weight_group == self.bone_group_table_ui.item( row, 0 ).text( ):
					an_prop.SetAnimated( True )
					an_prop_animation = an_prop.GetAnimationNode( )
					fcurve = an_prop_animation.FCurve
					fcurve.KeyAdd( pyfbsdk.FBTime( 0, 0, 0, curr_frame ), an_prop.Data )

		self.set_bone_weight_spinbox_to_red( row )


	def delete_key_to_weight_groups( self ):
		"""
		Deletes key of the currently selected weight group on the current time.

		*Arguments:*
		  * ``Argument`` Enter a description for the argument here.

		*Keyword Arguments:*
		  * ``Argument`` Enter a description for the keyword argument here.

		*Returns:*
		  * ``Value`` If any, enter a description for the return value here.
		"""

		#Get current anim node
		self.check_anim_node( )

		#Get current row and column in the ui
		row = self.bone_group_table_ui.currentRow( )

		#All nodes components
		all_nodes_components = pyfbsdk.FBSystem( ).Scene.Components
		bones_array = [ ]

		#Check components that are skeleton nodes and delete key based on matching selection in ui
		for curr_component in all_nodes_components:
			#if curr_component and curr_component.ClassName( ) == "FBModelSkeleton":
			p_bone_name = curr_component.PropertyList.Find('p_bone_name')
			if p_bone_name:
				bones_array.append( curr_component )
				for curr_comp_prop in curr_component.PropertyList:
					curr_bone_group = curr_component.PropertyList.Find( "p_bone_weightgroup" )
					if curr_bone_group.Data == self.bone_group_table_ui.item( row, 0 ).text( ):
						if curr_comp_prop.Name.endswith( "bone_weight" ):
							curr_comp_prop.SetAnimated( True )
							curr_comp_animation = curr_comp_prop.GetAnimationNode( )
							fcurve = curr_comp_animation.FCurve
							self.remove_key_at_current( curr_comp_animation )

		for an_prop in self.anim_node.PropertyList:
			if an_prop.Name.startswith( "wg" ):
				weight_group = an_prop.Name.split( ":" )[ 2 ]
				if weight_group == self.bone_group_table_ui.item( row, 0 ).text( ):
					an_prop_animation = an_prop.GetAnimationNode( )
					fcurve = an_prop_animation.FCurve
					self.remove_key_at_current( an_prop_animation )
					an_prop.SetAnimated( False )

		vmobu.core.evaluate()


	def remove_key_at_current( self, pAnimationNode ):
		"""
		Removes key at the current frame.

		*Arguments:*
		  * ``Argument`` Enter a description for the argument here.

		*Keyword Arguments:*
		  * ``Argument`` Enter a description for the keyword argument here.

		*Returns:*
		  * ``Value`` If any, enter a description for the return value here.
		"""

		#All nodes components
		all_nodes_components = pyfbsdk.FBSystem( ).Scene.Components
		bones_array = [ ]

		if len( pAnimationNode.Nodes ) == 0:
			pAnimationNode.KeyRemove( )
		else:
			for node in pAnimationNode.Nodes:
				self.remove_key_at_current( node )
				del( node )

		for curr_component in all_nodes_components:
			#if curr_component and curr_component.ClassName( ) == "FBModelSkeleton":
			p_bone_name = node.PropertyList.Find('p_bone_name')
			if p_bone_name:
				bones_array.append( curr_component )

	def select_bone_weight_curve( self ):
		"""
		Selects all FCurves relating to currently selected bone weight group in the ui.

		*Arguments:*
		  * ``Argument`` Enter a description for the argument here.

		*Keyword Arguments:*
		  * ``Argument`` Enter a description for the keyword argument here.

		*Returns:*
		  * ``Value`` If any, enter a description for the return value here.
		"""

		#Get current anim node
		self.check_anim_node( )

		#Get current row and column in the ui
		row = self.bone_group_table_ui.currentRow( )

		#All nodes components
		all_nodes_components = pyfbsdk.FBSystem( ).Scene.Components
		bones_array = [ ]

		#Check components that are skeleton nodes and delete key based on matching selection in ui
		for curr_component in all_nodes_components:
			#if curr_component and curr_component.ClassName( ) == "FBModelSkeleton":
			p_bone_name = curr_component.PropertyList.Find('p_bone_name')
			if p_bone_name:
				bones_array.append( curr_component )
				for curr_comp_prop in curr_component.PropertyList:
					curr_bone_group = curr_component.PropertyList.Find( "p_bone_weightgroup" )
					if curr_bone_group.Data == self.bone_group_table_ui.item( row, 0 ).text( ):
						if curr_comp_prop.Name.endswith( "bone_weight" ):
							curr_comp_animation = curr_comp_prop.GetAnimationNode( )
							fcurve = curr_comp_animation.FCurve
							fcurve.Selected = True
							print "Curves selected"


	def pick_anim_controller( self ):
		"""
		Picks the current character's anim controller.

		*Arguments:*
		  * ``Argument`` Enter a description for the argument here.

		*Keyword Arguments:*
		  * ``Argument`` Enter a description for the keyword argument here.

		*Returns:*
		  * ``Value`` If any, enter a description for the return value here.
		"""

		anim_controller = self.get_anim_controller( )
		if anim_controller:
			anim_controller.Selected = True
			self.anim_controller_edit_ui.setText( anim_controller.LongName )


	def update_ui( self ):
		"""
		Update ui when timer runs out.

		*Arguments:*
		  * ``Argument`` Enter a description for the argument here.

		*Keyword Arguments:*
		  * ``Argument`` Enter a description for the keyword argument here.

		*Returns:*
		  * ``Value`` If any, enter a description for the return value here.
		"""

		self.anim_exporter_widget.update( )

	def repopulate_cells( self ):
		"""
		Re-populates the UI with animation cells, sourcing from the anim node, based off past animations added.

		*Arguments:*
		  * ``Argument`` Enter a description for the argument here.

		*Keyword Arguments:*
		  * ``Argument`` Enter a description for the keyword argument here.

		*Returns:*
		  * ``Value`` If any, enter a description for the return value here.
		"""

		#Get current anim node
		self.check_anim_node( )

		#Refresh scene
		vmobu.core.evaluate( )

		# Delete all rows
		while self.anim_list_ui.rowCount( ) > 0:
			self.anim_list_ui.removeRow( 0 )

		#for row in range( self.anim_list_ui.rowCount( ) ):
			#self.anim_list_ui.removeRow( row )

		#load_widget through all properties of the current anim node to read the animation enum properties for repopulating re-opened ui
		try:
			animations = []
			for anim_node_prop in reversed( self.anim_node.PropertyList ):
				if anim_node_prop.IsUserProperty( ):
					if anim_node_prop.Name == "p_anim_file":
						if anim_node_prop.Data == "None" or anim_node_prop.Data == "none":
							self.export_dir_ui.setText( "" )
						else:
							self.export_dir_ui.setText( str( anim_node_prop.Data ) )

					# If the property is a volition custom property, we skip it
					if anim_node_prop.Name.startswith( "p_" ):
						continue

					# If the property is the bone prop, we skip
					if anim_node_prop.Name == "Bones":
						continue

					# We don't care about weight groups properties right now, so we skip
					if anim_node_prop.Name.startswith( "wg" ):
						continue

					# We don't want to ever edit the uid's
					if anim_node_prop.Name.startswith("uid") or anim_node_prop.Name == "uid":
						continue

					# If the property hasn't already been stored/updated. Lets do it.
					if anim_node_prop not in animations:
						animations.append(anim_node_prop)
						anim_node_take = anim_node_prop.Name

						anim_node_take_name_prop_enum_list = anim_node_prop.EnumList(0)
						anim_node_take_name_split = anim_node_take_name_prop_enum_list.split(":")
						anim_node_take_name = anim_node_take_name_split[1]

						anim_node_start_frame_prop_enum_list = anim_node_prop.EnumList( 1 )
						anim_node_start_frame_split = anim_node_start_frame_prop_enum_list.split( ":" )
						anim_node_start_frame = anim_node_start_frame_split[ 1 ]

						anim_node_end_frame_prop_enum_list = anim_node_prop.EnumList( 2 )
						anim_node_end_frame_split = anim_node_end_frame_prop_enum_list.split( ":" )
						anim_node_end_frame = anim_node_end_frame_split[ 1 ]

						anim_node_ramp_in_prop_enum_list = anim_node_prop.EnumList( 3 )
						anim_node_ramp_in_split = anim_node_ramp_in_prop_enum_list.split( ":" )
						anim_node_ramp_in = anim_node_ramp_in_split[ 1 ]

						anim_node_ramp_out_prop_enum_list = anim_node_prop.EnumList( 4 )
						anim_node_ramp_out_split = anim_node_ramp_out_prop_enum_list.split( ":" )
						anim_node_ramp_out = anim_node_ramp_out_split[ 1 ]

						anim_node_framerate_prop_enum_list = anim_node_prop.EnumList( 5 )
						anim_node_framerate_split = anim_node_framerate_prop_enum_list.split( ":" )
						anim_node_framerate = anim_node_framerate_split[ 1 ]

						if self.anim_node.LongName == str( self.character_combo_ui.currentText( ) ):
							self.anim_list_ui.insertRow( 0 )
							anim_name_item = PySide.QtGui.QTableWidgetItem( )
							start_frame_item = PySide.QtGui.QTableWidgetItem( )
							end_frame_item = PySide.QtGui.QTableWidgetItem( )
							ramp_in_item = PySide.QtGui.QTableWidgetItem( )
							ramp_out_item = PySide.QtGui.QTableWidgetItem( )
							framerate_item = PySide.QtGui.QTableWidgetItem( )
							take_name_item = PySide.QtGui.QTableWidgetItem()

							self.anim_list_ui.setItem( 0, 0, anim_name_item )
							self.anim_list_ui.setItem( 0, 1, start_frame_item )
							self.anim_list_ui.setItem( 0, 2, end_frame_item )
							self.anim_list_ui.setItem( 0, 3, ramp_in_item )
							self.anim_list_ui.setItem( 0, 4, ramp_out_item )
							self.anim_list_ui.setItem( 0, 5, framerate_item )
							self.anim_list_ui.setItem( 0, 6, take_name_item )

							#Repopulate ui with anim node properties
							anim_name_item.setText( anim_node_take )
							start_frame_item.setText( anim_node_start_frame )
							end_frame_item.setText( anim_node_end_frame )
							ramp_in_item.setText( anim_node_ramp_in )
							ramp_out_item.setText( anim_node_ramp_out )
							framerate_item.setText( anim_node_framerate )
							take_name_item.setText( anim_node_take_name )

							for row in range(self.anim_list_ui.rowCount()):
								self.add_take_widget_dropdown()
				else:
					pass
		except AttributeError:
			if self.anim_node:
				pass
			#else:
			#  pyfbsdk.FBMessageBox( "Anim Node Error", "No anim node found.", "OK" )

		return True


	def delete_animation_cell( self ):
		"""
		Deletes animation cells within the UI.

		*Arguments:*
		  * ``Argument`` Enter a description for the argument here.

		*Keyword Arguments:*
		  * ``Argument`` Enter a description for the keyword argument here.

		*Returns:*
		  * ``Value`` If any, enter a description for the return value here.
		"""

		#Get current row and column from ui, as well as current selected animation cell widget
		row_list = self.anim_list_ui.selectionModel().selectedRows()
		final_count = self.anim_list_ui.rowCount() - len( row_list )
		anim_cell_clicked = self.anim_list_ui.cellClicked.connect( self.cell_was_clicked )

		#curr_anim_name_item_ui = self.anim_list_ui.item( row, 0 )
		self.check_anim_node( )

		#Delete animation cell widget and refresh ui
		if self.anim_node:
			#for prop in self.anim_node.PropertyList:
			if row_list:
				try:
					#if prop.Name == str( curr_anim_name_item_ui.text( ) ):
					#	self.anim_node.PropertyRemove( prop )
					for item in reversed( row_list ):
						self.anim_list_ui.removeRow( item.row() )
					if self.anim_list_ui.rowCount() != final_count:
						pyfbsdk.FBMessageBox('Error Deleting', 'Error Deleting', 'OK')
				except RuntimeError:
					self.logger.warning('Had trouble deleting an animation cell within delete_animation_cell method.')

		vmobu.core.evaluate()

		self.remove_anim_node_properties()
		self.refresh_anim_node()


	def copy_anim_list( self ):
		"""
		Copies animation list in the ui.

		*Arguments:*
		  * ``Argument`` Enter a description for the argument here.

		*Keyword Arguments:*
		  * ``Argument`` Enter a description for the keyword argument here.

		*Returns:*
		  * ``Value`` If any, enter a description for the return value here.
		"""

		#Get current anim node
		self.check_anim_node( )

		self.stored_anim_data = [ ]


	def delete_bone_from_list( self ):
		"""
		Deletes currently selected bone in the bone list in the ui from only the ui.

		*Arguments:*
		  * ``Argument`` Enter a description for the argument here.

		*Keyword Arguments:*
		  * ``Argument`` Enter a description for the keyword argument here.

		*Returns:*
		  * ``Value`` If any, enter a description for the return value here.
		"""

		curr_sel = self.bone_list_ui.selectedItems( )

		for sel in curr_sel:
			row = self.bone_list_ui.row( sel )
			self.bone_list_ui.takeItem( row )


	def delete_tag_from_list( self ):
		"""
		Deletes currently selected tag in the tag list in the ui from only the ui.

		*Arguments:*
		  * ``Argument`` Enter a description for the argument here.

		*Keyword Arguments:*
		  * ``Argument`` Enter a description for the keyword argument here.

		*Returns:*
		  * ``Value`` If any, enter a description for the return value here.
		"""

		curr_sel = self.prop_list_ui.selectedItems( )

		for sel in curr_sel:
			row = self.prop_list_ui.row( sel )
			self.prop_list_ui.takeItem( row )


	def eventFilter( self, obj, event ):
		"""
		Binds the keyboard to the ui and Motionbuilder.

		*Arguments:*
		  * ``event`

		*Keyword Arguments:*
		  * ``obj, event``

		*Returns:*
		  * ``event``
		"""

		curr_tab_index = self.anim_exporter_widget.tabWidget.currentIndex()

		try:
			#Key keyboard binding for the key release
			if event.type( ) == PySide.QtCore.QEvent.KeyRelease and obj is self.anim_exporter_widget:
				key = event.key( )
				#Check that the key release is 'Enter' or 'Return'
				if key == PySide.QtCore.Qt.Key_Return or key == PySide.QtCore.Qt.Key_Enter:
					if not curr_tab_index == 0:
						self.update_widget_for_curr_node()
						return True
					else:
						self.refresh_anim_node( )
						return True
			#return PySide.QtGui.QMainWindow.eventFilter( self, obj, event )

		except AttributeError:
			vmobu.core.evaluate()

		return PySide.QtGui.QMainWindow.eventFilter(self, obj, event)


	def select_anim_node( self ):
		"""
		Deselects everything in the scene, then selects the anim node.

		*Arguments:*
		  * ``Argument`` Enter a description for the argument here.

		*Keyword Arguments:*
		  * ``Argument`` Enter a description for the keyword argument here.
		"""

		self.check_anim_node( )

		for comp in pyfbsdk.FBSystem( ).Scene.Components:
			comp.Selected = False

		self.anim_node.Selected = True


	def documentation( self ):
		"""
		Opens documentation for the Anim Exporter.

		*Arguments:*
		  * ``Argument`` Enter a description for the argument here.

		*Keyword Arguments:*
		  * ``Argument`` Enter a description for the keyword argument here.

		*Returns:*
		  * ``Value`` If any, enter a description for the return value here.
		"""

		print "Help menu selected"
		try:
			file_handle = urllib.urlopen( "http://vsp/projects/ctg/CTG%20OneNote/CTG/Tech%20Art%20Team/Tech%20Animation/Maya.one#Animation%20Exporter&section-id={2BD251CA-1B07-4F92-827B-9F09B7409ED8}&page-id={00D754BE-E1CB-4E37-825E-714B8E1B9E0F}&end", proxies=None )
		except RuntimeError:
			print "Could not find MS OneNote"


	def close_event( self ):
		"""
		Closes the UI.

		*Arguments:*
		  * ``Argument`` Enter a description for the argument here.

		*Keyword Arguments:*
		  * ``Argument`` Enter a description for the keyword argument here.

		*Returns:*
		  * ``Value`` If any, enter a description for the return value here.
		"""

		self.anim_exporter_widget.close( )


	def add_application_callbacks( self ):
		"""
		Adds callbacks for the pyfbsdk.FBApplication( ) based off the same structure the xDCC uses.

		*Arguments:*
		  * ``None``

		*Keyword Arguments:*
		  * ``None``

		*Returns:*
		  * ``Mobu callbacks``
		"""

		app_cb_dict = self.cb_mgr._scene_callbacks_ids

		vmobu.core.evaluate()

		#On file new
		self.cb_mgr.add_callback( 'App', pyfbsdk.FBApplication( ).OnFileNew, self.on_new_before, cb_dict = app_cb_dict )

		#On file new completed
		self.cb_mgr.add_callback( 'App', pyfbsdk.FBApplication( ).OnFileNewCompleted, self.on_new_after, cb_dict = app_cb_dict )

		#On file open
		self.cb_mgr.add_callback( 'App', pyfbsdk.FBApplication( ).OnFileOpen, self.on_new_before, cb_dict=app_cb_dict )

		#On file open completed
		self.cb_mgr.add_callback( 'App', pyfbsdk.FBApplication( ).OnFileOpenCompleted, self.on_new_after, cb_dict = app_cb_dict )

		#On file merge
		self.cb_mgr.add_callback( 'App', pyfbsdk.FBApplication( ).OnFileMerge, self.on_new_after, cb_dict = app_cb_dict )

		#When scene is changed
		if not pyfbsdk.FBApplication( ).OnFileExit:
			self.cb_mgr.add_callback( 'Nodes', pyfbsdk.FBSystem( ).Scene.OnChange, self.on_node_merged, cb_dict = app_cb_dict )

		#On file exit
		self.cb_mgr.add_callback( 'App', pyfbsdk.FBApplication( ).OnFileExit, self.on_dcc_exit, cb_dict = app_cb_dict )

		# On UiIdle
		self.cb_mgr.add_callback( 'App', self.system.OnUIIdle, self.onUiIdle, cb_dict = app_cb_dict )

	def onUiIdle( self, control, event ):
		"""
		Main refresh callback. Updates UI as time changes for property slider updates.

		*Arguments:*
		  * ``none``

		*Keyword Arguments:*
		  * ``none``

		*Returns:*
		  * ``None``
		"""
		# Called whenever the ui has become idle. Specifically useful for updating after time changes.
		current_time = self.system.LocalTime
		if current_time != self.end_eval_time:
			self.update_sliders( )
			self.end_eval_time = self.system.LocalTime
		return True

	def on_new_before( self, *args ):
		"""
		Removes callbacks for before creating a new file.

		*Arguments:*
		  * ``*args``

		*Keyword Arguments:*
		  * ``*args``

		*Returns:*
		  * ``None``
		"""

		self.cb_mgr.remove_all_callbacks( )
		self.v_cb_mgr.call( self.on_new_before )


	def on_new_after( self, *args ):
		"""
		Calls callbacks for after a new file is created.

		*Arguments:*
		  * ``*args``

		*Keyword Arguments:*
		  * ``*args``

		*Returns:*
		  * ``None``
		"""

		self.v_cb_mgr.call( self.on_new_after )
		if self.anim_exporter_widget:
			if self.anim_exporter_widget.tabWidget:
				try:
					self.anim_exporter_widget.tabWidget.setEnabled( True )
				except RuntimeError:
					pass
		try:
			self.update_ui_data( )
			self.repopulate_cells( )
			self.update_properties ( self.anim_node )
			self.update_properties( self.master_node )
			self.update_anim_properties()
		except RuntimeError:
			pass


	def on_merge_before( self, *args ):
		"""
		Runs callbacks for before a merge is completed.

		*Arguments:*
		  * ``*args``

		*Keyword Arguments:*
		  * ``*args``

		*Returns:*
		  * ``None``
		"""

		self._on_merge = True
		self.on_new_before( )


	def on_merge_after( self, *args ):
		"""
		Calls callbacks after a merge is completed.

		*Arguments:*
		  * ``*args``

		*Keyword Arguments:*
		  * ``*args``

		*Returns:*
		  * ``None``
		"""

		self._on_merge = False
		self.v_cb_mgr.call( self.on_merge_after )
		try:
			self.refresh_anim_node( )
			self.update_ui_data( )

		except RuntimeError:
			pass


	def on_dcc_exit( self, *args ):
		"""
		Removes all callbacks when exiting the file is attempted.

		*Arguments:*
		  * ``*args``

		*Keyword Arguments:*
		  * ``*args``

		*Returns:*
		  * ``None``
		"""

		self.cb_mgr.remove_all_callbacks( )
		vmobu.core.evaluate()

	def on_node_merged( self, control, event ):
		"""
		Runs callbacks on the instant a merge happens.

		*Arguments:*
		  * ``control, event``

		*Keyword Arguments:*
		  * ``None``

		*Returns:*
		  * ``None``
		"""

		if event.Type == pyfbsdk.FBSceneChangeType.kFBSceneChangeMergeTransactionBegin:
			self.cb_mgr.remove_all_callbacks( )
			self.v_cb_mgr.call( self.on_new_before )

		if event.Type == pyfbsdk.FBSceneChangeType.kFBSceneChangeMergeTransactionEnd:
			self.v_cb_mgr.call( self.on_new_after )
			self.refresh_anim_node( )


	def set_character_source( self ):
		"""
		Sets the character's source back to the corresponding HIK rig.

		*Arguments:*
		  * ``None``

		*Keyword Arguments:*
		  * ``None``

		*Returns:*
		  * ``None``
		"""

		curr_char = pyfbsdk.FBApplication( ).CurrentCharacter
		if curr_char:
			curr_char.ActiveInput = pyfbsdk.FBCharacterInputType.kFBCharacterInputCharacter


	def update_anim_nodes_list(self):
		"""
		Updates the anim nodes list inside the Exporter, and uses the weapon's anim node displayed

		*Arguments:*
		  * ``None``

		*Keyword Arguments:*
		  * ``None``

		*Returns:*
		  * ``None``
		"""
		self.character_combo_ui.clear( )

		curr_state = self.weapon_enabled_cb.isChecked( )

		#vmobu.core.evaluate()

		if self.character_combo_ui:
			for note in vmobu.core.scene.Notes:
				if note.LongName.endswith( 'anim_node' ):
					p_asset_type = note.PropertyList.Find( 'p_asset_type' )
					#self.weapon_enabled_cb.setChecked(False)
					if p_asset_type:

						# IF the note isn't a valid anim node, we skip out
						if not self.is_anim_node_valid( note ):
							continue

						if p_asset_type.Data == 'Actors\Characters' or p_asset_type.Data == 'Characters':
							self.character_combo_ui.addItem( note.LongName )

						if curr_state:
							if p_asset_type.Data == 'Actors\Vehicles' or p_asset_type.Data == 'Vehicles':
								self.character_combo_ui.addItem( note.LongName )

							if p_asset_type.Data == 'Actors\Weapons' or p_asset_type.Data == 'Weapons':
								self.character_combo_ui.addItem( note.LongName )

							if p_asset_type.Data == 'Actors\Items' or p_asset_type.Data == 'Items':
								self.character_combo_ui.addItem( note.LongName )

		# Reset current index
		#self.character_combo_ui.setCurrentIndex( current_anim_node_index )
		return True


	def debug_on( self ):
		# Turn on debug mode from within editor
		if self.debug:
			pass

		else:
			result, email = pyfbsdk.FBMessageBoxGetUserValue('Animation Exporter DEBUG MODE', 'You are entering debug mode. What email should your debug logs go to? ( Who are you working with to debug your error? )', 'evan.cox@dsvolition.com', pyfbsdk.FBPopupInputType.kFBPopupString,
			                                                 'Cool',
			                                                 'Cancel')
			if not result:
				return False

			self.debug_email = email

			pyfbsdk.FBMessageBox('Animation Exporter', 'Debug is now ON!', 'OK')
			self.debug = True

		return True


	def debug_off( self ):
		if not self.debug:
			pass

		else:
			pyfbsdk.FBMessageBox('Animation Exporter', 'Debug is now OFF!', 'OK')
			self.debug = False

		return True

	def is_anim_node_valid( self, anim_node ):
		# Go through all the standard anim node properties and make sure they're there. If not, we should add them.
		for prop_name in ANIM_NODE_PROPERTIES.keys( ):
			prop = anim_node.PropertyList.Find( prop_name )

			# If it's not found we will try to add it, if we can't we return false
			if not prop:
				prop_default_value = ANIM_NODE_PROPERTIES[ prop_name ]
				prop = vmobu.core.add_property_obj( anim_node, prop_name, prop_default_value )

				if not prop:
					return False

		return True

	def update_ui_data( self ):
		"""
		Update the UI fields from the anim node

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``
		"""

		#Set project directory
		self.project_dir = file_io.v_path.Path( core.const.workspace_dir.replace( '\\', '/' )[  :-1  ] ).splitdrive( )[
		   1  ].replace( '/projects/', '' )
		self.anim_exporter_widget.projectLineEdit.setText( str( self.project_dir ) )
		starting_anim_node = self.anim_node

		#Check for "Notes" in self.scene and apply to characterCombo field
		if len( pyfbsdk.FBSystem( ).Scene.Notes ) < 1:

			if not self.anim_node:
				self.anim_node = None
				self.character_combo_ui.clear( )
				try:
					self.character_combo_ui.currentText( self.anim_node )
				except TypeError:
					#FBMessageBox( "Anim Node Error", "No anim node present to populate.\n Killing process.", "OK" )
					print "No anim node present to populate."
		else:
			#Search through all notes in the scene for anim node notes and add them in the ui
			for n in pyfbsdk.FBSystem( ).Scene.Notes:
				anim_nodes = [ ]
				if n.Name.endswith( "anim_node" ):
					if n not in anim_nodes:
						# IF the anim node is valid, we store it to display
						if self.is_anim_node_valid( n ):
							anim_nodes.append( n )

			for anim_node in anim_nodes:
				#Check if there are notes and add anim nodes to the ui drop-down
				self.update_anim_nodes_list()

				# change the selected anim node
				if not self.anim_node:
					self.anim_node = anim_node

				if starting_anim_node:
					self.anim_node = starting_anim_node
					position = self.character_combo_ui.findText( starting_anim_node.LongName )
					if position > -1:
						# Set the ui to be the position of the previous anim node
						self.character_combo_ui.setCurrentIndex( position )

			if not self.anim_node:
				self.character_combo_ui.addItem( "No anim node" )
				return False

			# get the namespace
			self.namespace = vmobu.core.get_namespace_from_obj( self.anim_node, as_string = True )

			#self.repopulate_cells( )

			# update the anim controller path UI
			anim_controller = self.get_anim_controller( )
			if anim_controller:
				self.anim_controller_edit_ui.setText( anim_controller.LongName )

			# get the master node
			if not self.get_master_node( ):
				pyfbsdk.FBMessageBox( "Master Node Error", "There is no master node present to populate.\n Killing process.", "OK" )
				return False

			# update the anim path UI
			anim_path = self.get_anim_path( )
			if anim_path:

				# validate and fix the anim_path
				valid_anim_path, return_value, error_message = vmobu.mobu_export.mb_export.validate_anim_path( self.anim_node, self.master_node, anim_path )
				if valid_anim_path:
					anim_path = return_value

				# update the ui
				self.export_dir_ui.setText( anim_path )


			# update the rig path UI
			rig_file = self.get_rig_path( )
			if rig_file:

				#validate and fix the rig_file
				valid_rig_file, return_value, error_message = vmobu.mobu_export.mb_export.validate_rig_file( self.anim_node, self.master_node, rig_file )
				if valid_rig_file:
					rig_file = return_value

				# update the ui
				self.rigx_file_edit_ui.setText( rig_file )

			# update the list of tags in the Rigging tab
			self.update_tags_list( )

			# update the list of bones in the Rigging tab
			self.update_bones_list( )

			self.get_weight_groups( )

			self.setup_camera_anim_ramp(self.namespace)

		return True


	def load_widget( self ):
		"""
		Loads the widget from the .ui file of the anim exporter.

		*Arguments:*
		  * ``Argument`` Enter a description for the argument here.

		*Keyword Arguments:*
		  * PySide.QtGui.QMainWindow

		*Returns:*
		  * ``None``

		*Examples:* ::

		  >>> import Anim_Exporter
		  >>> Anim_Exporter.Anim_Exporter( ).load_widget( )
		"""

		#Set layout of UI
		layout = PySide.QtGui.QVBoxLayout( )
		layout.addWidget( self.anim_exporter_widget )
		self.setLayout( layout )

		self.update_ui_data( )
		self.refresh_anim_node()

		print "Anim Exporter Loaded!"

		return True

	def add_group_in_collection( self, name = 'NEW_GROUP' ):
		"""
		Add a new group in the weight groups list.

		*Arguments:*
		  * `None``

		*Keyword Arguments:*
		  * ``name`` A custom name if desired

		*Returns:*
		  * ``None``
		"""

		new_item = self.groups_list_ui.addItem( name )


	def edit_group_name( self ):
		"""
		Edits the name of the current selected group in weight group list.

		*Arguments:*
		  * ``None``

		*Keyword Arguments:*
		  * ``None``

		*Returns:*
		  * ``None``
		"""

		row = self.groups_list_ui.currentRow( )
		curr_item = self.groups_list_ui.item( row )

		curr_item.setFlags( curr_item.flags( ) | PySide.QtCore.Qt.ItemIsEditable )
		self.groups_list_ui.editItem( curr_item )


	def edit_bone_group( self ):
		"""
		Runs the edit collections ui, then connects them.

		*Arguments:*
		  * ``None``

		*Keyword Arguments:*
		  * ``None``

		*Returns:*
		  * ``None``
		"""

		self.load_collections_widget( )


	def get_active_weight_groups( self ):
		"""
		Get list of current weight groups.

		*Arguments:*
		  * ``None``

		*Keyword Arguments:*
		  * ``None``

		*Returns:*
		  * ``None``
		"""

		self.groups_list_ui.clear( )
		self.check_anim_node( )

		for prop in self.anim_node.PropertyList:
			if prop.Name.startswith( "wg" ):
				weight_group = prop.Name.split( ":" )[ 2 ]
				if not weight_group == "default":
					self.groups_list_ui.addItem( weight_group )


	def get_active_weighted_bones( self ):
		"""
		Get the list of assigned weighted bones.

		*Arguments:*
		  * ``None``

		*Keyword Arguments:*
		  * ``None``

		*Returns:*
		  * ``None``
		"""

		self.group_bone_list_ui.clear( )
		bones_array = [  ]

		#Get current anim node
		self.check_anim_node( )

		#Check the parent (master node) of the anim node and add bones to the array
		master_node = self.get_master_node( )
		if master_node:
			# get the hierarchy
			obj_hierarchy = vmobu.core.get_hierarchy( master_node )

			# delete the keys on each object in the hierarchy
			for child in obj_hierarchy:
				# double-check the namespace of the children objects
				if child.LongName.startswith( self.namespace ):
					p_bone_name = child.PropertyList.Find('p_bone_name')
					if p_bone_name:
						for prop in child.PropertyList:
							if prop.Name == 'p_bone_weightgroup':
								if prop.Data == "default" or prop.Data.lower() == 'none':
								#if prop.Data.lower() == 'none':
									pass
								else:
									if child not in bones_array:
										bones_array.append( child )
										self.group_bone_list_ui.addItem( str( child.LongName ) )


	def get_inactive_weighted_bones( self ):
		"""
		Get the list of unassigned weighted bones.

		*Arguments:*
		  * ``None``

		*Keyword Arguments:*
		  * ``None``

		*Returns:*
		  * ``None``
		"""

		self.unassigned_list_ui.clear( )
		bones_array = [  ]

		#Get current anim node
		self.check_anim_node( )

		master_node = self.get_master_node( )
		if master_node:
			# get the hierarchy
			obj_hierarchy = vmobu.core.get_hierarchy( master_node )

			# delete the keys on each object in the hierarchy
			for child in obj_hierarchy:
				# double-check the namespace of the children objects
				if child.LongName.startswith( self.namespace ):
					p_bone_name = child.PropertyList.Find('p_bone_name')
					if p_bone_name:
						pb_weightgroup = child.PropertyList.Find( "p_bone_weightgroup" )
						if not pb_weightgroup or pb_weightgroup.Data in [ None, 'none', 'default', 'None' ]:
							if child not in bones_array:
								bones_array.append( child )
								self.unassigned_list_ui.addItem( str( child.LongName ) )


	def groups_cell_was_clicked( self ):
		"""
		Checks the currently selected group in the collections list.

		*Arguments:*
		  * ``None``

		*Keyword Arguments:*
		  * ``None``

		*Returns:*
		  * ``None``
		"""

		row = self.groups_list_ui.currentRow( )
		col = self.groups_list_ui.currentColumn( )
		item = self.groups_list_ui.itemAt( row, col )
		self.ID = item.text( )

	def delete_group_from_collection( self ):
		"""
		Deletes group from the collection list.

		*Arguments:*
		  * ``None``

		*Keyword Arguments:*
		  * ``None``

		*Returns:*
		  * ``None``
		"""

		row = self.groups_list_ui.currentRow( )
		curr_item = self.groups_list_ui.item( row )
		self.groups_list_ui.takeItem( row )

		for comp in pyfbsdk.FBSystem( ).Scene.Components:

			for prop in comp.PropertyList:
				p_bone_name = comp.PropertyList.Find('p_bone_name')
				if p_bone_name:
					if prop.Name == 'p_bone_weightgroup':
						if prop.Data == str( curr_item.text( ) ):
							prop.Data = 'None'

		for prop in self.anim_node.PropertyList:
			if prop.Name.startswith( "wg" ):
				weight_group = prop.Name.split(":")[2]
				if weight_group == str( curr_item.text( ) ):
					self.anim_node.PropertyRemove( prop )

		self.update_group_bones( )
		self.get_inactive_weighted_bones()

		#self.get_active_weighted_bones( )


	def unassign_sel_group( self ):
		"""
		Sets the currently selected bone in the collections ui to have an unassigned weight group.

		*Arguments:*
		  * ``None``

		*Keyword Arguments:*
		  * ``None``

		*Returns:*
		  * ``None``
		"""

		selected_items = self.group_bone_list_ui.selectedItems( )
		if len( selected_items ) > 0:
			for sel in selected_items:
				sel.setSelected = True
				row = self.groups_list_ui.currentRow( )
				self.group_bone_list_ui.takeItem(row)
				self.unassigned_list_ui.addItem( str( sel.text( ) ) )
				assigned_item = self.group_bone_list_ui.item( row )
				assigned_item_index = self.group_bone_list_ui.indexFromItem( sel )
				assigned_obj = vmobu.core.get_object_by_name( str( sel.text( ) ), use_namespace=True, models_only=False)

				# update the weight group property
				if assigned_obj:
					set_prop = vmobu.core.set_property_obj( assigned_obj, 'p_bone_weightgroup', 'default' )

			for row in range( self.group_bone_list_ui.count( ) ):
				item = self.group_bone_list_ui.item( row )
				self.group_bone_list_ui.removeItemWidget( item )

			for row in range( self.unassigned_list_ui.count( ) ):
				item = self.unassigned_list_ui.item( row )
				self.unassigned_list_ui.removeItemWidget( item )

			self.group_bone_list_ui.clear()
			self.update_group_bones()

			self.get_inactive_weighted_bones()

		return True


	def assign_sel_group( self ):
		"""
		Sets the currently selected bone in the collections ui to be assigned to the selected weight group.

		*Arguments:*
		  * ``None``

		*Keyword Arguments:*
		  * ``None``

		*Returns:*
		  * ``None``
		"""

		selected_items = self.unassigned_list_ui.selectedItems( )
		selected_groups = self.groups_list_ui.selectedItems( )
		if len( selected_items ) > 0 and len( selected_groups ) == 1:
			for sel in selected_items:
				row = self.unassigned_list_ui.currentRow( )
				group_row = self.groups_list_ui.currentRow( )
				self.unassigned_list_ui.takeItem( row )
				#self.group_bone_list_ui.addItem( str( sel.text( ) ) )
				unassigned_item = self.unassigned_list_ui.item( row )
				unassigned_obj = vmobu.core.get_object_by_name( str( sel.text( ) ), use_namespace=True, models_only=False )

				# update the weight group property
				if unassigned_obj:
					selected_group = selected_groups[ 0 ].text( )
					set_prop = vmobu.core.set_property_obj( unassigned_obj, 'p_bone_weightgroup', selected_group )

			for row in range( self.group_bone_list_ui.count( ) ):
				item = self.group_bone_list_ui.item( row )
				self.group_bone_list_ui.removeItemWidget( item )

			for row in range( self.unassigned_list_ui.count( ) ):
				item = self.unassigned_list_ui.item( row )
				self.unassigned_list_ui.removeItemWidget( item )

			for sel in selected_items:
				self.group_bone_list_ui.addItem(str(sel.text()))

			self.get_inactive_weighted_bones()

		return True


	def cancel_edit_collections( self ):
		"""
		Closes the edit collections ui without making any changes in the scene.

		*Arguments:*
		  * ``None``

		*Keyword Arguments:*
		  * ``None``

		*Returns:*
		  * ``None``
		"""

		self.edit_dialog_collections_widget.close( )


	def finish_editing_collections( self ):
		"""
		Runs updates on the weight groups for the ui and the anim node once "OK" is pressed.

		*Arguments:*
		  * ``None``

		*Keyword Arguments:*
		  * ``None``

		*Returns:*
		  * ``None``
		"""
		self.check_anim_node( )
		if self.anim_node:
			collection_name = str( self.collection_name_ui.text( ) )
			self.collection_combo_ui.setEditText( collection_name )

			for row in range( self.groups_list_ui.count( ) ):
				item = self.groups_list_ui.item( row )
				item_str = "wg:{0}:{1}".format( collection_name , str( item.text( ) ) )

				anim_node_prop = self.anim_node.PropertyList.Find( item_str )
				if anim_node_prop:
					self.anim_node.PropertyRemove( anim_node_prop )
				#else:
					#anim_node_prop.Data = 0

				self.anim_node.PropertyCreate( item_str, pyfbsdk.FBPropertyType.kFBPT_int, "Int", True, True, None )

				for row in range( self.bone_group_table_ui.rowCount( ) ):
					self.bone_group_table_ui.removeRow( row )

			# Special case, account for the default weighting group
			item_str = "wg:default:default"
			if ( item_str not in [ prop.Name for prop in self.anim_node.PropertyList ] ):
				self.anim_node.PropertyCreate( item_str, pyfbsdk.FBPropertyType.kFBPT_int, "Int", True, True, None )

			for comp in pyfbsdk.FBSystem( ).Scene.Components:
				#if comp.ClassName( ) == 'FBModelSkeleton':
				p_bone_name = comp.PropertyList.Find('p_bone_name')
				if p_bone_name:
					wg_name = comp.PropertyList.Find( "p_bone_weightgroup" )
					wg_val = comp.PropertyList.Find( "p_bone_weight" )
					for an_prop in self.anim_node.PropertyList:
						if an_prop.Name.startswith( "wg" ):
							an_wg_name = an_prop.Name.split( ":" )[ 2 ]
							if wg_name:
								if wg_name.Data == an_wg_name:
									an_prop.Data = int( wg_val.Data )

								#if wg_val.IsAnimated( ):
								#	if wg_name.Data == an_wg_name:
								#		if not an_prop.IsAnimated():
								#			an_prop.SetAnimated( True )
								#		wg_anim = wg_val.GetAnimationNode( )
								#		an_prop_anim = an_prop.GetAnimationNode( )
								#		if wg_anim.FCurve:
								#			an_prop_anim.FCurve.KeyReplaceBy( wg_anim.FCurve )

								#except AttributeError:
								#  pass

			vmobu.core.evaluate()

			self.get_weight_groups( )

			vmobu.core.evaluate()

			self.edit_dialog_collections_widget.close( )

		return True


	def update_group_bones( self ):
		"""
		Update the list of bones with the given item group name

		*Arguments:*
			* ``item`` ui group item

		*Keyword Arguments:*
			* ``Argument`` Enter a description for the keyword argument here.

		*Returns:*
			* ``Value`` If any, enter a description for the return value here.
		"""

		self.group_bone_list_ui.clear( )
		bones_array = [  ]

		#Get current anim node
		self.check_anim_node( )

		selected_items = self.groups_list_ui.selectedItems()

		master_node = self.get_master_node( )
		if master_node:
			# get the hierarchy
			obj_hierarchy = vmobu.core.get_hierarchy( master_node )

			# delete the keys on each object in the hierarchy
			for child in obj_hierarchy:
				# double-check the namespace of the children objects
				if child.LongName.startswith( self.namespace ):
					p_bone_name = child.PropertyList.Find('p_bone_name')
					if p_bone_name:
						for prop in child.PropertyList:
							if prop.Name == 'p_bone_weightgroup':
								for sel in selected_items:
									if prop.Data != str( sel.text( ) ):
										pass
									else:
										if child not in bones_array:
											bones_array.append( child )
											self.group_bone_list_ui.addItem( str( child.LongName ) )


	def load_collections_widget( self ):
		"""
		Loads the edit collections widget.

		*Arguments:*
		  * ``None``

		*Keyword Arguments:*
		  * ``None``

		*Returns:*
		  * ``None``
		"""

		self.get_active_weight_groups( )
		self.get_inactive_weighted_bones( )
		self.collection_name_edit( )

		self.edit_dialog_collections_widget.open( )
	'''
	def restore_selection( func ):
		def _wrapper( *args, **kwargs):
			# Get the old selection indices
			old_selection = self.anim_list_ui.selectionModel( ).selectedRows( )

			# Run the function
			result = func( *args, **kwargs )

			# Clear selection
			for row in self.anim_list_ui.count( ):
				item = self.anim_list_ui.item( row )
				self.anim_list_ui.setItemSelected( item, False )

			# Restore old selection
			for row in old_selection:
				self.anim_list_ui.selectRow( row )

			return result

		return _wrapper
	'''

def run( ):
	"""
	Runs the creation and binding of the tool.

	*Arguments:*
	  * ``None``

	*Keyword Arguments:*
	  * ``None``

	*Returns:*
	  * ``None``

	*Examples:* ::

	  >>> import Anim_Exporter
	  >>> Anim_Exporter.run()
	"""

	main_tool_name = "Anim Exporter v{0}".format(VERSION)

	vmobu.core.evaluate()

	#Recreate development
	gDEVELOPMENT = True

	#Check if we need to recreate the tool
	if gDEVELOPMENT:
		pyfbsdk_additions.FBDestroyToolByName( main_tool_name )
		vmobu.core.evaluate()

	#Check if the tool is in the Mobu tool list
	if main_tool_name in pyfbsdk_additions.FBToolList:
		reload( Anim_Exporter )
		tool = pyfbsdk_additions.FBToolList[ main_tool_name ]
		pyfbsdk.ShowTool( tool )
	else:
		tool = Native_Qt_Widget_Tool( main_tool_name )
		pyfbsdk_additions.FBAddTool( tool )
		if gDEVELOPMENT:
			pyfbsdk.ShowTool( tool )

if not __name__ == '__main__':
	vmobu.core.logger.info( "menu.Anim_Exporter imported" )