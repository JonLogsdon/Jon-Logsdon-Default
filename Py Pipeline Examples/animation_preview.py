import wx
import AnimationEditor
import ctg.ae2.ui.const
import ctg.ui.widgets
import cPickle
import pprint
import ctg.ui.panel
import ctg.ui.util
import ctg.prefs
import wx.lib.buttons
import os
import ctg.ae2.ui.dialogs
import GUILib
import ctg
import _resourcelib
import vlib.ui.rb_ui.rb_dialog
import EditorLib


NOT_PLAYING						= 'not_playing'
PLAY_NORMAL_SPEED 			= 'play_normal_speed'
PLAY_HALF_SPEED 				= 'play_half_speed'
PLAY_QUARTER_SPEED 			= 'play_quarter_speed'
PLAY_BACKWARD 					= 'play_backward'
FORWARD 							= 'forward'
BACKWARD 						= 'backward'
HALF_SPEED 						= 'half_speed'
QUARTER_SPEED 					= 'quarter_speed'

ADD_PRESET 						= 'create_new_preset'
DELETE_PRESET 					= 'delete_preset'
GO_TO_FRAME 					= 'go_to_frame'

DEFAULT_RIG 					= 'malea.rig.fbx'
DEFAULT_MESH 					= 'male.mesh.fbx'
DEFAULT_PRESET 				= 'default'


SHOW_LABELS						= 2
SHOW_MIN_MAX_LABEL			= 4
SHOW_SPINNER					= 8
GRADIENT_FILL_HORIZONTAL	= 16


def build_control_dict():

	doc = AnimationEditor.get_active_document()
	if not doc:
		return

	control_dict = {
	   ADD_PRESET		: ctg.ae2.ui.dialogs.Generic_Text_Control( ),
	   DELETE_PRESET	: ctg.ae2.ui.dialogs.Generic_Label_Control( ),
	   GO_TO_FRAME		: ctg.ae2.ui.dialogs.Generic_Spinner( default_value = 0, min_val = 0, max_val = 1000, increment = 1, digits = 0 )
	}

	return control_dict


def build_image_dict( ):

	button_images_dict = {

	   'add_bmp' 									: ctg.ui.util.get_project_image( "anim_editor_plus_22.png", as_bitmap = True ),
	   'add_down_bmp' 							: ctg.ui.util.get_project_image( "anim_editor_plus_down_22.png", as_bitmap = True ),
	   'remove_bmp' 								: ctg.ui.util.get_project_image( "anim_editor_minus_22.png", as_bitmap = True ),
	   'remove_down_bmp' 						: ctg.ui.util.get_project_image( "anim_editor_minus_down_22.png", as_bitmap = True ),
	   'last_frame_bmp' 							: ctg.ui.util.get_project_image( "anim_editor_last_frame_32.png", as_bitmap = True ),
	   'last_frame_down_bmp' 					: ctg.ui.util.get_project_image( "anim_editor_last_frame_down_32.png", as_bitmap = True ),
	   'last_frame_rollover_bmp' 				: ctg.ui.util.get_project_image( "anim_editor_last_frame_rollover_32.png", as_bitmap = True ),
	   'first_frame_bmp' 						: ctg.ui.util.get_project_image( "anim_editor_first_frame_32.png", as_bitmap = True ),
	   'first_frame_down_bmp' 					: ctg.ui.util.get_project_image( "anim_editor_first_frame_down_32.png", as_bitmap = True ),
	   'first_frame_rollover_bmp' 			: ctg.ui.util.get_project_image( "anim_editor_first_frame_rollover_32.png", as_bitmap = True ),
	   'play_bmp' 									: ctg.ui.util.get_project_image( "anim_editor_play_32.png", as_bitmap = True ),
	   'play_down_bmp' 							: ctg.ui.util.get_project_image( "anim_editor_play_down_32.png", as_bitmap = True ),
	   'stop_bmp' 									: ctg.ui.util.get_project_image( "anim_editor_stop_32.png", as_bitmap = True ),
	   'stop_down_bmp' 							: ctg.ui.util.get_project_image( "anim_editor_stop_down_32.png", as_bitmap = True ),
	   'stop_rollover_bmp' 						: ctg.ui.util.get_project_image( "anim_editor_stop_rollover_32.png", as_bitmap = True ),
	   'rewind_bmp' 								: ctg.ui.util.get_project_image( "anim_editor_rewind_32.png", as_bitmap = True ),
	   'rewind_down_bmp' 						: ctg.ui.util.get_project_image( "anim_editor_rewind_down_32.png", as_bitmap = True ),
	   'rewind_rollover_bmp' 					: ctg.ui.util.get_project_image( "anim_editor_rewind_rollover_32.png", as_bitmap = True ),
	   'forward_bmp' 								: ctg.ui.util.get_project_image( "anim_editor_fastforward_32.png", as_bitmap = True ),
	   'forward_down_bmp' 						: ctg.ui.util.get_project_image( "anim_editor_fastforward_down_32.png", as_bitmap = True ),
	   'forward_rollover_bmp' 					: ctg.ui.util.get_project_image( "anim_editor_fastforward_rollover_32.png", as_bitmap = True ),
	   'loop_bmp' 									: ctg.ui.util.get_project_image( "anim_editor_loop_32.png", as_bitmap = True ),
	   'loop_down_bmp' 							: ctg.ui.util.get_project_image( "anim_editor_loop_down_32.png", as_bitmap = True ),
	   'loop_rollover_bmp' 						: ctg.ui.util.get_project_image( "anim_editor_loop_rollover_32.png", as_bitmap = True ),
	   'ac_lock_bmp' 								: ctg.ui.util.get_project_image( "anim_editor_aclock.png", as_bitmap = True ),
	   'ac_lock_down_bmp' 						: ctg.ui.util.get_project_image( "anim_editor_aclock_down.png", as_bitmap = True ),
	   'pause_bmp'    							: ctg.ui.util.get_project_image( "anim_editor_pause_32.png", as_bitmap = True ),
	   'pause_down_bmp'    						: ctg.ui.util.get_project_image( "anim_editor_pause_down_32.png", as_bitmap = True ),
	   'pause_rollover_bmp'    				: ctg.ui.util.get_project_image( "anim_editor_pause_rollover_32.png", as_bitmap = True ),
	   'play_backward_bmp'  					: ctg.ui.util.get_project_image( "anim_editor_play_reverse_32.png", as_bitmap = True ),
	   'play_backward_down_bmp'  				: ctg.ui.util.get_project_image( "anim_editor_play_reverse_down_32.png", as_bitmap = True ),
	   'play_backward_rollover_bmp'  		: ctg.ui.util.get_project_image( "anim_editor_play_reverse_rollover_32.png", as_bitmap = True ),
	   'play_half_speed_bmp'  					: ctg.ui.util.get_project_image( "anim_editor_play_half_32.png", as_bitmap = True ),
	   'play_half_speed_down_bmp'  			: ctg.ui.util.get_project_image( "anim_editor_play_half_down_32.png", as_bitmap = True ),
	   'play_half_speed_rollover_bmp'		: ctg.ui.util.get_project_image( "anim_editor_play_half_rollover_32.png", as_bitmap = True ),
	   'play_quarter_speed_bmp'  				: ctg.ui.util.get_project_image( "anim_editor_play_quarter_32.png", as_bitmap = True ),
	   'play_quarter_speed_down_bmp'  		: ctg.ui.util.get_project_image( "anim_editor_play_quarter_down_32.png", as_bitmap = True ),
	   'play_quarter_speed_rollover_bmp'  	: ctg.ui.util.get_project_image( "anim_editor_play_quarter_rollover_32.png", as_bitmap = True )

	}

	return button_images_dict


