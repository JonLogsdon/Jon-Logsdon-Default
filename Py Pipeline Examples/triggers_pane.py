

import wx
import collections
import weakref
import os
import numpy
import xml.etree

import v_engine
import vlib.ui.reflection

import AnimationEditor
import ctg.ae2.ui.lister
import ctg.ae2.ui.node
import ctg.ae2.ui.const
import ctg.ae2.core.ae_common_operations
import ctg.ui.widgets
import ctg.ui.dialogs
import ctg.ui.panel
import ctg.ui.util

import vlib.ui.widgets.panel
import vlib.ui.timeline.track_tree
import vlib.ui.timeline


ADD_TRIGGER 	= "Add Triggers"
DELETE_TRIGGER = "Delete Triggers"

CHOICES 	= "choices"
INTEGER 	= "integer"
FLOAT 	= "float"
STRING 	= "string"
BOOL 		= "bool"

NOT_PLAYING						= 'not_playing'
PLAY_NORMAL_SPEED 			= 'play_normal_speed'
PLAY_HALF_SPEED 				= 'play_half_speed'
PLAY_QUARTER_SPEED 			= 'play_quarter_speed'
PLAY_BACKWARD 					= 'play_backward'
FORWARD 							= 'forward'
BACKWARD 						= 'backward'
HALF_SPEED 						= 'half_speed'
QUARTER_SPEED 					= 'quarter_speed'

ADD_TRIGGER_ID     = 20
DELETE_TRIGGER_ID  = 21
MOVE_TRIGGER_ID    = 22
SCALE_TRIGGER_ID   = 23
WEIGHT_TRIGGER_ID  = 23
ADD_TRIGGER_CATEGORY_ID           = wx.NewId( )
DELETE_TRIGGER_CATEGORY_ID        = wx.NewId( )
CMD_ID_ADD_TRIGGER_TO_CATEGORY    = wx.NewId( )
CMD_ID_DELETE_CATEGORY            = wx.NewId( )
CMD_ID_RENAME_CATEGORY            = wx.NewId( )
CMD_ID_ADD_TRIGGER_CATEGORY       = wx.NewId( )
CMD_ID_ADD_TRIGGER                = wx.NewId( )
CMD_ID_DELETE_TRIGGER             = wx.NewId( )
CMD_ID_DELETE_SELECTED_TRIGGER    = wx.NewId( )
CMD_ID_MOVE_TRIGGER_TO_CATEGORY   = wx.NewId( )
CMD_ID_COPY_TRIGGERS              = wx.NewId( )
CMD_ID_COPY_SELECTED_TRIGGERS     = wx.NewId( )
CMD_ID_PASTE_TRIGGERS             = wx.NewId( )
CMD_ID_PASTE_TRIGGERS_TO_CATEGORY = wx.NewId( )


HELP_URL = ur"onenote:http://vsp/projects/ctg/CTG%20OneNote/CTG/Tools/User%20Documentation/CTG%20Editor/Animation%20Editor/General.one#section-id={866BB17A-1B64-4D66-AB0E-17AA3344AEA0}&end"


def set_colors( view ):
	renderer                            = view.get_renderer( )
	renderer.color_bg_border 				= wx.Colour( 130, 130, 130 )
	renderer.color_bg_default 				= wx.Colour( 0, 255, 0 )
	renderer.color_bg_default_odd 		= wx.Colour( 135, 135, 135 )
	renderer.color_bg_selected 			= wx.Colour( 255, 216, 0 )
	renderer.color_bg_selected_odd 		= wx.Colour( 255, 216, 0 )
	renderer.color_tree_connections  	= wx.Colour( 68, 68, 68 )
	renderer.color_txt_static				= wx.Colour( 0, 130, 130 )
	renderer.color_view_color_top 		= wx.Colour( 150, 150, 150 )
	renderer.color_view_color_bottom 	= wx.Colour( 150, 150, 150 )
	renderer.pen_item_bg					   = wx.Pen( renderer.color_bg_border, 1 )


