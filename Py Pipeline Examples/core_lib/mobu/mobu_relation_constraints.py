"""
Collection of methods for dealing with Relation Constraints in MotionBuilder

* Examples: *
	>>> vmobu.mobu_relation_constraints.create_relation_constraint( 'relation_constraint_name' )
	>>>
	>>> # Python code for motionbuilder to create that relation constraint is returned.
"""

# Motionbuilder lib
import pyfbsdk

#vmobu
import vmobu
import vmobu.mobu_constraints


class VMoBu_Relation_Constraints( vmobu.VMoBu_Core ):

	def __init__( self ):
		super( VMoBu_Relation_Constraints, self ).__init__( )
		self.logger = vmobu.core.logger

	def is_sender_component( self, box, constraint ):
		"""
		Determines whether or not passed box is a sender of the specified constraint

		*Arguments:*
		        * ``box`` Node to check
		        * ``constraint`` Constraint to check in

		*Keyword Arguments:*
		        * ``none``

		*Returns:*
		        * True/False
		"""

		function_boxes = [ fbbox for fbbox in constraint.Boxes ]

		if type( box ) == pyfbsdk.FBBox:
			return False

		# Get the animation in node for the current component
		animation_out_node = self.get_function_box_animation_nodes( box, direction = 'out' )

		# For each child node in the parent animation_node
		for node in animation_out_node.Nodes:

			#Get the source for the animation nodes
			if node.GetDstCount( ) > 0:
				output_function_box = node.GetDst(0).GetOwner()

				# If the owner of the node is a function box
				if type( output_function_box ) == pyfbsdk.FBBox:

					# If the output box is in the list of constraint function boxes
					if output_function_box in function_boxes:
						return True

		# If no function boxes are found in the constraint or destinations
		self.logger.info( 'No function boxes found on list of outputs for {0}'.format( box.Name ) )
		return False

	def is_receiver_component( self, box, constraint ):
		"""
		Determines whether or not passed box is a receiver of the specified constraint

		*Arguments:*
		        * ``box`` Node to check
		        * ``constraint`` Constraint to check in

		*Keyword Arguments:*
		        * ``none``

		*Returns:*
		        * True/False
		"""
		function_boxes = [ fbbox for fbbox in constraint.Boxes ]

		if type( box ) == pyfbsdk.FBBox:
			return False

		# Get the animation in node for the current component
		animation_in_node = self.get_function_box_animation_nodes( box, direction = 'in' )

		# For each child node in the parent animation_node
		for node in animation_in_node.Nodes:

			#Get the source for the animation nodes
			if node.GetSrcCount( ) > 0:
				input_function_box = node.GetSrc(0).GetOwner()

				# if input type is FBBox
				if type( input_function_box ) == pyfbsdk.FBBox:

					# if input node type is in the list of function_boxes
					if input_function_box in function_boxes:
						return True

		# If no function boxes are found in the inputs, must not be a receiver
		self.logger.info( 'No function boxes found on list of inputs for {0}'.format( box.Name ) )
		return False

	def get_function_boxes( self, constraint = None, get_reference_boxes = False ):
		"""
		Gets all function boxes involved in the specified constraint.
		If no constraint is specified in the call, assumes it is involved with python relation constraint source creation

		*Arguments:*
		        * ``none``

		*Keyword Arguments:*
		        * ``constraint`` Constraint to return all function boxes from
		        * ``get_reference_boxes`` If True, return only boxes not of type pyfbsdk.FBBox

		*Returns:*
		        * `` list of <pyfbsdk.FBBox> in given constraint
		"""
		list_of_boxes = []

		if not constraint:
			constraint = self.constraint

		# For every box in the constraint:
		for box in constraint.Boxes:

			# If the box type is an FBBox, add to the function box list:
			if type( box ) == pyfbsdk.FBBox:

				if not get_reference_boxes:
					list_of_boxes.append( box )

			# If not, check get_reference_boxes flag
			else:

				if get_reference_boxes:
					list_of_boxes.append( box )

		return list_of_boxes


	def query_function_boxes( self, function_boxes = [], constraint = None):
		"""
		Queries function boxes in the given constraints for general information for later use

		*Arguments:*
		        * ``none``

		*Keyword Arguments:*
		        * ``function_boxes`` <list> of <pyfbsdk.FBBox> object(s) to query information from
		        * ``return_type`` <str> 'in', 'out', 'position' will return a single FBBox's input or output animation nodes, or position

		*Returns:*
		        * ``box_dict`` <dict> object containing the following information:
							function boxes name: {
		                                                        'object': <pyfbsdk.FBBox>,
		                                                        'variable_name': Name of the box, #FOR PYTHON USE
		                                                        'in': input animation nodes,
		                                                        'out': output animation nodes,
		                                                        'position': current box position (X, Y)
									}
		        * ``input_nodes`` if return_type == 'in'
		        * ``output_nodes`` if return_type == 'out'
		        * ``position`` if return_type == 'position'
		"""
		if not constraint:
			self.logger.info('No constraint was passed for {0}. Finding one for each function box. Pass one in for faster solving'.format( function_boxes ) )
			pass

		box_dict = {}
		for box in function_boxes:
			if not constraint:
				constraint = self.get_constraint_from_function_box( box )

			# Get input and output nodes
			input_nodes = self.get_child_nodes_from_function_box(box, 'in')
			output_nodes = self.get_child_nodes_from_function_box(box, 'out')

			# Get the function boxes position in the constraint
			box_position = constraint.GetBoxPosition( box )

			# If only one object is passed in
			if len( function_boxes ) == 1:
				# Consolidate into a dictionary
				box_dict = { 'object': box,
					                'variable_name': mobu_rel_python.make_variable_names( box.Name, box = True ),
					                'in': input_nodes,
					                'out': output_nodes,
					                'position': box_position[1:] }
				return box_dict

			# Consolidate into a dictionary
			box_dict[ box.Name ] = { 'object': box,
				        'variable_name': mobu_rel_python.make_variable_names( box.Name, box = True ),
				        'in': input_nodes,
				        'out': output_nodes,
				        'position': box_position[1:] }

		return box_dict

	def find_constraint( self,  constraint_name ):
		"""
		Searches through the scene's list of constraints to find the constraint associated with the name supplied.

		*Arguments:*
		        * ``none``

		*Keyword Arguments:*
		        * ``none``

		*Returns:*
		        * ``constraint`` <FBConstraintRelation>
		        * ``False`` If no constraint in the scene matches the name given
		"""
		scene = pyfbsdk.FBSystem( ).Scene
		constraints = scene.Constraints

		for constraint in constraints:
			if constraint.LongName == constraint_name:
				return constraint

		self.logger.warning( 'No constraint found that matches name {0}'.format( constraint_name ) )
		return False

	def get_function_box_animation_nodes( self, function_box, direction = 'both' ):
		"""
		Queries the given box for its input or output (or both) parent animation nodes.
		Wrapper for <pyfbsdk.FBBox>.AnimationNodeInGet() & <pyfbsdk.FBBox>.AnimationNodeOutGet()

		*Arguments:*
		        * ``function_box`` Function box to query for animation nodes

		*Keyword Arguments:*
		        * ``direction`` Possible values - 'both', 'in', 'out'

		*Returns:*
		        * ``animation_node`` <FBAnimationNode> Depending on the direction flag.
				* if direction flag is 'in' or 'out', single node is returned.
				* if direction flag is 'both', list [ input_node, output_node ] is returned
		        * ``False`` If error
		"""
		# If box value is not of type pyfbsdk.FBBox, return False

		animation_nodes = [ function_box.AnimationNodeInGet( ), function_box.AnimationNodeOutGet( ) ]

		# If no animation nodes found
		if not animation_nodes:
			self.logger.warning('No animation nodes attached to specified box in vmobu.VMobu_Relation_Constraints.get_box_animation_nodes')
			return False

		# Return aniamtion node associated with direction value, or both
		if direction.lower( ) == 'in':
			return animation_nodes[0]

		if direction.lower( ) == 'out':
			return animation_nodes[1]

		if direction.lower( ) == 'both':
			return animation_nodes

		# If no valid flags were inserted, return False
		self.logger.warning( 'No valid flags were passed into the method get_box_animation_nodes' )
		return False

	def get_function_box_category( self, box ):
		"""
		Determines the category of the passed box

		*Arguments:*
		        * ``box`` Node to check

		*Keyword Arguments:*
		        * ``none``

		*Returns:*
		        * ``category`` Category of the box passed in
		"""
		input_list = self.get_child_nodes_from_function_box( box, direction = 'in' )

		box_name = box.Name
		split_box_name = box_name.split( ' ' )

		# if the last split is an enumeration
		if split_box_name[-1].isdigit():
			# Redeclare the box name
			box_name = ''
			# reconstruct the box name
			for item in split_box_name:
				if item == split_box_name[ -1 ].lower( ):
					continue
				box_name = box_name + item + ' '
			box_name = box_name.strip()

		for category in vmobu.mobu_constraints.RELATION_FUNCTION_BOXES:

			# For every node type in the dictionary category
			for node in vmobu.mobu_constraints.RELATION_FUNCTION_BOXES[ category ]:

				# Get the inputs of the current node in the category
				dictionary_inputs = vmobu.mobu_constraints.RELATION_FUNCTION_BOXES[ category ][ node ][ 'Inputs' ]
				box_input_list = [ input_tuple[ 1 ] for input_tuple in input_list ]

				node_name = node.lower()

				# Compare the name of the existing node to the name of the dictionary node
				if node_name == box_name.lower():

					# Confirm the list of inputs match, return category
					if self.compare_lists( box_input_list, dictionary_inputs ):

						return category, box_name

		return False

	def get_constraint_from_function_box( self, function_box ):
		"""
		Queries all constraints in the scene and figures out which constraint the given function box belongs to.

		*Arguments:*
		        * ``box`` Function box to check constraints for

		*Keyword Arguments:*
		        * ``none``

		*Returns:*
		        * ``constraint`` Constraint that the function box belongs to
		        * ``False`` if no constraint is found.
		"""
		# Check to be sure function_box value is a pyfbsdk.FBBox.
		if type( function_box ) != pyfbsdk.FBBox:
			return False

		# Get the constraints in the scene
		scene = pyfbsdk.FBSystem( ).Scene
		constraints = scene.Constraints

		# For each constraint in the scene
		for constraint in constraints:
			# Is the constraint a relation constraint
			if type(constraint) == pyfbsdk.FBConstraintRelation:
				# Is the function box in the constraint
				if function_box in constraint.Boxes:
					return constraint

		# Function box is not found in any constraint
		self.logger.error( 'Function box [ {0} ] not associated with any constraint.'.format( function_box.Name ) )
		return False

	def replace_node_as_source( self, constraint, new_source, old_source ):
		"""
		Queries constraints list of references and removes the old source, adds in new source.

		*Arguments:*
			* ``constraint`` constraint to change the source of
			* ``new_source`` box for new source
			* ``old_source`` box to replace

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``True`` if successful
			* ``False`` if error occurs

		*TODO*:
			* Before old source is deleted, get its connections and apply them to the new source
		"""
		if type( constraint ) != pyfbsdk.FBConstraintRelation:
			self.logger.warning( 'set_new_node_as_source: constraint must be of type pyfbsdk.FBConstraintRelation' )
			return False

		found = False

		# Get the list of receivers
		source_group = [ box for box in constraint.Boxes if type( box ) != pyfbsdk.FBFunctionBox ]

		# For every function box in the receiver list, check it against the old_receiver
		for box in source_group:
			if box == old_source:
				# When the old_source is found, delete it and exit the loop
				box.FBDelete()
				found = True
				break

		# If the box is not found, return False
		if not found:
			self.logger.warning('No object {0} found in {1}'.format( old_source.Name, constraint.Name ) )
			return False

		# Set the new source as a source
		box.SetAsSource( new_source )

		return True

	def replace_node_as_receiver( self, constraint, new_receiver, old_receiver ):
		"""
		Queries constraints list of constrained objects, removes the object and adds in the new constrained

		*Arguments:*
			* ``constraint`` constraint to change the source of
			* ``new_source`` box for new source
			* ``old_source`` box to replace

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``True`` if successful
			* ``False`` if error occurs

		*TODO:*
			* Before old receiver is deleted, get its connections and apply them to the new receiver
		"""
		if type( constraint ) != pyfbsdk.FBConstraintRelation:
			self.logger.warning( 'set_new_node_as_reciever: constraint must be of type pyfbsdk.FBConstraintRelation' )
			return False

		found = False

		# Get the list of receivers
		reciever_group = [ box for box in constraint.Boxes if type( box ) != pyfbsdk.FBFunctionBox ]

		# For every function box in the receiver list, check it against the old_receiver
		for box in reciever_group:
			if box == old_receiver:
				# When the old_receiver is found, delete it and exit the loop
				box.FBDelete()
				found = True
				break

		# If the box is not found, return False
		if not found:
			self.logger.warning('No object {0} found in {1}'.format( old_receiver.Name, constraint.Name ) )
			return False

		# Constrain the new reciever
		box.ConstrainObject( new_receiver )

		return True

	def append_source_to_constraint( self, constraint, new_source ):
		"""
		Compares the contents of two given lists. Lists must have the exact same contents to return True.

		*Arguments:*
			* ``constraint`` Constraint to add source to
			* ``new_source`` Source to add to the constraint

		*Keyword Arguments:*
			* ``none``
		"""
		if type( constraint ) != pyfbsdk.FBConstraintRelation:
			return False

		if type( new_source ) == pyfbsdk.FBBox:
			return False

		constraint.SetAsSource( new_source )
		return True

	def append_receiver_to_constraint( self, constraint, new_receiver ):
		"""
		Compares the contents of two given lists. Lists must have the exact same contents to return True.

		*Arguments:*
			* ``constraint`` Constraint to add source to
			* ``new_receiver`` Receiver to add to the constraint

		*Keyword Arguments:*
			* ``none``
		"""
		if type( constraint ) != pyfbsdk.FBConstraintRelation:
			return False

		if type( new_receiver ) == pyfbsdk.FBBox:
			return False

		constraint.ConstrainObject( new_receiver )
		return True

	def get_child_nodes_from_function_box( self, function_box, direction = 'in' ):
		"""
		Compares the contents of two given lists. Lists must have the exact same contents to return True.

		*Arguments:*
			* ``constraint`` Constraint to add source to
			* ``new_receiver`` Receiver to add to the constraint

		*Keyword Arguments:*
			* ``none``
		"""
		anim_nodes = self.get_function_box_animation_nodes( function_box , direction = direction )
		nodes = [ (node, node.Name) for node in anim_nodes.Nodes ]
		return nodes

	def get_placeholder_from_model( self, fb_object, constraint, sender_bool = True ):
		"""
		Given a model object from the scene, capture it's placeholder in a given constraint

		*Arguments:*
			* ``fb_object`` fb_object to search the constraint for
			* ``constraint`` constraint to search in

		*Keyword Arguments:*
			* ``sender_bool`` check for sender placeholder, else checks for receiver
		"""
		boxes = self.get_function_boxes( constraint, get_reference_boxes = True )
		for box in boxes:
			if sender_bool:
				if self.is_sender_component( box, constraint ):
					if box.Name == fb_object.Name:
						return box

			else:
				if self.is_receiver_component( box, constraint ):
					if box.Name == fb_object.Name:
						return box

	def get_function_box_from_name( self, name, constraint, similar = False ):
		"""
		Given a model object from the scene, capture it's placeholder in a given constraint

		*Arguments:*
			* ``name`` <str> of the name of the function_box to get
			* ``constraint`` constraint to search in

		*Keyword Arguments:*
			* ``similar`` return a list of function boxes with a similar name, not exact

		*Return:*
			* if not similar - box with the exact name of the node
			* if similar - all function boxes within the constraint with a name similar to the name value passed in
		"""

		# Get all boxes in the given constraint
		box_list = self.get_function_boxes(constraint)
		similar_list = []

		for box in box_list:
			# If not similar flag:
			if not similar:

				# if the box name is the name given, return the box
				if box.Name == name:
					return box

			# If the name value is in the name of the box, append to the box
			if name in box.Name:
				similar_list.append( box )

		# If similar list, return
		if similar_list:
			return similar_list
		# No box found
		self.logger.warning('No function box found matching name')
		return False

	def compare_lists( self, list_one, list_two ):
		"""
		Compares the contents of two given lists. Lists must have the exact same contents to return True.

		** PROBABLY NEEDS TO BE PUT IN ANOTHER LIB FOR EASY ACCESS **

		*Arguments:*
			* ``list_one`` First list to compare
			* ``list_two`` List to compare against list_one

		*Keyword Arguments:*
			* ``none``

		*Examples:* ::
			>>> old_list = [ 'hello', 'there', 'traveler' ]
			>>> new_list = [ 'there', 'traveler' 'hello' ]
			>>> self.compare_lists( old_list, new_list ) -> True
		"""

		for i in range( 0, len( list_one ) ):
			if list_one[i] in list_two:
				pass
			else:
				return False
		return True




