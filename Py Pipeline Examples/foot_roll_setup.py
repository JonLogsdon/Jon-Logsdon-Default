"""
Creates foot roll setup using Aux Effectors, based on selection of Ankle effectors.
"""



# Motionbuilder lib
from pyfbsdk import *
from pyfbsdk_additions import *

# vmobu
import vmobu

class Aux_Foot_Setup:
	"""
	Sets up the Aux Effectors and proper connections for foot roll setup.
	"""

	def __init__( self ):
		self.curr_char = FBApplication( ).CurrentCharacter
		self.control_set = self.curr_char.GetCurrentControlSet( )

	def get_pivots_points( self ):
		"""
		Grabs the points of the foot ball and toe end, and initializes vectors for the positions.

		*Arguments:*
			* ``None``

		*Keyword Arguments:*
			* ``None``

		*Returns:*
			* ``None``
		"""

		global left_toe_base_vector, left_toe_base_end_vector, right_toe_base_vector, right_toe_base_end_vector

		selection = FBModelList( )
		FBGetSelectedModels( selection )
		for sel in selection:
			if "Left" in sel.Name:
				left_toe_base = vmobu.core.get_objects_from_wildcard( "*skel:LeftToeBase", use_namespace=True, models_only=False, single_only=True )
				left_toe_base_end = vmobu.core.get_objects_from_wildcard("*skel:LeftToeBaseEnd", use_namespace=True, models_only=False, single_only=True)

				left_toe_base_vector = FBVector3d( )
				left_toe_base_end_vector = FBVector3d( )

				left_toe_base.GetVector( left_toe_base_vector, FBModelTransformationType.kModelTranslation )
				left_toe_base_end.GetVector( left_toe_base_end_vector, FBModelTransformationType.kModelTranslation )

				FBSystem( ).Scene.Evaluate( )

			if "Right" in sel.Name:
				right_toe_base = vmobu.core.get_objects_from_wildcard("*skel:RightToeBase", use_namespace=True,
										                                    models_only=False, single_only=True)
				right_toe_base_end = vmobu.core.get_objects_from_wildcard("*skel:RightToeBaseEnd", use_namespace=True,
										                                        models_only=False, single_only=True)

				right_toe_base_vector = FBVector3d()
				right_toe_base_end_vector = FBVector3d()

				right_toe_base.GetVector( right_toe_base_vector, FBModelTransformationType.kModelTranslation)
				right_toe_base_end.GetVector( right_toe_base_end_vector, FBModelTransformationType.kModelTranslation)

				FBSystem().Scene.Evaluate()

	def create_aux( self, control=None, event=None ):
		"""
		Creates the aux effectors and sets their proper properties.

		*Arguments:*
			* ``control, event`` Allows this function to be using as a command for the Mobu UI "Run" button.

		*Keyword Arguments:*
			* ``None``

		*Returns:*
			* ``None``
		"""

		global aux, heel_null, ball_null, toe_null, effector, heel_null_vector, ball_null_vector, toe_null_vector

		FBSystem( ).Scene.Evaluate( )

		checked_items = 0

		#Check the states of the checkboxes in the UI to know what needs to be created.
		if heel_checkbox.State == True:
			checked_items = checked_items + 1
			heel_null = FBModelNull( "heel_user_fr_null" )
			heel_null_vector = FBVector3d( )
			heel_null.GetVector( heel_null_vector, FBModelTransformationType.kModelTranslation )
		if ball_checkbox.State == True:
			checked_items = checked_items + 1
			ball_null = FBModelNull( "ball_pivot_user_fr_null" )
			ball_null_vector = FBVector3d( )
			ball_null.GetVector( ball_null_vector, FBModelTransformationType.kModelTranslation )
		if toe_checkbox.State == True:
			checked_items = checked_items + 1
			toe_null = FBModelNull( "toe_user_fr_null" )
			toe_null_vector = FBVector3d( )
			toe_null.GetVector( toe_null_vector, FBModelTransformationType.kModelTranslation )

		#Create the constraint
		self.create_constraint( )

		#Get selection to start process
		selection = FBModelList( )
		FBGetSelectedModels( selection )
		for sel in selection:
			if sel.Name.startswith( "Left" ):
				#Check how many items are checked in the UI.
				for i in range( checked_items ):
					#Set effector and turn off the reaches.
					effector = self.control_set.GetIKEffectorModel( FBEffectorId.kFBLeftAnkleEffectorId, 0 )
					for prop in effector.PropertyList:
						if prop.Name == "IK Reach Translation":
							prop.Data = 0.0
						if prop.Name == "IK Reach Rotation":
							prop.Data = 0.0

					#Create the new Aux Effector
					aux = self.curr_char.CreateAuxiliary( FBEffectorId.kFBLeftAnkleEffectorId, False )
					new_selection = FBModelList( )
					FBGetSelectedModels( new_selection )
					for nsel in new_selection:
						#Go through state checks of different combos of selections of the UI checkboxes.
						if heel_checkbox.State == True and ball_checkbox.State == True and toe_checkbox.State == True:
							if i == 0:
								nsel.Name = effector.Name + "_" + heel_null.Name + "Aux"
								left_heel_fr_constraint_pc.ReferenceAdd( 1, nsel )
								for prop in nsel.PropertyList:
									if prop.Name == "IK Reach Translation":
										prop.Data = 0.0
									if prop.Name == "IK Reach Rotation":
										prop.Data = 0.0
							if i == 1:
								nsel.Name = effector.Name + "_" + ball_null.Name + "Aux"
								left_fr_constraint_pc.ReferenceAdd( 0, ball_null )
							if i == 2:
								nsel.Name = effector.Name + "_" + toe_null.Name + "Aux"

								left_fr_constraint_pc.ReferenceAdd( 1, nsel )
								left_heel_fr_constraint_pc.ReferenceAdd( 0, nsel)

								for prop in nsel.PropertyList:
									if prop.Name == "IK Reach Translation":
										prop.Data = 0.0
									if prop.Name == "IK Reach Rotation":
										prop.Data = 0.0

						if heel_checkbox.State == False:
							if ball_checkbox.State == True and toe_checkbox.State == True:
								if i == 0:
									nsel.Name = effector.Name + "_" + ball_null.Name + "Aux"
									left_fr_constraint_pc.ReferenceAdd( 0, ball_null )
								if i == 1:
									nsel.Name = effector.Name + "_" + toe_null.Name + "Aux"

									left_fr_constraint_pc.ReferenceAdd( 1, nsel )

									for prop in nsel.PropertyList:
										if prop.Name == "IK Reach Translation":
											prop.Data = 0.0
										if prop.Name == "IK Reach Rotation":
											prop.Data = 0.0

						if heel_checkbox.State == False and ball_checkbox.State == False:
							if toe_checkbox.State == True:
								if i == 0:
									nsel.Name = effector.Name + "_" + toe_null.Name + "Aux"

						if heel_checkbox.State == True and toe_checkbox.State == True:
							if ball_checkbox.State == False:
								if i == 0:
									nsel.Name = effector.Name + "_" + heel_null.Name + "Aux"
									left_heel_fr_constraint_pc.ReferenceAdd( 1, nsel )
									for prop in nsel.PropertyList:
										if prop.Name == "IK Reach Translation":
											prop.Data = 0.0
										if prop.Name == "IK Reach Rotation":
											prop.Data = 0.0
								if i == 1:
									nsel.Name = effector.Name + "_" + toe_null.Name + "Aux"
									left_heel_fr_constraint_pc.ReferenceAdd( 0, nsel )
									for prop in nsel.PropertyList:
										if prop.Name == "IK Reach Translation":
											prop.Data = 0.0
										if prop.Name == "IK Reach Rotation":
											prop.Data = 0.0

			if sel.Name.startswith( "Right" ):
				#Check how many items are checked in the UI.
				for i in range( checked_items ):
					#Set effector and turn off the reaches.
					effector = self.control_set.GetIKEffectorModel( FBEffectorId.kFBRightAnkleEffectorId, 0 )
					for prop in effector.PropertyList:
						if prop.Name == "IK Reach Translation":
							prop.Data = 0.0
						if prop.Name == "IK Reach Rotation":
							prop.Data = 0.0

					#Create the new Aux Effector
					aux = self.curr_char.CreateAuxiliary( FBEffectorId.kFBRightAnkleEffectorId, False )
					new_selection = FBModelList( )
					FBGetSelectedModels( new_selection )
					for nsel in new_selection:
						#Go through state checks of different combos of selections of the UI checkboxes.
						if heel_checkbox.State == True and ball_checkbox.State == True and toe_checkbox.State == True:
							if i == 0:
								nsel.Name = effector.Name + "_" + heel_null.Name + "Aux"
								right_heel_fr_constraint_pc.ReferenceAdd( 1, nsel )
								for prop in nsel.PropertyList:
									if prop.Name == "IK Reach Translation":
										prop.Data = 0.0
									if prop.Name == "IK Reach Rotation":
										prop.Data = 0.0
							if i == 1:
								nsel.Name = effector.Name + "_" + ball_null.Name + "Aux"
								right_fr_constraint_pc.ReferenceAdd( 0, ball_null )
							if i == 2:
								nsel.Name = effector.Name + "_" + toe_null.Name + "Aux"

								right_fr_constraint_pc.ReferenceAdd( 1, nsel )
								right_heel_fr_constraint_pc.ReferenceAdd( 0, nsel )

								for prop in nsel.PropertyList:
									if prop.Name == "IK Reach Translation":
										prop.Data = 0.0
									if prop.Name == "IK Reach Rotation":
										prop.Data = 0.0

						if heel_checkbox.State == False:
							if ball_checkbox.State == True and toe_checkbox.State == True:
								if i == 0:
									nsel.Name = effector.Name + "_" + ball_null.Name + "Aux"
									right_fr_constraint_pc.ReferenceAdd( 0, ball_null )
								if i == 1:
									nsel.Name = effector.Name + "_" + toe_null.Name + "Aux"

									right_fr_constraint_pc.ReferenceAdd( 1, nsel )

									for prop in nsel.PropertyList:
										if prop.Name == "IK Reach Translation":
											prop.Data = 0.0
										if prop.Name == "IK Reach Rotation":
											prop.Data = 0.0

						if heel_checkbox.State == False and ball_checkbox.State == False:
							if toe_checkbox.State == True:
								if i == 0:
									nsel.Name = effector.Name + "_" + toe_null.Name + "Aux"

						if heel_checkbox.State == True and toe_checkbox.State == True:
							if ball_checkbox.State == False:
								if i == 0:
									nsel.Name = effector.Name + "_" + heel_null.Name + "Aux"
									right_heel_fr_constraint_pc.ReferenceAdd( 1, nsel )
									for prop in nsel.PropertyList:
										if prop.Name == "IK Reach Translation":
											prop.Data = 0.0
										if prop.Name == "IK Reach Rotation":
											prop.Data = 0.0
								if i == 1:
									nsel.Name = effector.Name + "_" + toe_null.Name + "Aux"
									right_heel_fr_constraint_pc.ReferenceAdd( 0, nsel )
									for prop in nsel.PropertyList:
										if prop.Name == "IK Reach Translation":
											prop.Data = 0.0
										if prop.Name == "IK Reach Rotation":
											prop.Data = 0.0

		self.get_bone_positions( )
		self.place_null_nodes( )
		self.delete_created_nulls( )
		self.activate_constraint( )
		self.parent_effectors_to_nulls( )

	def place_null_nodes( self ):
		if heel_checkbox.State == True:
			heel_null.SetVector( heel_aux_vector, FBModelTransformationType.kModelTranslation  )
		if ball_checkbox.State == True:
			ball_null.SetVector( ball_aux_vector, FBModelTransformationType.kModelTranslation )
		if toe_checkbox.State == True:
			toe_null.SetVector( toe_aux_vector, FBModelTransformationType.kModelTranslation )

	def parent_effectors_to_nulls( self ):
		if heel_checkbox.State == True:
			#heel_aux = vmobu.core.get_objects_from_wildcard( "*Effector*heel*fr_null*Aux", use_namespace=True, single_only=True )
			heel_aux.Parent = heel_null
		if ball_checkbox.State == True:
			#ball_aux = vmobu.core.get_objects_from_wildcard( "*Effector*ball_pivot*fr_null*Aux", use_namespace=True,
																				#single_only=True )
			ball_aux.Parent = ball_null
		if toe_checkbox.State == True:
			#toe_aux = vmobu.core.get_objects_from_wildcard( "*Effector*toe*fr_null*Aux", use_namespace=True,
																				#single_only=True )
			toe_aux.Parent = toe_null

	def get_proper_bones( self ):
		"""
		Gets the proper bones for the nulls to be placed.

		*Arguments:*
			* ``None``

		*Keyword Arguments:*
			* ``None``

		*Returns:*
			* ``None``
		"""

		global left_ankle, left_ball_toe, left_toe, right_ankle, right_ball_toe, right_toe

		#Go through components and set the proper bones needed for the process.
		for comp in FBSystem( ).Scene.Components:
			if comp and comp.ClassName( ) == 'FBModelSkeleton':
				if comp.LongName.endswith( "ToeBaseEnd" ):
					if comp.Name.startswith( "Left" ):
						left_toe = comp
					if comp.Name.startswith( "Right" ):
						right_toe = comp
				if comp.LongName.endswith( "ToeBase" ):
					if comp.Name.startswith( "Left" ):
						left_ball_toe = comp
					if comp.Name.startswith( "Right" ):
						right_ball_toe = comp
				if comp.LongName.endswith( "Foot" ):
					if comp.Name.startswith( "Left" ):
						left_ankle = comp
					if comp.Name.startswith( "Right" ):
						right_ankle = comp

	def get_bone_positions( self ):
		"""
		Gets the bone position, and sets the offsets for the newly created aux effectors.

		*Arguments:*
			* ``None``

		*Keyword Arguments:*
			* ``None``

		*Returns:*
			* ``None``
		"""

		self.get_proper_bones( )

		FBSystem( ).Scene.Evaluate( )

		self.get_pivots_points( )

		selection = FBModelList( )
		FBGetSelectedModels( selection )
		for sel in selection:
			#Check which side you are creating for.
			if sel.Name.startswith( "Left" ):
				#Check checkbox state.
				if heel_checkbox.State == True:
					#Grab proper aux based on wildcard.
					global heel_aux, heel_aux_vector
					heel_aux = vmobu.core.get_objects_from_wildcard( "*Left*_heel*Aux", use_namespace=True, single_only=True )

					#Create for IKPivot and Lcl Translation to set the offsets needed for Aux Effectors.
					for prop in heel_aux.PropertyList:
						if prop.Name == 'IKPivot':
							prop.Data = FBVector3d( 0, 11, 0 )
						if prop.Name == 'Lcl Translation':
							v1 = FBVector3d( 0, 11, 0 )
							v2 = prop.Data

							prop.Data = v2 - v1

					heel_aux_vector = FBVector3d( )
					heel_aux.GetVector( heel_aux_vector, FBModelTransformationType.kModelTranslation )

				if ball_checkbox.State == True:
					global ball_aux, ball_aux_vector
					ball_aux = vmobu.core.get_objects_from_wildcard( "*Left*_ball_pivot*Aux", use_namespace=True, single_only=True )
					ball_aux.SetVector( FBVector3d( left_toe_base_vector ), FBModelTransformationType.kModelTranslation )
					for prop in ball_aux.PropertyList:
						if prop.Name == 'IKPivot':
							prop.Data = FBVector3d( 0, 11, -14 )
						if prop.Name == 'Lcl Translation':
							v1 = FBVector3d( 0, 11, -14 )
							v2 = prop.Data

							prop.Data = v2 - v1

					ball_aux_vector = FBVector3d( )
					ball_aux.GetVector( ball_aux_vector, FBModelTransformationType.kModelTranslation )

				if toe_checkbox.State == True:
					global toe_aux, toe_aux_vector
					toe_aux = vmobu.core.get_objects_from_wildcard( "*Left*_toe*Aux", use_namespace=True, single_only=True )
					toe_aux.SetVector( FBVector3d( left_toe_base_end_vector ), FBModelTransformationType.kModelTranslation )
					for prop in toe_aux.PropertyList:
						if prop.Name == 'IKPivot':
							prop.Data = FBVector3d( 0, 11, -20 )
						if prop.Name == 'Lcl Translation':
							v1 = FBVector3d( 0, 11, -20 )
							v2 = prop.Data

							prop.Data = v2 - v1

					toe_aux_vector = FBVector3d( )
					toe_aux.GetVector( toe_aux_vector, FBModelTransformationType.kModelTranslation )

			if sel.Name.startswith( "Right" ):
				effector = self.control_set.GetIKEffectorModel( FBEffectorId.kFBRightAnkleEffectorId, 0 )
				if heel_checkbox.State == True:
					heel_aux = vmobu.core.get_objects_from_wildcard( "*Right*_heel*Aux", use_namespace=True,
													                         single_only=True )

					for prop in heel_aux.PropertyList:
						if prop.Name == 'IKPivot':
							prop.Data = FBVector3d( 0, 11, 0 )
						if prop.Name == 'Lcl Translation':
							v1 = FBVector3d( 0, 11, 0 )
							v2 = prop.Data

							prop.Data = v2 - v1

					heel_aux_vector = FBVector3d( )
					heel_aux.GetVector( heel_aux_vector, FBModelTransformationType.kModelTranslation )

				if ball_checkbox.State == True:
					ball_aux = vmobu.core.get_objects_from_wildcard( "*Right*_ball_pivot*Aux", use_namespace=True,
													                         single_only=True )
					ball_aux.SetVector(FBVector3d(right_toe_base_vector), FBModelTransformationType.kModelTranslation)
					for prop in ball_aux.PropertyList:
						if prop.Name == 'IKPivot':
							prop.Data = FBVector3d( 0, 11, -14 )
						if prop.Name == 'Lcl Translation':
							v1 = FBVector3d( 0, 11, -14 )
							v2 = prop.Data

							prop.Data = v2 - v1

					ball_aux_vector = FBVector3d( )
					ball_aux.GetVector( ball_aux_vector, FBModelTransformationType.kModelTranslation )

				if toe_checkbox.State == True:
					toe_aux = vmobu.core.get_objects_from_wildcard( "*Right*_toe*Aux", use_namespace=True, single_only=True )
					toe_aux.SetVector(FBVector3d(right_toe_base_end_vector), FBModelTransformationType.kModelTranslation)
					for prop in toe_aux.PropertyList:
						if prop.Name == 'IKPivot':
							prop.Data = FBVector3d( 0, 11, -20 )
						if prop.Name == 'Lcl Translation':
							v1 = FBVector3d( 0, 11, -20 )
							v2 = prop.Data

							prop.Data = v2 - v1

					toe_aux_vector = FBVector3d( )
					toe_aux.GetVector( toe_aux_vector, FBModelTransformationType.kModelTranslation )

		self.activate_floor_contacts( )

	def create_constraint( self ):
		"""
		Creates the Parent/Child constraint, to remain off until entire process is over.

		*Arguments:*
			* ``None``

		*Keyword Arguments:*
			* ``None``

		*Returns:*
			* ``None``
		"""

		#Create Parent/Child constraints.
		global left_fr_constraint_pc, right_fr_constraint_pc, left_heel_fr_constraint_pc, right_heel_fr_constraint_pc

		left_fr_constraint_pc = FBConstraintManager( ).TypeCreateConstraint( 3 )
		left_fr_constraint_pc.Name = "LeftFootRollConst"
		left_heel_fr_constraint_pc = FBConstraintManager( ).TypeCreateConstraint( 3 )
		left_heel_fr_constraint_pc.Name = "LeftHeelFootRollConst"
		right_fr_constraint_pc = FBConstraintManager( ).TypeCreateConstraint( 3 )
		right_fr_constraint_pc.Name = "RightFootRollConst"
		right_heel_fr_constraint_pc = FBConstraintManager( ).TypeCreateConstraint( 3 )
		right_heel_fr_constraint_pc.Name = "RightHeelFootRollConst"

		'''selection = FBModelList( )
		FBGetSelectedModels( selection )
		for sel in selection:
			if "Left" in sel.Name:
				if ball_checkbox.State == True and toe_checkbox.State == True:
					left_fr_constraint_pc = FBConstraintManager( ).TypeCreateConstraint( 3 )
					left_fr_constraint_pc.Name = "LeftFootRollConst"
				if heel_checkbox.State == True:
					left_heel_fr_constraint_pc = FBConstraintManager( ).TypeCreateConstraint( 3 )
					left_heel_fr_constraint_pc.Name = "LeftHeelFootRollConst"

			if "Right" in sel.Name:
				if ball_checkbox.State == True and toe_checkbox.State == True:
					right_fr_constraint_pc = FBConstraintManager( ).TypeCreateConstraint( 3 )
					right_fr_constraint_pc.Name = "RightFootRollConst"
				if heel_checkbox.State == True:
					right_heel_fr_constraint_pc = FBConstraintManager( ).TypeCreateConstraint( 3 )
					right_heel_fr_constraint_pc.Name = "RightHeelFootRollConst"   '''

	def delete_created_nulls( self ):
		"""
		Deletes the created nulls during the process.

		*Arguments:*
			* ``None``

		*Keyword Arguments:*
			* ``None``

		*Returns:*
			* ``None``
		"""

		#Search for the nulls created and delete them.
		for comp in FBSystem( ).Scene.Components:
			if comp.ClassName( ) == 'FBModelNull':
				if comp.Name == "Test":
					comp.FBDelete( )
					FBSystem( ).Scene.Evaluate( )

	def activate_constraint( self ):
		"""
		Activates the Parent/Child constraint.

		*Arguments:*
			* ``None``

		*Keyword Arguments:*
			* ``None``

		*Returns:*
			* ``None``
		"""

		#Activate constraints
		FBSystem( ).Scene.Evaluate( )
		left_fr_constraint_pc.Snap( )
		right_fr_constraint_pc.Snap( )
		left_heel_fr_constraint_pc.Snap( )
		right_heel_fr_constraint_pc.Snap( )

	def activate_floor_contacts( self ):
		"""
		Activates the floor contacts for the foot and toes.

		*Arguments:*
			* ``None``

		*Keyword Arguments:*
			* ``None``

		*Returns:*
			* ``None``
		"""

		#Find proper floor contact properties for "Feet" and "Toes".
		curr_char = FBApplication( ).CurrentCharacter
		feet_contact_prop = curr_char.PropertyList.Find( 'FootFloorContact' )
		toe_contact_prop = curr_char.PropertyList.Find( 'FootFingerContact' )

		feet_contact_prop.Data = True
		toe_contact_prop.Data = True

	def populate_ui( self, t ):
		global heel_checkbox, ball_checkbox, toe_checkbox

		x = FBAddRegionParam( 15, FBAttachType.kFBAttachNone, "" )
		y = FBAddRegionParam( 15, FBAttachType.kFBAttachNone, "" )
		w = FBAddRegionParam( 80, FBAttachType.kFBAttachNone, "" )
		h = FBAddRegionParam( 25, FBAttachType.kFBAttachNone, "" )
		t.AddRegion( "heel_cb", "heel_cb", x,y,w,h )

		heel_checkbox = FBButton( )
		heel_checkbox.Caption = "Heel"
		heel_checkbox.Style = FBButton( ).Style.kFBCheckbox
		heel_checkbox.Justify = FBTextJustify.kFBTextJustifyCenter
		heel_checkbox.State = False

		t.SetControl( "heel_cb", heel_checkbox )

		x = FBAddRegionParam( 65, FBAttachType.kFBAttachNone, "" )
		y = FBAddRegionParam( 15, FBAttachType.kFBAttachNone, "" )
		w = FBAddRegionParam( 80, FBAttachType.kFBAttachNone, "" )
		h = FBAddRegionParam( 25, FBAttachType.kFBAttachNone, "" )
		t.AddRegion( "ball_cb", "ball_cb", x, y, w, h )

		ball_checkbox = FBButton( )
		ball_checkbox.Caption = "Ball/Pivot"
		ball_checkbox.Style = FBButton( ).Style.kFBCheckbox
		ball_checkbox.Justify = FBTextJustify.kFBTextJustifyCenter
		ball_checkbox.State = True

		t.SetControl( "ball_cb", ball_checkbox )

		x = FBAddRegionParam( 145, FBAttachType.kFBAttachNone, "" )
		y = FBAddRegionParam( 15, FBAttachType.kFBAttachNone, "" )
		w = FBAddRegionParam( 120, FBAttachType.kFBAttachNone, "" )
		h = FBAddRegionParam( 25, FBAttachType.kFBAttachNone, "" )
		t.AddRegion( "toe_cb", "toe_cb", x, y, w, h )

		toe_checkbox = FBButton( )
		toe_checkbox.Caption = "Toe"
		toe_checkbox.Style = FBButton( ).Style.kFBCheckbox
		toe_checkbox.Justify = FBTextJustify.kFBTextJustifyCenter
		toe_checkbox.State = True

		t.SetControl( "toe_cb", toe_checkbox )

		x = FBAddRegionParam( 65, FBAttachType.kFBAttachNone, "" )
		y = FBAddRegionParam( 55, FBAttachType.kFBAttachNone, "" )
		w = FBAddRegionParam( 120, FBAttachType.kFBAttachNone, "" )
		h = FBAddRegionParam( 25, FBAttachType.kFBAttachNone, "" )
		t.AddRegion( "run", "run", x, y, w, h )

		run_button = FBButton( )
		run_button.Caption = "Run"
		run_button.Justify = FBTextJustify.kFBTextJustifyCenter
		run_button.OnClick.Add( self.create_aux )

		t.SetControl( "run", run_button )

	def main( self ):
		"""
		Runs the UI, syncing the methods to the tool.

		*Arguments:*
			* ``None``

		*Keyword Arguments:*
			* ``None``

		*Returns:*
			* ``None``
		"""

		t = FBCreateUniqueTool( "Foot Roll Setup v2.0.0" )
		t.StartSizeX = 275
		t.StartSizeY = 120
		self.populate_ui( t )
		ShowTool( t )

def run( ):
	if not FBApplication().CurrentCharacter:
		FBMessageBox( 'Foot Roll Error', 'Must have a character selected!', 'OK' )
		return False

	foot_roll = Aux_Foot_Setup( )
	foot_roll.main( )
