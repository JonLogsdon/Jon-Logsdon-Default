import wx

import ctg
import ctg.ae2
import ctg.ae2.core.data
import ctg.ae2.ui
import ctg.ae2.ui.const
import ctg.prefs
import AnimationEditor
import vlib.ui.node_graph


#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
## Events ##
#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

EVT_COMMAND_AE_CLIP_SELECT = wx.NewEventType( )
EVT_AE_CLIP_SELECT = wx.PyEventBinder( EVT_COMMAND_AE_CLIP_SELECT, 1 )

EVT_COMMAND_AE_CLIP_UPDATE = wx.NewEventType( )
EVT_AE_CLIP_UPDATE = wx.PyEventBinder( EVT_COMMAND_AE_CLIP_UPDATE, 1 )

EVT_COMMAND_AE_GROUP_SELECT = wx.NewEventType( )
EVT_AE_GROUP_SELECT = wx.PyEventBinder( EVT_COMMAND_AE_GROUP_SELECT, 1 )

EVT_COMMAND_AE_TAG_MODIFIED = wx.NewEventType( )
EVT_AE_TAG_MODIFIED = wx.PyEventBinder( EVT_COMMAND_AE_TAG_MODIFIED, 1 )

EVT_COMMAND_AE_KEYWORD_DISPLAY = wx.NewEventType( )
EVT_AE_KEYWORD_DISPLAY = wx.PyEventBinder( EVT_COMMAND_AE_KEYWORD_DISPLAY, 1 )

#state tags custom events
EVT_COMMAND_AE_STATE_TAG_SELECT = wx.NewEventType( )
EVT_AE_STATE_TAG_SELECT = wx.PyEventBinder( EVT_COMMAND_AE_STATE_TAG_SELECT, 1 )

EVT_COMMAND_AE_STATE_TAG_CREATED = wx.NewEventType( )
EVT_AE_STATE_TAG_CREATED = wx.PyEventBinder( EVT_COMMAND_AE_STATE_TAG_CREATED, 1 )

EVT_COMMAND_AE_STATE_TAG_RENAMED = wx.NewEventType( )
EVT_AE_STATE_TAG_RENAMED = wx.PyEventBinder( EVT_COMMAND_AE_STATE_TAG_RENAMED, 1 )

EVT_COMMAND_AE_STATE_TAG_DELETED = wx.NewEventType( )
EVT_AE_STATE_TAG_DELETED = wx.PyEventBinder( EVT_COMMAND_AE_STATE_TAG_DELETED, 1 )

#action tags custom events
EVT_COMMAND_AE_ACTION_TAG_SELECT = wx.NewEventType( )
EVT_AE_ACTION_TAG_SELECT = wx.PyEventBinder( EVT_COMMAND_AE_ACTION_TAG_SELECT, 1 )

EVT_COMMAND_AE_ACTION_TAG_CREATED = wx.NewEventType( )
EVT_AE_ACTION_TAG_CREATED = wx.PyEventBinder( EVT_COMMAND_AE_ACTION_TAG_CREATED, 1 )

EVT_COMMAND_AE_ACTION_TAG_RENAMED = wx.NewEventType( )
EVT_AE_ACTION_TAG_RENAMED = wx.PyEventBinder( EVT_COMMAND_AE_ACTION_TAG_RENAMED, 1 )

EVT_COMMAND_AE_ACTION_TAG_DELETED = wx.NewEventType( )
EVT_AE_ACTION_TAG_DELETED = wx.PyEventBinder( EVT_COMMAND_AE_ACTION_TAG_DELETED, 1 )

#control filter custom events
EVT_COMMAND_AE_CONTROL_FILTER_SELECT = wx.NewEventType( )
EVT_AE_CONTROL_FILTER_SELECT = wx.PyEventBinder( EVT_COMMAND_AE_CONTROL_FILTER_SELECT, 1 )

EVT_COMMAND_AE_CONTROL_FILTER_CREATED = wx.NewEventType( )
EVT_AE_CONTROL_FILTER_CREATED = wx.PyEventBinder( EVT_COMMAND_AE_CONTROL_FILTER_CREATED, 1 )

EVT_COMMAND_AE_CONTROL_FILTER_RENAMED = wx.NewEventType( )
EVT_AE_CONTROL_FILTER_RENAMED = wx.PyEventBinder( EVT_COMMAND_AE_CONTROL_FILTER_RENAMED, 1 )

EVT_COMMAND_AE_CONTROL_FILTER_DELETED = wx.NewEventType( )
EVT_AE_CONTROL_FILTER_DELETED = wx.PyEventBinder( EVT_COMMAND_AE_CONTROL_FILTER_DELETED, 1 )

EVT_COMMAND_AE_CONTROL_FILTER_MODIFIED = wx.NewEventType( )
EVT_AE_CONTROL_FILTER_MODIFIED = wx.PyEventBinder( EVT_COMMAND_AE_CONTROL_FILTER_MODIFIED, 1 )

#control parameter custom events
EVT_COMMAND_AE_CONTROL_PARAMETER_SELECT = wx.NewEventType( )
EVT_AE_CONTROL_PARAMETER_SELECT = wx.PyEventBinder( EVT_COMMAND_AE_CONTROL_PARAMETER_SELECT, 1 )

EVT_COMMAND_AE_CONTROL_PARAMETER_CREATED = wx.NewEventType( )
EVT_AE_CONTROL_PARAMETER_CREATED = wx.PyEventBinder( EVT_COMMAND_AE_CONTROL_PARAMETER_CREATED, 1 )

EVT_COMMAND_AE_CONTROL_PARAMETER_RENAMED = wx.NewEventType( )
EVT_AE_CONTROL_PARAMETER_RENAMED = wx.PyEventBinder( EVT_COMMAND_AE_CONTROL_PARAMETER_RENAMED, 1 )

EVT_COMMAND_AE_CONTROL_PARAMETER_DELETED = wx.NewEventType( )
EVT_AE_CONTROL_PARAMETER_DELETED = wx.PyEventBinder( EVT_COMMAND_AE_CONTROL_PARAMETER_DELETED, 1 )

EVT_COMMAND_AE_CONTROL_PARAMETER_MODIFIED = wx.NewEventType( )
EVT_AE_CONTROL_PARAMETER_MODIFIED = wx.PyEventBinder( EVT_COMMAND_AE_CONTROL_PARAMETER_MODIFIED, 1 )

#group custom events
EVT_COMMAND_AE_GROUP_SELECT = wx.NewEventType( )
EVT_AE_GROUP_SELECT = wx.PyEventBinder( EVT_COMMAND_AE_GROUP_SELECT, 1 )

EVT_COMMAND_AE_GROUP_CREATED = wx.NewEventType( )
EVT_AE_GROUP_CREATED = wx.PyEventBinder( EVT_COMMAND_AE_GROUP_CREATED, 1 )

EVT_COMMAND_AE_GROUP_RENAMED = wx.NewEventType( )
EVT_AE_GROUP_RENAMED = wx.PyEventBinder( EVT_COMMAND_AE_GROUP_RENAMED, 1 )

EVT_COMMAND_AE_GROUP_DELETED = wx.NewEventType( )
EVT_AE_GROUP_DELETED = wx.PyEventBinder( EVT_COMMAND_AE_GROUP_DELETED, 1 )

EVT_COMMAND_AE_GROUP_MODIFIED = wx.NewEventType( )
EVT_AE_GROUP_MODIFIED = wx.PyEventBinder( EVT_COMMAND_AE_GROUP_MODIFIED, 1 )

#sets custom events
EVT_COMMAND_AE_SET_SELECT = wx.NewEventType( )
EVT_AE_SET_SELECT = wx.PyEventBinder( EVT_COMMAND_AE_SET_SELECT, 1 )

EVT_COMMAND_AE_SET_CREATED = wx.NewEventType( )
EVT_AE_SET_CREATED = wx.PyEventBinder( EVT_COMMAND_AE_SET_CREATED, 1 )

EVT_COMMAND_AE_SET_RENAMED = wx.NewEventType( )
EVT_AE_SET_RENAMED = wx.PyEventBinder( EVT_COMMAND_AE_SET_RENAMED, 1 )

EVT_COMMAND_AE_SET_DELETED = wx.NewEventType( )
EVT_AE_SET_DELETED = wx.PyEventBinder( EVT_COMMAND_AE_SET_DELETED, 1 )

EVT_COMMAND_AE_SET_MODIFIED = wx.NewEventType( )
EVT_AE_SET_MODIFIED = wx.PyEventBinder( EVT_COMMAND_AE_SET_MODIFIED, 1 )

#state machine custom events
EVT_COMMAND_AE_STATE_MACHINE_SELECT = wx.NewEventType( )
EVT_AE_STATE_MACHINE_SELECT = wx.PyEventBinder( EVT_COMMAND_AE_STATE_MACHINE_SELECT, 1 )

EVT_COMMAND_AE_STATE_MACHINE_LOAD = wx.NewEventType( )
EVT_AE_STATE_MACHINE_LOAD = wx.PyEventBinder( EVT_COMMAND_AE_STATE_MACHINE_LOAD, 1 )

EVT_COMMAND_AE_STATE_MACHINE_CREATED = wx.NewEventType( )
EVT_AE_STATE_MACHINE_CREATED = wx.PyEventBinder( EVT_COMMAND_AE_STATE_MACHINE_CREATED, 1 )

EVT_COMMAND_AE_STATE_MACHINE_RENAMED = wx.NewEventType( )
EVT_AE_STATE_MACHINE_RENAMED = wx.PyEventBinder( EVT_COMMAND_AE_STATE_MACHINE_RENAMED, 1 )

EVT_COMMAND_AE_STATE_MACHINE_DELETED = wx.NewEventType( )
EVT_AE_STATE_MACHINE_DELETED = wx.PyEventBinder( EVT_COMMAND_AE_STATE_MACHINE_DELETED, 1 )

EVT_COMMAND_AE_STATE_MACHINE_MODIFIED = wx.NewEventType( )
EVT_AE_STATE_MACHINE_MODIFIED = wx.PyEventBinder( EVT_COMMAND_AE_STATE_MACHINE_MODIFIED, 1 )

#blend tree custom events
EVT_COMMAND_AE_BLEND_TREE_SELECT = wx.NewEventType( )
EVT_AE_BLEND_TREE_SELECT = wx.PyEventBinder( EVT_COMMAND_AE_BLEND_TREE_SELECT, 1 )

EVT_COMMAND_AE_BLEND_TREE_LOAD = wx.NewEventType( )
EVT_AE_BLEND_TREE_LOAD = wx.PyEventBinder( EVT_COMMAND_AE_BLEND_TREE_LOAD, 1 )

EVT_COMMAND_AE_BLEND_TREE_CREATED = wx.NewEventType( )
EVT_AE_BLEND_TREE_CREATED = wx.PyEventBinder( EVT_COMMAND_AE_BLEND_TREE_CREATED, 1 )

EVT_COMMAND_AE_BLEND_TREE_RENAMED = wx.NewEventType( )
EVT_AE_BLEND_TREE_RENAMED = wx.PyEventBinder( EVT_COMMAND_AE_BLEND_TREE_RENAMED, 1 )

