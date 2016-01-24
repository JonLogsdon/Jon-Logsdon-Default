import GUILib
import AnimationEditor
import EditorLib
import render_lib
import ctg.ui
import ctg.ui.util
import ctg.callbacks
import ctg.prefs
import vlib.image
import wx
import os
import ctg
import subprocess


NO_CLIP_SELECTED  = '<no animx filename>'
TEMP_DIR				= '{0}\\ae_screen_grabs\\'.format( os.environ[ 'temp' ] )
OUTPUT_FOLDER		= 'D:\\rendered_animation_clips\\'


class Render_Preview_Progress_Dialog( ctg.ui.dialogs.CTG_Dialog ):
	def __init__( self, parent ):
		ctg.ui.dialogs.CTG_Dialog.__init__( self, parent, title = 'Render Preview Movies', size = ( 374, 350 ), lock_min_size=False, style = wx.DEFAULT_DIALOG_STYLE ) #wx.FRAME_TOOL_WINDOW )

		doc = AnimationEditor.get_active_document( )
		self.current_frame	      	= 0
		self.finished			      	= False

		self.movie_file_created			= False
		self.sel_rendered_movie_name 	= None

		self.animx_name					= self.get_sel_clips_names( )[0]
		self.frame_count					= doc.get_preview_clip_frame_count( )
		self.image_files					= [ ]
		self.path_movie_name_dict  	= { }

		self.ToggleWindowStyle( wx.RESIZE_BORDER )

		# BUILD THE UI
		#==========================================
		self.main_sizer 					= wx.BoxSizer( wx.VERTICAL )
		self.btn_sizer 					= wx.BoxSizer( wx.HORIZONTAL )
		self.output_folder_sizer 		= wx.BoxSizer( wx.HORIZONTAL )
		self.movie_ext_sizer 			= wx.BoxSizer( wx.HORIZONTAL )
		self.rendered_movies_box 		= wx.StaticBox( self, -1, 'Recent rendered movies:' )
		self.rendered_movies_sizer 	= wx.StaticBoxSizer( self.rendered_movies_box, wx.VERTICAL )


		self.txt_prog_message 			= wx.StaticText( self, -1, 'Rendering movie: {0}{1}'.format( self.animx_name, '.animx' ) )
		self.txt_output_folder 			= wx.StaticText( self, -1, 'Output Folder: ')
		self.txt_movie_ext 				= wx.StaticText( self, -1, 'Movie Ext: ')
		self.prg_render_progress 		= wx.Gauge( self, -1, self.frame_count, style = wx.GA_SMOOTH )

		self.output_folder_control 	= ctg.ui.widgets.misc.Directory_Control( self, -1, message='Choose Path:',
		                                                                       show_full_path=True,
		                                                                       default_path = OUTPUT_FOLDER,
		                                                                       size=( 224, 25 ) )


		self.btn_cancel 				= wx.Button( self, -1, "Cancel Rendering" )
		self.btn_render 				= wx.Button( self, -1, "Render Movie" )
		self.btn_close 				= wx.Button( self, -1, size=( 60,-1), label = "Close" )
		self.btn_play 					= wx.Button( self, -1, size=( 85, -1), label = "Play Movie" )
		self.btn_play.Enable( False )

		self.movie_type_control 	= wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, ( 60, -1 ), ['mov', 'avi', 'mpeg'] , 0 )
		self.render_movies 			= wx.ListBox(self, -1, (-1,-1 ), (320, 80), [ ], wx.LB_SINGLE )
		warning_str = wx.StaticText( self, -1, "WARNING: While these movie is rendering,you cannot move any\nother window on top of the AE's preview window. Rendering data\nwill be lost if this happens." )

		self.movie_ext_sizer.AddSpacer( 22 )
		self.movie_ext_sizer.Add( self.txt_movie_ext, 0, wx.ALIGN_CENTER, 5 )
		self.movie_ext_sizer.Add( self.movie_type_control, 1, wx.EXPAND | wx.ALIGN_CENTER, 5 )

		self.output_folder_sizer.Add( self.txt_output_folder, 0, wx.ALIGN_CENTER, 5 )
		self.output_folder_sizer.Add( self.output_folder_control, 1, wx.EXPAND | wx.ALIGN_CENTER, 5 )

		self.btn_sizer.Add( self.btn_render, 0, wx.ALIGN_CENTER, 5 )
		self.btn_sizer.Add( self.btn_cancel, 0, wx.ALIGN_CENTER, 5 )
		self.btn_sizer.Add( self.btn_play, 0, wx.ALIGN_CENTER, 5 )
		self.btn_sizer.Add( self.btn_close, 0, wx.ALIGN_CENTER, 5 )

		self.rendered_movies_sizer.Add( self.render_movies, 1, wx.EXPAND | wx.ALIGN_CENTER, 5 )

		self.main_sizer.Add( self.txt_prog_message, 0, wx.EXPAND | wx.ALL, 8 )
		self.main_sizer.Add( warning_str, 0, wx.EXPAND | wx.ALL, 8 )
		self.main_sizer.AddSpacer( 6 )
		self.main_sizer.Add( self.output_folder_sizer, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 1 )
		self.main_sizer.AddSpacer( 4 )
		self.main_sizer.Add( self.movie_ext_sizer, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 1 )
		self.main_sizer.AddSpacer( 4 )
		self.main_sizer.Add( self.rendered_movies_sizer, 1, wx.EXPAND )
		self.main_sizer.Add( self.prg_render_progress, 1, wx.EXPAND| wx.ALIGN_CENTER, 10 )
		self.main_sizer.Add( self.btn_sizer, 0, wx.ALIGN_CENTER | wx.TOP, 5 )
		self.main_sizer.AddSpacer( 7 )
		#==========================================

		#bind events
		self.btn_cancel.Bind( wx.EVT_BUTTON, self.cancel_pressed )
		self.Bind( wx.EVT_CLOSE, self.cancel_pressed )
		self.btn_render.Bind( wx.EVT_BUTTON, self.on_render_movie )
		self.btn_close.Bind( wx.EVT_BUTTON, self.close )
		self.btn_play.Bind( wx.EVT_BUTTON, self.on_play_movie )
		self.render_movies.Bind( wx.EVT_LISTBOX, self.on_movie_name_selected )
		self.output_folder_control.Bind( ctg.ui.widgets.misc.EVT_DIRECTORY_SELECTED, self.on_output_folder_changed  )
		self.movie_type_control.Bind( wx.EVT_CHOICE, self.on_movie_ext_changed  )

		#callbacks
		self.callback_string = 'animation_preview_render_dialog_callbacks_%s' % id( doc )

		#set default rendering values and enable controls
		self.set_default_values( )
		self.enable_controls( True )

		#setup main sizer
		self.SetSizer( self.main_sizer )


	def update_rendered_movie_names( self ):
		self.sel_rendered_movie_name = None
		items = self.get_render_movie_files( self.output_folder )
		items.sort( )
		self.render_movies.Set( items )
		self.btn_play.Enable( False )


	def on_output_folder_changed( self, event ):
		self.output_folder = self.output_folder_control.GetValue( )
		self.update_rendered_movie_names( )
		self.save_render_prefs( )


	def on_movie_ext_changed( self, event ):
		self.movie_ext = self.movie_type_control.GetStringSelection( )
		self.save_render_prefs( )


	def on_play_movie( self, event ):
		filename = self.path_movie_name_dict.get( self.sel_rendered_movie_name )

		# play movie
		if os.path.exists( filename ):
			subprocess.Popen( ( '\"' + filename + '\"' ) , shell = True )


	def on_movie_name_selected( self, event ):
		self.sel_rendered_movie_name = event.GetString( )
		if self.sel_rendered_movie_name:
			self.btn_play.Enable( True )


	def get_sel_clips_names( self ):
		doc = AnimationEditor.get_active_document( )
		sel_clips_names = [ ]

		if not doc:
			return sel_clips_names

		sel_clip_objs = doc.selection_manager.get_recent_sel_clips()
		if not sel_clip_objs:
			sel_clips_names = [ NO_CLIP_SELECTED ]
			return sel_clips_names

		for clip_obj in sel_clip_objs:
			sel_clips_names.append( clip_obj.get_name( ) )

		return sel_clips_names


	def get_preview_window_screen_rect( self ):
		"""
		Returns the screen rect of the AE's preview window.
		"""
		doc = AnimationEditor.get_active_document( )
		if not doc:
			return None

		rect 				= wx.Rect( 0, 0, 0, 0 )
		screen_rect 	= doc.get_preview_rect( )
		rect.SetPosition( ( screen_rect[ 0 ], screen_rect[ 1 ] ) )
		rect.SetSize( ( screen_rect[ 2 ] - screen_rect[ 0 ], screen_rect[ 3 ] - screen_rect[ 1 ] ) )

		return rect


	def update_frame_count( self ):
		doc = AnimationEditor.get_active_document( )
		if not doc:
			return

		self.frame_count = doc.get_preview_clip_frame_count( )
		self.prg_render_progress.SetRange( ( self.frame_count - 1 ) )


	def update_current_frame( self, doc ):

		if not self.finished:
			if self.current_frame < self.frame_count:
				self.current_frame += 1
				self.prg_render_progress.SetValue( self.current_frame )
				self.prg_render_progress.Update( )

				self.grab_anim_viewport( )
				doc.set_preview_clip_frame( int( self.current_frame ) )


		if len( self.image_files ) == self.frame_count:
			self.finish( )
			self.compile_anim_clip( )
			ctg.CALLBACK_SYSTEM.unregister_callbacks( self.callback_string )

			self.delete_temp_images( )


	def get_render_movie_files( self, directory ):
		movie_files = [ ]
		for r, d, f in os.walk( directory ):
			for movie_file in f:
				if movie_file.endswith(".mov") \
					or movie_file.endswith(".avi")\
					or movie_file.endswith(".mpeg"):

					movie_files.append( movie_file )
					self.path_movie_name_dict[ movie_file ] = os.path.join( r, movie_file )

		return movie_files


	def reset_values( self ):
		self.delete_temp_images( )
		self.finished 					= False
		self.current_frame 			= 0
		self.movie_file_created 	= False
		self.image_files 				= [ ]


	def on_render_movie( self, event ):
		doc = AnimationEditor.get_active_document( )
		if not doc:
			return

		self.enable_controls( False )
		self.update_frame_count( )
		self.reset_values( )

		#callbacks
		ctg.CALLBACK_SYSTEM.register_callback( self.callback_string, 'ae preview updated', self.update_current_frame )

		if event:
			event.Skip( )


	def finish( self ):
		self.finished = True
		self.prg_render_progress.SetValue( self.current_frame )
		self.Refresh( )


	def set_position( self ):
		"""
		Sets the position of this dialog into the middle of the screen,
		unless that would cover the preview window, which it's then moved.
		"""
		screen_rect = self.get_preview_window_screen_rect( )

		while screen_rect.Intersects( self.GetScreenRect( ) ):
			pos = self.GetPosition( )
			self.SetPosition( ( pos[ 0 ] - 2, pos[ 1 ] + 2 ) )


	def cancel_pressed( self, event ):
		doc = AnimationEditor.get_active_document( )
		if not doc:
			return

		self.enable_controls( False )

		if not self.movie_file_created:
			self.txt_prog_message.SetLabel( 'Rendering canceled... Closing...' )
			ctg.CALLBACK_SYSTEM.unregister_callbacks( self.callback_string )

		self.reset_values( )
		ctg.ui.util.set_editor_modal( False )

		self.Show( False )
		self.Destroy( )


	def delete_temp_images( self ):

		if os.path.exists( TEMP_DIR ):
			try:
				vlib.os.dir_remove( TEMP_DIR )
			except WindowsError:
				print "Could not delete the Animation Editor's preview window temp image files."


	def setup_dialog( self ):
		doc = AnimationEditor.get_active_document( )

		if self.IsShown( ) or not doc:
			return

		if hasattr( doc, 'preview_pane' ):
			self.set_position( )
			self.Show( True )
			self.Layout( )

		else:
			return


	def enable_controls( self, value ):
		if value:
			bool_cancel = False
		else:
			bool_cancel = True

		self.btn_cancel.Enable( bool_cancel )
		self.btn_close.Enable( value )
		self.btn_render.Enable( value )
		self.output_folder_control.Enable( value )
		self.movie_type_control.Enable( value )
		self.render_movies.Enable( value )


	def grab_anim_viewport( self ):

		# Create the folder if it doesn't exist
		if not os.path.exists( TEMP_DIR ):
			os.mkdir( TEMP_DIR )

		screen_grab_filename = '{0}{1}_{2}.jpg'.format( TEMP_DIR, self.animx_name, self.current_frame )
		EditorLib.editor_set_active_context( )
		did_render = render_lib.screenshot_jpeg( screen_grab_filename )

		if did_render:
			self.image_files.append( screen_grab_filename )


	def compile_anim_clip( self ):

		out_put_filename = self.animx_name + '.animx'

		text_to_burn_dict = { }
		if self.show_anim_clip_name:
			text_to_burn_dict = { self.animx_name: self.anim_name_corner }

		try:
			vlib.image.make_movie_from_image_sequence( self.image_files, self.output_folder, out_put_filename,
								                            ignore_missing_sources = True,
								                            fps = self.fps,
								                            bitrate = self.bitrate,
								                            show_movie = True,
								                            show_frame_count = self.show_frame_count,
								                            frame_count_corner = self.frame_count_corner,
								                            text_to_burn = text_to_burn_dict,
								                            font_size = self.font_size,
								                            font_color = self.font_color,
								                            extension = self.movie_ext,
								                            delete_source_images = False )
		except:
			raise AttributeError, 'Could not complete the rendering of movie: {0}'.format( self.animx_name )

		self.movie_file_created = True
		self.enable_controls( True )
		self.update_rendered_movie_names( )


	def set_default_values( self ):
		#get render preferences
		self.get_render_prefs( )


	def get_render_prefs( self ):
		# Create the folder if it doesn't exist
		if not os.path.exists( OUTPUT_FOLDER ):
			os.mkdir( OUTPUT_FOLDER )

		self.output_folder				= ctg.prefs.user.setdefault("global.animation_editor.output_folder", OUTPUT_FOLDER )
		self.movie_ext 					= ctg.prefs.user.setdefault("global.animation_editor.movie_ext", 'mov' )
		self.show_frame_count			= ctg.prefs.user.setdefault("global.animation_editor.show_frame_count", True )
		self.frame_count_corner			= ctg.prefs.user.setdefault("global.animation_editor.frame_count_corner", vlib.image.IMAGE_CORNER_UPPER_LEFT )
		self.show_anim_clip_name		= ctg.prefs.user.setdefault("global.animation_editor.show_animx_name", True )
		self.anim_name_corner			= ctg.prefs.user.setdefault("global.animation_editor.animx_name_corner", vlib.image.IMAGE_CORNER_UPPER_RIGHT )
		text_color							= ctg.prefs.user.setdefault("global.animation_editor.font_color", list( vlib.image.FONT_COLOR_WHITE ) )
		self.font_size						= ctg.prefs.user.setdefault("global.animation_editor.font_size", vlib.image.DEFAULT_FONT_SIZE )
		self.output_to_source			= ctg.prefs.user.setdefault("global.animation_editor.output_to_source", False )
		self.fps								= ctg.prefs.user.setdefault("global.animation_editor.fps", vlib.image.DEFAULT_FPS )
		self.bitrate						= ctg.prefs.user.setdefault("global.animation_editor.bitrate", vlib.image.DEFAULT_BITRATE )

		#we have to convert the color values to ints
		self.font_color 					= ( int( text_color[0] ), int( text_color[1] ), int( text_color[2] ) )

		# Create the folder if it doesn't exist
		if not os.path.exists( self.output_folder ):
			os.mkdir( self.output_folder )

		self.output_folder_control.SetValue( self.output_folder )
		self.movie_type_control.SetStringSelection( self.movie_ext )

		self.update_rendered_movie_names( )


	def save_render_prefs( self ):
		ctg.prefs.user["global.animation_editor.output_folder"] = self.output_folder_control.GetValue( )
		ctg.prefs.user["global.animation_editor.movie_ext"] = self.movie_type_control.GetStringSelection( )


	def close( self, event ):
		ctg.ui.util.set_editor_modal( False )
		self.Show( False )
		self.Destroy( )


def render_selected_anim_clips( ):

	# check to make sure the dialog exists. if not, create it
	try:
		ctg_win              = GUILib.get_global_application( ).get_main_frame( ).get_handle( )
		ctg_pre_frame        = ctg.ui.util.get_ctg_pre_frame( ctg_win )
		render_progress_win  = Render_Preview_Progress_Dialog( ctg_pre_frame )

	finally:
		ctg_pre_frame.DissociateHandle( )


	ctg.ui.util.set_editor_modal( True )
	render_progress_win.setup_dialog( )