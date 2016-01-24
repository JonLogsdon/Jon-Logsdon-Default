import wx
import vlib.ui.lister_lib.renderer
import GUILib

import ctg
import ctg.prefs
import ctg.ae2.ui.const
import AnimationEditor

def scale_color( color, scale = 1.0 ):
	# Scale and clamped to 0-255
	out_color = [ max( 0, min( int( float( c ) * scale ), 255 ) ) for c in color ]

	return wx.Colour( *out_color )


class Color_Set( object ):
	def __init__( self, pref_string_root, display_string = u'', ):

		self.pref_string_root = pref_string_root
		self.display_string = display_string

		self.color_defaults_dict = {}
		self.color_name_dict = {}


	def _get_color_id( self, ):
		''' Override this Method '''
		pass


	def _get_color_pref_string( self, color_id ):
		pref_string = '{0}_{1}'.format( self.pref_string_root, color_id )
		return pref_string


	def get_color_dict( self ):
		colors_dict = { }

		for color_id in self.color_defaults_dict.keys( ):
			color_pref = None
			pref_string = 'theme.ae_' + self._get_color_pref_string( color_id )

			# get the default value
			color_tuple = tuple( self.color_defaults_dict[ color_id ] )

			# get the color from the user prefs
			try:
				color_pref = ctg.prefs.user[ pref_string ]
			except KeyError:
				pass

			if color_pref:
				color_tuple = tuple( color_pref )

			colors_dict[ color_id ] = ( wx.Colour( *color_tuple ), self.color_name_dict[ color_id ] )

		return colors_dict


	def set_color_by_id( self, color, color_id ):
		pref_string = 'theme.ae_' + self._get_color_pref_string( color_id )
		ctg.prefs.user[ pref_string ] = list( color )


	def get_color( self ):
		''' Override this Method '''
		pass


	def set_color( self ):
		''' Override this Method '''
		pass



class Grid_Colors( Color_Set ):
	def __init__( self, pref_string_root, display_string = u'',
	              grid_color_axis		= wx.Colour( 0, 235, 0 ),
	              grid_color_major	= wx.Colour( 0, 0, 235 ),
	              grid_color_minor	= wx.Colour( 235, 0, 0 ),
		           ):

		Color_Set.__init__( self, pref_string_root, display_string )

		self.color_defaults_dict = { \
			'gridlines_color_axis'	: grid_color_axis,
			'gridlines_color_major'	: grid_color_major,
			'gridlines_color_minor'	: grid_color_minor,
		}

		self.color_name_dict = { \
			'gridlines_color_axis'	: 'Grid Color Axis',
			'gridlines_color_major'	: 'Grid Color Major',
		   'gridlines_color_minor'	: 'Grid Color Minor',
		}


	def _get_prefs( self ):
		return ctg.prefs.user


	def _get_color_pref_string( self, color_id ):
		pref_string = '{0}'.format( color_id )

		return pref_string


	def _get_color_id( self, axis, major, minor ):
		if axis:
			color_id = 'gridlines_color_axis'
		elif major:
			color_id = 'gridlines_color_major'
		elif minor:
			color_id = 'gridlines_color_minor'

		return color_id


	def get_color( self, axis = False, major = False, minor = False ):
		# Get the Color ID
		color_id = self._get_color_id( axis = axis, major = major, minor = minor )
		pref_string = "theme.ae_grid_" + self._get_color_pref_string( color_id )
		color_pref = None

		# Lookup color ( setting default if necessary )
		color_tuple = tuple( self.color_defaults_dict[ color_id ] )

		# get the color from the user prefs
		try:
			color_pref = ctg.prefs.user[ pref_string ]
		except KeyError:
			pass

		if color_pref:
			color_tuple = tuple( color_pref )

		color_wx = wx.Colour( *color_tuple )

		return color_wx


	def set_color_by_id( self, color, color_id ):
		pref_string = "theme.ae_grid_" + self._get_color_pref_string( color_id )
		ctg.prefs.user[ pref_string ] = list( color )


	def set_color( self, color, axis, major, minor ):
		color_id = self._get_color_id( axis, major, minor )

		self.set_color_by_id( color, color_id )