class Trigger_Tree_Renderer( vlib.ui.timeline.renderer.Timeline_Renderer ):
	def draw_item_buttons( self, view, item, dc, rect ):
		"""
		Draw the buttons for a particular item (expand, loop, etc.)

		*Arguments:*
			* ``view``			The view that contains the item
			* ``item``			The item to draw
			* ``dc``				The DC to draw in
			* ``rect``			The rect to draw in

		*Keyword Arguments:*
			* ``None``

		*Returns:*
			* ``None``

		*Author:*
			* Jon Logsdon, jon.logsdon@dsvolition.com
		"""

		button_rect = wx.Rect( *rect )
		buttons     = list( view.get_registered_item_buttons( ) )
		buttons.reverse( )

		index = 0
		for node_button in buttons:
			if node_button.can_draw( view, item ):

				hit_rect = node_button.get_hit_rect( view, button_rect, item )
				if node_button.order > 1:
					hit_rect.x = hit_rect.x + 1

				if node_button.align == wx.ALIGN_RIGHT:
					color = vlib.ui.timeline.renderer.Color( *self.color_bg_label )
					dc.SetBrush( wx.Brush( color.get_scaled( 0.9 ) ) )
					dc.SetPen( wx.Pen( self.color_bg_border, 1 ) )
					dc.DrawRectangle( *hit_rect )
					dc.SetPen( wx.Pen( color.get_scaled( 1.1 ), 1 ) )
					dc.DrawLine( hit_rect.x, hit_rect.bottom, hit_rect.right, hit_rect.bottom )
					dc.DrawLine( hit_rect.x, hit_rect.top, hit_rect.right, hit_rect.top )
					dc.DrawLine( hit_rect.right, hit_rect.top, hit_rect.right, hit_rect.bottom + 1 )
					dc.DrawLine( hit_rect.left, hit_rect.top, hit_rect.left, hit_rect.bottom + 1 )

				icon = node_button.get_draw_icon( view, item, draw_state = False )
				w, h = icon.GetSize( )
				icon_rect = wx.Rect( 0, 0, w, h )
				icon_rect = icon_rect.CenterIn( hit_rect )

				# event rect height w/ odd icon size OR inverse
				if ( ( hit_rect.height%2 == 0 ) and ( h%2 != 0 ) ) or \
				   ( ( hit_rect.height%2 != 0 ) and ( h%2 == 0 ) ):
					icon_rect.y += 1

				dc.SetBackgroundMode( wx.TRANSPARENT )
				if icon.IsOk( ):
					dc.DrawBitmap( icon, icon_rect.x, icon_rect.y, useMask = True )

				index += 1


	def _draw_clip_bar( self, dc, view, item, rect, reverse = False, hover = False ):
		"""
		Draw a clip bar for a track with keys

		*Arguments:*
			* ``dc``					The DC to draw to
			* ``view``				The view containing the item
			* ``item``				The item to draw a clip for
			* ``rect``				The rect to draw the clip in
			* ``reverse``			<bool> Whether to instead draw a clip bar in the reverse range

		*Keyword Arguments:*
			* ``None``

		*Returns:*
			* ``range				<tuple> The start and end X values of the clip bar

		*Author:*
			* Jon Logsdon, jon.logsdon@dsvolition.com
		"""

		has_split_key = False
		clip_length   = view.get_clip_length( )
		l_time        = view.get_time_at_frame( clip_length )

		for key in item.get_keys( ):
			if key.split:
				has_split_key = True
				break

		if reverse:
			track_range = item.get_range( recursive = True, include_clips = False )
			r_end       = view.reverse_range.get_end( )
			s_start     = view.sequence_range.get_start( )
			try:
				track_range = ( r_end - track_range[ 1 ] + s_start, r_end - track_range[ 0 ] + s_start )
			except TypeError:
				return None, None
		else:
			track_range = item.get_range( recursive = True, include_clips = True )


		if not view.grid.is_range_visible( track_range ):
			return None, None

		is_selected = item in view.get_selection_manager( ).get_selection( )
		is_hover    = item is view.get_hover_item( )

		if reverse:
			pen_color = self._get_clip_color( item, False, False )
		else:
			pen_color   = self._get_clip_color( item, is_selected = is_selected, is_hover = is_hover )
			brush_color = vlib.ui.timeline.renderer.Color( *pen_color )

		pen_color.ScaleRGB( 0.75 )

		if has_split_key:
			start_x, end_x = view.get_coord_at_time( 0 ), view.get_coord_at_time( l_time )
		else:
			start_x, end_x = view.get_range_coords( track_range )

		start_x -= view.label_width
		end_x -= view.label_width

		clip_rect = wx.Rect( start_x, rect.bottom - self.icon_range[ 0 ].Size[ 1 ] + 1, end_x - start_x, self.icon_range[ 0 ].Size[ 1 ] )
		dc.SetPen( wx.Pen( pen_color, 1 ) )
		if reverse or ( not is_hover and not is_selected and view.get_item_accessor( ).is_key_track( item ) ):
			dc.SetBrush( wx.TRANSPARENT_BRUSH )
		else:
			dc.SetBrush( wx.Brush( brush_color ) )

		dc.DrawRectangle( *clip_rect )
		if is_selected and not reverse and not start_x == end_x:
			view_range = view.grid.get_range( vertical = False )
			icon_y     = rect.bottom - self.icon_range[ 0 ].Size[ 1 ]
			if track_range[ 0 ] >= view_range[ 0 ]:
				dc.DrawBitmap( self.icon_range[ 0 ], clip_rect.x, clip_rect.y, useMask = True )

			if track_range[ 1 ] <= view_range[ 1 ]:
				dc.DrawBitmap( self.icon_range[ 1 ], clip_rect.right - self.icon_range[ 1 ].Size[ 0 ] + 1, clip_rect.y, useMask = True )

		return start_x, end_x


	def _draw_label( self, dc, view, item, rect ):
		"""
		Draw a track's label

		*Arguments:*
			* ``dc``				The DC to draw to
			* ``view``			The view containing the item
			* ``item``			The item to draw a label for
			* ``rect``			The rect to draw the label in

		*Keyword Arguments:*
			* ``None``

		*Returns:*
			* ``None``

		*Author:*
			* Jon Logsdon, jon.logsdon@dsvolition.com
		"""

		accessor = view.column_collection.get_accessor_by_visible_index( 0 )
		label = accessor.get_display_value( item )

		# Define color and font weight based on selection, errors, etc.
		if item in view.get_selection_manager( ).get_selection( ):
			if item.get_hidden( ):
				dc.SetFont( self.hidden_font_selected )
			else:
				dc.SetFont( self.bold_font )

			if accessor.get_has_error( item, view ):
				color = self.color_bg_error
			else:
				color = vlib.ui.timeline.renderer.Color( *self.color_bg_label )
				color.maximize_RGB( )
		else:
			if item.get_hidden( ):
				dc.SetFont( self.hidden_font )
			else:
				dc.SetFont( self.orig_font )

			if accessor.get_has_error( item, view ):
				color = self.color_bg_error

			elif item.get_hidden( ):
				color = self.color_hidden_bg

			elif item in view.get_emphasis( ):
				color = vlib.ui.timeline.renderer.Color( *self.color_bg_range_bar )
				color.ScaleRGB( 1.35 )

			else:
				color = self.color_bg_label

		dc.SetTextForeground( self.get_item_font_color( view, item, accessor ) )

		# Draw track label background
		dc.SetPen( wx.TRANSPARENT_PEN )
		if not accessor.is_key_track( item ):
			color = color.get_scaled( 0.86 )

		dc.SetBrush( wx.Brush( color ) )
		dc.DrawRectangle( *rect )

		text_rect = self.get_item_text_rect( view, rect, item, accessor = accessor )

		if accessor.is_key_track( item ):
			color = self._get_clip_color( item )
			side_length = rect.height * 0.5
			dc.SetPen( wx.Pen( color.get_scaled( 0.75 ), 1 ) )
			dc.SetBrush( wx.Brush( color ) )

		if label:
			if dc.GetTextExtent( label )[ 0 ] >= text_rect.GetWidth( ):
				# Clipping region operations are slow;
				# so we only use it if we determine the text will overflow
				dc.DestroyClippingRegion( )
				dc.SetClippingRegion( *text_rect )

				dc.DrawLabel( label, text_rect, wx.ALIGN_CENTER_VERTICAL )
				dc.DestroyClippingRegion( )
			else:
				dc.DrawLabel( label, text_rect, wx.ALIGN_CENTER_VERTICAL )


	def _draw_hover_item( self, dc, view ):
		return


	def _draw_keys( self, dc, view, item, rect ):
		"""
		Draw keys for all visible tracks.

		*Arguments:*
			* ``dc``				The DC to draw to
			* ``view``			The view containing the item
			* ``item``			The item to draw a label for
			* ``rect``			The rect to draw the label in

		*Keyword Arguments:*
			* ``None``

		*Returns:*
			* ``None``

		*To Do:*
			* Split this up into more manageable chunks; this method is too large for easy comprehension

		*Author:*
			* Jon Logsdon, jon.logsdon@dsvolition.com
		"""


		clips = item.get_keys( recursive = False, include_clips = True )
		has_selected_keys = False

		if not clips:
			return

		for key in clips:
			if key in view.get_selection_manager( ).get_selection( ):
				has_selected_keys = True
				break

		#if a track got any selected keys draw ticks and frame labels
		if has_selected_keys:
			frames_per_tick = 1000 / float( view.frames_per_second )
			ms_per_interval = 1000


			clip_rect = wx.Rect( 0, rect.y - 1, view.Size[ 0 ] - view.label_width + 1, rect.height + 1 )
			self._draw_time_scale_ticks( dc, view, clip_rect, frames_per_tick, ms_per_interval )
			self._draw_frame_labels_on_track( dc, view, clip_rect )


		item_accessor = view.get_item_accessor( )
		item_range    = item.get_range( recursive = False )
		keys          = [ ]

		dc.SetBackgroundMode( wx.TRANSPARENT )
		key_rect        = wx.Rect( *rect )
		key_rect.y      = key_rect.y + 1
		key_rect.height = self.get_key_icon( view ).Size[ 1 ] + 4

		# Draw unselected clips, store others for later
		sel_clips = [ ]
		for clip in clips:
			if clip.get_length( ) == 0:
				# If the clip has 0 length, save it as a keyframe to draw later
				keys.append( clip )
				continue
			if not clip.intersects( *view.grid.get_range( vertical = False) ):
				# If the clip starts after or ends before the viewable range, don't draw it
				continue
			if clip in view.get_selection_manager( ).get_selection( ):
				# If the clip is selected, save it for drawing later
				sel_clips.append( clip )
			else:
				# Draw the clip
				self._draw_clip( dc, view, clip, key_rect, False, item_accessor )
		# Now draw selected clips
		for clip in sel_clips:
			self._draw_clip( dc, view, clip, key_rect, True, item_accessor )

		# Draw start/end lines, only if there is more than one key on the track
		# We check the length of keys because clips currently don't loop
		loop_time_offset = None
		if len( keys ) > 1:
			dc.SetPen( wx.BLACK_PEN )
			start_time = item_range[ 0 ]
			# Draw start line
			if view.grid.is_point_visible( ( start_time, None ) ):
				line_x = view.get_coord_at_time( start_time )
				dc.DrawLine( line_x, rect.y + ( rect.height * 0.5 ), line_x, rect.bottom )
			# Draw end line
			if view.grid.is_point_visible( ( item_range[ 1 ], None ) ):
				line_x = view.get_coord_at_time( item_range[ 1 ] )
				dc.DrawLine( line_x, rect.y + ( rect.height * 0.5 ), line_x, rect.bottom )

			if item_accessor.is_looping( item ):
				# Draw multiple lines for each loop of the key set
				loop_time_offset = item_range[ 1 ] - start_time + item.get_loop_offset( )
				start_time += loop_time_offset
				# If the start of the track is left of the viewable range, increase start_time until it's in it
				while start_time < view.grid.get_start( )[ 0 ]:
					start_time += loop_time_offset
				while view.sequence_range.contains( start_time ):
					line_x = view.get_coord_at_time( start_time )
					dc.DrawLine( line_x, rect.y + ( rect.height * 0.5 ), line_x, rect.bottom )
					start_time += loop_time_offset

		# Prepare to draw key icons
		dc.SetFont( self.key_font )
		dc.SetTextForeground( self.color_clip_text )

		def_keys = [ ]
		sel_keys = [ ]

		for key in keys:
			if key in view.get_selection_manager( ).get_selection( ):
				# Key is selected, save it in selected key list
				sel_keys.append( key )
			elif item_accessor.can_be_moved( key ):
				# Key is not selected and can be moved, save it in default key list
				def_keys.append( key )
			else:
				# Key should be drawn ghosted
				label = item_accessor.get_display_value( key )
				self._draw_key( dc, view, key, key_rect, False, label )

		# Draw default keys
		for key in def_keys:
			label = item_accessor.get_display_value( key )
			self._draw_key( dc, view, key, key_rect, False, label )

		# Draw selected keys last so that they appear overtop unselected keys
		for key in sel_keys:
			label = item_accessor.get_display_value( key )
			self._draw_key( dc, view, key, key_rect, True, label )


	def _draw_frame_labels_on_track( self, dc, view, rect ):

		# Get the time of the next interval
		labels_per_second = 1000 / float( view.ms_per_interval )
		while view.frames_per_second % labels_per_second > 0:
			labels_per_second -= 1
		ms_per_label = 1000 / labels_per_second

		next_tick = vlib.ui.timeline.renderer.get_next_multiple_of( ms_per_label, view.grid.get_start( )[0])
		dc.SetPen( wx.GREY_PEN )
		dc.SetFont( self.clip_font )

		t_end = view.Size[ 0 ] - view.label_width
		t = view.get_time_at_frame( view.clip_length )
		c = view.get_coord_at_time( t )

		while next_tick < view.grid.get_end( )[ 0 ]:
			# Get the X value of the interval
			tick_val = int( next_tick * 0.01 ) * 100
			text_x   = view.get_coord_at_time( next_tick ) - view.label_width

			# Convert the interval time to m, s, ms for display purposes
			time_text = str( int( round ( ( abs( next_tick ) / 1000 ) * view.frames_per_second ) ) )
			text_w, text_h = dc.GetTextExtent( time_text )

			# Add a minus sign if the time is less than zero
			if next_tick < 0:
				time_text = '-{0}'.format( time_text )
				n_text_w, n_text_h = dc.GetTextExtent( time_text )
				text_x -= ( n_text_w - text_w ) * 0.5
				text_w  = n_text_w

			# Calculate the text rect and draw the label
			text_rect = wx.Rect( text_x - ( text_w * 0.5 ), rect.y + 1, text_w, text_h )
			dc.DrawLabel( time_text, text_rect )
			next_tick += ms_per_label


	def _draw_clip( self, gcdc, view, item, rect, is_selected, item_accessor ):
		"""
		Draw a clip, which is basically a key with length

		*Arguments:*
			* ``gcdc``				The GC to draw to
			* ``view``				The view containing the item
			* ``item``				The item to draw a clip for
			* ``rect``				The rect to draw the item in
			* ``is_selected``		<bool> Whether the item is selected
			* ``item_accessor``	The item accessor for the view

		*Keyword Arguments:*
			* ``None``

		*Returns:*
			* ``None``

		*Author:*
			* Jon Logsdon, jon.logsdon@dsvolition.com
		"""

		# create graphics context from the device context
		start = item.get_start( )
		end   = item.get_end( )

		start_frame = view.convert_time_to_frame( float( start ), rounded = True )
		end_frame   = view.convert_time_to_frame( float( end ), rounded = True )
		clip_length = view.get_clip_length( )
		clip_end_time = view.get_time_at_frame( clip_length )

		start_x, end_x = view.get_coord_at_time( item.get_start( ) ), view.get_coord_at_time( item.get_end( ) )
		if start_x is None:
			return
		start_x -= view.label_width
		end_x -= view.label_width

		w = end_x - start_x + 1
		clip_rect = wx.Rect( start_x, rect.y, w, rect.height + 1 )


		is_hover    = item is view.get_hover_item( )
		pen_color   = vlib.ui.timeline.renderer.Color( *self._get_clip_color( item.get_track( ), is_selected, is_hover = is_hover ) )
		brush_color = vlib.ui.timeline.renderer.Color( *pen_color )

		if item in view.get_selection_manager( ).get_selection( ):
			icon_index = 1
		else:
			icon_index = 0

		pen_color.ScaleRGB( 0.75 )

		gcdc.SetBrush( wx.Brush( wx.Colour( pen_color[0], pen_color[1], pen_color[2], 130 ) ) )
		gcdc.SetPen( wx.Pen( wx.Colour( brush_color[0], brush_color[1], brush_color[2], 220 ), 1 ) )

		off_set = self.icon_clip_end[ icon_index ].Size[ 0 ]
		if end_frame > clip_length and start_frame < clip_length:

			d = end_frame - clip_length
			t_e_time = view.get_time_at_frame( d )
			t_s_time = view.get_time_at_frame( 0 )

			s_x, e_x = view.get_coord_at_time( int( t_s_time ) ), view.get_coord_at_time( int( t_e_time ) )

			s_x -= view.label_width
			e_x -= view.label_width

			end_rect_width = e_x - s_x + 1
			s_clip_rect    = wx.Rect( s_x, rect.y, end_rect_width, rect.height + 1 )

			#draw end rect
			gcdc.DrawRectangle( *s_clip_rect )
			if start_frame != end_frame:
				self.draw_display_value_text( gcdc, s_clip_rect, item, item_accessor, off_set )

			#start rect
			s_x_s, e_x_e = view.get_coord_at_time( int( start ) ), view.get_coord_at_time( int( clip_end_time ) )
			s_x_s -= view.label_width
			e_x_e -= view.label_width

			start_rect_width = e_x_e - s_x_s + 1
			s_clip_rect_s = wx.Rect( s_x_s, rect.y, start_rect_width, rect.height + 1 )

			#draw start rect
			gcdc.DrawRectangle( *s_clip_rect_s )
			if start_frame != end_frame:
				self.draw_display_value_text( gcdc, s_clip_rect_s, item, item_accessor, off_set )

			item.update_split_rects( True, s_clip_rect, s_clip_rect_s )

		else:
			gcdc.DrawRectangle( *clip_rect )
			item.update_split_rects( False, None, None )
			if start_frame != end_frame:
				self.draw_display_value_text( gcdc, clip_rect, item, item_accessor, off_set )


		gcdc.DrawLine( start_x, clip_rect.y, start_x, clip_rect.bottom )
		if not start_x == end_x:

			# Left clip/key icon
			start_t = start_x
			if start_frame > clip_length:
				e = start_frame - clip_length
				s_e_time = view.get_time_at_frame( e )
				start_t  = view.get_coord_at_time( int( s_e_time ) )

				start_t -= view.label_width

			start_icon = ctg.ui.util.get_project_image( "range_start_left.png", as_bitmap = True )
			if icon_index == 1:
				if not item.scale_left:
					start_icon = ctg.ui.util.get_project_image( "range_start_def.png", as_bitmap = True )

			icon_y     = rect.y + ( rect.height * 0.5 ) - ( start_icon.Size[ 1 ] * 0.5 )
			start_rect = wx.Rect( start_t, icon_y, *start_icon.Size )
			gcdc.DrawBitmap( start_icon, start_rect.x, start_rect.y + 5, useMask = True )

			# Right clip/key icon
			end_t = end_x
			if end_frame > clip_length:
				d        = end_frame - clip_length
				t_e_time = view.get_time_at_frame( d )
				end_t    = view.get_coord_at_time( int( t_e_time ) )

				end_t -= view.label_width

			end_icon = ctg.ui.util.get_project_image( "range_end_right.png", as_bitmap = True )
			if icon_index == 1:
				if not item.scale_right:
					end_icon = ctg.ui.util.get_project_image( "range_end_def.png", as_bitmap = True )

			gcdc.DrawLine( end_t, clip_rect.y, end_t, clip_rect.bottom )
			end_t = end_t - end_icon.Size[ 0 ] + 1
			end_rect = wx.Rect( end_t, icon_y, *end_icon.Size )
			gcdc.DrawBitmap( end_icon, end_rect.x, end_rect.y + 5, useMask = True )


	def draw_display_value_text( self, dc, clip_rect, item, item_accessor, off_set ):
		# Label the clip in two lines: Value of clip and duration of clip
		dc.SetFont( self.clip_font )
		dc.SetTextForeground( self.color_clip_text )
		text_rect = wx.Rect( *clip_rect )
		m = text_rect.width /2
		text_rect.x = ( m + text_rect.x ) - off_set
		dc.DrawLabel( item_accessor.get_display_value( item ), text_rect, wx.ALIGN_CENTER_VERTICAL )


	def _get_clip_color( self, item, is_selected = False, is_hover = False ):
		"""
		Get a clip's display color based on selection/hover states

		*Arguments:*
			* ``item``			The item to get the color of

		*Keyword Arguments:*
			* ``is_selected``	<bool> Whether the item is selected
			* ``is_hover``		<bool> Whether the mouse is currently over this item

		*Returns:*
			* ``color``			<Color> The color to display

		*Author:*
			* Jon Logsdon, jon.logsdon@dsvolition.com
		"""

		if is_selected:
			return vlib.ui.timeline.renderer.Color( *item.get_color_selected( ) )
		else:
			return vlib.ui.timeline.renderer.Color( *wx.Colour( 0, 255, 0 ) )



