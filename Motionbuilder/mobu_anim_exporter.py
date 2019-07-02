"""
Contains classes related to the Motionbuilder Anim Exporter.

*Todo:*
    *Add ability to add bones and props

*Author:*
    * Jon Logsdon, jon.logsdon@volition-inc.com, 3/13/2014 9:41:55 AM
    
"""

# Python std lib
import os
import sys
import urllib

# PySide
import PySide.QtCore
import PySide.QtGui
import PySide.QtUiTools
import PySide.shiboken
import pysideuic

# Motionbuilder lib
from pyfbsdk import *
from pyfbsdk_additions import *
import mbdebugger

# Volition Mobu callbacks
import vlib.callback

#vmobu
import vmobu
import core
import core.const
import vmobu.mobu_callback

#file_io
import file_io.perforce
import file_io.v_path
import file_io.v_fbx
import file_io.resource_lib
import diagnostics.dcc_logger


UI_FILE_PATH = os.path.abspath( os.path.join( vmobu.const.DCC_CORE_ABS, r'..\ui\anim_exporter.ui') )
ED_UI_FILE_PATH = os.path.abspath( os.path.join( vmobu.const.DCC_CORE_ABS, r'..\ui\editCollectionsDialog.ui') )
ICON_PATH = os.path.abspath( os.path.join( vmobu.const.DCC_CORE_ABS, r'..\icons\anim_exporter') )
VERSION = 3.0
STATUS_TIMEOUT = 3000
DEBUG = False

OPTION_USED_FOR_LOADING = False
OPTION_USED_FOR_SAVING = True
NO_LOAD_UI_DIALOG = False

class Native_Widget_Holder( FBWidgetHolder ):
  """
  Holder for the PySide widget.
  
  *Arguments:*
    * ``FBWidgetHolder`` Mobu holder for 3rd party widgets.
  
  *Keyword Arguments:*
    * ``None``
  
  *Author:*
    * Jon Logsdon, jon.logsdon@volition-inc.com, 4/10/2014 5:07:09 PM
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
    
    *Author:*
      * Jon Logsdon, jon.logsdon@volition-inc.com, 4/10/2014 5:10:33 PM
    """

    FBSystem( ).Scene.Evaluate( )
    
    loader = PySide.QtUiTools.QUiLoader( ) 
    self.anim_exporter_widget = loader.load( UI_FILE_PATH ) 
    self.pointer = PySide.shiboken.getCppPointer( self.anim_exporter_widget )[ 0 ]    

    try:
      Anim_Exporter( self.anim_exporter_widget )
    except AttributeError:
      FBSystem( ).Scene.Evaluate( )
      self.WidgetCreate( pWidgetParent )
      
    FBSystem( ).Scene.Evaluate( )
    
    return self.pointer