EVT_COMMAND_AE_BLEND_TREE_DELETED = wx.NewEventType( )
EVT_AE_BLEND_TREE_DELETED = wx.PyEventBinder( EVT_COMMAND_AE_BLEND_TREE_DELETED, 1 )

EVT_COMMAND_AE_BLEND_TREE_MODIFIED = wx.NewEventType( )
EVT_AE_BLEND_TREE_MODIFIED = wx.PyEventBinder( EVT_COMMAND_AE_BLEND_TREE_MODIFIED, 1 )

#tag association custom events
EVT_COMMAND_AE_TAG_ASSOCIATION_CREATED = wx.NewEventType( )
EVT_AE_TAG_ASSOCIATION_CREATED = wx.PyEventBinder( EVT_COMMAND_AE_TAG_ASSOCIATION_CREATED, 1 )

EVT_COMMAND_AE_TAG_ASSOCIATION_MODIFIED = wx.NewEventType( )
EVT_AE_TAG_ASSOCIATION_MODIFIED = wx.PyEventBinder( EVT_COMMAND_AE_TAG_ASSOCIATION_MODIFIED, 1 )

EVT_COMMAND_AE_TAG_ASSOCIATION_UPDATED = wx.NewEventType( )
EVT_AE_TAG_ASSOCIATION_UPDATED = wx.PyEventBinder( EVT_COMMAND_AE_TAG_ASSOCIATION_UPDATED, 1 )

EVT_COMMAND_AE_TAG_ASSOCIATION_DELETED = wx.NewEventType( )
EVT_AE_TAG_ASSOCIATION_DELETED = wx.PyEventBinder( EVT_COMMAND_AE_TAG_ASSOCIATION_DELETED, 1 )

EVT_COMMAND_AE_NODE_GRAPH_DEPENDENTS_MODIFIED = wx.NewEventType( )
EVT_AE_NODE_GRAPH_DEPENDENTS_MODIFIED = wx.PyEventBinder( EVT_COMMAND_AE_NODE_GRAPH_DEPENDENTS_MODIFIED, 1 )

#named value custom events
EVT_COMMAND_AE_NAMED_VALUE_SELECT = wx.NewEventType( )
EVT_AE_NAMED_VALUED_SELECT = wx.PyEventBinder( EVT_COMMAND_AE_NAMED_VALUE_SELECT, 1 )

EVT_COMMAND_AE_NAMED_VALUED_CREATED = wx.NewEventType( )
EVT_AE_NAMED_VALUED_CREATED = wx.PyEventBinder( EVT_COMMAND_AE_NAMED_VALUED_CREATED, 1 )

EVT_COMMAND_AE_NAMED_VALUED_RENAMED = wx.NewEventType( )
EVT_AE_NAMED_VALUED_RENAMED = wx.PyEventBinder( EVT_COMMAND_AE_NAMED_VALUED_RENAMED, 1 )

EVT_COMMAND_AE_NAMED_VALUED_DELETED = wx.NewEventType( )
EVT_AE_NAMED_VALUED_DELETED = wx.PyEventBinder( EVT_COMMAND_AE_NAMED_VALUED_DELETED, 1 )

EVT_COMMAND_AE_NAMED_VALUED_MODIFIED = wx.NewEventType( )
EVT_AE_NAMED_VALUED_MODIFIED = wx.PyEventBinder( EVT_COMMAND_AE_NAMED_VALUED_MODIFIED, 1 )


#rig bones custom events
EVT_COMMAND_AE_RIG_BONE_SELECT = wx.NewEventType( )
EVT_AE_RIG_BONE_SELECT = wx.PyEventBinder( EVT_COMMAND_AE_RIG_BONE_SELECT, 1 )

EVT_COMMAND_AE_RIG_BONE_MODIFIED = wx.NewEventType( )
EVT_AE_RIG_BONE_MODIFIED = wx.PyEventBinder( EVT_COMMAND_AE_RIG_BONE_MODIFIED, 1 )


#rig aux data custom events
EVT_COMMAND_AE_RIG_AUX_DATA_SELECT = wx.NewEventType( )
EVT_AE_RIG_AUX_DATA_SELECT = wx.PyEventBinder( EVT_COMMAND_AE_RIG_AUX_DATA_SELECT, 1 )

EVT_COMMAND_AE_RIG_AUX_DATA_MODIFIED = wx.NewEventType( )
EVT_AE_RIG_AUX_DATA_MODIFIED = wx.PyEventBinder( EVT_COMMAND_AE_RIG_AUX_DATA_MODIFIED, 1 )

EVT_COMMAND_AE_RIG_AUX_DATA_DELETED = wx.NewEventType( )
EVT_AE_RIG_AUX_DATA_DELETED = wx.PyEventBinder( EVT_COMMAND_AE_RIG_AUX_DATA_DELETED, 1 )


#modifier custom events
EVT_COMMAND_AE_MODIFIER_SELECT = wx.NewEventType( )
EVT_AE_MODIFIER_SELECT = wx.PyEventBinder( EVT_COMMAND_AE_MODIFIER_SELECT, 1 )

EVT_COMMAND_AE_MODIFIER_MODIFIED = wx.NewEventType( )
EVT_AE_MODIFIER_MODIFIED = wx.PyEventBinder( EVT_COMMAND_AE_MODIFIER_MODIFIED, 1 )

EVT_COMMAND_AE_MODIFIER_DELETED = wx.NewEventType( )
EVT_AE_MODIFIER_DELETED = wx.PyEventBinder( EVT_COMMAND_AE_MODIFIER_DELETED, 1 )



class Event_Base( wx.PyCommandEvent ):
	def __init__( self, event_type, data_objs = None, old_name = None, new_name = None, group_name = None, set_name = None, data = None, active_tag_type = None, owner = None, properties_update = True, dependent = None, use_clip_column = False ):
		wx.PyCommandEvent.__init__( self, id = wx.ID_ANY )
		self.validate_data_obj( data_objs )
		self.data_objs         = data_objs
		self.old_name          = old_name
		self.new_name          = new_name
		self.set_name          = set_name
		self.group_name        = group_name
		self.data              = data
		self.owner             = owner
		self.properties_update = properties_update
		self.active_tag_type   = active_tag_type
		self.dependent         = dependent
		self.use_clip_column   = use_clip_column

		self.SetEventType( event_type )

	def validate_data_obj( self, data_objs ):
		#if data_obj and ( not isinstance( data_obj, ctg.ae2.core.data.Clip_Item ) ):
		#	assert False, 'Event_Clip_Select got {0}; expected {1}'.format( type( data_obj ), '<type \'ctg.ae2.core.data.Clip_Item\'>' )
		pass


	def get_data_objs( self ):
		return self.data_objs


	def get_clip_name( self ):
		if self.data_objs:
			return self.data_obj[0].get_name( )

		return None


class Event_Clip_Update( Event_Base ):
	def __init__( self, data_objs = None ):
		Event_Base.__init__( self, EVT_COMMAND_AE_CLIP_UPDATE, data_objs = data_objs )


class Event_Clip_Select( Event_Base ):
	def __init__( self, data_objs = None ):
		Event_Base.__init__( self, EVT_COMMAND_AE_CLIP_SELECT, data_objs = data_objs )


	def validate_data_obj( self, data_objs ):
		if data_objs and ( not isinstance( data_objs[0], ctg.ae2.core.data.Clip_Item ) ):
			assert False, 'Event_Clip_Select got {0}; expected {1}'.format( type( data_objs[0] ), '<type \'ctg.ae2.core.data.Clip_Item\'>' )


class Event_Keywords_Display( Event_Base ):
	def __init__( self, data_objs=None ):
		Event_Base.__init__( self, EVT_COMMAND_AE_KEYWORD_DISPLAY, data_objs=data_objs )


class Event_Group_Select( Event_Base ):
	def __init__( self, data_objs = None, owner = None ):
		Event_Base.__init__( self, EVT_COMMAND_AE_GROUP_SELECT, data_objs = data_objs, owner = owner )


#General tag modification for undo/redo
class Event_Tag_Modified( Event_Base ):
	def __init__( self, data_objs = None, old_name = None ):
		Event_Base.__init__( self, EVT_COMMAND_AE_TAG_MODIFIED, data_objs = data_objs, old_name = old_name )



#State tag events
class Event_State_Tag_Select( Event_Base ):
	def __init__( self, data_objs = None ):
		Event_Base.__init__( self, EVT_COMMAND_AE_STATE_TAG_SELECT, data_objs = data_objs )



class Event_State_Tag_Created( Event_Base ):
	def __init__( self, data_objs = None ):
		Event_Base.__init__( self, EVT_COMMAND_AE_STATE_TAG_CREATED, data_objs = data_objs )



class Event_State_Tag_Renamed( Event_Base ):
	def __init__( self, data_objs = None, old_name = None ):
		Event_Base.__init__( self, EVT_COMMAND_AE_STATE_TAG_RENAMED, data_objs = data_objs, old_name = old_name )



class Event_State_Tag_Deleted( Event_Base ):
	def __init__( self, data_objs = None, old_name = None ):
		Event_Base.__init__( self, EVT_COMMAND_AE_STATE_TAG_DELETED, data_objs = data_objs )


#Action tag events
class Event_Action_Tag_Select( Event_Base ):
	def __init__( self, data_objs = None ):
		Event_Base.__init__( self, EVT_COMMAND_AE_ACTION_TAG_SELECT, data_objs = data_objs )



class Event_Action_Tag_Created( Event_Base ):
	def __init__( self, data_objs = None ):
		Event_Base.__init__( self, EVT_COMMAND_AE_ACTION_TAG_CREATED, data_objs = data_objs )



class Event_Action_Tag_Renamed( Event_Base ):
	def __init__( self, data_objs = None, old_name = None ):
		Event_Base.__init__( self, EVT_COMMAND_AE_ACTION_TAG_RENAMED, data_objs = data_objs, old_name = old_name )



class Event_Action_Tag_Deleted( Event_Base ):
	def __init__( self, data_objs = None, old_name = None ):
		Event_Base.__init__( self, EVT_COMMAND_AE_ACTION_TAG_DELETED, data_objs = data_objs )


#control filter
class Event_Control_Filter_Select( Event_Base ):
	def __init__( self, data_objs = None ):
		Event_Base.__init__( self, EVT_COMMAND_AE_CONTROL_FILTER_SELECT, data_objs = data_objs )


class Event_Control_Filter_Created( Event_Base ):
	def __init__( self, data_objs = None ):
		Event_Base.__init__( self, EVT_COMMAND_AE_CONTROL_FILTER_CREATED, data_objs = data_objs )


class Event_Control_Filter_Renamed( Event_Base ):
	def __init__( self, data_objs = None, old_name = None ):
		Event_Base.__init__( self, EVT_COMMAND_AE_CONTROL_FILTER_RENAMED, data_objs = data_objs, old_name = old_name )


class Event_Control_Filter_Deleted( Event_Base ):
	def __init__( self, data_objs = None ):
		Event_Base.__init__( self, EVT_COMMAND_AE_CONTROL_FILTER_DELETED, data_objs = data_objs )


class Event_Control_Filter_Modified( Event_Base ):
	def __init__( self, data_objs = None ):
		Event_Base.__init__( self, EVT_COMMAND_AE_CONTROL_FILTER_MODIFIED, data_objs = data_objs )