class Separator_Control( wx.Panel ):

	def __init__( self, parent, id=-1,size=( 2, 2 ), style=wx.DEFAULT, colour = wx.SystemSettings.GetColour( wx.SYS_COLOUR_LISTBOX ) ):

		wx.Panel.__init__( self, parent, -1, size = size, style= style )
		self.style = style
		self.colour = colour
		self.parent = parent

		self.SetBackgroundColour( colour )

		self.Show( )
		self.Layout( )

	# Methods
	def Refresh( self ):
		self.Refresh( )

	def SetColour( self, colour ):
		self.SetBackgroundColour( colour )

	def SetSize( self, size ):
		self.SetSize( size )

	def GetStyle( self ):
		return self.style

	def GetSize( self ):
		return self.GetSize( )



class Animation_Editor_3d_Viewport( wx.Window ):
	def __init__( self, parent ):
		wx.Window.__init__( self, parent, -1 )

		doc	= AnimationEditor.get_active_document( )

		self.view_manager    = doc.get_view_manager( )

		# default headless mode to false
		headless_mode = False
		self.view_index		= self.view_manager.create_mesh_view( self.GetHandle( ), headless_mode)
		self.preview_mesh		= None
		self.preview_rig		= None
		self.preview_mesh_ptr = None

		self.prop_mesh_names = []
		self.prop_mesh_ptrs = []
		self.prop_rigs = []


		# The light creation makes document changes.  Let's not do that.
		doc.set_document_changes_enabled( False )

		# Create the light and add it to the lists
		self.light1 = self.view_manager.add_light( self.view_index )
		# Set the light's type
		self.light1.params[ "type" ] =  EditorLib.OMNI
		# Set the translation and position
		self.light1.set_translation( ( 1, 4, 1 ) )

		# Create the light and add it to the lists
		self.light2 = self.view_manager.add_light( self.view_index )
		# Set the light's type
		self.light2.params[ "type" ] =  EditorLib.OMNI
		# Set the translation and position
		self.light2.set_translation( ( -1, 4, -1 ) )

		doc.set_document_changes_enabled( True )

		self.Bind( wx.EVT_SIZE, self.on_size )


	def get_preview_mesh_filename( self ):
		return self.preview_mesh


	def get_preview_rig_filename( self ):
		return self.preview_rig


	def get_view_manager( self ):
		self.view_manager

	def get_camera_orbit( self ):
		return self.view_manager.get_camera_orbit( 0 )

	def set_camera_orbit( self, pos ):
		self.view_manager.set_camera_orbit( 0, pos[0], pos[1], pos[2] )

	def get_camera_center( self ):
		return self.view_manager.get_camera_center( 0 )

	def set_camera_center( self, pos ):
		self.view_manager.set_camera_center( 0, ( pos[0], pos[1], pos[2] ) )


	def get_view_index( self ):
		return self.view_index


	def set_bg_color( self, color ):
		doc	= AnimationEditor.get_active_document( )
		if not doc:
			return

		self.view_manager.clear_bg_image( self.view_index )
		self.view_manager.set_bg_color( self.view_index, color )

	def set_bg_image_colors( self, top_color, mid_color, bottom_color, use_mid_color ):
		doc	= AnimationEditor.get_active_document( )
		if not doc:
			return

		self.view_manager.set_bg_image_colors( self.view_index, top_color, mid_color, bottom_color, use_mid_color )


	def set_bg_image( self, image ):
		doc	= AnimationEditor.get_active_document( )
		if not doc:
			return

		self.view_manager.set_bg_image( self.view_index, image )


	def set_grid_visibility( self, state ):
		doc	= AnimationEditor.get_active_document( )
		if not doc:
			return

		self.view_manager.set_grid_visibility( self.view_index, state )


	def set_hdr_enabled( self, state ):
		doc	= AnimationEditor.get_active_document( )
		if not doc:
			return

		self.view_manager.set_hdr_enabled( self.view_index, state )

	def update_lights(self, doc):
		if not doc:
			return
		position = doc.get_character_position()
		self.light1.set_translation( ( 1 + position[0], 4 + position[1], 1 + position[2] ) )
		self.light2.set_translation( ( -1 + position[0], 4 + position[1], -1 + position[2] ) )


	def set_mesh( self, preview_mesh_filename ):
		doc	= AnimationEditor.get_active_document( )
		if not doc:
			return

		if preview_mesh_filename:
			self.preview_mesh = preview_mesh_filename
			if self.preview_mesh_ptr == None:
				self.preview_mesh_ptr = self.view_manager.create_render_mesh(self.view_index, preview_mesh_filename, EditorLib.ASSET_TYPE_ANIMTION)
				doc.set_character_editor_mesh(self.preview_mesh_ptr)

				return
			self.view_manager.set_render_mesh( self.preview_mesh_ptr, preview_mesh_filename, EditorLib.ASSET_TYPE_ANIMTION )

	def set_prop_mesh(self, filename, index):
		doc	= AnimationEditor.get_active_document( )
		if not doc:
			return

		# if this index isn't in the lists lets fill it up with empty entries so we can add to it
		while index >= len(self.prop_mesh_ptrs):
			self.prop_mesh_ptrs.append(None)
			self.prop_mesh_names.append(None)
			self.prop_rigs.append(None)

		if filename == '' and self.prop_mesh_ptrs[index] != None:
			self.view_manager.delete_render_mesh(self.view_index, self.prop_mesh_ptrs[index])
			self.prop_mesh_ptrs[index] = None
			self.prop_mesh_names[index] = ''
			doc.set_character_prop_mesh(self.prop_mesh_ptrs[index], index)
			return

		if filename:
			self.prop_mesh_names[index] = filename
			self.prop_rigs[index] = filename.replace('.mesh.', '.rig.')
			if self.prop_mesh_ptrs[index] == None:
				self.prop_mesh_ptrs[index] = self.view_manager.create_render_mesh(self.view_index, filename, EditorLib.ASSET_TYPE_DEFAULT)
				doc.set_character_prop_mesh(self.prop_mesh_ptrs[index], index)
			else:
				self.view_manager.set_render_mesh( self.prop_mesh_ptrs[index], filename, EditorLib.ASSET_TYPE_DEFAULT )

			doc.set_character_prop_rig(self.prop_rigs[index], index)


	def on_size( self, event ):
		doc	= AnimationEditor.get_active_document( )
		if not doc:
			return

		self.view_manager.resize_mesh_view( self.view_index )
		self.Refresh( )


	def update_view( self ):
		doc	= AnimationEditor.get_active_document( )
		if not doc:
			return

		self.view_manager.update_mesh_view( self.view_index )


	def get_size( self ):
		return self.GetSize( )


	def get_rect( self ):
		return self.GetRect( )



class Animation_3D_View_Panel( ctg.ui.panel.CTG_Panel ):
	def __init__( self, parent ):
		ctg.ui.panel.CTG_Panel.__init__( self, parent, style=wx.BORDER_SUNKEN )


		self.main_sizer = wx.BoxSizer( wx.HORIZONTAL )
		self.SetSizer( self.main_sizer )

		doc = AnimationEditor.get_active_document( )

		#3d preview viewport
		self.preview_viewport = Animation_Editor_3d_Viewport( self )
		background_color = ( 0.03, 0.03, 0.03, 0 )
		# Set the viewport color
		self.preview_viewport.set_bg_color( background_color )

		# Set the colors on the background rectangle (which renders as part of the scene, in front of the viewport color)
		# The parameters are:
		#	  top_color - tuple of 4 floats from (0.0-1.0)
		#	  mid_color - tuple of 4 floats from (0.0-1.0)
		#	  bottom_color - tuple of 4 floats from (0.0-1.0)
		#	  use_float_color - boolean of whether or not to use the middle color specified
		self.preview_viewport.set_bg_image_colors( background_color, background_color, background_color, False )
		self.preview_viewport.set_grid_visibility( True )
		self.preview_viewport.set_hdr_enabled( True )
		setattr( doc, 'preview_3d_viewport', self.preview_viewport )
		self.preview_viewport.SetFocus( )


		self.main_sizer.Add( self.preview_viewport, 1, wx.EXPAND | wx.ALIGN_CENTRE )


	def get_preview_viewport( self ):
		return self.preview_viewport


	def refresh( self ):
		print('refresh')



