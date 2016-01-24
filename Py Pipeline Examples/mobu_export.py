"""
Export utilities

*Todo:*
	* KS: ATM, this is just a placeholder for anticipated classes\methods yet to be implemented.
"""

# Motionbuilder Python SDK
import pyfbsdk
import os
import json

# Volition Common DCC lib...
import file_io.v_path

# Motionbuilder tools API
import core
import vmobu
import vmobu.const
import vmobu.mobu_file
import vmobu.mobu_perforce

from vlib.dcc.python.ui.progress_dialog import V_PROGRESS_BAR

DEBUG = False


class Mobu_Export( vmobu.VMoBu_Core ):
	"""
	Super class and foundational MotionBuilder utility library
	"""

	def __init__(self):
		""" Mobu_Export.__init__():  set initial parameters """
		super(Mobu_Export, self).__init__()

		self.final_save_filepath = None
		self.project_dir = core.const.workspace_dir


	def make_path_relative( self, absolute_path, working_dir ):
		"""
		Finds path relative to project working directory

		*Arguments:*
			* ``absolute_path`` complete path
			* ``working_dir`` project path

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``relative_path`` path relative to working dir
		"""

		relative_path = absolute_path

		if working_dir:
			working_dir = file_io.v_path.Path( working_dir ).pretty.string( ).lower( )
		else:
			working_dir = None

		if absolute_path:
			absolute_path = file_io.v_path.Path( absolute_path ).pretty.string( ).lower( )
		else:
			absolute_path = None

		if absolute_path and working_dir:
			if absolute_path.startswith( working_dir ):
				relative_path = absolute_path[ len( working_dir ): ]
				relative_path = relative_path.replace( '/', '\\' )

		return relative_path


	def validate_file_path( self, path, must_contain = None ):
		"""
		Make sure path exists on disk and is in a valid package location

		*Arguments:*
			* ``path`` path to check

		*Keyword Arguments:*
			* ``must_contain`` If necessary check addition directories

		*Returns:*
			* ``True`` if successful
		"""

		# make sure the path exists
		if not self.project_dir in path:
			abs_path = os.path.join( self.project_dir, path )
			if not os.path.exists( abs_path ):
				if not path.lower() == 'none':
					try:
						os.makedirs( abs_path )
					except WindowsError:
						return False
		else:
			abs_path = path

		# make sure the path is in a valid package
		found_package = False
		pretty_path = file_io.v_path.Path( abs_path ).make_pretty( False, True )
		if pretty_path:
			for package_dir in vmobu.const.PROJECT_PACKAGE_DIRS:
				if package_dir in pretty_path:
					found_package = True
					break

		# check any additional locations
		if must_contain:
			if pretty_path:
				if must_contain in pretty_path:
					return True
				else:
					return False

		if found_package:
			return True

		return False


	def validate_resource_file( self, filename ):
		"""
		Make sure the rig is a valid resource before exporting animation

		*Arguments:*
			* ``filename`` filename to check

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``bool`` If the rig is a valid resource
			* ``filename`` relative path of the filename found
		"""

		relative_resource_filename = None

		if filename:

			# get the resourcelib info on the file
			file_info = None
			try:
				file_info = file_io.resource_lib._resourcelib.get_file_info( os.path.basename( filename ) )
			except RuntimeError:
				return False, relative_resource_filename
			except ValueError:
				return False, relative_resource_filename

			if file_info:
				# get the relative file path
				relative_resource_filename = file_info.get_local_relative_filename( )
				return True, relative_resource_filename

			else:
				return False, relative_resource_filename
		else:
			return False, relative_resource_filename

		return False, relative_resource_filename


	def can_export_file( self, filepath ):
		"""
		Check to see if the file is a resource.
		- If it is make sure your file path is the same
		- If it is make sure it is synced
		- If it is make sure it can be checked out

		*Arguments:*
			* ``filepath`` file to check

		*Keyword Arguments:*
			* ``Argument`` Enter a description for the keyword argument here.

		*Returns:*
			* ``Value`` If any, enter a description for the return value here.
		"""

		# make sure there is only one resource location for the animation file
		file_info = None
		file_base_name = os.path.basename( filepath )

		try:
			file_info = file_io.resource_lib._resourcelib.get_file_info( file_base_name )
		except RuntimeError:
			# this may be a new file so there may not yet be a resource
			pass

		# make sure the resourcelib file and the current file are the same
		if file_info:

			local_file = file_info.full_local_filename

			# make the files relative so that we can compare properly
			rel_local_file = self.make_path_relative( local_file, self.project_dir )
			rel_filepath = self.make_path_relative( filepath, self.project_dir )
			if not rel_local_file == rel_filepath:
				message = 'error1_ABORTING EXPORT!\n\nExported file resource already exists in another location.\n {0}\n {1}'.format( rel_local_file, rel_filepath )
				return False, message

			else:
				# Get the target files of the local file
				anim_pc_filepath = local_file.replace( 'anim.fbx', 'anim_pc' )
				anim_ps4_filepath = local_file.replace( 'anim.fbx', 'anim_ps4' )
				anim_xbox3_filepath = local_file.replace( 'anim.fbx', 'anim_xbox3' )
				anim_files = [ local_file, anim_pc_filepath, anim_ps4_filepath, anim_xbox3_filepath ]

				# sync the file
				for file_name in anim_files:
					have_latest = vmobu.mobu_perforce.mb_perforce.have_latest( file_name )
					if not have_latest:
						print 'Syncing file: {0}'.format( file_name )
						sync_file = vmobu.mobu_perforce.mb_perforce.get_latest( file_name )

				# since this is a resource try to check it out
				user = vmobu.mobu_perforce.mb_perforce.already_checkedout( filepath, include_self=False )
				if user:
					message = "ABORTING EXPORT!\n\nExported file checked out by: {0}\n{1}".format( user, filepath )
					return False, message

				# try to check out the file
				if not vmobu.mobu_perforce.mb_perforce.checkout( filepath, quiet=True ):
					message = 'ABORTING EXPORT!\n\nCould not check out the exported file:\n {0}'.format( filepath )
					return False, message

		else:

			# check the package location
			if not self.validate_file_path( filepath ):
				message = ( 'The export path defined is not in a valid package location!\n{0}\n\nPlease select a valid package location!\n\n{1}'.format( filepath, vmobu.const.PROJECT_PACKAGE_STRING ) )
				return False, message

			# make the directory
			if not os.path.lexists( os.path.dirname( filepath ) ):
				os.makedirs( os.path.dirname( filepath ) )

		return True, 'Valid File'


	def update_data_path( self, filepath ):
		"""
		Utility method to handle changing data paths when known file locations change in the depot.
		A dictionary of old paths and new paths set in const.py will be referenced when changes paths

		*Arguments:*
			* ``filepath`` Filepath to check if we need to swap the locations

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``string`` New filepath if changed

		*Examples:* ::

			update_data_path( 'project_dir\data\test\anim' )
			return 'project_dir\data\core_game\anim\clips\

		*Todo:*
			* Enter thing to do. (optional field)
		"""

		updated_path = filepath #.replace( '\\', '/' )
		for key, value in vmobu.const.FIX_DATA_PATHS.iteritems( ):
			if key in filepath:
				updated_path = filepath.replace( key, value )
				break

		return updated_path


	def update_controller_constraints( self, anim_node, namespace ):
		"""
		Sets the anim controller, offset bone, and aim node to be at the character's feet for export.

		*Arguments:*
		  * ``anim_node`` animation node, note object
		  * ``namespace`` namespace of the character being exported

		*Keyword Arguments:*
		  * ``None``

		*Returns:*
		  * ``None``
		"""

		# dictionary of bones and their controller counterparts
		bones_and_controllers = { 'Offset' : 'Offset_controller',
					                 'AnimationController' : 'AnimationController_controller',
					                 'AimNode' : 'AimNodeGroup' }

		for bone_name, controller_name in bones_and_controllers.iteritems():
			# get the nodes
			bone_node = vmobu.core.get_objects_from_wildcard( namespace + ':*:' + bone_name, use_namespace=True, single_only=True )
			controller_node = vmobu.core.get_objects_from_wildcard( namespace + ':*:' + controller_name, use_namespace=True, single_only=True )

			# make sure we got the nodes
			if not bone_node or not controller_node:
				error_message = 'Could not find the {0} bone or the {1} controller object'.format( bone_name, controller_name )
				self.logger.warning( error_message )
				return False, error_message

			# get and unlock the constraint
			if bone_node.IsConstrained:
				for index in range( bone_node.GetSrcCount() ):
					source = bone_node.GetSrc( index )
					if isinstance( source, pyfbsdk.FBConstraint ):
						lock_prop = vmobu.core.get_property( source, 'Lock', return_value = False )
						if lock_prop:
							lock_prop.Data = False

			# create vectors
			vector_trans = pyfbsdk.FBVector3d( )
			vector_rot = pyfbsdk.FBVector3d( )

			# get the vectors from the controller
			controller_node.GetVector( vector_rot, pyfbsdk.FBModelTransformationType.kModelRotation )
			controller_node.GetVector( vector_trans, pyfbsdk.FBModelTransformationType.kModelTranslation )

			# set the vectors on the bone
			bone_node.SetVector( pyfbsdk.FBVector3d( vector_trans ), pyfbsdk.FBModelTransformationType.kModelTranslation )
			bone_node.SetVector( pyfbsdk.FBVector3d( vector_rot ), pyfbsdk.FBModelTransformationType.kModelRotation )

			# refresh the scene
			pyfbsdk.FBSystem( ).Scene.Evaluate( )

		return True, 'Updated_Constraint Nodes'


	def remove_backup_folder( self, filepath='' ):
		"""
		Removes the backup folder created when exporting.

		*Arguments:*
		  * ``None``

		*Keyword Arguments:*
		  * ``filepath`` Filepath of export file

		*Returns:*
		  * ``None``
		"""

		if filepath:
			for file_ in os.listdir( filepath ):
				curr_file = os.path.join( filepath, file_ )
				try:
					if os.path.isfile( curr_file ):
						os.unlink( curr_file )
				except IOError:
					pass

			# finally delete the folder
			if os.path.exists( filepath ):
				os.rmdir( filepath )

	def bake_camera_bone_data ( self, camera_bone, fov_shift = 0 ):
		"""
		   bakes down the camera settings onto the camera bone of the rig

			*Arguments:*
			  * ``camera_bone`` - The bone you are baking down to

			*Keyword Arguments:*
			  * ``None``

			*Returns:*
			  * ``None``
			"""

		# The runtime camera of the character rig
		camera_runtime = None

		#Grab the current take stop and start frames
		anim_start = vmobu.core.system.CurrentTake.LocalTimeSpan.GetStart( ).GetFrame( )
		anim_end   = vmobu.core.system.CurrentTake.LocalTimeSpan.GetStop( ).GetFrame( )

		if camera_bone:
			# remember current frame
			original_frame = vmobu.core.get_frame_current( )
			# Set Camera bone FOV Attribute = to Focal Length of Runtime Camera
			camera_fov =  camera_bone.PropertyList.Find( 'FieldOfView' )
			camera_fov_cust_prop = camera_bone.PropertyList.Find( "p_ft_camera_fov" )
			camera_weight_cust_property = camera_bone.PropertyList.Find( 'p_ft_camera_weight' )

			# If we found the properties
			if camera_fov and camera_fov_cust_prop and camera_weight_cust_property:
				# If camera runtime is found, do the following on each frame of the animation
				for t in range ( int( anim_start ), int( anim_end + 1 ) ):
					pyfbsdk.FBPlayerControl( ).Goto( pyfbsdk.FBTime( 0, 0, 0, t ) )

					vmobu.core.evaluate( )
					camera_fov_cust_prop.Data = camera_fov.Data + fov_shift
					camera_fov_cust_prop.Key( )

					# SEt the property to itself so we can make it dirty?
					camera_weight_cust_property.Data = float( camera_weight_cust_property.Data )
					camera_weight_cust_property.Key( )

				## TODO: Calculate Blur/Expose this on the runtime camera somehow
				# They otherwise have to change this attribute by hand

			# Transfer near clip and far clip plane values to the Camera Bone
			near_clip_plane =  camera_bone.PropertyList.Find( 'NearPlane' )
			near_clip_cust_prop = camera_bone.PropertyList.Find( "p_ft_camera_near_clip_plane" )

			far_clip_plane =  camera_bone.PropertyList.Find( 'FarPlane' )
			far_clip_cust_prop = camera_bone.PropertyList.Find( "p_ft_camera_far_clip_plane" )

			if near_clip_plane and near_clip_cust_prop and far_clip_plane and far_clip_cust_prop:
				near_clip_cust_prop.Data = near_clip_plane.Data
				far_clip_cust_prop.Data = far_clip_plane.Data

			# Set DOF flag
			apply_dof = camera_bone.PropertyList.Find( 'UseDepthOfField' )
			apply_dof_cust_prop = camera_bone.PropertyList.Find( 'p_ft_camera_apply_dof' )

			if apply_dof and apply_dof_cust_prop:
				apply_dof_cust_prop.Data = apply_dof.Data

			#vmobu.core.plot_on_objects( [ camera_bone ] )

		return True


	def get_animation_length( self, anim_node, anim_name ):
		"""
		Get the length of the animation from the anim start and anim end values

		*Arguments:*
			* ``anim_node`` anim node object, Note node
			* ``anim_name`` name of the animation

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``Int`` length of the animation
		"""

		# animation enum properties
		anim_node_prop = vmobu.core.get_property( anim_node, anim_name, return_value = False )
		anim_start = None
		anim_end = None
		if anim_node_prop:
			prop_indices = [1,2]
			for index in prop_indices:
				prop_take_enum = anim_node_prop.EnumList( index )
				prop_take_split = prop_take_enum.split( ':' )
				if prop_take_split:
					if index == 1:
						anim_start = prop_take_split[1]
					else:
						anim_end = prop_take_split[1]

		# get the animation length
		animation_length = 1
		if anim_start and anim_end:
			animation_length = int(anim_end) - int(anim_start)

		return animation_length


	def get_children_recursive( self, node, children = [ ], has_prop = None ):
		"""
		Get all the children of a node recursively, not just the direct children
		Optionally, only return nodes of specific types using property checks

		*Arguments:*
			* ``node`` Node to return list of children from
			* ``children`` list of children to update

		*Keyword Arguments:*
			* ``has_prop`` Check of the child object has a property

		*Returns:*
			* ``list`` List of children nodes
		"""

		for child in node.Children:
			# only get objects with a property
			if has_prop:
				if vmobu.core.get_property( child, 'p_bone_name' ):
					children.append( child )

			self.get_children_recursive( child, children, has_prop = has_prop )

		return children


	def get_controller_nodes( self, namespace ):
		"""
		Get the animation controller nodes by namespace.

		*Arguments:*
			* ``namespace`` Namespace to wildcard search for

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``list`` list of animation controller nodes
		"""

		controller_nodes = []
		controller_names = []
		for name in vmobu.const.ANIMATION_CONTROLLER_NAMES:
			controller_node = vmobu.core.get_objects_from_wildcard( namespace + "*:" + name, use_namespace=True, single_only=True )
			if controller_node:
				controller_nodes.append( controller_node )
				controller_names.append( controller_node.Name )

		return controller_nodes, controller_names


	def validate_rig_file( self, anim_node, master_node, rig_file ):
		"""
		Make sure the given rig file is updated and valid

		*Arguments:*
			* ``anim_node`` animation node, Note object
			* ``master_node`` master node, helper object with export parameters

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``Bool`` True if valid
		"""

		if not anim_node or not master_node:
			return False, 'The anim_node or master_node was not valid!'

		# make sure the rig is a valid resource
		rig_is_valid, rig_filename = self.validate_resource_file( rig_file )
		if rig_is_valid:

			# update the properties in case the file location has changed
			vmobu.core.set_property( anim_node, 'p_export_rig', rig_filename )
			vmobu.core.set_property( master_node, 'p_export_rig', rig_filename )
			return True, rig_filename, 'Rig is valid'

		else:
			error_message = 'The rig assigned is not a valid resource!\n{0}'.format( rig_file )
			self.logger.warning( error_message )
			return False, rig_filename, error_message


	def validate_anim_path( self, anim_node, master_node, anim_path ):
		"""
		Make sure the animation path is updated and valid

		*Arguments:*
			* ``anim_node`` animation node, Note object
			* ``master_node`` master node, helper object with export parameters
			* ``anim_path`` animation file path

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``Bool`` if valid
			* ``animation path`` if valid, return the path
			* ``string`` if not valid return the error string
		"""

		if not anim_node or not master_node:
			return False, None, 'The anim_node or master_node was not valid!'

		# update the anim path if the base filepaths have changed
		updated_anim_path = self.update_data_path( anim_path )
		anim_export_path = self.make_path_relative( updated_anim_path, self.project_dir )
		if anim_export_path:
			# update the anim path in the animNode and Master
			vmobu.core.set_property( anim_node, 'p_anim_file',   str( anim_export_path ) )
			vmobu.core.set_property( master_node, 'p_anim_file', str( anim_export_path ) )

		else:
			error_message = 'The updated animation path was incorrect: {0}'.format( updated_anim_path )
			self.logger.warning( error_message )
			return False, anim_export_path, error_message

		# make sure the anim export path is valid
		if not self.validate_file_path( anim_export_path, must_contain = 'anim\\clips' ):
			error_message = 'The anim export path selected is not in a valid package location!\n{0}\n\nPlease select a valid package location containing "anim\clips"!\n{1}'.format( anim_export_path, vmobu.const.PROJECT_PACKAGE_STRING )
			self.logger.warning( error_message )
			return False, anim_export_path, error_message

		else:
			return True, anim_export_path, 'Anim path is valid'