class Preload_Color( Color_Set ):
	def __init__( self, pref_string_root, display_string = u'',
		           clip_loaded 		= wx.Colour( 0, 0, 200 ),
		           clip_unloaded	= wx.Colour( 100, 100, 100 ),
		           ):

		Color_Set.__init__( self, pref_string_root, display_string )

		self.color_defaults_dict = { \
			'clip_loaded'		: clip_loaded,
			'clip_unloaded'	: clip_unloaded,
		}

		self.color_name_dict = { \
			'clip_loaded'		: 'Clip Loaded',
			'clip_unloaded'	: 'Clip Unloaded',
		}


	def _get_color_id( self, loaded ):
		if loaded:
			color_id = 'clip_loaded'
		else:
			color_id = 'clip_unloaded'

		return color_id


	def get_color( self, loaded = False ):
		# Get the color id
		color_id = self._get_color_id( loaded = loaded )
		pref_string = "theme.ae_preload_" + self._get_color_pref_string( color_id )
		color_pref = None

		# Lookup color ( setting default if necessary )
		color_tuple = list( self.color_defaults_dict[ color_id ] )

		# get the color from the user prefs
		try:
			color_pref = ctg.prefs.user[ pref_string ]
		except KeyError:
			pass

		if color_pref:
			color_tuple = tuple( color_pref )

		color_wx = wx.Colour( *color_tuple )

		return color_wx


	def set_color( self, color, loaded ):
		color_id = self._get_color_id( loaded )

		self.set_color_by_id( color, color_id )



class Node_Color_Set( Color_Set ):
	def __init__( self, pref_string_root, display_string = u'',
		           selected_even 		= wx.Colour( 255, 216, 0 ),
		           selected_odd			= wx.Colour( 255, 216, 0 ),
		           selected_text		= wx.Colour( 0, 0, 0 ),
		           unselected_even		= wx.Colour( 150, 150, 150 ),
		           unselected_odd		= wx.Colour( 135, 135, 135 ),
		           unselected_text		= wx.Colour( 0, 0, 0 ),
		           border_selected 	= wx.Colour( 0, 0, 0 ),
		           border_unselected	= wx.Colour( 0, 0, 0 ),
		           #loaded				= wx.Colour( 0, 245, 0 ),
		           #unloaded				= wx.Colour( 155, 155, 155 )
	              ):

		Color_Set.__init__( self, pref_string_root, display_string )

		self.color_defaults_dict = { \
			'selected_even'		: selected_even,
			'selected_odd'			: selected_odd,
			'selected_text'		: selected_text,
			'unselected_even'		: unselected_even,
			'unselected_odd'		: unselected_odd,
			'unselected_text'		: unselected_text,
			'border_selected'		: border_selected,
			'border_unselected'	: border_unselected,
			#'loaded'				: loaded,
			#'unloaded'				: unloaded,
		}

		self.color_name_dict = { \
			'selected_even'		: 'Selected Even',
			'selected_odd'			: 'Selected Odd',
			'selected_text'		: 'Selected Text',
			'unselected_even'		: 'Unselected Even',
			'unselected_odd'		: 'Unselected Odd',
			'unselected_text'		: 'Unselected Text',
			'border_selected'		: 'Border Selected',
			'border_unselected'	: 'Border Unselected',
			#'loaded'				: 'Loaded',
			#'unloaded'				: 'Unloaded',
		}


	def _get_color_id( self, selected, even = True, text = False, border = False ):
		color_id = None

		#if loaded:
			#color_id = 'loaded'
		#elif unloaded:
			#color_id = 'unloaded'

		if not color_id:
			if selected:
				if even:
					color_id = 'selected_even'
				else:
					color_id = 'selected_odd'

				if text:
					color_id = 'selected_text'

				if border:
					color_id = 'border_selected'
			else:
				if even:
					color_id = 'unselected_even'
				else:
					color_id = 'unselected_odd'

				if text:
					color_id = 'unselected_text'

				if border:
					color_id = 'border_unselected'

		return color_id


	def get_color( self, selected, even = True, text = False, border = False, ):
		# Get the color id
		color_id = self._get_color_id( selected, even, text = text, border = border, )
		pref_string = "theme.ae_" + self._get_color_pref_string( color_id )
		color_pref = None

		# Lookup color ( setting default if necessary )
		color_tuple = list( self.color_defaults_dict[ color_id ] )

		# get the color from the user prefs
		try:
			color_pref = ctg.prefs.user[ pref_string ]
		except KeyError:
			pass

		if color_pref:
			color_tuple = tuple( color_pref )

		color_wx = wx.Colour( *color_tuple )

		return color_wx


	def set_color( self, color, selected, even = True, text = False, border = False, ):
		color_id = self._get_color_id( selected, even, text = text, border = border, )
		self.set_color_by_id( color, color_id )


	def get_text_color( self, selected ):
		return self.get_color( selected, text = True )


	def set_text_color( self, selected ):
		self.set_color( color, selected, text = True )


	def get_style( self, selected, text = False ):
		style = wx.Font( pointSize = 9,
		                 family = wx.FONTFAMILY_DEFAULT,
		                 style = wx.FONTSTYLE_NORMAL,
		                 weight = wx.FONTWEIGHT_NORMAL,
		                 underline = False,
		                 face = u'Segoe UI',
		                 encoding = wx.FONTENCODING_SYSTEM )
		if selected:
			style = wx.Font( pointSize = 9,
		                 family = wx.FONTFAMILY_DEFAULT,
		                 style = wx.FONTSTYLE_NORMAL,
		                 weight = wx.FONTWEIGHT_BOLD,
		                 underline = False,
		                 face = u'Segoe UI',
		                 encoding = wx.FONTENCODING_SYSTEM )

		return style


	def set_style( self, style, selected, text = False ):
		pass


	def get_text_style( self, selected ):
		return self.get_style( selected, text = True )


	def set_text_style( self, selected ):
		self.set_style( style, selected, text = True )