class Floater_Dialog( vlib.ui.lister_lib.core.Floater_Input_Dialog_Base ):
	def __init__( self, parent, id_string, label_text, mesh_name, rig_name, position, min_value = 0, max_value = 0, initial_frame = 0 ):
		self.label_text 		= label_text
		self.mesh_name			= mesh_name
		self.rig_name 			= rig_name
		self.control 			= build_control_dict()[ id_string ]
		self.id_string 		= id_string
		self.parent 			= parent
		self.min_value 		= min_value
		self.max_value			= max_value
		self.initial_frame   = initial_frame

		vlib.ui.lister_lib.core.Floater_Input_Dialog_Base.__init__( self, parent, position )

		self.disable_editor_window( True )


	def setup_controls( self ):
		doc	= AnimationEditor.get_active_document( )
		if not doc:
			return

		if self.id_string == DELETE_PRESET:
			self.ctrl = self.control.create_control( self, self.label_text )
			self.ctrl.SetLabel( self.label_text )

			label_text = 'Delete Preset: '

		else:
			self.ctrl = self.control.create_control( self )
			label_text = self.label_text

			if self.id_string == GO_TO_FRAME:
				self.ctrl.SetRange( self.min_value, self.max_value )
				self.ctrl.SetValue( self.initial_frame )


		label = wx.StaticText( self, -1, label_text )
		label.SetFont( wx.Font( 8, 70, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, wx.EmptyString ) )
		self.sizer_inner.Add( label, 0, wx.EXPAND | wx.ALL, 4 )

		self.sizer_inner.Add( self.ctrl, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 2 )


		if isinstance( self.ctrl, wx.TextCtrl ):
			self.ctrl.Bind( wx.EVT_TEXT, self.text_changed )


	def on_ok_pressed( self, event ):

		if self.id_string == DELETE_PRESET:
			self.parent.delete_preset( self.label_text )

		elif self.id_string == GO_TO_FRAME:
			self.parent.go_to_frame( int( self.ctrl.GetValue( ) ) )

		else:
			self.parent.add_preset( self.ctrl.GetValue( ) )


		self.disable_editor_window( False )
		self.Show( False )
		self.Destroy( )


	def on_cancel_pressed( self, event ):
		self.disable_editor_window( False )
		self.Show( False )
		self.Destroy( )


	def disable_editor_window( self, value ):
		ctg.ui.util.set_editor_modal( value )


	def text_changed( self, event ):

		preset_name		= self.ctrl.GetValue( )
		bg_color = wx.SystemSettings.GetColour( wx.SYS_COLOUR_LISTBOX )

		if hasattr( self.parent, 'validate_name' ):
			valid = self.parent.validate_name( preset_name )

			if not valid:
				bg_color = wx.Colour( 255, 0, 0 )


		self.ctrl.SetBackgroundColour( bg_color )
		self.ctrl.Refresh( )

		if event:
			event.Skip()