class Mobu_FBX_Export( Mobu_Export ):
	"""
	Sub-class to hold any methods that have to do with exporting fbx

	*Examples:* ::

		>>> import vmobu.mobu_export
		>>> m_fbx_export = vmaya.mobu_export.Mobu_FBX_Export()
	"""

	def __init__( self ):
		super( Mobu_FBX_Export, self ).__init__( )

		# debug
		if DEBUG:
			self.logger.level = 10
		else:
			self.logger.level = 20

		self.filepath = None
		self.filename = None


	def get_fbx_options( self, take_name=None, export_type = 'Animation' ):
		"""
		Get a predefined fbx option setting based on export_type give

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``take_name`` If we need to export only a specific take set that here
			* ``export_type`` The specific type of export that should return a specific fbx_options

		*Returns:*
			* ``fbx_options`` fbx export options object
		"""

		if export_type == 'Animation':
			# set the fbx flags
			fbx_options = pyfbsdk.FBFbxOptions( False )

			# new options
			fbx_options.SetAll( pyfbsdk.FBElementAction.kFBElementActionDiscard, False )
			fbx_options.UseASCIIFormat = True
			fbx_options.Bones = pyfbsdk.FBElementAction.kFBElementActionSave
			fbx_options.BonesAnimation = True
			fbx_options.Cameras = pyfbsdk.FBElementAction.kFBElementActionSave
			fbx_options.CamerasAnimation = True
			fbx_options.Models = pyfbsdk.FBElementAction.kFBElementActionSave
			fbx_options.ModelsAnimation = True
			fbx_options.Characters = pyfbsdk.FBElementAction.kFBElementActionDiscard
			fbx_options.Actors = pyfbsdk.FBElementAction.kFBElementActionDiscard
			fbx_options.Constraints = pyfbsdk.FBElementAction.kFBElementActionDiscard
			fbx_options.Solvers = pyfbsdk.FBElementAction.kFBElementActionDiscard
			fbx_options.CharactersAnimation = False
			fbx_options.SaveControlSet = False
			fbx_options.SaveSelectedModelsOnly = True

			# set the active take only to export
			if take_name:
				#for take in pyfbsdk.FBSystem( ).Scene.Takes:
				for index in range( fbx_options.GetTakeCount( ) ):
					fbx_take_name = fbx_options.GetTakeName( index )
					if fbx_take_name == take_name:
						fbx_options.SetTakeSelect( index, True )
					else:
						fbx_options.SetTakeSelect( index, False )
		else:
			fbx_options = pyfbsdk.FBFbxOptions( True )
			fbx_options.UseASCIIFormat = True

		return fbx_options


	def export( self, filepath = None, character = None, fbx_options = None, remove_namespace = True ):
		"""
		Perform export process

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``filepath`` file to export
			* ``character`` the character we are exporting
			* ``remove_namespace`` strip namespaces after exporting

		*Returns:*
			* ``True`` if successful

		*Examples:* ::

			>>> import vmobu.mobu_export
			>>> vmobu.mobu_export.mb_export.export()
		"""

		if filepath:
			self.filepath = filepath

		if not self.filepath:
			error_message = 'No filepath specified to export'
			self.logger.warning( error_message )
			return False, error_message

		# does this file exist
		new = True
		if os.path.exists( self.filepath ):
			new = False

		# actual export
		if character:
			pyfbsdk.FBApplication().SaveCharacterRigAndAnimation( str( self.filepath ).lower(), character, fbx_options )
		else:
			# Else, export as normal without character
			pyfbsdk.FBApplication().FileSave( str( self.filepath ).lower(), fbx_options )

		if new:
			# mark for add
			if not vmobu.mobu_perforce.mb_perforce.mark_for_add( self.filepath, quiet=True ):
				self.logger.warning( 'Could not add {0}'.format( self.filepath ) )

		# strip namespace
		if remove_namespace:
			vfbx = file_io.v_fbx.FBX( self.filepath )
			vfbx.remove_namespace( )
			vfbx.save_scene_file( )

		return True, 'Export Pass'


	def export_animation( self, anim_node, character, anim_name, anim_take, master_node = None, debug = False ):
		"""
		Exports animation as fbx, reading data from passed anim_node

		*Arguments:*
			* ``anim_node`` animation node, Note Object
			* ``character`` HIK character
			* ``anim_name`` name of the animation
			* ``anim_take`` name of the associated animation take

		*Keyword Arguments:*
			* ``debug`` whether or not to debug the export

		*Returns:*
			* ``amount/False`` progressWindow amount for multi-animation updating
		"""
		export_pbar = V_PROGRESS_BAR( percent= 0.0, subtitle='mobu_export.export_animation()', message='Validating that a rig is set in the anim_node.' )

		# make sure a rig is set in the anim_node
		rig_file = vmobu.core.get_property( anim_node, 'p_export_rig' )
		if not rig_file:
			error_message = "A valid rig has not been set!"
			self.logger.warning( error_message )
			return False, error_message

		# get the master
		export_pbar.update( percent = 0.02, message= 'Getting the Master node.')
		character_namespace = vmobu.core.get_namespace_from_obj( anim_node, as_string = True )
		if not master_node:
			master_node = vmobu.core.get_objects_from_wildcard( character_namespace + ":*Master", use_namespace=True, single_only=True )
		if not master_node:
			error_message = 'Could not locate the {0}:Master!'.format( character_namespace )
			self.logger.warning( error_message )
			return False, error_message

		# make sure the animation path is set
		export_pbar.update( percent = 0.05, message= 'Ensuring that the animation path is set.')
		anim_path = vmobu.core.get_property( anim_node, 'p_anim_file' )
		if not anim_path:
			error_message = 'A valid animation path was not found on the anim_node: {0}'.format( anim_node )
			self.logger.warning( error_message )
			return False, error_message

		# update and validate the anim_path
		valid_anim_path, anim_export_path, error_message = self.validate_anim_path( anim_node, master_node, anim_path )
		if not valid_anim_path:
			return False, error_message

		valid_rig_file, rig_filename, error_message = self.validate_rig_file( anim_node, master_node, rig_file )
		if not valid_rig_file:
			return False, error_message

		# make clean file_path
		export_pbar.update( percent = 0.1, message= 'Cleaning the file_path.')
		self.filepath = os.path.join( self.project_dir, anim_export_path )
		self.filename = anim_name + '.anim.fbx'
		self.filepath = os.path.join( self.filepath, self.filename )
		self.filepath = self.filepath.replace( '/', '\\' )

		# make sure we can export the anim file
		can_export_anim, error_message = self.can_export_file( self.filepath )
		if not can_export_anim:
			self.logger.warning( error_message )
			return False, error_message

		pyfbsdk.FBSystem( ).Scene.Evaluate( )

		# set the plot options
		export_pbar.update( percent = 0.15, message= 'Setting the plot options.')
		plot_options = pyfbsdk.FBPlotOptions( )
		plot_options.ConstantKeyReducerKeepOneKey = False
		plot_options.PlotAllTakes = False
		plot_options.PlotOnFrame = True

		# Set our plotting to skeleton from ctrl rig
		export_pbar.update( percent = 0.2, message= 'Plotting to skeleton from control_rig.')
		#vmobu.core.retarget_character( character, character_namespace )
		if character:
			skeleton = pyfbsdk.FBCharacterPlotWhere.kFBCharacterPlotOnSkeleton
			vmobu.core.plot_character(character, plot_where=skeleton, quiet=True,
			                         options=plot_options, force=True)

		p_template_file = master_node.PropertyList.Find('p_template_file')

		if p_template_file:
			# Update controller constraints ( animationcontroller, offsetNode, etc )
			export_pbar.update( percent = 0.3, message= 'Updating Animation_Controller Constraints.')
			if p_template_file.Data in vmobu.const.LEGACY_RIG_NAMES:
				self.update_controller_constraints( anim_node, character_namespace )

		# clear selected scene objects
		vmobu.core.unselect_all_components()

		# Starting with the Master node, select exportable objects
		export_pbar.update( percent = 0.35, message= 'Selecting exportable objects in the Master node hierarchy.')
		export_selection = [ master_node ]
		# add the direct children of the master node
		for child in master_node.Children:
			if isinstance( child, ( pyfbsdk.FBModelNull, pyfbsdk.FBModelSkeleton, pyfbsdk.FBModelRoot ) ):
				export_selection.append( child )
		export_selection = self.get_children_recursive( master_node, export_selection, has_prop = 'p_bone_name' )

		map( vmobu.core.select_obj, export_selection )

		# set the selected models
		lModels = pyfbsdk.FBModelList()
		pyfbsdk.FBGetSelectedModels( lModels )

		# 20150911KS:  I inserted this to get plotting on the animation_controller, which was lacking on the drone
		#              this might result in objects being plotted twice as there is overlap with
		#              <export.animation_exporter.Anim_Exporter#bake_skeleton_in_hierarchy>
		if not character:
			vmobu.core.plot_on_objects( export_selection )

		pyfbsdk.FBSystem( ).Scene.Evaluate( )

		# do main export
		# get the animation specific fbx export options
		export_pbar.update( percent = 0.4, message= 'Exporting FBX file.')
		fbx_options = self.get_fbx_options( take_name = anim_take, export_type = 'Animation' )
		self.filepath = str( self.filepath.lower( ) )
		start_frame = master_node.PropertyList.Find('p_export_framestart')
		end_frame   = master_node.PropertyList.Find('p_export_frameend')
		time_span   = vmobu.core.get_timespan_in_frames( )

		# 20150122 EC: If the master node has a parent, we don't send it through to the exporter with a character. The character exporter saves the entire hierarchy, where saving
		#              only the objs saves just the objects we have selected. The Master node MUST be the root node of the hierarchy for the cruncher to succeed.
		if master_node.Parent:
			character = None

		did_export, error_message = self.export( filepath = self.filepath, character = character, fbx_options = fbx_options, remove_namespace = False )
		if not did_export:
			return False, error_message

		# strip namespace
		export_pbar.update( percent = 0.6, message='Performing cleanup-operations on the FBX file.')
		vfbx = file_io.v_fbx.FBX( self.filepath )
		vfbx.remove_namespace( )
		# remove_objects not needed in exported animation files
		vfbx.remove_nodes_by_names( vmobu.const.ANIMATION_CONTROLLER_NAMES )
		vfbx.remove_nodes_by_keywords( vmobu.const.ANIMATION_CONTROLLER_KEYWORDS )
		vfbx.save_scene_file( )

		# add the file to resourcelib/perforce
		export_pbar.update( percent = 0.7, message='Adding file to resourcelib & perforce.')
		if not file_io.resource_lib.submit( self.filepath, 'fbx_anim' ):
			error_message = 'Failed to add the exported file to resourcelib\n{0}'.format( self.filepath )
			self.logger.warning( error_message )
			return False, error_message

		# get the rig version
		rig_version = vmobu.core.get_property( master_node, 'p_rig_version' )
		if not rig_version:
			rig_version = 0
			self.logger.warning( 'No rig version found on the Master: {0}'.format( master_node.Name ) )

		# get the animation length
		animation_length = self.get_animation_length( anim_node, anim_name )

		# set the resource attributes
		# this MUST BE DONE before crunch
		rig_name = os.path.basename( rig_filename )
		relative_scene_name = self.make_path_relative( vmobu.core.scene_name, self.project_dir )
		att_dict = { 'associated_character_rig': str( rig_name ), 'rig_version': rig_version,
	                'source_asset_file': relative_scene_name,
	                'animation_length': animation_length }
		if not file_io.resource_lib.set_attributes( self.filepath, att_dict ):
			error_message = 'Failed to set attributes on the resource!\n{0}'.format( self.filepath )
			self.logger.warning( error_message )
			return False, error_message

		# crunch the exported file
		export_pbar.update( percent = 0.9, message='Crunching the resource.')
		if not file_io.resource_lib.crunch( str( self.filepath ) ):
			error_message = 'Failed to crunch file: {0}\nCheck the output window for details!'.format( self.filepath )
			self.logger.warning( error_message )
			return False, error_message

		# move crunched animation files to the proper changelist
		anim_pc_filepath = self.filepath.replace( 'anim.fbx', 'anim_pc' )
		anim_ps4_filepath = self.filepath.replace( 'anim.fbx', 'anim_ps4' )
		anim_xbox3_filepath = self.filepath.replace( 'anim.fbx', 'anim_xbox3' )
		anim_files = [ self.filepath, anim_pc_filepath, anim_ps4_filepath, anim_xbox3_filepath ]
		error_message = ''
		failed_move = False
		export_pbar.update( percent = 0.95, message='Moving files to Mobu Changelist.')
		for anim_file in anim_files:
			if not vmobu.mobu_perforce.mb_perforce.move_to_changelist( anim_file, quiet = True ):
				error_message += 'Could not move {0} to Mobu Changelist\n'.format( anim_file )
		if failed_move:
			self.logger.warning( error_message )
			return False, error_message

		# clean up the backup folder
		backup_folder = os.path.join( os.path.dirname( self.filepath ), anim_name + '.anim.bck' )
		if os.path.exists( backup_folder ):
			self.remove_backup_folder( backup_folder )

		export_pbar.update( percent = 1.0, message='Done!')
		return True, 'Animation Exported!\n'


	def animation_copy_paste( self, obj = None, operation_type = 'export', file_name = 'temp' ):
		"""
		Exports and imports animations to and from a temporary file onto either a rig or FBModel.

		*Arguments:*
			* ``operation_type`` 'export' or 'import' depending on operation
			* ``obj`` optional inline object specification.
			* ``file_name`` optional file_name to save or load from. Default is 'temp'

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``True\Confirmation``
			* ``False\Error Message``

		*Examples:* ::

			>>> import vmobu.mobu_export
			>>> vmobu.mobu_export.mb_fbx_export.animation_copy_paste( )

			>>> vmobu.mobu_export.mb_fbx_export.animation_copy_paste( operation_type = 'import' )

		*TODO:*
			* Support multiple model selection
			* Support channel selection (Only rotate and scale, only translate etc.)
		"""
		#File directory script saves files to.
		temp_path = 'C:\\Temp\\'

		#If object is given in function call, use it as basis to grab parent_component.
		if obj:
			parent_component = vmobu.core.get_top_node_of_hierarchy( obj )

		else:

			obj_list = vmobu.core.get_selected( class_group_name = 'Model' )
			if not obj_list:
				self.logger.warning( "No object selected! Be sure you have a FBModel, FBModelMarker or FBSkeleton Selected" )
				return False

			#Get current selected object and set it to be animated, creating animation_nodes
			obj = obj_list[ 0 ]
			obj.Translation.SetAnimated(True)
			obj.Rotation.SetAnimated(True)
			obj.Scaling.SetAnimated(True)
			#Determine the top node of the hierarchy

			parent_component = vmobu.core.get_top_node_of_hierarchy( obj )

		#Unselect all components and select parent_component
		vmobu.core.unselect_all_components( )


		animation_nodes = [ ]
		property_list = ['T', 'R', 'S']

		#Import ( Paste ) Operation
		if operation_type.lower( ) == 'import':
			#Where the FBX options and actual import occur.
			if obj.ClassName( ) in ('FBModelMarker', 'FBSkeleton'):
				parent_component.Selected = True
				if not os.path.exists( '{0}{1}.fbx'.format( temp_path, file_name ) ):
					self.logger.warning('No FBX animation is currently saved')
					return False

				fbx_options = vmobu.mobu_export.mb_fbx_export.get_fbx_options()
				pyfbsdk.FBApplication( ).FileImport( '{0}{1}.fbx'.format( temp_path, file_name ) )

			#Import of animation data for FBModel
			elif obj.ClassName( ) in ( 'FBModel', 'FBModelCube' ):

				#Check to see if file exists, if nothing exists print a warning and return.
				if not os.path.exists( '{0}{1}.json'.format( temp_path, file_name ) ):
					self.logger.warning( 'No file -{0}.json- exists in directory: {1}'.format( file_name, temp_path ) )
					return False

				#Open the temporary file and read data.
				#Convert string to dict
				with open( '{0}{1}.json'.format( temp_path, file_name ), 'r' ) as open_file:
					object_data_dict = json.loads( open_file.read( ) )
				open_file.close( )

				#For each property, get animation nodes associated with its x y & z axis
				for prop in property_list:
					animation_nodes.append( vmobu.core.get_animnode_transform( obj, axis = 'x', transform = prop ) )
					animation_nodes.append( vmobu.core.get_animnode_transform( obj, axis = 'y', transform = prop ) )
					animation_nodes.append( vmobu.core.get_animnode_transform( obj, axis = 'z', transform = prop ) )

				#For each animation node in the list, if it exists, deserialize keyframe information into it.
				for index in range( 0, len( animation_nodes ) ):
					if animation_nodes[ index ] is not None:
						vmobu.core.deserialize_fcurve(animation_nodes[index], object_data_dict[str(index)] )

			#If object selected is neither of type FBModel or FBModelMarker etc. return.
			else:
				self.logger.warning('Type of {0} not recognized! ( IMPORT ) \n'.format( parent_component.ClassName( ) ) )
				return False

			vmobu.core.unselect_all_components()
			return True, 'Animation Imported from Temporary File -{0}-!\n'.format(file_name)

		#Export ( Copy ) Operation
		elif operation_type.lower( ) == 'export':
			#Where the FBX options and actual export occurs.
			if parent_component.ClassName( ) == 'FBModelMarker':
				parent_component.Selected = True
				fbx_options = self.get_fbx_options( )
				pyfbsdk.FBApplication( ).FileExport( '{0}{1}.fbx'.format( temp_path, file_name ) )

			#Export of animation data for FBModel
			elif obj.ClassName( ) in ( 'FBModel', 'FBModelCube' ):
				object_data_dict = { }
				#Loop - each property [T, R, S] get the animation nodes [x, y, z] get the actual animation node
				for prop in property_list:
					animation_nodes.append( vmobu.core.get_animnode_transform( obj, axis = 'x', transform = prop ) )
					animation_nodes.append( vmobu.core.get_animnode_transform( obj, axis = 'y', transform = prop ) )
					animation_nodes.append( vmobu.core.get_animnode_transform( obj, axis = 'z', transform = prop ) )

				#For each animation node, serialize information and return into dictionary which is saved.
				for index in range( 0, len( animation_nodes ) ):
					if animation_nodes[ index ] is not None:
						object_data_dict[ index ] = vmobu.core.serialize_fcurve( animation_nodes[ index ] )

				#Create file and write data from dictionary to file.
				with open( '{0}{1}.json'.format( temp_path, file_name ), 'w' ) as open_file:
					open_file.write( json.dumps( object_data_dict, indent = 4 ) )
				open_file.close( )

			else:
				return False, 'Type of {0} not recognized! ( EXPORT ) \n'.format( parent_component.ClassName( ) )

			vmobu.core.unselect_all_components()
			return True, 'Animation Exported to Temporary File -{0}-!\n'.format(file_name)

		return False, 'Operation Not Found'


mb_export = Mobu_Export()
mb_fbx_export = Mobu_FBX_Export()