class Default_Renderer( vlib.ui.lister_lib.renderer.Lister_Renderer ):
	def __init__( self, grid ):
		vlib.ui.lister_lib.renderer.Lister_Renderer.__init__( self, grid )

		self._show_child_count 			= False
		self._label_indent_depth 		= 1
		self._show_active_column		= False
		self._color_tree_connections  = wx.Colour( 68, 68, 68 )

		# Flat styles
		self._color_bg_even				= wx.Colour( 150, 150, 150 )
		self._color_bg_odd 				= wx.Colour( 135, 135, 135 )
		self._color_bg_even_sel			= wx.Colour( 50, 165, 255 )
		self._color_bg_odd_sel			= wx.Colour( 40, 155, 245 )
		self._color_cell_border 		= wx.Colour( 219, 219, 219 )
		self._color_column_border_sel = wx.Colour( 255, 162, 0 )

		# Gradient style
		self._color_bg_grad_top			= wx.Colour( 133, 212, 78 )
		self._color_bg_grad_bottom		= wx.Colour( 95, 172, 42 )
		self._color_stroke_grad			= wx.Colour( 51, 92, 23 )
		self._color_stroke_grad_inner	= wx.Colour( 122, 208, 62 )
		self._color_bg_even_grad		= self._color_bg_even
		self._color_bg_odd_grad 		= self._color_bg_odd

		# Tree metrics
		#self._tree_icon_spacing		= 18
		#self._tree_icon_size			= 16
		#self._tree_margin_left			= 4
		#self._tree_row_size				= self._tree_icon_spacing + 1


	def get_text_color( self, grid, node, column_object, is_selected ):
		color = wx.Colour( 0, 0, 0 )

		if hasattr( node, 'get_render_colors' ):
			node_color_set = node.get_render_colors( column_object )

			color	= node_color_set.get_text_color( is_selected )

		return color


	def get_text_style( self, grid, node, column_object, is_selected ):
		style = wx.Font( pointSize = 9,
		                 family = wx.FONTFAMILY_DEFAULT,
		                 style = wx.FONTSTYLE_NORMAL,
		                 weight = wx.FONTWEIGHT_NORMAL,
		                 underline = False,
		                 face = u'Segoe UI',
		                 encoding = wx.FONTENCODING_SYSTEM )

		if is_selected:
			if hasattr( node, 'get_render_colors' ):
				node_color_set = node.get_render_colors( column_object )
				valid_column_ids = [ 'tag_assoc_tag', 'tag_assoc_clip' ]
				column_string_dict = { 'NODE_TYPE_TAG_STATE'	: 'tag_assoc_tag',
					                    'NODE_TYPE_TAG_ACTION': 'tag_assoc_tag',
					                    'NODE_TYPE_ANIM_CLIP'	: 'tag_assoc_clip' }


				if column_object.id_string in valid_column_ids:
					doc = AnimationEditor.get_active_document( )
					if doc and ( doc.selection_manager.recent_sel_tag_associations_col == column_object.id_string ):
						style = node_color_set.get_text_style( is_selected )

		return style


	def draw_tree_connections( self, grid, dc, rect, row, col, is_selected = False ):
		node = grid.get_row_as_node( row )

		if hasattr( grid, 'show_tree_connections' ):
			if node:
				node_depth 		= node.get_depth( )
				icon_spacing	= self.get_tree_icon_spacing( )
				tree_margin 	= self.get_tree_margin_left( )
				pen_lines 		= wx.Pen( self.get_tree_connections_color( ), style = wx.PENSTYLE_DOT )

				top_point 		= wx.Point( *rect.TopLeft )
				bottom_point	= wx.Point( *rect.BottomLeft )
				offset = ( icon_spacing + tree_margin ) * 0.5
				top_point.x += offset
				top_point.y += 2
				bottom_point.x += offset

				last_node = False

				sibling = node.get_next_sibling( )
				has_sibling = bool( sibling )

				if not has_sibling or ( node_depth > sibling.node_depth ):
					last_node = True

				depth_parent_node = node.get_parent( )

				line_depths = range( node_depth + 1 )

				# Draw a vertical line for each depth level. Additionally drawing a
				# horizontal line for same level siblings.
				for i in line_depths:
					dc.SetPen( pen_lines )

					center = ( bottom_point.y - top_point.y ) * 0.5
					new_bottom = top_point.y + center

					depth_parent_node = node

					for n in range( len( line_depths ) - i - 1 ):
						if depth_parent_node:
							depth_parent_node = depth_parent_node.get_parent( )

					if ( i == node_depth ) and last_node:
						# draw a l-shape to indicate the last item in the tree
						dc.DrawLine( top_point.x, top_point.y, bottom_point.x, new_bottom )

					elif ( i == node_depth ) and has_sibling and node_depth == sibling.get_depth( ):
						dc.DrawLine( top_point.x, top_point.y, bottom_point.x, bottom_point.y )

					elif depth_parent_node and ( i == depth_parent_node.get_depth( ) ) and \
						  depth_parent_node.get_next_sibling( ) and \
						  ( i == depth_parent_node.get_next_sibling( ).get_depth( ) ):
						dc.DrawLine( top_point.x, top_point.y, bottom_point.x, bottom_point.y )

					if node_depth == i:
						dc.DrawLine( top_point.x, new_bottom, bottom_point.x + ( icon_spacing * 0.5 ), new_bottom )

					top_point.x += icon_spacing
					bottom_point.x += icon_spacing


	def draw_background( self, grid, dc, rect, row, col, is_selected, flat_style = False ):

		# Rect gets modified, so make a copy of it
		rect = wx.Rect( rect.x, rect.y, rect.width, rect.height )

		node = grid.get_row_as_node( row )
		column_collection = grid.get_column_collection( )
		column_object = column_collection.column_order[ col ]

		# Magic number for bumping the selection draw caps out of the clipping region
		offset_buffer = 10

		if hasattr( node, 'get_render_colors' ):

			# if this is the asset manager override the node colors for all node types
			if grid.get_pane_callback_id( ) is ctg.ae2.ui.const.PANE_LISTENER_ASSET_MANAGER_CALLBACK_ID:
				node_color_set = ctg.ae2.ui.const.NODE_COLORS_ASSET_MANAGER
			else:
				node_color_set = node.get_render_colors( column_object )

			is_even = ( row%2 == 0 )

			bg_color 							= node_color_set.get_color( False, is_even )
			color 								= node_color_set.get_color( is_selected, is_even )
			color_bg_top 						= color
			color_bg_bottom 					= scale_color( color, 0.7 )
			color_stroke_inner 				= scale_color( color, 0.9 )
			color_stroke_outer 				= scale_color( color, 0.4 )
			self._color_cell_border 		= node_color_set.get_color( is_selected, is_even, border = True )
			self._color_column_border_sel = node_color_set.get_color( is_selected, is_even, border = True )

		else:
			bg_color 				= self.get_background_color_for_row( row, is_selected = is_selected, flat_style = flat_style )
			color_bg_top 			= self._color_bg_grad_top
			color_bg_bottom 		= self._color_bg_grad_bottom
			color_stroke_inner 	= self._color_stroke_grad_inner
			color_stroke_outer 	= self._color_stroke_grad


		dc.SetBrush( wx.Brush( bg_color, wx.SOLID ) )

		if flat_style:
			dc.SetPen( wx.TRANSPARENT_PEN )
			dc.DrawRectangleRect( rect )

		else:
			dc.DestroyClippingRegion( )
			dc.SetClippingRegion( *rect )

			# Change rect a bit so we don't have doubled borders
			rect.x -= 1
			rect.width += 1

			bg_rect = wx.Rect( *rect )
			bg_rect.y -= 1
			bg_rect.height += 1

			if grid.lister_style == vlib.ui.lister_lib.const.STYLE_TREE:
				if hasattr( grid, 'show_tree_connections' ):
					bg_rect.Inflate( 1, 0 )

			border_pen = wx.Pen( self.get_border_color( ), 1 )

			dc.SetPen( border_pen )
			dc.DrawRectangleRect( bg_rect )

			if is_selected == True:
				draw_divider = False

				# Make the selection capsule look correct if it extends multiple columns
				rect_grad = wx.Rect( *rect )

				if col == 0:
					if grid.GetNumberCols( ) > 1:
						# Send capsule right side beyond clipping region
						rect_grad.width += offset_buffer
						draw_divider = True
					else:
						# Only column
						if grid.GetScrollThumb( 1 ):
							rect_grad.width -= wx.SystemSettings.GetMetric( wx.SYS_VTHUMB_Y ) + 2 # Remove the 2 pixel buffer problem
				else:
					if col == ( grid.GetNumberCols( ) - 1 ):
						# Last column, bump left side
						rect_grad.x -= offset_buffer
						rect_grad.width += offset_buffer
					else:
						# Middle columns
						rect_grad.Inflate( offset_buffer, 0 )
						draw_divider = True

				rect_grad.Deflate( 2, 2 )

				dc.GradientFillLinear( rect_grad, color_bg_top, color_bg_bottom, wx.DOWN )

				dc.SetBrush( wx.TRANSPARENT_BRUSH )

				# Draw stroke
				stroke_pen_inner = wx.Pen( color_stroke_inner, 1 )
				stroke_pen_inner.SetJoin( wx.JOIN_MITER )

				dc.SetPen( stroke_pen_inner )
				rect_grad.Inflate( 1, 1 )
				dc.DrawRoundedRectangleRect( rect_grad, 2 )

				stroke_pen = wx.Pen( color_stroke_outer, 1.5 )
				stroke_pen.SetJoin( wx.JOIN_MITER )

				dc.SetPen( stroke_pen )
				rect_grad.Inflate( 1, 1 )
				dc.DrawRoundedRectangleRect( rect_grad, 3 )

				if draw_divider:
					dc.SetPen( wx.Pen( scale_color( color_bg_top, 1.1 ), 1 ) )
					rect.Deflate( 0, 1 )
					t_pt = rect.GetTopRight( )
					b_pt = rect.GetBottomRight( )
					dc.DrawLine( t_pt.x, t_pt.y, b_pt.x, b_pt.y )

			dc.DestroyClippingRegion( )