#control parameter events
class Event_Control_Parameter_Select( Event_Base ):
	def __init__( self, data_objs = None ):
		Event_Base.__init__( self, EVT_COMMAND_AE_CONTROL_PARAMETER_SELECT, data_objs = data_objs )



class Event_Control_Parameter_Created( Event_Base ):
	def __init__( self, data_objs = None ):
		Event_Base.__init__( self, EVT_COMMAND_AE_CONTROL_PARAMETER_CREATED, data_objs = data_objs )



class Event_Control_Parameter_Renamed( Event_Base ):
	def __init__( self, data_objs = None, old_name = None ):
		Event_Base.__init__( self, EVT_COMMAND_AE_CONTROL_PARAMETER_RENAMED, data_objs = data_objs, old_name = old_name )



class Event_Control_Parameter_Deleted( Event_Base ):
	def __init__( self, data_objs = None ):
		Event_Base.__init__( self, EVT_COMMAND_AE_CONTROL_PARAMETER_DELETED, data_objs = data_objs )



class Event_Control_Parameter_Modified( Event_Base ):
	def __init__( self, data_objs = None ):
		Event_Base.__init__( self, EVT_COMMAND_AE_CONTROL_PARAMETER_MODIFIED, data_objs = data_objs )



#State Machine events
class Event_State_Machine_Select( Event_Base ):
	def __init__( self, data_objs = None ):
		Event_Base.__init__( self, EVT_COMMAND_AE_STATE_MACHINE_SELECT, data_objs = data_objs )



class Event_State_Machine_Load( Event_Base ):
	def __init__( self, data_objs = None, owner = None, dependent = None ):
		Event_Base.__init__( self, EVT_COMMAND_AE_STATE_MACHINE_LOAD, data_objs = data_objs, owner = owner, dependent = dependent )


class Event_State_Machine_Created( Event_Base ):
	def __init__( self, data_objs = None ):
		Event_Base.__init__( self, EVT_COMMAND_AE_STATE_MACHINE_CREATED, data_objs = data_objs )


class Event_State_Machine_Renamed( Event_Base ):
	def __init__( self, data_objs = None, old_name = None, new_name = None ):
		Event_Base.__init__( self, EVT_COMMAND_AE_STATE_MACHINE_RENAMED, data_objs = data_objs, old_name = old_name, new_name = new_name )


class Event_State_Machine_Deleted( Event_Base ):
	def __init__( self, data_objs = None ):
		Event_Base.__init__( self, EVT_COMMAND_AE_STATE_MACHINE_DELETED, data_objs = data_objs )


class Event_State_Machine_Modified( Event_Base ):
	def __init__( self, data_objs = None ):
		Event_Base.__init__( self, EVT_COMMAND_AE_STATE_MACHINE_MODIFIED, data_objs = data_objs )


#Blend tree events
class Event_Blend_Tree_Select( Event_Base ):
	def __init__( self, data_objs = None ):
		Event_Base.__init__( self, EVT_COMMAND_AE_BLEND_TREE_SELECT, data_objs = data_objs )


class Event_Blend_Tree_Load( Event_Base ):
	def __init__( self, data_objs = None, owner = None, dependent = None ):
		Event_Base.__init__( self, EVT_COMMAND_AE_BLEND_TREE_LOAD, data_objs = data_objs, owner = owner, dependent = dependent )


class Event_Blend_Tree_Created( Event_Base ):
	def __init__( self, data_objs = None ):
		Event_Base.__init__( self, EVT_COMMAND_AE_BLEND_TREE_CREATED, data_objs = data_objs )


class Event_Blend_Tree_Renamed( Event_Base ):
	def __init__( self, data_objs = None, old_name = None, new_name = None ):
		Event_Base.__init__( self, EVT_COMMAND_AE_BLEND_TREE_RENAMED, data_objs = data_objs, old_name = old_name, new_name = new_name )


class Event_Blend_Tree_Deleted( Event_Base ):
	def __init__( self, data_objs = None ):
		Event_Base.__init__( self, EVT_COMMAND_AE_BLEND_TREE_DELETED, data_objs = data_objs )


class Event_Blend_Tree_Modified( Event_Base ):
	def __init__( self, data_objs = None ):
		Event_Base.__init__( self, EVT_COMMAND_AE_BLEND_TREE_MODIFIED, data_objs = data_objs )


#group events
class Event_Group_Created( Event_Base ):
	def __init__( self, data_objs = None, group_name = None, set_name = None ):
		Event_Base.__init__( self, EVT_COMMAND_AE_GROUP_CREATED, data_objs = data_objs, group_name = group_name, set_name = set_name )


class Event_Group_Renamed( Event_Base ):
	def __init__( self, data_objs = None, old_name = None, set_name = None, owner = None ):
		Event_Base.__init__( self, EVT_COMMAND_AE_GROUP_RENAMED, data_objs = data_objs, old_name = old_name, set_name = set_name, owner = owner )


class Event_Group_Deleted( Event_Base ):
	def __init__( self, data_objs = None, group_name = None, set_name = None ):
		Event_Base.__init__( self, EVT_COMMAND_AE_GROUP_DELETED, data_objs = data_objs, group_name = group_name, set_name = set_name )


class Event_Group_Modified( Event_Base ):
	def __init__( self, data_objs = None, group_name = None ):
		Event_Base.__init__( self, EVT_COMMAND_AE_GROUP_MODIFIED, data_objs = data_objs, group_name = group_name )


#sets events
class Event_Set_Select( Event_Base ):
	def __init__( self, data_objs = None, owner = None ):
		Event_Base.__init__( self, EVT_COMMAND_AE_SET_SELECT, data_objs = data_objs, owner = owner )



class Event_Set_Created( Event_Base ):
	def __init__( self, data_objs = None ):
		Event_Base.__init__( self, EVT_COMMAND_AE_SET_CREATED, data_objs = data_objs )



class Event_Set_Renamed( Event_Base ):
	def __init__( self, data_objs = None, old_name = None, owner = None ):
		Event_Base.__init__( self, EVT_COMMAND_AE_SET_RENAMED, data_objs = data_objs, old_name = old_name, owner = owner )



class Event_Set_Deleted( Event_Base ):
	def __init__( self, data_objs = None ):
		Event_Base.__init__( self, EVT_COMMAND_AE_SET_DELETED, data_objs = data_objs )



class Event_Set_Modified( Event_Base ):
	def __init__( self, data_objs = None ):
		Event_Base.__init__( self, EVT_COMMAND_AE_SET_MODIFIED, data_objs = data_objs )


#tag association events
class Event_Tag_Association_Created( Event_Base ):
	def __init__( self, data_objs = None, data = None, active_tag_type = None ):
		Event_Base.__init__( self, EVT_COMMAND_AE_TAG_ASSOCIATION_CREATED, data_objs = data_objs , data = data, active_tag_type = active_tag_type )



class Event_Tag_Association_Modified( Event_Base ):
	def __init__( self, data_objs = None ):
		Event_Base.__init__( self, EVT_COMMAND_AE_TAG_ASSOCIATION_MODIFIED, data_objs = data_objs )



class Event_Tag_Association_Updated( Event_Base ):
	def __init__( self, data_objs = None, active_tag_type = None, use_clip_column = False ):
		Event_Base.__init__( self, EVT_COMMAND_AE_TAG_ASSOCIATION_UPDATED, data_objs = data_objs, active_tag_type = active_tag_type, use_clip_column = use_clip_column )



class Event_Tag_Association_Deleted( Event_Base ):
	def __init__( self, data_objs = None, active_tag_type = None ):
		Event_Base.__init__( self, EVT_COMMAND_AE_TAG_ASSOCIATION_DELETED, data_objs = data_objs, active_tag_type = active_tag_type )


#named value events
class Event_Named_Value_Selected( Event_Base ):
	def __init__( self, data_objs = None ):
		Event_Base.__init__( self, EVT_COMMAND_AE_NAMED_VALUE_SELECT, data_objs = data_objs )

class Event_Named_Value_Created( Event_Base ):
	def __init__( self, data_objs = None ):
		Event_Base.__init__( self, EVT_COMMAND_AE_NAMED_VALUED_CREATED, data_objs = data_objs )


class Event_Named_Value_Renamed( Event_Base ):
	def __init__( self, data_objs = None ):
		Event_Base.__init__( self, EVT_COMMAND_AE_NAMED_VALUED_RENAMED, data_objs = data_objs )


class Event_Named_Value_Deleted( Event_Base ):
	def __init__( self, data_objs = None ):
		Event_Base.__init__( self, EVT_COMMAND_AE_NAMED_VALUED_DELETED, data_objs = data_objs )

class Event_Named_Value_Modified( Event_Base ):
	def __init__( self, data_objs = None ):
		Event_Base.__init__( self, EVT_COMMAND_AE_NAMED_VALUED_MODIFIED, data_objs = data_objs )


#rig bones events
class Event_Rig_Bone_Selected( Event_Base ):
	def __init__( self, data_objs = None ):
		Event_Base.__init__( self, EVT_COMMAND_AE_RIG_BONE_SELECT, data_objs = data_objs )


class Event_Rig_Bone_Modified( Event_Base ):
	def __init__( self, data_objs = None ):
		Event_Base.__init__( self, EVT_COMMAND_AE_RIG_BONE_MODIFIED, data_objs = data_objs )

#rig aux data events
class Event_Rig_Aux_Data_Selected( Event_Base ):
	def __init__( self, data_objs = None ):
		Event_Base.__init__( self, EVT_COMMAND_AE_RIG_AUX_DATA_SELECT, data_objs = data_objs )


class Event_Rig_Aux_Data_Modified( Event_Base ):
	def __init__( self, data_objs = None ):
		Event_Base.__init__( self, EVT_COMMAND_AE_RIG_AUX_DATA_MODIFIED, data_objs = data_objs )


class Event_Rig_Aux_Data_Deleted( Event_Base ):
	def __init__( self, data_objs = None ):
		Event_Base.__init__( self, EVT_COMMAND_AE_RIG_AUX_DATA_DELETED, data_objs = data_objs )


#modifier events
class Event_Modifier_Selected( Event_Base ):
	def __init__( self, data_objs = None ):
		Event_Base.__init__( self, EVT_COMMAND_AE_MODIFIER_SELECT, data_objs = data_objs )


class Event_Modifier_Modified( Event_Base ):
	def __init__( self, data_objs = None ):
		Event_Base.__init__( self, EVT_COMMAND_AE_MODIFIER_MODIFIED, data_objs = data_objs )

class Event_Modifier_Deleted( Event_Base ):
	def __init__( self, data_objs = None ):
		Event_Base.__init__( self, EVT_COMMAND_AE_MODIFIER_DELETED, data_objs = data_objs )


#node graph dependance events
class Event_Node_Graph_Dependents_Modified( Event_Base ):
	def __init__( self, new_name = None ):
		Event_Base.__init__( self, EVT_COMMAND_AE_NODE_GRAPH_DEPENDENTS_MODIFIED, new_name = new_name )



#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
## Manager ##
#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