class Trigger_Timeline_Key( vlib.ui.timeline.data.Timeline_Key ):
	def __init__( self, parent,
	              time_val,
	              length   = 0,
	              value    = None,
	              data_obj = None ):

		self.split       = False
		self.left_rect   = None
		self.right_rect  = None
		self.scale_right = False
		self.scale_left  = False


		super( Trigger_Timeline_Key, self ).__init__( parent,
		                                              time_val,
		                                              length   = length,
		                                              value    = value,
		                                              data_obj = data_obj )

		self.original_end_time = self.get_end( )


	def update_split_rects( self, split, left_rect, right_rect ):
		self.split      = split
		self.left_rect  = left_rect
		self.right_rect = right_rect

	def get_data_obj( self ):
		return self._data_obj


	def get_start( self ):
		"""
		Convenience function that duplicates functionality of get_time, but makes more sense with the concept of a range.

		*Author:*
			* Jon Logsdon, jon.logsdon@dsvolition.com
		"""
		return self.get_time( )


	def set_start( self, value ):
		"""
		Set the start time of the range without affecting the end time.

		*Author:*
			* Jon Logsdon, jon.logsdon@dsvolition.com
		"""
		end = self.get_end( )
		self.set_time( value )
		self.set_end( end )


	def get_end( self ):
		return self.get_start( ) + self.get_length( )


	def set_end( self, time_val ):
		self.set_length( max( 0, time_val - self.get_start( ) ) )


	def get_range( self ):
		return ( self.get_start( ), self.get_end( ) )


	def set_range( self, start_time, end_time ):
		self.set_start( start_time )
		self.set_end( end_time )



class Trigger_Timeline_Track( vlib.ui.timeline.data.Timeline_Track ):
	def __init__( self, parent 	= None,
	              name 				= 'Track Name',
	              show_range		= False,
	              show_clips		= False,
	              show_keys			= False,
	              imply_zero_key	= False,
	              reversible		= True,
	              key_class       = Trigger_Timeline_Key,
	              *args, **kwargs ):

		super( Trigger_Timeline_Track, self ).__init__( parent 	= parent,
		                                                name 				= name,
		                                                show_range		= show_range,
		                                                show_clips		= show_clips,
		                                                show_keys			= show_keys,
		                                                imply_zero_key	= imply_zero_key,
		                                                reversible		= reversible,
		                                                key_class       = key_class,
		                                                *args, **kwargs )


	def _create_child_track( self, name = None ):
		"""
		Create a track with this track as its parent. If a track already exists with the provided name, that track is returned.

		*Arguments:*
			* ``None``

		*Keyword Arguments:*
			* ``name``		The name of the track to create, or a ( name, class ) tuple for the class to create

		*Returns:*
			* ``child``		The child track with the provided name.

		*Author:*
			* Jon Logsdon, jon.logsdon@dsvolition.com
		"""

		name, track_class = self._split_track_name_class( name )
		child_track = self.get_child_by_name( name )

		if child_track is not None:
			# this track already has a child with the provided name, return it
			return child_track

		# No child exists with provided name; make a new track
		child_track = track_class( self, name = name )
		self.add_child( child_track )
		self._show_clips = True

		return child_track


	def _split_track_name_class( self, name ):
		"""
		If a tuple is sent in for name, split it into name and track_class

		*Arguments:*
			* ``name``		The name of a track, or a ( name, class ) tuple for the class to create

		*Keyword Arguments:*
			* ``None``

		*Returns:*
			* ``name``				The name to use
			* ``track_class``		The class to use

		*Author:*
			* Jon Logsdon, jon.logsdon@dsvolition.com
		"""

		try:
			# name is a collection with two entries. Use the first as name and the second as track_class
			name, track_class = name.__iter__( )

		except AttributeError:
			# name is not a collection, so leave it alone and prepare track_class
			track_class = Trigger_Timeline_Track

		except ValueError:
			# name is a collection but has more than two entries. Use the first as name and prepare a track_class
			name = name[ 0 ]
			track_class = Trigger_Timeline_Track

		return name, track_class


class Trigger_Column_Accessor_Label( vlib.ui.timeline.data.Column_Accessor_Label ):
	def get_editor_widget_kwargs_for_item( self, item, widget_class = None ):
		doc = AnimationEditor.get_active_document( )
		widget_kwargs = {"choices": list( doc.get_trigger_names( ) ), "allow_invalid_entry": True, "style": wx.BORDER_NONE }

		return widget_kwargs

	def get_value( self, item ):
		value = item
		return item.get_name( )

	def set_value( self, item, value ):
		item.set_name( value )


	def get_editor_class_for_item( self, item, for_renderer = False ):

		if isinstance( item, vlib.types.Base_Parent ):
			return None

		return ctg.ae2.ui.column_editors.Editor_Type_Auto_Comp_Enum


class Trigger_Column_Accessor_Track( vlib.ui.timeline.data.Column_Accessor_Track ):

	def get_editor_widget_kwargs_for_item( self, item, widget_class = None ):
		doc = AnimationEditor.get_active_document( )
		widget_kwargs = {"choices": list( doc.get_trigger_names( ) ), "allow_invalid_entry": True, "style": wx.BORDER_NONE }
		return widget_kwargs


	def get_value( self, item ):
		value = item
		if hasattr( item, 'get_name' ):
			return item.get_name( )


	def set_value( self, item, value ):
		if hasattr( item, 'set_name' ):
			item.set_name( value )


	def get_icon_rects( self, view, item, item_rect = None ):
		"""
		Get the icon rects for a key or clip.

		*Arguments:*
			* ``view``			The view that contains the item
			* ``item``			The item in question
			* ``item_rect``	The item rect to offset the icon rects into. Useful for getting clip rects in a clip group track.

		*Keyword Arguments:*
			* ``None``

		*Returns:*
			* ``range_rect``	The rect of the item's range
			* ``start_rect``	The rect of the start scale handle, or None
			* ``end_rect``		The rect of the end scale handle, or None

		*Author:*
			* Jon Logsdon, jon.logsdon@dsvolition.com
		"""

		item_range = self.get_range( item )
		if item_range[ 0 ] is None:
			return None, None, None

		if item_rect is None:
			item_rect = self.get_item_rect( view, item )

		item_rect = wx.Rect( *item_rect )
		start_x   = view.get_coord_at_time( item_range[ 0 ] )
		end_x     = view.get_coord_at_time( item_range[ 1 ] )

		start_rect = None
		end_rect   = None

		if isinstance( item, vlib.ui.timeline.data.Timeline_Key ):
			if start_x == end_x:

				# A key with no length
				icon_x, icon_y = view.get_renderer( ).icon_key_default.Size
				start_x -= icon_x * 0.5
				end_x   += icon_x * 0.5
				item_rect.height -= ( item_rect.height - icon_y ) * 0.5

			else:
				# A key with length
				icon_x, icon_y = view.get_renderer( ).icon_clip_start[ 0 ].Size
				if item.split:
					start_x = item.right_rect.x
					end_x   = item.left_rect.x + item.left_rect.width

				start_rect = wx.Rect( start_x, item_rect.top + 10, icon_x, icon_y + 50 )
				end_rect   = wx.Rect( end_x - icon_x, item_rect.top + 10, icon_x, icon_y + 50 )

		elif isinstance( item, vlib.ui.timeline.data.Timeline_Track ):
			icon_x, icon_y = view.get_renderer( ).icon_range[ 0 ].Size
			start_rect = wx.Rect( start_x, item_rect.bottom - icon_y, icon_x, icon_y )
			end_rect   = wx.Rect( end_x - icon_x, item_rect.bottom - icon_y, icon_x, icon_y )


		range_rect = wx.Rect( start_x, item_rect.bottom - icon_y, end_x - start_x, icon_y )
		range_rect.height = range_rect.height + 6


		return range_rect, start_rect, end_rect



DELETE_ON_ICON  = ctg.ui.util.get_project_image( 'delete_16.png', as_bitmap = True )
DELETE_OFF_ICON = ctg.ui.util.get_project_image( 'deleteDisabled_16.png', as_bitmap = True )
ICON_SET_DELETE = { \
   0	:  DELETE_ON_ICON,
   1	:  DELETE_OFF_ICON,
   2	:  DELETE_OFF_ICON, # tri-state
}

ADD_ON_ICON  = ctg.ui.util.get_project_image( 'add_item_16.png', as_bitmap = True )
ADD_OFF_ICON = ctg.ui.util.get_project_image( 'add_item_16.png', as_bitmap = True )
ICON_SET_ADD = { \
   0	:  ADD_ON_ICON,
   1	:  ADD_OFF_ICON,
   2	:  ADD_ON_ICON, # tri-state
}



class Item_Button_Delete_Track( vlib.ui.timeline.track_tree.Item_Button ):
	def __init__( self ):
		super( Item_Button_Delete_Track, self ).__init__( ICON_SET_DELETE, order = 1 )


	def can_draw( self, view, item, accessor = None ):
		return view.get_item_accessor( ).is_key_track( item )


	def on_click( self, view, rect, item, coord, items ):
		if self.is_enabled:
			column_rect = wx.Rect( rect.x, rect.y, view.label_width, rect.height )
			if self.did_click( view, column_rect, item, coord ):
				triggers = [ ]
				for key in item.get_keys( ):
					if key.get_data_obj( ):
						triggers.append( key.get_data_obj( ) )

				if triggers:
					dlg = wx.MessageDialog( view, 'Are you sure you want to delete {0} trigger(s)?'.format( len( triggers ) ),
					                        'Deleting Animation Trigger(s)', wx.OK | wx.CANCEL | wx.ICON_INFORMATION )
					if dlg.ShowModal() == wx.ID_OK:
						delete = view.delete_triggers( triggers )
						if delete:
							wx.CallAfter( view.GetParent( ).GetParent( ).refresh_ui )
							wx.CallAfter( view.GetParent( ).GetParent( ).refresh_anim_properties_pane )

					dlg.Destroy( )

				return False

		return False


class Item_Button_Add_Track( vlib.ui.timeline.track_tree.Item_Button ):
	def __init__( self ):
		super( Item_Button_Add_Track, self ).__init__( ICON_SET_ADD, order = 2 )


	def can_draw( self, view, item, accessor = None ):
		return view.get_item_accessor( ).is_key_track( item )


	def on_click( self, view, rect, item, coord, items ):
		if self.is_enabled:
			column_rect = wx.Rect( rect.x, rect.y, view.label_width, rect.height )
			if self.did_click( view, column_rect, item, coord ):
				frame = view.convert_time_to_frame( view.get_time( ), rounded = True )
				start_frame = frame
				end_frame   = frame + 1
				category    = item.get_parent( ).get_name( )

				if category == 'Default':
					category = None

				view.add_new_trigger( item.get_name( ), start_frame, end_frame, category = category )

				return True

		return False