class Relation_Python_Utility( VMoBu_Relation_Constraints ):
	"""
	Class used to query and reproduce Relation Constraints in motion builder by returning Python source code.

	*Arguments:*
	        * ``none``

	*Keyword Arguments:*
	        * ``print_flag`` <bool> Whether or not to return results to the script editor.

	*Examples:* ::
	        >>> relation_utility = Relation_Python_Utility( 'constraint' )
	        >>> relation_utility.run( )

	*TODO:* ::
	        * Get source and destinations for function boxes
	        * Needs a lot more error checking.
	"""

	def __init__( self ):
		super( Relation_Python_Utility, self ).__init__( )

	def run( self, constraint_name, test = False, print_flag = False, file_path = None ):
		"""
		Runs the actual logic of the relation constraint utility

		*Arguments:*
		        * ``constraint_name`` <str> Name of relation constraint to query

		*Keyword Arguments:*
		        * ``print_flag`` <bool> whether or not to print output to the mobu python editor
		        * ``file_path`` <str> where to write resulting python code. Default is system temp folder

		*Examples:* ::
		        >>> relation_utility = Relation_Utility( )
		        >>> relation_utility.run_python_translator( 'constraint' )
		"""
		self.result_list = [ ]
		self.result = ''
		self.sender_receivers = [ ]
		self.print_flag = print_flag

		self.box_dict = { }
		# Box name (raw name): {
			# object: <FBBox object>
			# in: <list> of input connections available ( animation node, animation node name )
			# out: <list> of output connections available ( animation node, animation node name )
			# position: <tuple> containing function box position in node graph ( X Position, Y Position )
			# var_name: variable name in python associated with function box                 *** FOR PYTHON USE
			# in_variable: <list> of ( variable name, animation node, animation node name )  *** FOR PYTHON USE
			# out_variable: <list> of ( variable name, animation node, animation node name ) *** FOR PYTHON USE
			# }


		self.constraint = self.find_constraint( constraint_name )
		if not self.constraint:
			return False

		self.create_relation( )

		# Get function boxes
		self.boxes = self.get_function_boxes( self.constraint )
		self.sender_receivers = self.get_function_boxes( self.constraint, get_reference_boxes = True )

		# Get information for function boxes and senders and receivers
		self.function_box_dict = self.query_function_boxes( self.boxes )
		self.sender_receiver_dict = self.query_function_boxes( self.sender_receivers, constraint = self.constraint )

		# Generate code to create function_boxes and their inputs and outputs
		self.create_function_boxes( )
		self.result_list.append('\n \nvmobu.core.evaluate( ) \n')
		self.create_inputs_and_outputs( self.function_box_dict )

		# Generate code to set function box positions
		self.result_list.append('\n \nvmobu.core.evaluate( ) \n')
		self.set_function_box_positions( self.function_box_dict )

		self.result_list.append('\n \nvmobu.core.evaluate( ) \n')
		self.result_list.append( '\n \n# Connection of nodes \n' )

		for box in self.function_box_dict:
			self.pair_connections( self.function_box_dict[ box ][ 'out_variable' ] )

		self.result_list.append('\n \nvmobu.core.evaluate( ) \n')

		self.consolidate_results( )

		if self.print_flag:
			print( '\n \n# ------------ PYTHON ------------- # \n \n' )
			print( self.result )

		return self.result

	def create_relation( self ):
		"""
		Gets information required to make code for creating a relation constraint.

		*Arguments:*
		        * ``none``
		"""
		constraint_creation = 'constraint = vmobu.core.create_constraint( "Relation", long_name = "{0}" )\n'.format( self.constraint.Name )
		self.result_list.append( constraint_creation )

	def create_function_boxes( self ):
		"""
		Creates python code for creating relation constraint function boxes.
		Queries mobu_constraint.RELATION_FUNCTION_BOXES for categorical information related to FBBox creation

		*Arguments:*
		        * ``none``

		*Keyword Arguments:*
		        * ``none``
		"""
		# Check box type and append box creation to result list
		self.result_list.append('\n \n# Create function boxes\n')

		# For every key in the box_dictionary (function box name )
		for box in self.function_box_dict.keys():
			category, box_name = self.get_function_box_category( self.function_box_dict [box]['object'] )
			box_creation = '{0} = constraint.CreateFunctionBox( "{1}", "{2}" )\n'.format( self.function_box_dict[ box ][ 'variable_name' ], category, box_name )
			self.result_list.append( box_creation )

	def create_inputs_and_outputs( self, box_dict ):
		"""
		Creates python code necessary for instantiating the input and output variables for relation constraint creation

		*Arguments:*
		        * ``box_dict`` dictionary full of box information returned from the query_function_box method

		*Keyword Arguments:*
		        * ``none``
		"""
		direction_tuple = ( 'in', 'out' )
		for direction_key in direction_tuple:
			self.result_list.append( '\n \n# Create {0}put connection variables\n'.format( direction_key ) )
			for box in box_dict:
				box_dict[ box ][ '{0}_variable'.format( direction_key ) ] = [ ]
				for connection in box_dict[ box ][ direction_key ]:
					connection_var = self.make_variable_names( connection[ 1 ] )
					# Appends python code for connection plug instantiation to result list
					self.result_list.append( '{0}_{3}_{2} = vmobu.core.get_node_connection( {0}, "{1}", direction = "{2}")\n'.format( box_dict[ box ]['variable_name'], connection[ 1 ], direction_key, connection_var ).lower( ) )

					# Creates a new key for in_variables and out_variables in the box_dictionary associated with the variable name, the connection name and object
					box_dict[ box ][ '{0}_variable'.format( direction_key ) ].append( ( '{0}_{1}_{2}'.format( box_dict[ box ]['variable_name'], connection_var, direction_key ).lower(), connection[ 0 ], connection[ 1 ] ) )

	def pair_connections( self, output_list ):
		connections = []
		input_con = ''
		output_con = ''

		# For each box in the output list
		for box in output_list:
			# Get the box count and iterate through
			for i in range( 0, box[1].GetDstCount( ) ):
				# Get the input box
				in_box_name = box[1].GetDst(i).GetOwner().Name
				if not in_box_name:
					# If nothing connected, keep on moving
					continue
				# Get the name of the in_box
				in_box_dest_name = self.make_variable_names( str( in_box_name ), box=True) + "_" + box[1].GetDst(i).UserName.lower() + "_in"

				# Get the output boxes name
				out_box_name = box[0]

				# Print those connections
				self.print_connection_nodes( out_box_name, in_box_dest_name )

	def print_connection_nodes( self, output_var = None, input_var = None, value = None ):
		# If a value is passed in for the input, append the WriteData statement.
		if value:
			self.result_list.append( '{0}.WriteData( [ {1} ] )\n'.format( input_var, value ) )
			return True

		# Redeclare variable names once parsed for bad characters.
		input_var  = self.make_variable_names( input_var )
		output_var = self.make_variable_names( output_var )

		# Append the Connection statement to the result list.
		self.result_list.append('pyfbsdk.FBConnect( {0}, {1} )\n'.format( output_var, input_var ) )

	def set_function_box_positions( self, box_dict ):
		"""
		Creates python code for setting the positions of created relation constraint function boxes.

		*Arguments:*
		        * ``none``

		*Keyword Arguments:*
		        * ``none``
		"""
		self.result_list.append( '\n \n# Set Function box positions\n' )
		for box in box_dict:
			self.result_list.append( 'constraint.SetBoxPosition( {0}, {1}, {2} )\n'.format( box_dict[ box ][ 'variable_name' ] , box_dict[ box ][ 'position' ][ 0 ], box_dict[ box ][ 'position' ][ 1 ] ) )

	def consolidate_results( self ):
		"""
		Consolidates all lines of code into one string for printing.

		*Arguments:*
		        * ``none``

		*Keyword Arguments:*
		        * ``none``
		"""
		for line in self.result_list:
			self.result = self.result + line

	def make_variable_names( self, var_name, box = False ):
		"""
		Given the name of the object, converts it into a name usable as a variable in the python code

		*Arguments:*
		        * ``var_name`` string of the variable name

		*Keyword Arguments:*
		        * ``box`` bool, whether or not to add '_box' to the end of the var

		*Returns:*
		        * ``lower_name`` lowercase and converted name of the function box, usable as a python variable
		        * ``False`` if a string is not supplied
		"""

		if not var_name or not isinstance( var_name, str ):
			return False

		bad_characters = [ ( ' ', '_' ),
		                   ( '_(a_x_b)_', '' ),
		                   ( '_(a_/_b)_', '' ),
		                   ( '_(b/a)', '' ),
		                   ( '_(a/b)', '' ),
		                   ( '(', '' ),
		                   ( '.', '' ),
		                   ( ')', '' ),
		                   ( '%', 'percent' ),
		                   ('!=', ''),
		                   ( '!', ''),
		                   (',', ''),
		                   ( '-', 'min' ),
		                   ( '+', 'plus' ),
		                   ( '>', 'greater' ),
		                   ( '<', 'less' ),
		                   ( '=', 'equal' ),
		                   ( '/', '_div_' ),
		                   ( '__', '_' ) ]

		lower_name = var_name.lower( )
		for char_tuple in bad_characters:
			lower_name = lower_name.replace( char_tuple[ 0 ], char_tuple[ 1 ] )

		if box:
			return '{0}_box'.format( lower_name )

		return lower_name

mobu_rel_constraints = VMoBu_Relation_Constraints( )
mobu_rel_python = Relation_Python_Utility( )

def create_relation_constraint( constraint_name = False, file_path = None ):
	"""
	Given the name of the constraint, returns python code to create the constraint

	*Arguments:*
			  * ``none``

	*Keyword Arguments:*
			  * ``constraint_name`` name of the constraint to query
			  * ``file_path`` path directory to spit out the python code. Not required, will print it out anyway.

	*Returns:*
			  * True/False
	"""
	if not constraint_name:
		return False

	return mobu_rel_python.run( constraint_name, print_flag= True, file_path = file_path )