class Native_Qt_Widget_Tool( FBTool ):
  """
  Builds the Mobu window holder for the PySide widget.
  
  *Arguments:*
    * ``FBTool`` The main function for a Mobu tool.
  
  *Author:*
    * Jon Logsdon, jon.logsdon@volition-inc.com, 4/10/2014 5:18:03 PM
  """
  
  def __init__( self, name ):
    FBTool.__init__( self, name )
    self.widget_holder = Native_Widget_Holder( );
    self.build_layout()
    self.StartSizeX = 600
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
    
    *Author:*
      * Jon Logsdon, jon.logsdon@volition-inc.com, 4/10/2014 5:18:55 PM
    """
    
    x = FBAddRegionParam( 0,FBAttachType.kFBAttachLeft, "" )
    y = FBAddRegionParam( 0,FBAttachType.kFBAttachTop, "" )
    w = FBAddRegionParam( 0,FBAttachType.kFBAttachRight, "" )
    h = FBAddRegionParam( 0,FBAttachType.kFBAttachBottom, "" )
    self.AddRegion( "main","main", x, y, w, h )
    self.SetControl( "main", self.widget_holder )  

class Anim_Exporter( PySide.QtGui.QMainWindow ):
  """
  Main class for Motionbuilder animation exporter data and manipulation.
  
  *Examples:* ::
  
    >>> import mobu_anim_exporter
    >>> anim_exporter = Anim_Exporter( )
  
  *Author:*
    * Jon Logsdon, jon.logsdon@volition-inc.com, 3/13/2014 9:41:55 AM
  """
  
  def __init__( self, anim_exporter_widget ):
    """
    Call .ui file for anim_exporter, and load all aspects into Motionbuilder space.
    
    *Arguments:*
      * parent
    
    *Returns:*
      * UI elements
    
    *Author:*
      * Jon Logsdon, jon.logsdon@volition-inc.com, 3/13/2014 9:53:32 AM
    """
    
    FBSystem( ).Scene.Evaluate( )
    
    self.anim_exporter_widget = anim_exporter_widget    
    
    #Set Mobu system and scene
    system = FBSystem( )
    self.scene = system.Scene
    
    self.curr_filename = FBApplication( ).FBXFileName
    
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
    self.anim_node = None
    self.anim_controller = None
    self.master = None
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
    
    #Connect with UI classes for animation tab
    self.tab_widget = self.anim_exporter_widget.tabWidget
    self.project_line_edit = self.anim_exporter_widget.projectLineEdit
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
    
    #Connect with documentation classes 
    self.action_debug_on = self.anim_exporter_widget.actionDebugOn
    
    #Grab the current take stop and start frames
    self.end_time = FBSystem( ).CurrentTake.LocalTimeSpan.GetStop( )
    self.end_frame = FBSystem( ).CurrentTake.LocalTimeSpan.GetStop( ).GetFrame( )
    self.start_time = FBSystem( ).CurrentTake.LocalTimeSpan.GetStart( )
    self.start_frame = FBSystem( ).CurrentTake.LocalTimeSpan.GetStart( ).GetFrame( )
    
    self.anim_list_ui.setColumnWidth( 0, 200 )
    for i in range( 1, 5 ):
      self.anim_list_ui.setColumnWidth( i, 60 )
      
    self.bone_group_table_ui.setColumnWidth( 1, 70 )
    
    #Set connections for animation tab buttons
    self.add_animation_button_ui.clicked.connect( self.add_animation )
    self.set_timerange_button_ui.clicked.connect( self.set_current_table_timerange )
    self.batch_button.clicked.connect( self.batch_process )
    self.animx_export_sel_ui.clicked.connect( self.anim_export_sel )
    self.animx_browse_ui.clicked.connect( self.browse_anim_export_dirs )
    self.update_button_ui.clicked.connect( self.refresh_anim_node )
    self.browse_button.clicked.connect( self.browse_batch_dirs )
    self.animx_copy_ui.clicked.connect( self.copy_anim_export_path )
    self.animx_paste_ui.clicked.connect( self.paste_anim_export_path )
    self.animx_clear_ui.clicked.connect( self.clear_anim_export_path )
    self.delete_animation_button_ui.clicked.connect( self.delete_animation_cell )
    self.animx_export_all_ui.clicked.connect( self.export_all_anim )
    self.move_up_button_ui.clicked.connect( self.move_anim_row_up )
    self.move_down_button_ui.clicked.connect( self.move_anim_row_down )
    self.copy_all_animation_ui.clicked.connect( self.copy_all_sel_anim )
    self.paste_all_animation_ui.clicked.connect( self.paste_all_sel_anim )
  
    self.anim_list_ui.setUpdatesEnabled( True )
    
    #Set connection for anim_node drop-down
    self.character_combo_ui.currentIndexChanged.connect( self.update_widget_for_curr_node )
    
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
    
    #self.action_debug_on.triggered.connect( self.debug_on )
    
    #Set initial line edits texts to blank
    self.export_dir_ui.setText( '' )
    self.rigx_file_edit_ui.setText( '' )
    self.anim_controller_edit_ui.setText( '' ) 

    #Set key bindings function to the main widget
    self.anim_exporter_widget.installEventFilter( self )
  
    #Call the loading of the widget function
    self.load_widget( )
    
    #self.on_new_before( )
    
    #Sets initial callbacks
    self.add_application_callbacks( )  
  
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
    
    *Author:*
      * Jon Logsdon, jon.logsdon@volition-inc.com, 4/8/2014 2:38:22 PM
    """
    
    curr_anim_node_text = str( self.character_combo_ui.currentText( ) )
    self.anim_node = vmobu.core.get_object_by_name( curr_anim_node_text, use_namespace=True, models_only=False )  
    
    if self.anim_node:
      return True
    #else:
    #  FBMessageBox( "Anim Node Error", "The current anim node does not exist.\n Killing process.", "OK" )
    
  def update_widget_for_curr_node( self ):
    """
    Updates widget for the current anim node selected.
    
    *Arguments:*
      * ``None``
    
    *Keyword Arguments:*
      * ``None``
    
    *Returns:*
      * ``self.character_combo_ui.currentText()`` 

    *Author:*
      * Jon Logsdon, jon.logsdon@volition-inc.com, 3/13/2014 11:05:55 AM
    """
    
    #Grab current index and anim_node from drop-down
    curr_index = self.character_combo_ui.currentIndex( )
    self.character_combo_ui.itemData( curr_index )
    curr_combo_item_string = self.character_combo_ui.currentText( ) 
    
    for row in range( self.anim_list_ui.rowCount( ) ):
      self.anim_list_ui.removeRow( row )
        
    self.repopulate_cells( )
      
  def add_animation( self ):
    """
    Adds all aspects to creating a new "animation" within the exporter.
    
    *Arguments:*
      * ``None``
    
    *Keyword Arguments:*
      * ``None``
    
    *Returns:*
      * ``None``
    
    *Author:*
      * Jon Logsdon, jon.logsdon@volition-inc.com, 3/13/2014 11:06:32 AM
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
    
    *Author:*
      * Jon Logsdon, jon.logsdon@volition-inc.com, 3/13/2014 11:06:57 AM
    """
    
    #Inserts a new animation row within the UI and runs method to populate fields of animation row
    self.anim_list_ui.insertRow( 0 )
    item = PySide.QtGui.QTableWidgetItem( )
    self.anim_list_ui.setItem( 0, 0, item )
    
    self.set_take_properties( )
    self.store_anim_takes( )
    
    
  def set_take_properties( self, row=None ):
    """
    Sets the properties for the current take in the exporter.
    
    *Arguments:*
      * ``row`` The row of the anim exporter Animation tab.
    
    *Keyword Arguments:*
      * ``None``
    
    *Returns:*
      * ``None``
    
    *Author:*
      * Jon Logsdon, jon.logsdon@volition-inc.com, 3/13/2014 11:07:17 AM
    """
    
    #Refresh scene and check if a row is present, and declare the selected row and column as 'row' and 'col'
    FBSystem( ).Scene.Evaluate( )
    if row is None:
      row = 0
    else:
      row = self.anim_list_ui.currentRow( )
    
    #Grab current Mobu take  
    curr_take = vmobu.core.get_current_take( )
    
    #Set the default name of newly created animation row in UI as the take name
    take_name_widget_item = PySide.QtGui.QTableWidgetItem( )
    self.anim_list_ui.setItem( 0, 0, take_name_widget_item )    
    take_name_widget_item.setText( curr_take.Name )
    
    #Grab current anim_node name from drop-down and find it in scene based on it's name
    self.check_anim_node( )
    
    #Grab the parent of the anim_node (the master) and set default ramp-in, ramp-out, and framerate in anim_node based off master
    for parent in self.anim_node.Parents:
      if not isinstance( parent, FBScene ):
        sel_namespace = parent.LongName.split( ":" )
        master = vmobu.core.get_objects_from_wildcard( sel_namespace[ 0 ] + ":*Master", use_namespace=True ) 
        try:
          if master.PropertyList.Find( 'p_export_rampin' ) != "":
            rig_ramp_in = master.PropertyList.Find( 'p_export_rampin' )
            rig_ramp_out = master.PropertyList.Find( 'p_export_rampout' )
            rig_frame_rate = master.PropertyList.Find( 'p_export_framerate' )
        except AttributeError:
          print "There is no Master control to selection."
          self.close_event( )
    
    #Populate columns of UI with the ramp-in, ramp-out, and framerate values  
    ramp_in_widget_item = PySide.QtGui.QTableWidgetItem( )
    self.anim_list_ui.setItem( row, 3, ramp_in_widget_item )
    ramp_in_widget_item.setText( str( rig_ramp_in ) )
    
    ramp_out_widget_item = PySide.QtGui.QTableWidgetItem( )
    self.anim_list_ui.setItem( row, 4, ramp_out_widget_item )
    ramp_out_widget_item.setText( str( rig_ramp_out ) )    
    
    framerate_widget_item = PySide.QtGui.QTableWidgetItem( )
    self.anim_list_ui.setItem( row, 5, framerate_widget_item )
    framerate_widget_item.setText( str( rig_frame_rate ) )
    
    #Grab current take's start and end frames
    start = FBSystem( ).CurrentTake.LocalTimeSpan.GetStart( ).GetFrame( ) 
    end = FBSystem( ).CurrentTake.LocalTimeSpan.GetStop( ).GetFrame( )      
    
    #Set start and end frame values in the UI
    start_frame_widget_item = PySide.QtGui.QTableWidgetItem( )
    self.anim_list_ui.setItem( row, 1, start_frame_widget_item )
    start_frame_text = start_frame_widget_item.setText( str( start ) )
  
    end_frame_widget_item = PySide.QtGui.QTableWidgetItem( )
    self.anim_list_ui.setItem( row, 2, end_frame_widget_item )
    end_frame_widget_item.setText( str( end ) )    
    
  def set_current_table_timerange( self, row=None ):
    """
    Sets current timerange from Motionbuilder within the exporter.
    
    *Arguments:*
      * ``None``
    
    *Keyword Arguments:*
      * ``row`` Rows of the animation tab in Anim Exporter
    
    *Returns:*
      * ``None``
    
    *Author:*
      * Jon Logsdon, jon.logsdon@volition-inc.com, 3/13/2014 11:07:34 AM
    """
    
    #Refresh scene and check if a row is present, and declare the selected row and column as 'row' and 'col'
    FBSystem( ).Scene.Evaluate( )
    
    altered_end = FBPlayerControl( ).GotoEnd( )
    end_frame = FBSystem( ).LocalTime.GetFrame( )
    start_frame = FBSystem( ).CurrentTake.LocalTimeSpan.GetStart( ).GetFrame( )  
    
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
    
    *Author:*
      * Jon Logsdon, jon.logsdon@volition-inc.com, 3/13/2014 11:07:52 AM
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
        
  def export_all_anim( self ):
    """
    Exports all animation of one character based off animation made in the ui
    
    *Arguments:*
      * ``None``
    
    *Keyword Arguments:*
      * ``None``
    
    *Returns:*
      * ``None``
    
    *Author:*
      * Jon Logsdon, jon.logsdon@volition-inc.com, 3/20/2014 9:55:48 AM
    """
    
    #Grab current row and column in ui, as well as the currently selected animation cell widget
    for row in range( self.anim_list_ui.rowCount( ) ): 
      if row < 1:
        self.anim_list_ui.selectRow( 0 )
        self.anim_export_sel( )
      else:
        self.anim_list_ui.selectRow( row )
        self.anim_export_sel( )
        
  def lock_proper_constraints( self ): 
    """
    Sets the anim controller, offset bone, and aim node to be at the character's feet for export.
    
    *Arguments:*
      * ``None``
    
    *Keyword Arguments:*
      * ``None`` 
    
    *Returns:*
      * ``None``
    
    *Author:*
      * Jon Logsdon, jon.logsdon@volition-inc.com, 5/7/2014 4:39:21 PM
    """
    
    self.check_anim_node( )
    
    curr_char_namespace = self.anim_node.LongName.split( ":" )
    anim_controller = vmobu.core.get_objects_from_wildcard( curr_char_namespace[ 0 ] + ":*skel:AnimationController", use_namespace=True )
    offset_node = vmobu.core.get_objects_from_wildcard( curr_char_namespace[ 0 ] + ":*skel:Offset", use_namespace=True )
    aim_node = vmobu.core.get_objects_from_wildcard( curr_char_namespace[ 0 ] + ":*skel:AimNode", use_namespace=True )
    aim_node_group = vmobu.core.get_objects_from_wildcard( curr_char_namespace[ 0 ] + ":*skel:AimNodeGroup", use_namespace=True )
    
    anim_driver_vector_trans = FBVector3d( )
    anim_driver_vector_rot = FBVector3d( )
    offset_controller_vector_trans = FBVector3d( )
    offset_controller_vector_rot = FBVector3d( )
    anim_driver = vmobu.core.get_objects_from_wildcard( curr_char_namespace[ 0 ] + ":*AnimationController_controller", use_namespace=True )
    offset_controller = vmobu.core.get_objects_from_wildcard( curr_char_namespace[ 0 ] + ":*skel:Offset_controller", use_namespace=True )
    
    if anim_controller:
      for const in FBSystem( ).Scene.Constraints:
        if 'AnimationController' in const.Name:
          lock_prop = const.PropertyList.Find( 'Lock' )
          lock_prop.Data = False           
  
      anim_driver.GetVector( anim_driver_vector_rot, FBModelTransformationType.kModelRotation )
      anim_controller.SetVector( FBVector3d( anim_driver_vector_rot ), FBModelTransformationType.kModelRotation )    
      
      anim_driver.GetVector( anim_driver_vector_trans, FBModelTransformationType.kModelTranslation )
      anim_controller.SetVector( FBVector3d( anim_driver_vector_trans ), FBModelTransformationType.kModelTranslation )
      
      FBSystem( ).Scene.Evaluate( )
      
      for const in FBSystem( ).Scene.Constraints:
        if 'AnimationController' in const.Name:
          lock_prop = const.PropertyList.Find( 'Lock' )
          if lock_prop.Data != True:
            lock_prop.Data = True
            
    if offset_node:
      for const in FBSystem( ).Scene.Constraints:
        if 'Offset' in const.Name:
          lock_prop = const.PropertyList.Find( 'Lock' )
          lock_prop.Data = False  
          
      offset_controller.GetVector( offset_controller_vector_trans, FBModelTransformationType.kModelTranslation )
      offset_controller.GetVector( offset_controller_vector_rot, FBModelTransformationType.kModelRotation )
          
      offset_node.SetVector( FBVector3d( offset_controller_vector_rot ), FBModelTransformationType.kModelRotation )
      offset_node.SetVector( FBVector3d( offset_controller_vector_trans ), FBModelTransformationType.kModelTranslation )
      
      FBSystem( ).Scene.Evaluate( )
      
      for const in FBSystem( ).Scene.Constraints:
        if 'Offset' in const.Name:
          lock_prop = const.PropertyList.Find( 'Lock' )
          if lock_prop.Data != True:
            lock_prop.Data = True
      
    if aim_node:
      for const in FBSystem( ).Scene.Constraints:
        if 'AimNode' in const.Name and not 'AimNodeGroup' in const.Name:
          lock_prop = const.PropertyList.Find( 'Lock' )
          lock_prop.Data = False
          
      anim_driver.GetVector( anim_driver_vector_trans, FBModelTransformationType.kModelTranslation )
      anim_driver.GetVector( anim_driver_vector_rot, FBModelTransformationType.kModelRotation )
      
      aim_node_group.SetVector( FBVector3d( anim_driver_vector_rot ), FBModelTransformationType.kModelRotation )
      aim_node_group.SetVector( FBVector3d( anim_driver_vector_trans ), FBModelTransformationType.kModelTranslation )
      aim_node.SetVector( FBVector3d( anim_driver_vector_rot ), FBModelTransformationType.kModelRotation )
      aim_node.SetVector( FBVector3d( anim_driver_vector_trans ), FBModelTransformationType.kModelTranslation )
      
      FBSystem( ).Scene.Evaluate( )
      
      for const in FBSystem( ).Scene.Constraints:
        if 'AimNodeGroup' in const.Name:
          lock_prop = const.PropertyList.Find( 'Lock' )
          if lock_prop.Data != True:
            lock_prop.Data = True
            
  def check_min_boneweight_values( self ):
    """
    Sets the minimum value of the 'p_bone_weight' property to 0.
    
    *Arguments:*
      * ``None`` 
    
    *Keyword Arguments:*
      * ``None`` 
    
    *Returns:*
      * ``None``
    
    *Author:*
      * Jon Logsdon, jon.logsdon@volition-inc.com, 5/19/2014 5:17:12 PM
    """
    
    for comp in FBSystem( ).Scene.Components:
      for prop in comp.PropertyList:
        if prop.Name == 'p_bone_weight':
          prop.SetMin( 0 )
  
  def anim_export_sel( self, remove_namespace=True ):
    """
    Exports animation based on the animation cell widget selected in the exporter.
    
    *Arguments:*
      * ``None``
    
    *Keyword Arguments:*
      * ``None`` 
    
    *Returns:*
      * ``None``
    
    *Author:*
      * Jon Logsdon, jon.logsdon@volition-inc.com, 3/13/2014 11:08:23 AM
    """
    
    #Refresh 3d space
    FBSystem( ).Scene.Evaluate( )
    
    self.refresh_anim_node( )
    
    application = FBApplication( )
    
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
    #Get current take
    curr_take = vmobu.core.get_current_take( )    
    
    #Set export path from the ui  
    set_export_path = os.path.join( core.const.workspace_dir, self.export_dir_ui.text( ) )    
      
    self.filepath = os.path.join( str( set_export_path ), str( anim_name.text( ) ) + ".anim.fbx" ) 
    self.filepath = self.filepath.replace( '/', '\\' )

    try:
      file_io.resource_lib._initialize_resourcelib( )
    except:
      FBMessageBox( "Export Error", "Could not initialize resourcelib!\n Quitting!", "OK" )
      return False
    
    for prop in self.anim_node.PropertyList:
      if prop.Name.endswith( "export_rig" ):
        rig_file = prop.Data
        
    if not rig_file:
      FBMessageBox( "Rig Error", "A valid rig has not been set!", "OK" )
      return False
    else:
      try:
        rig_file_info = file_io.resource_lib._resourcelib.get_file_info( os.path.basename( rig_file ) )
      except RuntimeError:
        FBMessageBox( "Export Error", "Rig filename is not a valid resource: {0}.".format( rig_file ), "OK" )
        return False
      
      if rig_file_info:
        rig_filename = rig_file_info.get_local_relative_filename( )
        for prop in self.anim_node.PropertyList:
          if prop.Name.endswith( "export_rig" ):
            prop.Data = str( rig_filename )
      else:
        FBMessageBox( "Rig Error", "A valid rig file has not been set!", "OK" )
        return False
    
    FBSystem( ).Scene.Evaluate( )
    
    export_nodes_name = self.anim_node.PropertyList.Find( "Bones" )
    
    #Set export path from the ui
    set_export_path = os.path.join( core.const.workspace_dir, self.export_dir_ui.text( ) )
      
    if os.path.exists( set_export_path ):
      #self.setup_resource_lib( )
      
      filename = application.FBXFileName    
      
      #Grab current character's master node
      sel_namespace = self.anim_node.LongName.split( ":" )
      #master = vmobu.core.get_objects_from_wildcard( sel_namespace[ 0 ] + ":*Master", use_namespace=True )    
      
      #Get start and end frame from selected
      start_frame_item_ui = self.anim_list_ui.item( row, 1 )
      end_frame_item_ui = self.anim_list_ui.item( row, 2 )  
      
      #User's start and end frame based off ui animation cell widget
      user_start_frame = int( start_frame_item_ui.text( ) )
      user_end_frame = int( end_frame_item_ui.text( ) )    
      
      #Set our plotting to skeleton from Ctrl rig
      skeleton = FBCharacterPlotWhere.kFBCharacterPlotOnSkeleton
      
      #Plot to skeleton
      plot_options = FBPlotOptions( )
      plot_options.ConstantKeyReducerKeepOneKey = False
      plot_options.PlotAllTakes = False
      plot_options.PlotOnFrame = True
      
      #Save/export animation
      fbx_options = FBFbxOptions( False )
      fbx_options.SetAll( FBElementAction.kFBElementActionDiscard, False )
      fbx_options.UseASCIIFormat = True
      fbx_options.Bones = FBElementAction.kFBElementActionSave
      fbx_options.BonesAnimation = True
      fbx_options.Models = FBElementAction.kFBElementActionSave
      fbx_options.Characters = FBElementAction.kFBElementActionDiscard
      fbx_options.Actors = FBElementAction.kFBElementActionDiscard
      fbx_options.Constraints = FBElementAction.kFBElementActionDiscard
      fbx_options.Solvers = FBElementAction.kFBElementActionDiscard
      fbx_options.CharactersAnimation = False
      fbx_options.SaveControlSet = False
      fbx_options.SaveSelectedModelsOnly = True
      
      self.check_min_boneweight_values( )
      
      for take in FBSystem( ).Scene.Takes:
        for index in range( fbx_options.GetTakeCount( ) ):
          if fbx_options.GetTakeName( index ) == take.Name:
            fbx_options.SetTakeSelect( index, True )
          else:
            fbx_options.SetTakeSelect( index, False )
      
      if anim_cell_clicked:
        curr_char.PlotAnimation( skeleton, plot_options )
      
        #if not master.Selected:
        #  master.Selected = True
          
        export_file = os.path.join( str( set_export_path ), str( anim_name.text( ) ) + ".anim.fbx" )
        
        self.lock_proper_constraints( )
        
        #Check if the file is already checked out
        if export_file :
          self.get_latest( export_file )
          print "Got latest."

          self.checkout( export_file )
          print "Checked out!"
          file_io.perforce.edit( export_file ) 
          
          selection_array = [ ]
          if curr_char:
            for comp in FBSystem( ).Scene.Components:
              comp.Selected = False
              if comp.ClassName() != 'FBSet':
                if comp.Name == 'Master':
                  selection_array.append( comp )
                  for child in comp.Children:
                    for prop in child.PropertyList:
                      if prop.Name == 'p_bone_weight':
                        if prop.Data > 0:
                          selection_array.append( child )
                        else:
                          if child in selection_array:
                            selection_array.remove( child )
            
            for sel in selection_array:
              if "Effector" in sel.Name:
                sel.Selected = False
              else:
                sel.Selected = True
              
            lModels = FBModelList()
            FBGetSelectedModels(lModels)
            application.SaveCharacterRigAndAnimation( export_file, curr_char, fbx_options )
          
          _type = "fbx_anim"
          
          if not file_io.resource_lib.submit( export_file, _type ):
            FBMessageBox( "Crunch Error", "Unable to submit export for crunch.", "OK" )
            return False
          else:
            #self.setup_attributes_for_crunch( )
            char_namespace = self.anim_node.LongName.split( ":" )
            master = vmobu.core.get_objects_from_wildcard( char_namespace[ 0 ] + ":*Master", use_namespace=True ) 
            rig_version_prop = master.PropertyList.Find( "p_rig_version" )
            rig_version = rig_version_prop.Data
            if not rig_version:
              print "No rig version set"
            
            if os.path.exists( export_file ):
              if remove_namespace:
                vfbx = file_io.v_fbx.FBX( export_file )
                vfbx.remove_namespace( )
                vfbx.clean_up( )   
                
              if self.curr_filename == "":
                self.curr_filename = export_file
                
              #Set attributes for resource lib  
              att_dict = { 'associated_character_rig': str( rig_file ), 'rig_version': str( rig_version ),
                          'source_asset_file': file_io.resource_lib.get_relative_filename( self.curr_filename ) }
              if not file_io.resource_lib.set_attributes( export_file, att_dict ):
                print "Skipping: {0}".format( export_file )
                return False            
                          
              if not file_io.resource_lib.crunch( export_file ):
                return False
              
              FBMessageBox( "Export Status", "Animation exported!\n", "OK" )
              self.set_character_source( )
              
              backup_file = export_file + ".bck"
              if os.path.exists( export_file ):
                self.remove_backup_folder( backup_file )               
        else:
          FBMessageBox( "Export Error", "No animation to export!\n", "OK" )
    else:
      FBMessageBox( "File Path Error", "The current path does not exist.", "OK" )
      
  def anim_export_batch( self ):
    """
    Exports batch animation based on current characters in the scene and animations added to their anim node.
    
    *Arguments:*
      * ``None``
    
    *Keyword Arguments:*
      * ``None``
    
    *Returns:*
      * ``None``
    
    *Author:*
      * Jon Logsdon, jon.logsdon@volition-inc.com, 3/13/2014 11:08:23 AM
    """
    
    #Refresh 3d space
    FBSystem( ).Scene.Evaluate( )
    
    self.refresh_anim_node( )
    
    application = FBApplication( )
    
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

    #Set export path from the ui  
    set_export_path = os.path.join( core.const.workspace_dir, self.batch_dir.text( ) )    
      
    self.filepath = os.path.join( str( set_export_path ), str( anim_name.text( ) ) + ".anim.fbx" ) 
    self.filepath = self.filepath.replace( '/', '\\' )

    try:
      file_io.resource_lib._initialize_resourcelib( )
    except:
      FBMessageBox( "Export Error", "Could not initialize resourcelib!\n Quitting!", "OK" )
      return False
    
    for prop in self.anim_node.PropertyList:
      if prop.Name.endswith( "export_rig" ):
        rig_file = prop.Data
        
    if not rig_file:
      FBMessageBox( "Rig Error", "A valid rig has not been set!", "OK" )
      return False
    else:
      rig_file_info = None
      try:
        rig_file_info = file_io.resource_lib._resourcelib.get_file_info( os.path.basename( rig_file ) )
      except RuntimeError:
        FBMessageBox( "Export Error", "Rig filename is not a valid resource: {0}.".format( rig_file ), "OK" )
        return False
      
      if rig_file_info:
        rig_filename = rig_file_info.get_local_relative_filename( )
        for prop in self.anim_node.PropertyList:
          if prop.Name.endswith( "export_rig" ):
            prop.Data = str( rig_filename )
      else:
        FBMessageBox( "Rig Error", "A valid rig file has not been set!", "OK" )
        return False
    
    FBSystem( ).Scene.Evaluate( )
    
    export_nodes_name = self.anim_node.PropertyList.Find( "Bones" )
    
    #Set export path from the ui
    set_export_path = os.path.join( core.const.workspace_dir, self.batch_dir.text( ) )
      
    if os.path.exists( set_export_path ):
      #Grab current character's master node
      sel_namespace = self.anim_node.LongName.split( ":" )
      master = vmobu.core.get_objects_from_wildcard( sel_namespace[ 0 ] + ":*Master", use_namespace=True )    
      
      #Get start and end frame from selected
      start_frame_item_ui = self.anim_list_ui.item( row, 1 )
      end_frame_item_ui = self.anim_list_ui.item( row, 2 )  
      
      #User's start and end frame based off ui animation cell widget
      user_start_frame = int( start_frame_item_ui.text( ) )
      user_end_frame = int( end_frame_item_ui.text( ) )    
      
      master.Selected = True
      
      #Set our plotting to skeleton from Ctrl rig
      skeleton = FBCharacterPlotWhere.kFBCharacterPlotOnSkeleton
      
      #Plot to skeleton
      plot_options = FBPlotOptions( )
      plot_options.ConstantKeyReducerKeepOneKey = False
      plot_options.PlotAllTakes = True
      plot_options.PlotOnFrame = True
      
      #Save/export animation
      fbx_options = FBFbxOptions( False )
      fbx_options.SaveCharacter = True
      fbx_options.SaveControlSet = False
      fbx_options.SaveCharacterExtension = False
      fbx_options.ShowFileDialog = False
      fbx_options.ShowOptionsDialog = False
      fbx_options.UseASCIIFormat = True
      
      for take in FBSystem( ).Scene.Takes:
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
            FBMessageBox( "Crunch Error", "Unable to submit export for crunch.", "OK" )
            return False
          else:
            #self.setup_attributes_for_crunch( )
            char_namespace = self.anim_node.LongName.split( ":" )
            master = vmobu.core.get_objects_from_wildcard( char_namespace[ 0 ] + ":*Master", use_namespace=True ) 
            rig_version = master.PropertyList.Find( "p_rig_version" )
            rig_version = rig_version.Data
            if not rig_version:
              print "No rig version set"
              
            att_dict = { 'associated_character_rig': str( rig_file ), 'rig_version': rig_version,
                        'source_asset_file': file_io.resource_lib.get_relative_filename( FBSystem( ).CurrentDirectory( ) ) }
            if not file_io.resource_lib.set_attributes( self.filepath, att_dict ):
              print "Skipping: {0}".format( self.filepath )
              return False
            if os.path.exists( export_file ):
              file_io.resource_lib.crunch( export_file )
              FBMessageBox( "Export Status", "Animation exported!\n", "OK" )
              self.set_character_source( )
              
              backup_file = export_file + ".bck"
              if os.path.exists( backup_file ):
                self.remove_batch_backup_folder( export_file )
              else:
                pass
        else:
          FBMessageBox( "Export Error", "No animation to export!\n", "OK" )
    else:
      FBMessageBox( "File Path Error", "The current path does not exist.", "OK" )
      
  def remove_backup_folder( self, filepath='' ):
    """
    Removes the backup folder created when exporting.
    
    *Arguments:*
      * ``None``
    
    *Keyword Arguments:*
      * ``filepath`` Filepath of export file
    
    *Returns:*
      * ``None``
    
    *Author:*
      * Jon Logsdon, jon.logsdon@volition-inc.com, 3/28/2014 4:05:16 PM
    """
    
    row = self.anim_list_ui.currentRow( )
    selection_take = self.anim_list_ui.item( row, 0 )    
    if filepath:
      set_export_path = os.path.join( core.const.workspace_dir, str( self.export_dir_ui.text( ) ), str( selection_take.text( ) ) )
      self.filepath = file_io.v_path.Path( set_export_path + ".anim.bck")  
      
      for f in os.listdir( self.filepath ):
        curr_file = os.path.join( self.filepath, f )
        try:
          if os.path.isfile( curr_file ):
            os.unlink( curr_file )
        except IOError:
          pass
        
      if os.path.exists( self.filepath ):
        os.rmdir( self.filepath )
      
  def remove_batch_backup_folder( self, filepath='' ):
    """
    Removes the backup folder created when batch exporting.
    
    *Arguments:*
      * ``None``
    
    *Keyword Arguments:*
      * ``filepath`` Filepath of export file
    
    *Returns:*
      * ``None``
    
    *Author:*
      * Jon Logsdon, jon.logsdon@volition-inc.com, 3/28/2014 4:05:16 PM
    """
    
    row = self.anim_list_ui.currentRow( )
    selection_take = self.anim_list_ui.item( row, 0 )    
    if filepath:
      set_export_path = os.path.join( core.const.workspace_dir, str( self.batch_dir.text( ) ), str( selection_take.text( ) ) )
      self.filepath = file_io.v_path.Path( set_export_path + ".anim.bck")  
      
      if self.filepath:
        for files in self.filepath:
          curr_files = os.path.join( self.filepath, files )
          try:
            if os.path.isfile( curr_files ):
              os.unlink( curr_files )
          except RuntimeError:
            pass
        os.rmdir( self.filepath )
      else:
        print "No backup folders found. Moving forward."
        pass
      
  def mark_for_add( self, filepath='', quiet=False ):
    """
    Marks the animation export to add to Perforce.
    
    *Arguments:*
      * ``None``
    
    *Keyword Arguments:*
      * ``filepath`` Filepath of export file
    
    *Returns:*
      * ``None``
    
    *Author:*
      * Jon Logsdon, jon.logsdon@volition-inc.com, 3/28/2014 4:04:53 PM
    """
    
    row = self.anim_list_ui.currentRow( )
    selection_take = self.anim_list_ui.item( row, 0 )
    if filepath:
      set_export_path = os.path.join( core.const.workspace_dir, str( self.export_dir_ui.text( ) ), str( selection_take.text( ) ) )
      self.filepath = file_io.v_path.Path( set_export_path + ".anim.fbx")
      print self.filepath
      
    #if not quiet:
    #  FBSystem( ).Scene.Evaluate( )
    
    if not self.filepath.exists( ):
      if not quiet:
        FBMessageBox( "New file", "No file with name: {0}".format(
          self.filepath ), "OK", "Cancel" )
      return False
    
    print "Made it here!"
    
    if self.in_depot( self.filepath ):
      print "It's here!"
      self.checkout( self.filepath )
    else:
      file_io.perforce.add( [ self.filepath ], binary=False, changelist=self.get_changelist_number( ) )
      print "Added to Perforce"
      
    #result = FBMessageBox( "Ready for crunch", "This file is ready for crunch.\n Do so now?", "OK", "Cancel" )
    
    #if not result == "OK":
    #  return False
    
    #else:
    #  self.crunch_export( self.filepath )
      
    return True
  
  def crunch_export( self, filepath, ui=True ):
    """
    Crunches the animation export.
    
    *Arguments:*
      * ``None``
    
    *Keyword Arguments:*
      * ``filepath`` Filepath of export file
    
    *Returns:*
      * ``None``
    
    *Author:*
      * Jon Logsdon, jon.logsdon@volition-inc.com, 3/28/2014 4:04:38 PM
    """
    
    self.check_anim_node( ) 
    bones_array = [ ]
    
    curr_anim_node_namespace = self.anim_node.LongName.split( ":" )
    anim_controller = vmobu.core.get_objects_from_wildcard( curr_anim_node_namespace[ 0 ] + ":*AnimationController", use_namespace=True )
    if filepath:
      self.filepath = filepath
        
    FBSystem( ).Scene.Evaluate( )
    for anim_node_prop in self.anim_node.PropertyList:
      if anim_node_prop.IsUserProperty( ):
        if not anim_node_prop.Name.startswith( "p_" ):
          for bone in self.anim_node.EnumList:
            bones_array.append( bone )
            exported_nodes = bones_array
            exported_nodes.append( anim_controller )
              
    FBMessageBox( "Crunch Status", "Crunching...", "OK" )
    if not file_io.resource_lib.crunch( self.filepath ):
      result = False
      
  def in_depot( self, filepath='', quiet=False ):
    """
    Checks if the export is in the depot.
    
    *Arguments:*
      * ``None`` 
    
    *Keyword Arguments:*
      * ``filepath`` Variable for export filepath
    
    *Returns:*
      * ``None``
    
    *Author:*
      * Jon Logsdon, jon.logsdon@volition-inc.com, 3/28/2014 4:03:18 PM
    """
    
    row = self.anim_list_ui.currentRow( )
    selection_take = self.anim_list_ui.item( row, 0 )    
    if filepath:
      set_export_path = os.path.join( core.const.workspace_dir, str( self.export_dir_ui.text( ) ), str( selection_take.text( ) ) )
      self.filepath = file_io.v_path.Path( set_export_path + ".anim.fbx")
      
    already_there = False
    stats = file_io.perforce.fstat( self.filepath )
    if not stats:
      if not quiet:
        return True
    else:
      if stats[ 0 ].has_key( 'action' ):
        if not stats[ 0 ][ 'action' ] == 'add':
          already_there = True
        elif stats[ 0 ].has_key( 'depotFile' ):
          already_there = True
          
    return already_there
      
  def get_changelist( self, quiet=False ):
    """
    Gets the changelist for the export.
    
    *Arguments:*
      * ``None``
    
    *Keyword Arguments:*
      * ``None`` 
    
    *Returns:*
      * ``None``
    
    *Author:*
      * Jon Logsdon, jon.logsdon@volition-inc.com, 3/28/2014 4:02:59 PM
    """
    
    all_changelists = file_io.perforce.get_client_changelists( )
    exists = False
    for cl in all_changelists:
      if cl[ 'Description' ][ :-1 ] == self.changelist_name:
        return cl
    if not exists:
      return file_io.perforce.create_changelist( self.changelist_name )
      
  def get_changelist_number( self, quiet=False ):
    """
    Gets the changelist number.
    
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
      * Jon Logsdon, jon.logsdon@volition-inc.com, 3/28/2014 4:02:45 PM
    """
    
    return int( self.get_changelist( quiet )[ 'Change' ] ) 
      
  def file_already_checked_out( self, filepath=None, include_self=True ):
    """
    Checks if the file is already checked out.
    
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
      * Jon Logsdon, jon.logsdon@volition-inc.com, 3/28/2014 4:02:26 PM
    """
    
    if filepath:
      self.filepath = file_io.v_path.Path( filepath )
      
    stats = file_io.perforce.fstat( self.filepath )
    if stats:
      if stats[ 0 ].has_key( 'otherOpen' ):
        user = stats[ 0 ][ 'otherOpen' ][ 0 ]
        user = user[ :user.rfind( '@' ) ]
        return user
      if include_self:
        if stats[ 0 ].has_key( 'action' ):
          if stats[ 0 ].has_key( 'actionOwner' ):
            return True
          
    return False
  
  def checkout( self, filepath='', quiet=False, force=False ):
    """
    Checks if the current file is checked out, and if not it checks it out before exporting.
    
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
      * Jon Logsdon, jon.logsdon@volition-inc.com, 3/28/2014 4:01:52 PM
    """
    
    row = self.anim_list_ui.currentRow( )
    selection_take = self.anim_list_ui.item( row, 0 )
    if filepath:
      set_export_path = os.path.join( core.const.workspace_dir, str( self.export_dir_ui.text( ) ), str( selection_take.text( ) ) )
      self.filepath = file_io.v_path.Path( set_export_path + ".anim.fbx")
    else:
      self.filepath = file_io.v_path.Path( FBSystem( ).CurrentDirectory( ) )
    if not self.filepath:
      if not quiet:
        print "No filename. Please 'Save As'."
      else:
        print "No filename. Please 'Save As'."
      return False
    
    already_there = self.in_depot( self.filepath )
    if os.path.exists( self.filepath ):
      if already_there:
        if not self.is_latest( self.filepath ):
          return False
    #else:
    #  self.mark_for_add( self.filepath )
      
    user = self.file_already_checked_out( self.filepath )
    #if type( user ) == str and not user == getpass.getuser( ).lower( ):
    #  if not quiet:
    #    FBMessageBox( "Checked Out!", "{ 0 } checked out by: { 1 }. Quitting.".format( self.filepath, user ), "OK" )
    #  else:
    #    print "{ 0 } checked out by: { 1 }.".format( self.filepath, user )
    #  if not force:
    #    return False
      
    file_io.perforce.edit( self.filepath, self.get_changelist_number( quiet ) )
    return True
  
  def get_latest( self, filepath='' ):
    if filepath:
      self.filepath = file_io.v_path.Path( filepath )
      
    file_io.perforce.sync( [ self.filepath ] )
    if self.is_latest( self.filepath ):
      return True
    else:
      return False
    
  def is_latest( self, filepath='' ):
    if filepath:
      self.filepath = file_io.v_path.Path( filepath )
      
    head_rev = file_io.perforce.fstat( self.filepath, [ 'headRev' ] )
    have_rev = file_io.perforce.fstat( self.filepath, [ 'haveRev' ] )
    if head_rev and have_rev:
      if head_rev[ 0 ] and have_rev[ 0 ]:
        if have_rev[ 0 ][ 'haveRev' ] == head_rev[ 0 ][ 'headRev' ]:
          return True
        
    return False
        
  def setup_resource_lib( self ):
    """
    Sets up the resource lib and checks the valid rig file.
    
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
      * Jon Logsdon, jon.logsdon@volition-inc.com, 3/27/2014 2:24:06 PM
    """
    
    #Get current anim node
    self.check_anim_node( )
    
    try:
      file_io.resource_lib._initialize_resourcelib( )
      print "Resource lib initialized."
    except:
      return False
      
    rig_file = self.anim_node.PropertyList.Find( "p_export_rig" )
    full_rig_path = os.path.join( core.const.workspace_dir, str( rig_file.Data ) )
    if not rig_file:
      print "No rig file set."
      FBMessageBox( "Export Error", "No rig file exists: {0}. Quitting.".format( rig_file.Data ), "OK" )
      return False
    else:
      rig_file_info = None
      try:
        rig_file_info = file_io.resource_lib._resourcelib.get_file_info( os.path.basename( str( rig_file.Data ) ) )
      except RuntimeError:
        FBMessageBox( "Export Error", "Rig filename is not a valid resource: {0}\n Quitting.".format( rig_file.Data ), "OK")
        return False
        
      if rig_file_info:
        rig_filename = rig_file_info.get_local_relative_filename( )
        rig_file.Data = rig_filename
        rig_file = file_io.v_path.Path( full_rig_path ).make_pretty( )
          
        print "Resource lib setup!"
      else:
        FBMessageBox( "Export Error", "No file path exists: {0}. Quitting.".format( str( rig_file.Data ) ) )
        return False
        
  def setup_attributes_for_crunch( self ):
    """
    Sets up the attributes for the rig file before crunch.
    
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
      * Jon Logsdon, jon.logsdon@volition-inc.com, 3/28/2014 4:01:16 PM
    """
    
    #Get current anim node
    self.check_anim_node( )
    
    rig_file = self.anim_node.PropertyList.Find( "p_export_rig" )
    full_rig_path = os.path.join( core.const.workspace_dir, str( rig_file.Data ) )
    if not rig_file:
      print "No rig file set."
      FBMessageBox( "Export Error", "No rig file exists: {0}. Quitting.".format( rig_file.Data ), "OK" )
      return False
    else:
      rig_file_info = None
      try:
        rig_file_info = file_io.resource_lib._resourcelib.get_file_info( os.path.basename( str( rig_file.Data ) ) )
      except RuntimeError:
        FBMessageBox( "Export Error", "Rig filename is not a valid resource: {0}\n Quitting.".format( full_rig_path ), "OK")
        return False
        
      if rig_file_info:
        rig_filename = rig_file_info.get_local_relative_filename( )
        rig_file.Data = rig_filename
        rig_file = file_io.v_path.Path( full_rig_path ).make_pretty( )
          
        print "Resource lib setup!"
      else:
        FBMessageBox( "Export Error", "No file path exists: {0}. Quitting.".format( str( rig_file.Data ) ) )
        return False
      
    for prop in self.anim_node.PropertyList:
      if prop.Name.endswith( 'rig_version' ):
        rig_version = float( prop.Data )
        if not rig_version:
          FBMessageBox( "Rig Error", "No rig version set!", "OK" )
          
        att_dict = { 'associated_character_rig': full_rig_path, 'rig_version': rig_version,
                       'source_asset_file': file_io.resource_lib.get_relative_filename( FBSystem( ).CurrentDirectory( ) ) }
          
        if not file_io.resource_lib.set_attributes( full_rig_path, att_dict ):
          FBMessageBox( "WARNING", "Skipping {0}.".format( str( self.filepath ) ), "OK" )
          return False    
    
  def cell_was_clicked( self ):
    """
    Checks which cell is selected at a given time in the ui.
    
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
      * Jon Logsdon, jon.logsdon@volition-inc.com, 3/26/2014 5:01:59 PM
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
    
    *Examples:* ::
    
      Enter code examples here. (optional field )
    
    *Todo:*
      * Enter thing to do. (optional field )
    
    *Author:*
      * Jon Logsdon, jon.logsdon@volition-inc.com, 3/13/2014 11:08:41 AM
    """
    
    browse_dialog = PySide.QtGui.QFileDialog( self )
    browse_dialog.setFileMode( PySide.QtGui.QFileDialog.Directory )
    browse_dialog.setOption( PySide.QtGui.QFileDialog.ShowDirsOnly )
    browse_dialog.setHistory( os.path.join( core.const.workspace_dir, str( self.export_dir_ui.text( ) ) ) )
    browse_dialog.setFileMode( PySide.QtGui.QFileDialog.ExistingFile )

    export_path = browse_dialog.getExistingDirectory( self, '', os.path.join( core.const.workspace_dir, str( self.export_dir_ui.text( ) ) ) )
    
    if export_path:
      if core.const.workspace_dir.lower( ) in export_path.lower( ):
        export_path = export_path.lower( ).replace( core.const.workspace_dir.lower( ), '' )
        export_path = export_path + "\\"
        self.export_dir_ui.setText( export_path )
        
        if self.export_dir_ui.text( ) != "":
          self.animx_clear_ui.setEnabled( True )
      else:
        FBMessageBox( "File Path Error", "The current export path is not based in your project.", "OK" )
        return     
    
  def browse_rig_export_dirs( self ):
    """
    Browses directories for the rig export.
    
    *Arguments:*
      * ``Argument`` Enter a description for the argument here.
    
    *Keyword Arguments:*
      * ``Argument`` Enter a description for the keyword argument here.
    
    *Returns:*
      * ``Value`` If any, enter a description for the return value here.
    
    *Examples:* ::
    
      Enter code examples here. (optional field )
    
    *Todo:*
      * Enter thing to do. (optional field )
    
    *Author:*
      * Jon Logsdon, jon.logsdon@volition-inc.com, 3/13/2014 11:08:58 AM
    """
    
    browse_dialog = PySide.QtGui.QFileDialog( )
    browse_dialog.setFileMode( PySide.QtGui.QFileDialog.Directory )
    browse_dialog.setOption( PySide.QtGui.QFileDialog.ShowDirsOnly )
    
    export_path = browse_dialog.getExistingDirectory( None, '' )
    if export_path:
      if core.const.workspace_dir.lower( ) in export_path.lower( ):
        export_path = export_path.lower( ).replace( core.const.workspace_dir.lower( ), '' )
        export_path = export_path + "\\"
        self.rigx_file_edit_ui.setText( export_path )
        
        if self.export_dir_ui.text( ) != "":
          self.rigx_clear_ui.setEnabled( True )
          
      else:
        FBMessageBox( "File Path Error", "The current export path is not based in your project.", "OK" )
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
    
    *Examples:* ::
    
      Enter code examples here. (optional field )
    
    *Todo:*
      * Enter thing to do. (optional field )
    
    *Author:*
      * Jon Logsdon, jon.logsdon@volition-inc.com, 3/13/2014 11:09:18 AM
    """
    
    browse_dialog = PySide.QtGui.QFileDialog( self )
    browse_dialog.setFileMode( PySide.QtGui.QFileDialog.Directory )
    browse_dialog.setOption( PySide.QtGui.QFileDialog.ShowDirsOnly )
    browse_dialog.setHistory( os.path.join( core.const.workspace_dir, str( self.batch_dir.text( ) ) ) )
    browse_dialog.setFileMode( PySide.QtGui.QFileDialog.ExistingFile )

    export_path = browse_dialog.getExistingDirectory( self, '', os.path.join( core.const.workspace_dir, str( self.batch_dir.text( ) ) ) )
    
    if export_path:
      if core.const.workspace_dir.lower( ) in export_path.lower( ):
        export_path = export_path.lower( ).replace( core.const.workspace_dir.lower( ), '' )
        export_path = export_path + "\\"
        self.batch_dir.setText( export_path )
        
        if self.batch_dir.text( ) != "":
          self.animx_clear_ui.setEnabled( True )
      else:
        FBMessageBox( "File Path Error", "The current export path is not based in your project.", "OK" )
        return  
    
  def refresh_anim_node( self, auto_fix=False, quiet=False ):
    """
    Refreshes the active anim node.
    
    *Arguments:*
      * ``Argument`` Enter a description for the argument here.
    
    *Keyword Arguments:*
      * ``Argument`` Enter a description for the keyword argument here.
    
    *Returns:*
      * ``Value`` If any, enter a description for the return value here.
    
    *Examples:* ::
    
      Enter code examples here. (optional field )
    
    *Todo:*
      * Enter thing to do. (optional field )
    
    *Author:*
      * Jon Logsdon, jon.logsdon@volition-inc.com, 3/13/2014 11:09:35 AM
    """
    
    #print('--Updated--', STATUS_TIMEOUT )
    
    #Set new project directory path
    self.project_dir = file_io.v_path.Path( core.const.workspace_dir.replace( '\\', '/' )[  :-1  ] ).splitdrive( )[ 
      1  ].replace( '/projects/', '' )    
    
    self.project_line_edit.setText( str( self.project_dir ) )
    
    #Check the type of the anim drop-down
    if type( self.character_combo_ui ) == PySide.QtGui.QComboBox:
      try:
        if self.character_combo_ui.count( ) != len( FBSystem( ).Scene.Notes ):
          for i in range( 0, self.character_combo_ui.count( ) ):
            item_str = str( self.character_combo_ui.itemText( i ) )
            item = vmobu.core.get_object_by_name( item_str, use_namespace=True, models_only=False )
            for note in FBSystem( ).Scene.Notes:
              if note.LongName != item.LongName:
                self.character_combo_ui.addItem( note.LongName )
          
        self.tab_widget.setEnabled( True )
        
        if not self.anim_node:
          self.tab_widget.setEnabled( False )

      except RuntimeError, e:
        #Try to close
        self.close_event( )
    
    self.update_anim_node_p_properties( ) 
    self.update_master_properties( )
    self.update_anim_properties( )

  def update_anim_properties( self ):
    """
    Updates the properties of the currently selected animation in the exporter.
    
    *Arguments:*
      * ``Argument`` Enter a description for the argument here.
    
    *Keyword Arguments:*
      * ``Argument`` Enter a description for the keyword argument here.
    
    *Returns:*
      * ``Value`` If any, enter a description for the return value here.
    
    *Examples:* ::
    
      Enter code examples here. (optional field )
    
    *Todo:*
      * Enter thing to do. (optional field )
    
    *Author:*
      * Jon Logsdon, jon.logsdon@volition-inc.com, 3/13/2014 11:09:53 AM
    """
    
    if self.anim_list_ui.rowCount( ) > 0:
      self.check_anim_node( )    
      row = self.anim_list_ui.currentRow( )
    
      #Check properties of current anim node and remove anim properties and recreate them
      FBSystem( ).Scene.Evaluate( )
      for anim_node_prop in self.anim_node.PropertyList:
        if anim_node_prop.IsUserProperty( ):
          if not anim_node_prop.Name.startswith( "p_" ):
            if not anim_node_prop.Name == "Bones":
              if not anim_node_prop.Name.startswith( "wg" ):
                FBSystem( ).Scene.Evaluate( )
                self.anim_node.PropertyRemove( anim_node_prop )
                self.store_anim_takes( )
      
      indexes = self.anim_list_ui.selectionModel( ).selectedRows( )
      for index in sorted( indexes ):
        item = self.anim_list_ui.itemFromIndex( index )
        if item is None:
          FBMessageBox( "Selection Error", "Please select an animation within the UI.", "OK" )
        else:    
          #Get user start and end frames from ui 
          start_frame_item_ui = self.anim_list_ui.item( row, 1 )
          end_frame_item_ui = self.anim_list_ui.item( row, 2 )
              
          user_start_frame = int( start_frame_item_ui.text( ) )
          user_end_frame = int( end_frame_item_ui.text( ) )
              
          #Set timerange of the current take based off the ui  
          for row in range( self.anim_list_ui.rowCount( ) ):
            curr_anim_name_item_ui = self.anim_list_ui.item( row, 0 )
                
          FBSystem( ).Scene.Evaluate( ) 
    #else:
      #FBMessageBox( "Animation Error", "There are currently no animations.", "OK" )
    
  def update_anim_node_p_properties( self ):
    """
    Updates the p_ properties of the anim node based off the values in the UI.
    
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
      * Jon Logsdon, jon.logsdon@volition-inc.com, 3/18/2014 10:30:02 AM
    """
    
    #Check current anim node and current row and column
    if self.anim_list_ui.rowCount( ) > 0: 
      self.check_anim_node( )
      row = self.anim_list_ui.currentRow( ) 
      
      indexes = self.anim_list_ui.selectionModel( ).selectedRows( )
      for index in sorted( indexes ):
        item = self.anim_list_ui.itemFromIndex( index )
        if item is None:
          FBMessageBox( "Selection Error", "Please select an animation within the UI.", "OK" )
        else:
          #Check all items in current animation row
          curr_anim_name_item_ui = self.anim_list_ui.item( row, 0 )
          curr_start_frame_item_ui = self.anim_list_ui.item( row, 1 )
          curr_end_frame_item_ui = self.anim_list_ui.item( row, 2 )
          curr_ramp_in_item_ui = self.anim_list_ui.item( row, 3 )
          curr_ramp_out_item_ui = self.anim_list_ui.item( row, 4 )
          curr_framerate_item_ui = self.anim_list_ui.item( row, 5 ) 
          
          #Step through properties of the master and update them according to anim node properties
          FBSystem( ).Scene.Evaluate( )
          for prop in self.anim_node.PropertyList:
            if prop.IsUserProperty( ):          
              if prop.Name.endswith( "framestart" ):
                prop.Data = int( curr_start_frame_item_ui.text( ) )
              elif prop.Name.endswith( "frameend" ):
                prop.Data = int( curr_end_frame_item_ui.text( ) )
              elif prop.Name.endswith( "rampin" ):
                prop.Data = int( curr_ramp_in_item_ui.text( ) )
              elif prop.Name.endswith( "rampout" ):
                prop.Data = int( curr_ramp_out_item_ui.text( ) )
              elif prop.Name.endswith( "framerate" ):
                prop.Data = int( curr_framerate_item_ui.text( ) )   
              elif prop.Name.endswith( "export_anim" ):
                prop.Data = str( curr_anim_name_item_ui.text( ) )              
                
      #Set value of p properties in anim node based off values from UI
      for prop in self.anim_node.PropertyList:
        if prop.IsUserProperty( ):
          if prop.Name.endswith( "anim_file" ):
            prop.Data = str( self.export_dir_ui.text( ) )
    #else:
      #FBMessageBox( "Animation Error", "There are currently no animations.", "OK" )
      
  def check_for_anim_node( self ):
    """
    Checks for an anim node in the scene.
    
    *Arguments:*
      * ``Argument`` Enter a description for the argument here.
    
    *Keyword Arguments:*
      * ``Argument`` Enter a description for the keyword argument here.
    
    *Returns:*
      * ``Value`` If any, enter a description for the return value here.
    
    *Examples:* ::
    
      Enter code examples here. (optional field )
    
    *Todo:*
      * Enter thing to do. (optional field )
    
    *Author:*
      * Jon Logsdon, jon.logsdon@volition-inc.com, 3/13/2014 11:10:11 AM
    """
    
    #Check all notes in scene and verify the anim nodes
    for note in FBSystem( ).Scene.Notes:
      if note.Name.endswith( 'anim_node' ):
        print "------------------------------------------"
        print "Anim node " + note.LongName + " found!"
      else:
        FBMessageBox( "WARNING:", "\n" + "There is currently no anim node, or the anim node\n" +  "in your self.scene is incorrectly setup.\n" +  "Please contact a TA to fix this issue.", "OK" )
      
  def store_anim_takes( self, row=None ):
    """
    Stores the current take within the UI to the properties of the anim node.
    
    *Arguments:*
      * ``Argument`` Enter a description for the argument here.
    
    *Keyword Arguments:*
      * ``Argument`` Enter a description for the keyword argument here.
    
    *Returns:*
      * ``Value`` If any, enter a description for the return value here.
    
    *Examples:* ::
    
      Enter code examples here. (optional field )
    
    *Todo:*
      * Enter thing to do. (optional field )
    
    *Author:*
      * Jon Logsdon, jon.logsdon@volition-inc.com, 3/13/2014 11:11:07 AM
    """
    
    #Get current index of the anim node drop-down
    curr_index = self.character_combo_ui.currentIndex( )
    self.character_combo_ui.itemData( curr_index )
    curr_combo_item_string = self.character_combo_ui.currentText( )    
    
    #Get current take
    curr_take = vmobu.core.get_current_take( )
    
    #Get current row and column from ui
    if row is None:
      row = 0
    else:
      row = self.anim_list_ui.currentRow( )
    
    self.remove_anim_node_properties( )
    
    #Check all notes in scene for anim nodes  
    for anim_node in FBSystem( ).Scene.Notes:
      if anim_node.LongName == curr_combo_item_string:
        anim_node_parent = anim_node.Parents.Name
        for row in range( self.anim_list_ui.rowCount( ) ):
          curr_anim_name_item_ui = self.anim_list_ui.item( row, 0 )
            
          #Get all items from the ui
          curr_take_item_ui = "take:" + curr_take.Name
          start_frame_item_ui = self.anim_list_ui.item( row, 1 )
          end_frame_item_ui = self.anim_list_ui.item( row, 2 )
          ramp_in_item_ui = self.anim_list_ui.item( row, 3 )
          ramp_out_item_ui = self.anim_list_ui.item( row, 4 )
          framerate_item_ui = self.anim_list_ui.item( row, 5 )
            
          #Create new animation property in anim node with enum list for values
          self.anim_node_anim_property = anim_node.PropertyCreate( str( curr_anim_name_item_ui.text( ) ), FBPropertyType.kFBPT_enum, "Enum", False, True, None )
               
          #Set values for enum list
          start_frame_text = "startFrame:" + str( start_frame_item_ui.text( ) )
          end_frame_text = "endFrame:" + str( end_frame_item_ui.text( ) )
          ramp_in_text = "rampIn:" + str( ramp_in_item_ui.text( ) )
          ramp_out_text = "rampOut:" + str( ramp_out_item_ui.text( ) )
          framerate_text = "frameRate:" + str( framerate_item_ui.text( ) )
               
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
          
  def remove_anim_node_properties( self ):
    """
    Removes animation properties to reapply them when adding new animations and updating current animations.
    
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
      * Jon Logsdon, jon.logsdon@volition-inc.com, 3/19/2014 3:55:37 PM
    """
    
    #Get current anim node
    self.check_anim_node( )    
    
    #Remove animation properties from anim node for new creation
    for prop in self.anim_node.PropertyList:
      if prop.IsUserProperty( ):
        if not prop.Name.startswith( "p_" ):
          if not prop.Name == "Bones":
            if not prop.Name.startswith( "wg" ):
              self.anim_node.PropertyRemove( prop )
    
  def read_apply_window_attribute_settings( self ):
    """
    Read and applies the settings of your last session of the UI.
    
    *Arguments:*
      * ``Argument`` Enter a description for the argument here.
    
    *Keyword Arguments:*
      * ``Argument`` Enter a description for the keyword argument here.
    
    *Returns:*
      * ``Value`` If any, enter a description for the return value here.
    
    *Examples:* ::
    
      Enter code examples here. (optional field )
    
    *Todo:*
      * Enter thing to do. (optional field )
    
    *Author:*
      * Jon Logsdon, jon.logsdon@volition-inc.com, 3/13/2014 11:11:51 AM
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
    
    *Examples:* ::
    
      Enter code examples here. (optional field )
    
    *Todo:*
      * Enter thing to do. (optional field )
    
    *Author:*
      * Jon Logsdon, jon.logsdon@volition-inc.com, 3/13/2014 11:12:20 AM
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
    
    *Examples:* ::
    
      Enter code examples here. (optional field )
    
    *Todo:*
      * Enter thing to do. (optional field )
    
    *Author:*
      * Jon Logsdon, jon.logsdon@volition-inc.com, 3/13/2014 11:12:37 AM
    """
    
    #Store current text in export path into clipboard
    clipboard = PySide.QtGui.QApplication.clipboard( )
    command = self.export_dir_ui.text( )
    os.system(command )
    
  def paste_anim_export_path( self ):
    """
    Pastes the animation export path from clipboard.
    
    *Arguments:*
      * ``Argument`` Enter a description for the argument here.
    
    *Keyword Arguments:*
      * ``Argument`` Enter a description for the keyword argument here.
    
    *Returns:*
      * ``Value`` If any, enter a description for the return value here.
    
    *Examples:* ::
    
      Enter code examples here. (optional field )
    
    *Todo:*
      * Enter thing to do. (optional field )
    
    *Author:*
      * Jon Logsdon, jon.logsdon@volition-inc.com, 3/13/2014 11:12:53 AM
    """
    
    #Paste text from clipboard into export path
    clipboard = PySide.QtGui.QApplication.clipboard( )
    mime_data = clipboard.mime_data( )
    if mime_data.hasText( ):
      self.export_dir_ui.setText( mime_data.text( ) )
      
  def clear_anim_export_path( self ):
    """
    Clears the animation export path from the UI.
    
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
      * Jon Logsdon, jon.logsdon@volition-inc.com, 3/13/2014 5:22:35 PM
    """
    
    #Clear text in anim export path
    self.export_dir_ui.setText( '' )
    self.animx_clear_ui.setEnabled( False )
  
  def add_bones_list( self ):
    """
    Adds the bones to the bones list in the UI.
    
    *Arguments:*
      * ``Argument`` Enter a description for the argument here.
    
    *Keyword Arguments:*
      * ``Argument`` Enter a description for the keyword argument here.
    
    *Returns:*
      * ``Value`` If any, enter a description for the return value here.
    
    *Examples:* ::
    
      Enter code examples here. (optional field )
    
    *Todo:*
      * Enter thing to do. (optional field )
    
    *Author:*
      * Jon Logsdon, jon.logsdon@volition-inc.com, 3/13/2014 11:13:09 AM
    """
    
    #All nodes components
    all_nodes_components = FBSystem( ).Scene.Components
    bones_array = [  ]
    
    #Get current anim node
    self.check_anim_node( )
    
    #Check the parent (master node) of the anim node and add bones to the array
    for parent in self.anim_node.Parents:
      if not isinstance( parent, FBScene ):
        parent.Selected = True  
        sel_namespace = parent.LongName.split( ":" )
        for namespace in sel_namespace:
          for curr_component in all_nodes_components:
            if curr_component and curr_component.ClassName( ) == "FBModelSkeleton":
              if curr_component not in bones_array:
                bones_array.append( curr_component )
                self.bone_list_ui.addItem( str( curr_component.LongName ) )
        
  def add_tags_list( self ):
    """
    Adds the tags list from your scene within the UI
    
    *Arguments:*
      * ``Argument`` Enter a description for the argument here.
    
    *Keyword Arguments:*
      * ``Argument`` Enter a description for the keyword argument here.
    
    *Returns:*
      * ``Value`` If any, enter a description for the return value here.
    
    *Examples:* ::
    
      Enter code examples here. (optional field )
    
    *Todo:*
      * Enter thing to do. (optional field )
    
    *Author:*
      * Jon Logsdon, jon.logsdon@volition-inc.com, 3/13/2014 11:13:59 AM
    """
    
    #Get current anim node and add tags to ui from scene based on keyword
    self.check_anim_node( )
    for parent in self.anim_node.Parents:
      if not isinstance( parent, FBScene ):
        parent.Selected = True  
        sel_namespace = parent.LongName.split( ":" )
        tag_list = vmobu.core.get_objects_from_wildcard( sel_namespace[ 0 ] + ":*tag_*", use_namespace=True )  
        try:
          for tag in tag_list:
            self.prop_list_ui.addItem( tag.LongName )
        except TypeError:
          print "TAG LIST ERROR! Problem loading tag list."
          
  def add_bone( self ):
    """
    Adds a bone to the bone list based off if selection is a bone.
    
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
      * Jon Logsdon, jon.logsdon@volition-inc.com, 4/2/2014 11:12:27 AM
    """
    
    curr_sel = FBModelList( )
    FBGetSelectedModels( curr_sel )
    for bone in curr_sel:
      if bone and bone.ClassName( ) == "FBModelSkeleton":
        self.bone_list_ui.addItem( str( bone.LongName ) )
        
  def add_tag( self ):
    """
    Adds a tag to the tag list based off of selection.
    
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
      * Jon Logsdon, jon.logsdon@volition-inc.com, 4/2/2014 11:12:27 AM
    """
    
    curr_sel = FBModelList( )
    FBGetSelectedModels( curr_sel )
    for tag in curr_sel:
      if tag and tag.ClassName( ) != "FBModelSkeleton":
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
    
    *Examples:* ::
    
      Enter code examples here. (optional field)
    
    *Todo:*
      * Enter thing to do. (optional field)
    
    *Author:*
      * Jon Logsdon, jon.logsdon@volition-inc.com, 4/2/2014 11:38:02 AM
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
    
    *Examples:* ::
    
      Enter code examples here. (optional field)
    
    *Todo:*
      * Enter thing to do. (optional field)
    
    *Author:*
      * Jon Logsdon, jon.logsdon@volition-inc.com, 4/2/2014 11:38:33 AM
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
    
    *Examples:* ::
    
      Enter code examples here. (optional field)
    
    *Todo:*
      * Enter thing to do. (optional field)
    
    *Author:*
      * Jon Logsdon, jon.logsdon@volition-inc.com, 4/2/2014 2:57:39 PM
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
        new_anim_prop_enum = self.anim_node.PropertyCreate( prop.Name, FBPropertyType.kFBPT_enum, "Enum", False, True, None )
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
        
        for take in FBSystem( ).Scene.Takes:
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
    
    *Examples:* ::
    
      Enter code examples here. (optional field)
    
    *Todo:*
      * Enter thing to do. (optional field)
    
    *Author:*
      * Jon Logsdon, jon.logsdon@volition-inc.com, 4/2/2014 2:57:21 PM
    """
    
    #Check the number of animations in the ui and remove them for ui repopulation
    for row in range( self.anim_list_ui.rowCount( ) ):
      self.anim_list_ui.removeRow( row )
     
    self.repopulate_cells( )
        
  def get_rig_path( self ):
    """
    Grabs the rig path of the current character.
    
    *Arguments:*
      * ``Argument`` Enter a description for the argument here.
    
    *Keyword Arguments:*
      * ``Argument`` Enter a description for the keyword argument here.
    
    *Returns:*
      * ``Value`` If any, enter a description for the return value here.
    
    *Examples:* ::
    
      Enter code examples here. (optional field )
    
    *Todo:*
      * Enter thing to do. (optional field )
    
    *Author:*
      * Jon Logsdon, jon.logsdon@volition-inc.com, 3/13/2014 11:14:33 AM
    """
    
    #Get current anim node and get it's parent (master node)
    self.check_anim_node( )
    for parent in self.anim_node.Parents:
      if not isinstance( parent, FBScene ):
        parent.Selected = True  
        sel_namespace = parent.LongName.split( ":" )
        master = vmobu.core.get_objects_from_wildcard( sel_namespace[ 0 ] + ":*Master", use_namespace=True ) 
        
        #Get export rig path and populate it into the ui
        for prop in master.PropertyList:
          if prop.Name.endswith( "export_rig" ):
            self.rigx_file_edit_ui.setText( prop.Data )
  
  def get_anim_controller( self ):
    """
    Finds the anim controller for the current character.
    
    *Arguments:*
      * ``Argument`` Enter a description for the argument here.
    
    *Keyword Arguments:*
      * ``Argument`` Enter a description for the keyword argument here.
    
    *Returns:*
      * ``Value`` If any, enter a description for the return value here.
    
    *Examples:* ::
    
      Enter code examples here. (optional field )
    
    *Todo:*
      * Enter thing to do. (optional field )
    
    *Author:*
      * Jon Logsdon, jon.logsdon@volition-inc.com, 3/13/2014 11:14:50 AM
    """
    
    #Get current anim node and walk hierarchy to find Animation Controller
    self.check_anim_node( )
    for parent in self.anim_node.Parents:
      if not isinstance( parent, FBScene ):
        parent.Selected = True  
        sel_namespace = parent.LongName.split( ":" )
        anim_controller = vmobu.core.get_objects_from_wildcard( sel_namespace[ 0 ] + ":*AnimationController", use_namespace=True )
      
        self.anim_controller_edit_ui.setText( anim_controller.LongName )
      
  def copy_rig_export_path( self ):
    """
    Copies the export rig path.
    
    *Arguments:*
      * ``Argument`` Enter a description for the argument here.
    
    *Keyword Arguments:*
      * ``Argument`` Enter a description for the keyword argument here.
    
    *Returns:*
      * ``Value`` If any, enter a description for the return value here.
    
    *Examples:* ::
    
      Enter code examples here. (optional field )
    
    *Todo:*
      * Enter thing to do. (optional field )
    
    *Author:*
      * Jon Logsdon, jon.logsdon@volition-inc.com, 3/13/2014 11:15:04 AM
    """
    
    #Copy current text in export path to clipboard
    clipboard = PySide.QtGui.QApplication.clipboard( )
    command = self.rigx_file_edit_ui.text( )
    os.system( command )
    
  def paste_rig_export_path( self ):
    """
    Pastes the export rig path from clipboard.
    
    *Arguments:*
      * ``Argument`` Enter a description for the argument here.
    
    *Keyword Arguments:*
      * ``Argument`` Enter a description for the keyword argument here.
    
    *Returns:*
      * ``Value`` If any, enter a description for the return value here.
    
    *Examples:* ::
    
      Enter code examples here. (optional field )
    
    *Todo:*
      * Enter thing to do. (optional field )
    
    *Author:*
      * Jon Logsdon, jon.logsdon@volition-inc.com, 3/13/2014 11:15:18 AM
    """
    
    #Paste current text from clipboard to rig export path
    clipboard = PySide.QtGui.QApplication.clipboard( )
    mime_data = clipboard.mime_data( )
    if mime_data.hasText( ):
      self.rigx_file_edit_ui.setText( mime_data.text( ) )
      
  def clear_rig_path( self ):
    """
    Clears the export rig path.
    
    *Arguments:*
      * ``Argument`` Enter a description for the argument here.
    
    *Keyword Arguments:*
      * ``Argument`` Enter a description for the keyword argument here.
    
    *Returns:*
      * ``Value`` If any, enter a description for the return value here.
    
    *Examples:* ::
    
      Enter code examples here. (optional field )
    
    *Todo:*
      * Enter thing to do. (optional field )
    
    *Author:*
      * Jon Logsdon, jon.logsdon@volition-inc.com, 3/13/2014 11:15:33 AM
    """
    
    self.rigx_file_edit_ui.setText( '' )
    self.rigx_clear_ui.setEnabled( False )
    
  def add_bone_group_list( self ):
    """
    Adds the bone groups list within the UI.
    
    *Arguments:*
      * ``Argument`` Enter a description for the argument here.
    
    *Keyword Arguments:*
      * ``Argument`` Enter a description for the keyword argument here.
    
    *Returns:*
      * ``Value`` If any, enter a description for the return value here.
    
    *Examples:* ::
    
      Enter code examples here. (optional field )
    
    *Todo:*
      * Enter thing to do. (optional field )
    
    *Author:*
      * Jon Logsdon, jon.logsdon@volition-inc.com, 3/13/2014 11:15:50 AM
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
    
    *Examples:* ::
    
      Enter code examples here. (optional field )
    
    *Todo:*
      * Enter thing to do. (optional field )
    
    *Author:*
      * Jon Logsdon, jon.logsdon@volition-inc.com, 3/13/2014 11:16:38 AM
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
    
    *Author:*
      * Jon Logsdon, jon.logsdon@volition-inc.com, 4/30/2014 11:14:40 AM
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
    
    *Author:*
      * Jon Logsdon, jon.logsdon@volition-inc.com, 4/30/2014 11:14:50 AM
    """
    
    self.collection_name_ui.setText( str( self.collection_combo_ui.currentText( ) ) )
    
  def get_collection_index( self ):
    self.bone_group_table_ui.currentIndex( )
  
  def set_bone_weight_spinbox_to_red( self, rowCol ):
    """
    Sets spin box of weight group to a red border if weight group is keyed.
    
    *Arguments:*
      * ``None`` 
    
    *Keyword Arguments:*
      * ``None``
    
    *Returns:*
      * ``None`` 
    
    *Author:*
      * Jon Logsdon, jon.logsdon@volition-inc.com, 5/27/2014 10:49:17 AM
    """
    
    row = self.bone_group_table_ui.currentRow( )
    col = self.bone_group_table_ui.currentColumn( )
    
    item = self.bone_group_table_ui.item( row, 1 )
    item.setBackground( PySide.QtGui.QColor( 'red' ) )
    
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
    
    *Author:*
      * Jon Logsdon, jon.logsdon@volition-inc.com, 5/14/2014 1:56:31 PM
    """
    
    row = int( rowCol.split( '-' )[ 0 ] )
    col = int( rowCol.split( '-' )[ 1 ] )
    
    val = self.bone_group_table_ui.cellWidget( row, col ).value( )
    group = self.bone_group_table_ui.item( row, 0 ).text( )
    
    #collection_index = self.get_collection_index( self.collection_combo_ui.currentText( ) )
    
    if group == 'anim_controller':
      for prop in self.anim_node.PropertyList:
        if prop.Name.startswith( "wg" ):
          if "anim_controller" in prop.Name:
            prop.Data = val
            
      for comp in FBSystem( ).Scene.Components:
        if comp.ClassName( ) == 'FBModelSkeleton':
          wg_name = comp.PropertyList.Find( "p_bone_weightgroup" )
          if wg_name != None:
            if wg_name.Data == group:
              for prop in comp.PropertyList:
                if prop.Name == "p_bone_weight":
                  prop.Data = val

    else:
      for prop in self.anim_node.PropertyList:
        if prop.Name.startswith( "wg" ):
          if group in prop.Name:
            prop.Data = val
            
      for comp in FBSystem( ).Scene.Components:
        if comp.ClassName( ) == 'FBModelSkeleton':
          wg_name = comp.PropertyList.Find( "p_bone_weightgroup" )
          if wg_name != None:
            if wg_name.Data == group:
              for prop in comp.PropertyList:
                if prop.Name == "p_bone_weight":
                  prop.Data = val
            
    self.bone_group_table_ui.setCurrentCell( row, col )
    
  def get_weight_groups( self ):
    """
    Grabs the weight groups from current character.
    
    *Arguments:*
      * ``Argument`` Enter a description for the argument here.
    
    *Keyword Arguments:*
      * ``Argument`` Enter a description for the keyword argument here.
    
    *Returns:*
      * ``Value`` If any, enter a description for the return value here.
    
    *Examples:* ::
    
      Enter code examples here. (optional field )
    
    *Todo:*
      * Enter thing to do. (optional field )
    
    *Author:*
      * Jon Logsdon, jon.logsdon@volition-inc.com, 3/13/2014 11:16:57 AM
    """
    
    #Get current anim node and parent (master node)
    self.check_anim_node( )
    
    for anim_node_prop in self.anim_node.PropertyList:
      if anim_node_prop.Name.startswith( "wg" ):
        weight_group_property = anim_node_prop.Name.split( ":" )[ 2 ]
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
            #Create a signal and a spin box for the values of the weight groups
            signal_mapper = PySide.QtCore.QSignalMapper( self )
            spin_box = PySide.QtGui.QSpinBox( )
            spin_box.setParent( self.bone_group_table_ui )
            signal_mapper.setMapping( spin_box, str( row ) + '-' + str( 1 ) )
  
            #self.connect( spin_box, PySide.QtCore.SIGNAL( "valueChanged( int )" ), self.update_wg_properties )
            self.connect( spin_box, PySide.QtCore.SIGNAL( "valueChanged( int )" ), signal_mapper,
                          PySide.QtCore.SLOT( "map()" ) )
            
            spin_box.setRange( 0, 100 )
            spin_box.setValue( anim_node_prop.Data )
            
            self.bone_group_table_ui.setCellWidget( row, 1, spin_box )
            signal_mapper.connect( PySide.QtCore.SIGNAL( "mapped(const QString &)" ), self,
                          PySide.QtCore.SLOT( "weight_changed(const QString &)" ) )

    self.set_existing_collections( )
    return True       
  
  def set_existing_collections( self ):
    """
    Sets the collections in the drop-down of the "Animated Weights" tab.
    
    *Arguments:*
      * ``None``
    
    *Keyword Arguments:*
      * ``None``
    
    *Returns:*
      * ``None``
    
    *Author:*
      * Jon Logsdon, jon.logsdon@volition-inc.com, 4/30/2014 11:29:15 AM
    """
    
    for prop in self.anim_node.PropertyList:
      if prop.IsUserProperty( ):
        if prop.Name.startswith( "wg" ):
          collection_namespace = prop.Name.split( ":" )
    self.collection_combo_ui.addItem( collection_namespace[ 1 ] )

  def set_key_to_weight_groups( self ):
    """
    Sets key of the current weight group on the current time.
    
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
      * Jon Logsdon, jon.logsdon@volition-inc.com, 3/26/2014 12:17:50 PM
    """
    
    #Get current anim node
    self.check_anim_node( )    
    
    #Get current row and column in the ui
    row = self.bone_group_table_ui.currentRow( )
    
    curr_frame = FBSystem( ).LocalTime.GetFrame( )
    
    #All nodes components
    all_nodes_components = FBSystem( ).Scene.Components
    bones_array = [ ]
    
    #Check components that are skeleton nodes and set key based on matching selection in ui
    for curr_component in all_nodes_components:
      if curr_component and curr_component.ClassName( ) == "FBModelSkeleton":
        bones_array.append( curr_component )
        for curr_comp_prop in curr_component.PropertyList:
          curr_bone_group = curr_component.PropertyList.Find( "p_bone_weightgroup" )
          if curr_bone_group.Data == self.bone_group_table_ui.item( row, 0 ).text( ):
            if curr_comp_prop.Name.endswith( "bone_weight" ):
              curr_comp_prop.SetAnimated( True )
              curr_comp_animation = curr_comp_prop.GetAnimationNode( )
              fcurve = curr_comp_animation.FCurve
              curr_data = self.bone_group_table_ui.item( row, 1 ).text( )
              fcurve.KeyAdd( FBTime( 0, 0, 0, curr_frame ), curr_comp_prop.Data )
              
    for prop in self.anim_node.PropertyList:
      if prop.Name.startswith( "wg" ):
        weight_group = prop.Name.split( ":" )[ 2 ]
        if weight_group == self.bone_group_table_ui.item( row, 0 ).text( ):
          prop.SetAnimated( True )
          prop_animation = prop.GetAnimationNode( )
          fcurve = prop_animation.FCurve
          fcurve.KeyAdd( FBTime( 0, 0, 0, curr_frame ), prop.Data ) 
    
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
    
    *Examples:* ::
    
      Enter code examples here. (optional field)
    
    *Todo:*
      * Enter thing to do. (optional field)
    
    *Author:*
      * Jon Logsdon, jon.logsdon@volition-inc.com, 3/26/2014 12:17:20 PM
    """
    
    #Get current anim node
    self.check_anim_node( )  
    
    #Get current row and column in the ui
    row = self.bone_group_table_ui.currentRow( ) 
    
    #All nodes components
    all_nodes_components = FBSystem( ).Scene.Components
    bones_array = [ ]
    
    #Check components that are skeleton nodes and delete key based on matching selection in ui
    for curr_component in all_nodes_components:
      if curr_component and curr_component.ClassName( ) == "FBModelSkeleton":
        bones_array.append( curr_component )
        for curr_comp_prop in curr_component.PropertyList:
          curr_bone_group = curr_component.PropertyList.Find( "p_bone_weightgroup" )
          if curr_bone_group.Data == self.bone_group_table_ui.item( row, 0 ).text( ):          
            if curr_comp_prop.Name.endswith( "bone_weight" ):
              curr_comp_prop.SetAnimated( True )
              curr_comp_animation = curr_comp_prop.GetAnimationNode( )
              fcurve = curr_comp_animation.FCurve
              self.remove_key_at_current( curr_comp_animation )
              
  def remove_key_at_current( self, pAnimationNode ):
    """
    Removes key at the current frame.
    
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
      * Jon Logsdon, jon.logsdon@volition-inc.com, 3/26/2014 1:20:07 PM
    """
    
    #All nodes components
    all_nodes_components = FBSystem( ).Scene.Components  
    bones_array = [ ]  
    
    if len( pAnimationNode.Nodes ) == 0:
      pAnimationNode.KeyRemove( )
    else:
      for node in pAnimationNode.Nodes:
        self.remove_key_at_current( node )
        del( node )
    
    for curr_component in all_nodes_components:
      if curr_component and curr_component.ClassName( ) == "FBModelSkeleton":
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
    
    *Examples:* ::
    
      Enter code examples here. (optional field)
    
    *Todo:*
      * Enter thing to do. (optional field)
    
    *Author:*
      * Jon Logsdon, jon.logsdon@volition-inc.com, 3/26/2014 1:32:22 PM
    """
    
    #Get current anim node
    self.check_anim_node( ) 
        
    #Get current row and column in the ui
    row = self.bone_group_table_ui.currentRow( )
        
    #All nodes components
    all_nodes_components = FBSystem( ).Scene.Components
    bones_array = [ ]
        
    #Check components that are skeleton nodes and delete key based on matching selection in ui
    for curr_component in all_nodes_components:
      if curr_component and curr_component.ClassName( ) == "FBModelSkeleton":
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
    
    *Examples:* ::
    
      Enter code examples here. (optional field )
    
    *Todo:*
      * Enter thing to do. (optional field )
    
    *Author:*
      * Jon Logsdon, jon.logsdon@volition-inc.com, 3/13/2014 11:17:15 AM
    """
    
    anim_controller_text = str( self.anim_controller_edit_ui.text( ) )
    anim_controller = vmobu.core.get_object_by_name( anim_controller_text, use_namespace=True, models_only=False )
    anim_controller.Selected = True
      
  def update_timer( self ):
    """
    Timer for auto-update of the anim exporter.
    
    *Arguments:*
      * ``Argument`` Enter a description for the argument here.
    
    *Keyword Arguments:*
      * ``Argument`` Enter a description for the keyword argument here.
    
    *Returns:*
      * ``Value`` If any, enter a description for the return value here.
    
    *Examples:* ::
    
      Enter code examples here. (optional field )
    
    *Todo:*
      * Enter thing to do. (optional field )
    
    *Author:*
      * Jon Logsdon, jon.logsdon@volition-inc.com, 3/13/2014 11:17:50 AM
    """
    
    #Sets a timer for the ui for refreshing
    timer = PySide.QtCore.QTimer( self )
    timer.timeout.connect( self.update_ui )
    
    #Timer timeout set for every 10 seconds
    timer.start( 10000 )
    
  def update_ui( self ):
    """
    Update ui when timer runs out.
    
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
      * Jon Logsdon, jon.logsdon@volition-inc.com, 3/26/2014 2:24:32 PM
    """
    
    self.anim_exporter_widget.update( )
    
  def update_master_properties( self ):
    """
    Updates properties within the master node with the new property values of the anim node.
    
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
      * Jon Logsdon, jon.logsdon@volition-inc.com, 3/17/2014 9:34:18 AM
    """
    
    #Grab current anim node and current row and column of animation cell widgets
    if self.anim_list_ui.rowCount( ) > 0:
      self.check_anim_node( )
      row = self.anim_list_ui.currentRow( )
      
      #Find parent of anim node (master node)
      for parent in self.anim_node.Parents:
        if not isinstance( parent, FBScene ):
          sel_namespace = parent.LongName.split( ":" )
          master = vmobu.core.get_objects_from_wildcard( sel_namespace[ 0 ] + ":*Master", use_namespace=True ) 
          
      indexes = self.anim_list_ui.selectionModel( ).selectedRows( )
      for index in sorted( indexes ):
        item = self.anim_list_ui.itemFromIndex( index )
        if item is None:
          FBMessageBox( "Selection Error", "Please select an animation within the UI.", "OK" )
        else: 
          curr_anim_name_item_ui = self.anim_list_ui.item( row, 0 )
          curr_start_frame_item_ui = self.anim_list_ui.item( row, 1 )
          curr_end_frame_item_ui = self.anim_list_ui.item( row, 2 )
          curr_ramp_in_item_ui = self.anim_list_ui.item( row, 3 )
          curr_ramp_out_item_ui = self.anim_list_ui.item( row, 4 )
          curr_framerate_item_ui = self.anim_list_ui.item( row, 5 ) 
      
          #Step through properties of the master and update them according to anim node properties
          for prop in master.PropertyList:
            if prop.IsUserProperty( ):
              if prop.Name.endswith( "framestart" ):
                prop.Data = int( curr_start_frame_item_ui.text( ) )
              elif prop.Name.endswith( "frameend" ):
                prop.Data = int( curr_end_frame_item_ui.text( ) )
              elif prop.Name.endswith( "rampin" ):
                prop.Data = int( curr_ramp_in_item_ui.text( ) )
              elif prop.Name.endswith( "rampout" ):
                prop.Data = int( curr_ramp_out_item_ui.text( ) )
              elif prop.Name.endswith( "framerate" ):
                prop.Data = int( curr_framerate_item_ui.text( ) )
              elif prop.Name.endswith( "export_anim" ):
                prop_name = self.anim_node.PropertyList.Find( "p_export_anim" )
                prop.Data = prop_name.Data
              elif prop.Name.endswith( "anim_file" ):
                prop_name = self.anim_node.PropertyList.Find( "p_anim_file" )
                prop.Data = prop_name.Data
    #else:
      #FBMessageBox( "Animation Error", "There are currently no animations.", "OK" )
    
  def repopulate_cells( self ):
    """
    Re-populates the UI with animation cells, sourcing from the anim node, based off past animations added.
    
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
      * Jon Logsdon, jon.logsdon@volition-inc.com, 3/17/2014 9:33:32 AM
    """
    
    #Get current anim node
    self.check_anim_node( )
    
    #Refresh scene
    FBSystem( ).Scene.Evaluate( )
    
    for row in range( self.anim_list_ui.rowCount( ) ):
      self.anim_list_ui.removeRow( row )
    
    #load_widget through all properties of the current anim node to read the animation enum properties for repopulating re-opened ui
    try:
      for anim_node_prop in self.anim_node.PropertyList:
        if anim_node_prop.IsUserProperty( ):
          if anim_node_prop.Name == "p_anim_file":
            if anim_node_prop.Data == "none":
              self.export_dir_ui.setText( "" )
            else:
              self.export_dir_ui.setText( str( anim_node_prop.Data ) )
            
          if not anim_node_prop.Name.startswith( "p_" ):
            if not anim_node_prop.Name == "Bones":
              if not anim_node_prop.Name.startswith( "wg" ):
                anim_node_take = anim_node_prop.Name
                  
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
                        
                  self.anim_list_ui.setItem( 0, 0, anim_name_item )
                  self.anim_list_ui.setItem( 0, 1, start_frame_item )
                  self.anim_list_ui.setItem( 0, 2, end_frame_item )
                  self.anim_list_ui.setItem( 0, 3, ramp_in_item )
                  self.anim_list_ui.setItem( 0, 4, ramp_out_item )
                  self.anim_list_ui.setItem( 0, 5, framerate_item )
                  
                  #Repopulate ui with anim node properties    
                  anim_name_item.setText( anim_node_take )
                  start_frame_item.setText( anim_node_start_frame )
                  end_frame_item.setText( anim_node_end_frame )
                  ramp_in_item.setText( anim_node_ramp_in )
                  ramp_out_item.setText( anim_node_ramp_out )
                  framerate_item.setText( anim_node_framerate )
        else:
          pass
    except AttributeError:
      if self.anim_node:
        pass
      #else:
      #  FBMessageBox( "Anim Node Error", "No anim node found.", "OK" )
          
  def delete_animation_cell( self ):
    """
    Deletes animation cells within the UI.
    
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
      * Jon Logsdon, jon.logsdon@volition-inc.com, 3/17/2014 9:32:26 AM
    """
    
    #Get current row and column from ui, as well as current selected animation cell widget
    row = self.anim_list_ui.currentRow( )  
    anim_cell_clicked = self.anim_list_ui.cellClicked.connect( self.cell_was_clicked )
    
    curr_anim_name_item_ui = self.anim_list_ui.item( row, 0 )
    self.check_anim_node( )  
    
    #Delete animation cell widget and refresh ui
    for prop in self.anim_node.PropertyList:
      if prop.Name == str( curr_anim_name_item_ui.text( ) ):
        self.anim_node.PropertyRemove( prop )
        self.anim_list_ui.removeRow( row )
    
    self.refresh_anim_node( )
      
  def copy_anim_list( self ):
    """
    Copies animation list in the ui.
    
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
      * Jon Logsdon, jon.logsdon@volition-inc.com, 3/20/2014 3:13:35 PM
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
    
    *Examples:* ::
    
      Enter code examples here. (optional field)
    
    *Todo:*
      * Enter thing to do. (optional field)
    
    *Author:*
      * Jon Logsdon, jon.logsdon@volition-inc.com, 3/20/2014 5:06:27 PM
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
    
    *Examples:* ::
    
      Enter code examples here. (optional field)
    
    *Todo:*
      * Enter thing to do. (optional field)
    
    *Author:*
      * Jon Logsdon, jon.logsdon@volition-inc.com, 3/20/2014 5:06:27 PM
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
    
    *Author:*
      * Jon Logsdon, jon.logsdon@volition-inc.com, 4/4/2014 3:22:41 PM
    """

    try:
      #Key keyboard binding for the key release
      if event.type( ) == PySide.QtCore.QEvent.KeyRelease and obj is self.anim_exporter_widget:
        key = event.key( )
        #Check that the key release is 'Enter' or 'Return'
        if key == PySide.QtCore.Qt.Key_Return or key == PySide.QtCore.Qt.Key_Enter:
          self.refresh_anim_node( )
          return True
      return PySide.QtGui.QMainWindow.eventFilter( self, obj, event )
        
    except AttributeError:
      FBSystem( ).Scene.Evaluate( )
  
  def select_anim_node( self ):
    """
    Deselects everything in the scene, then selects the anim node.
    
    *Arguments:*
      * ``Argument`` Enter a description for the argument here.
    
    *Keyword Arguments:*
      * ``Argument`` Enter a description for the keyword argument here.
    
    *Returns:*
      * anim_node
    
    *Examples:* ::
    
      Enter code examples here. (optional field)
    
    *Todo:*
      * Enter thing to do. (optional field)
    
    *Author:*
      * Jon Logsdon, jon.logsdon@volition-inc.com, 4/3/2014 12:59:03 PM
    """
    
    self.check_anim_node( )
    
    for comp in FBSystem( ).Scene.Components:
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
    
    *Examples:* ::
    
      Enter code examples here. (optional field)
    
    *Todo:*
      * Enter thing to do. (optional field)
    
    *Author:*
      * Jon Logsdon, jon.logsdon@volition-inc.com, 4/3/2014 1:14:26 PM
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
    
    *Examples:* ::
    
      Enter code examples here. (optional field)
    
    *Todo:*
      * Enter thing to do. (optional field)
    
    *Author:*
      * Jon Logsdon, jon.logsdon@volition-inc.com, 4/7/2014 5:21:02 PM
    """
    
    self.anim_exporter_widget.close( )
    
  def add_application_callbacks( self ):
    """
    Adds callbacks for the FBApplication( ) based off the same structure the xDCC uses.
    
    *Arguments:*
      * ``None``
    
    *Keyword Arguments:*
      * ``None``
    
    *Returns:*
      * ``Mobu callbacks`` 
    
    *Examples:* ::
    
      Enter code examples here. (optional field)
    
    *Todo:*
      * Enter thing to do. (optional field)
    
    *Author:*
      * Jon Logsdon, jon.logsdon@volition-inc.com, 4/14/2014 12:29:49 PM
    """
    
    app_cb_dict = self.cb_mgr._scene_callbacks_ids
    
    #On file new
    self.cb_mgr.add_callback( 'App', FBApplication( ).OnFileNew, self.on_new_before, cb_dict = app_cb_dict )
    
    #On file new completed
    self.cb_mgr.add_callback( 'App', FBApplication( ).OnFileNewCompleted, self.on_new_after, cb_dict = app_cb_dict )
    
    #On file open completed
    self.cb_mgr.add_callback( 'App', FBApplication( ).OnFileOpenCompleted, self.on_new_after, cb_dict = app_cb_dict )
    
    #On file merge
    self.cb_mgr.add_callback( 'App', FBApplication( ).OnFileMerge, self.on_new_after, cb_dict = app_cb_dict )
    
    #When scene is changed
    if not FBApplication( ).OnFileExit:
      self.cb_mgr.add_callback( 'Nodes', FBSystem( ).Scene.OnChange, self.on_node_merged, cb_dict = app_cb_dict )
    
    #On file exit
    self.cb_mgr.add_callback( 'App', FBApplication( ).OnFileExit, self.on_dcc_exit, cb_dict = app_cb_dict )
    
    FBApplication( ).OnFileExit.Add( self.on_dcc_exit )
    
  def on_new_before( self, *args ):
    """
    Removes callbacks for before creating a new file.
    
    *Arguments:*
      * ``*args``
    
    *Keyword Arguments:*
      * ``*args``
    
    *Returns:*
      * ``None``
    
    *Author:*
      * Jon Logsdon, jon.logsdon@volition-inc.com, 4/14/2014 2:19:20 PM
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
    
    *Author:*
      * Jon Logsdon, jon.logsdon@volition-inc.com, 4/14/2014 2:20:16 PM
    """
    
    self.v_cb_mgr.call( self.on_new_after )
    try:
      self.repopulate_cells( )
      self.refresh_anim_node( )
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
    
    *Author:*
      * Jon Logsdon, jon.logsdon@volition-inc.com, 4/14/2014 2:20:20 PM
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
    
    *Author:*
      * Jon Logsdon, jon.logsdon@volition-inc.com, 4/14/2014 2:20:23 PM
    """
    
    self._on_merge = False
    self.v_cb_mgr.call( self.on_merge_after )
    try:
      self.refresh_anim_node( )
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
    
    *Author:*
      * Jon Logsdon, jon.logsdon@volition-inc.com, 4/14/2014 2:20:27 PM
    """
    
    self.cb_mgr.remove_all_callbacks( )
    FBSystem( ).Scene.Evaluate( )
  
  def on_node_merged( self, control, event ):
    """
    Runs callbacks on the instant a merge happens.
    
    *Arguments:*
      * ``control, event``
    
    *Keyword Arguments:*
      * ``None``
    
    *Returns:*
      * ``None``
    
    *Author:*
      * Jon Logsdon, jon.logsdon@volition-inc.com, 4/14/2014 2:20:30 PM
    """
    
    if event.Type == FBSceneChangeType.kFBSceneChangeMergeTransactionBegin:
      self.cb_mgr.remove_all_callbacks( )
      self.v_cb_mgr.call( self.on_new_before )
      
    if event.Type == FBSceneChangeType.kFBSceneChangeMergeTransactionEnd:
      self.v_cb_mgr.call( self.on_new_after )
      try:
        self.refresh_anim_node( )
      except RuntimeError:
        pass
      
  def set_character_source( self ):
    """
    Sets the character's source back to the corresponding HIK rig.
    
    *Arguments:*
      * ``None`` 
    
    *Keyword Arguments:*
      * ``None``
    
    *Returns:*
      * ``None``
    
    *Author:*
      * Jon Logsdon, jon.logsdon@volition-inc.com, 4/30/2014 9:36:28 AM
    """
    
    curr_char = FBApplication( ).CurrentCharacter
    curr_char.ActiveInput = FBCharacterInputType.kFBCharacterInputCharacter
    
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
    
    *Author:*
      * Jon Logsdon, jon.logsdon@volition-inc.com, 3/13/2014 11:18:05 AM
    """
    
    #Set layout of UI
    layout = PySide.QtGui.QVBoxLayout( )
    layout.addWidget( self.anim_exporter_widget )
    self.setLayout( layout ) 
    
    #Set project directory
    self.project_dir = file_io.v_path.Path( core.const.workspace_dir.replace( '\\', '/' )[  :-1  ] ).splitdrive( )[ 
          1  ].replace( '/projects/', '' ) 
    
    self.project_line_edit.setText( str( self.project_dir ) )
    
    #Check for "Notes" in self.scene and apply to characterCombo field
    if len( FBSystem( ).Scene.Notes ) < 1:
      self.check_anim_node( )
      if not self.anim_node:
        self.anim_node = "No anim node"
        self.character_combo_ui.clear( )
        try:
          self.character_combo_ui.currentText( self.anim_node )
        except TypeError:
          FBMessageBox( "Anim Node Error", "No anim node present to populate.\n Killing process.", "OK" )
    else:
      #Search through all notes in the scene for anim node notes and add them in the ui  
      for n in FBSystem( ).Scene.Notes:
        if n.Name.endswith( "anim_node" ):
          self.anim_node = n.LongName
        else:
          self.anim_node = None
        
        #Check if there are notes and add anim nodes to the ui drop-down  
        if n == "":
          self.character_combo_ui.addItem( "No anim node" )
          if not anim_node:
            print "WARNING: No anim node is present."
        else:
          if self.anim_node != None:
            self.character_combo_ui.addItem( self.anim_node )
          
      print "Anim Exporter Loaded!"
      
      self.repopulate_cells( )
      
      self.check_for_anim_node( )
      self.get_anim_controller( )
      self.get_rig_path( )
      self.add_tags_list( )
      self.add_bones_list( )
      self.get_weight_groups( )
      
      self.update_timer( )   
      
  def add_group_in_collection( self ):
    """
    Add a new group in the weight groups list.
    
    *Arguments:*
      * `None``
    
    *Keyword Arguments:*
      * ``None``
    
    *Returns:*
      * ``None`` 
    
    *Author:*
      * Jon Logsdon, jon.logsdon@volition-inc.com, 4/28/2014 2:59:49 PM
    """
    
    new_item = self.groups_list_ui.addItem( 'NEW_GROUP' )
    
  def edit_group_name( self ):
    """
    Edits the name of the current selected group in weight group list.
    
    *Arguments:*
      * ``None`` 
    
    *Keyword Arguments:*
      * ``None``
    
    *Returns:*
      * ``None`` 
    
    *Author:*
      * Jon Logsdon, jon.logsdon@volition-inc.com, 4/28/2014 3:00:46 PM
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
    
    *Author:*
      * Jon Logsdon, jon.logsdon@volition-inc.com, 4/28/2014 3:04:19 PM
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
    
    *Author:*
      * Jon Logsdon, jon.logsdon@volition-inc.com, 4/28/2014 3:05:18 PM
    """
    
    self.groups_list_ui.clear( )
    self.check_anim_node( )
    
    for prop in self.anim_node.PropertyList:
      if prop.Name.startswith( "wg" ):
        weight_group = prop.Name.split( ":" )[ 2 ]
        self.groups_list_ui.addItem( weight_group )
        
        prop_anim = prop.GetAnimationNode( )
        if prop_anim.FCurve.Keys:
          for row in range( self.bone_group_table_ui.rowCount( ) ):
            item = self.bone_group_table_ui.item( row, 0 )
            if weight_group == str( item.text( ) ):
              self.set_bone_weight_spinbox_to_red( row )
            
        
  def get_active_weighted_bones( self ):
    """
    Get the list of assigned weighted bones.
    
    *Arguments:*
      * ``None``
      
    *Keyword Arguments:*
      * ``None``
    
    *Returns:*
      * ``None``
    
    *Author:*
      * Jon Logsdon, jon.logsdon@volition-inc.com, 4/28/2014 3:05:25 PM
    """
    
    self.group_bone_list_ui.clear( )
    #All nodes components
    all_nodes_components = FBSystem( ).Scene.Components
    bones_array = [  ]
    
    #Get current anim node
    self.check_anim_node( )
    
    #Check the parent (master node) of the anim node and add bones to the array
    for parent in self.anim_node.Parents:
      if not isinstance( parent, FBScene ):
        parent.Selected = True  
        sel_namespace = parent.LongName.split( ":" )
        for namespace in sel_namespace:
          for curr_component in all_nodes_components:
            if curr_component and curr_component.ClassName( ) == "FBModelSkeleton":
              for prop in curr_component.PropertyList:
                if prop.Name == 'p_bone_weightgroup':
                  if prop.Data == "default" or prop.Data == "none":
                    pass
                  else:
                    if curr_component not in bones_array:
                      bones_array.append( curr_component )
                      self.group_bone_list_ui.addItem( str( curr_component.LongName ) )
                    
  def get_inactive_weighted_bones( self ):
    """
    Get the list of unassigned weighted bones.
    
    *Arguments:*
      * ``None`` 
    
    *Keyword Arguments:*
      * ``None``
    
    *Returns:*
      * ``None``
    
    *Author:*
      * Jon Logsdon, jon.logsdon@volition-inc.com, 4/28/2014 3:05:31 PM
    """
    
    self.unassigned_list_ui.clear( )
    #All nodes components
    all_nodes_components = FBSystem( ).Scene.Components
    bones_array = [  ]
    
    #Get current anim node
    self.check_anim_node( )
    
    #Check the parent (master node) of the anim node and add bones to the array
    for parent in self.anim_node.Parents:
      if not isinstance( parent, FBScene ):
        parent.Selected = True  
        sel_namespace = parent.LongName.split( ":" )
        for namespace in sel_namespace:
          for curr_component in all_nodes_components:
            if curr_component and curr_component.ClassName( ) == "FBModelSkeleton":
              if curr_component.PropertyList.Find( "p_bone_weightgroup" ) == None or curr_component.PropertyList.Find( "p_bone_weightgroup" ).Data == "default" or curr_component.PropertyList.Find( "p_bone_weightgroup" ).Data == "none":
                if curr_component not in bones_array:
                  bones_array.append( curr_component )
                  self.unassigned_list_ui.addItem( str( curr_component.LongName ) )
                  
  def groups_cell_was_clicked( self ):
    """
    Checks the currently selected group in the collections list.
    
    *Arguments:*
      * ``None``
    
    *Keyword Arguments:*
      * ``None``
    
    *Returns:*
      * ``None`` 
    
    *Author:*
      * Jon Logsdon, jon.logsdon@volition-inc.com, 4/28/2014 3:05:37 PM
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
    
    *Author:*
      * Jon Logsdon, jon.logsdon@volition-inc.com, 4/28/2014 3:05:41 PM
    """
    
    row = self.groups_list_ui.currentRow( )
    curr_item = self.groups_list_ui.item( row )
    self.groups_list_ui.takeItem( row )
    
    for comp in FBSystem( ).Scene.Components:
      if comp.ClassName( ) == 'FBModelSkeleton':
        for prop in comp.PropertyList:
          if prop.Name == 'p_bone_weightgroup':
            if prop.Data == str( curr_item.text( ) ):
              prop.Data = 'none'
              
    self.get_inactive_weighted_bones( )
    self.get_active_weighted_bones( )
    
  def unassign_sel_group( self ):
    """
    Sets the currently selected bone in the collections ui to have an unassigned weight group.
    
    *Arguments:*
      * ``None`` 
    
    *Keyword Arguments:*
      * ``None`` 
    
    *Returns:*
      * ``None`` 
    
    *Author:*
      * Jon Logsdon, jon.logsdon@volition-inc.com, 4/28/2014 5:07:24 PM
    """
    
    selected_items = self.group_bone_list_ui.selectedItems( )
    for sel in selected_items:
      sel.setSelected = True
      row = self.groups_list_ui.currentRow( )
      assigned_item = self.group_bone_list_ui.item( row )
      assigned_item_index = self.group_bone_list_ui.indexFromItem( sel )
      assigned_obj = vmobu.core.get_object_by_name( str( sel.text( ) ), use_namespace=True, models_only=False)
      self.group_bone_list_ui.takeItem( row )
      self.unassigned_list_ui.addItem( str( sel.text( ) ) )
    
      for prop in assigned_obj.PropertyList:
        if prop.Name == 'p_bone_weightgroup':
          try:
            prop.Data = 'default'
          except AttributeError:
            pass
          
    for row in range( self.group_bone_list_ui.count( ) ):
      item = self.group_bone_list_ui.item( row )
      self.group_bone_list_ui.removeItemWidget( item )
      
    for row in range( self.unassigned_list_ui.count( ) ):
      item = self.unassigned_list_ui.item( row )
      self.unassigned_list_ui.removeItemWidget( item )   
      
    self.get_active_weighted_bones( )
    self.get_inactive_weighted_bones( )
          
  def assign_sel_group( self ):
    """
    Sets the currently selected bone in the collections ui to be assigned to the selected weight group.
    
    *Arguments:*
      * ``None`` 
    
    *Keyword Arguments:*
      * ``None`` 
    
    *Returns:*
      * ``None`` 
    
    *Author:*
      * Jon Logsdon, jon.logsdon@volition-inc.com, 4/28/2014 5:07:24 PM
    """ 
    
    selected_items = self.unassigned_list_ui.selectedItems( )
    selected_groups = self.groups_list_ui.selectedItems( )
    for sel in selected_items:
      sel.setSelected = True
      row = self.unassigned_list_ui.currentRow( )
      group_row = self.groups_list_ui.currentRow( )
      unassigned_item = self.unassigned_list_ui.item( row )
      unassigned_obj = vmobu.core.get_object_by_name( str( sel.text( ) ), use_namespace=True, models_only=False )
      self.unassigned_list_ui.takeItem( row )
      self.group_bone_list_ui.addItem( str( sel.text( ) ) )
      
      for prop in unassigned_obj.PropertyList:
        wg_name = unassigned_obj.PropertyList.Find( 'p_bone_weightgroup' )
        if wg_name:
          try:
            for sg in selected_groups:
              wg_name.Data = str( sg.text( ) )
          except AttributeError:
            pass
          
    for row in range( self.group_bone_list_ui.count( ) ):
      item = self.group_bone_list_ui.item( row )
      self.group_bone_list_ui.removeItemWidget( item )
          
    for row in range( self.unassigned_list_ui.count( ) ):
      item = self.unassigned_list_ui.item( row )
      self.unassigned_list_ui.removeItemWidget( item )   
          
    self.get_active_weighted_bones( )
    self.get_inactive_weighted_bones( )    
    
  def cancel_edit_collections( self ):
    """
    Closes the edit collections ui without making any changes in the scene.
    
    *Arguments:*
      * ``None``
    
    *Keyword Arguments:*
      * ``None``
    
    *Returns:*
      * ``None``
    
    *Author:*
      * Jon Logsdon, jon.logsdon@volition-inc.com, 4/30/2014 11:21:12 AM
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
    
    *Author:*
      * Jon Logsdon, jon.logsdon@volition-inc.com, 4/30/2014 11:16:08 AM
    """
    
    self.check_anim_node( )
    self.collection_combo_ui.setEditText( str( self.collection_name_ui.text( ) ) )
    for row in range( self.groups_list_ui.count( ) ):
      item = self.groups_list_ui.item( row )
      item_str = "wg:{0}:{1}".format( str( self.collection_name_ui.text( ) ), str( item.text( ) ) )
      for anim_node_prop in self.anim_node.PropertyList:
        if anim_node_prop.Name.startswith( "wg" ):
          if anim_node_prop.Name == item_str:
            self.anim_node.PropertyRemove( anim_node_prop )
          else:
            anim_node_prop.Data = 0
          
      self.anim_node.PropertyCreate( item_str, FBPropertyType.kFBPT_int, "Int", True, True, None )
      for row in range( self.bone_group_table_ui.rowCount( ) ):
        self.bone_group_table_ui.removeRow( row )
       
    for comp in FBSystem( ).Scene.Components:
        if comp.ClassName( ) == 'FBModelSkeleton':
          wg_name = comp.PropertyList.Find( "p_bone_weightgroup" )
          wg_val = comp.PropertyList.Find( "p_bone_weight" )
          for an_prop in self.anim_node.PropertyList:
            if an_prop.Name.startswith( "wg" ):
              an_wg_name = an_prop.Name.split( ":" )[ 2 ]
              if wg_name:
                if wg_name.Data == an_wg_name:
                  an_prop.Data = int( wg_val.Data )
              #except AttributeError:
              #  pass
        
    self.get_weight_groups( )
    self.edit_dialog_collections_widget.close( )
      
  def update_group_bones( self, item ):
    self.group_bone_list_ui.clear( )
    #All nodes components
    all_nodes_components = FBSystem( ).Scene.Components
    bones_array = [  ]
    
    #Get current anim node
    self.check_anim_node( )
    
    #Check the parent (master node) of the anim node and add bones to the array
    for parent in self.anim_node.Parents:
      if not isinstance( parent, FBScene ):
        parent.Selected = True  
        sel_namespace = parent.LongName.split( ":" )
        for namespace in sel_namespace:
          for curr_component in all_nodes_components:
            if curr_component and curr_component.ClassName( ) == "FBModelSkeleton":
              for prop in curr_component.PropertyList:
                if prop.Name == 'p_bone_weightgroup':
                  if prop.Data != str( item.text( ) ):
                    pass
                  else:
                    if curr_component not in bones_array:
                      bones_array.append( curr_component )
                      self.group_bone_list_ui.addItem( str( curr_component.LongName ) )
          
  def load_collections_widget( self ):
    """
    Loads the edit collections widget.
    
    *Arguments:*
      * ``None``
    
    *Keyword Arguments:*
      * ``None``
    
    *Returns:*
      * ``None``
    
    *Author:*
      * Jon Logsdon, jon.logsdon@volition-inc.com, 4/28/2014 3:05:45 PM
    """
    
    self.get_active_weight_groups( )
    self.get_active_weighted_bones( )
    self.get_inactive_weighted_bones( )
    self.collection_name_edit( )
    
    self.edit_dialog_collections_widget.open( )
    self.edit_dialog_collections_widget.exec_( )
      
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
  
  *Author:*
    * Jon Logsdon, jon.logsdon@volition-inc.com, 4/10/2014 5:20:09 PM
  """
  
  main_tool_name = "Anim Exporter"
  
  FBSystem( ).Scene.Evaluate( )
  
  #Recreate development
  gDEVELOPMENT = True
  
  #Check if we need to recreate the tool
  if gDEVELOPMENT:
    FBDestroyToolByName( main_tool_name )
    FBSystem( ).Scene.Evaluate( )
    
  #Check if the tool is in the Mobu tool list  
  if main_tool_name in FBToolList:
    reload( Anim_Exporter )
    tool = FBToolList[ main_tool_name ]
    ShowTool( tool )
  else:
    tool = Native_Qt_Widget_Tool( main_tool_name )
    FBAddTool( tool )
    if gDEVELOPMENT:
      ShowTool( tool )
      
if not __name__ == '__main__':
  vmobu.core.logger.info( "menu.Anim_Exporter imported" )

  