#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
## Boolean Bullet Editor
#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
class Grig_Image_Renderer( wx.grid.PyGridCellRenderer ):
	def __init__(self, ):
		wx.grid.PyGridCellRenderer.__init__(self)
		self.bmp_error 			= ctg.ui.util.get_project_image( "outliner_no_export_16.png", as_bitmap = True )
		self.bmp_blendtree 		= ctg.ui.util.get_project_image( "blendtree_16.png", as_bitmap = True )
		self.bmp_statemachine 	= ctg.ui.util.get_project_image( "statemachine_16.png", as_bitmap = True )

	def Draw( self, grid, attr, dc, rect, row, col, isSelected ):

		# Get the column_collection
		column_collection = grid.get_column_collection( )

		# Draw Background
		renderer = grid.get_renderer( )
		renderer.draw_background( grid, dc, rect, row, col, isSelected )

		# Draw Column Highlight
		column_object = column_collection.column_order[ col ]

		# Get the node
		node = grid.get_row_as_node( row )
		if node.repair( ):
			# This node was in need of repair and was successfully repaired
			pass

		obj = node.get_data_obj( )
		obj_val = column_object.get_value( node )
		obj_locked = grid.is_node_read_only( node )

		isSortColumn = ( column_object == column_collection.sort_column )

		# set the proper bitmap
		bitmap = None

		# if the object is a state machine or blendtree set the appropriate icon
		doc = AnimationEditor.get_active_document( )
		if doc:
			if node.is_clip_valid:
				clip_name = obj.get_tag( ).get_clip_name( )
				if clip_name:
					if doc.is_blend_tree( clip_name ):
						bitmap = self.bmp_blendtree
					elif doc.is_state_machine( clip_name ):
						bitmap = self.bmp_statemachine

		#clip_name = obj.get_tag( ).get_clip_name( )
		#if clip_name:
			## get the name lists
			#if clip_name.endswith( ' sm' ):
				#bitmap = self.bmp_statemachine
			#elif clip_name.endswith( ' bt' ):
				#bitmap = self.bmp_blendtree

		# see if the object has an error if it does override the icon with the error
		if not node.is_clip_valid or not node.is_tag_valid:
			bitmap = self.bmp_error

		if bitmap:
			image = wx.MemoryDC( )
			image.SelectObject( bitmap )

		# set the bullet color
		if obj_val == True:
			color = wx.GREEN
		else:
			color = wx.LIGHT_GREY

		# set the colors
		dc.SetBrush( wx.Brush( wx.GREEN ) )
		dc.SetPen( wx.BLACK_PEN )

		#dc.DrawRectangleRect( rect )

		# copy the image but only to the size of the grid cell
		if bitmap:
			width, height = bitmap.GetWidth(), bitmap.GetHeight()

			if width > rect.width-2:
				width = rect.width-2

			if height > rect.height-2:
				height = rect.height-2

			dc.Blit(rect.x+6, rect.y+3, width, height, image, 0, 0, wx.COPY, True)


	def GetBestSize( self, grid, attr, dc, row, col ):
		# When getting width we want to get widest -- Column header VS defined cell width (in this case checkbox width w/ even padding either side (13px * 3))
		dc.SetFont( grid.GetLabelFont( ) )
		header_width = dc.GetTextExtent( grid.GetColLabelValue( col ) )[ 0 ] + 10
		return wx.Size( max( [ ( 13 * 3 ), header_width ] ), grid.GetRowSize( row ) )


	def Clone(self):
		return Grig_Image_Renderer()


