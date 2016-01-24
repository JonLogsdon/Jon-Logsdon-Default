
import wx
import AnimationEditor
import vlib.ui
import ctg.ui.panel
import ctg.ae2.core
import vlib.ui.node_graph.node
import ctg.ui.bitmaps

import ctg.ae2.ui.panes.property_panels.animation_triggers
import ctg.ae2.ui.panes.property_panels.animation_set_panel
import ctg.ae2.ui.panes.property_panels.animation_group_panel
import ctg.ae2.ui.panes.property_panels.control_filter_panel
import ctg.ae2.ui.panes.property_panels.control_parameter_panel
import ctg.ae2.ui.panes.property_panels.tag_association_panel
import ctg.ae2.ui.panes.property_panels.graph_node_panel
import ctg.ae2.ui.panes.property_panels.rig_bones_panel
import ctg.ae2.ui.panes.property_panels.animation_modifier_panel

import ctg.ae2.node_graph.ae_node
import ctg.ae2.node_graph.ae_blend_tree_nodes
import ctg.ae2.node_graph.ae_state_machine_nodes

import inspect


class Properties_Pane( wx.Panel ):
	PANE_ID 		= ctg.ae2.ui.const.PANE_ID_PROPERTIES_PANE
	PANE_TITLE 	= ctg.ae2.ui.const.PANE_TITLE_PROPERTIES_PANE

	def __init__( self, parent, size = (-1, -1 ) ):
		wx.Panel.__init__( self, parent, size=size )

		#self.SetDoubleBuffered( True )

		self.folding_panes_dict 		= { }
		self.prop_panes_dict 			= { }
		self.child_prop_panes_dict 	= { }
		self.fold_pane_to_show  		= [ ]
		self.fold_pane_to_hide 			= [ ]
		self.last_shown_panes 			= [ ]
		self.prop_panes_to_show       = [ ]
		self.sel_obj_name 				= ''
		self.fold_pane_names_dict     = { }

		#main pane sizer
		main_sizer = wx.BoxSizer( wx.VERTICAL )
		self.name_inner_sizer = wx.BoxSizer( wx.HORIZONTAL )

		#folding panels images
		self.fp_images = wx.ImageList( 16, 16 )
		expanded = vlib.image.cache.load( ctg.ui.bitmaps.STR_BMP_EXPANDED_ICON_16 )
		self.fp_images.Add( expanded.get_wx_bitmap( ) )

		collapsed = vlib.image.cache.load( ctg.ui.bitmaps.STR_BMP_COLLAPSED_ICON_16 )
		self.fp_images.Add( collapsed.get_wx_bitmap( ) )

		#folding panels style setup
		self.fp_style = wx.lib.agw.foldpanelbar.CaptionBarStyle( )
		self.fp_style.SetCaptionStyle( wx.lib.agw.foldpanelbar.CAPTIONBAR_FILLED_RECTANGLE )
		self.fp_style.SetFirstColour( wx.Colour( 160, 160, 160, 255 ) )
		self.fp_style.SetSecondColour( wx.Colour( 0, 0, 0, 255 ) )
		self.fp_style.SetCaptionColour( wx.Colour( 0, 0, 0, 255 ) )

		#label to display selected name
		self.name_label = wx.StaticText( self, -1, 'Name:' )
		self.name_label.SetFont( wx.Font( 8, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.BOLD ))
		self.selected_name_text_ctrl = wx.TextCtrl( self, -1, '', size = (240, 20), style = wx.TE_PROCESS_ENTER )
		self.sync_bt_ctrl   	= wx.Button( self, -1, '', size=(20, 20))
		self.sync_bt_ctrl.SetBackgroundColour( wx.Colour( 255, 0, 0 ) )

		#label to display selected type
		self.type_label = wx.StaticText( self, -1, 'Type:' )
		self.type_label.SetFont( wx.Font( 8, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.BOLD ))
		self.selected_type_label = wx.StaticText( self, -1, '' )

		#setup name and type sizer
		self.name_inner_sizer.Add( self.selected_name_text_ctrl )
		self.name_inner_sizer.AddSpacer( 3 )
		self.name_inner_sizer.Add( self.sync_bt_ctrl, wx.ALIGN_TOP )

		self.name_type_sizer = wx.FlexGridSizer(cols=2, hgap=9, vgap=4)
		self.name_type_sizer.Add( self.name_label )
		self.name_type_sizer.Add( self.name_inner_sizer )
		self.name_type_sizer.Add( self.type_label )
		self.name_type_sizer.Add( self.selected_type_label )

		# scroll panel for properties folding panels
		self.scroll_panel = wx.ScrolledWindow( self, -1, pos=wx.DefaultPosition, size=self.GetSize( ), style=wx.SUNKEN_BORDER )

		self.pnl_page  = wx.Panel( self.scroll_panel, wx.ID_ANY )
		self.pnl_sizer = wx.BoxSizer( wx.VERTICAL )
		self.pnl_page.SetSizer( self.pnl_sizer )

		# create folding panel
		self.folding_panels = wx.lib.agw.foldpanelbar.FoldPanelBar( self.pnl_page, -1, wx.DefaultPosition, wx.DefaultSize, wx.lib.agw.foldpanelbar.FPB_VERTICAL )
		self.pnl_sizer.Add( self.folding_panels, 1, wx.EXPAND|wx.ALL, 2 )
		self.scroll_panel.SetScrollRate( 20, 20 )

		#setup main panel sizer
		self.main_sizer = wx.BoxSizer( wx.VERTICAL )
		self.main_sizer.AddSpacer( 5 )
		self.main_sizer.Add( self.name_type_sizer, 0, wx.ALL, 2 )
		self.main_sizer.Add( self.scroll_panel, 1, wx.EXPAND|wx.ALL, 2  )
		self.SetSizer( self.main_sizer )

		#bind event to update scroll bars
		self.folding_panels.Bind( wx.lib.agw.foldpanelbar.EVT_CAPTIONBAR, self.update_scrolling_bars )
		self.Bind( wx.EVT_SIZE, self.on_panel_resize )
		self.selected_name_text_ctrl.Bind( wx.EVT_TEXT_ENTER, self.on_name_changed )
		self.selected_name_text_ctrl.Bind( wx.EVT_TEXT, self.text_changed )
		self.sync_bt_ctrl.Bind( wx.EVT_BUTTON, self.on_sync_file_pressed )
		self.scroll_panel.Bind( wx.EVT_CHILD_FOCUS, self.on_folding_panel_gain_focus )
		self.Bind( wx.EVT_KEY_DOWN, self.on_key_down )

		#refresh pane
		self.refresh_ui( )

		doc = AnimationEditor.get_active_document( )
		setattr( doc, 'animation_properties_pane', self )


	def update_size( self, size ):
		unit = 16
		width, height = self.pnl_page.GetSize( )

		width = size[ 0 ]
		scroll_width = width - unit

		if height > self.GetSize( )[ 1 ]:
			width -= unit

		self.pnl_page.SetSize( ( width, height ) )

		self.scroll_panel.SetVirtualSize( ( scroll_width, height ) )
		self.scroll_panel.SetScrollRate( unit, unit )


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

		event.Skip( )


	def on_folding_panel_gain_focus( self, event ):
		"""
		This method is just the way to force the wx.lib.scrolledpanel.ScrolledPanel
		not to try to auto-scroll whenever a child gains focus, it does nothing but
		to tell the scroll window not to do anything, so as to avoid flickering of
		the properties pane.

		*Arguments:*
			* ``event`` wx.EVT_CHILD_FOCUS

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``none``
		"""

		pass


	@vlib.debug.Debug_Timing( 'refresh_property_panel', precision = 4 )
	def refresh_ui( self ):
		"""
		This method refreshes the properties pane.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``none``
		"""

		self.Freeze( )

		prop_panes 	= self.get_property_panels()
		width 		= self.GetSize()[0]
		height 		= 100

		self.fold_pane_to_show  	= [ ]
		self.fold_pane_to_hide 		= [ ]
		self.pane_titles_to_show 	= [ ]
		self.reposition_panel 		= 0
		self.hidden_panel_pos 		= 0


		if prop_panes != self.last_shown_panes:

			self.last_shown_panes 	= prop_panes
			for pane in prop_panes:
				if pane not in self.folding_panes_dict.keys():
					#add fold pane
					panels = self.add_fold_pane( pane, pane.pane_title, pane.collapse_fold_pane )
					self.folding_panes_dict[ pane ] 	= panels[1]
					self.prop_panes_dict[ pane ]  	= panels[0]

		#get the list of panes types to hide/show
		for key in self.folding_panes_dict.keys():
			if key not in prop_panes:
				self.fold_pane_to_hide.append( key )
			else:
				self.fold_pane_to_show.append( key )


		#show, reposition and refresh panes based on selected type
		if self.fold_pane_to_show:
			new_panes_to_show = self.fold_pane_to_show

			for pane in self.fold_pane_to_show:
				if hasattr( pane, 'get_child_prop_panes_objects' ):
					c_pane 				= self.prop_panes_dict.get( pane )
					child_prop_panes 	= c_pane.get_child_prop_panes_objects( )

					if child_prop_panes:
						for child_pane in child_prop_panes:
							if child_pane.pane_title not in self.child_prop_panes_dict.keys( ):
								#add fold pane
								child_panels = self.add_fold_pane( child_pane, child_pane.pane_title, child_pane.collapse_fold_pane )
								self.child_prop_panes_dict[ child_panels[0].pane_title ] = [ child_panels[0], child_panels[1] ]

							new_panes_to_show.append( child_pane )

			#this is just to make sure that everything is in order based on
			#display weight values
			self.prop_panes_to_show = self.sort_panes_display_order( new_panes_to_show )

			for prop_pane in self.prop_panes_to_show:
				folding_pane 	= self.folding_panes_dict.get( prop_pane )

				if folding_pane:
					self.show_or_hide_folding_pane( folding_pane, prop_pane.pane_title, True )

				child_pane 		= self.child_prop_panes_dict.get( prop_pane.pane_title )
				if child_pane:
					self.show_or_hide_folding_pane( child_pane[1], child_pane[0].pane_title, True )

		#hide fold panes that are not part of the selected object
		if self.fold_pane_to_hide:
			for prop_pane in self.fold_pane_to_hide:
				folding_pane = self.folding_panes_dict.get( prop_pane )
				if folding_pane:
					self.show_or_hide_folding_pane( folding_pane, pane_title= prop_pane.pane_title )

		#hide child prop panes that are not part of the selected objects properties pane
		for value in self.child_prop_panes_dict.values( ):
			if value:
				if value[0].pane_title not in self.pane_titles_to_show:
					child_pane = self.child_prop_panes_dict.get( value[0].pane_title )
					if child_pane:
						self.show_or_hide_folding_pane( child_pane[1], pane_title= value[0].pane_title)

		#update scroll panel
		self.update_scrolling_bars( None )

		#update
		self.Thaw( )


	def show_or_hide_folding_pane( self, folding_pane, pane_title = None, show_pane = False ):

		if folding_pane:
			if show_pane:
				if pane_title:
					self.pane_titles_to_show.append( pane_title )

				#reposition folding pane
				folding_pane.Reposition( self.reposition_panel )
				self.refresh_fold_pane( folding_pane )
				self.reposition_panel += 20

			else:
				self.hidden_panel_pos = ( 20 * len( self.prop_panes_to_show ) ) + self.hidden_panel_pos
				folding_pane.Reposition( self.hidden_panel_pos  )

			folding_pane.Show( show_pane )


	def reposition_panes( self ):

		if self.prop_panes_to_show:
			pane_index = self.folding_panels._panels.index( self.folding_panes_dict.get( self.prop_panes_to_show[0] ) )
			pos = self.folding_panels._panels[pane_index].GetItemPos() + self.folding_panels._panels[pane_index].GetPanelLength( )

			for i in range( pane_index+1, len( self.folding_panels._panels )):
				if self.folding_panels._panels[i].IsShown():
					pos = pos + self.folding_panels._panels[i].Reposition( pos )


	#@vlib.debug.Debug_Timing( 'update scrollbars', precision = 4 )
	def update_scrolling_bars( self, event ):
		"""
		This method update scrolling bars for scroll panel.

		*Arguments:*
			* ``event`` - wx.lib.agw.foldpanelbar.EVT_CAPTIONBAR event object, the event can be None.

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``none``

		"""

		folding_panel_count = self.folding_panels.GetCount( )
		height 	= 0
		h_off_set 	= 20
		w_off_set 	= 8

		if folding_panel_count > 0:

			#get folding panels total height
			for i in range( folding_panel_count ):
				folding_panel  = self.folding_panels.GetFoldPanel( i )
				panel_expanded = folding_panel.IsExpanded( )

				if folding_panel.IsShown():
					if event:
						if folding_panel._captionBar == event.GetEventObject( ):
							panel_expanded = not panel_expanded

					if panel_expanded:
						panel_height = folding_panel.GetBestSize( )[ 1 ]
					else:
						panel_height = folding_panel.GetCaptionLength( )

					height += panel_height

			width  = self.GetSize()[0] - w_off_set
			height = height + h_off_set
			size   = ( width, height )

			self.pnl_page.SetSize( size )
			self.update_size( size )

		if self.prop_panes_to_show:
			self.folding_panels.RedisplayFoldPanelItems( )
			self.reposition_panes( )

		if event:
			event.Skip( )


	def on_panel_resize( self, event ):
		"""
		This method updates scrolling bars for scroll panel, when a resize event
		is fired.

		*Arguments:*
			* ``event`` -wx.EVT_SIZE event object

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``none``
		"""

		#update scrolling bars
		self.update_scrolling_bars( event )

		if event:
			event.Skip( )


	#@vlib.debug.Debug_Timing( 'get_property_panels', precision = 4 )
	def get_property_panels( self ):
		"""
		This method gets and returns a list of property panes based on type of item
		selected.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``none``
		"""
		#get active document
		doc = AnimationEditor.get_active_document( )
		#get property panes subclasses
		subclasses = ctg.ui.panel.CTG_Animation_Properties_Panel.__subclasses__()

		panes_to_show 	= [ ]
		if not doc:
			return panes_to_show

		#update name and type controls and return a list of type names of selected objects
		type_names = self.update_name_type_controls( )

		#get selected objects
		sel_objs = doc.selection_manager.get_selected_objects()

		if not sel_objs or len( type_names ) > 1:
			return panes_to_show

		#get the panes and the display weight value
		prop_pane_type_name = self.get_prop_pane_type_to_display( )
		for sub_class in subclasses:
			prop_class = None
			if hasattr( sub_class, 'PROPERTY_PANE_TYPE' ):
				if sub_class.PROPERTY_PANE_TYPE == prop_pane_type_name:
					if hasattr( sel_objs[0], 'get_prop_nodes'):
						#get child prop nodes
						if sel_objs[0].get_prop_nodes()[0]:
							prop_class = sub_class
					else:
						prop_class = sub_class

			if prop_class:
				panes_to_show.append( prop_class )

		return panes_to_show


	def get_prop_pane_type_to_display( self ):
		doc = AnimationEditor.get_active_document( )
		prop_pane_type_to_display = None

		if not doc:
			return prop_pane_type_to_display

		sel_objs = doc.selection_manager.get_selected_objects()
		if sel_objs:
			prop_pane_type_to_display = list( inspect.getmro( sel_objs[0].__class__ ) )[ -2 ].__name__

		return prop_pane_type_to_display


	#@vlib.debug.Debug_Timing( 'add_fold_pane', precision = 4 )
	def add_fold_pane( self, pane, pane_title, collapse ):

		width 	= self.GetSize()[0]
		height 	= 100

		fold_panel = self.folding_panels.AddFoldPanel( pane_title, collapsed = collapse, foldIcons = self.fp_images )
		fold_panel.ApplyCaptionStyle( self.fp_style )

		if hasattr( pane, 'create_prop_panel'):
			prop_pane = pane.create_prop_panel( fold_panel )
		else:
			prop_pane = pane( fold_panel )

		if hasattr( prop_pane, 'get_height' ):
			height = prop_pane.get_height( )

		fold_panel.SetSizeWH( width, height )
		fold_panel.display_weight = prop_pane.display_weight
		fold_panel.pane_title     = pane_title

		if pane_title not in self.fold_pane_names_dict.keys( ):
			self.fold_pane_names_dict[ pane_title ] = fold_panel

		if hasattr( prop_pane, 'fold_pane' ):
			prop_pane.fold_pane = fold_panel

		self.folding_panels.AddFoldPanelWindow( fold_panel, prop_pane, wx.lib.agw.foldpanelbar.FPB_ALIGN_WIDTH, 5, 5 )

		return [ prop_pane, fold_panel ]

	#@vlib.debug.Debug_Timing( 'sort_panes_display_order', precision = 4 )
	def sort_panes_display_order( self, panes ):
		"""
		This method sorts panes based on the display weight value.

		*Arguments:*
			* ``panes`` list of property panes

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``list`` -sorted list of property panes in there display weight.
		"""

		sorted_list = [ ]
		if panes:
			sorted_list = sorted( panes, key=lambda pane: pane.display_weight )

		return sorted_list


	#@vlib.debug.Debug_Timing( 'update_name_type_controls', precision = 4 )
	def update_name_type_controls( self ):
		"""
		This method updates name and type controls.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``type_names`` Names of all types
		"""
		doc	= AnimationEditor.get_active_document( )
		if not doc:
			return

		type_names  		= [ ]
		obj_names   		= [ ]
		enable 				= False

		sel_objs = doc.selection_manager.get_selected_objects()

		if sel_objs:
			for obj in sel_objs:

				#object type
				if hasattr( obj, "object_type_name") and obj.object_type_name != None:
					type_name 	= "{0}_{1}".format( str( obj.object_type_name ).replace(" ", "_"), "Node" )
				else:
					type_name 	= obj.__class__.__name__

				#object name
				if hasattr( obj, 'get_name'):
					obj_name = obj.get_name( )
				elif hasattr( obj, 'get_bone_name'):
					obj_name = obj.get_bone_name( )
				elif hasattr( obj, 'name'):
					obj_name = obj.name

				#add object type to list of object type
				if type_name not in type_names:
					type_names.append( type_name )

				#add object name to list of object names
				if obj_name not in obj_names:
					obj_names.append( obj_name )

			if len( sel_objs ) == 1:
				if type_names[0] in [ 'Clip_Item', 'Tag_Association_Item', 'Control_Parameter_Node', 'Rig_Bone_Item' ] or obj_names[0].lower() == 'Default'.lower():
					enable = False
				else:
					enable = True
		else:
			enable = False

		if not obj_names or len( obj_names ) > 1:
			self.selected_name_text_ctrl.SetValue( '' )
			self.sel_obj_name  = ''
		else:
			self.selected_name_text_ctrl.SetValue( obj_names[0] )
			self.sel_obj_name  = obj_names[0]

		if not type_names:
			self.selected_type_label.SetLabel( '' )
		else:
			if len( type_names ) == 1:
				self.selected_type_label.SetLabel( type_names[0] )
			else:
				self.selected_type_label.SetLabel( 'Multiple Types Selected' )

		#enable
		self.selected_name_text_ctrl.Enable( enable )
		self.name_inner_sizer.Hide( self.sync_bt_ctrl )
		self.name_inner_sizer.Layout( )
		self.name_type_sizer.Layout( )

		return type_names


	def on_sync_file_pressed( self, event ):
		doc	= AnimationEditor.get_active_document( )
		if not doc:
			return

		sel_objs = doc.selection_manager.get_recent_sel_clips()
		if sel_objs:
			if len( sel_objs ) == 1:
				if hasattr( sel_objs[0], 'sync_file'):
					synced = sel_objs[0].sync_file( )
					self.update_sync_button_bg_color( synced )


	#@vlib.debug.Debug_Timing( 'refresh_fold_pane prop', precision = 4 )
	def refresh_fold_pane( self, fold_pane ):
		for child in fold_pane.GetChildren( ):
			if hasattr( child, 'refresh_ui' ):
				child.refresh_ui( )


	@vlib.debug.Debug_Timing( 'refresh_redisplay_fold_pane', precision = 4 )
	def refresh_redisplay_fold_pane( self, fold_pane ):
		self.Freeze( )

		self.refresh_fold_pane( fold_pane )
		self.update_scrolling_bars( None )

		self.Thaw( )


	def update_sync_button_bg_color( self, synced ):
		if synced == True:
			self.sync_bt_ctrl.SetBackgroundColour( wx.Colour( 122, 208, 62, 255 ) )
		elif synced == False:
			self.sync_bt_ctrl.SetBackgroundColour( wx.Colour( 255, 255, 0, 255 ) )
		else:
			self.sync_bt_ctrl.SetBackgroundColour( wx.Colour( 255, 0, 0, 255 ) )


	def on_name_changed( self, event ):
		doc	= AnimationEditor.get_active_document( )
		if not doc:
			return

		sel_objs 	= doc.selection_manager.get_selected_objects()
		value 		= self.selected_name_text_ctrl.GetValue( )

		if sel_objs:
			if len( sel_objs ) == 1:
				if hasattr( sel_objs[0], 'validate_name' ):
					valid = sel_objs[0].validate_name( value )

					if valid:
						if hasattr( sel_objs[0], 'rename'):
							did_rename 	= sel_objs[0].rename( value )

							if did_rename:

								#obj = doc.selection_manager.get_item_from_collection( sel_objs[0], value )
								#self.post_item_rename_event( obj, self.sel_obj_name )
								self.sel_obj_name = sel_objs[0].get_name( )
								self.selected_name_text_ctrl.SetValue( self.sel_obj_name  )

							else:
								dlg = wx.MessageDialog(self, 'Renaming failed.','Renaming Failed', wx.OK | wx.ICON_INFORMATION )

								if dlg.ShowModal() == wx.ID_OK:
									self.selected_name_text_ctrl.SetValue( self.sel_obj_name )

								dlg.Destroy()

					else:
						dlg = wx.MessageDialog(self, 'The name is invalid either the name exist\n or has invalid characters.','Invalid Name',
													  wx.OK | wx.ICON_INFORMATION )

						if dlg.ShowModal() == wx.ID_OK:
							self.selected_name_text_ctrl.SetValue( self.sel_obj_name )

						dlg.Destroy()


	def text_changed( self, event ):
		doc	= AnimationEditor.get_active_document( )
		if not doc:
			return

		sel_objs = doc.selection_manager.get_selected_objects()
		value 	= self.selected_name_text_ctrl.GetValue( )
		bg_color = wx.SystemSettings.GetColour( wx.SYS_COLOUR_LISTBOX )

		if sel_objs:
			if len( sel_objs ) == 1:
				if hasattr( sel_objs[0], 'validate_name' ):
					valid = sel_objs[0].validate_name( value )

					if not valid:
						bg_color = wx.Colour( 255, 0, 0 )

		try:
			self.selected_name_text_ctrl.SetBackgroundColour( bg_color )
		except:
			print('This fails when adding a state or action tag association')
		self.selected_name_text_ctrl.Refresh( )

		if event:
			event.Skip()


	def post_item_rename_event( self, data_obj, old_name = '' ):
		doc	= AnimationEditor.get_active_document( )
		if not doc:
			return

		if isinstance( data_obj, ctg.ae2.core.data.Set_Item ):
			doc.event_manager.post_set_renamed_event( [ data_obj ], old_name )

		elif isinstance( data_obj, ctg.ae2.core.data.Group_Item ):
			doc.event_manager.post_group_renamed_event( [ data_obj ], old_name )

		elif isinstance( data_obj, ctg.ae2.core.data.State_Tag_Item ):
			doc.event_manager.post_state_tag_renamed_event( [ data_obj ] )

		elif isinstance( data_obj, ctg.ae2.core.data.Action_Tag_Item ):
			doc.event_manager.post_action_tag_renamed_event( [ data_obj ] )

		elif isinstance( data_obj, ctg.ae2.core.data.Control_Filter_Item ):
			doc.event_manager.post_control_filter_renamed_event( [ data_obj ], old_name )

		elif isinstance( data_obj, ctg.ae2.core.data.Control_Parameter_Item ):
			doc.event_manager.post_control_parameter_renamed_event( [ data_obj ], old_name )

		elif isinstance( data_obj, ctg.ae2.core.data.State_Machine_Item ):
			doc.event_manager.post_state_machine_renamed_event( [ data_obj ], old_name )

		elif isinstance( data_obj, ctg.ae2.core.data.Blend_Tree_Item ):
			doc.event_manager.post_blend_tree_renamed_event( [ data_obj ], old_name )