class Trigger_Timeline_Selection_Manager( vlib.ui.timeline.input.Selection_Manager_Timeline ):

	def get_items_in_rect( self, view, rect, virtual = True ):
		"""
		Get the items (keyframes) that are in a specific rect

		*Arguments:*
			* ``view``		The view that the items exist in
			* ``rect``		The rect to test items against

		*Keyword Arguments:*
			* ``None``

		*Returns:*
			* ``items``		<list> Items that exist full inside the rect

		*Author:*
			* Jon Logsdon, jon.logsdon@dsvolition.com
		"""

		items     = [ ]
		icon_size = view.get_renderer( ).get_key_icon( view ).Size
		icon_rect = wx.Rect( 0, 0, *icon_size )

		i = 0
		# Loop through the visible track rects
		for r in view.visible_item_rects:

			# Make sure the selection rectangle intersects with the track
			if rect.Intersects( r ):

				# Move the icon rect to vertically sit inside this track
				icon_rect.y = r.y + 2

				# Get the item associated with that rect and make sure it is a track
				item = view.visible_items[ i ]
				if view.get_item_accessor( ).is_track( item ):

					# Test each key (and that key's looping keys) to see if any are in the rect
					for key in item.get_keys( recursive = False ):
						if key.split:
							left_rect    = wx.Rect( *key.left_rect )
							right_rect   = wx.Rect( *key.right_rect )
							left_rect.y  = r.y + 2
							right_rect.y = r.y + 2

							left_rect.x += view.label_width
							right_rect.x += view.label_width

							# Save them in the selected items list to be returned
							if left_rect.Intersects( rect ) or right_rect.Intersects( rect ):
								items.append( key )

						else:
							length = key.get_length( )
							if length > 0:
								length = view.get_coord_offset( length )
							if virtual:
								x_coords = [ x for x in view.get_renderer( ).get_key_x_coords( view, key ) if x >= 0 ]
							else:
								x_coords = [ view.get_coord_at_time( key.get_time( ) ) ]

							for x in x_coords:
								icon_rect.x = x
								if length:
									icon_rect.width = length + 1
								else:
									icon_rect.width = icon_size[ 0 ]
									icon_rect.x -= icon_rect.width * 0.5

								# Save them in the selected items list to be returned
								if icon_rect.Intersects( rect ):
									items.append( key )
			i += 1
		return items


	def _coord_get_key_track( self, key_track, view, coord, virtual = True ):
		"""
		Get the key on track that exists at a specific coordinate

		*Arguments:*
			* ``key_track``		The track that the key is on
			* ``view``				The view that the track exists in
			* ``coord``				The ( x, y ) coordinate to test items against

		*Keyword Arguments:*
			* ``None``

		*Returns:*
			* ``key``		The track that exists at that coordinate or None

		*Author:*
			* Jon Logsdon, jon.logsdon@dsvolition.com
		"""

		# Make sure there are keys on the track, return if not
		keys = key_track.get_keys( )
		if len( keys ) < 1:
			return None

		# Get the visible rect for the key_track
		item_accessor = view.get_item_accessor( )
		rect = item_accessor.get_item_rect( view, key_track )

		## Make a rect for the key icon that can be moved along the X-axis for hit testing
		#icon_rect = wx.Rect( 0, rect.y + 2, *view.get_renderer( ).get_key_icon( view ).Size )

		# Test each key (and that key's looping keys) to see if any are in the rect
		for key in keys:
			if key.split:
				coord[0] -= view.label_width
				left_rect    = key.left_rect
				right_rect   = key.right_rect
				left_rect.y  = rect.y
				right_rect.y = rect.y

				if left_rect.Contains( coord ) or right_rect.Contains( coord ):
					return key
			else:
				start = view.get_coord_at_time( key.get_start( ) )
				end   = view.get_coord_at_time( key.get_end( ) )
				width = end - start

				key_rect = wx.Rect( start, rect.y, width, rect.height )
				if key_rect.Contains( coord ):
					return key


		return None



class Trigger_Selection_Move_Timeline_Object_Input( vlib.ui.timeline.input.Handler_Selection_Move_Timeline_Object ):


	def set_item_clicked( self, item, click_pos, mod_state ):
		"""
		Set appropriate variables when an item is clicked.

		* Arguments:
			* ``item``				The item being clicked
			* ``click_pos``		The position being clicked
			* ``mod_state``		The state of key modifiers

		* Keyword Arguments:
			* ``None``

		* Returns:
			* ``None``

		* Author:
			* Andy Kelts, andy.kelts@dsvolition.com, 5/8/2014
		"""

		track = self.view.get_selection_manager( ).get_track_at_coord( self.view, click_pos )
		item_accessor = self.view.get_item_accessor( )

		item_rect = item_accessor.get_item_rect( self.view, track )
		range_rect, start_rect, end_rect = item_accessor.get_icon_rects( self.view, item, item_rect )


		if range_rect is None or click_pos.x < self.view.label_width:
			return None

		selection = None
		if start_rect and start_rect.Contains( click_pos ):
			item_range = item_accessor.get_range( item )
			self.initial_pivot_left  = item_range[ 0 ]
			self.initial_pivot_right = item_range[ 1 ]
			selection       = item
			self.scale_left = True


		elif end_rect and end_rect.Contains( click_pos ):
			item_range = item_accessor.get_range( item )
			self.initial_pivot_left  = item_range[ 0 ]
			self.initial_pivot_right = item_range[ 1 ]
			selection        = item
			self.scale_right = True


		elif range_rect.Contains( click_pos ):
			selection = item


		if selection:
			self.can_drag = True
			self.view.snap_manager.add_snap_times( [ self.view.get_time( ),
			                                         self.view.playback_range.get_start( ),
			                                         self.view.playback_range.get_end( ),
			                                         self.view.sequence_range.get_start( ),
			                                         self.view.sequence_range.get_end( ) ] )

		item.scale_right = self.scale_right
		item.scale_left  = self.scale_left

		# If a scale handle was clicked, but there is no length of the clip being scaled, scaling cannot continue
		if (self.scale_left or self.scale_right) and self.initial_pivot_left == self.initial_pivot_right:
			self.scale_left = self.scale_right = False

		return item


	def can_process_event( self, event ):
		"""
		Determine whether to process the event.

		* Arguments:
			* ``event``		The wx.EVT_MOUSE_MOVE event

		* Keyword Arguments:
			* ``None``

		* Returns:
			* ``None``

		* Author:
			* Andy Kelts, andy.kelts@dsvolition.com, 5/8/2014
		"""

		# Does the click take place outside the grid items
		click_pos = event.GetPosition( )

		if click_pos.x < self.view.label_width or click_pos.y < self.view.column_header_height:
			return False

		sel_man 	 = self.view.track_selection_manager
		mod_state = sel_man.get_mod_state_from_event( event )
		item 		 = sel_man.get_item_at_coord( self.view, click_pos, virtual = True )
		if item and click_pos.x > self.view.label_width:
			item	 = self.set_item_clicked( item, click_pos, mod_state )

		self.initial_item 		= item
		self.initial_selection	= sel_man.get_selection( )
		self.rect_select 			= sel_man.is_multi_select and ( item == None )


		# If we aren't using a modifier and have clicked a selected item, process dragging
		if ( mod_state == vlib.ui.lister_lib2.const.SM_MOD_STATE_SINGLE ) and sel_man.is_item_selected( item ):
			self.can_drag = True
			self.set_offset_time( click_pos, item )
			return True

		else:
			if self.rect_select:
				mod_state = sel_man.get_mod_state_from_event( event, is_marquee = True )
				# Do a simulated click
				did_click = sel_man.select_item_at_coord( self.view, click_pos, mod_state = mod_state )
				self.rect_mod_state = mod_state
				self.can_drag = True

				return True

			else:
				self.view.track_selection_manager.set_selection( self.view, [ item ], mod_state )
				self.set_offset_time( click_pos, item )
				self.can_drag = True
				self.view.dirty_labels = True
				self.view.dirty_time_scale = True
				return item and sel_man.is_item_selected( item )
				#return True


	def do_item_offset( self, offset_val ):
		"""
		Offset the current selection.

		* Arguments:
			* ``offset_val``	Value to offset the keys by

		* Keyword Arguments:
			* ``None``

		* Returns:
			* ``None``

		* Author:
			* Andy Kelts, andy.kelts@dsvolition.com, 5/8/2014
		"""

		if not self.did_move:
			sel_man = self.view.get_selection_manager( )
			if abs( offset_val ) > self.move_threshold:
				self.did_move = True
				self.drag_selection = set( sel_man.get_selection( ) )

				# convert dragging clips to keys, removing any locked keys
				item_accessor = self.view.get_item_accessor( )
				keys = [ ]
				for item in self.drag_selection:
					if item_accessor.is_track( item ):
						keys.extend( [ key for key in item.get_keys( ) if item_accessor.can_be_moved( key ) ] )
					if item_accessor.is_key( item ) and item_accessor.can_be_moved( item ):
						keys.append( item )
				self.drag_selection = set( keys )
		else:
			self.pos_start = self.pos_last
			self.view.dirty_tracks = True
			for item in self.drag_selection:
				if self.view.bookend_keys and self.view.bookend_keys[1] != None:
					if ( item in self.view.bookend_keys and item.get_end( ) > self.view.sequence_range.get_end( ) ) \
					   or ( item.get_end( ) > self.view.bookend_keys[ 1 ].get_end( ) ):
						self.view.is_dirty = True


				item.offset_time( offset_val )
				start = item.get_start( )
				end   = item.get_end( )

				trigger_uid = item.get_data_obj( ).get_uid( )

				self.view.play_trigger( )
				trigger     = self.view.get_trigger_from_id( trigger_uid )
				start_frame = self.view.convert_time_to_frame( float( start ), rounded = True )
				end_frame   = self.view.convert_time_to_frame( float( end ), rounded = True )
				clip_length = self.view.get_clip_length( )


				start_time = None
				end_time   = None

				if end_frame > clip_length:
					end_frame = end_frame - clip_length

				if start_frame > clip_length:
					start_frame = start_frame - clip_length

				if start_frame == clip_length:
					start_time = self.view.get_time_at_frame( 0 )
					end_time   = self.view.get_time_at_frame( end_frame )

				if start_frame < 0:
					start_time = self.view.get_time_at_frame( clip_length + start_frame )
					end_time   = self.view.get_time_at_frame( clip_length + end_frame )

				if start_frame < end_frame and start_frame >= 0:
					start_time = self.view.get_time_at_frame( start_frame )
					end_time   = self.view.get_time_at_frame( end_frame )

				if start_time != None and end_time != None:
					item.set_start( int( start_time ) )
					item.set_end( int( end_time ) )

				self.view.set_trigger_value( 'start_frame', start_frame, trigger )
				self.view.set_trigger_value( 'end_frame', end_frame, trigger )

				item.get_track( ).is_dirty = True
				item.get_track( ).set_range_dirty( )


	def do_clip_scale( self, event, left = True ):
		"""
		Determine the scale value of a dragged item and scale all selected items.

		* Arguments:
			* ``event``		The wx.EVT_MOUSE_MOVE event

		* Keyword Arguments:
			* ``left``		True if scaling from the left side, False if scaling from the right side

		* Returns:
			* ``None``

		* Author:
			* Andy Kelts, andy.kelts@dsvolition.com, 5/8/2014
		"""

		self.pos_last = self.view.get_time_at_coord( event.x )
		if self.snap:
			self.pos_last = self.view.snap_manager.get_nearest_snap_time_in_tolerance( self.pos_last, self._tolerance )


		item_accessor = self.view.get_item_accessor( )
		if not self.did_move:

			if abs( self.pos_last - self.pos_start ) > self.move_threshold:
				self.did_move = True
				self.drag_selection = set( self.view.get_selection_manager( ).get_selection( ) )

				# convert dragging clips to keys, excepting any locked keys and storing necessary pivots
				self.key_times = { }
				for item in self.drag_selection:
					if item_accessor.is_track( item ):
						# Get the pivot points of the clip to store for all the keys in the clip
						clip_pivots = item_accessor.get_clip_pivots( item )

						for key in item.get_keys( ):
							if item_accessor.can_be_moved( key ):
								key_range = key.get_range( )

								# Only move the key if it's not at the pivot point
								if ( left and key_range[ 0 ] < clip_pivots[ 1 ] ) or ( not left and key_range[ 1 ] > clip_pivots[ 0 ] ) :
									self.key_times[ key ] = ( key_range, clip_pivots )

					# If the item is a key, only scale it if it can be moved and has a duration
					elif item_accessor.is_key( item ) and item_accessor.can_be_moved( item ) and item.get_length( ):
						key_range = item.get_range( )
						clip_pivots = item_accessor.get_clip_pivots( item )

						# Only move the key if it's not at the pivot point
						if ( left and key_range[ 0 ] < clip_pivots[ 1 ] ) or ( not left and key_range[ 1 ] > clip_pivots[ 0 ] ) :
							self.key_times[ item ] = ( key_range, clip_pivots )

				self.drag_selection = set( self.key_times.keys( ) )

		else:
			self.pos_start = self.pos_last
			self.view.dirty_tracks = True
			if left:
				width = self.initial_pivot_right - self.pos_last
			else:
				width = self.pos_last - self.initial_pivot_left

			scale_percent = width / float( self.initial_pivot_right - self.initial_pivot_left )

			for item in self.drag_selection:
				if self.key_times.has_key( item ):
					# If the scale is 0, but the track won't allow zero-length clips, skip this key
					if scale_percent == 0 and not item_accessor.allow_zero_length_clip( item ):
						continue

					item_times, item_pivots = self.key_times[ item ]

					if left:
						item_pivot = item_pivots[ 1 ]
					else:
						item_pivot = item_pivots[ 0 ]

					# Calculate the new start/end times
					start = int( ( item_times[ 0 ] - item_pivot ) * scale_percent ) + item_pivot
					end   = int( ( item_times[ 1 ] - item_pivot ) * scale_percent ) + item_pivot

					if self.view.bookend_keys and self.view.bookend_keys[1] != None:
						if ( item in self.view.bookend_keys and item.get_end( ) > self.view.sequence_range.get_end( ) ) \
						   or ( item.get_end( ) > self.view.bookend_keys[ 1 ].get_end( ) ):
							self.view.is_dirty = True

					trigger     = self.view.get_trigger_from_id( item.get_data_obj( ).get_uid( ) )
					start_frame = self.view.convert_time_to_frame( float( start ), rounded = True )
					end_frame   = self.view.convert_time_to_frame( float( end ), rounded = True )
					clip_length = self.view.get_clip_length( )


					if left:
						current_frame = start_frame
					else:
						current_frame = end_frame

					if current_frame > clip_length:
						current_frame = clip_length
					elif current_frame < 0:
						current_frame = 0

					if trigger:
						s_frame = trigger.get_frame( )
						e_frame = trigger.get_end_frame( )

						if left:
							if current_frame > e_frame:
								duration  = int( clip_length - current_frame ) + e_frame
							else:
								duration  = int( e_frame - current_frame )

							s_time = self.view.get_time_at_frame( current_frame )
							e_time = self.view.get_time_at_frame( duration + current_frame )

							self.set_start_and_end( item, s_time, e_time )
							self.view.set_trigger_value( 'start_frame', current_frame, trigger )

						else:
							if s_frame > current_frame:
								duration  = int( clip_length - s_frame ) + current_frame
							else:
								duration  = int( current_frame - s_frame )

							s_time = self.view.get_time_at_frame( s_frame )
							e_time = self.view.get_time_at_frame( duration + s_frame )

							self.set_start_and_end( item, s_time, e_time )
							self.view.set_trigger_value( 'end_frame', current_frame, trigger )

				#Refresh the triggers pane ui for every frame increment
				self.view.parent.Parent.refresh_ui( )
				item.get_track( ).is_dirty = True
				item.get_track( ).set_range_dirty( )



	def set_start_and_end( self, item, start, end ):

		if start == end:
			end = end + 10

		item.set_start( int( start ) )
		item.set_end( int( end ) )


	def on_release( self, event = None ):
		"""
		Event handler for releasing the left mouse button.

		* Arguments:
			* ``None``

		* Keyword Arguments:
			* ``event``		The wx.EVT_LEFT_UP event

		* Returns:
			* ``None``

		* Author:
			* Andy Kelts, andy.kelts@dsvolition.com, 5/8/2014
		"""

		skip = True
		doc = AnimationEditor.get_active_document( )

		if not doc:
			return

		if self.is_handling:
			sel_man = self.view.get_selection_manager( )

			if self.rect_select:
				sel_man.set_selection( self.view, sel_man.get_selection( ), post_event = True )

			elif not self.can_drag:
				sel_man.set_selection( self.view, [ self.initial_item ], post_event = True )

			elif self.drag_selection:
				if self.drag_selection:
					for item in self.drag_selection:
						item.original_end_time = item.get_end( )
						item.scale_right = False
						item.scale_left  = False

				self.view._on_move_timeline_objects( [ obj for obj in self.drag_selection ] )

			self.reset( )
			skip = False

			#refresh properties pane
			doc.animation_properties_pane.refresh_ui( )
			#self.view.play_trigger( )

		if event:
			event.Skip( skip )


	def reset( self ):
		"""
		Reset the input handler state; called after handling is complete.

		* Arguments:
			* ``None``

		* Keyword Arguments:
			* ``None``

		* Returns:
			* ``None``

		* Author:
			* Andy Kelts, andy.kelts@dsvolition.com, 5/8/2014
		"""

		super( Trigger_Selection_Move_Timeline_Object_Input, self ).reset( )

		self.drag_selection      = None
		self.offset_time         = 0
		self.scale_left          = False
		self.scale_right         = False
		self.initial_pivot_left  = 0
		self.initial_pivot_right = 0
		self.view.is_dirty       = True