#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
## Boolean Bullet Editor
#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
class Bullet_Bool_Renderer( wx.grid.PyGridCellRenderer ):
	def __init__(self, ):
		wx.grid.PyGridCellRenderer.__init__(self)
		self.set_colors( )


	def set_colors( self ):
		# set the preload button colors
		self.color_set = ctg.ae2.ui.const.NODE_COLORS_TYPE_DICT.get( ctg.ae2.ui.const.PRELOAD_BUTTON )
		self.loaded		= self.color_set.get_color( True )
		self.unloaded	= self.color_set.get_color( False )


	def Draw( self, grid, attr, dc, rect, row, col, isSelected ):
		renderer = grid.get_renderer( )
		column_collection = grid.get_column_collection( )

		# Draw Background
		renderer.draw_background( grid, dc, rect, row, col, isSelected )

		# Draw Column Highlight
		column_object = column_collection.column_order[ col ]

		node = grid.get_row_as_node( row )

		if node.repair( ):
			# This node was in need of repair and was successfully repaired
			pass

		obj = node.get_data_obj( )
		obj_val = column_object.get_value( node )

		#obj_locked = ( row in grid.locked_objects )
		obj_locked = grid.is_node_read_only( node )

		isSortColumn = ( column_object == column_collection.sort_column )

		# set the bullet color
		# moved the rest to the node
		if obj_val:
			color = self.loaded
		else:
			color = self.unloaded

		dc.SetBrush( wx.Brush( color ) )
		dc.SetPen( wx.BLACK_PEN )
		x, y = ((rect.left + rect.right) / 2.0, (rect.top + rect.bottom ) / 2.0 ) #make this a float if you're using more fancy classes over DC

		dc.DrawCircle( x, y, 6 )


	def SetSize(self, rect):
		"""
		Called to position/size the edit control within the cell rectangle.
		If you don't fill the cell (the rect) then be sure to override
		PaintBackground and do something meaningful there.
		"""
		self._tc.SetDimensions(rect.x, rect.y, rect.width+2, rect.height+2,
                               wx.SIZE_ALLOW_MINUS_ONE)


	def GetBestSize( self, grid, attr, dc, row, col ):
		# When getting width we want to get widest -- Column header VS defined cell width (in this case checkbox width w/ even padding either side (13px * 3))
		dc.SetFont( grid.GetLabelFont( ) )
		header_width = dc.GetTextExtent( grid.GetColLabelValue( col ) )[ 0 ] + 10
		return wx.Size( max( [ ( 13 * 3 ), header_width ] ), grid.GetRowSize( row ) )


	def Clone(self):
		return Bullet_Bool_Renderer()