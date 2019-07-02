"""
Creates all of the base constraints for the characters upon asset_add.

*Author:*
	* Jon Logsdon, jon.logsdon@volition-inc.com, 6/4/2014 12:51:05 PM
"""


# Motionbuilder lib
from pyfbsdk import *
from pyfbsdk_additions import *

#vmobu
import vmobu
import core

class Mobu_Rig_Constraint_Builder:
	"""
	Builds constraints for proper roll bones when not using Control Rig or HIK.

	*Examples:* ::

		*>>> import Constraint_Converter
		*>>> Constraint_Converter.Mobu_Rig_Constraint_Builder().build_constraint()

	*Author:*
		* Jon Logsdon, jon.logsdon@volition-inc.com, 6/4/2014 12:41:36 PM
	"""
	
	def __init__( self ):
		self.curr_char = FBApplication( ).CurrentCharacter

		#Current namespace
		curr_char_namespace = self.curr_char.LongName.split( ":" )
		required_bones = [ ]

		#Objects needed for constraints
		self.shoulders = vmobu.core.get_objects_from_wildcard( curr_char_namespace[0] + ":*Shoulder", use_namespace=True )
		self.arms = vmobu.core.get_objects_from_wildcard( curr_char_namespace[ 0 ] + ":*Arm", use_namespace=True )
		self.arm_twists = vmobu.core.get_objects_from_wildcard( curr_char_namespace[ 0 ] + "*ArmTwist", use_namespace=True)
		self.hands = vmobu.core.get_objects_from_wildcard( curr_char_namespace[ 0 ] + ":*Hand", use_namespace=True)
		self.arm_rolls = vmobu.core.get_objects_from_wildcard( curr_char_namespace[ 0 ] + ":*ArmRoll", use_namespace=True )
		self.forearm_rolls = vmobu.core.get_objects_from_wildcard( curr_char_namespace[ 0 ] + ":*ForeArmRoll", use_namespace=True )
		self.up_legs = vmobu.core.get_objects_from_wildcard( curr_char_namespace[ 0 ] + ":*UpLeg", use_namespace=True )
		self.legs = vmobu.core.get_objects_from_wildcard( curr_char_namespace[ 0 ] + ":*Leg", use_namespace=True )
		self.up_leg_rolls = vmobu.core.get_objects_from_wildcard( curr_char_namespace[ 0 ] + ":*UpLegRoll", use_namespace=True )
		self.leg_rolls = vmobu.core.get_objects_from_wildcard( curr_char_namespace[ 0 ] + ":*LegRoll", use_namespace=True )
		self.up_vectors = vmobu.core.get_objects_from_wildcard( curr_char_namespace[ 0 ] + ":*UpVector", use_namespace=True )
		self.elbows = vmobu.core.get_objects_from_wildcard( curr_char_namespace[ 0 ] + ":*Elbow", use_namespace=True )
		self.knees = vmobu.core.get_objects_from_wildcard( curr_char_namespace[ 0 ] + ":*Knee", use_namespace=True )
		self.forearms = vmobu.core.get_objects_from_wildcard( curr_char_namespace[ 0 ] + ":*ForeArm", use_namespace=True )
		self.knee_targets = vmobu.core.get_objects_from_wildcard( curr_char_namespace[ 0 ] + ":*tag*KneeTarget*", use_namespace=True )
		self.elbow_targets = vmobu.core.get_objects_from_wildcard( curr_char_namespace[ 0 ] + ":*tag*ElbowTarget*", use_namespace=True )
		self.hips = vmobu.core.get_objects_from_wildcard( curr_char_namespace[0] + ":*Hips", use_namespace=True)
		self.feet = vmobu.core.get_objects_from_wildcard( curr_char_namespace[0] + ":*Foot", use_namespace=True )

		required_bones.append( self.arms )
		required_bones.append( self.hands )
		required_bones.append( self.arm_rolls )
		required_bones.append( self.forearm_rolls )
		required_bones.append( self.up_legs )
		required_bones.append( self.legs )
		required_bones.append( self.up_leg_rolls )
		required_bones.append( self.leg_rolls )
		required_bones.append( self.up_vectors)
		required_bones.append( self.elbows )
		required_bones.append( self.knees )
		required_bones.append( self.forearms )
		required_bones.append( self.knee_targets )
		required_bones.append( self.elbow_targets )

		for bone in required_bones:
			if isinstance( bone, FBModelSkeleton ):
				self.arms_list = []
				self.hand_list = []
				self.arm_roll_list = []
				self.forearm_roll_list = []
				self.up_leg_list = []
				self.leg_list = []
				self.up_leg_roll_list = []
				self.leg_roll_list = []
				self.up_vector_list = []
				self.elbow_list = []
				self.knee_list = []
				self.forearm_list = []
				self.knee_target_list = []
				self.elbow_target_list = []

				for arm in self.arms:
					if not "Fore" in arm.Name:
						self.arms_list.append(arm)

				for hand in self.hands:
					self.hand_list.append(hand)

				for arm_roll in self.arm_rolls:
					if not "Fore" in arm_roll.Name:
						self.arm_roll_list.append(arm_roll)

				for far in self.forearm_rolls:
					if "Fore" in far.Name:
						self.forearm_roll_list.append(far)

				for ul in self.up_legs:
					if "Up" in ul.Name:
						self.up_leg_list.append(ul)

				for leg in self.legs:
					if not "Up" in leg.Name:
						self.leg_list.append(leg)

				for ulr in self.up_leg_rolls:
					if "Up" in ulr.Name:
						self.up_leg_roll_list.append(ulr)

				for lr in self.leg_rolls:
					if not "Up" in lr.Name:
						self.leg_roll_list.append(lr)

				for uv in self.up_vectors:
					self.up_vector_list.append(uv)

				for elbow in self.elbows:
					self.elbow_list.append(elbow)

				for knee in self.knees:
					self.knee_list.append(knee)

				for forearm in self.forearms:
					self.forearm_list.append(forearm)

				for kt in self.knee_targets:
					self.knee_target_list.append(kt)

				for et in self.elbow_targets:
					self.elbow_target_list.append(et)

		#Relation constraints
		self.up_arm_exp_const = None
		self.forearm_exp_const = None
		self.leg_up_roll_exp_const = None
		self.leg_roll_exp_const = None
		self.elbow_exp_const = None
		self.knee_exp_const = None

		#Parent/Child constraints
		self.knee_position_const = None
		self.elbow_position_const = None
		self.aim_node_point_const = None
		self.spine_bend_point_const = None

		#Point constraints
		self.anim_controller_parent_const = None
		self.offset_parent_const = None
		self.spine_bend_parent_const = None
		self.aim_node_parent_const = None
		self.left_hand_prop_parent_const = None
		self.right_hand_prop_parent_const = None

		#Aim constraints
		self.left_up_vector_aim_const = None
		self.right_up_vector_aim_const = None

	def mute_proper_attributes( self, side ):
		"""
		Mutes proper properties on roll bones.

		*Arguments:*
			* ``side`` Side of the character.

		*Keyword Arguments:*
			* ``None``

		*Returns:*
			* ``None``

		*Author:*
			* Jon Logsdon, jon.logsdon@volition-inc.com, 7/9/2014 2:15:54 PM
		"""

		for forearm_roll in self.forearm_rolls:
			if "Ctrl" not in forearm_roll.LongName:
				if forearm_roll.ClassName() == 'FBModelSkeleton':
					forearm_rotation_prop = forearm_roll.PropertyList.Find( 'Lcl Rotation' )
					forearm_rotation_prop.SetMemberMuted(1, True)
					forearm_rotation_prop.SetMemberMuted(2, True)

		for up_leg_roll in self.up_leg_rolls:
			if "Ctrl" not in up_leg_roll.LongName:
				if up_leg_roll.ClassName() == 'FBModelSkeleton':
					upleg_roll_rotation_prop = up_leg_roll.PropertyList.Find( 'Lcl Rotation' )
					upleg_roll_rotation_prop.SetMemberMuted(1, True)
					upleg_roll_rotation_prop.SetMemberMuted(2, True)

		for arm_roll in self.arm_rolls:
			if "Ctrl" not in arm_roll.LongName:
				if arm_roll.ClassName() == 'FBModelSkeleton':
					arm_roll_rotation_prop = arm_roll.PropertyList.Find('Lcl Rotation')
					arm_roll_rotation_prop.SetMemberMuted(1, True)
					arm_roll_rotation_prop.SetMemberMuted(2, True)

	def find_animation_node( self, pParent, pName ):
		"""
		Finds the animation node associated to the relation constraint box created.
		
		*Arguments:*
			* ``pParent, pName`` Parent and name of function box of relation constraint
		
		*Keyword Arguments:*
			* ``None`` 
		
		*Returns:*
			* ``lResult`` The animation node associated.
		
		*Author:*
			* Jon Logsdon, jon.logsdon@volition-inc.com, 6/4/2014 12:44:40 PM
		"""
		
		lResult = None
		for lNode in pParent.Nodes:
			if lNode.Name == pName:
				lResult = lNode
				break
		return lResult

	def activate_const_anim_nodes( self, side, side2 ):
		"""
		Activates the anim nodes for the position constraints bound to the procedural relation constraints.

		*Arguments:*
			* ``side, side2`` Side of the character.

		*Keyword Arguments:*
			* ``None``

		*Returns:*
			* ``None``

		*Author:*
			* Jon Logsdon, jon.logsdon@volition-inc.com, 7/9/2014 2:15:54 PM
		"""

		for knee_target in self.knee_targets:
			if knee_target.Name.lower().startswith("tag_{0}".format(side)):
				target_weight_prop = self.knee_position_const.PropertyList.Find('{0}.Weight'.format(knee_target.LongName))
				target_weight_prop.Data = 0.0
				target_weight_prop.SetAnimated( True )

		for elbow_target in self.elbow_targets:
			if elbow_target.Name.lower().startswith("tag_{0}".format(side2)):
				target_weight_prop = self.elbow_position_const.PropertyList.Find('{0}.Weight'.format(elbow_target.LongName))
				target_weight_prop.Data = 0.0
				target_weight_prop.SetAnimated(True)

	def build_constraint( self ):
		"""
		Main wrapper function to build constraint system.

		*Arguments:*
			* ``None``

		*Keyword Arguments:*
			* ``None``

		*Returns:*
			* ``None``

		*Author:*
			* Jon Logsdon, jon.logsdon@volition-inc.com, 7/9/2014 2:15:54 PM
		"""

		side = ['left', 'right']
		side2 = ['lft', 'rgt']
		for i in range(0, len(side)):
			if i == 0:
				self.create_constraints( side[0], side2[0] )

			if i == 1:
				self.create_constraints(side[1], side2[1])

		self.set_linear_constraints()

	def activate_constraints( self ):
		"""
		Activates the constraints.

		*Arguments:*
			* ``None``

		*Keyword Arguments:*
			* ``None``

		*Returns:*
			* ``None``

		*Author:*
			* Jon Logsdon, jon.logsdon@volition-inc.com, 7/9/2014 2:15:54 PM
		"""

		self.elbow_exp_const.Snap()
		self.knee_exp_const.Snap()
		self.up_arm_exp_const.Snap()
		self.forearm_exp_const.Snap()
		self.leg_up_roll_exp_const.Snap()
		self.leg_roll_exp_const.Snap()
		self.knee_position_const.Snap()
		self.elbow_position_const.Snap()

	def create_constraints( self, side, side2 ):
		"""
		Creates the constraints and runs desired methods to connect constraints.

		*Arguments:*
			* ``side, side2`` Side of the character.

		*Keyword Arguments:*
			* ``None``

		*Returns:*
			* ``None``

		*Author:*
			* Jon Logsdon, jon.logsdon@volition-inc.com, 7/9/2014 2:15:54 PM
		"""

		curr_char_namespace = self.curr_char.LongName.split(":")

		self.elbow_exp_const = FBConstraintRelation(('{0}:{1}Elbow:Procedural'.format(curr_char_namespace[0], side)))
		self.knee_exp_const = FBConstraintRelation(('{0}:{1}Knee:Procedural'.format(curr_char_namespace[0], side)))
		self.up_arm_exp_const = FBConstraintRelation(( '{0}:{1}ArmRoll:Procedural'.format(curr_char_namespace[0], side)))
		self.forearm_exp_const = FBConstraintRelation(( '{0}:{1}ForeArmRoll:Procedural'.format(curr_char_namespace[0], side)))
		self.leg_up_roll_exp_const = FBConstraintRelation(('{0}:{1}UpLegRoll:Procedural'.format(curr_char_namespace[0], side)))
		self.leg_roll_exp_const = FBConstraintRelation(('{0}:{1}LegRoll:Procedural'.format(curr_char_namespace[0], side)))

		self.knee_position_const = FBConstraintManager().TypeCreateConstraint(5)
		self.elbow_position_const = FBConstraintManager().TypeCreateConstraint(5)

		self.mute_proper_attributes(side)

		for knee in self.knees:
			if knee.Name.lower().startswith(side):
				self.knee_position_const.ReferenceAdd(0, knee)

		for knee_target in self.knee_targets:
			if knee_target.Name.lower().startswith("tag_{0}".format(side)):
				if knee_target.Name.endswith("TargetA"):
					self.knee_position_const.ReferenceAdd(1, knee_target)
				if knee_target.Name.endswith("TargetB"):
					self.knee_position_const.ReferenceAdd(1, knee_target)
				if knee_target.Name.endswith("TargetC"):
					self.knee_position_const.ReferenceAdd(1, knee_target)

		self.knee_position_const.Name = '{0}:{1}Knee:PosConst'.format(curr_char_namespace[0], side)

		for elbow in self.elbows:
			if elbow.Name.lower().startswith(side):
				self.elbow_position_const.ReferenceAdd(0, elbow)

		for elbow_target in self.elbow_targets:
			if elbow_target.Name.lower().startswith("tag_{0}".format(side2)):
				self.elbow_position_const.ReferenceAdd(1, elbow_target)


		self.elbow_position_const.Name = '{0}:{1}:ElbowPosConst'.format(curr_char_namespace[0], side)

		self.set_bend_constraints( side, side2 )
		self.set_roll_constraints(side)
		self.activate_constraints()

	def set_bend_constraints(self, side, side2, pRX=True, pRY=True, pRZ=True):
		"""
		Sets up the knee and elbow relation constraints.

		*Arguments:*
			* ``side, side2`` Side of the character.

		*Keyword Arguments:*
			* ``None``

		*Returns:*
			* ``None``

		*Author:*
			* Jon Logsdon, jon.logsdon@volition-inc.com, 7/9/2014 2:15:54 PM
		"""

		curr_char_namespace = self.curr_char.LongName.split(":")

		self.activate_const_anim_nodes(side, side2)

		#================= Knee constraints ======================================
		for knee in self.knees:
			if side in knee.Name.lower():
				#Create function boxes for relation constraint
				vector_to_number = self.knee_exp_const.CreateFunctionBox('Converters', 'Vector to Number')
				is_greater_or_equal_a = self.knee_exp_const.CreateFunctionBox('Number',
																												'Is Greater or Equal (a >= b)')
				divide_a = self.knee_exp_const.CreateFunctionBox('Number', 'Divide (a/b)')
				subtract_a = self.knee_exp_const.CreateFunctionBox('Number', 'Subtract (a - b)')
				is_greater_or_equal_b = self.knee_exp_const.CreateFunctionBox('Number',
																												'Is Greater or Equal (a >= b)')
				scale_and_offset_a = self.knee_exp_const.CreateFunctionBox('Number', 'Scale And Offset (Number)')
				is_greater_or_equal_c = self.knee_exp_const.CreateFunctionBox('Number',
																												'Is Greater or Equal (a >= b)')
				divide_b = self.knee_exp_const.CreateFunctionBox('Number', 'Divide (a/b)')
				scale_and_offset_b = self.knee_exp_const.CreateFunctionBox('Number', 'Scale And Offset (Number)')
				is_greater_or_equal_d = self.knee_exp_const.CreateFunctionBox('Number',
																												'Is Greater or Equal (a >= b)')
				add_a = self.knee_exp_const.CreateFunctionBox('Number', 'Add (a + b)')
				divide_c = self.knee_exp_const.CreateFunctionBox('Number', 'Divide (a/b)')
				subtract_b = self.knee_exp_const.CreateFunctionBox('Number', 'Subtract (a - b)')
				scale_and_offset_c = self.knee_exp_const.CreateFunctionBox('Number', 'Scale And Offset (Number)')
				if_cond_a = self.knee_exp_const.CreateFunctionBox('Number', 'IF Cond Then A Else B')
				add_b = self.knee_exp_const.CreateFunctionBox('Number', 'Add (a + b)')
				is_greater_or_equal_e = self.knee_exp_const.CreateFunctionBox('Number',
																												'Is Greater or Equal (a >= b)')
				divide_d = self.knee_exp_const.CreateFunctionBox('Number', 'Divide (a/b)')
				scale_and_offset_d = self.knee_exp_const.CreateFunctionBox('Number', 'Scale And Offset (Number)')
				if_cond_b = self.knee_exp_const.CreateFunctionBox('Number', 'IF Cond Then A Else B')
				if_cond_c = self.knee_exp_const.CreateFunctionBox('Number', 'IF Cond Then A Else B')
				if_cond_d = self.knee_exp_const.CreateFunctionBox('Number', 'IF Cond Then A Else B')
				if_cond_e = self.knee_exp_const.CreateFunctionBox('Number', 'IF Cond Then A Else B')
				if_cond_f = self.knee_exp_const.CreateFunctionBox('Number', 'IF Cond Then A Else B')

				#Initialize inputs and outputs of each function box
				for leg in self.legs:
					if side in leg.Name.lower():
						if "tag" not in leg.Name and "Up" not in leg.Name:
							if leg.ClassName() == 'FBModelSkeleton':
								source_sender_out_node = self.knee_exp_const.SetAsSource(leg)
								source_sender_out_node.UseGlobalTransforms = False
								source_sender_out = self.find_animation_node(source_sender_out_node.AnimationNodeOutGet(), 'Lcl Rotation')

				vector_to_number_v_in = self.find_animation_node(vector_to_number.AnimationNodeInGet(), 'V')
				vector_to_number_z_out = self.find_animation_node(vector_to_number.AnimationNodeOutGet(), 'Z')

				is_greater_or_equal_a_a_in = self.find_animation_node(is_greater_or_equal_a.AnimationNodeInGet(),
																							  'a')
				is_greater_or_equal_a_b_in = self.find_animation_node(is_greater_or_equal_a.AnimationNodeInGet(),
																							  'b')
				is_greater_or_equal_a_result_out = self.find_animation_node(
					is_greater_or_equal_a.AnimationNodeOutGet(), 'Result')

				divide_a_a_in = self.find_animation_node(divide_a.AnimationNodeInGet(), 'a')
				divide_a_b_in = self.find_animation_node(divide_a.AnimationNodeInGet(), 'b')
				divide_a_result_out = self.find_animation_node(divide_a.AnimationNodeOutGet(), 'Result')

				subtract_a_a_in = self.find_animation_node(subtract_a.AnimationNodeInGet(), 'a')
				subtract_a_b_in = self.find_animation_node(subtract_a.AnimationNodeInGet(), 'b')
				subtract_a_result_out = self.find_animation_node(subtract_a.AnimationNodeOutGet(), 'Result')

				is_greater_or_equal_b_a_in = self.find_animation_node(is_greater_or_equal_b.AnimationNodeInGet(),
																							  'a')
				is_greater_or_equal_b_b_in = self.find_animation_node(is_greater_or_equal_b.AnimationNodeInGet(),
																							  'b')
				is_greater_or_equal_b_result_out = self.find_animation_node(
					is_greater_or_equal_b.AnimationNodeOutGet(), 'Result')

				scale_and_offset_a_offset_in = self.find_animation_node(scale_and_offset_a.AnimationNodeInGet(),
																								 'Offset')
				scale_and_offset_a_scale_factor_in = self.find_animation_node(
					scale_and_offset_a.AnimationNodeInGet(), 'Scale Factor')
				scale_and_offset_a_x_in = self.find_animation_node(scale_and_offset_a.AnimationNodeInGet(), 'X')
				scale_and_offset_a_result_out = self.find_animation_node(scale_and_offset_a.AnimationNodeOutGet(),
																								  'Result')

				is_greater_or_equal_c_a_in = self.find_animation_node(is_greater_or_equal_c.AnimationNodeInGet(),
																							  'a')
				is_greater_or_equal_c_b_in = self.find_animation_node(is_greater_or_equal_c.AnimationNodeInGet(),
																							  'b')
				is_greater_or_equal_c_result_out = self.find_animation_node(
					is_greater_or_equal_c.AnimationNodeOutGet(), 'Result')

				divide_b_a_in = self.find_animation_node(divide_b.AnimationNodeInGet(), 'a')
				divide_b_b_in = self.find_animation_node(divide_b.AnimationNodeInGet(), 'b')
				divide_b_result_out = self.find_animation_node(divide_b.AnimationNodeOutGet(), 'Result')

				scale_and_offset_b_offset_in = self.find_animation_node(scale_and_offset_b.AnimationNodeInGet(),
																								 'Offset')
				scale_and_offset_b_scale_factor_in = self.find_animation_node(
					scale_and_offset_b.AnimationNodeInGet(), 'Scale Factor')
				scale_and_offset_b_x_in = self.find_animation_node(scale_and_offset_b.AnimationNodeInGet(), 'X')
				scale_and_offset_b_result_out = self.find_animation_node(scale_and_offset_b.AnimationNodeOutGet(),
																								  'Result')

				is_greater_or_equal_d_a_in = self.find_animation_node(is_greater_or_equal_d.AnimationNodeInGet(),
																							  'a')
				is_greater_or_equal_d_b_in = self.find_animation_node(is_greater_or_equal_d.AnimationNodeInGet(),
																							  'b')
				is_greater_or_equal_d_result_out = self.find_animation_node(
					is_greater_or_equal_d.AnimationNodeOutGet(), 'Result')

				add_a_a_in = self.find_animation_node(add_a.AnimationNodeInGet(), 'a')
				add_a_b_in = self.find_animation_node(add_a.AnimationNodeInGet(), 'b')
				add_a_result_out = self.find_animation_node(add_a.AnimationNodeOutGet(), 'Result')

				divide_c_a_in = self.find_animation_node(divide_c.AnimationNodeInGet(), 'a')
				divide_c_b_in = self.find_animation_node(divide_c.AnimationNodeInGet(), 'b')
				divide_c_result_out = self.find_animation_node(divide_c.AnimationNodeOutGet(), 'Result')

				subtract_b_a_in = self.find_animation_node(subtract_b.AnimationNodeInGet(), 'a')
				subtract_b_b_in = self.find_animation_node(subtract_b.AnimationNodeInGet(), 'b')
				subtract_b_result_out = self.find_animation_node(subtract_b.AnimationNodeOutGet(), 'Result')

				scale_and_offset_c_offset_in = self.find_animation_node(scale_and_offset_c.AnimationNodeInGet(),
																								 'Offset')
				scale_and_offset_c_scale_factor_in = self.find_animation_node(
					scale_and_offset_c.AnimationNodeInGet(), 'Scale Factor')
				scale_and_offset_c_x_in = self.find_animation_node(scale_and_offset_c.AnimationNodeInGet(), 'X')
				scale_and_offset_c_result_out = self.find_animation_node(scale_and_offset_c.AnimationNodeOutGet(),
																								  'Result')

				if_cond_a_a_in = self.find_animation_node(if_cond_a.AnimationNodeInGet(), 'a')
				if_cond_a_b_in = self.find_animation_node(if_cond_a.AnimationNodeInGet(), 'b')
				if_cond_a_cond_in = self.find_animation_node(if_cond_a.AnimationNodeInGet(), 'Cond')
				if_cond_a_result_out = self.find_animation_node(if_cond_a.AnimationNodeOutGet(), 'Result')

				add_b_a_in = self.find_animation_node(add_b.AnimationNodeInGet(), 'a')
				add_b_b_in = self.find_animation_node(add_b.AnimationNodeInGet(), 'b')
				add_b_result_out = self.find_animation_node(add_b.AnimationNodeOutGet(), 'Result')

				is_greater_or_equal_e_a_in = self.find_animation_node(is_greater_or_equal_e.AnimationNodeInGet(),
																							  'a')
				is_greater_or_equal_e_b_in = self.find_animation_node(is_greater_or_equal_e.AnimationNodeInGet(),
																							  'b')
				is_greater_or_equal_e_result_out = self.find_animation_node(
					is_greater_or_equal_e.AnimationNodeOutGet(), 'Result')

				divide_d_a_in = self.find_animation_node(divide_d.AnimationNodeInGet(), 'a')
				divide_d_b_in = self.find_animation_node(divide_d.AnimationNodeInGet(), 'b')
				divide_d_result_out = self.find_animation_node(divide_d.AnimationNodeOutGet(), 'Result')

				scale_and_offset_d_offset_in = self.find_animation_node(scale_and_offset_d.AnimationNodeInGet(),
																								 'Offset')
				scale_and_offset_d_scale_factor_in = self.find_animation_node(
					scale_and_offset_d.AnimationNodeInGet(), 'Scale Factor')
				scale_and_offset_d_x_in = self.find_animation_node(scale_and_offset_d.AnimationNodeInGet(), 'X')
				scale_and_offset_d_result_out = self.find_animation_node(scale_and_offset_d.AnimationNodeOutGet(),
																								  'Result')

				if_cond_b_a_in = self.find_animation_node(if_cond_b.AnimationNodeInGet(), 'a')
				if_cond_b_b_in = self.find_animation_node(if_cond_b.AnimationNodeInGet(), 'b')
				if_cond_b_cond_in = self.find_animation_node(if_cond_b.AnimationNodeInGet(), 'Cond')
				if_cond_b_result_out = self.find_animation_node(if_cond_b.AnimationNodeOutGet(), 'Result')

				if_cond_c_a_in = self.find_animation_node(if_cond_c.AnimationNodeInGet(), 'a')
				if_cond_c_b_in = self.find_animation_node(if_cond_c.AnimationNodeInGet(), 'b')
				if_cond_c_result_out = self.find_animation_node(if_cond_c.AnimationNodeOutGet(), 'Result')

				if_cond_d_a_in = self.find_animation_node(if_cond_d.AnimationNodeInGet(), 'a')
				if_cond_d_b_in = self.find_animation_node(if_cond_d.AnimationNodeInGet(), 'b')
				if_cond_d_cond_in = self.find_animation_node(if_cond_d.AnimationNodeInGet(), 'Cond')
				if_cond_d_result_out = self.find_animation_node(if_cond_d.AnimationNodeOutGet(), 'Result')

				if_cond_e_a_in = self.find_animation_node(if_cond_e.AnimationNodeInGet(), 'a')
				if_cond_e_b_in = self.find_animation_node(if_cond_e.AnimationNodeInGet(), 'b')
				if_cond_e_cond_in = self.find_animation_node(if_cond_e.AnimationNodeInGet(), 'Cond')
				if_cond_e_result_out = self.find_animation_node(if_cond_e.AnimationNodeOutGet(), 'Result')

				if_cond_f_a_in = self.find_animation_node(if_cond_f.AnimationNodeInGet(), 'a')
				if_cond_f_b_in = self.find_animation_node(if_cond_f.AnimationNodeInGet(), 'b')
				if_cond_f_cond_in = self.find_animation_node(if_cond_f.AnimationNodeInGet(), 'Cond')
				if_cond_f_result_out = self.find_animation_node(if_cond_f.AnimationNodeOutGet(), 'Result')

				self.knee_exp_const.ConstrainObject(self.knee_position_const)

				pos_const_weight_a = self.knee_position_const.ReferenceGet(1, 0)
				pos_const_weight_b = self.knee_position_const.ReferenceGet(1, 1)
				pos_const_weight_c = self.knee_position_const.ReferenceGet(1, 2)

				pos_a_in = self.find_animation_node(self.knee_position_const.AnimationNodeInGet(),
																'{0}.Weight'.format(pos_const_weight_a.LongName))
				pos_b_in = self.find_animation_node(self.knee_position_const.AnimationNodeInGet(),
																'{0}.Weight'.format(pos_const_weight_b.LongName))
				pos_c_in = self.find_animation_node(self.knee_position_const.AnimationNodeInGet(),
																'{0}.Weight'.format(pos_const_weight_c.LongName))

				FBSystem().Scene.Evaluate()

				#Set values for specific function box inputs (specific to this relation constraint)
				is_greater_or_equal_a_a_in.WriteData([-45.0])
				divide_a_b_in.WriteData([-45.0])
				if_cond_b_b_in.WriteData([100.0])
				scale_and_offset_a_offset_in.WriteData([100.0])
				scale_and_offset_a_scale_factor_in.WriteData([-100.0])
				if_cond_a_a_in.WriteData([0.0])
				is_greater_or_equal_b_a_in.WriteData([-90.0])
				is_greater_or_equal_c_a_in.WriteData([-45.0])
				divide_b_b_in.WriteData([-45.0])
				scale_and_offset_b_offset_in.WriteData([-100.0])
				scale_and_offset_b_scale_factor_in.WriteData([100.0])
				add_a_a_in.WriteData([90.0])
				divide_c_b_in.WriteData([-90.0])
				subtract_b_b_in.WriteData([1.0])
				scale_and_offset_c_offset_in.WriteData([-100.0])
				scale_and_offset_c_scale_factor_in.WriteData([-100.0])
				if_cond_c_a_in.WriteData([100.0])
				if_cond_d_b_in.WriteData([0.0])
				add_b_a_in.WriteData([90.0])
				divide_d_b_in.WriteData([-90.0])
				scale_and_offset_d_offset_in.WriteData([0.0])
				scale_and_offset_d_scale_factor_in.WriteData([100.0])
				if_cond_f_b_in.WriteData([0.0])
				is_greater_or_equal_e_a_in.WriteData([-90.0])
				is_greater_or_equal_d_a_in.WriteData([-100.0])
				subtract_a_b_in.WriteData([1.0])

				FBSystem().Scene.Evaluate()

				#Check if the leg is present and make connections of the inputs and outputs
				if source_sender_out_node:
					FBConnect(source_sender_out, vector_to_number_v_in)
					FBConnect(vector_to_number_z_out, is_greater_or_equal_a_b_in)
					FBConnect(is_greater_or_equal_a_result_out, if_cond_b_cond_in)
					FBConnect(if_cond_b_result_out, pos_a_in)
					FBConnect(vector_to_number_z_out, divide_a_a_in)
					FBConnect(divide_a_result_out, subtract_a_a_in)
					FBConnect(subtract_a_result_out, scale_and_offset_a_x_in)
					FBConnect(scale_and_offset_a_result_out, if_cond_a_b_in)
					FBConnect(if_cond_a_result_out, if_cond_b_a_in)
					FBConnect(vector_to_number_z_out, is_greater_or_equal_b_b_in)
					FBConnect(is_greater_or_equal_b_result_out, if_cond_a_cond_in)
					FBConnect(vector_to_number_z_out, is_greater_or_equal_c_b_in)
					FBConnect(is_greater_or_equal_c_result_out, if_cond_e_cond_in)
					FBConnect(if_cond_e_result_out, pos_b_in)
					FBConnect(vector_to_number_z_out, divide_b_a_in)
					FBConnect(divide_b_result_out, scale_and_offset_b_x_in)
					FBConnect(scale_and_offset_b_result_out, if_cond_e_a_in)
					FBConnect(vector_to_number_z_out, add_a_b_in)
					FBConnect(add_a_result_out, divide_c_a_in)
					FBConnect(divide_c_result_out, subtract_b_a_in)
					FBConnect(subtract_b_result_out, scale_and_offset_c_x_in)
					FBConnect(scale_and_offset_c_result_out, if_cond_c_b_in)
					FBConnect(if_cond_c_result_out, if_cond_d_a_in)
					FBConnect(if_cond_d_result_out, if_cond_e_b_in)
					FBConnect(vector_to_number_z_out, add_b_b_in)
					FBConnect(add_b_result_out, divide_d_a_in)
					FBConnect(divide_d_result_out, scale_and_offset_d_x_in)
					FBConnect(scale_and_offset_d_result_out, if_cond_f_a_in)
					FBConnect(if_cond_f_result_out, pos_c_in)
					FBConnect(vector_to_number_z_out, is_greater_or_equal_e_b_in)
					FBConnect(is_greater_or_equal_e_result_out, if_cond_f_cond_in)
					FBConnect(vector_to_number_z_out, is_greater_or_equal_d_b_in)
					FBConnect(is_greater_or_equal_d_result_out, if_cond_d_cond_in)

				FBSystem().Scene.Evaluate()

		#================= Elbow constraints =======================================
		for elbow in self.elbows:
			if side in elbow.Name.lower():
				#Create function boxes for relation constraint
				vector_to_number = self.elbow_exp_const.CreateFunctionBox('Converters', 'Vector to Number')
				is_greater_or_equal_a = self.elbow_exp_const.CreateFunctionBox('Number',
																												 'Is Greater or Equal (a >= b)')
				divide_a = self.elbow_exp_const.CreateFunctionBox('Number', 'Divide (a/b)')
				subtract_a = self.elbow_exp_const.CreateFunctionBox('Number', 'Subtract (a - b)')
				is_greater_or_equal_b = self.elbow_exp_const.CreateFunctionBox('Number',
																												 'Is Greater or Equal (a >= b)')
				scale_and_offset_a = self.elbow_exp_const.CreateFunctionBox('Number', 'Scale And Offset (Number)')
				is_greater_or_equal_c = self.elbow_exp_const.CreateFunctionBox('Number',
																												 'Is Greater or Equal (a >= b)')
				divide_b = self.elbow_exp_const.CreateFunctionBox('Number', 'Divide (a/b)')
				scale_and_offset_b = self.elbow_exp_const.CreateFunctionBox('Number', 'Scale And Offset (Number)')
				is_greater_or_equal_d = self.elbow_exp_const.CreateFunctionBox('Number',
																												 'Is Greater or Equal (a >= b)')
				add_a = self.elbow_exp_const.CreateFunctionBox('Number', 'Add (a + b)')
				divide_c = self.elbow_exp_const.CreateFunctionBox('Number', 'Divide (a/b)')
				subtract_b = self.elbow_exp_const.CreateFunctionBox('Number', 'Subtract (a - b)')
				scale_and_offset_c = self.elbow_exp_const.CreateFunctionBox('Number', 'Scale And Offset (Number)')
				if_cond_a = self.elbow_exp_const.CreateFunctionBox('Number', 'IF Cond Then A Else B')
				add_b = self.elbow_exp_const.CreateFunctionBox('Number', 'Add (a + b)')
				is_greater_or_equal_e = self.elbow_exp_const.CreateFunctionBox('Number',
																												 'Is Greater or Equal (a >= b)')
				divide_d = self.elbow_exp_const.CreateFunctionBox('Number', 'Divide (a/b)')
				scale_and_offset_d = self.elbow_exp_const.CreateFunctionBox('Number', 'Scale And Offset (Number)')
				if_cond_b = self.elbow_exp_const.CreateFunctionBox('Number', 'IF Cond Then A Else B')
				if_cond_c = self.elbow_exp_const.CreateFunctionBox('Number', 'IF Cond Then A Else B')
				if_cond_d = self.elbow_exp_const.CreateFunctionBox('Number', 'IF Cond Then A Else B')
				if_cond_e = self.elbow_exp_const.CreateFunctionBox('Number', 'IF Cond Then A Else B')
				if_cond_f = self.elbow_exp_const.CreateFunctionBox('Number', 'IF Cond Then A Else B')

				#Initialize inputs and outputs of each function box
				for forearm in self.forearms:
					if side in forearm.Name.lower():
						if "tag" not in forearm.Name and "Up" not in forearm.Name:
							if forearm.ClassName() == 'FBModelSkeleton':
								source_sender_out_node = self.elbow_exp_const.SetAsSource(forearm)
								source_sender_out_node.UseGlobalTransforms = False
								source_sender_out = self.find_animation_node(source_sender_out_node.AnimationNodeOutGet(), 'Lcl Rotation')

				vector_to_number_v_in = self.find_animation_node(vector_to_number.AnimationNodeInGet(), 'V')
				vector_to_number_z_out = self.find_animation_node(vector_to_number.AnimationNodeOutGet(), 'Z')

				is_greater_or_equal_a_a_in = self.find_animation_node(is_greater_or_equal_a.AnimationNodeInGet(),
																							  'a')
				is_greater_or_equal_a_b_in = self.find_animation_node(is_greater_or_equal_a.AnimationNodeInGet(),
																							  'b')
				is_greater_or_equal_a_result_out = self.find_animation_node(
					is_greater_or_equal_a.AnimationNodeOutGet(), 'Result')

				divide_a_a_in = self.find_animation_node(divide_a.AnimationNodeInGet(), 'a')
				divide_a_b_in = self.find_animation_node(divide_a.AnimationNodeInGet(), 'b')
				divide_a_result_out = self.find_animation_node(divide_a.AnimationNodeOutGet(), 'Result')

				subtract_a_a_in = self.find_animation_node(subtract_a.AnimationNodeInGet(), 'a')
				subtract_a_b_in = self.find_animation_node(subtract_a.AnimationNodeInGet(), 'b')
				subtract_a_result_out = self.find_animation_node(subtract_a.AnimationNodeOutGet(), 'Result')

				is_greater_or_equal_b_a_in = self.find_animation_node(is_greater_or_equal_b.AnimationNodeInGet(),
																							  'a')
				is_greater_or_equal_b_b_in = self.find_animation_node(is_greater_or_equal_b.AnimationNodeInGet(),
																							  'b')
				is_greater_or_equal_b_result_out = self.find_animation_node(
					is_greater_or_equal_b.AnimationNodeOutGet(), 'Result')

				scale_and_offset_a_offset_in = self.find_animation_node(scale_and_offset_a.AnimationNodeInGet(),
																								 'Offset')
				scale_and_offset_a_scale_factor_in = self.find_animation_node(
					scale_and_offset_a.AnimationNodeInGet(), 'Scale Factor')
				scale_and_offset_a_x_in = self.find_animation_node(scale_and_offset_a.AnimationNodeInGet(), 'X')
				scale_and_offset_a_result_out = self.find_animation_node(scale_and_offset_a.AnimationNodeOutGet(),
																								  'Result')

				is_greater_or_equal_c_a_in = self.find_animation_node(is_greater_or_equal_c.AnimationNodeInGet(),
																							  'a')
				is_greater_or_equal_c_b_in = self.find_animation_node(is_greater_or_equal_c.AnimationNodeInGet(),
																							  'b')
				is_greater_or_equal_c_result_out = self.find_animation_node(
					is_greater_or_equal_c.AnimationNodeOutGet(), 'Result')

				divide_b_a_in = self.find_animation_node(divide_b.AnimationNodeInGet(), 'a')
				divide_b_b_in = self.find_animation_node(divide_b.AnimationNodeInGet(), 'b')
				divide_b_result_out = self.find_animation_node(divide_b.AnimationNodeOutGet(), 'Result')

				scale_and_offset_b_offset_in = self.find_animation_node(scale_and_offset_b.AnimationNodeInGet(),
																								 'Offset')
				scale_and_offset_b_scale_factor_in = self.find_animation_node(
					scale_and_offset_b.AnimationNodeInGet(), 'Scale Factor')
				scale_and_offset_b_x_in = self.find_animation_node(scale_and_offset_b.AnimationNodeInGet(), 'X')
				scale_and_offset_b_result_out = self.find_animation_node(scale_and_offset_b.AnimationNodeOutGet(),
																								  'Result')

				is_greater_or_equal_d_a_in = self.find_animation_node(is_greater_or_equal_d.AnimationNodeInGet(),
																							  'a')
				is_greater_or_equal_d_b_in = self.find_animation_node(is_greater_or_equal_d.AnimationNodeInGet(),
																							  'b')
				is_greater_or_equal_d_result_out = self.find_animation_node(
					is_greater_or_equal_d.AnimationNodeOutGet(), 'Result')

				add_a_a_in = self.find_animation_node(add_a.AnimationNodeInGet(), 'a')
				add_a_b_in = self.find_animation_node(add_a.AnimationNodeInGet(), 'b')
				add_a_result_out = self.find_animation_node(add_a.AnimationNodeOutGet(), 'Result')

				divide_c_a_in = self.find_animation_node(divide_c.AnimationNodeInGet(), 'a')
				divide_c_b_in = self.find_animation_node(divide_c.AnimationNodeInGet(), 'b')
				divide_c_result_out = self.find_animation_node(divide_c.AnimationNodeOutGet(), 'Result')

				subtract_b_a_in = self.find_animation_node(subtract_b.AnimationNodeInGet(), 'a')
				subtract_b_b_in = self.find_animation_node(subtract_b.AnimationNodeInGet(), 'b')
				subtract_b_result_out = self.find_animation_node(subtract_b.AnimationNodeOutGet(), 'Result')

				scale_and_offset_c_offset_in = self.find_animation_node(scale_and_offset_c.AnimationNodeInGet(),
																								 'Offset')
				scale_and_offset_c_scale_factor_in = self.find_animation_node(
					scale_and_offset_c.AnimationNodeInGet(), 'Scale Factor')
				scale_and_offset_c_x_in = self.find_animation_node(scale_and_offset_c.AnimationNodeInGet(), 'X')
				scale_and_offset_c_result_out = self.find_animation_node(scale_and_offset_c.AnimationNodeOutGet(),
																								  'Result')

				if_cond_a_a_in = self.find_animation_node(if_cond_a.AnimationNodeInGet(), 'a')
				if_cond_a_b_in = self.find_animation_node(if_cond_a.AnimationNodeInGet(), 'b')
				if_cond_a_cond_in = self.find_animation_node(if_cond_a.AnimationNodeInGet(), 'Cond')
				if_cond_a_result_out = self.find_animation_node(if_cond_a.AnimationNodeOutGet(), 'Result')

				add_b_a_in = self.find_animation_node(add_b.AnimationNodeInGet(), 'a')
				add_b_b_in = self.find_animation_node(add_b.AnimationNodeInGet(), 'b')
				add_b_result_out = self.find_animation_node(add_b.AnimationNodeOutGet(), 'Result')

				is_greater_or_equal_e_a_in = self.find_animation_node(is_greater_or_equal_e.AnimationNodeInGet(),
																							  'a')
				is_greater_or_equal_e_b_in = self.find_animation_node(is_greater_or_equal_e.AnimationNodeInGet(),
																							  'b')
				is_greater_or_equal_e_result_out = self.find_animation_node(
					is_greater_or_equal_e.AnimationNodeOutGet(), 'Result')

				divide_d_a_in = self.find_animation_node(divide_d.AnimationNodeInGet(), 'a')
				divide_d_b_in = self.find_animation_node(divide_d.AnimationNodeInGet(), 'b')
				divide_d_result_out = self.find_animation_node(divide_d.AnimationNodeOutGet(), 'Result')

				scale_and_offset_d_offset_in = self.find_animation_node(scale_and_offset_d.AnimationNodeInGet(),
																								 'Offset')
				scale_and_offset_d_scale_factor_in = self.find_animation_node(
					scale_and_offset_d.AnimationNodeInGet(), 'Scale Factor')
				scale_and_offset_d_x_in = self.find_animation_node(scale_and_offset_d.AnimationNodeInGet(), 'X')
				scale_and_offset_d_result_out = self.find_animation_node(scale_and_offset_d.AnimationNodeOutGet(),
																								  'Result')

				if_cond_b_a_in = self.find_animation_node(if_cond_b.AnimationNodeInGet(), 'a')
				if_cond_b_b_in = self.find_animation_node(if_cond_b.AnimationNodeInGet(), 'b')
				if_cond_b_cond_in = self.find_animation_node(if_cond_b.AnimationNodeInGet(), 'Cond')
				if_cond_b_result_out = self.find_animation_node(if_cond_b.AnimationNodeOutGet(), 'Result')

				if_cond_c_a_in = self.find_animation_node(if_cond_c.AnimationNodeInGet(), 'a')
				if_cond_c_b_in = self.find_animation_node(if_cond_c.AnimationNodeInGet(), 'b')
				if_cond_c_result_out = self.find_animation_node(if_cond_c.AnimationNodeOutGet(), 'Result')

				if_cond_d_a_in = self.find_animation_node(if_cond_d.AnimationNodeInGet(), 'a')
				if_cond_d_b_in = self.find_animation_node(if_cond_d.AnimationNodeInGet(), 'b')
				if_cond_d_cond_in = self.find_animation_node(if_cond_d.AnimationNodeInGet(), 'Cond')
				if_cond_d_result_out = self.find_animation_node(if_cond_d.AnimationNodeOutGet(), 'Result')

				if_cond_e_a_in = self.find_animation_node(if_cond_e.AnimationNodeInGet(), 'a')
				if_cond_e_b_in = self.find_animation_node(if_cond_e.AnimationNodeInGet(), 'b')
				if_cond_e_cond_in = self.find_animation_node(if_cond_e.AnimationNodeInGet(), 'Cond')
				if_cond_e_result_out = self.find_animation_node(if_cond_e.AnimationNodeOutGet(), 'Result')

				if_cond_f_a_in = self.find_animation_node(if_cond_f.AnimationNodeInGet(), 'a')
				if_cond_f_b_in = self.find_animation_node(if_cond_f.AnimationNodeInGet(), 'b')
				if_cond_f_cond_in = self.find_animation_node(if_cond_f.AnimationNodeInGet(), 'Cond')
				if_cond_f_result_out = self.find_animation_node(if_cond_f.AnimationNodeOutGet(), 'Result')

				self.elbow_exp_const.ConstrainObject(self.elbow_position_const)

				pos_const_weight_a = self.elbow_position_const.ReferenceGet(1, 0)
				pos_const_weight_b = self.elbow_position_const.ReferenceGet(1, 1)
				pos_const_weight_c = self.elbow_position_const.ReferenceGet(1, 2)

				pos_a_in = self.find_animation_node(self.elbow_position_const.AnimationNodeInGet(),
																'{0}.Weight'.format(pos_const_weight_a.LongName))
				pos_b_in = self.find_animation_node(self.elbow_position_const.AnimationNodeInGet(),
																'{0}.Weight'.format(pos_const_weight_b.LongName))
				pos_c_in = self.find_animation_node(self.elbow_position_const.AnimationNodeInGet(),
																'{0}.Weight'.format(pos_const_weight_c.LongName))

				FBSystem().Scene.Evaluate()

				#Set values for specific function box inputs (specific to this relation constraint)
				is_greater_or_equal_a_a_in.WriteData([-45.0])
				divide_a_b_in.WriteData([-45.0])
				if_cond_b_b_in.WriteData([100.0])
				scale_and_offset_a_offset_in.WriteData([100.0])
				scale_and_offset_a_scale_factor_in.WriteData([-100.0])
				if_cond_a_a_in.WriteData([0.0])
				is_greater_or_equal_b_a_in.WriteData([-90.0])
				is_greater_or_equal_c_a_in.WriteData([-45.0])
				divide_b_b_in.WriteData([-45.0])
				scale_and_offset_b_offset_in.WriteData([-100.0])
				scale_and_offset_b_scale_factor_in.WriteData([100.0])
				add_a_a_in.WriteData([90.0])
				divide_c_b_in.WriteData([-90.0])
				subtract_b_b_in.WriteData([1.0])
				scale_and_offset_c_offset_in.WriteData([-100.0])
				scale_and_offset_c_scale_factor_in.WriteData([-100.0])
				if_cond_c_a_in.WriteData([100.0])
				if_cond_d_b_in.WriteData([0.0])
				add_b_a_in.WriteData([90.0])
				divide_d_b_in.WriteData([-90.0])
				scale_and_offset_d_offset_in.WriteData([0.0])
				scale_and_offset_d_scale_factor_in.WriteData([100.0])
				if_cond_f_b_in.WriteData([0.0])
				is_greater_or_equal_e_a_in.WriteData([-90.0])
				is_greater_or_equal_d_a_in.WriteData([-100.0])
				subtract_a_b_in.WriteData([1.0])

				FBSystem().Scene.Evaluate()

				#Check if the leg is present and make connections of the inputs and outputs
				if source_sender_out_node:
					FBConnect(source_sender_out, vector_to_number_v_in)
					FBConnect(vector_to_number_z_out, is_greater_or_equal_a_b_in)
					FBConnect(is_greater_or_equal_a_result_out, if_cond_b_cond_in)
					FBConnect(if_cond_b_result_out, pos_a_in)
					FBConnect(vector_to_number_z_out, divide_a_a_in)
					FBConnect(divide_a_result_out, subtract_a_a_in)
					FBConnect(subtract_a_result_out, scale_and_offset_a_x_in)
					FBConnect(scale_and_offset_a_result_out, if_cond_a_b_in)
					FBConnect(if_cond_a_result_out, if_cond_b_a_in)
					FBConnect(vector_to_number_z_out, is_greater_or_equal_b_b_in)
					FBConnect(is_greater_or_equal_b_result_out, if_cond_a_cond_in)
					FBConnect(vector_to_number_z_out, is_greater_or_equal_c_b_in)
					FBConnect(is_greater_or_equal_c_result_out, if_cond_e_cond_in)
					FBConnect(if_cond_e_result_out, pos_b_in)
					FBConnect(vector_to_number_z_out, divide_b_a_in)
					FBConnect(divide_b_result_out, scale_and_offset_b_x_in)
					FBConnect(scale_and_offset_b_result_out, if_cond_e_a_in)
					FBConnect(vector_to_number_z_out, add_a_b_in)
					FBConnect(add_a_result_out, divide_c_a_in)
					FBConnect(divide_c_result_out, subtract_b_a_in)
					FBConnect(subtract_b_result_out, scale_and_offset_c_x_in)
					FBConnect(scale_and_offset_c_result_out, if_cond_c_b_in)
					FBConnect(if_cond_c_result_out, if_cond_d_a_in)
					FBConnect(if_cond_d_result_out, if_cond_e_b_in)
					FBConnect(vector_to_number_z_out, add_b_b_in)
					FBConnect(add_b_result_out, divide_d_a_in)
					FBConnect(divide_d_result_out, scale_and_offset_d_x_in)
					FBConnect(scale_and_offset_d_result_out, if_cond_f_a_in)
					FBConnect(if_cond_f_result_out, pos_c_in)
					FBConnect(vector_to_number_z_out, is_greater_or_equal_e_b_in)
					FBConnect(is_greater_or_equal_e_result_out, if_cond_f_cond_in)
					FBConnect(vector_to_number_z_out, is_greater_or_equal_d_b_in)
					FBConnect(is_greater_or_equal_d_result_out, if_cond_d_cond_in)

				FBSystem().Scene.Evaluate()


	def set_roll_constraints( self, side, pRX=True, pRY=True, pRZ=True ):
		"""
		Sets up the function boxes and connections to the forearm roll relation constraints.
		
		*Arguments:*
			* ``side`` Side of the character.
		
		*Keyword Arguments:*
			* ``None``
		
		*Returns:*
			* ``None`` 
		
		*Author:*
			* Jon Logsdon, jon.logsdon@volition-inc.com, 7/9/2014 2:15:54 PM
		"""

		#Current namespace
		curr_char_namespace = self.curr_char.LongName.split(":")


		#======================================== Up Arm Roll/Twist ======================================================
		#Relation constraints
		if self.arm_rolls:
			for arm_roll in self.arm_rolls:
				if side in arm_roll.Name.lower():
					if arm_roll.ClassName() == 'FBModelSkeleton':
						if "Fore" not in arm_roll.Name:
							vector_to_number_box1 = self.up_arm_exp_const.CreateFunctionBox('Converters', 'Vector to Number')
							multiply_box1 = self.up_arm_exp_const.CreateFunctionBox('Number', 'Multiply (a x b)')
							scale_and_offset_box1 = self.up_arm_exp_const.CreateFunctionBox('Number', 'Scale And Offset (Number)')
							number_to_vector_box1 = self.up_arm_exp_const.CreateFunctionBox('Converters', 'Number to Vector')
							number_to_vector_box2 = self.up_arm_exp_const.CreateFunctionBox('Converters', 'Number to Vector')

							for arm in self.arms:
								if side in arm.Name.lower():
									if "Fore" not in arm.Name:
										if arm.ClassName() == 'FBModelSkeleton':
											source_sender_out_node = self.up_arm_exp_const.SetAsSource(arm)
											source_sender_out_node.UseGlobalTransforms = False
											source_sender_out = self.find_animation_node(source_sender_out_node.AnimationNodeOutGet(), 'Lcl Rotation')

							for arm_roll in self.arm_rolls:
								if side in arm_roll.Name.lower():
									if "Fore" not in arm_roll.Name:
										if arm_roll.ClassName() == 'FBModelSkeleton':
											cobject_result_in_node = self.up_arm_exp_const.ConstrainObject(arm_roll)
											cobject_result_in_node.UseGlobalTransforms = False
											cobject_result_in1 = self.find_animation_node(cobject_result_in_node.AnimationNodeInGet(), 'Lcl Rotation')

							for arm_twist in self.arm_twists:
								if side in arm_twist.Name.lower():
									if "Fore" not in arm_twist.Name:
										if arm_twist.ClassName() == 'FBModelSkeleton':
											cobject_result_in_node = self.up_arm_exp_const.ConstrainObject(arm_twist)
											cobject_result_in_node.UseGlobalTransforms = False
											cobject_result_in2 = self.find_animation_node(cobject_result_in_node.AnimationNodeInGet(), 'Lcl Rotation')

							vector_to_number_box1_v_in = self.find_animation_node(vector_to_number_box1.AnimationNodeInGet(), 'V')
							vector_to_number_box1_x_out = self.find_animation_node(vector_to_number_box1.AnimationNodeOutGet(), 'X')

							multiply_box1_a_in = self.find_animation_node(multiply_box1.AnimationNodeInGet(), 'a')
							multiply_box1_b_in = self.find_animation_node(multiply_box1.AnimationNodeInGet(), 'b')
							multiply_box1_result_out = self.find_animation_node(multiply_box1.AnimationNodeOutGet(), 'Result')

							scale_and_offset_box1_offset_in = self.find_animation_node(scale_and_offset_box1.AnimationNodeInGet(), 'Offset')
							scale_and_offset_box1_scale_factor_in = self.find_animation_node(scale_and_offset_box1.AnimationNodeInGet(), 'Scale Factor')
							scale_and_offset_box1_x_in = self.find_animation_node(scale_and_offset_box1.AnimationNodeInGet(), 'X')
							scale_and_offset_box1_result_out = self.find_animation_node(scale_and_offset_box1.AnimationNodeOutGet(), 'Result')

							number_to_vector_box1_x_in = self.find_animation_node(number_to_vector_box1.AnimationNodeInGet(), 'X')
							number_to_vector_box1_result_out = self.find_animation_node(number_to_vector_box1.AnimationNodeOutGet(), 'Result')

							number_to_vector_box2_x_in = self.find_animation_node(number_to_vector_box2.AnimationNodeInGet(), 'X')
							number_to_vector_box2_result_out = self.find_animation_node( number_to_vector_box2.AnimationNodeOutGet(), 'Result')

							multiply_box1_b_in.WriteData([-0.5])
							scale_and_offset_box1_offset_in.WriteData([360.0])
							scale_and_offset_box1_scale_factor_in.WriteData([-0.3])

							if source_sender_out and cobject_result_in1 and cobject_result_in2:
								FBConnect(source_sender_out, vector_to_number_box1_v_in)
								FBConnect(vector_to_number_box1_x_out, multiply_box1_a_in)
								FBConnect(multiply_box1_result_out, number_to_vector_box2_x_in)
								FBConnect(vector_to_number_box1_x_out, scale_and_offset_box1_x_in)
								FBConnect(scale_and_offset_box1_result_out, number_to_vector_box1_x_in)
								FBConnect(number_to_vector_box1_result_out, cobject_result_in1)
								FBConnect(number_to_vector_box2_result_out, cobject_result_in2)

							FBSystem().Scene.Evaluate()

		#================================== Forearm Rolls ================================================================
		if self.forearm_rolls:
			for forearm_roll in self.forearm_rolls:
				if side in forearm_roll.Name.lower():
					if forearm_roll.ClassName() == 'FBModelSkeleton':
						if "Fore" in forearm_roll.Name:
							vector_to_number_box1 = self.forearm_exp_const.CreateFunctionBox('Converters', 'Vector to Number')
							is_less_box1 = self.forearm_exp_const.CreateFunctionBox('Number', 'Is Less (a < b)')
							scale_and_offset_box1 = self.forearm_exp_const.CreateFunctionBox('Number', 'Scale And Offset (Number)')
							if_cond_box2 = self.forearm_exp_const.CreateFunctionBox('Number', 'IF Cond Then A Else B')
							number_to_vector_box1 = self.forearm_exp_const.CreateFunctionBox('Converters', 'Number to Vector')

							for hand in self.hands:
								if side in hand.Name.lower():
									if hand.ClassName() == 'FBModelSkeleton':
										source_sender_out_node = self.forearm_exp_const.SetAsSource(hand)
										source_sender_out_node.UseGlobalTransforms = False
										source_sender_out = self.find_animation_node(source_sender_out_node.AnimationNodeOutGet(), 'Lcl Rotation')

							for forearm_roll in self.forearm_rolls:
								if side in forearm_roll.Name.lower():
									if forearm_roll.ClassName() == 'FBModelSkeleton':
										cobject_result_in_node = self.forearm_exp_const.ConstrainObject(forearm_roll)
										cobject_result_in_node.UseGlobalTransforms = False
										cobject_result_in = self.find_animation_node(cobject_result_in_node.AnimationNodeInGet(), 'Lcl Rotation')

							vector_to_number_box1_v_in = self.find_animation_node(vector_to_number_box1.AnimationNodeInGet(), 'V')
							vector_to_number_box1_x_out = self.find_animation_node(vector_to_number_box1.AnimationNodeOutGet(), 'X')

							is_less_box1_a_in = self.find_animation_node(is_less_box1.AnimationNodeInGet(), 'a')
							is_less_box1_b_in = self.find_animation_node(is_less_box1.AnimationNodeInGet(), 'b')
							is_less_box1_result_out = self.find_animation_node(is_less_box1.AnimationNodeOutGet(), 'Result')

							scale_and_offset_box1_offset_in = self.find_animation_node(scale_and_offset_box1.AnimationNodeInGet(), 'Offset')
							scale_and_offset_box1_scale_factor_in = self.find_animation_node(scale_and_offset_box1.AnimationNodeInGet(), 'Scale Factor')
							scale_and_offset_box1_x_in = self.find_animation_node(scale_and_offset_box1.AnimationNodeInGet(), 'X')
							scale_and_offset_box1_result_out = self.find_animation_node(scale_and_offset_box1.AnimationNodeOutGet(), 'Result')

							if_cond_box2_a_in = self.find_animation_node(if_cond_box2.AnimationNodeInGet(), 'a')
							if_cond_box2_b_in = self.find_animation_node(if_cond_box2.AnimationNodeInGet(), 'b')
							if_cond_box2_cond_in = self.find_animation_node(if_cond_box2.AnimationNodeInGet(), 'Cond')
							if_cond_box2_result_out = self.find_animation_node(if_cond_box2.AnimationNodeOutGet(), 'Result')

							number_to_vector_box1_x_in = self.find_animation_node(number_to_vector_box1.AnimationNodeInGet(), 'X')
							number_to_vector_box1_result_out = self.find_animation_node(number_to_vector_box1.AnimationNodeOutGet(), 'Result')

							is_less_box1_a_in.WriteData([0.0])
							scale_and_offset_box1_offset_in.WriteData([360.0])
							scale_and_offset_box1_scale_factor_in.WriteData([1.0])

							if source_sender_out and cobject_result_in:
								FBConnect(source_sender_out, vector_to_number_box1_v_in)
								FBConnect(vector_to_number_box1_x_out, is_less_box1_b_in)
								FBConnect(vector_to_number_box1_x_out, scale_and_offset_box1_x_in)
								FBConnect(vector_to_number_box1_x_out, if_cond_box2_b_in)
								FBConnect(is_less_box1_result_out, if_cond_box2_cond_in)
								FBConnect(scale_and_offset_box1_result_out, if_cond_box2_a_in)
								FBConnect(if_cond_box2_result_out, number_to_vector_box1_x_in)
								FBConnect(number_to_vector_box1_result_out, cobject_result_in)

							FBSystem().Scene.Evaluate()

		#============================================ Up Leg Rolls =======================================================
		if self.up_leg_rolls:
			for up_leg_roll in self.up_leg_rolls:
				if side in up_leg_roll.Name.lower():
					if up_leg_roll.ClassName() == 'FBModelSkeleton':
						vector_to_number_box1 = self.leg_up_roll_exp_const.CreateFunctionBox('Converters', 'Vector to Number')
						vector_to_number_box2 = self.leg_up_roll_exp_const.CreateFunctionBox('Converters', 'Vector to Number')
						is_greater_box1 = self.leg_up_roll_exp_const.CreateFunctionBox('Number', 'Is Greater (a > b)')
						is_less_box1 = self.leg_up_roll_exp_const.CreateFunctionBox('Number', 'Is Less (a < b)')
						add_box1 = self.leg_up_roll_exp_const.CreateFunctionBox('Number', 'Add (a + b)')
						divide_box1 = self.leg_up_roll_exp_const.CreateFunctionBox('Number', 'Divide (a/b)')
						if_cond_box1 = self.leg_up_roll_exp_const.CreateFunctionBox('Number', 'IF Cond Then A Else B')
						if_cond_box2 = self.leg_up_roll_exp_const.CreateFunctionBox('Number', 'IF Cond Then A Else B')
						number_to_vector_box1 = self.leg_up_roll_exp_const.CreateFunctionBox('Converters', 'Number to Vector')

						vector_to_number_box1_v_in = self.find_animation_node(vector_to_number_box1.AnimationNodeInGet(), 'V')
						vector_to_number_box1_x_out = self.find_animation_node(vector_to_number_box1.AnimationNodeOutGet(), 'X')

						vector_to_number_box2_v_in = self.find_animation_node(vector_to_number_box2.AnimationNodeInGet(), 'V')
						vector_to_number_box2_x_out = self.find_animation_node(vector_to_number_box2.AnimationNodeOutGet(), 'X')

						is_greater_box1_a_in = self.find_animation_node(is_greater_box1.AnimationNodeInGet(), 'a')
						is_greater_box1_b_in = self.find_animation_node(is_greater_box1.AnimationNodeInGet(), 'b')
						is_greater_box1_result_out = self.find_animation_node(is_greater_box1.AnimationNodeOutGet(), 'Result')

						is_less_box1_a_in = self.find_animation_node(is_less_box1.AnimationNodeInGet(), 'a')
						is_less_box1_b_in = self.find_animation_node(is_less_box1.AnimationNodeInGet(), 'b')
						is_less_box1_result_out = self.find_animation_node(is_less_box1.AnimationNodeOutGet(), 'Result')

						add_box1_a_in = self.find_animation_node(add_box1.AnimationNodeInGet(), 'a')
						add_box1_b_in = self.find_animation_node(add_box1.AnimationNodeInGet(), 'b')
						add_box1_result_out = self.find_animation_node(add_box1.AnimationNodeOutGet(), 'Result')

						divide_box1_a_in = self.find_animation_node(divide_box1.AnimationNodeInGet(), 'a')
						divide_box1_b_in = self.find_animation_node(divide_box1.AnimationNodeInGet(), 'b')
						divide_box1_result_out = self.find_animation_node(divide_box1.AnimationNodeOutGet(), 'Result')

						if_cond_box1_a_in = self.find_animation_node(if_cond_box1.AnimationNodeInGet(), 'a')
						if_cond_box1_b_in = self.find_animation_node(if_cond_box1.AnimationNodeInGet(), 'b')
						if_cond_box1_cond_in = self.find_animation_node(if_cond_box1.AnimationNodeInGet(), 'Cond')
						if_cond_box1_result_out = self.find_animation_node(if_cond_box1.AnimationNodeOutGet(), 'Result')

						if_cond_box2_a_in = self.find_animation_node(if_cond_box2.AnimationNodeInGet(), 'a')
						if_cond_box2_b_in = self.find_animation_node(if_cond_box2.AnimationNodeInGet(), 'b')
						if_cond_box2_cond_in = self.find_animation_node(if_cond_box2.AnimationNodeInGet(), 'Cond')
						if_cond_box2_result_out = self.find_animation_node(if_cond_box2.AnimationNodeOutGet(), 'Result')

						number_to_vector_box1_x_in = self.find_animation_node(number_to_vector_box1.AnimationNodeInGet(), 'X')
						number_to_vector_box1_result_out = self.find_animation_node(number_to_vector_box1.AnimationNodeOutGet(), 'Result')

						for up_leg in self.up_legs:
							if side in up_leg.Name.lower():
								if up_leg.ClassName() == 'FBModelSkeleton':
									source_sender_out_node = self.leg_up_roll_exp_const.SetAsSource(up_leg)
									source_sender_out_node.UseGlobalTransforms = False
									source_sender_out1 = self.find_animation_node(source_sender_out_node.AnimationNodeOutGet(), 'Lcl Rotation')

						for hips in self.hips:
							if hips.ClassName() == 'FBModelSkeleton':
								source_sender_out_node = self.leg_up_roll_exp_const.SetAsSource(hips)
								source_sender_out_node.UseGlobalTransforms = False
								source_sender_out2 = self.find_animation_node(source_sender_out_node.AnimationNodeOutGet(), 'Lcl Rotation')

						for up_leg_roll in self.up_leg_rolls:
							if side in up_leg_roll.Name.lower():
								if up_leg_roll.ClassName() == 'FBModelSkeleton':
									cobject_result_in_node = self.leg_up_roll_exp_const.ConstrainObject(up_leg_roll)
									cobject_result_in_node.UseGlobalTransforms = False
									cobject_result_in = self.find_animation_node(cobject_result_in_node.AnimationNodeInGet(), 'Lcl Rotation')

						is_greater_box1_a_in.WriteData([0.0])
						is_less_box1_a_in.WriteData([0.0])
						divide_box1_b_in.WriteData([-2.0])
						if_cond_box2_b_in.WriteData([0.0])

						if source_sender_out1 and source_sender_out2 and cobject_result_in:
							FBConnect(source_sender_out1, vector_to_number_box1_v_in)
							FBConnect(source_sender_out2, vector_to_number_box2_v_in)
							FBConnect(vector_to_number_box1_x_out, is_greater_box1_b_in)
							FBConnect(vector_to_number_box1_x_out, is_less_box1_b_in)
							FBConnect(vector_to_number_box1_x_out, add_box1_a_in)
							FBConnect(vector_to_number_box2_x_out, add_box1_b_in)
							FBConnect(add_box1_result_out, divide_box1_a_in)
							FBConnect(divide_box1_result_out, if_cond_box1_a_in)
							FBConnect(divide_box1_result_out, if_cond_box2_a_in)
							FBConnect(if_cond_box2_result_out, if_cond_box1_b_in)
							FBConnect(is_greater_box1_result_out, if_cond_box1_cond_in)
							FBConnect(is_less_box1_result_out, if_cond_box2_cond_in)
							FBConnect(if_cond_box1_result_out, number_to_vector_box1_x_in)
							FBConnect(number_to_vector_box1_result_out, cobject_result_in)

						FBSystem().Scene.Evaluate()

		#========================================= Lower Leg Rolls =======================================================
		if self.leg_rolls:
			for leg_roll in self.leg_rolls:
				if side in leg_roll.Name.lower():
					if leg_roll.ClassName() == 'FBModelSkeleton':
						if "Up" not in leg_roll.Name:
							vector_to_number_box1 = self.leg_roll_exp_const.CreateFunctionBox('Converters', 'Vector to Number')
							is_less_box1 = self.leg_roll_exp_const.CreateFunctionBox('Number', 'Is Less (a < b)')
							scale_and_offset_box1 = self.leg_roll_exp_const.CreateFunctionBox('Number', 'Scale And Offset (Number)')
							if_cond_box2 = self.leg_roll_exp_const.CreateFunctionBox('Number', 'IF Cond Then A Else B')
							number_to_vector_box1 = self.leg_roll_exp_const.CreateFunctionBox('Converters', 'Number to Vector')

							for foot in self.feet:
								if side in foot.Name.lower():
									if foot.ClassName() == 'FBModelSkeleton':
										source_sender_out_node = self.leg_roll_exp_const.SetAsSource(foot)
										source_sender_out_node.UseGlobalTransforms = False
										source_sender_out = self.find_animation_node(source_sender_out_node.AnimationNodeOutGet(), 'Lcl Rotation')

							for leg_roll in self.leg_rolls:
								if side in leg_roll.Name.lower():
									if leg_roll.ClassName() == 'FBModelSkeleton':
										if "Up" not in leg_roll.Name:
											cobject_result_in_node = self.leg_roll_exp_const.ConstrainObject(leg_roll)
											cobject_result_in_node.UseGlobalTransforms = False
											cobject_result_in = self.find_animation_node(cobject_result_in_node.AnimationNodeInGet(), 'Lcl Rotation')

							vector_to_number_box1_v_in = self.find_animation_node(vector_to_number_box1.AnimationNodeInGet(), 'V')
							vector_to_number_box1_x_out = self.find_animation_node(vector_to_number_box1.AnimationNodeOutGet(), 'X')

							is_less_box1_a_in = self.find_animation_node(is_less_box1.AnimationNodeInGet(), 'a')
							is_less_box1_b_in = self.find_animation_node(is_less_box1.AnimationNodeInGet(), 'b')
							is_less_box1_result_out = self.find_animation_node(is_less_box1.AnimationNodeOutGet(), 'Result')

							scale_and_offset_box1_offset_in = self.find_animation_node(scale_and_offset_box1.AnimationNodeInGet(), 'Offset')
							scale_and_offset_box1_scale_factor_in = self.find_animation_node(scale_and_offset_box1.AnimationNodeInGet(), 'Scale Factor')
							scale_and_offset_box1_x_in = self.find_animation_node(scale_and_offset_box1.AnimationNodeInGet(), 'X')
							scale_and_offset_box1_result_out = self.find_animation_node(scale_and_offset_box1.AnimationNodeOutGet(), 'Result')

							if_cond_box2_a_in = self.find_animation_node(if_cond_box2.AnimationNodeInGet(), 'a')
							if_cond_box2_b_in = self.find_animation_node(if_cond_box2.AnimationNodeInGet(), 'b')
							if_cond_box2_cond_in = self.find_animation_node(if_cond_box2.AnimationNodeInGet(), 'Cond')
							if_cond_box2_result_out = self.find_animation_node(if_cond_box2.AnimationNodeOutGet(), 'Result')

							number_to_vector_box1_x_in = self.find_animation_node(number_to_vector_box1.AnimationNodeInGet(), 'X')
							number_to_vector_box1_result_out = self.find_animation_node(number_to_vector_box1.AnimationNodeOutGet(), 'Result')

							is_less_box1_a_in.WriteData([0.0])
							scale_and_offset_box1_offset_in.WriteData([360.0])
							scale_and_offset_box1_scale_factor_in.WriteData([1.0])

							if source_sender_out and cobject_result_in:
								FBConnect(source_sender_out, vector_to_number_box1_v_in)
								FBConnect(vector_to_number_box1_x_out, is_less_box1_b_in)
								FBConnect(vector_to_number_box1_x_out, scale_and_offset_box1_x_in)
								FBConnect(vector_to_number_box1_x_out, if_cond_box2_b_in)
								FBConnect(is_less_box1_result_out, if_cond_box2_cond_in)
								FBConnect(scale_and_offset_box1_result_out, if_cond_box2_a_in)
								FBConnect(if_cond_box2_result_out, number_to_vector_box1_x_in)
								FBConnect(number_to_vector_box1_result_out, cobject_result_in)

							FBSystem().Scene.Evaluate()


	def set_linear_constraints( self ):
		"""
		Sets up the remaining constraints for the "one off" bones.

		*Arguments:*
			* ``None``

		*Keyword Arguments:*
			* ``None``

		*Returns:*
			* ``None``

		*Author:*
			* Jon Logsdon, jon.logsdon@volition-inc.com, 7/9/2014 2:15:54 PM
		"""

		curr_char_namespace = self.curr_char.LongName.split(":")

		#Position constraints
		self.aim_node_point_const = FBConstraintManager().TypeCreateConstraint(5)
		self.spine_bend_point_const = FBConstraintManager().TypeCreateConstraint(5)

		#Parent constraints
		self.anim_controller_parent_const = FBConstraintManager().TypeCreateConstraint(3)
		self.offset_parent_const = FBConstraintManager().TypeCreateConstraint(3)
		self.spine_bend_parent_const = FBConstraintManager().TypeCreateConstraint(3)
		self.aim_node_parent_const = FBConstraintManager().TypeCreateConstraint(3)
		self.left_hand_prop_parent_const = FBConstraintManager().TypeCreateConstraint(3)
		self.right_hand_prop_parent_const = FBConstraintManager().TypeCreateConstraint(3)

		#Aim constraints
		self.left_up_vector_aim_const = FBConstraintManager().TypeCreateConstraint(0)
		self.right_up_vector_aim_const = FBConstraintManager().TypeCreateConstraint(0)

		aim_node_grp = vmobu.core.get_objects_from_wildcard("*AimNodeGroup", use_namespace=True, models_only=False, single_only=True)
		anim_controller = vmobu.core.get_objects_from_wildcard("*AnimationController", use_namespace=True, models_only=False, single_only=True)
		spine_bend_controller = vmobu.core.get_objects_from_wildcard("*SpineBend_controller", use_namespace=True, models_only=False, single_only=True)
		hips = vmobu.core.get_objects_from_wildcard("*Hips", use_namespace=True, models_only=False, single_only=True)
		anim_controller_ctrl = vmobu.core.get_objects_from_wildcard("*AnimationController_controller", use_namespace=True, models_only=False, single_only=True)
		offset = vmobu.core.get_objects_from_wildcard("*Offset", use_namespace=True, models_only=False, single_only=True)
		offset_controller = vmobu.core.get_objects_from_wildcard("*Offset_controller", use_namespace=True, models_only=False, single_only=True)
		spine_bend_skel = vmobu.core.get_objects_from_wildcard("*SpineBend", use_namespace=True, models_only=False, single_only=True)
		aim_node = vmobu.core.get_objects_from_wildcard("*AimNode", use_namespace=True, models_only=False, single_only=True)
		aim_node_controller = vmobu.core.get_objects_from_wildcard("*AimNode_controller", use_namespace=True, models_only=False,single_only=True)
		left_hand_prop_skel = vmobu.core.get_objects_from_wildcard("*LeftHandProp", use_namespace=True, models_only=False, single_only=True)
		left_hand_prop_controller = vmobu.core.get_objects_from_wildcard("*left_handProp_controller", use_namespace=True, models_only=False, single_only=True)
		right_hand_prop_skel = vmobu.core.get_objects_from_wildcard("*RightHandProp", use_namespace=True, models_only=False, single_only=True)
		right_hand_prop_controller = vmobu.core.get_objects_from_wildcard("*right_handProp_controller", use_namespace=True, models_only=False, single_only=True)
		left_up_vector = vmobu.core.get_objects_from_wildcard("*LeftArm_UpVector", use_namespace=True, models_only=False, single_only=True)
		left_shoulder = vmobu.core.get_objects_from_wildcard("*LeftShoulder", use_namespace=True, models_only=False, single_only=True)
		right_up_vector = vmobu.core.get_objects_from_wildcard("*RightArm_UpVector", use_namespace=True, models_only=False, single_only=True)
		right_shoulder = vmobu.core.get_objects_from_wildcard("*RightShoulder", use_namespace=True, models_only=False, single_only=True)

		#self.aim_node_position_const
		self.aim_node_point_const.ReferenceAdd(0, aim_node_grp)
		self.aim_node_point_const.ReferenceAdd(1, anim_controller)
		self.aim_node_point_const.Name = '{0}:{1}:PosConst'.format(curr_char_namespace[0], aim_node_grp.Name)

		#self.spine_bend_position_const
		self.spine_bend_point_const.ReferenceAdd(0, spine_bend_controller)
		self.spine_bend_point_const.ReferenceAdd(1, hips)
		self.spine_bend_point_const.Name = '{0}:{1}:PosConst'.format(curr_char_namespace[0], spine_bend_controller.Name)

		#self.anim_controller_parent_const
		self.anim_controller_parent_const.ReferenceAdd(0, anim_controller)
		self.anim_controller_parent_const.ReferenceAdd(1, anim_controller_ctrl)
		self.anim_controller_parent_const.Name = '{0}:{1}:ParentConst'.format(curr_char_namespace[0], anim_controller.Name)

		#self.offset_parent_const
		self.offset_parent_const.ReferenceAdd(0, offset)
		self.offset_parent_const.ReferenceAdd(1, offset_controller)
		self.offset_parent_const.Name = '{0}:{1}:ParentConst'.format(curr_char_namespace[0], offset.Name)

		#self.spine_bend_parent_const
		self.spine_bend_parent_const.ReferenceAdd(0, spine_bend_skel)
		self.spine_bend_parent_const.ReferenceAdd(1, spine_bend_controller)
		self.spine_bend_parent_const.Name = '{0}:{1}:ParentConst'.format(curr_char_namespace[0], spine_bend_skel.Name)

		#self.aim_node_parent_const
		self.aim_node_parent_const.ReferenceAdd(0, aim_node)
		self.aim_node_parent_const.ReferenceAdd(1, aim_node_controller)
		self.aim_node_parent_const.Name = '{0}:{1}:ParentConst'.format(curr_char_namespace[0], aim_node.Name)

		#self.left_hand_prop_parent_const
		self.left_hand_prop_parent_const.ReferenceAdd(0, left_hand_prop_skel)
		self.left_hand_prop_parent_const.ReferenceAdd(1, left_hand_prop_controller)
		self.left_hand_prop_parent_const.Name = '{0}:{1}:ParentConst'.format(curr_char_namespace[0], left_hand_prop_skel.Name)

		#self.right_hand_prop_parent_const
		self.right_hand_prop_parent_const.ReferenceAdd(0, right_hand_prop_skel)
		self.right_hand_prop_parent_const.ReferenceAdd(1, right_hand_prop_controller)
		self.right_hand_prop_parent_const.Name = '{0}:{1}:ParentConst'.format(curr_char_namespace[0], right_hand_prop_skel.Name)

		#self.left_up_vector_aim_const
		self.left_up_vector_aim_const.ReferenceAdd(0, left_up_vector)
		self.left_up_vector_aim_const.ReferenceAdd(1, left_shoulder)
		for forearm in self.forearms:
			if not "Ctrl" in forearm.LongName:
				if forearm.ClassName() == 'FBModelSkeleton':
					if "Left" in forearm.Name:
						self.left_up_vector_aim_const.ReferenceAdd(2, forearm)
		self.left_up_vector_aim_const.Name = '{0}:{1}:AimConst'.format(curr_char_namespace[0], left_up_vector.Name)

		#self.right_up_vector_aim_const
		self.right_up_vector_aim_const.ReferenceAdd(0, right_up_vector)
		self.right_up_vector_aim_const.ReferenceAdd(1, right_shoulder)
		for forearm in self.forearms:
			if not "Ctrl" in forearm.LongName:
				if forearm.ClassName() == 'FBModelSkeleton':
					if "Right" in forearm.Name:
						self.right_up_vector_aim_const.ReferenceAdd(2, forearm)
		self.right_up_vector_aim_const.Name = '{0}:{1}AimConst'.format(curr_char_namespace[0], right_up_vector.Name)

		#Turn on constraints
		self.aim_node_point_const.Snap()
		self.spine_bend_point_const.Snap()
		self.anim_controller_parent_const.Snap()
		self.offset_parent_const.Snap()
		self.spine_bend_parent_const.Snap()
		self.aim_node_parent_const.Snap()
		self.left_hand_prop_parent_const.Snap()
		self.right_hand_prop_parent_const.Snap()
		self.left_up_vector_aim_const.Snap()
		self.right_up_vector_aim_const.Snap()

Mobu_Rig_Constraint_Builder().build_constraint()