class Editor_Type_Auto_Comp_Enum_Trigger_Name( ctg.ae2.ui.column_editors.Editor_Type_Auto_Comp_Enum ):

	def on_value_changed( self, event ):
		doc = AnimationEditor.get_active_document( )
		if not doc:
			return

		trigger_names = list( doc.get_trigger_names() )
		val = self.ctrl.GetValue( )

		refresh_view = False
		if val not in [ None, '' ]:
			if val not in trigger_names:
				doc.undoable_create_trigger_name( val )

			for key in self.item.get_keys( ):
				trigger = key.get_data_obj( )
				if trigger:
					self.view.set_trigger_value( 'name', val, trigger )

			self.accessor.set_value( self.item, val )
			refresh_view = True

		self.on_lost_focus( event )
		if refresh_view:
			wx.CallAfter( self.view.GetParent( ).GetParent( ).refresh_ui )


	def setup( self, parent ):
		super( Editor_Type_Auto_Comp_Enum_Trigger_Name, self ).setup( parent )
		self.ctrl.Bind( wx.EVT_KILL_FOCUS,	self.on_value_changed )

		self.view.set_active_editor( self )


	def on_lost_focus( self, event ):

		wx.CallAfter( self.view.destroy_active_editor )
		event.Skip( False )



class Trigger_Timeline_Context_Menu( vlib.ui.lister_lib2.core.Tree_Context_Menu ):
	"""
	This is a custon menu class for named values.

	*Arguments:*
		* ``grid``   				-wx grid
		* ``column`` 				-column number
		* ``row``    				-row number
		* ``menu_title``   		-menu title
		* ``grid_cell_found``   -bool indicating whether the user right-licked
										on a cell or not.
		* ``node_type_id``   	-named value node type
		* ``sel_objs_data``   	-selected named values data

	*Keyword Arguments:*
		* <none>

	*Author:*
		* Jon Logsdon, jon.logsdon@dsvolition.com
	"""

	def __init__( self, view, item ):
		self.prop_id_string = None

		self.selected_items = [ ]

		super( Trigger_Timeline_Context_Menu, self ).__init__( view, item )


	# OVERRIDDEN
	def _setup_menu_custom( self ):

		self.clipboard_data    = ctg.ae2.core.ae_common_operations.get_data_from_clipboard( ctg.ae2.ui.const.ANIMATION_TRIGGER )
		self.category_ids_dict = { }
		doc = AnimationEditor.get_active_document( )
		selected_clips = doc.selection_manager.get_recent_sel_clips( )
		show_menu_options = False
		if selected_clips and selected_clips[0].get_clip_length( ) > 0:
			show_menu_options = True

		if self.item and show_menu_options:
			if isinstance( self.item, Trigger_Timeline_Track ):
				if self.item.is_clip_track( ):
					add_item = wx.MenuItem( self, CMD_ID_ADD_TRIGGER_TO_CATEGORY, u'Add Trigger to Category', wx.EmptyString, wx.ITEM_NORMAL )
					add_item.SetBitmap( ctg.ui.util.get_project_image( 'outliner_objset_delete_16.png', as_bitmap = True ), wx.BITMAP_TYPE_ANY )
					self.AppendItem( add_item )

					if self.item.get_name( ) != 'Default':
						add_item = wx.MenuItem( self, CMD_ID_RENAME_CATEGORY, u'Rename Category', wx.EmptyString, wx.ITEM_NORMAL )
						add_item.SetBitmap( ctg.ui.util.get_project_image( 'outliner_objset_delete_16.png', as_bitmap = True ), wx.BITMAP_TYPE_ANY )
						self.AppendItem( add_item )

						add_item = wx.MenuItem( self, CMD_ID_DELETE_CATEGORY, u'Delete Category', wx.EmptyString, wx.ITEM_NORMAL )
						add_item.SetBitmap( ctg.ui.util.get_project_image( 'outliner_objset_delete_16.png', as_bitmap = True ), wx.BITMAP_TYPE_ANY )
						self.AppendItem( add_item )

					paste_item = wx.MenuItem( self, CMD_ID_PASTE_TRIGGERS_TO_CATEGORY, u'Paste Triggers to Category', wx.EmptyString, wx.ITEM_NORMAL )
					paste_item.SetBitmap( ctg.ui.util.get_project_image( 'outliner_objset_delete_16.png', as_bitmap = True ), wx.BITMAP_TYPE_ANY )
					self.AppendItem( paste_item )

				else:
					add_item = wx.MenuItem( self, CMD_ID_ADD_TRIGGER, u'Add Trigger', wx.EmptyString, wx.ITEM_NORMAL )
					add_item.SetBitmap( ctg.ui.util.get_project_image( 'outliner_objset_delete_16.png', as_bitmap = True ), wx.BITMAP_TYPE_ANY )
					self.AppendItem( add_item )

				self.AppendSeparator( )
			elif isinstance( self.item, Trigger_Timeline_Key ):

				delete_item = wx.MenuItem( self, CMD_ID_DELETE_SELECTED_TRIGGER, u'Delete Selected Trigger(s)', wx.EmptyString, wx.ITEM_NORMAL )
				delete_item.SetBitmap( ctg.ui.util.get_project_image( 'outliner_objset_delete_16.png', as_bitmap = True ), wx.BITMAP_TYPE_ANY )
				self.AppendItem( delete_item )


			if self.item and show_menu_options:
				category_names = self.view.get_all_category_items( )
				if category_names:
					move_to_menu = wx.Menu( )
					cat_names = category_names.keys( )
					cat_item  = self.item
					has_triggers = True

					if isinstance( self.item, Trigger_Timeline_Key ):
						cat_item = self.item.get_parent( ).get_parent( )
					else:
						if not self.item.is_clip_track( ):
							cat_item = self.item.get_parent( )

					if cat_item.is_clip_track( ):
						del cat_names[ cat_names.index( cat_item.get_name( ) ) ]

					if cat_names:
						for category_name in cat_names:
							item_id = wx.NewId()
							self.category_ids_dict[ item_id ] = category_name

							cat_menu_item = wx.MenuItem( self, item_id, category_name, wx.EmptyString, wx.ITEM_NORMAL )
							cat_menu_item.SetBitmap( ctg.ui.util.get_project_image( 'add_item_16.png', as_bitmap = True ), wx.BITMAP_TYPE_ANY )
							move_to_menu.AppendItem( cat_menu_item )

						self.AppendSubMenu( move_to_menu, 'Move Triggers to' )

				if isinstance( self.item, Trigger_Timeline_Track ):
					copy_item = wx.MenuItem( self, CMD_ID_COPY_TRIGGERS, u'Copy', wx.EmptyString, wx.ITEM_NORMAL )
					copy_item.SetBitmap( ctg.ui.util.get_project_image( 'outliner_objset_delete_16.png', as_bitmap = True ), wx.BITMAP_TYPE_ANY )
					self.AppendItem( copy_item )
				else:
					copy_item = wx.MenuItem( self, CMD_ID_COPY_SELECTED_TRIGGERS, u'Copy Selected Trigger(s)', wx.EmptyString, wx.ITEM_NORMAL )
					copy_item.SetBitmap( ctg.ui.util.get_project_image( 'outliner_objset_delete_16.png', as_bitmap = True ), wx.BITMAP_TYPE_ANY )
					self.AppendItem( copy_item )

		if show_menu_options:
			paste_item = wx.MenuItem( self, CMD_ID_PASTE_TRIGGERS, u'Paste', wx.EmptyString, wx.ITEM_NORMAL )
			paste_item.SetBitmap( ctg.ui.util.get_project_image( 'outliner_objset_delete_16.png', as_bitmap = True ), wx.BITMAP_TYPE_ANY )
			self.AppendItem( paste_item )
			paste_item.Enable( False )

			self.AppendSeparator( )

		if len( self.clipboard_data ) > 0 and show_menu_options:
			paste_item.Enable( True )


		if not self.item and show_menu_options:
			add_item = wx.MenuItem( self, CMD_ID_ADD_TRIGGER, u'Add Trigger', wx.EmptyString, wx.ITEM_NORMAL )
			add_item.SetBitmap( ctg.ui.util.get_project_image( 'outliner_objset_delete_16.png', as_bitmap = True ), wx.BITMAP_TYPE_ANY )
			self.AppendItem( add_item )

			add_item = wx.MenuItem( self, CMD_ID_ADD_TRIGGER_CATEGORY, u'Add Trigger Category', wx.EmptyString, wx.ITEM_NORMAL )
			add_item.SetBitmap( ctg.ui.util.get_project_image( 'outliner_objset_delete_16.png', as_bitmap = True ), wx.BITMAP_TYPE_ANY )
			self.AppendItem( add_item )
			self.AppendSeparator( )


		if self.GetMenuItemCount( ) > 0:
			self.SetTitle( "Triggers Menu" )


	def on_menu_clicked( self, event ):
		handled = super( Trigger_Timeline_Context_Menu, self ).on_menu_clicked( event )

		sender = event.GetId( )
		if sender == CMD_ID_ADD_TRIGGER_TO_CATEGORY:
			self.view.add_new_trigger( 'New Trigger', 0, 1, category= self.item.get_name( ) )

		elif sender == CMD_ID_RENAME_CATEGORY:
			self.view.rename_trigger_category( self.item )

		elif sender == CMD_ID_ADD_TRIGGER:
			self.view.add_new_trigger( 'New Trigger', 0, 1, category= '' )

		elif sender == CMD_ID_DELETE_CATEGORY:
			self.view.delete_trigger_category( self.item )

		elif sender == CMD_ID_DELETE_SELECTED_TRIGGER:
			self.view.on_delete_trigger( )

		elif sender in self.category_ids_dict.keys( ):
			self.view.move_triggers_to_category( self.item, self.category_ids_dict.get( sender ), refresh_view = True )

		elif sender == CMD_ID_ADD_TRIGGER_CATEGORY:
			self.view.add_trigger_category( )

		elif sender == CMD_ID_COPY_TRIGGERS:
			data = self.view.get_obj_data( self.item )
			if data:
				ctg.ae2.core.ae_common_operations.copy( data, ctg.ae2.ui.const.ANIMATION_TRIGGER )

		elif sender == CMD_ID_COPY_SELECTED_TRIGGERS:

			data = self.view.get_selected_triggers_data( )
			if data:
				ctg.ae2.core.ae_common_operations.copy( data, ctg.ae2.ui.const.ANIMATION_TRIGGER )

		elif sender == CMD_ID_PASTE_TRIGGERS:
			if self.clipboard_data:
				self.view.paste_triggers( self.clipboard_data )

		elif sender == CMD_ID_PASTE_TRIGGERS_TO_CATEGORY:
			if self.clipboard_data:
				self.view.paste_triggers( self.clipboard_data, category = self.item.get_name( ) )


		return handled