class Animation_Preview( wx.Window ):
	PANE_ID 		= ctg.ae2.ui.const.PANE_ID_PREVIEW_PANE
	PANE_TITLE 	= ctg.ae2.ui.const.PANE_TITLE_PREVIEW_PANE

	def __init__( self, parent, size = (-1, -1 ) ):

		self.menu_win = None
		wx.Window.__init__( self, parent, size=size )

		#toolbar_background_color 	= wx.Colour( 135, 135, 135, 0 ) #wx.Colour( 65, 65, 65, 0 )
		self.background_color 		= wx.Colour( 225, 225, 225, 255 )
		bg_color 						= wx.Colour( 10, 16, 165, 255 )
		#toolbar_background_color 	= wx.Colour( 240, 240, 240, 255 )
		self.selected_bg_colour 	= wx.Colour( 170, 170, 170, 0 )

		self.toolbar_bg_color 		= wx.SystemSettings.GetColour( wx.SYS_COLOUR_LISTBOX )
		self.start_time 				= 0
		self.current_value 			= 0
		doc 								= AnimationEditor.get_active_document( )

		self.setup_default_values( )
		self.prefs 		= self.get_pref( )

		main_sizer 		= wx.BoxSizer( wx.VERTICAL )
		self.top_sizer = wx.BoxSizer( wx.HORIZONTAL )
		self.top_sizerB = wx.BoxSizer( wx.HORIZONTAL )
		bottom_sizer 	= wx.BoxSizer( wx.HORIZONTAL )

		self.top_toolbar 			= wx.Panel(self, -1, size=( -1, 26 ))#, style=wx.BORDER )
		self.top_toolbarB			= wx.Panel(self, -1, size=( -1, 18 ))#, style=wx.BORDER )
		self.bottom_toolbar 		= wx.Panel(self, -1, size=( -1, 37 ))#, style=wx.BORDER )
		bmp = ctg.ui.util.get_project_image( "editCrunchers_16.png", as_bitmap = True )

		self.preset_label 	= wx.StaticText( self.top_toolbar, label="  Presets: " )
		self.mesh_label 		= wx.StaticText( self.top_toolbar, label="Mesh: " )
		self.rig_label 		= wx.StaticText( self.top_toolbar, label="Rig: " )
		self.add_bt 			= wx.lib.buttons.GenBitmapButton( self.top_toolbar, -1, bitmap = build_image_dict()['add_bmp'], style=wx.NO_BORDER, name = 'Add', size=( 22, 22) )
		self.delete_bt 		= wx.lib.buttons.GenBitmapButton( self.top_toolbar, -1, bitmap = build_image_dict()['remove_bmp'], style=wx.NO_BORDER, name = 'Delete', size=( 22, 22) )
		self.mesh_bt 			= wx.lib.buttons.GenBitmapTextButton( self.top_toolbar, -1, bitmap = None, style=wx.BORDER, label= DEFAULT_MESH, size=( 120, 22), name = 'Mesh')
		self.rig_bt 			= wx.lib.buttons.GenBitmapTextButton( self.top_toolbar, -1, bitmap = None, style=wx.BORDER, label= DEFAULT_RIG, size=( -1, 22), name = 'Rig')
		self.ac_locked_bt 	= wx.lib.buttons.GenBitmapToggleButton( self.top_toolbar, -1, bitmap = build_image_dict()['ac_lock_bmp'], size = ( -1, 22), name = 'AC LOCK', style = wx.BORDER )
		self.preset_choice 	= wx.ComboBox( self.top_toolbar, -1, "", choices=[], size=(130,22), style=wx.CB_DROPDOWN | wx.CB_READONLY )

		self.active_set_label		= wx.StaticText( self.top_toolbarB, label = "  Set: " )
		self.active_group_label    = wx.StaticText( self.top_toolbarB, label = "  Group: " )
		self.top_sizerB.AddSpacer( 8 )
		self.top_sizerB.Add( self.active_set_label, 0, wx.ALIGN_RIGHT )
		self.top_sizerB.AddSpacer( 15 )
		self.top_sizerB.Add( self.active_group_label, 0, wx.ALIGN_RIGHT )

		self.add_bt.SetBitmapSelected( build_image_dict()['add_down_bmp'] )
		self.delete_bt.SetBitmapSelected( build_image_dict()['remove_down_bmp'] )
		self.ac_locked_bt.SetBitmapSelected( build_image_dict()['ac_lock_down_bmp'] )

		self.top_sizer.Add( self.preset_label, 0, wx.ALIGN_CENTER )
		self.top_sizer.Add( self.add_bt, 0, wx.ALIGN_CENTRE )
		self.top_sizer.AddSpacer( 3 )
		self.top_sizer.Add( self.delete_bt, 0, wx.ALIGN_CENTRE )
		self.top_sizer.AddSpacer( 3 )
		self.top_sizer.Add( self.preset_choice, 0, wx.ALIGN_CENTRE )
		self.top_sizer.AddSpacer( 10 )
		self.top_sizer.Add( self.mesh_label, 0, wx.ALIGN_CENTER )
		self.top_sizer.Add( self.mesh_bt, 1, wx.ALIGN_CENTRE )
		self.top_sizer.AddSpacer( 5 )
		self.top_sizer.Add( self.rig_label, 0, wx.ALIGN_CENTER  )
		self.top_sizer.Add( self.rig_bt, 1, wx.ALIGN_CENTRE )
		self.top_sizer.AddSpacer( 10 )
		self.top_sizer.Add( self.add_separator( self.top_toolbar ), 0, wx.ALIGN_CENTER )
		self.top_sizer.Add( self.ac_locked_bt, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTRE )

		bt_size = ( 32, 32 )
		self.first_bt 		= wx.lib.buttons.GenBitmapButton( self.bottom_toolbar, -1, bitmap = build_image_dict()['first_frame_bmp'], size = bt_size, name = 'First Frame', style = wx.NO_BORDER )
		self.last_bt 		= wx.lib.buttons.GenBitmapButton( self.bottom_toolbar, -1, bitmap = build_image_dict()['last_frame_bmp'], size = bt_size, name = 'Last Frame', style = wx.NO_BORDER )
		self.play_bt 		= wx.lib.buttons.GenBitmapButton( self.bottom_toolbar, -1, bitmap = self.playing_bmp, size = bt_size, name = 'Play', style = wx.NO_BORDER )
		self.stop_bt 		= wx.lib.buttons.GenBitmapButton( self.bottom_toolbar, -1, bitmap = build_image_dict()['stop_bmp'], size = bt_size, name = 'Stop', style = wx.NO_BORDER )
		self.rewind_bt		= wx.lib.buttons.GenBitmapButton( self.bottom_toolbar, -1, bitmap = build_image_dict()['rewind_bmp'], size = bt_size, name = 'Rewind', style = wx.NO_BORDER )
		self.forward_bt 	= wx.lib.buttons.GenBitmapButton( self.bottom_toolbar, -1, bitmap = build_image_dict()['forward_bmp'], size = bt_size, name = 'Forward', style = wx.NO_BORDER )
		self.loop_bt 		= wx.lib.buttons.GenBitmapToggleButton( self.bottom_toolbar, -1, bitmap = build_image_dict()['loop_bmp'], size = bt_size, name = 'Loop', style = wx.NO_BORDER )
		self.play_back_slider      = wx.Slider( self.bottom_toolbar, size = ( 20, -1 ) )
		self.clip_counter_label 	= wx.StaticText( self.bottom_toolbar, label="0" )
		self.clip_counter_label.SetFont( wx.Font( 11, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.BOLD ) )

		self.rewind_bt.SetBitmapSelected( build_image_dict()['rewind_down_bmp'] )
		self.forward_bt.SetBitmapSelected( build_image_dict()['forward_down_bmp'] )
		self.stop_bt.SetBitmapSelected( build_image_dict()['stop_down_bmp'] )
		self.first_bt.SetBitmapSelected( build_image_dict()['first_frame_down_bmp'] )
		self.last_bt.SetBitmapSelected( build_image_dict()['last_frame_down_bmp'] )
		self.loop_bt.SetBitmapSelected( build_image_dict()['loop_down_bmp'] )
		self.play_bt.SetBitmapSelected( self.playing_down_bmp )

		bottom_sizer.Add( self.first_bt, 0, wx.ALIGN_CENTRE )
		bottom_sizer.Add( self.add_separator( self.bottom_toolbar ), 0, wx.ALIGN_CENTER )
		bottom_sizer.Add( self.play_bt, 0, wx.ALIGN_CENTRE )
		bottom_sizer.Add( self.add_separator( self.bottom_toolbar ), 0, wx.ALIGN_CENTER )
		bottom_sizer.Add( self.stop_bt, 0, wx.ALIGN_CENTRE )
		bottom_sizer.Add( self.add_separator( self.bottom_toolbar ), 0, wx.ALIGN_CENTER )
		bottom_sizer.Add( self.rewind_bt, 0, wx.ALIGN_CENTRE )
		bottom_sizer.Add( self.add_separator( self.bottom_toolbar ), 0, wx.ALIGN_CENTER )
		bottom_sizer.Add( self.forward_bt, 0, wx.ALIGN_CENTRE )
		bottom_sizer.Add( self.add_separator( self.bottom_toolbar ), 0, wx.ALIGN_CENTER )
		bottom_sizer.Add( self.last_bt, 0, wx.ALIGN_CENTRE )
		bottom_sizer.Add( self.add_separator( self.bottom_toolbar ), 0, wx.ALIGN_CENTER )
		bottom_sizer.Add( self.loop_bt, 0 , wx.ALIGN_CENTRE)
		bottom_sizer.Add( self.add_separator( self.bottom_toolbar ), 0, wx.ALIGN_CENTER )
		bottom_sizer.AddSpacer( 5 )
		bottom_sizer.Add( self.play_back_slider, 1, wx.ALIGN_CENTER )
		bottom_sizer.Add( self.clip_counter_label, 0, wx.ALIGN_CENTER  )
		bottom_sizer.AddSpacer( 30 )

		self.top_toolbar.SetSizer( self.top_sizer )
		self.top_toolbarB.SetSizer( self.top_sizerB )
		self.bottom_toolbar.SetSizer( bottom_sizer )

		self.preview_viewport = Animation_3D_View_Panel( self )
		setattr( doc, 'preview_viewport_pane', self.preview_viewport )
		setattr( doc, 'preview_pane', self )

		self.loop_bt.SetToggle( True )
		self.loop_bt.SetBackgroundColour( self.selected_bg_colour )

		self.sub_sizer = wx.BoxSizer( wx.VERTICAL )
		self.sub_sizer.Add( self.preview_viewport, 1, wx.EXPAND | wx.ALIGN_CENTRE, 0 )

		main_sizer.Add( self.top_toolbar, 0, wx.EXPAND | wx.LEFT | wx.RIGHT )
		main_sizer.Add( self.top_toolbarB, 0, wx.EXPAND | wx.LEFT | wx.RIGHT )
		main_sizer.Add( self.sub_sizer, 1, wx.EXPAND | wx.ALIGN_CENTRE, 0 )
		main_sizer.Add( self.bottom_toolbar, 0, wx.EXPAND )

		self.SetSizer( main_sizer )

		self.mesh_bt.Bind( wx.EVT_BUTTON, self.on_mesh_bt_pressed )
		self.rig_bt.Bind( wx.EVT_BUTTON, self.on_rig_bt_pressed )
		self.play_bt.Bind( wx.EVT_BUTTON, self.on_play )
		self.play_bt.Bind( wx.EVT_RIGHT_DOWN, self.on_context_menu )
		self.stop_bt.Bind( wx.EVT_BUTTON, self.on_stop )
		self.first_bt.Bind( wx.EVT_BUTTON, self.on_first_frame )
		self.last_bt.Bind( wx.EVT_BUTTON, self.on_last_frame )
		self.loop_bt.Bind( wx.EVT_BUTTON, self.on_loop_clip )
		self.forward_bt.Bind( wx.EVT_BUTTON, self.on_frame_step_forward )
		self.rewind_bt.Bind( wx.EVT_BUTTON, self.on_frame_step_back )
		self.ac_locked_bt.Bind( wx.EVT_BUTTON, self.on_ac_lock_toggle )
		self.bottom_toolbar.Bind( wx.EVT_SCROLL, self.on_slider)
		self.preset_choice.Bind( wx.EVT_COMBOBOX, self.on_preset_selection  )
		self.clip_counter_label.Bind( wx.EVT_LEFT_DCLICK, self.on_go_to_frame )

		self.add_bt.Bind( wx.EVT_BUTTON, self.on_add_preset )
		self.delete_bt.Bind( wx.EVT_BUTTON, self.on_delete_preset )

		self.refresh_ui( )

		#callbacks
		self.callback_string = 'animation_preview_pane_callbacks'
		self.Show( True )
		self.Layout( )
		#self.Update( )


	def setup_default_values( self ):
		doc	= AnimationEditor.get_active_document( )
		if not doc:
			return

		self.playing 							= PLAY_NORMAL_SPEED
		self.play_direction 					= FORWARD
		self.clip_playing_foward 			= False
		self.clip_playing_backward 		= False
		self.playing_bmp 						= build_image_dict()['play_bmp']
		self.playing_down_bmp 				= build_image_dict()['play_down_bmp']
		self.loop_anim_clip 					= True
		self.finish_playing					= False
		self.pop_up_menu						= None
		self.is_playing_reverse				= False
		self.is_playing_forward    		= False
		self.is_playing_half_speed			= False
		self.is_playing_quarter_speed    = False
		self.network_view_previewing     = False
		self.catalog_view_previewing     = False
		self.camera_orbit_pos = [ ]
		self.camera_center_pos = [ ]
		self.animation_controller_lock( False )
		doc.preview_loop( True )


	def refresh_ui( self ):
		self.update_controls( )


	def get_viewport_rect( self ):
		doc	= AnimationEditor.get_active_document( )
		if not doc:
			return None

		top_offset 		= self.top_toolbar.GetSize()[1]
		bottom_offset 	= self.bottom_toolbar.GetSize()[1] + top_offset

		rect = wx.Rect( 0, 0, 0, 0 )
		screen_rect = doc.get_preview_rect( )
		rect.SetPosition( ( screen_rect[ 0 ], ( screen_rect[ 1 ] + top_offset ) ) )
		rect.SetSize( ( screen_rect[ 2 ] - screen_rect[ 0 ], screen_rect[ 3 ] - ( screen_rect[ 1 ] + bottom_offset ) ) )

		return rect


	def on_ac_lock_toggle( self, event ):
		btn = event.GetEventObject()
		toggle = btn.GetToggle()

		self.animation_controller_lock( toggle )


	def animation_controller_lock( self, value ):
		doc	= AnimationEditor.get_active_document( )
		if not doc:
			return

		doc.set_preview_animation_controller_lock( value )


	def on_slider( self, event ):
		doc	= AnimationEditor.get_active_document( )
		if not doc:
			return

		doc.preview_pause( True )
		self.update_play_button( )
		frame = self.play_back_slider.GetValue( )
		self.reset_playing_direction( )
		doc.set_preview_clip_frame( int( frame ) )
		self.clip_counter_label.SetLabel( str( frame ) )

		if self.loop_anim_clip == False:
			if self.play_direction  == FORWARD:
				if frame  == self.play_back_slider.GetMax():
					if frame > 0:
						self.set_finish_playing( )
			elif self.play_direction  == BACKWARD:
				if ( frame - 1) == 0:
					self.set_finish_playing( )



	def update_slider_and_label( self, doc ):
		if self.preview_viewport:
			try:
				self.preview_viewport.preview_viewport.update_lights(doc)
			except wx._core.PyDeadObjectError:
				pass

		if self.finish_playing:
			return

		frame 		= doc.get_preview_clip_frame()
		clip_len 	= doc.get_preview_clip_frame_count( )


		self.play_back_slider.SetRange( 0, clip_len )

		if doc.get_preview_paused( ) == False:
			self.update_slider_value( frame  )

		if self.loop_anim_clip == False:
			if self.play_direction  == FORWARD:
				if frame  == clip_len:
					if frame > 0:
						self.set_finish_playing( )

			elif self.play_direction  == BACKWARD:
				if ( frame - 1) == 0:
					self.set_finish_playing( )
					self.update_slider_value( 0 )
					doc.set_preview_clip_frame( int( 0 ) )


		doc.preview_loop( self.loop_anim_clip )


	def set_finish_playing( self ):
		doc	= AnimationEditor.get_active_document( )
		if not doc:
			return

		self.finish_playing = True
		doc.preview_pause( True )
		self.update_play_button( )
		self.update_play_flags( False, False, False, False )


	def update_controls( self ):

		doc = AnimationEditor.get_active_document( )

		presets 		= self.get_preset_prefs_dict( )
		presets_list = list( presets.keys( ) )
		mesh = DEFAULT_MESH
		rig  = DEFAULT_RIG

		if DEFAULT_PRESET not in presets_list:
			presets_list.insert( 0, DEFAULT_PRESET )

		else:
			presets_list.insert( 0, presets_list.pop( presets_list.index( DEFAULT_PRESET ) ) )

			mesh = presets.get( DEFAULT_PRESET )[0]
			rig  = presets.get( DEFAULT_PRESET )[1]

		self.preset_choice.SetItems( presets_list )
		self.preset_choice.SetSelection( 0 )

		self.mesh_bt.SetLabel( mesh )
		self.rig_bt.SetLabel( rig )

		self.set_preview_mesh_and_rig( rig, mesh )

		self.update_set_group_label( )


	def update_set_group_label( self ):
		doc	= AnimationEditor.get_active_document( )
		if not doc:
			return

		# set the active set/group
		if doc.active_set:
			self.active_set_label.LabelText = ( r'Set:  ' + doc.active_set )
			doc.set_preview_set( doc.active_set)

		if doc.active_group:
			self.active_group_label.LabelText = ( r'Group:  ' + doc.active_group )
			doc.set_preview_group(doc.active_group)


	def enable_controls( self, value ):
		self.play_back_slider.Enable( value )
		self.clip_counter_label.Enable( value )


	def set_preview_mesh_and_rig( self, rig_name, mesh_name ):

		doc	= AnimationEditor.get_active_document( )
		if not doc:
			return

		rig_resource 	= self.get_resource( rig_name )
		mesh_resource 	= self.get_resource( mesh_name )

		current_preview_rig = doc.get_preview_rig( )
		current_preview_mesh = doc.get_preview_mesh( )

		if mesh_resource:
			if current_preview_mesh != mesh_resource.filename:
				self.preview_viewport.get_preview_viewport().set_mesh( mesh_resource.filename )

		if rig_resource:
			if current_preview_rig != rig_resource.filename:
				doc.set_preview_rig( rig_resource.filename )


	def on_preset_selection( self, event ):

		presets 		= self.get_preset_prefs_dict( )
		preset_name = self.preset_choice.GetStringSelection()
		items 		= self.preset_choice.GetItems()

		if items.index( preset_name ) != 0:
			items.insert( 0, items.pop( items.index( preset_name ) ) )

			self.preset_choice.SetItems( items )
			self.preset_choice.SetSelection( 0 )

		value = presets.get( preset_name )
		if value:
			mesh_name 	= presets.get( preset_name )[0]
			rig_name 	= presets.get( preset_name )[1]
		else:
			mesh_name 	= DEFAULT_MESH
			rig_name  	= DEFAULT_RIG


		self.rig_bt.SetLabel( rig_name )
		self.mesh_bt.SetLabel( mesh_name )
		self.set_preview_mesh_and_rig( rig_name, mesh_name )

		self.on_stop( None )
		self.top_toolbar.Refresh( )



	def on_add_preset( self, event ):

		mesh_name = self.mesh_bt.GetLabel( )
		rig_name = self.rig_bt.GetLabel( )
		position = self.get_position( )

		win = Floater_Dialog( self, ADD_PRESET, 'Create Preset:', mesh_name,
		                      rig_name, position )
		win.Show()


	def on_delete_preset( self, event ):

		mesh_name 	= self.mesh_bt.GetLabel( )
		rig_name 	= self.rig_bt.GetLabel( )
		preset_name = self.preset_choice.GetStringSelection( )
		position 	= self.get_position( )

		win = Floater_Dialog( self, DELETE_PRESET, preset_name, mesh_name,
		                      rig_name, position )
		win.Show()


	def get_resource( self, filename ):

		filename = filename.lower( )

		try:
			resource = _resourcelib.get_file_info( filename )
		except RuntimeError:
			resource = None

		return resource


	def on_go_to_frame( self, event ):

		doc	= AnimationEditor.get_active_document( )
		if not doc:
			return

		doc.preview_pause( True )
		self.update_play_button( )

		m_position 		= wx.GetMouseState( ).GetPosition( )
		position 		= wx.Point( m_position[0] - 80, m_position[1] - 70 )
		max_value 		= self.play_back_slider.GetMax( )
		initial_frame 	= self.play_back_slider.GetValue( )

		win = Floater_Dialog( self, GO_TO_FRAME, 'Go to frame:', '', '',
		                      position, min_value = 0, max_value = max_value,
		                      initial_frame = initial_frame )
		win.Show()


	def go_to_frame( self, frame_num ):
		doc	= AnimationEditor.get_active_document( )
		if not doc:
			return

		self.reset_playing_direction( )
		doc.set_preview_clip_frame( frame_num )
		self.update_slider_value( frame_num  )


	def get_position( self ):

		m_position 	= wx.GetMouseState( ).GetPosition( )
		position 	= wx.Point( m_position[0] + 100, m_position[1] + 80 )

		return position


	def on_play( self, event ):

		doc	= AnimationEditor.get_active_document( )
		if not doc:
			return

		if self.menu_win:
			self.menu_win.close( )

		if self.playing == PLAY_NORMAL_SPEED:
			self.play_normal_speed( )

		elif self.playing == PLAY_QUARTER_SPEED:
			self.play_quarter_speed( )

		elif self.playing == PLAY_HALF_SPEED:
			self.play_half_speed( )

		elif self.playing == PLAY_BACKWARD:
			self.play_backward( )


	def check_callback_registration( self ):

		if not ctg.CALLBACK_SYSTEM.is_callback_registered( self.callback_string ):
			if ctg.CALLBACK_SYSTEM.is_callback_disabled( self.callback_string ):
				ctg.CALLBACK_SYSTEM.enable_callbacks_by_id( self.callback_string )
			else:
				ctg.CALLBACK_SYSTEM.register_callback( self.callback_string, 'ae preview updated', self.update_slider_and_label )


	def on_stop( self, event ):
		doc	= AnimationEditor.get_active_document( )
		if not doc:
			return

		frame = 0
		self.update_play_flags( False, False, False, False )
		doc.preview_stop( )
		self.finish_playing_clip( )
		doc.set_preview_clip_frame( frame )
		self.update_slider_value( frame )
		self.update_play_button( )

		if event:
			if ctg.CALLBACK_SYSTEM.is_callback_registered( self.callback_string ):
				ctg.CALLBACK_SYSTEM.disable_callbacks_by_id( self.callback_string )


	def on_first_frame( self, event ):
		doc	= AnimationEditor.get_active_document( )
		if not doc:
			return

		doc.set_preview_clip_frame( self.play_back_slider.GetMin( ) )
		self.update_slider_value( self.play_back_slider.GetMin( ) )


	def on_last_frame( self, event ):
		doc	= AnimationEditor.get_active_document( )
		if not doc:
			return

		doc.set_preview_clip_frame( self.play_back_slider.GetMax( ) )
		self.update_slider_value( self.play_back_slider.GetMax( ) )


	def on_play_backward( self, event ):
		self.play_backward( )


	def set_clip_frame_and_update_slider( self, frame ):
		doc	= AnimationEditor.get_active_document( )
		if not doc:
			return

		self.update_slider_value( frame )
		doc.set_preview_clip_frame( int( frame ) )


	def play_backward( self ):
		doc	= AnimationEditor.get_active_document( )
		if not doc:
			return

		doc.set_preview_playback_speed( 1.0 )
		self.play_direction 	= BACKWARD
		self.playing 			= PLAY_BACKWARD

		if self.is_playing_reverse == True:
			self.pause_on_off( )
		else:
			self.on_stop( None )
			doc.preview_reverse( )
			self.update_play_flags( False, True, False, False )

		self.update_play_bmp( build_image_dict()['play_backward_bmp'],
		                      build_image_dict()['play_backward_down_bmp'] )

		self.check_callback_registration( )


	def finish_playing_clip( self ):
		doc	= AnimationEditor.get_active_document( )
		if not doc:
			return

		if self.finish_playing == True:
			doc.preview_loop( self.loop_anim_clip )
			self.finish_playing = False


	def play_normal_speed( self ):
		doc	= AnimationEditor.get_active_document( )
		if not doc:
			return

		doc.set_preview_playback_speed( 1.0 )
		self.play_direction 	= FORWARD
		self.playing 			= PLAY_NORMAL_SPEED

		if self.is_playing_forward == True:
			self.pause_on_off( )
		else:
			self.on_stop( None )
			doc.preview_play( )
			self.update_play_flags( True, False, False, False )

		self.update_play_bmp( build_image_dict()['play_bmp'],
		                      build_image_dict()['play_down_bmp'] )

		self.check_callback_registration( )

	def play_half_speed( self ):
		doc	= AnimationEditor.get_active_document( )
		if not doc:
			return

		doc.set_preview_playback_speed( 0.5 )
		self.play_half_speed_based_on_direction( )

		self.playing = PLAY_HALF_SPEED
		self.update_play_bmp(  build_image_dict()['play_half_speed_bmp'],
		                       build_image_dict()['play_half_speed_down_bmp'] )

		self.check_callback_registration( )


	def play_quarter_speed( self ):
		doc	= AnimationEditor.get_active_document( )
		if not doc:
			return

		doc.set_preview_playback_speed( 0.25 )
		self.play_quarter_speed_based_on_direction( )

		self.playing = PLAY_QUARTER_SPEED
		self.update_play_bmp( build_image_dict()['play_quarter_speed_bmp'],
		                      build_image_dict()['play_quarter_speed_down_bmp'] )

		self.check_callback_registration( )


	def play_half_speed_based_on_direction( self ):

		if self.is_playing_half_speed == True:
			self.pause_on_off( )
		else:
			self.on_stop( None )
			self.play_based_on_direction( )
			self.update_play_flags( False, False, True, False )


	def play_quarter_speed_based_on_direction( self ):

		if self.is_playing_quarter_speed == True:
			self.pause_on_off( )
		else:
			self.on_stop( None )
			self.play_based_on_direction( )
			self.update_play_flags( False, False, False, True )


	def pause_on_off( self ):
		doc	= AnimationEditor.get_active_document( )
		if not doc:
			return

		paused = doc.get_preview_paused( )
		if paused == True:
			doc.preview_pause( False )
			doc.preview_loop( self.loop_anim_clip )
		else:
			doc.preview_pause( True )


	def play_based_on_direction( self ):
		doc	= AnimationEditor.get_active_document( )
		if not doc:
			return

		if self.play_direction == FORWARD:
			doc.preview_play( )
		elif self.play_direction == BACKWARD:
			doc.preview_reverse( )


	def update_play_flags( self, forward, reverse, half_speed, quarter_speed ):
		self.is_playing_forward 			= forward
		self.is_playing_reverse 			= reverse
		self.is_playing_half_speed 		= half_speed
		self.is_playing_quarter_speed 	= quarter_speed


	def update_play_bmp( self, up_bmp, down_bmp ):
		self.playing_bmp = up_bmp
		self.playing_down_bmp = down_bmp
		self.update_play_button( )


	def update_slider_value( self, frame ):
		self.play_back_slider.SetValue( float( frame ) )
		self.clip_counter_label.SetLabel( str( frame ) )


	def update_play_button( self ):
		doc	= AnimationEditor.get_active_document( )
		if not doc:
			return

		if doc.get_preview_paused( ):
			self.play_bt.SetBitmapLabel( self.playing_bmp )
			self.play_bt.SetBitmapSelected( self.playing_down_bmp )
		else:
			self.play_bt.SetBitmapLabel( build_image_dict()['pause_bmp'] )
			self.play_bt.SetBitmapSelected( build_image_dict()['pause_down_bmp'] )

		self.bottom_toolbar.Refresh( )


	def on_frame_step_forward( self, event ):
		doc	= AnimationEditor.get_active_document( )
		if not doc:
			return

		selected_view_layout = self.get_active_view( )

		doc.preview_pause( True )
		slider_value 		= self.play_back_slider.GetValue( )
		slider_max_value 	= self.play_back_slider.GetMax( )

		if self.play_direction == BACKWARD:
			self.reset_playing_direction( )

		if selected_view_layout == ctg.ae2.ui.const.NETWORK_VIEW_LAYOUT:
			doc.preview_step_forward( )
		else:
			if slider_value < slider_max_value:
				frame 	= slider_value + 1
				self.update_slider_value( frame )
			else:
				frame 	= doc.get_preview_clip_frame( )

			doc.set_preview_clip_frame( int( frame ) )

		self.update_play_button( )
		self.finish_playing = False


	def on_frame_step_back( self, event ):
		doc	= AnimationEditor.get_active_document( )
		if not doc:
			return

		doc.preview_pause( True )
		slider_value = self.play_back_slider.GetValue( )
		selected_view_layout = self.get_active_view( )

		if self.play_direction == FORWARD:
			self.reset_playing_direction( )

		if selected_view_layout == ctg.ae2.ui.const.NETWORK_VIEW_LAYOUT:
			doc.preview_step_backward( )
		else:
			if slider_value > 0:
				frame = slider_value - 1
				self.update_slider_value( frame )
				doc.set_preview_clip_frame( int( frame ) )

		self.update_play_button( )
		self.finish_playing = False

	def get_active_view( self ):
		return ctg.prefs.user.setdefault( "global.animation_editor.selected_view_layout", ctg.ae2.ui.const.NETWORK_VIEW_LAYOUT )


	def get_recent_selected_clips( self ):
		doc	= AnimationEditor.get_active_document( )
		if not doc:
			return

		sel_clip_objs = doc.selection_manager.get_recent_sel_clips( )

		return sel_clip_objs


	def on_loop_clip( self, event ):

		loop_btn 				= event.GetEventObject( )
		self.update_loop_state( loop_btn.GetToggle( ) )
		self.update_play_button( )


	def update_loop_state( self, value ):
		doc	= AnimationEditor.get_active_document( )
		if not doc:
			return

		self.loop_anim_clip 	= value

		doc.preview_loop( self.loop_anim_clip )
		self.finish_playing = False


	def layout_view_changed( self ):
		if self.is_clip_playing( ):
			self.on_stop( None )


	def is_clip_playing( self ):
		doc	= AnimationEditor.get_active_document( )
		if not doc:
			return False

		if self.is_playing_forward or \
		   self.is_playing_half_speed or \
		   self.is_playing_quarter_speed or \
		   self.is_playing_reverse:
			#doc.get_preview_paused( ) or \

			return True

		else:
			return False


	def reset_playing_clip( self ):
		self.on_stop( None )
		self.on_play( None )


	def reset_playing_direction( self ):

		if self.finish_playing == True:
			if self.playing == PLAY_NORMAL_SPEED:
				self.is_playing_forward = True

			elif self.playing == PLAY_HALF_SPEED:
				self.is_playing_half_speed = True

			elif self.playing == PLAY_QUARTER_SPEED:
				self.is_playing_quarter_speed = True

			elif self.playing == PLAY_BACKWARD:
				self.is_playing_reverse = True

			self.finish_playing = False


	def add_preset( self, preset_name ):

		valid = self.validate_name( preset_name )
		if valid:
			self.save_preset( preset_name, self.mesh_bt.GetLabel( ), self.rig_bt.GetLabel( ) )

		else:
			dlg = wx.MessageDialog( self, 'Preset name "{0}" exist.'.format( preset_name ),
			                        'Preset', wx.OK | wx.ICON_INFORMATION )
			dlg.ShowModal()
			dlg.Destroy()


	def save_preset( self, preset_name, mesh_filename, rig_filename ):

		presets = self.get_preset_prefs_dict( )
		presets[ preset_name ] = [ str( mesh_filename ), str( rig_filename ) ]

		items = self.preset_choice.GetItems()
		if preset_name not in items:
			items.insert( 0, preset_name )
		else:
			items.insert( 0, items.pop( items.index( preset_name ) ) )

		self.preset_choice.SetItems( items )
		self.preset_choice.SetSelection( 0 )

		self.save_preset_prefs( presets )


	def delete_preset( self, preset_name ):
		presets 			= self.get_preset_prefs_dict( )
		preset_name 	= self.preset_choice.GetStringSelection()

		if preset_name.lower() == DEFAULT_PRESET.lower():
			dlg = wx.MessageDialog( self, '"Default" preset cannot be deleted.',
			                        'Deleting Preset.', wx.OK | wx.ICON_INFORMATION )
			dlg.ShowModal()
			dlg.Destroy()

		else:
			dlg = wx.MessageDialog( self, 'Are you sure you want to delete "{0}" preset?'.format( preset_name ),
			                        'Deleting Preset.', wx.OK | wx.CANCEL | wx.ICON_INFORMATION )

			if dlg.ShowModal() == wx.ID_OK:
				if preset_name in presets.keys():
					presets.pop( preset_name )
					self.save_preset_prefs( presets )

					items = self.preset_choice.GetItems( )
					if preset_name in items:
						items.pop( items.index( preset_name ) )

						self.preset_choice.SetItems( items )
						self.preset_choice.SetStringSelection( DEFAULT_PRESET )

						self.rig_bt.SetLabel( DEFAULT_RIG )
						self.mesh_bt.SetLabel( DEFAULT_MESH )
						self.set_preview_mesh_and_rig( DEFAULT_RIG , DEFAULT_MESH )

						self.top_toolbar.Refresh( )

			dlg.Destroy( )


	def check_name_existance( self, name ):
		if name in list( self.get_preset_prefs_dict( ).keys() ):
			return True

		return False


	def validate_name_pattern( self, name, pattern = set('$,;:/":.\`|@%&^*#)(!+-~=?><][}{') ):
		s_char = "'"

		if any((char in pattern) for char in name) or s_char in name:
			return False
		else:
			return True


	def validate_name( self, name ):
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


	def setup_preset_prefs( self ):
		preset_prefs_string = self.prefs.setdefault( 'global.animation_editor.anim_presets', '' ).replace( '$NL$', '\n' )

		return preset_prefs_string


	def get_preset_prefs_dict( self ):
		preset_prefs_string = self.setup_preset_prefs( )
		preset_prefs_dict = { }
		try:
			preset_prefs_dict = cPickle.loads( preset_prefs_string )
		except EOFError:
			pass

		return preset_prefs_dict


	def save_preset_prefs( self, preset_dict ):
		preset_prefs_string = cPickle.dumps( preset_dict ).replace( '\n', '$NL$' )
		self.prefs['global.animation_editor.anim_presets'] = preset_prefs_string


	def get_pref( self ):
		return ctg.prefs.user


	def on_mesh_bt_pressed( self, event ):
		#stop animation
		self.on_stop( event )

		resource = None
		dlg = vlib.ui.rb_ui.rb_dialog.RB_Dialog( None, [ 'gml_mesh' ], multi_select = False )
		if ctg.ui.dialogs.show_dialog_modal( dlg ) == wx.ID_OK:
			resource = dlg.get_selected_file_info_object( )

		if isinstance( resource, _resourcelib.file_info ):
			self.set_preview_mesh_update_toolbar( resource.filename )

			#save selected preset
			self.save_preset( self.preset_choice.GetStringSelection( ), self.mesh_bt.GetLabel( ), self.rig_bt.GetLabel( ) )


	def on_rig_bt_pressed( self, event ):
		#stop animation
		self.on_stop( event )

		resource = None
		dlg = vlib.ui.rb_ui.rb_dialog.RB_Dialog( None, [ 'fbx_rig' ], multi_select = False  )
		if ctg.ui.dialogs.show_dialog_modal( dlg ) == wx.ID_OK:
			resource = dlg.get_selected_file_info_object( )

		if isinstance( resource, _resourcelib.file_info ):
			self.set_preview_rig_update_toolbar( resource.filename )

			#save selected preset
			self.save_preset( self.preset_choice.GetStringSelection( ), self.mesh_bt.GetLabel( ), self.rig_bt.GetLabel( ) )


	def set_preview_mesh_update_toolbar( self, mesh_filename ):

		doc	= AnimationEditor.get_active_document( )
		if not doc:
			return


		if mesh_filename:
			self.mesh_bt.SetLabel( mesh_filename )
			doc.set_preview_mesh( mesh_filename )
			self.preview_viewport.get_preview_viewport().set_mesh( mesh_filename )

			self.top_toolbar.Refresh( )


	def set_preview_rig_update_toolbar( self, rig_file_name ):

		doc	= AnimationEditor.get_active_document( )
		if not doc:
			return


		if rig_file_name:
			self.rig_bt.SetLabel( rig_file_name )
			doc.set_preview_rig( rig_file_name )

			if hasattr( doc, 'rig_bones_pane'):
				doc.rig_bones_pane.refresh_ui( )

			self.top_toolbar.Refresh( )


	def update_preview_mesh_rig( self, mesh_filename, rig_filename ):
		doc	= AnimationEditor.get_active_document( )
		if not doc:
			return

		if self.is_clip_playing( ):
			self.on_stop( None )

		self.set_preview_mesh_update_toolbar( mesh_filename )
		self.set_preview_rig_update_toolbar( rig_filename )

		#save default preset
		self.save_preset( 'default', self.mesh_bt.GetLabel( ), self.rig_bt.GetLabel( ) )

	def update_preview_props_and_tags(self, prop, prop_tag, character_tag, index):
		doc	= AnimationEditor.get_active_document( )
		if not doc:
			return

		self.preview_viewport.get_preview_viewport().set_prop_mesh( prop, index )
		doc.set_character_attach_tag(character_tag, index)
		doc.set_character_prop_attach_tag(prop_tag, index)


	def on_context_menu( self, event ):

		if not self.menu_win:

			self.menu_win = Context_Menu( self )

			#Show the menu right below or above the button
			btn = event.GetEventObject()
			pos = btn.ClientToScreen( (0,0) )
			size  =  btn.GetSize()
			self.menu_win.Position(pos, (0, size[1]))

			self.menu_win.Show( True )
			self.menu_win.SetFocus( )

		else:
			self.menu_win.close( )


	def add_separator( self, parent ):
		separator = Separator_Control( parent, -1, size=( 1, 24 ),
		                               colour=wx.Colour( 170, 170, 170, 0 ) )

		return separator


	def get_playing_type( self ):
		return self.playing