class Manager( object ):
	"""
	Class for event manager object.

	*Arguments:*
		* ``doc`` -active animation object

	*Keyword Arguments:*
		* ``none``
	"""

	def __init__( self, doc ):
		self.doc = doc
		self.managed_controls = set( )
		self.current_event = None


	#anim set modified
	#-----------------------------------------------------
	def register_control( self, ctrl ):
		self.managed_controls.add( ctrl )


	def unregister_control( self, ctrl ):
		self.managed_controls.discard( ctrl )


	#-----------------------------------------------------
	def post_clip_select_event( self, data_objs, properties_update = True ):
		"""
		This method posts clip select custom event, also updates recent selected
		data objects and the properties pane.

		*Arguments:*
			* ``data_objs`` -selected clip data objects

		*Keyword Arguments:*
			* ``properties_update`` - Boolean to update the properties pane

		*Returns:*
			* ``none``
		"""

		event = Event_Clip_Select( data_objs )

		for ctrl in self.managed_controls:
			ctrl.SafelyProcessEvent( event.Clone( ) )

		#update selected object and refresh properties pane
		self.update_sel_obj_and_prop_pane( data_objs, properties_update = properties_update )

		#refresh triggers timeline, after updating the cureent selected clip item
		doc = AnimationEditor.get_active_document( )
		if hasattr( doc, 'anim_triggers_timeline'):
			doc.anim_triggers_timeline.refresh_ui( )


	def post_keyword_display_event( self ):
		event = Event_Keywords_Display( )


	def post_clip_update_event( self, data_objs ):
		"""
		This method posts clip select custom event, also updates recent selected
		data objects and the properties pane.

		*Arguments:*
			* ``data_objs`` -selected clip data objects

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``none``
		"""

		event = Event_Clip_Update( data_objs )

		for ctrl in self.managed_controls:
			ctrl.SafelyProcessEvent( event.Clone( ) )

		#update selected object and refresh properties pane
		self.update_sel_obj_and_prop_pane( data_objs )

	#-----------------------------------------------------
	def post_rig_bone_select_event( self, data_objs, properties_update = True ):
		"""
		This method posts clip select custom event, also updates recent selected
		data objects and the properties pane.

		*Arguments:*
			* ``data_objs`` -selected clip data objects

		*Keyword Arguments:*
			* ``properties_update`` - Boolean to update the properties pane

		*Returns:*
			* ``none``
		"""

		event = Event_Rig_Bone_Selected( data_objs )

		for ctrl in self.managed_controls:
			ctrl.SafelyProcessEvent( event.Clone( ) )

		#update selected object and refresh properties pane
		self.update_sel_obj_and_prop_pane( data_objs, properties_update = properties_update )



	def post_rig_bone_modified_event( self, data_objs ):
		"""
		This method posts clip select custom event, also updates recent selected
		data objects and the properties pane.

		*Arguments:*
			* ``data_objs`` -selected clip data objects

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``none``
		"""

		event = Event_Rig_Bone_Modified( data_objs )

		for ctrl in self.managed_controls:
			ctrl.SafelyProcessEvent( event.Clone( ) )

		#update selected object and refresh properties pane
		self.update_sel_obj_and_prop_pane( data_objs )


	def post_modifier_select_event( self, data_objs ):
		"""
		This method posts state tag select custom event, also updates recent selected
		data objects and the properties pane.

		*Arguments:*
			* ``data_objs`` -selected state tag data objects

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``none``
		"""

		event = Event_Modifier_Selected( data_objs )

		for ctrl in self.managed_controls:
			ctrl.SafelyProcessEvent( event.Clone( ) )

		#update selected object and refresh properties pane
		self.update_sel_obj_and_prop_pane( data_objs )

	#post modifier data events
	def post_modifier_deleted_event( self, data_objs ):
		"""
		This method posts blend tree select custom event, also updates recent selected
		data objects and the properties pane.

		*Arguments:*
			* ``data_objs`` -selected blend tree data objects

		*Keyword Arguments:*
			* ``<none>``

		*Returns:*
			* ``none``
		"""

		event = Event_Modifier_Deleted( data_objs )
		doc = AnimationEditor.get_active_document( )

		for ctrl in self.managed_controls:
			ctrl.SafelyProcessEvent( event.Clone( ) )

		#update selected object and refresh properties pane
		self.update_sel_obj_and_prop_pane( [ None ] )


	def post_state_tag_select_event( self, data_objs ):
		"""
		This method posts state tag select custom event, also updates recent selected
		data objects and the properties pane.

		*Arguments:*
			* ``data_objs`` -selected state tag data objects

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``none``
		"""

		event = Event_State_Tag_Select( data_objs )

		for ctrl in self.managed_controls:
			ctrl.SafelyProcessEvent( event.Clone( ) )

		#update selected object and refresh properties pane
		self.update_sel_obj_and_prop_pane( data_objs )


	def post_state_tag_created_event( self, data_objs = None ):
		"""
		This method posts state tag created custom event.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``data_objs`` -selected state tag data objects

		*Returns:*
			* ``none``
		"""

		event = Event_State_Tag_Created( data_objs )

		for ctrl in self.managed_controls:
			ctrl.SafelyProcessEvent( event.Clone( ) )

		#update selected object and refresh properties pane
		#self.update_sel_obj_and_prop_pane( data_obj )


	def post_tag_modified_event( self, data_objs ):
		"""
		This method posts generic tag modified custom event, also updates recent selected
		data objects and the properties pane.

		*Arguments:*
			* ``data_objs`` -selected tag data objects

		*Keyword Arguments:*
			``none``

		*Returns:*
			* ``none``
		"""

		event = Event_Tag_Modified( data_objs )

		for ctrl in self.managed_controls:
			ctrl.SafelyProcessEvent( event.Clone( ) )

		#update selected object and refresh properties pane
		self.update_sel_obj_and_prop_pane( data_objs )


	def post_state_tag_renamed_event( self, data_objs ):
		"""
		This method posts state tag renamed custom event, also updates recent selected
		data objects and the properties pane.

		*Arguments:*
			* ``data_objs`` -selected state tag data objects

		*Keyword Arguments:*
			``none``

		*Returns:*
			* ``none``
		"""

		event = Event_State_Tag_Renamed( data_objs )

		for ctrl in self.managed_controls:
			ctrl.SafelyProcessEvent( event.Clone( ) )

		#update selected object and refresh properties pane
		self.update_sel_obj_and_prop_pane( data_objs )


	def post_state_tag_delete_event( self, data_objs ):
		"""
		This method posts state tag deleted custom event, also updates recent selected
		data objects and the properties pane.

		*Arguments:*
			* ``data_objs`` -selected state tag data objects

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``none``
		"""

		event = Event_State_Tag_Deleted( data_objs )

		for ctrl in self.managed_controls:
			ctrl.SafelyProcessEvent( event.Clone( ) )

		#update selected object and refresh properties pane
		self.update_sel_obj_and_prop_pane( data_objs )


	def post_action_tag_select_event( self, data_objs ):
		"""
		This method posts action tag select custom event, also updates recent selected
		data objects and the properties pane.

		*Arguments:*
			* ``data_objs`` -selected action tag data objects

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``none``
		"""

		event = Event_Action_Tag_Select( data_objs )

		for ctrl in self.managed_controls:
			ctrl.SafelyProcessEvent( event.Clone( ) )

		#update selected object and refresh properties pane
		self.update_sel_obj_and_prop_pane( data_objs )


	def post_action_tag_created_event( self, data_objs = None ):
		"""
		This method posts action tag created custom event.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``data_objs`` -selected action tag data objects

		*Returns:*
			* ``none``
		"""

		event = Event_Action_Tag_Created( data_objs )

		for ctrl in self.managed_controls:
			ctrl.SafelyProcessEvent( event.Clone( ) )

		#update selected object and refresh properties pane
		#self.update_sel_obj_and_prop_pane( data_obj )


	def post_action_tag_renamed_event( self, data_objs ):
		"""
		This method posts action tag renamed custom event, also updates recent selected
		data objects and the properties pane.

		*Arguments:*
			* ``data_objs`` -selected action tag data objects

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``none``
		"""

		event = Event_Action_Tag_Renamed( data_objs )

		for ctrl in self.managed_controls:
			ctrl.SafelyProcessEvent( event.Clone( ) )

		#update selected object and refresh properties pane
		self.update_sel_obj_and_prop_pane( data_objs )


	def post_action_tag_delete_event( self, data_objs ):
		"""
		This method posts action tag deleted custom event, also updates recent selected
		data objects and the properties pane.

		*Arguments:*
			* ``data_objs`` -selected action tag data objects

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``none``
		"""

		event = Event_Action_Tag_Deleted( data_objs )

		for ctrl in self.managed_controls:
			ctrl.SafelyProcessEvent( event.Clone( ) )

		#update selected object and refresh properties pane
		self.update_sel_obj_and_prop_pane( data_objs )



	#post control filter events
	def post_control_filter_select_event( self, data_objs ):
		"""
		This method posts control filter select custom event, also updates recent selected
		data objects and the properties pane.

		*Arguments:*
			* ``data_objs`` -selected control filter data objects

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``none``
		"""

		event = Event_Control_Filter_Select( data_objs )

		for ctrl in self.managed_controls:
			ctrl.SafelyProcessEvent( event.Clone( ) )

		#update selected object and refresh properties pane
		self.update_sel_obj_and_prop_pane( data_objs )


	def post_control_filter_created_event( self, data_objs ):
		"""
		This method posts control filter created custom event, also updates recent selected
		data objects and the properties pane.

		*Arguments:*
			* ``data_objs`` -selected control filter data objects

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``none``
		"""

		event = Event_Control_Filter_Created( data_objs )

		for ctrl in self.managed_controls:
			ctrl.SafelyProcessEvent( event.Clone( ) )

		#update selected object and refresh properties pane
		self.update_sel_obj_and_prop_pane( data_objs )


	def post_control_filter_renamed_event( self, data_objs, old_name ):
		"""
		This method posts control filter renamed custom event, also updates recent selected
		data objects and the properties pane.

		*Arguments:*
			* ``data_objs`` -selected control filter data objects

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``none``
		"""

		event = Event_Control_Filter_Renamed( data_objs, old_name )

		for ctrl in self.managed_controls:
			ctrl.SafelyProcessEvent( event.Clone( ) )

		#update selected object and refresh properties pane
		self.update_sel_obj_and_prop_pane( data_objs )


	def post_control_filter_deleted_event( self, data_objs ):
		"""
		This method posts control filter deleted custom event, also updates recent selected
		data objects and the properties pane.

		*Arguments:*
			* ``data_objs`` -selected control filter data objects

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``none``
		"""

		event = Event_Control_Filter_Deleted( data_objs )

		for ctrl in self.managed_controls:
			ctrl.SafelyProcessEvent( event.Clone( ) )

		#update selected object and refresh properties pane
		self.update_sel_obj_and_prop_pane( data_objs )


	def post_control_filter_modified_event( self, data_objs ):
		"""
		This method posts control filter deleted custom event, also updates recent selected
		data objects and the properties pane.

		*Arguments:*
			* ``data_objs`` -selected control filter data objects

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``none``
		"""

		event = Event_Control_Filter_Modified( data_objs )

		for ctrl in self.managed_controls:
			ctrl.SafelyProcessEvent( event.Clone( ) )

		#update selected object and refresh properties pane
		self.update_sel_obj_and_prop_pane( data_objs )


	#post control parameter events
	def post_control_parameter_select_event( self, data_objs ):
		"""
		This method posts control parameter select custom event, also updates recent selected
		data objects and the properties pane.

		*Arguments:*
			* ``data_objs`` -selected control parameter data objects

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``none``
		"""

		event = Event_Control_Parameter_Select( data_objs )

		for ctrl in self.managed_controls:
			ctrl.SafelyProcessEvent( event.Clone( ) )

		#update selected object and refresh properties pane
		self.update_sel_obj_and_prop_pane( data_objs )


	def post_control_parameter_created_event( self, data_objs ):
		"""
		This method posts control parameter created custom event, also updates recent selected
		data objects and the properties pane.

		*Arguments:*
			* ``data_objs`` -selected control parameter data objects

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``none``
		"""

		event = Event_Control_Parameter_Created( data_objs )

		for ctrl in self.managed_controls:
			ctrl.SafelyProcessEvent( event.Clone( ) )

		#update selected object and refresh properties pane
		self.update_sel_obj_and_prop_pane( data_objs )


	def post_control_parameter_renamed_event( self, data_objs, old_name ):
		"""
		This method posts control parameter renamed custom event, also updates recent selected
		data objects and the properties pane.

		*Arguments:*
			* ``data_objs`` -selected control parameter data objects

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``none``
		"""

		event = Event_Control_Parameter_Renamed( data_objs, old_name )

		for ctrl in self.managed_controls:
			ctrl.SafelyProcessEvent( event.Clone( ) )

		#update selected object and refresh properties pane
		self.update_sel_obj_and_prop_pane( data_objs )


	def post_control_parameter_deleted_event( self, data_objs ):
		"""
		This method posts control parameter deleted custom event, also updates recent selected
		data objects and the properties pane.

		*Arguments:*
			* ``data_objs`` -selected control parameter data objects

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``none``
		"""

		event = Event_Control_Parameter_Deleted( data_objs )

		for ctrl in self.managed_controls:
			ctrl.SafelyProcessEvent( event.Clone( ) )

		#update selected object and refresh properties pane
		self.update_sel_obj_and_prop_pane( data_objs )


	def post_control_parameter_modified_event( self, data_objs ):
		"""
		This method posts control parameter deleted custom event, also updates recent selected
		data objects and the properties pane.

		*Arguments:*
			* ``data_objs`` -selected control parameter data objects

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``none``
		"""

		event = Event_Control_Parameter_Modified( data_objs )

		for ctrl in self.managed_controls:
			ctrl.SafelyProcessEvent( event.Clone( ) )

		#update selected object and refresh properties pane
		self.update_sel_obj_and_prop_pane( data_objs )


	#post state machine events
	def post_state_machine_select_event( self, data_objs, properties_update = True ):
		"""
		This method posts state machine select custom event, also updates recent selected
		data objects and the properties pane.

		*Arguments:*
			* ``data_objs`` -selected state machine data objects

		*Keyword Arguments:*
			* ``properties_update`` - Boolean to update the properties pane

		*Returns:*
			* ``none``
		"""

		event = Event_State_Machine_Select( data_objs )

		for ctrl in self.managed_controls:
			ctrl.SafelyProcessEvent( event.Clone( ) )

		#update selected object and refresh properties pane
		self.update_sel_obj_and_prop_pane( data_objs, properties_update = properties_update )


	def post_state_machine_load_event( self, data_objs, owner = None, dependent = None ):
		"""
		This method posts state machine select custom event, also updates recent selected
		data objects and the properties pane.

		*Arguments:*
			* ``data_objs`` -selected state machine data objects

		*Keyword Arguments:*
			* ``owner`` - What pane is posting this event
			* ``dependent`` - What owning/parent node graph is loading this node graph

		*Returns:*
			* ``none``
		"""

		event = Event_State_Machine_Load( data_objs, owner = owner, dependent = dependent )

		for ctrl in self.managed_controls:
			ctrl.SafelyProcessEvent( event.Clone( ) )

		#update selected node graph loaded
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		doc.selection_manager.set_recent_node_graph_loaded( data_objs[0] )


	def post_state_machine_created_event( self, data_objs ):
		"""
		This method posts state machine created custom event, also updates recent selected
		data objects and the properties pane.

		*Arguments:*
			* ``data_objs`` -selected state machine data objects

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``none``
		"""

		event = Event_State_Machine_Created( data_objs )

		for ctrl in self.managed_controls:
			ctrl.SafelyProcessEvent( event.Clone( ) )

		#update selected object and refresh properties pane
		self.update_sel_obj_and_prop_pane( data_objs )


	def post_state_machine_renamed_event( self, data_objs, old_name = None, new_name = None ):
		"""
		This method posts state machine renamed custom event, also updates recent selected
		data objects and the properties pane.

		*Arguments:*
			* ``data_objs`` -selected state machine data objects

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``none``
		"""

		event = Event_State_Machine_Renamed( data_objs, old_name, new_name )

		for ctrl in self.managed_controls:
			ctrl.SafelyProcessEvent( event.Clone( ) )

		#update selected object and refresh properties pane
		self.update_sel_obj_and_prop_pane( data_objs )


	def post_state_machine_deleted_event( self, data_objs ):
		"""
		This method posts state machine deleted custom event, also updates recent selected
		data objects and the properties pane.

		*Arguments:*
			* ``data_objs`` -selected state machine data objects

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``none``
		"""

		event = Event_State_Machine_Deleted( data_objs )

		for ctrl in self.managed_controls:
			ctrl.SafelyProcessEvent( event.Clone( ) )

		#update selected object and refresh properties pane
		self.update_sel_obj_and_prop_pane( [ None ] )


	def post_state_machine_modified_event( self, data_objs ):
		"""
		This method posts state machine deleted custom event, also updates recent selected
		data objects and the properties pane.

		*Arguments:*
			* ``data_objs`` -selected state machine data objects

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``none``
		"""

		event = Event_State_Machine_Modified( data_objs )

		for ctrl in self.managed_controls:
			ctrl.SafelyProcessEvent( event.Clone( ) )

		#update selected object and refresh properties pane
		self.update_sel_obj_and_prop_pane( data_objs )


	#post blend tree events
	def post_blend_tree_select_event( self, data_objs, properties_update = True ):
		"""
		This method posts blend tree select custom event, also updates recent selected
		data objects and the properties pane.

		*Arguments:*
			* ``data_objs`` -selected blend tree data objects

		*Keyword Arguments:*
			* ``properties_update`` - Boolean to update the properties pane

		*Returns:*
			* ``none``
		"""

		event = Event_Blend_Tree_Select( data_objs )

		for ctrl in self.managed_controls:
			ctrl.SafelyProcessEvent( event.Clone( ) )

		#update selected object and refresh properties pane
		self.update_sel_obj_and_prop_pane( data_objs, properties_update = properties_update )

	#post rig aux data events
	def post_rig_aux_data_select_event( self, data_objs ):
		"""
		This method posts blend tree select custom event, also updates recent selected
		data objects and the properties pane.

		*Arguments:*
			* ``data_objs`` -selected blend tree data objects

		*Keyword Arguments:*
			* ``<none>``

		*Returns:*
			* ``none``
		"""

		event = Event_Rig_Aux_Data_Selected( data_objs )
		doc = AnimationEditor.get_active_document( )

		for ctrl in self.managed_controls:
			ctrl.SafelyProcessEvent( event.Clone( ) )

		#update selected object and refresh properties pane
		self.update_sel_obj_and_prop_pane( data_objs )
		if hasattr( doc, 'rig_bones_pane'):
			doc.rig_bones_pane.refresh_ui( )


	#post rig aux data events
	def post_rig_aux_data_modified_event( self, data_objs ):
		"""
		This method posts blend tree select custom event, also updates recent selected
		data objects and the properties pane.

		*Arguments:*
			* ``data_objs`` -selected blend tree data objects

		*Keyword Arguments:*
			* ``<none>``

		*Returns:*
			* ``none``
		"""

		event = Event_Rig_Aux_Data_Modified( data_objs )
		doc = AnimationEditor.get_active_document( )

		for ctrl in self.managed_controls:
			ctrl.SafelyProcessEvent( event.Clone( ) )

		#update selected object and refresh properties pane
		self.update_sel_obj_and_prop_pane( data_objs )
		if hasattr( doc, 'rig_bones_pane'):
			doc.rig_bones_pane.refresh_ui( )


	#post rig aux data events
	def post_rig_aux_data_deleted_event( self, data_objs ):
		"""
		This method posts blend tree select custom event, also updates recent selected
		data objects and the properties pane.

		*Arguments:*
			* ``data_objs`` -selected blend tree data objects

		*Keyword Arguments:*
			* ``<none>``

		*Returns:*
			* ``none``
		"""

		event = Event_Rig_Aux_Data_Deleted( data_objs )
		doc = AnimationEditor.get_active_document( )

		for ctrl in self.managed_controls:
			ctrl.SafelyProcessEvent( event.Clone( ) )

		#update selected object and refresh properties pane
		self.update_sel_obj_and_prop_pane( [ None ] )
		if hasattr( doc, 'rig_bones_pane'):
			doc.rig_bones_pane.refresh_ui( )


	def post_blend_tree_load_event( self, data_objs, owner = None, dependent = None ):
		"""
		This method posts blend tree select custom event, also updates recent selected
		data objects and the properties pane.

		*Arguments:*
			* ``data_objs`` -selected blend tree data objects

		*Keyword Arguments:*
			* ``owner`` - What pane is posting this event
			* ``dependent`` - What owning/parent node graph is loading this node graph

		*Returns:*
			* ``none``
		"""

		event = Event_Blend_Tree_Load( data_objs, owner = owner, dependent = dependent )

		for ctrl in self.managed_controls:
			ctrl.SafelyProcessEvent( event.Clone( ) )

		#update selected node graph loaded
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		doc.selection_manager.set_recent_node_graph_loaded( data_objs[0] )


	def post_blend_tree_created_event( self, data_objs ):
		"""
		This method posts blend tree created custom event, also updates recent selected
		data objects and the properties pane.

		*Arguments:*
			* ``data_objs`` -selected blend tree data objects

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``none``
		"""

		event = Event_Blend_Tree_Created( data_objs )

		for ctrl in self.managed_controls:
			ctrl.SafelyProcessEvent( event.Clone( ) )

		#update selected object and refresh properties pane
		self.update_sel_obj_and_prop_pane( data_objs )


	def post_blend_tree_renamed_event( self, data_objs, old_name = None, new_name = None ):
		"""
		This method posts blend tree renamed custom event, also updates recent selected
		data objects and the properties pane.

		*Arguments:*
			* ``data_objs`` -selected blend tree data objects

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``none``
		"""

		event = Event_Blend_Tree_Renamed( data_objs, old_name, new_name )

		for ctrl in self.managed_controls:
			ctrl.SafelyProcessEvent( event.Clone( ) )

		#update selected object and refresh properties pane
		self.update_sel_obj_and_prop_pane( data_objs )


	def post_blend_tree_deleted_event( self, data_objs ):
		"""
		This method posts blend tree deleted custom event, also updates recent selected
		data objects and the properties pane.

		*Arguments:*
			* ``data_objs`` -selected blend tree data objects

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``none``
		"""

		event = Event_Blend_Tree_Deleted( data_objs )

		for ctrl in self.managed_controls:
			ctrl.SafelyProcessEvent( event.Clone( ) )

		#update selected object and refresh properties pane
		self.update_sel_obj_and_prop_pane( [ None ] )


	def post_blend_tree_modified_event( self, data_objs ):
		"""
		This method posts blend tree deleted custom event, also updates recent selected
		data objects and the properties pane.

		*Arguments:*
			* ``data_objs`` -selected blend tree data objects

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``none``
		"""

		event = Event_Blend_Tree_Modified( data_objs )

		for ctrl in self.managed_controls:
			ctrl.SafelyProcessEvent( event.Clone( ) )

		#update selected object and refresh properties pane
		self.update_sel_obj_and_prop_pane( data_objs )


	#post group events
	def post_group_select_event( self, data_objs, owner = None, properties_update = True ):
		"""
		This method posts group select custom event, also updates recent selected
		data objects and the properties pane and sets animation set preview group.

		*Arguments:*
			* ``data_objs`` - Selected group data objects

		*Keyword Arguments:*
			* ``owner``		       - The id of the pane that called this event
			* ``properties_update`` - Boolean to update the properties pane

		*Returns:*
			* ``none``
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		event = Event_Group_Select( data_objs, owner = owner )

		for ctrl in self.managed_controls:
			ctrl.SafelyProcessEvent( event.Clone( ) )

		#update the preview pane to show the mesh and rig relative to the anim set
		if owner in [ ctg.ae2.ui.const.PANE_ID_ANIM_SETS, ctg.ae2.ui.const.PANE_ID_TAG_ASSOC, ctg.ae2.ui.const.PANE_ID_ANIM_ASSET_MANAGER ]:
			if data_objs:
				if len( data_objs ) == 1:
					if data_objs[0]:
						# update the doc and preview pane
						group_name = data_objs[0].get_name( )
						if not group_name == doc.active_group:

							# set the last active group preference
							ctg.prefs.user[ "session.anim_set_tree_active_group" ] = group_name

							doc.active_group = group_name
							doc.set_preview_group( group_name )

							# refresh
							if hasattr( doc, 'preview_pane' ):
								doc.preview_pane.refresh_ui( )

							print 'Set preview group: {0}'.format( doc.active_group )

		#update selected object and refresh properties pane
		self.update_sel_obj_and_prop_pane( data_objs, properties_update = properties_update )
		self.refresh_tag_association_pane( )


	def refresh_tag_association_pane( self ):
		#This is temp untill we figure out why events are not getting posted"
		doc = AnimationEditor.get_active_document( )
		if hasattr( doc, 'tag_association_pane' ):
			doc.tag_association_pane.refresh_ui( )

	def add_to_catelog( self, data_objs ):
		#This is temp untill we figure out why events are not getting posted"
		doc = AnimationEditor.get_active_document( )
		if hasattr( doc, 'tag_association_pane' ):
			doc.tag_association_pane.add_to_catelog( objs = data_objs )

	def remove_from_catelog( self, data_objs ):
		#This is temp untill we figure out why events are not getting posted"
		doc = AnimationEditor.get_active_document( )
		if hasattr( doc, 'tag_association_pane' ):
			doc.tag_association_pane.remove_from_catelog( objs = data_objs )


	def post_group_created_event( self, data_objs = None, group_name = None, set_name = None ):
		"""
		This method posts group created custom event, also updates recent selected
		data objects and the properties pane.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``data_objs`` 	-selected group data objects
			* ``group_name`` 	-animation group name.
			* ``set_name`` 	-animation set name.

		*Returns:*
			* ``none``
		"""

		event = Event_Group_Created( data_objs, group_name, set_name )

		for ctrl in self.managed_controls:
			ctrl.SafelyProcessEvent( event.Clone( ) )

		#update selected object and refresh properties pane
		if data_objs:
			self.update_sel_obj_and_prop_pane( data_objs )

		self.refresh_tag_association_pane( )


	def post_group_renamed_event( self, data_objs, old_name, set_name = None, owner = None, properties_update = True ):
		"""
		This method posts group renamed custom event, also updates recent selected
		data objects and the properties pane and sets animation set preview group.

		*Arguments:*
			* ``data_objs`` -selected group data object.
			* ``old_name``  -selected group data object old name.

		*Keyword Arguments:*
			* ``set_name``			   - Name of the set the group is related to
			* ``owner``		         - The id of the pane that called this event
			* ``properties_update`` - Boolean to update the properties pane

		*Returns:*
			* ``none``
		"""

		event = Event_Group_Renamed( data_objs, old_name, set_name, owner = owner )

		for ctrl in self.managed_controls:
			ctrl.SafelyProcessEvent( event.Clone( ) )

		#update selected object and refresh properties pane
		if not data_objs[0] is None:
			if properties_update:
				self.update_sel_obj_and_prop_pane( data_objs )

		self.refresh_tag_association_pane( )


	def post_group_deleted_event( self, data_objs, group_name = None, set_name = None ):
		"""
		This method posts group deleted custom event.

		*Arguments:*
			* ``data_objs`` 	-selected group data object.

		*Keyword Arguments:*
			* ``group_name``  -selected group data object name.

		*Returns:*
			* ``none``
		"""

		event = Event_Group_Deleted( data_objs, group_name, set_name )

		for ctrl in self.managed_controls:
			ctrl.SafelyProcessEvent( event.Clone( ) )

		self.refresh_tag_association_pane( )
		#update selected object and refresh properties pane
		#self.update_sel_obj_and_prop_pane( data_objs )


	def post_group_modified_event( self, data_objs = None, group_name = None ):
		"""
		This method posts group modified custom event.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``data_objs`` 	-selected group data object.
			* ``group_name``  -selected group data object name.

		*Returns:*
			* ``none``
		"""

		event = Event_Group_Modified( data_objs, group_name )

		for ctrl in self.managed_controls:
			ctrl.SafelyProcessEvent( event.Clone( ) )


		#update selected object and refresh properties pane
		#self.update_sel_obj_and_prop_pane( data_objs )
		self.refresh_tag_association_pane( )


	def post_set_select_event( self, data_objs, owner = None, properties_update = True ):
		"""
		This method posts set select custom event, also updates recent selected
		data objects and the properties pane and sets animation set preview set.

		*Arguments:*
			* ``data_objs`` -selected set data objects.

		*Keyword Arguments:*
			* ``owner``             - The id of the Pane that called the event
			* ``properties_update`` - Bool to update the properties pane

		*Returns:*
			* ``none``
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		event = Event_Set_Select( data_objs, owner = owner )

		for ctrl in self.managed_controls:
			ctrl.SafelyProcessEvent( event.Clone( ) )


		#update the preview pane to show the mesh and rig relative to the anim set
		if owner in [ ctg.ae2.ui.const.PANE_ID_ANIM_SETS, ctg.ae2.ui.const.PANE_ID_TAG_ASSOC, ctg.ae2.ui.const.PANE_ID_ANIM_ASSET_MANAGER ]:
			if data_objs:
				if len( data_objs ) == 1:
					if data_objs[0]:

						# update the active set and preview pane
						set_name = data_objs[0].get_name( )
						if not set_name == doc.active_set:

							# set the last active set preference
							ctg.prefs.user[ "session.anim_set_tree_active_set" ] = set_name

							# update the document and preview set
							doc.active_set = set_name
							doc.set_preview_set( set_name )


							# update the preview pane mesh/rig
							if hasattr( doc, 'preview_pane' ):
								mesh = data_objs[0].get_set_preview_mesh( )
								rig  = data_objs[0].get_set_preview_rig( )
								doc.preview_pane.update_preview_mesh_rig( mesh, rig )

								# prop stuffs
								prop1 = data_objs[0].get_set_preview_prop(0)
								prop1_attach_tag = data_objs[0].get_set_preview_prop_attach_tag(0)
								prop1_character_tag = data_objs[0].get_set_preview_character_attach_tag(0)
								doc.preview_pane.update_preview_props_and_tags( prop1, prop1_attach_tag, prop1_character_tag, 0)

								prop2 = data_objs[0].get_set_preview_prop(1)
								prop2_attach_tag = data_objs[0].get_set_preview_prop_attach_tag(1)
								prop2_character_tag = data_objs[0].get_set_preview_character_attach_tag(1)
								doc.preview_pane.update_preview_props_and_tags( prop2, prop2_attach_tag, prop2_character_tag, 1)

								doc.preview_pane.refresh_ui( )
								print 'Set preview set: {0}'.format( doc.active_set )

		#update selected object and refresh properties pane
		self.update_sel_obj_and_prop_pane( data_objs, properties_update = properties_update )
		self.refresh_tag_association_pane( )


	def post_set_created_event( self, data_objs ):
		"""
		This method posts set created custom event, also updates recent selected
		data objects and the properties pane.

		*Arguments:*
			* ``data_objs`` -selected set data objects.

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``none``
		"""

		event = Event_Set_Created( data_objs )

		for ctrl in self.managed_controls:
			ctrl.SafelyProcessEvent( event.Clone( ) )

		#update selected object and refresh properties pane
		self.update_sel_obj_and_prop_pane( data_objs )


	def post_set_renamed_event( self, data_objs, old_name, owner = None ):
		"""
		This method posts set renamed custom event, also updates recent selected
		data objects and the properties pane.

		*Arguments:*
			* ``data_objs`` 	-selected set data objects.
			* ``old_name`` 	-selected set data object old name.

		*Keyword Arguments:*
			* ``owner``       -The id of the Pane that called the event

		*Returns:*
			* ``none``
		"""

		event = Event_Set_Renamed( data_objs, old_name, owner = owner )

		for ctrl in self.managed_controls:
			ctrl.SafelyProcessEvent( event.Clone( ) )

		#update selected object and refresh properties pane
		#self.update_sel_obj_and_prop_pane( data_objs )
		self.refresh_tag_association_pane( )


	def post_set_deleted_event( self, data_objs ):
		"""
		This method posts set deleted custom event.

		*Arguments:*
			* ``data_objs`` 	-selected set data objects.

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``none``
		"""

		event = Event_Set_Deleted( data_objs )

		for ctrl in self.managed_controls:
			ctrl.SafelyProcessEvent( event.Clone( ) )

		#update selected object and refresh properties pane
		#self.update_sel_obj_and_prop_pane( data_objs )
		self.refresh_tag_association_pane( )


	def post_set_modified_event( self, data_objs = None ):
		"""
		This method posts set modified custom event.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``data_objs`` 	-selected set data objects.

		*Returns:*
			* ``none``
		"""

		event = Event_Set_Modified( data_objs )

		for ctrl in self.managed_controls:
			ctrl.SafelyProcessEvent( event.Clone( ) )

		#update selected object and refresh properties pane
		#self.update_sel_obj_and_prop_pane( data_objs )
		self.refresh_tag_association_pane( )


	def post_tag_association_created_event( self, data_objs, data = None, active_tag_type = None, add_to_catelog = False ):
		"""
		This method posts tag association created custom event, also updates recent selected
		data objects and the properties pane.

		*Arguments:*
			* ``data_objs`` 	-selected tag association data objects.

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``none``
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		event = Event_Tag_Association_Created( data_objs, data = data, active_tag_type = active_tag_type )

		for ctrl in self.managed_controls:
			ctrl.SafelyProcessEvent( event.Clone( ) )

		self.update_sel_obj_and_prop_pane( data_objs )

		if add_to_catelog:
			self.add_to_catelog( data_objs )


	def post_tag_association_updated_event( self, data_objs, active_tag_type = None, use_clip_column = False ):
		"""
		This method posts tag association modified custom event, also updates recent selected
		data objects and the properties pane.

		*Arguments:*
			* ``data_objs`` 	-selected tag association data objects.

		*Keyword Arguments:*
			* ``active_tag_type`` - The active tag type
			* ``use_clip_column`` - Used to make the active column type clip if True

		*Returns:*
			* ``none``
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		event = Event_Tag_Association_Updated( data_objs, active_tag_type = active_tag_type, use_clip_column = use_clip_column )

		for ctrl in self.managed_controls:
			ctrl.SafelyProcessEvent( event.Clone( ) )


	def post_tag_association_modified_event( self, data_objs ):
		"""
		This method posts tag association modified custom event, also updates recent selected
		data objects and the properties pane.

		*Arguments:*
			* ``data_objs`` 	-selected tag association data objects.

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``none``
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		event = Event_Tag_Association_Modified( data_objs )

		for ctrl in self.managed_controls:
			ctrl.SafelyProcessEvent( event.Clone( ) )


	def post_tag_association_deleted_event( self, data_objs, active_tag_type = None ):
		"""
		This method posts tag association deleted custom event.

		*Arguments:*
			* ``data_objs`` 			-selected tag association data objects.

		*Keyword Arguments:*
			* ``active_tag_type`` 	-active animation tag type.

		*Returns:*
			* ``none``
		"""

		event = Event_Tag_Association_Deleted( data_objs, active_tag_type = active_tag_type )

		for ctrl in self.managed_controls:
			ctrl.SafelyProcessEvent( event.Clone( ) )

		self.update_sel_obj_and_prop_pane( data_objs )
		self.remove_from_catelog( data_objs )


	def post_redraw_event( self ):
		for ctrl in self.managed_controls:
			if hasattr( ctrl, 'redraw' ):
				ctrl.redraw( )


	def post_node_graph_dependents_modified_event( self, new_name ):
		"""
		This method posts state machine deleted custom event, also updates recent selected
		data objects and the properties pane.

		*Arguments:*
			* ``data_objs`` -selected state machine data objects

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``none``
		"""

		event = Event_Node_Graph_Dependents_Modified( new_name )

		for ctrl in self.managed_controls:
			ctrl.SafelyProcessEvent( event.Clone( ) )

		#update selected object and refresh properties pane
		#self.update_sel_obj_and_prop_pane( data_objs )



	def post_named_value_created_event( self, data_objs ):
		"""
		This method posts named value created custom event, also updates recent selected
		data objects and the properties pane.

		*Arguments:*
			* ``data_objs`` -created named values data objects

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``none``
		"""

		event = Event_Named_Value_Created( data_objs )

		for ctrl in self.managed_controls:
			ctrl.SafelyProcessEvent( event.Clone( ) )

		#update selected object and refresh properties pane
		self.update_sel_obj_and_prop_pane( data_objs )


	def post_named_value_selected_event( self, data_objs ):
		"""
		This method posts named value selected custom event, also updates recent selected
		data objects and the properties pane.

		*Arguments:*
			* ``data_objs`` -selected named value data objects

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``none``
		"""

		event = Event_Named_Value_Selected( data_objs )

		for ctrl in self.managed_controls:
			ctrl.SafelyProcessEvent( event.Clone( ) )

		#update selected object and refresh properties pane
		self.update_sel_obj_and_prop_pane( data_objs )



	def post_named_value_renamed_event( self, data_objs ):
		"""
		This method posts named value renamed custom event, also updates recent selected
		data objects and the properties pane.

		*Arguments:*
			* ``data_objs`` -renamed named value data objects

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``none``
		"""

		event = Event_Named_Value_Renamed( data_objs )

		for ctrl in self.managed_controls:
			ctrl.SafelyProcessEvent( event.Clone( ) )

		#update selected object and refresh properties pane
		self.update_sel_obj_and_prop_pane( data_objs )


	def post_named_value_deleted_event( self, data_objs ):
		"""
		This method posts named value deleted custom event, also updates recent selected
		data objects and the properties pane.

		*Arguments:*
			* ``data_objs`` -deleted named values objects data objects

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``none``
		"""

		event = Event_Named_Value_Deleted( data_objs )

		for ctrl in self.managed_controls:
			ctrl.SafelyProcessEvent( event.Clone( ) )

		#update selected object and refresh properties pane
		self.update_sel_obj_and_prop_pane( [ None ] )


	def post_named_value_modified_event( self, data_objs ):
		"""
		This method posts named value modified custom event, also updates recent selected
		data objects and the properties pane.

		*Arguments:*
			* ``data_objs`` -modified named value data objects

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``none``
		"""

		event = Event_Named_Value_Modified( data_objs )

		for ctrl in self.managed_controls:
			ctrl.SafelyProcessEvent( event.Clone( ) )

		#update selected object and refresh properties pane
		self.update_sel_obj_and_prop_pane( data_objs )


	def update_properties_pane( self ):
		"""
		This method updates the properties pane.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``none``
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		if hasattr( doc, 'animation_properties_pane' ):
			doc.animation_properties_pane.refresh_ui()


	def update_anim_sets_pane_selection(  self, post_event ):
		"""
		This method updates selection in animation sets pane.

		*Arguments:*
			* ``post_event`` -bool to whether post a selection event after selection or not.

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``none``
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		if hasattr( doc, 'animation_sets_pane' ):
			doc.animation_sets_pane.update_selection( post_event )


	def update_assetmanager_pane_selection( self, node_type, post_event ):
		"""
		This method updates selection for the asset manager pane.

		*Arguments:*
			* ``node_type`` 	-data objects node types for the current active tab in asset manager.
			* ``post_event`` 	-bool to whether post a selection event after selection or not.

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``none``
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		if hasattr( doc, 'asset_manager_pane' ):
			doc.asset_manager_pane.update_selection( node_type, post_event )


	def update_selected_object( self, data_objs ):
		"""
		This method updates recent selected data objects.

		*Arguments:*
			* ``data_objs`` -recent selected data objects.

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``none``
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		if hasattr( doc, 'selection_manager'):
			doc.selection_manager.set_selected_object( data_objs )




	def update_sel_obj_and_prop_pane( self, data_objs, properties_update = True ):
		"""
		This method updates recent selected data objects and the properties pane.

		*Arguments:*
			* ``data_objs`` -recent selected data objects.

		*Keyword Arguments:*
			* ``properties_update`` - Boolean to update the properties pane

		*Returns:*
			* ``none``
		"""

		#update selected object
		self.update_selected_object( data_objs )

		#refresh the properties pane
		if properties_update:
			self.update_properties_pane()



#Selection Manager
class Selection_Manager( object ):
	"""
	Class for selection manager object

	*Arguments:*
		* ``doc``  -Active animation document

	*Keyword Arguments:*
		* ``none``
	"""

	def __init__( self, doc ):
		self.doc = doc
		self.selected_objects = None

		#recent selected data objects by type
		self.recent_sel_sets	 						= None
		self.recent_sel_groups 						= None
		self.recent_sel_state_tags 				= None
		self.recent_sel_action_tags 				= None
		self.recent_sel_clips 						= None
		self.recent_sel_state_machines 			= None
		self.resent_sel_blend_trees				= None
		self.recent_sel_control_filters 			= None
		self.recent_sel_control_parameters 		= None
		self.recent_sel_tag_associations			= None
		self.recent_sel_tag_associations_col	= None
		self.recent_sel_graph_nodes 				= None
		self.recent_sel_graphs                 = None
		self.recent_sel_node_graph_loaded		= None
		self.recent_sel_named_values	         = None
		self.recent_sel_rig_bones	            = None
		self.recent_sel_rig_aux_data 		      = None
		self.recent_sel_modifiers 				   = None

		self.recent_selections 						= [ ]



	def set_selected_object( self, data_objs ):
		"""
		This method sets recent selected data objects based on the type.

		*Arguments:*
			* ``data_objs`` -list of data objects that has been recently selected.

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``none``
		"""

		data_obj_names = [ ]

		if not data_objs or not data_objs[0]:
			self.selected_objects = None
			self.set_recent_selections( None, data_obj_names )

			return

		if isinstance( data_objs[0], ctg.ae2.core.data.Clip_Item ):
			self.recent_sel_clips 					= data_objs
			for data_obj in data_objs:
				data_obj.selected_triggers = []

			if len( data_objs ) == 1:
				self.update_preview_clip( data_objs[0].get_name() )

		elif isinstance( data_objs[0], ctg.ae2.core.data.Set_Item ):
			self.recent_sel_sets 					= data_objs

		elif isinstance( data_objs[0], ctg.ae2.core.data.Group_Item ):
			self.recent_sel_groups 					= data_objs

		elif isinstance( data_objs[0], ctg.ae2.core.data.State_Tag_Item ):
			self.recent_sel_state_tags 			= data_objs

		elif isinstance( data_objs[0], ctg.ae2.core.data.Action_Tag_Item ):
			self.recent_sel_action_tags 			= data_objs

		elif isinstance( data_objs[0], ctg.ae2.core.data.State_Machine_Item ):
			self.recent_sel_state_machines 		= data_objs

		elif isinstance( data_objs[0], ctg.ae2.core.data.Blend_Tree_Item ):
			self.resent_sel_blend_trees 			= data_objs

		elif isinstance( data_objs[0], ctg.ae2.core.data.Control_Parameter_Item ):
			self.recent_sel_control_parameters 	= data_objs

		elif isinstance( data_objs[0], ctg.ae2.core.data.Control_Filter_Item ):
			self.recent_sel_control_filters 		= data_objs

		elif isinstance( data_objs[0], ctg.ae2.core.data.Tag_Association_Item ):
			self.recent_sel_tag_associations 	= data_objs
			data_objs[0].set_preview_tag_association( )
			clip_item = data_objs[0].get_clip_name( )
			self.update_preview_clip( clip_item, tag=data_objs[0] )

		elif isinstance( data_objs[0], vlib.ui.node_graph.node.Node ):
			self.recent_sel_graph_nodes			= data_objs

		elif isinstance( data_objs[0], ctg.ae2.core.data.Node_Graph_Tree_Item ):
			self.recent_sel_graphs			      = data_objs

		elif isinstance( data_objs[0], ctg.ae2.core.data.Anim_Named_Value_Item ):
			self.recent_sel_named_values		   = data_objs

		elif isinstance( data_objs[0], ctg.ae2.ui.panes.rig_bones_pane.Rig_Bone ):
			self.recent_sel_rig_bones		      = data_objs

		elif isinstance( data_objs[0], ctg.ae2.core.data.Modifier_Item ):
			self.recent_sel_modifiers		      = data_objs

		elif isinstance( data_objs[0], ctg.ae2.core.data.Rig_Aux_Data_Item ):

			doc = AnimationEditor.get_active_document( )
			if doc:
				doc.set_current_rig_aux_data( data_objs[0].get_name())

			self.recent_sel_rig_aux_data		   = data_objs


		if data_objs:
			if not None in data_objs:
				self.selected_objects = data_objs

		for obj in data_objs:
			if obj:
				if hasattr( obj, 'get_name' ):
					data_obj_names.append( obj.get_name( ) )
				elif hasattr( obj, 'get_bone_name' ):
					data_obj_names.append( obj.get_bone_name( ) )

		if self.recent_selections:
			if self.recent_selections[0]:
				if data_objs[0]:
					if data_objs[0].get_node_type() == self.recent_selections[0].keys()[0]:
						if self.recent_selections[0].values()[0] != data_obj_names:
							self.set_recent_selections( data_objs[0].get_node_type( ), data_obj_names )
					else:
						self.set_recent_selections( data_objs[0].get_node_type( ), data_obj_names )


	def get_recent_selections( self ):
		"""
		This method gets and returns a list of all recent selected data objects.
		This is a list containing dictionaries of selected objects node type as key
		and a list of data objects name as value.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``list`` - list of dictionaries of selected objects node type as key and a list of data objects name as value.
		"""

		return self.recent_selections


	def set_recent_selections( self, node_type, data_obj_names ):
		"""
		This method add recent selected to a list of all recent selected data objects.
		This is a list containing dictionaries of selected objects node type as key
		and a list of data objects name as value.

		*Arguments:*
			* ``node_type`` 		- node type for selected data objects.
			* ``data_obj_names`` - a list of selected data objects names.

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``none``
		"""

		self.recent_selections.insert( 0, { node_type : data_obj_names } )

		#Limit list in recent selections to last 30 of any type,
		#so that the list does not go nuts.
		self.recent_selections = self.recent_selections[ :30 ]


	def get_selected_objects( self ):
		"""
		This method gets and returns most recent selected data objects.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``list or None`` -list of most recent selected data objects or None
		"""

		return self.selected_objects


	def get_recent_sel_sets( self ):
		"""
		This method gets and returns most recent selected sets data objects.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``list or None`` -list of most recent selected sets data objects or None.
		"""

		return self.recent_sel_sets


	def get_recent_sel_modifiers( self ):
		"""
		This method gets and returns most recent selected modifiers data objects.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``list or None`` -list of most recent selected sets data objects or None.
		"""

		return self.recent_sel_modifiers



	def get_recent_sel_rig_aux_data( self ):
		"""
		This method gets and returns most recent selected rig aux data data objects.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``list or None`` -list of most recent selected sets data objects or None.
		"""

		return self.recent_sel_rig_aux_data


	def get_recent_sel_groups( self ):
		"""
		This method gets and returns most recent selected groups data objects.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``list or None`` -list of most recent selected groups data objects or None.
		"""

		return self.recent_sel_groups


	def set_recent_node_graph_loaded( self, data_obj ):
		"""
		Set up the recent loaded node graph

		*Arguments:*
			* ``data_obj`` ListerLib data container

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``none``
		"""

		self.recent_sel_node_graph_loaded = data_obj


	def get_recent_sel_node_graph_loaded( self ):
		"""
		This method gets and returns most recent loaded node graph.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``list or None`` -list of most recent selected groups data objects or None.
		"""

		return self.recent_sel_node_graph_loaded


	def get_recent_sel_clips( self ):
		"""
		This method gets and returns most recent selected clips data objects.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``list or None`` -list of most recent selected clips data objects or None.
		"""

		return self.recent_sel_clips


	def get_recent_sel_action_tags( self ):
		"""
		This method gets and returns most recent selected action tags data objects.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``list or None`` -list of most recent selected action tags data objects or None.
		"""

		return self.recent_sel_action_tags


	def get_recent_sel_state_tags( self ):
		"""
		This method gets and returns most recent selected state tags data objects.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``list or None`` -list of most recent selected state tags data objects or None.
		"""

		return self.recent_sel_state_tags


	def get_recent_sel_state_machines( self ):
		"""
		This method gets and returns most recent selected state machines data objects.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``list or None`` -list of most recent selected state machines data objects or None.
		"""

		return self.recent_sel_state_machines


	def get_recent_sel_blend_trees( self ):
		"""
		This method gets and returns most recent selected blend trees data objects.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``list or None`` -list of most recent selected blend trees data objects or None.
		"""

		return self.resent_sel_blend_trees


	def get_recent_sel_graph_nodes( self ):
		"""
		This method gets and returns most recent selected graph node objects.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``list or None`` -list of most recent selected graph node objects or None.
		"""

		return self.recent_sel_graph_nodes


	def get_recent_sel_graphs( self ):
		"""
		This method gets and returns most recent selected graph objects.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``list or None`` -list of most recent selected graph node objects or None.
		"""

		return self.recent_sel_graphs


	def get_recent_sel_rig_bones( self ):
		"""
		This method gets and returns most recent selected rig bones data objects.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``list or None`` -list of most recent selected rig bones data objects or None.
		"""

		return self.recent_sel_rig_bones


	def get_recent_sel_control_filters( self ):
		"""
		This method gets and returns most recent selected control filters data objects.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``list or None`` -list of most recent selected control filters data objects or None.
		"""

		return self.recent_sel_control_filter


	def get_recent_sel_control_paramters( self ):
		"""
		This method gets and returns most recent selected control parameters data objects.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``list or None`` -list of most recent selected control parameters data objects or None.
		"""

		return self.recent_sel_control_parameters


	def get_recent_sel_tag_associations( self ):
		"""
		This method gets and returns most recent selected tag associations data objects.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``list or None`` -list of most recent selected tag associations data objects or None.
		"""

		return self.recent_sel_tag_associations


	def get_recent_sel_named_values( self ):
		"""
		This method gets and returns most recent selected tag associations data objects.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``list or None`` -list of most recent selected tag associations data objects or None.
		"""

		return self.recent_sel_named_values


	def get_recent_sel_by_type( self, node_type ):
		"""
		This method gets and returns recent selected objects by node type.

		*Arguments:*
			* ``node_type`` -node type of recent selected objects.

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``list or None`` -list of recent selected objects of specified node type or None.
		"""

		recent_sel_objs = None
		if node_type == ctg.ae2.ui.const.NODE_TYPE_ANIM_CLIP:
			recent_sel_objs = self.get_recent_sel_clips()

		elif node_type == ctg.ae2.ui.const.NODE_TYPE_ANIM_SET_TREE:
			recent_sel_objs = self.get_recent_sel_sets()

		elif node_type == ctg.ae2.ui.const.NODE_TYPE_ANIM_GROUP_TREE:
			recent_sel_objs = self.get_recent_sel_groups()

		elif node_type == ctg.ae2.ui.const.NODE_TYPE_TAG_ACTION:
			recent_sel_objs = self.get_recent_sel_action_tags()

		elif node_type == ctg.ae2.ui.const.NODE_TYPE_TAG_STATE:
			recent_sel_objs = self.get_recent_sel_state_tags()

		elif node_type == ctg.ae2.ui.const.NODE_TYPE_TAG_ASSOCIATION:
			recent_sel_objs = self.get_recent_sel_tag_associations()

		elif node_type == ctg.ae2.ui.const.NODE_TYPE_ANIM_NAMED_VALUE:
			recent_sel_objs = self.get_recent_sel_named_values()

		elif node_type == ctg.ae2.ui.const.NODE_TYPE_MODIFIER:
			recent_sel_objs = self.get_recent_sel_modifiers( )

		elif node_type == ctg.ae2.ui.const.NODE_TYPE_RIG_AUX_DATA:
			recent_sel_objs = self.get_recent_sel_rig_aux_data( )

		elif node_type == ctg.ae2.ui.const.NODE_TYPE_RIG_BONE:
			recent_sel_objs = self.get_recent_sel_rig_bones( )

		return recent_sel_objs


	def get_item_from_collection( self, data_obj, name ):
		"""
		This method gets and returns data object from collections by name.

		*Arguments:*
			* ``data_obj`` -data object.
			* ``name`` 		-name of object to be check for.

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``data object or None`` -data object or None.
		"""
		doc = AnimationEditor.get_active_document()
		obj = None
		if not doc:
			return obj

		if isinstance( data_obj, ctg.ae2.core.data.Clip_Item ):
			obj = doc.clip_collection.get_item_by_name( name )

		elif isinstance( data_obj, ctg.ae2.core.data.Set_Item ):
			obj = doc.set_collection.get_item_by_name( name )

		elif isinstance( data_obj, ctg.ae2.core.data.Group_Item ):
			obj = doc.anim_group_collection.get_item_by_name( name )

		elif isinstance( data_obj, ctg.ae2.core.data.State_Tag_Item ):
			obj = doc.state_tag_collection.get_item_by_name( name )

		elif isinstance( data_obj, ctg.ae2.core.data.Action_Tag_Item ):
			obj = doc.action_tag_collection.get_item_by_name( name )

		elif isinstance( data_obj, ctg.ae2.core.data.State_Machine_Item ):
			obj = doc.state_machine_collection.get_item_by_name( name )

		elif isinstance( data_obj, ctg.ae2.core.data.Blend_Tree_Item ):
			obj = doc.blend_tree_collection.get_item_by_name( name )

		elif isinstance( data_obj, ctg.ae2.core.data.Control_Parameter_Item ):
			obj = doc.control_parameter_collection.get_item_by_name( name )

		elif isinstance( data_obj, ctg.ae2.core.data.Control_Filter_Item ):
			obj = doc.control_filter_collection.get_item_by_name( name )

		elif isinstance( data_obj, ctg.ae2.core.data.Tag_Association_Item ):
			obj = doc.tag_association_collection.get_item_by_name( name )

		elif isinstance( data_obj, ctg.ae2.core.data.Anim_Named_Value_Item ):
			obj = doc.named_values_collection.get_item_by_name( name )

		elif isinstance( data_obj, ctg.ae2.core.data.Modifier_Item ):
			obj = doc.modifier_collection.get_item_by_name( name )

		elif isinstance( data_obj, ctg.ae2.core.data.Rig_Aux_Data_Item ):
			obj = doc.rig_aux_data_collection.get_item_by_name( name )


		return obj


	def set_preview_anim( self, clip_name, tag=None ):
		doc = AnimationEditor.get_active_document( )
		if not doc:
			return

		if tag:
			if isinstance( tag, ctg.ae2.core.data.Tag_Association_Item ):
				try:
					return doc.set_preview_anim( clip_name, int( tag.get_uid( ) ) )
				except AttributeError:
					return None

			else:
				return None

		else:
			try:
				return doc.set_preview_anim( clip_name, -1 )
			except AttributeError:
				return None


		return None


	def update_preview_clip( self, preview_clip_name, tag=None ):
		"""
		This method updates animation preview clip and resets animation.

		*Arguments:*
			* ``preview_clip_name`` -name of animation clip to be previewed.

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``none``
		"""
		doc = AnimationEditor.get_active_document()
		if not doc:
			return

		if hasattr( doc, 'preview_pane' ):
			if doc.preview_pane.is_clip_playing( ):
				if tag:
					self.set_preview_anim( preview_clip_name, tag )
				else:
					self.set_preview_anim( preview_clip_name )

				doc.set_preview_clip( preview_clip_name )
				doc.preview_pane.reset_playing_clip( )
			else:
				if tag:
					self.set_preview_anim( preview_clip_name, tag )
				else:
					self.set_preview_anim( preview_clip_name )

				doc.set_preview_clip( preview_clip_name )
				doc.preview_pane.on_play( None )