class Trigger_Timeline_Menu_Input( vlib.ui.timeline.input.Handler_Context_Menu ):

	def on_context_menu( self, event ):
		"""
		Event handler for Right Mouse Button Down. Determines the context based on where the mouse is and
		builds the appropriate context menu.

		* Arguments:
			* ``event``		The wx.EVT_RIGHT_DOWN event

		* Keyword Arguments:
			* ``None``

		* Returns:
			* ``None``

		* Author:
			* Andy Kelts, andy.kelts@dsvolition.com, 5/8/2014
		"""

		click_pos = event.GetPosition( )
		sel_man   = self.view.get_selection_manager( )

		self.on_release( event )
		item = sel_man.get_item_at_coord( self.view, click_pos )
		# If an item has not been clicked on, find which track has been clicked on
		if item is None:
			if hasattr( sel_man, 'get_track_at_coord' ):
				item = sel_man.get_track_at_coord( self.view, click_pos )

		if item is not None:
			if not item in sel_man.get_selection( ):
				sel_man.set_selection( self.view, [ item ] )

		menu = Trigger_Timeline_Context_Menu( self.view, item )
		self.view.PopupMenu( menu )
		menu.Destroy( )

		self.reset( )
		event.Skip( True )


class Trigger_Timeline_Label_Colunm_Handler( vlib.ui.timeline.input.Handler_Virtual_Buttons ):

	def setup_bindings( self ):
		self.Bind( wx.EVT_LEFT_DCLICK, self.on_left_double_click )
		super( Trigger_Timeline_Label_Colunm_Handler, self ).setup_bindings( )


	def on_left_down( self, event ):
		if not self.can_process_event( event ):
			event.Skip( True )
			return

		self.is_handling = True


	def can_process_event( self, event ):
		if self.view.get_active_editor( ):
			self.view.destroy_active_editor( )

		return super( Trigger_Timeline_Label_Colunm_Handler, self ).can_process_event( event )


	def on_left_double_click( self, event ):
		item     = self.view.get_selection_manager( ).get_item_at_coord( self.view, event.GetPosition( ) )
		buttons  = len( list( self.view.get_registered_item_buttons( ) ) )
		w_offset = ( buttons - 1 ) * 18

		if item and self.view.get_item_accessor( ).is_key_track( item ):
			accessor  = self.view.get_item_accessor( )
			rect      = wx.Rect( 0, self.view.column_header_height - 2, self.view.label_width, 1 )
			item_rect = self.view.get_rect_for_cell( item, accessor )

			editor_rect = wx.Rect( rect.x, item_rect.y, rect.width - w_offset, item_rect.height + 1 )
			editor_rect.Deflate( 1, 1 )

			trigger_name_editor = Editor_Type_Auto_Comp_Enum_Trigger_Name( self.view, self.view.get_item_accessor( ), item, editor_rect )
			trigger_name_editor.SetPosition( ( 1, editor_rect.y - 2 ) )
			trigger_name_editor.Show( )

			event.Skip( )

			return False

		else:
			if self.view.get_active_editor( ):
				wx.CallAfter( self.view.destroy_active_editor )

		event.Skip( )



ITEM_BUTTONS_ALL = [ \
   vlib.ui.timeline.track_tree.Item_Button_Expand( ),
   Item_Button_Add_Track( ),
   Item_Button_Delete_Track( )
]