class Context_Menu( wx.PopupTransientWindow ):
	def __init__( self, parent ):
		wx.PopupTransientWindow.__init__( self, parent, wx.SIMPLE_BORDER )

		self.parent 	= parent
		self.selected_bg_colour  		= wx.SystemSettings.GetColour( wx.SYS_COLOUR_GRADIENTINACTIVECAPTION )
		#self.selected_bg_colour 	= wx.Colour( 180, 180, 180, 0 )
		bt_size 			= ( 30, 30 )

		self.play_quarter_speed_bt 	= wx.lib.buttons.GenBitmapToggleButton( self, -1, bitmap = build_image_dict()['play_quarter_speed_bmp'], size = bt_size, name = 'Play Quarter Speed', style = wx.NO_BORDER)
		self.play_half_speed_bt 		= wx.lib.buttons.GenBitmapToggleButton( self, -1, bitmap = build_image_dict()['play_half_speed_bmp'], size = bt_size, name = 'Play Half Speed', style = wx.NO_BORDER)
		self.play_normal_speed_bt 		= wx.lib.buttons.GenBitmapToggleButton( self, -1, bitmap = build_image_dict()['play_bmp'], size = bt_size, name = 'Play Normal Speed', style = wx.NO_BORDER )
		self.play_backward_bt 			= wx.lib.buttons.GenBitmapToggleButton( self, -1, bitmap = build_image_dict()['play_backward_bmp'], size = bt_size, name = 'Play Rervese', style = wx.NO_BORDER)

		self.play_normal_speed_bt.SetBitmapSelected( build_image_dict()['play_down_bmp'] )
		self.play_backward_bt.SetBitmapSelected( build_image_dict()['play_backward_down_bmp'] )
		self.play_quarter_speed_bt.SetBitmapSelected( build_image_dict()['play_quarter_speed_down_bmp'] )
		self.play_half_speed_bt.SetBitmapSelected( build_image_dict()['play_half_speed_down_bmp'] )

		self.main_sizer = wx.BoxSizer( wx.VERTICAL )

		self.main_sizer.AddSpacer( 2 )
		self.main_sizer.Add( self.play_normal_speed_bt, 0, wx.ALIGN_CENTRE )
		self.main_sizer.Add( self.add_separator( self ), 0, wx.ALIGN_CENTER )
		self.main_sizer.Add( self.play_quarter_speed_bt,0, wx.ALIGN_CENTRE )
		self.main_sizer.Add( self.add_separator( self ), 0, wx.ALIGN_CENTER )
		self.main_sizer.Add( self.play_half_speed_bt,0, wx.ALIGN_CENTRE )
		self.main_sizer.Add( self.add_separator( self ), 0, wx.ALIGN_CENTER )
		self.main_sizer.Add( self.play_backward_bt, 0, wx.ALIGN_CENTRE )


		self.play_quarter_speed_bt.Bind( wx.EVT_BUTTON, self.on_play_quarter_speed )
		self.play_half_speed_bt.Bind( wx.EVT_BUTTON, self.on_play_half_speed )
		self.play_backward_bt.Bind( wx.EVT_BUTTON, self.on_play_backward )
		self.play_normal_speed_bt.Bind( wx.EVT_BUTTON, self.on_play_normal_speed )
		self.play_normal_speed_bt.Bind( wx.EVT_RIGHT_DOWN, self.on_right_down )
		self.play_backward_bt.Bind( wx.EVT_RIGHT_DOWN, self.on_right_down )
		self.play_half_speed_bt.Bind( wx.EVT_RIGHT_DOWN, self.on_right_down )
		self.play_quarter_speed_bt.Bind( wx.EVT_RIGHT_DOWN, self.on_right_down )


		self.SetSize( ( 35, 128 ) )
		self.SetSizer( self.main_sizer )
		self.Layout( )

		self.set_button_down( )


	def on_right_down( self, event ):
		self.close( )


	def on_play_backward( self, event ):
		self.parent.play_backward( )
		self.close( )


	def on_play_half_speed( self, event ):
		self.parent.play_half_speed( )
		self.close( )


	def on_play_quarter_speed( self, event ):
		self.parent.play_quarter_speed( )
		self.close( )


	def on_play_normal_speed( self, event ):
		self.parent.play_normal_speed( )
		self.close( )


	def close( self ):
		self.parent.menu_win = None
		self.Show( False )
		self.Destroy( )


	def set_button_down( self ):
		play_type = self.parent.get_playing_type( )

		if play_type == PLAY_NORMAL_SPEED:
			self.play_normal_speed_bt.SetToggle( True )
			self.play_normal_speed_bt.SetBackgroundColour( self.selected_bg_colour )

		elif play_type == PLAY_QUARTER_SPEED:
			self.play_quarter_speed_bt.SetToggle( True )
			self.play_quarter_speed_bt.SetBackgroundColour( self.selected_bg_colour )

		elif play_type == PLAY_HALF_SPEED:
			self.play_half_speed_bt.SetToggle( True )
			self.play_half_speed_bt.SetBackgroundColour( self.selected_bg_colour )

		elif play_type == PLAY_BACKWARD:
			self.play_backward_bt.SetToggle( True )
			self.play_backward_bt.SetBackgroundColour( self.selected_bg_colour )


	def add_separator( self, parent ):
		separator = Separator_Control( parent, -1, size=( 24, 1 ), colour=wx.Colour( 170, 170, 170, 0 ) )

		return separator