class Trigger_Timeline_Track_Tree( vlib.ui.timeline.track_tree.Track_Tree ):
	def __init__( self, parent, id	        = wx.ID_ANY,
	              start_time			        = 0,
	              end_time				        = 5000,
	              ms_per_interval		        = 1000,
	              ms_per_frame			        = 25,
	              item_buttons               = ITEM_BUTTONS_ALL,
	              context_menu_class	        = Trigger_Timeline_Menu_Input,
	              renderer_class		        = vlib.ui.timeline.renderer.Timeline_Renderer,
	              selection_manager	        = Trigger_Timeline_Selection_Manager,
	              current_time_handler_class = Trigger_Timeline_Label_Colunm_Handler,
	              drag_handler_class         = Trigger_Selection_Move_Timeline_Object_Input,
	              label_accessor_class       = Trigger_Column_Accessor_Label,
	              track_accessor_class       = Trigger_Column_Accessor_Track,
	              *args, **kwargs ):

		self.track_tree = self

		self.display_mode				= vlib.ui.timeline.const.TIME_DISPLAY_SECONDS
		self.clip_length          = 5
		self.inter_val_increament = 0
		self.callback_string = 'animation_preview_pane_callbacks'
		vlib.ui.timeline.track_tree.Track_Tree.__init__( self, parent, id	        = id,
		                                                  start_time			        = start_time,
		                                                  end_time				        = end_time,
		                                                  ms_per_interval		        = ms_per_interval,
		                                                  ms_per_frame			        = ms_per_frame,
		                                                  item_buttons               = item_buttons,
		                                                  context_menu_class	        = context_menu_class,
		                                                  renderer_class		        = renderer_class,
		                                                  selection_manager	        = selection_manager,
		                                                  current_time_handler_class = current_time_handler_class,
		                                                  drag_handler_class         = drag_handler_class,
		                                                  label_accessor_class       = label_accessor_class,
		                                                  track_accessor_class       = track_accessor_class )

		self.new_categories = {}
		ctg.CALLBACK_SYSTEM.register_callback( 'track_tree_pane_callbacks', 'ae preview updated', self.update_time )
		self.Bind( wx.EVT_WINDOW_DESTROY, self._on_destroy )

		self.setup_default_values( )


	def _on_destroy( self, event ):
		if event.GetWindow( ) is self:
			ctg.CALLBACK_SYSTEM.unregister_callbacks( 'track_tree_pane_callbacks' )

		event.Skip( )


	def update_time( self, doc ):
		if not doc:
			return

		frame = doc.get_preview_clip_frame()
		self.set_time( int( self.get_time_at_frame( frame ) ) )
		self.Refresh( )


	# CONTROLS / INPUT
	def set_end_time( self, end_time ):
		self.end_time = end_time
		self.grid.set_range( self.grid.get_start( ), ( end_time, self.grid.get_end( )[ 1 ] ) )
		self.sequence_range.set_end( end_time )
		self.playback_range.set_end( end_time )
		self.reverse_range.set_end( end_time )


	def get_time_at_frame( self, frame ):
		m_seconds = ( float( frame ) / float( self.frames_per_second ) ) * 1000

		return m_seconds


	def convert_time_to_frame( self, time, rounded = False ):

		frame = float( time / 1000.0 ) * float( self.frames_per_second )
		if rounded:
			return int( round( frame ) )
		else:
			return frame


	def add_trigger( self ):
		doc = AnimationEditor.get_active_document( )

		if not doc:
			return

		recent_selected_clips = doc.selection_manager.get_recent_sel_clips( )
		successful = False

		if recent_selected_clips:
			if len( recent_selected_clips ) == 1:
				successful, uids = recent_selected_clips[0].add_animation_triggers()
		else:
			dlg = wx.MessageDialog( None, "No Animation Clip selected to add a Trigger to.", caption = 'Add Trigger', style = wx.OK | wx.ICON_INFORMATION )
			ctg.ui.dialogs.show_dialog_modal( dlg )
			dlg.Destroy( )

		if successful:
			wx.CallAfter( self.GetParent( ).GetParent( ).refresh_ui )
			wx.CallAfter( self.GetParent( ).GetParent( ).refresh_anim_properties_pane )


	def on_delete_trigger( self ):
		doc = AnimationEditor.get_active_document( )

		if not doc:
			return

		recent_selected_clips = doc.selection_manager.get_recent_sel_clips( )
		if recent_selected_clips:
			selected_triggers = self.get_triggers_from_selection( )

			if selected_triggers:
				dlg = wx.MessageDialog( self, ( "Are you sure you want to delete selected Triggers?" ),
					                                 'Delete Triggers', wx.OK | wx.CANCEL | wx.ICON_INFORMATION )

				if ctg.ui.dialogs.show_dialog_modal( dlg ) == wx.ID_OK:
					delete = self.delete_triggers( selected_triggers )
					if delete:
						wx.CallAfter( self.GetParent( ).GetParent( ).refresh_ui )
						wx.CallAfter( self.GetParent( ).GetParent( ).refresh_anim_properties_pane )

				dlg.Destroy()


	def add_new_trigger( self, name, start_frame, end_frame, category= None ):
		doc = AnimationEditor.get_active_document( )

		if not doc:
			return

		recent_selected_clips = doc.selection_manager.get_recent_sel_clips( )
		refresh_view = False

		if start_frame > self.clip_length:
			dlg = wx.MessageDialog( None, "Trigger start and end frames has to be\nwithin the range of clip length.", caption = 'Add Trigger', style = wx.OK | wx.ICON_INFORMATION )
			ctg.ui.dialogs.show_dialog_modal( dlg )
			dlg.Destroy( )

		else:

			if recent_selected_clips:
				if len( recent_selected_clips ) == 1:
					refresh_view, uids = recent_selected_clips[0].add_animation_triggers( name=name, category=category, start_frame = start_frame, end_frame = end_frame )

		if refresh_view:
			wx.CallAfter( self.GetParent( ).GetParent( ).refresh_ui )
			wx.CallAfter( self.GetParent( ).GetParent( ).refresh_anim_properties_pane )

		return refresh_view


	def setup_default_values( self ):
		doc	= AnimationEditor.get_active_document( )
		if not doc:
			return

		self.playing 							= PLAY_NORMAL_SPEED
		self.play_direction 					= FORWARD
		self.clip_playing_foward 			= False
		self.clip_playing_backward 		= False
		self.loop_anim_clip 					= True
		self.finish_playing					= False
		self.pop_up_menu						= None
		self.is_playing_reverse				= False
		self.is_playing_forward    		= False
		self.is_playing_half_speed			= False
		self.is_playing_quarter_speed    = False
		self.network_view_previewing     = False
		self.catalog_view_previewing     = False
		doc.preview_loop( True )


	def add_trigger_category( self ):
		doc = AnimationEditor.get_active_document( )
		if doc:
			recent_selected_clips = doc.selection_manager.get_recent_sel_clips( )
			if recent_selected_clips:
				cat_names = self.new_categories.get( recent_selected_clips[0].get_name( ) )
				if not cat_names:
					cat_names = [ ]

				dlg = wx.TextEntryDialog(
				   self, 'Add New Category',
				   'Add New Category', "New Category" )

				if dlg.ShowModal() == wx.ID_OK:
					val   = dlg.GetValue()

					if val != '' and val not in cat_names:
						cat_names.append( val )
						self.new_categories[ recent_selected_clips[0].get_name( ) ] = cat_names

					wx.CallAfter( self.GetParent( ).GetParent( ).refresh_ui )
					wx.CallAfter( self.GetParent( ).GetParent( ).refresh_anim_properties_pane )

				dlg.Destroy()


	def to_start( self ):
		doc	= AnimationEditor.get_active_document( )
		if not doc:
			return

		doc.set_preview_clip_frame( doc.preview_pane.play_back_slider.GetMin( ) )
		doc.preview_pane.update_slider_value( doc.preview_pane.play_back_slider.GetMin( ) )


	def play_trigger( self ):
		doc = AnimationEditor.get_active_document( )
		if not doc:
			return

		playing = doc.preview_pane.is_playing_forward

		doc.set_preview_playback_speed( 1.0 )
		self.play_direction 	= FORWARD
		self.playing 			= PLAY_NORMAL_SPEED

		if playing and self.is_playing_forward:
			self.pause_trigger( )
		else:
			self.stop_trigger( )
			doc.preview_play( )
			doc.preview_pane.update_play_flags( True, False, False, False )

		doc.preview_pane.update_play_button( )
		doc.preview_pane.check_callback_registration( )


	def pause_trigger( self ):
		doc = AnimationEditor.get_active_document( )

		doc.preivew_pane.pause_on_off( )
		doc.preview_pane.update_play_button( )


	def stop_trigger( self ):
		doc	= AnimationEditor.get_active_document( )
		if not doc:
			return

		frame = 0
		doc.preview_pane.update_play_flags( False, False, False, False )
		doc.preview_stop( )
		doc.preview_pane.finish_playing_clip( )
		doc.set_preview_clip_frame( frame )
		doc.preview_pane.update_slider_value( frame )
		doc.preview_pane.update_play_button( )


	def pause_trigger( self ):
		doc = AnimationEditor.get_active_document( )
		if not doc:
			return

		paused = doc.get_preview_paused( )
		if paused == True:
			doc.preview_pause( False )
			doc.preview_loop( self.loop_anim_clip )
		else:
			doc.preview_pause( True )


	def rewind_trigger( self ):
		doc = AnimationEditor.get_active_document( )
		doc.preview_pane.play_backward( )


	def fast_forward_trigger( self ):
		doc = AnimationEditor.get_active_document( )
		doc.preview_pane.play_quarter_speed( )


	def to_end( self ):
		doc	= AnimationEditor.get_active_document( )
		if not doc:
			return

		doc.set_preview_clip_frame( doc.preview_pane.play_back_slider.GetMax( ) )
		doc.preview_pane.update_slider_value( doc.preview_pane.play_back_slider.GetMax( ) )


	def zoom_step( self, zoom_out = True ):
		factor = ( 1.1, 1.1 ) if zoom_out else ( 0.9, 0.9 )
		self.track_tree.adjust_zoom( factor )


	def toggle_frames_visible( self ):
		self.set_frames_visible( self.display_mode == vlib.ui.timeline.const.TIME_DISPLAY_SECONDS )


	def toggle_curves_visible( self ):
		self.set_curves_visible( not self.view_curves )


	def get_all_category_items( self ):
		items = self.get_items( )
		category_dict = { }

		for item in items:
			if item.is_clip_track( ):
				category_dict[ item.get_name( ) ] = item

		return category_dict


	def delete_trigger_category( self, category_item ):
		doc = AnimationEditor.get_active_document( )
		if not doc:
			return

		success 	= False
		recent_selected_clips = doc.selection_manager.get_recent_sel_clips( )
		if recent_selected_clips:
			cat_names = self.new_categories.get( recent_selected_clips[0].get_name( ) )
			if not cat_names:
				cat_names = [ ]

			if category_item:
				dlg = wx.MessageDialog( self, ( "Are you sure you want to delete the category?" ),
								            'Delete Category', wx.OK | wx.CANCEL | wx.ICON_INFORMATION )

				if dlg.ShowModal() == wx.ID_OK:
					del cat_names[ cat_names.index( category_item.get_name( ) ) ]

					self.new_categories[ recent_selected_clips[0].get_name( ) ] = cat_names

					triggers = self.get_trigger_objs_from_item( category_item )
					if triggers:
						recent_selected_clips[0].set_triggers_category( triggers, '' )

					wx.CallAfter( self.GetParent( ).GetParent( ).refresh_ui )
					wx.CallAfter( self.GetParent( ).GetParent( ).refresh_anim_properties_pane )


				dlg.Destroy()



	def rename_trigger_category( self, category_item ):
		doc = AnimationEditor.get_active_document( )
		if not doc:
			return

		success 	= False
		recent_selected_clips = doc.selection_manager.get_recent_sel_clips( )
		if recent_selected_clips:
			cat_names = self.new_categories.get( recent_selected_clips[0].get_name( ) )
			if not cat_names:
				cat_names = [ ]

			if category_item:
				dlg = wx.TextEntryDialog(
								   self, 'Category Name',
								   'Rename Category', category_item.get_name( ) )

				if dlg.ShowModal() == wx.ID_OK:
					val      = dlg.GetValue()
					old_name = category_item.get_name( )

					del cat_names[ cat_names.index( old_name ) ]
					if val not in cat_names:
						cat_names.append( val )

					self.new_categories[ recent_selected_clips[0].get_name( ) ] = cat_names

					category_item.set_name( val )
					triggers = self.get_trigger_objs_from_item( category_item )
					if triggers:
						recent_selected_clips[0].set_triggers_category( triggers, val )

					wx.CallAfter( self.GetParent( ).GetParent( ).refresh_ui )

				dlg.Destroy()


	def get_trigger_objs_from_item( self, track ):
		trigger_objs = [ ]
		child_objs = track.get_children_recursive( )

		for child_obj in child_objs:
			if isinstance( child_obj, Trigger_Timeline_Key ):
				trigger_objs.append( child_obj.get_data_obj( ) )

		return trigger_objs


	def get_trigger_from_id( self, uid ):
		doc 	= AnimationEditor.get_active_document( )
		clips = doc.selection_manager.get_recent_sel_clips( )

		trigger = None
		if clips:
			trigger = clips[0].get_anim_trigger_from_uid( uid )

		return trigger


	def set_trigger_value( self, prop_id, value, trigger ):
		doc 	= AnimationEditor.get_active_document( )
		clips = doc.selection_manager.get_recent_sel_clips( )

		self.stop_trigger( )

		if clips:
			clip_length = clips[0].get_clip_length( )
			if trigger:
				clips[0].set_trigger_value( prop_id, value, trigger, ctg.ae2.ui.const.ANIMATION_TRIGGER )

				wx.CallAfter( self.GetParent( ).GetParent( ).refresh_ui )
				wx.CallAfter( self.GetParent( ).GetParent( ).refresh_anim_properties_pane )


	def move_triggers_to_category( self, item, category_name, refresh_view = False ):
		triggers = self.get_triggers_from_item( item )

		for trigger in triggers:
			self.set_trigger_value( 'category', category_name, trigger )

		if refresh_view and triggers:
			wx.CallAfter( self.GetParent( ).GetParent( ).refresh_ui )


	def get_triggers_from_item( self, item ):
		triggers = [ ]

		if isinstance( item, Trigger_Timeline_Key ):
			triggers.append( item.get_data_obj( ) )
		else:
			triggers = self.get_trigger_objs_from_item( item )

		return triggers

	def get_triggers_from_selection( self ):
		triggers = [ ]
		selected_items = self.get_selection_manager( ).get_selection( )

		for selected_item in selected_items:
			triggers.extend( self.get_triggers_from_item( selected_item ) )

		return triggers


	def get_selected_triggers_data( self ):

		doc = AnimationEditor.get_active_document()
		if not doc:
			return [ ]

		trigger_data = [ ]
		triggers     = self.get_triggers_from_selection( )
		clips        = doc.selection_manager.get_recent_sel_clips( )
		if not clips:
			return [ ]

		if len( clips ) == 1:
			trigger_data = clips[0].get_anim_triggers_data( triggers )

		return trigger_data



	def get_clip_length( self ):
		doc 	 = AnimationEditor.get_active_document( )
		if not doc:
			return 0

		clips  = doc.selection_manager.get_recent_sel_clips( )
		length = 0

		if clips:
			length = clips[0].get_length( )

		return length


	def delete_triggers( self, triggers ):
		doc 	  = AnimationEditor.get_active_document( )
		clips   = doc.selection_manager.get_recent_sel_clips( )
		deleted = False
		if triggers:
			if clips:
				deleted = clips[0].delete_triggers( triggers )

		return deleted


	def get_obj_data( self, item ):
		"""
		This method gets and returns a list of selected animation trigger data.

		*Arguments:*
			* <none>

		*Keyword Arguments:*
			* <none>

		*Returns:*
			* ``list`` -animation trigger data.

		*Author:*
			* Jon Logsdon, jon.logsdon@dsvolition.com
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		trigger_data = [ ]
		triggers     = self.get_triggers_from_item( item )
		clips        = doc.selection_manager.get_recent_sel_clips( )
		if not clips:
			return

		if len( clips ) == 1:
			trigger_data = clips[0].get_anim_triggers_data( triggers )

		return trigger_data


	def paste_triggers( self, data, category = None ):
		"""
		This method pastes animation triggers on clip property object, and refreshes
		animation properties pane.

		*Arguments:*
			* ``data`` -animation trigger to be set on pasted triggers.

		*Keyword Arguments:*
			* <none>

		*Returns:*
			* <none>

		*Author:*
			* Jon Logsdon, jon.logsdon@dsvolition.com
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		clips  = doc.selection_manager.get_recent_sel_clips( )
		if not clips:
			return

		success = False
		if len( clips ) == 1:
			anim_success, uids = clips[0].add_animation_triggers( len( data ) )
			if anim_success:
				triggers = clips[0].get_anim_triggers_from_uids( uids )
				success 	= clips[0].set_anim_trigger_data( triggers, data, category = category )

		if success:
			wx.CallAfter( self.GetParent( ).GetParent( ).refresh_ui )


class Timeline_Tree_Panel( vlib.ui.timeline.track_tree.Timeline_Panel ):


	def _init_controls( self,
	                    track_tree_class	= Trigger_Timeline_Track_Tree,
	                    start_time			= 0,
	                    end_time				= 5000,
	                    ms_per_interval		= 1000,
	                    ms_per_frame			= 25,
	                    context_menu_class	= Trigger_Timeline_Menu_Input,
	                    renderer_class     = Trigger_Tree_Renderer ):

		super( Timeline_Tree_Panel, self )._init_controls( track_tree_class,
		                                                   start_time,
		                                                   end_time,
		                                                   ms_per_interval,
		                                                   ms_per_frame,
		                                                   context_menu_class,
		                                                   renderer_class )


	def _init_commands( self ):
		self.cmds = [ ]
		doc = AnimationEditor.get_active_document( )

		command = vlib.ui.command.UI_Command(	id = 'anim.trigger.add_trigger',
			                                     title = 'Add Trigger',
			                                     description = 'Add a trigger to the selected category.',
			                                     icon_name = 'tod_timeline_add_32' )
		command.set_execute_method( self.track_tree.add_trigger )
		self.cmds.append( command )

		command = vlib.ui.command.UI_Command(	id = 'anim.trigger.delete_trigger',
			                                     title = 'Delete Trigger',
			                                     description = 'Delete selected triggers.',
			                                     icon_name = 'tod_timeline_delete_32' )
		command.set_execute_method( self.track_tree.on_delete_trigger )
		self.cmds.append( command )

		command = vlib.ui.command.UI_Command(	id = 'anim.trigger.add_category',
			                                     title = 'Add Trigger Category',
			                                     description = 'Add a new trigger category.',
			                                     icon_name = 'outliner_objset_add' )
		command.set_execute_method( self.track_tree.add_trigger_category )
		self.cmds.append( command )

		command = vlib.ui.command.UI_Command(   id = 'anim.trigger.go_to_start',
		                                        title = 'Go To Start',
		                                        description = 'Goes to the beginning of the timerange.',
		                                        icon_name = 'anim_editor_first_frame' )
		command.set_execute_method( self.track_tree.to_start )
		self.cmds.append( command )

		command = vlib.ui.command.UI_Command(   id = 'anim.trigger.rewind',
		                                        title = 'Rewind Trigger',
		                                        description = 'Rewind trigger',
		                                        icon_name = 'anim_editor_rewind' )
		command.set_execute_method( self.track_tree.rewind_trigger )
		self.cmds.append( command )

		command = vlib.ui.command.UI_Command(   id = 'anim.trigger.play',
	                                           title = 'Play Trigger',
	                                           description = 'Play trigger',
	                                           icon_name = 'anim_editor_play' )
		command.set_execute_method( self.track_tree.play_trigger )
		self.cmds.append( command )

		command = vlib.ui.command.UI_Command(   id = 'anim.trigger.pause',
			                                     title = 'Pause Trigger',
			                                     description = 'Pause trigger',
			                                     icon_name = 'anim_editor_pause' )
		command.set_execute_method( self.track_tree.pause_trigger )
		self.cmds.append( command )

		command = vlib.ui.command.UI_Command(   id = 'anim.trigger.stop',
		                                        title = 'Stop Trigger',
		                                        description = 'Stop trigger',
		                                        icon_name = 'anim_editor_stop' )
		command.set_execute_method( self.track_tree.stop_trigger )
		self.cmds.append( command )

		command = vlib.ui.command.UI_Command(   id = 'anim.trigger.fast_forward',
			                                     title = 'Fast Forward Trigger',
			                                     description = 'Fast Forward trigger',
			                                     icon_name = 'anim_editor_fastforward' )
		command.set_execute_method( self.track_tree.fast_forward_trigger )
		self.cmds.append( command )

		command = vlib.ui.command.UI_Command(   id = 'anim.trigger.go_to_end',
			                                     title = 'Go To End',
			                                     description = 'Goes to the end of the timerange',
			                                     icon_name = 'anim_editor_last_frame' )
		command.set_execute_method( self.track_tree.to_end )
		self.cmds.append( command )

		command = vlib.ui.command.UI_Command(   id = 'anim.trigger.zoom_in',
		                                        title = 'Zoom In',
		                                        description = 'Zooms in the time range',
		                                        icon_name = 'zoom_in' )
		command.set_execute_method( self.track_tree.zoom_step, zoom_out=False )
		self.cmds.append( command )

		command = vlib.ui.command.UI_Command(   id = 'anim.trigger.zoom_out',
			                                     title = 'Zoom Out',
			                                     description = 'Zooms out the time range',
			                                     icon_name = 'zoom_out' )
		command.set_execute_method( self.track_tree.zoom_step, zoom_out=True )
		self.cmds.append( command )

		command = vlib.ui.command.UI_Command(	id = 'anim.trigger.toggle_time_display',
			                                     title			= 'Toggle Time Display',
			                                     description	= 'Toggles the time range between frames and seconds',
			                                     icon_name	= vlib.ui.timeline.const.ICON_VIEW_FRAMES )
		command.set_execute_method( self.track_tree.toggle_frames_visible )
		command.set_checked_method( self.get_frames_visible )
		self.cmds.append( command )

		self.toolbar_buttons = self.toolbar_commands.add_commands( self.cmds, label = '', size = ( 32, 32 ), bitmap_margin = 0, border_margin = 0, bitmap_size = 16 )

		self.toolbar_commands.insert_separators( [ 0, 3, 10, 12, 13 ] )

		for button in self.toolbar_buttons:
			ctg.WX_APP.Bind( wx.EVT_IDLE, button._on_idle )


	def get_frames_visible( self ):
		return self.track_tree.display_mode == vlib.ui.timeline.const.TIME_DISPLAY_FRAMES



class Triggers_Timeline_Panel( wx.Panel ):
	PANE_ID 		= ctg.ae2.ui.const.PANE_ID_TRIGGERS
	PANE_TITLE 	= ctg.ae2.ui.const.PANE_TITLE_TRIGGERS_PANE

	def __init__( self, parent, id = wx.ID_ANY ):

		# initialize base class
		wx.Panel.__init__( self, parent, id = id, size=parent.GetSize( ) )

		self.parent           = parent
		self.tracks           = [ ]
		self.selected_objects = [ ]

		self.timeline_panel = Timeline_Tree_Panel( self, wx.ID_ANY, end_time = 600, ms_per_frame = 0.03, track_tree_class = Trigger_Timeline_Track_Tree )
		self.timeline_panel.track_tree.on_set_view_scale( )
		self.timeline_panel.set_frames_visible( True )
		self.timeline_panel.track_tree.set_use_hover_updating( False )

		#set track tree rendering colors
		set_colors( self.timeline_panel.track_tree )

		self.trigger_tracks = { }
		self.root_tracks    = { }
		self.sub_root_tracks = { }
		self.timeline_panel.track_tree.grid.set_range( ( 0, 0 ), ( 1, 1 ) )

		self.element_trigger_id_dict = { }
		self.main_sizer   = wx.BoxSizer( wx.VERTICAL )
		self.main_sizer.Add( self.timeline_panel, 1, wx.EXPAND )
		self.main_sizer.AddSpacer( 4 )
		self.SetSizer( self.main_sizer )

		self.refresh_ui( )


	def on_panel_resize( self, event ):
		self.timeline_panel.track_tree.on_set_view_scale( )

	def add_trigger_track( self, root_track, start, length, trigger_id, frame_range, name, start_frame, end_frame, trigger ):
		category = None
		if trigger.get_category( ) == '' or trigger.get_category( ) == 'Default':
			category = 'Default'
		else:
			category = trigger.get_category( )

		if root_track.get_children( ):
			for i in range( len( root_track.get_children( ) ) ):
				if category in str( root_track.get_children( )[i] ):
					key = root_track.get_children( )[i].add_key( time_val = start, length = length, value = frame_range, data_obj = trigger, path = [ name ] )
		else:
			key = root_track.add_key( time_val = start, length = length, value = frame_range, data_obj = trigger, path = [ name ] )


	def enable_ui( self ):
		doc = AnimationEditor.get_active_document( )

		enable = False

		if doc:
			recent_selected_clips = doc.selection_manager.get_recent_sel_clips( )
			if recent_selected_clips and recent_selected_clips[0].get_clip_length( ) > 0:
				enable = True


	def create_track_tree( self, category_names, clip_name, existing_items=None ):
		self.root_tracks = {}
		track = None
		clip_track = None

		tracks = [ ]

		if category_names:
			if not clip_track:
				clip_track = Trigger_Timeline_Track( self, name = clip_name )

			for category_name in category_names:
				track = Trigger_Timeline_Track( self, name = category_name )
				track._show_range = True
				track._show_clips = True

				if track not in tracks:
					tracks.append( track )

				self.root_tracks[ category_name ] = clip_track

			self.timeline_panel.track_tree.get_or_set_item_expanded( clip_track, state=True )

			if tracks:
				for track in tracks:
					track.parent_to( clip_track )
					self.timeline_panel.track_tree.get_or_set_item_expanded( track, state=True )

		self.timeline_panel.track_tree.set_item_collection( self.root_tracks.values( ), immediate = True, use_timer = False )
		self.timeline_panel.track_tree.populate_entries( )
		self.timeline_panel.track_tree.update_item_collection( use_timer = False )
		self.timeline_panel.track_tree.Refresh( )


	def delete_trigger( self, event ):
		doc = AnimationEditor.get_active_document( )
		if not doc:
			return

		success 		= False
		trigger_ids = [ ]
		recent_selected_clips = doc.selection_manager.get_recent_sel_clips( )
		if recent_selected_clips:
			trigger_ids = self.get_trigger_ids_from_elements( )
			if trigger_ids:
				success = recent_selected_clips[0].delete_triggers_by_uids( trigger_ids )

				if success:
					recent_selected_clips[0].selected_triggers = []
					self.refresh_ui( )
					self.refresh_anim_properties_pane( )

		if not recent_selected_clips or not trigger_ids:
			dlg = wx.MessageDialog( None, "No Triggers selected for delete.", caption = 'Delete Triggers', style = wx.OK | wx.ICON_INFORMATION )
			ctg.ui.dialogs.show_dialog_modal( dlg )
			dlg.Destroy( )

		if event:
			event.Skip( )


	@vlib.debug.Debug_Timing( 'refresh_trigger_timeline_ui', precision = 4 )
	def refresh_ui( self, refresh_trigger_prop = True ):

		doc 	= AnimationEditor.get_active_document( )
		clips = doc.selection_manager.get_recent_sel_clips( )
		was_playing = False
		playing = False

		if getattr( doc, 'preview_pane', None ):
			playing = doc.preview_pane.is_clip_playing( )

		if playing:
			was_playing = True
			doc.preview_pause( True )

		self.trigger_tracks.clear( )
		self.root_tracks.clear( )

		self.element_trigger_id_dict.clear( )

		all_trigger_names = list( doc.get_trigger_names() )

		if clips:
			trigger_names_list = [ ]
			#make sure  the default category is always there
			trigger_category_names = [ ]
			trigger_uids_list  = [ ]
			triggers           = self.get_triggers( clips[0] )
			clip_length        = clips[0].get_clip_length( )

			end_time = self.timeline_panel.track_tree.get_time_at_frame( clip_length )
			if clip_length == 0:
				end_time = self.timeline_panel.track_tree.get_time_at_frame( 1 )


			self.timeline_panel.track_tree.set_end_time( int( end_time ) )
			self.timeline_panel.track_tree.clip_length = clip_length

			if triggers:
				trigger_category_names = [ 'Default' ]

				for trigger in triggers:
					trigger_name = self.get_trigger_display_name( trigger )

					if trigger_name == '':
						clips[0].delete_triggers_by_uids( [ trigger.get_uid( )], mark_dirty = False )
						continue

					category_name = trigger.get_category( )

					if category_name not in [ None, '' ]:
						if category_name not in trigger_category_names:
							trigger_category_names.append( category_name )

					self.element_trigger_id_dict[ ( trigger.get_uid( ), trigger_name ) ] = [ trigger.get_frame( ), trigger.get_end_frame( ), trigger.get_category( ), trigger ]
					if trigger_name not in trigger_names_list:
						trigger_names_list.append( trigger_name )

					if trigger_name not in all_trigger_names:
						if isinstance( doc.selection_manager.get_selected_objects( ), ctg.ae2.core.data.Clip_Item ):
							comp_trig_list = [ ]
							compared_triggers = doc.selection_manager.get_selected_objects( ).get_anim_triggers( )
							for trig in compared_triggers:
								comp_trig_list.append( trig.get_name( ) )

							if trigger_name not in [ None, 'none', '', 'New Trigger']:
								if trigger_name not in comp_trig_list:
									doc.undoable_create_trigger_name( trigger_name )
									all_trigger_names.append( trigger_name )

					if trigger.get_uid( ) not in trigger_uids_list:
						trigger_uids_list.append( trigger.get_uid( ) )


			categories = self.timeline_panel.track_tree.new_categories.get( clips[0].get_name( ) )
			if categories:
				trigger_category_names.extend( categories )

			#this removes duplicates
			trigger_category_names = list( set( trigger_category_names ) )

			items = self.timeline_panel.track_tree.get_items( )

			#create category tracks
			self.create_track_tree( trigger_category_names, clips[0].get_name( ), existing_items=items )
			if trigger_names_list:

				for name in sorted( trigger_names_list ):
					trigger_track = self.trigger_tracks.get( name )

					for t_id in trigger_uids_list:
						value = self.element_trigger_id_dict.get( ( t_id, name ) )

						if value:
							start_time    = self.timeline_panel.track_tree.get_time_at_frame( value[0] )
							end_time      = self.timeline_panel.track_tree.get_time_at_frame( value[1] )
							clip_end_time = self.timeline_panel.track_tree.get_time_at_frame( clip_length )

							if start_time > end_time:
								clip_len = ( clip_end_time - start_time ) + end_time

							else:
								clip_len = end_time - start_time

							if value[0] == value[1]:
								clip_len = start_time + 10

							track = self.root_tracks.get( value[2] )
							if value[2] in [None, '']:
								track = self.root_tracks.get( "Default" )

							range_trigger = clips[0].get_anim_trigger_from_uid( t_id )
							trigger_start = clips[0].get_trigger_value( 'start_frame', range_trigger )
							trigger_end =	clips[0].get_trigger_value( 'end_frame', range_trigger )

							self.add_trigger_track( track, int( start_time ), int( clip_len ), t_id, '{0} - {1}'.format( trigger_start, trigger_end ), name, value[0], value[1], value[3] )

		if was_playing:
			self.timeline_panel.track_tree.play_trigger( )

		root_values = [ ]
		for val in self.root_tracks.values( ):
			if val not in root_values:
				root_values.append( val )

		self.timeline_panel.track_tree.set_item_collection( root_values, immediate = True, use_timer = False )
		self.timeline_panel.track_tree.populate_entries( )
		self.timeline_panel.track_tree.update_item_collection( use_timer = False )
		#self.timeline_panel.track_tree.Refresh( )

		#enable ui
		self.enable_ui( )


	def get_triggers( self, clip ):
		triggers = [ ]
		if clip:
			triggers = clip.get_anim_triggers( )

		return triggers


	def get_trigger_display_name( self, trigger ):
		trigger_name = None

		if trigger:
			trigger_name = trigger.get_name( )

		return trigger_name


	def get_trigger_by_uid( self, uid, clip ):
		trigger = None

		if clip:
			trigger = clip.get_anim_trigger_from_uid( uid )

		return trigger


	def refresh_anim_properties_pane( self ):
		doc = AnimationEditor.get_active_document( )
		selected_objs  = doc.selection_manager.get_selected_objects( )

		if selected_objs:
			if isinstance( selected_objs[0], ctg.ae2.core.data.Clip_Item  ):
				doc.animation_properties_pane.refresh_ui( )


