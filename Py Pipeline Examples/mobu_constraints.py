"""

Creates all of the base constraints for the characters upon asset_add.
"""

# Motionbuilder lib
import pyfbsdk
# from pyfbsdk import *

#vmobu
import vmobu
import vmobu.decorators
import vmobu.mobu_relation_constraints

ALT_SIDES = { 'Left':'Lft', 'Right':'Rgt' }
TARGET_INDICES = { 'a': 0, 'b': 1, 'c': 2 } # This dictionary is used later when we associate targets with bend constraints.

# { Category:
	# { Box Type:
		# { Inputs: [ List of Inputs ],
		#   Outputs: [ List of Outputs ],
		#   Description: ' Description '} } }
RELATION_FUNCTION_BOXES =  {
        'Boolean': {
                'AND':                   { 'Inputs': [ 'a', 'b' ],     'Outputs': [ 'Result' ], 'Description': '' },
                'Flip Flop':             { 'Inputs': [ 'B', 'Clear' ], 'Outputs': [ 'Result' ], 'Description': '' },
                'Memory (B1 when REC)':  { 'Inputs': [ 'B 1', 'REC' ], 'Outputs': [ 'Result' ], 'Description': '' },
                'Memory (last trigger)': { 'Inputs': [ 'B 1', 'B 2', 'B 3', 'B 4', 'B 5', 'B 6', 'B 7', 'B 8', 'B10', 'Clear'], 'Outputs': [ 'Out 1', 'Out 2', 'Out 3', 'Out 4 ', 'Out 5', 'Out 6', 'Out 7', 'Out 8', 'Out 9', 'Out10', 'Result'], 'Description': '' },
                'NAND':                  { 'Inputs': [ 'a', 'b' ],     'Outputs': [ 'Result' ], 'Description': '' },
                'NOR':                   { 'Inputs': [ 'a', 'b' ],     'Outputs': [ 'Result' ], 'Description': '' },
                'NOT':                   { 'Inputs': [ 'a' ],          'Outputs': [ 'Result' ], 'Description': '' },
                'OR':                    { 'Inputs': [ 'a', 'b' ],     'Outputs': [ 'Result' ], 'Description': '' },
                'XNOR':                  { 'Inputs': [ 'a', 'b' ],     'Outputs': [ 'Result' ], 'Description': '' },
                'XOR':                   { 'Inputs': [ 'a', 'b' ],     'Outputs': [ 'Result' ], 'Description': '' }
                },
        'Converters': {
                'Deg To Rad':        { 'Inputs': [ 'a' ],                'Outputs': [ 'Result' ], 'Description': '' },
                'HSB To RGB':        { 'Inputs': [ 'HSB' ],              'Outputs': [ 'RGB' ], 'Description': '' },
                'Number To RGBA':    { 'Inputs': [ 'A', 'B', 'G', 'R' ], 'Outputs': [ 'RGBA' ], 'Description': '' },
                'Number To Vector':  { 'Inputs': [ 'X', 'Y', 'Z' ],      'Outputs': [ 'Result' ], 'Description': '' },
                'Number To Vector2': { 'Inputs': [ 'X', 'Y' ],           'Outputs': [ 'Result' ], 'Description': '' },
                'Rad To Deg':        { 'Inputs': [ 'a' ],                'Outputs': [ 'Result' ], 'Description': '' },
                'RGB To HSB':        { 'Inputs': [ 'RGB' ],              'Outputs': [ 'HSB' ], 'Description': '' },
                'RGB To RGBA':       { 'Inputs': [ 'Alpha', 'RGB' ],     'Outputs': [ 'RGBA' ], 'Description': '' },
                'RGBA To Number':    { 'Inputs': [ 'RGBA' ],             'Outputs': [ 'A', 'B', 'G', 'R' ], 'Description': '' },
                'RGBA To RGB':       { 'Inputs': [ 'RGBA' ],             'Outputs': [ 'Alpha', 'RGB' ], 'Description': '' },
                'Seconds to Time':   { 'Inputs': [ 'Seconds' ],          'Outputs': [ 'Result' ], 'Description': '' },
                'Time to seconds':   { 'Inputs': [ 'Time' ],             'Outputs': [ 'Result' ], 'Description': '' },
                'Time to TimeCode':  { 'Inputs': [ 'Time' ],             'Outputs': [ 'Result' ], 'Description': '' },
                'TimeCode to Time':  { 'Inputs': [ 'TimeCode' ],         'Outputs': [ 'Result' ], 'Description': '' },
                'Vector to Number':  { 'Inputs': [ 'V' ],                'Outputs': [ 'X', 'Y', 'Z' ], 'Description': '' },
                'Vector2 to Number': { 'Inputs': [ 'V' ],                'Outputs': [ 'X', 'Y' ], 'Description': '' }
                },
        'Number': {
                'Absolute (|a|)': { 'Inputs': [ 'a' ], 'Outputs': [ 'Result' ], 'Description': '' },
                'Add (a + b)': { 'Inputs': [ 'a', 'b' ], 'Outputs': [ 'Result' ], 'Description': '' },
                'arccos(a)': { 'Inputs': [ 'a' ], 'Outputs': [ 'Result' ], 'Description': '' },
                'arcsin(a)': { 'Inputs': [ 'a' ], 'Outputs': [ 'Result' ], 'Description': '' },
                'arctan(a)': { 'Inputs': [ 'a' ], 'Outputs': [ 'Result'], 'Description': '' },
                'arctan2(b/a)': { 'Inputs': [ 'a', 'b' ], 'Outputs': [ 'Result' ], 'Description': '' },
                'Cosine cos(a)': { 'Inputs': [ 'a' ], 'Outputs': [ 'Result' ], 'Description': '' },
                'Damp': { 'Inputs': [ 'a', 'Damping Factor' ], 'Outputs': [ 'Result' ], 'Description': '' },
                'Damp (Clock based)': { 'Inputs': [ 'a', 'Damping Factor', 'Play Mode' ], 'Outputs': [ 'Result' ], 'Description': '' },
                'Distance Numbers': { 'Inputs': [ 'a', 'b' ], 'Outputs': [ 'Result'], 'Description': '' },
                'Divide (a/b)': { 'Inputs': [ 'a', 'b' ], 'Outputs': [ 'Result' ], 'Description': '' },
                'exp(a)': { 'Inputs': [ 'a' ], 'Outputs': [ 'Result' ], 'Description': '' },
                'Exponent (a^b)': { 'Inputs': [ 'a', 'b' ], 'Outputs': [ 'Result' ], 'Description': '' },
                'IF Cond Then A Else B': { 'Inputs': [ 'a', 'b', 'Cond' ], 'Outputs': [ 'Result' ], 'Description': '' },
                'Integer': { 'Inputs': [ 'a' ], 'Outputs': [ 'Result' ], 'Description': '' },
                'Invert (1/a)': { 'Inputs': [ 'a' ], 'Outputs': [ 'Result' ], 'Description': '' },
                'Is Between A and B': { 'Inputs': [ 'a', 'b', 'Value' ], 'Outputs': [ 'Result' ], 'Description': '' },
                'Is Different (a != b)': { 'Inputs': [ 'a', 'b' ], 'Outputs': [ 'Result' ], 'Description': '' },
                'Is Greater (a > b)': { 'Inputs': [ 'a', 'b' ], 'Outputs': [ 'Result' ], 'Description': '' },
                'Is Greater or Equal (a >= b)': { 'Inputs': [ 'a', 'b' ], 'Outputs': [ 'Result' ] },
                'Multiply (a x b)': { 'Inputs': [ 'a', 'b' ], 'Outputs': [ 'Result' ] },
                'Min Pass-thru': { 'Inputs': [ 'P01', 'P02', 'P03', 'P04', 'P05', 'P06', 'P07', 'P08', 'P09', 'P10', 'P11', 'P12', 'P13', 'P14', 'P15' ], 'Outputs': [ 'Result' ] },
                'log(a)': { 'Inputs': [ 'a' ], 'Outputs': [ 'Result' ] },
                'Is Greater (a > b)': { 'Inputs': [ 'a', 'b' ], 'Outputs': [ 'Result' ] },
                'sqrt(a)': {'Inputs': [ 'a' ], 'Outputs': [ 'Result' ] },
                'Modulo mod(a, b)': { 'Inputs': [ 'a', 'b' ], 'Outputs': [ 'Result' ] },
                'Memory (a when REC)': { 'Inputs': [ 'a', 'REC' ], 'Outputs': [ 'Result' ] },
                'ln(a)': { 'Inputs': [ 'a' ], 'Outputs': [ 'Result' ] },
                'Scale And Offset (Number)': { 'Inputs': [ 'X', 'Scale Factor', 'Offset', 'Clamp Max', 'Clamp Min' ], 'Outputs': [ 'Result' ] },
                'Tangeant tan(a)': { 'Inputs': ['a'], 'Outputs': [ 'Result' ] },
                'Sum 10 numbers': { 'Inputs': [ 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j' ], 'Outputs': [ 'Result' ] },
                'Sine sin(a)': { 'Inputs': [ 'a' ], 'Outputs': [ 'Result' ] },
                'Subtract (a - b)': { 'Inputs': [ 'a', 'b' ], 'Outputs': [ 'Result' ] },
                'Is Less (a < b)': { 'Inputs': [ 'a', 'b' ], 'Outputs': [ 'Result' ] },
                'Triggered Delay with Memory (Number)': { 'Inputs': [ 'Number', 'Delay', 'Toggle Switch' ], 'Outputs': [ 'Result' ] },
                'Pull Number': { 'Inputs': [ 'a' ], 'Outputs': ['Result'] },
                'Precision Numbers': { 'Inputs': [ 'a', 'Precision' ], 'Outputs': [ 'Result' ] },
                'Max Pass-thru': { 'Inputs': [ 'P01', 'P02', 'P03', 'P04', 'P05', 'P06', 'P07', 'P08', 'P09', 'P10', 'P11', 'P12', 'P13', 'P14', 'P15' ], 'Outputs': [ 'Result' ] },
                'Is Less or Equal (a <= b)': { 'Inputs': [ 'a', 'b' ], 'Outputs': [ 'Result' ] },
                'Is Identical (a == b)': { 'Inputs': [ 'a', 'b' ], 'Outputs': [ 'Result' ] },
                'Triggered Delay (Number)': { 'Inputs': [ 'Number', 'Delay', 'Enabled', 'Panic Button' ], 'Outputs': [ 'Result' ] }
                },
        'Other': {
                'Bezier Curve':               { 'Inputs': [ 'Control Point 1', 'Control Point 2', 'Control Point 3', 'Control Point 4', 'Position Ratio', 'Previous Segment\'s Result', 'Segment Count', 'Segment Index' ], 'Outputs': [ 'Result' ], 'Description': '' },
                'Damping (3D)':               { 'Inputs': [ 'Damping Factor', 'P' ], 'Outputs': [ 'Result' ], 'Description': '' },
                'Damping (3D) (Clock based)': { 'Inputs': [ 'Damping Factor', 'P', 'Play Mode' ], 'Outputs': [ 'Result' ], 'Description': '' },
                'FCurve Number (%)':          { 'Inputs': [ 'Position %' ], 'Outputs': [ 'Value' ], 'Description': '' },
                'FCurve Number (Time)':       { 'Inputs': [ 'Position' ], 'Outputs': [ 'Value' ], 'Description': '' },
                'Real Time Filter': { 'Inputs': [ 'In P  0', 'In P  1', 'In P  2', 'In P  3', 'In P  4', 'In P  5', 'In P  6', 'In P  7', 'In P  8', 'In P  9', 'In P 10', 'In P 11', 'In P 12', 'In P 13', 'In P 14', 'In P 15', 'In P 16', 'In P 17', 'In P 18', 'In P 19', 'In P 20', 'In P 21', 'In P 22', 'In P 23', 'In P 24', 'In P 25', 'In P 26', 'In P 27', 'In P 28', 'In P 29', 'In P 30', 'In P 31', 'Enable', 'Drop Error', 'Drop Analysis', 'Filter Type', 'Filter Len' ], 'Outputs': [ 'Out P  0', 'Out P  1', 'Out P  2', 'Out P  3', 'Out P  4', 'Out P  5', 'Out P  6', 'Out P  7', 'Out P  8', 'Out P  9', 'Out P 10', 'Out P 11', 'Out P 12', 'Out P 13', 'Out P 14', 'Out P 15', 'Out P 16', 'Out P 17', 'Out P 18', 'Out P 19', 'Out P 20', 'Out P 21', 'Out P 22', 'Out P 23', 'Out P 24', 'Out P 25', 'Out P 26', 'Out P 27', 'Out P 28', 'Out P 29', 'Out P 30', 'Out P 31' ] },
                'Triggered Plus Minus Counter': { 'Inputs': [ 'Increment', 'Loop', 'Max', 'Min', 'Trigger Decrease', 'Trigger Increase' ], 'Outputs': [ 'Result' ], 'Description': '' },
                'Triggered Random':           { 'Inputs': [ 'Max', 'Min', 'Precision', 'Seed', 'Trigger Get Number' ], 'Outputs': [ 'Result' ], 'Description': '' }
                },
        'Rotation': {
                'Add (R1 + R2)':               { 'Inputs': [ 'Ra', 'Rb' ], 'Outputs': [ 'Result' ], 'Description': '' },
                'Angle Difference (Points)':   { 'Inputs': [ 'P1', 'P2', 'Radius' ], 'Outputs': [ 'Angle' ], 'Description': '' },
                'Angle Difference (Rotations)':{ 'Inputs': [ 'Mult. Factor', 'Offset', 'R1', 'R2' ], 'Outputs': [ 'Angle' ], 'Description': '' },
                'Angular Acceleration':        { 'Inputs': [ 'R' ], 'Outputs': [ 'Result' ], 'Description': '' },
                'Angular Speed':               { 'Inputs': [ 'R' ], 'Outputs': [ 'Result' ], 'Description': '' },
                'Damp (Rotation)':             { 'Inputs': [ 'Damping', 'Max acc', 'Max speed', 'Play Mode', 'R' ], 'Outputs': [ 'Result' ], 'Description': '' },
                'Global To Local':             { 'Inputs': [ 'Base', 'Global Rot' ], 'Outputs': [ 'Local Rot' ], 'Description': '' },
                'Interpolate':                 { 'Inputs': [ 'c', 'Ra', 'Rb' ], 'Outputs': [ 'Result' ], 'Description': '' },
                'Local To Global':             { 'Inputs': [ 'Base', 'Local Rot' ], 'Outputs': [ 'Global Rot' ], 'Description': '' },
                'Rotation Scaling':            { 'Inputs': [ 'b', 'Ra' ], 'Outputs': [ ], 'Description': '' },
                'Sensor Rotation Helper':      { 'Inputs': [ 'Model', 'Offset', 'Sensor', 'X Factor', 'Y Factor', 'Z Factor' ], 'Outputs': [ 'Result' ], 'Description': '' },
                'Subtract (R1 - R2)':          { 'Inputs': [ 'Ra', 'Rb' ], 'Outputs': [ 'Result' ], 'Description': '' },
                'Three-Point Constraint':      { 'Inputs': [ 'Pa', 'Pb', 'Pc' ], 'Outputs': [ 'Result' ], 'Description': '' }
                },
        'Shapes': {
                'Select exclusive': { 'Inputs': [ '1', '2', '3', '4', '5', '6', 'Percent' ], 'Outputs': [ '1', '2', '3', '4', '5', '6', 'Default' ], 'Description': '' },
                'Select exclusive 24': { 'Inputs': [ 'Percent', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24' ], 'Outputs': [ 'Default', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24' ] },
                'Shape calibration': { 'Inputs': [ 'Max', 'Min', 'Reverse', 'Value' ], 'Outputs': [ 'Percent' ], 'Description': '' }
                },
        'Sources': {
                'Counter with Start Stop': { 'Inputs': [ 'Trigger', 'Freq', 'Start', 'Stop', 'Bounce' ], 'Outputs': [ 'Count' ] },
                'Sine Ramp': { 'Inputs': [ 'Amp', 'Freq', 'Phase %', 'Play Mode' ], 'Outputs': [ 'Result' ] },
                'Random': { 'Inputs': [ 'Min', 'Max', 'Freq', 'Precision', 'Seed', 'Play Mode', 'Trigger Play / Pause' ], 'Outputs': [ 'Result' ] },
                'Ramp': { 'Inputs': [ ], 'Outputs': [ 'Count' ] },
                'Pulse': { 'Inputs': [ 'Freq Hz', 'Enabled', 'Play Mode' ], 'Outputs': [ 'Result' ] },
                'Isoceles Triangle Ramp': { 'Inputs': [ 'Amp', 'Freq', 'Phase %', 'Play Mode' ], 'Outputs': [ 'Result' ] },
                'Square Ramp': { 'Inputs': [ 'Amp', 'Freq', 'Phase %', 'Play Mode' ], 'Outputs': [ 'Result' ] },
                'Half Circle Ramp': { 'Inputs': [ 'Amp', 'Freq', 'Phase %', 'Play Mode' ], 'Outputs': [ 'Result' ] },
                'Right Triangle Ramp': { 'Inputs': [ 'Amp', 'Freq', 'Phase %', 'Play Mode' ], 'Outputs': [ 'Result' ] },
                'Counter with Play Pause': { 'Inputs': [ 'Loop', 'Bounce', 'Min', 'Max', 'Speed', 'Trigger Play / Pause', 'Trigger Reset', 'Play Mode' ], 'Outputs': [ 'Count' ] }
                },
        'System': {
                'Local Time':     { 'Inputs': [ ], 'Outputs': [ 'Result' ] },
                'Reference Time': { 'Inputs': [ ], 'Outputs': [ 'Result' ] },
                'Play Mode':      { 'Inputs': [ ], 'Outputs': [ 'Result' ] },
                'Current Time':   { 'Inputs': [ ], 'Outputs': [ 'Result' ] },
                'System Time':    { 'Inputs': [ ], 'Outputs': [ 'Result' ] }
                },
        'Time': {
                'Is Greater (T1 > T2)':           { 'Inputs': [ 'T1', 'T2' ], 'Outputs': [ 'Result' ] },
                'Is Greater or Equal (T1 >= T2)': { 'Inputs': [ 'T1', 'T2' ], 'Outputs': [ 'Result' ] },
                'Is Less or Equal (T1 <= T2)':    { 'Inputs': [ 'T1', 'T2' ], 'Outputs': [ 'Result' ] },
                'Is Identical (T1 == T2)':        { 'Inputs': [ 'T1', 'T2' ], 'Outputs': [ 'Result' ] },
                'Is Less (T1 < T2)':              { 'Inputs': [ 'T1', 'T2' ], 'Outputs': [ 'Result' ] },
                'Is Different (T1 != T2)':        { 'Inputs': [ 'T1', 'T2' ], 'Outputs': [ 'Result' ] },
                'IF Cond Then T1 Else T2':        { 'Inputs': [ 'Cond', 'T1', 'T2' ], 'Outputs': [ 'Result' ] }
                },
        'Vector': {
                'Normalize': { 'Inputs': [ 'Vector' ], 'Outputs': [ 'Result' ] },
                'Subtract (V1 - V2)': { 'Inputs': [ 'V1', 'V2' ], 'Outputs': [ 'Result' ] },
                'Derive': { 'Inputs': [ 'V1', 'V2', 'Reset' ], 'Outputs': [ 'Result' ] },
                'Angle': { 'Inputs': [ 'V1', 'V2' ], 'Outputs': [ 'Result' ] },
                'Middle Point': { 'Inputs': [ 'v1 (Position)', 'v2 (Position)', 'ratio' ], 'Outputs': [ 'Result' ] },
                'Gravity': { 'Inputs': [ 'Position', 'Speed', 'Acceleration' ], 'Outputs': [ 'Result' ] },
                'Scale Damping': { 'Inputs': [ 'S', 'Max speed', 'Max acc', 'Damping', 'Play Mode' ], 'Outputs': [ 'Result' ] },
                'Memory (V1 when REC)': { 'Inputs': [ 'V1', 'REC' ], 'Outputs': [ 'Result' ] },
                'Determinant': { 'Inputs': [ 'I', 'J', 'K' ], 'Outputs': [ 'Result' ] },
                'Is Different (V1 != V2)': { 'Inputs': [ 'V1', 'V2' ], 'Outputs': [ 'Result' ] },
                'Damp Position': { 'Inputs': [ 'T', 'Max speed', 'Max acc', 'Damping', 'Play Mode' ], 'Outputs': [ 'Result' ] },
                'Is Identical (V1 == V2)': { 'Inputs': [ 'V1', 'V2' ], 'Outputs': [' Result' ] },
                'Scale (a x V)': { 'Inputs': [ 'Number', 'Vector' ], 'Outputs': [ 'Result' ] },
                'Distance': { 'Inputs': [ 'v1 (Position)', 'v2 (Position)' ], 'Outputs': [ 'Result' ] },
                'Add (V1 + V2)': { 'Inputs': [ 'V1', 'V2' ], 'Outputs': [ 'Result' ] },
                'Center Of Mass': { 'Inputs': [ 'P  0', 'P  1', 'P  2', 'P  3', 'P  4', 'P  5', 'P  6', 'P  7', 'P  8', 'P  9' ], 'Outputs': [ 'Mass Center' ] },
                'Precision Vectors': { 'Inputs': [ 'a', 'Precision' ], 'Outputs': [ 'Result' ] },
                'Length': { 'Inputs': [ 'Vector' ], 'Outputs': [ 'Result' ] },
                'Orbit Attraction': { 'Inputs': [ 'Origin', 'Position', 'Speed', 'Acceleration cte' ], 'Outputs': [ 'Result' ] },
                'Vector Product (V1 x V2)': { 'Inputs': [ 'V1', 'V2' ], 'Outputs': [ 'Result' ] },
                'Pull Vector': { 'Inputs': [ 'V' ], 'Outputs': ['Result' ] },
                'IF Cond Then A Else B': { 'Inputs': [ 'Cond', 'a', 'b' ], 'Outputs': [ 'Result' ] },
                'Displacement': { 'Inputs': [ 'Velocity', 'Reset' ], 'Outputs': [ 'T' ] },
                'Scale And Offset (Vector)': { 'Inputs': [ 'X', 'Scale Factor', 'Offset', 'Clamp Max', 'Clamp Min' ], 'Outputs': [ 'Result' ] },
                'Sum 10 vectors': { 'Inputs': [ 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j' ], 'Outputs': [ 'Result' ] },
                'Triggered Delay (Vector)': { 'Inputs': [ 'Vector', 'Delay', 'Enabled', 'Panic Button' ], 'Outputs': [ 'Result' ] },
                'Acceleration': { 'Inputs': [ 'Position' ], 'Outputs': ['Result']},
                'Triggered Delay with Memory (Vector)': { 'Inputs': [ 'Vector', 'Delay', 'Toggle Switch' ], 'Outputs': [ 'Result' ] },
                'Speed': { 'Inputs': [ 'Position' ], 'Outputs': [ 'T' ] },
                'Dot Product (V1.V2)': { 'Inputs': [ 'V1', 'V2' ], 'Outputs': [ 'Result' ] }
                }
}

class Character_Rig_Constraint_Builder:
	"""
	Class used to setup Constraints on a standard Volition bipedal character.

	*Arguments:*
		* ``character`` <pyfbsdk.FBCharacter>

	*Keyword Arguments:*
		* ``none``

	*Examples:* ::
		>>> constraint_rigger = Character_Rig_Constraint_Builder( my_char )
		>>> constraint_rigger.run()
	"""
	def __init__( self, character ):
		self.character = character
		self.namespace = character.LongName.split(":")[0]
		self.character_constraint_folder = None
		self.constraints = dict() #{ <str> 'long_name': {'constraint':<FBConstraint>,'snap':<bool>}, ... }
		self.object_cache = dict() #build this up as parts are run and objects identified { <str> Tag : [ <pyfbsdk.FBModel> ], ... }

	@staticmethod
	def _extract_side_from_name( long_name, label ):
		"""
		PRIVATE, extracts "Right" from 'idealMale:idealMale_skel:RightKnee:PosConst'

		*Arguments:*
			* ``long_name`` <str> .LongName of the object
			* ``label``     <str> portion of a .LongName to use when locating the 'side', e.g. "Knee" in "idealMale:idealMale_skel:RightKnee:PosConst"

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``found`` <str> the side found or '' if not found
		"""
		label_split = label.split( ":" )
		name_split  = long_name.split( ":" )

		found = ""
		for split in name_split:
			if label_split[ 0 ] in split:
				found = split[ :split.find( label_split[ 0 ] ) ]
				break

		return found

	def _get_target_objects( self, obj, child_name_key, target_name_key, symmetry=True, alt_sides=ALT_SIDES ):
		"""
		PRIVATE method to identify the target objects associated with a child(constrained) object.  Handles limiting result to appropriate Left or Right side.

		*Arguments:*
			* ``obj``         <pyfbsdk.FBModel> object being constrained.

		*Keyword Arguments:*
			* ``symmetry``    <bool> process Left\Right filtering
			* ``alt_sides``   <dict> e.g. { 'Left':'Lft', 'Right':'Rgt' }

		*Returns:*
			* ``target_objs`` <list> of resulting found target objects
		"""

		# note: NOT case sensitive
		if symmetry:
			alt_side = None
			i = obj.Name.find( child_name_key )
			if i:
				side = obj.Name[ :i ]
			else:
				side = ''

			# Lame, also need to handle spelling differences like 'Left','Lft' and 'Right','Rgt'
			target_objs = [ target_obj for target_obj in self.object_cache[ target_name_key ] if side.lower() in target_obj.Name.lower() ]

			if alt_sides:
				for k,v in alt_sides.iteritems():
					if side == k:
						alt_side = v
					if side == v:
						alt_side = k

			if alt_side:
				target_objs += [ target_obj for target_obj in self.object_cache[ target_name_key ] if alt_side.lower() in target_obj.Name.lower() ]
		else:
			target_objs = [ target_obj for target_obj in self.object_cache[ target_name_key ] ]

		return target_objs

	@staticmethod
	def _is_rejected( obj, reject_list ):
		"""
		PRIVATE, returns True if any items in the 'reject_list' are found to be in the obj.LongName

		*Arguments:*
			* ``obj``            <pyfbsdk.FBComponent>
			* ``reject_list``    <list> or <tuple>, e.g. ('tag','Ctrl')

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``result``         <bool>
		"""
		return vmobu.core.is_pattern_in_string( obj.LongName, reject_list )

	@staticmethod
	def _force_target_object_order( target_object_list ):
		"""
		PRIVATE, reorders a list of target objects. Forces the list to be in alphabetical order if the targets name ends with A, B, C etc.

		**Arguments:**

			:``target_object_list``:	`ls` List of target objects we are going to reorder
		"""

		new_list = [ ]
		for i in range( 0, len( target_object_list ) ):
			new_list.append( None )
		for target in target_object_list:
			for key in TARGET_INDICES.keys( ):
				if target.Name.lower( ).endswith( key ):
					new_list[ TARGET_INDICES[ key ] ] = target

		return new_list

	def _create_procedural_control( self, namespace, control_label, align_object, simple = False ):
		# Create and edit look of control
		control = pyfbsdk.FBModelMarker( '{0}:Ctrl:{1}_Effector'.format( namespace, control_label ) )
		control.Length = 10
		control.Show = True
		control.Color = pyfbsdk.FBColor( .2, 1, .2 )
		control.Look = pyfbsdk.FBMarkerLook.kFBMarkerLookCapsule
		control.ResLevel = pyfbsdk.FBMarkerResolutionLevel.kFBMarkerLowResolution
		vmobu.core.add_property_obj( control, 'effector_type', 'procedural',
				                       force=True,
				                       attr_def=None)

		vmobu.core.add_property_obj( control, 'effector_type', 'procedural',
				                       force=True,
				                       attr_def=None)

		null_holder = pyfbsdk.FBModelNull( '{0}:Ctrl:{1}_Holder'.format( namespace, control_label ) )
		# Position to the align_object and parent to the control
		vmobu.core.align_objects( control, align_object, False, True, True )
		vmobu.core.align_objects( null_holder, align_object, False, True, True )

		control.Parents.append( null_holder )
		null_holder.Parents.append( vmobu.core.get_object_by_name( '{0}:ctrl:reference'.format( namespace ), case_sensitive = False, models_only = True, single_only = True ) )

		# Get the character extension
		character_extension_dict = vmobu.core.get_extensions_from_character( self.character )

		for extension in character_extension_dict.keys( ):
			if 'CustomControl' in extension:
				extension = character_extension_dict[extension]['mobu_object']
				extension.AddObjectDependency( control )
				extension.AddObjectDependency( null_holder )
				extension.UpdateStancePose( )
				break

		if simple:
			# Create parent child constraint
			parent_constraint = self.create_parent_constraint( '*{0}'.format( null_holder.Name ), '*skel:{0}'.format( align_object.Parent.Name ), snap=True, label='Parent', reject=('tag',), symmetry=True )[ 0 ]
			parent_constraint.Snap()

		return control, null_holder


	def activate_constraints(self):
		"""
		Activates all constraints found on this class instance.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``success``  <bool> True on completion
		"""
		for constraint_dict in self.constraints.values():
			constraint = constraint_dict['constraint']

			if constraint_dict['snap']:
				constraint.Snap()
			else:
				constraint.Active = True

		return True

	def organize_constraints( self, character_name = None, body_part = 'Arm', keywords = None ):
		"""
		Activates all constraints found on this class instance.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``success``  <bool> True on completion
		"""
		parent_folder       = None
		right_folder        = None
		left_folder         = None
		if keywords == None:
			keywords = []

		for constraint in pyfbsdk.FBSystem().Scene.Constraints:
			constraint_is_relative = False

			# If the constraint doesn't have the characters name in it, pass. We don't care about it.
			if not self.namespace in constraint.LongName.split( ':' )[ 0 ] or isinstance(constraint, pyfbsdk.FBCharacter ):
				continue

			if self.character_constraint_folder is None:
				self.character_constraint_folder = pyfbsdk.FBFolder( '{0}:Constraints'.format( self.namespace ), constraint )
				self.character_constraint_folder.Items.pop( 0 )

			for keyword in keywords:
				if keyword.lower( ) in constraint.Name.lower( ):
					constraint_is_relative = True
					continue

			if not constraint_is_relative:
				continue

			#Create the parent folder
			if not parent_folder:
				parent_folder = pyfbsdk.FBFolder('{0}:{1}_Constraints'.format( character_name, body_part ), constraint )
				parent_folder.Items.pop( 0 )

			# If there's a side...
			if 'right' in constraint.Name.lower( ):
				# If a folder for the side doesn't exist, make one and add that constraint to it.
				if not right_folder:
					right_folder = pyfbsdk.FBFolder( '{0}:Right_{1}_Constraints'.format( character_name, body_part ), constraint )
					continue
				right_folder.Items.append( constraint )
				continue

			if 'left' in constraint.Name.lower( ):
				if not left_folder:
					left_folder = pyfbsdk.FBFolder( '{0}:Left_{1}_Constraints'.format( character_name, body_part ), constraint )
					continue
				left_folder.Items.append( constraint )
				continue
			else:
				parent_folder.Items.append( constraint )

		# Append the two sides
		parent_folder.Items.append( right_folder )
		parent_folder.Items.append( left_folder )
		self.character_constraint_folder.Items.append( parent_folder )

		return True

	def _filtered_get_obj_by_wildcard(self, namespace, pattern, case_sensitive=False, reject=('tag','Ctrl') ):
		"""
		PRIVATE, filters the result from a wildcard search by rejecting any matches with the 'reject' list.

		*Arguments:*
			* ``namespace``         <str> namespace portion of wildcard pattern to search within
			* ``pattern`` 				<str> string name or pattern supporting '*' of the object(s) being searched for

		*Keyword Arguments:*
			* ``case_sensitive``    <bool> is the wildcard search case_sensitive?
			* ``reject_list``       <list> or <tuple>, e.g. ('tag','Ctrl')

		*Returns:*
			* ``result`             <list> filtered objects <pyfbsdk.FBComponent>
		"""
		result = []
		wild_list = vmobu.core.get_objects_from_wildcard( "{0}:{1}".format( namespace, pattern ), use_namespace=True, case_sensitive=case_sensitive )
		if wild_list:
			for obj in wild_list:
				if reject and self._is_rejected( obj, reject ):
					pass
				else:
					result.append( obj )

		return result

	@staticmethod
	def _create_new_constraint_name( obj, label ):
		"""
		PRIVATE, simple LongName constructor for new constraints

		*Arguments:*
			* ``obj``      <pyfbsdk.FBComponent> object being constrained
			* ``label``    <str> typically the type of constraint

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``new_name`` <str> e.g. "namespace:obj_name:Position"
		"""
		full_namespace = vmobu.core.get_namespace_from_obj( obj, as_string=True )
		if full_namespace:
			new_name = '{0}:{1}:{2}'.format( full_namespace, label, obj.Name )
		else:
			new_name = '{0}:{1}'.format( label, obj.Name )

		return new_name

	def create_aim_constraint( self, child_name_pattern, aim_name_pattern, up_name_pattern, snap=True, label='AimConst', reject=('tag','Ctrl')  ):
		"""
		Creates and returns a new 'aim constraint', or several if appropriate(e.g. Left & Right)

		*Arguments:*
			* ``child_name_pattern``   <str> pattern to identify the objects that will be constrained,   e.g. '*Arm_UpVector'
			* ``aim_name_pattern``     <str> pattern to identify the aim object(s),                      e.g. '*Shoulder'
			* ``up_name_pattern``      <str>	pattern to identify the 'up' object,                        e.g. '*ForeArm'

		*Keyword Arguments:*
			* ``snap``                 <bool>   When the constraint is activated, should it be via 'Snap'(True) or 'Active'(False)
			* ``label``                <str>    label to be used when naming the constraint object
			* ``reject_list``          <list> or <tuple>, e.g. ('tag','Ctrl')

		*Returns:*
			* ``result``               <list> of <pyfbsdk.FBConstraint>
		"""
		result = []

		child_name_key = child_name_pattern.replace( "*", "" )
		aim_name_key   = aim_name_pattern.replace( "*", "" )

		if up_name_pattern:
			up_name_key   = up_name_pattern.replace( "*", "" )

		self.object_cache[ child_name_key ] = self._filtered_get_obj_by_wildcard( self.namespace, child_name_pattern, reject=reject )
		self.object_cache[ aim_name_key ]   = self._filtered_get_obj_by_wildcard( self.namespace, aim_name_pattern,   reject=reject )

		if up_name_pattern:
			self.object_cache[ up_name_key ]    = self._filtered_get_obj_by_wildcard( self.namespace, up_name_pattern,    reject=reject )

		for obj in self.object_cache[ child_name_key ]:
			aim_objs = self._get_target_objects( obj, child_name_key, aim_name_key )

			if up_name_pattern:
				up_obj   = self._get_target_objects( obj, child_name_key, up_name_key )[0]

			constraint = vmobu.core.create_constraint( 'Aim', long_name=self._create_new_constraint_name( obj, label )  )
			# constraint = vmobu.core.create_constraint( 'Aim', long_name='{1}:{0}'.format( obj.LongName, label )  )
			constraint.ReferenceAdd( 0, obj )
			for aim_obj in aim_objs:
				constraint.ReferenceAdd( 1, aim_obj )

			if up_name_pattern:
				constraint.ReferenceAdd( 2, up_obj )

			self.constraints[ constraint.LongName ] = { 'constraint':constraint, 'snap':snap }

			result.append( constraint )

		vmobu.core.evaluate()
		return result

	def create_parent_constraint( self, child_name_pattern, target_name_pattern, snap=True, label='ParentConst', reject=('tag',), symmetry = True):
		"""
		Creates and returns a new 'parent constraint', or several if appropriate(e.g. Left & Right)

		*Arguments:*
			* ``child_name_pattern``   <str> pattern to identify the objects that will be constrained,   e.g. '*Offset'
			* ``target_name_pattern``  <str> pattern to identify the target object(s),                   e.g. '*Offset_controller'

		*Keyword Arguments:*
			* ``snap``                 <bool>   When the constraint is activated, should it be via 'Snap'(True) or 'Active'(False)
			* ``label``                <str>    label to be used when naming the constraint object
			* ``reject_list``          <list> or <tuple>, e.g. ('tag','Ctrl')

		*Returns:*
			* ``result``               <list> of <pyfbsdk.FBConstraint>
		"""
		result = []

		child_name_key = child_name_pattern.replace( "*", "" )
		target_name_key = target_name_pattern.replace( "*", "" )

		self.object_cache[ child_name_key ] = self._filtered_get_obj_by_wildcard( self.namespace, child_name_pattern,  reject=reject )
		self.object_cache[ target_name_key ]= self._filtered_get_obj_by_wildcard( self.namespace, target_name_pattern, reject=reject )

		for obj in self.object_cache[ child_name_key ]:
			target_objs = self._get_target_objects( obj, child_name_key, target_name_key, symmetry = symmetry )

			constraint = vmobu.core.create_constraint_parent( obj, target_objs, name = self._create_new_constraint_name( obj, label ) )

			self.constraints[ constraint.LongName ] = {'constraint':constraint, 'snap':snap }
			vmobu.core.evaluate()

			result.append( constraint )

		return result

	def create_position_constraint( self, child_name_pattern, target_name_pattern, snap=False, label='PosConst', animated=False, reject=('tag',), symmetry = True):
		"""
		Creates and returns a new 'position constraint', or several if appropriate(e.g. Left & Right)

		*Arguments:*
			* ``child_name_pattern``   <str> pattern to identify the objects that will be constrained,   e.g. '*Offset'
			* ``target_name_pattern``  <str> pattern to identify the target object(s),                   e.g. '*Offset_controller'

		*Keyword Arguments:*
			* ``snap``                 <bool>   When the constraint is activated, should it be via 'Snap'(True) or 'Active'(False)
			* ``label``                <str>    label to be used when naming the constraint object
			* ``reject``               <list> or <tuple>, e.g. ('tag','Ctrl')

		*Returns:*
			* ``result``               <list> of <pyfbsdk.FBConstraint>
		"""
		result = []

		child_name_key = child_name_pattern.replace( "*", "" )
		target_name_key = target_name_pattern.replace( "*", "" )

		self.object_cache[ child_name_key ] = self._filtered_get_obj_by_wildcard( self.namespace, child_name_pattern,  reject=reject )
		self.object_cache[ target_name_key ]= self._filtered_get_obj_by_wildcard( self.namespace, target_name_pattern, reject=reject )

		if self.object_cache[ child_name_key ] and self.object_cache[ target_name_key ]:
			for obj in self.object_cache[ child_name_key ]:
				constraint_index = 0

				constraint = vmobu.core.create_constraint( 'Position', long_name=self._create_new_constraint_name( obj, label ) )
				constraint.ReferenceAdd( 0, obj )

				target_objs = self._get_target_objects( obj, child_name_key, target_name_key, symmetry=symmetry )
				if len( target_objs ) > 1:
					target_objs = self._force_target_object_order( target_objs )

				for target_obj in target_objs:
					constraint.ReferenceAdd( 1, target_obj )
					if animated:
						weight_prop = constraint.PropertyList.Find( target_obj.LongName + ".Weight" )
						weight_prop.SetAnimated( True )

				self.constraints[ constraint.LongName ] = {'constraint': constraint, 'snap': snap }
				vmobu.core.evaluate( )

				result.append( constraint )

		return result


	def create_rotation_constraint(self, child_name_pattern, target_name_pattern, snap=True, label='RotConst',
											 reject=('tag',), affectx=True, affecty=True, affectz=True, mute=[], weight=100, roll_constraint = False ):
		"""
		Creates and returns a new 'rotation constraint', or several if appropriate(e.g. Left & Right)

		*Arguments:*
			* ``child_name_pattern``   <str> pattern to identify the objects that will be constrained,   e.g. '*Offset'
			* ``target_name_pattern``  <str> pattern to identify the target object(s),                   e.g. '*Offset_controller'

		*Keyword Arguments:*
			* ``snap``                 <bool>   When the constraint is activated, should it be via 'Snap'(True) or 'Active'(False)
			* ``label``                <str>    label to be used when naming the constraint object
			* ``reject``               <list> or <tuple>, e.g. ('tag','Ctrl')

		*Returns:*
			* ``result``               <list> of <pyfbsdk.FBConstraint>
		"""
		result = []

		child_name_key = child_name_pattern.replace("*", "")
		target_name_key = target_name_pattern.replace("*", "")

		self.object_cache[child_name_key] = self._filtered_get_obj_by_wildcard(self.namespace, child_name_pattern,
																									  reject=reject)
		self.object_cache[target_name_key] = self._filtered_get_obj_by_wildcard(self.namespace, target_name_pattern,
																										reject=reject)

		for obj in self.object_cache[child_name_key]:
			vmobu.core.mute_property_members(obj, 'Lcl Rotation', (mute))

		for obj in self.object_cache[child_name_key]:
			constraint = vmobu.core.create_constraint('Rotation', long_name=self._create_new_constraint_name(obj, label))
			constraint.ReferenceAdd(0, obj)

			target_objs = self._get_target_objects(obj, child_name_key, target_name_key)
			for target_obj in target_objs:
				constraint.ReferenceAdd(1, target_obj)

			self.constraints[constraint.LongName] = {'constraint': constraint, 'snap': snap}
			vmobu.core.evaluate()

			result.append(constraint)

			const_weight = constraint.PropertyList.Find('Weight')
			const_affect_x = constraint.PropertyList.Find('AffectX')
			const_affect_y = constraint.PropertyList.Find('AffectY')
			const_affect_z = constraint.PropertyList.Find('AffectZ')
			const_weight.Data = weight
			const_affect_x.Data = affectx
			const_affect_y.Data = affecty
			const_affect_z.Data = affectz

			if roll_constraint:
				self.create_additive_simple_constraint( constraint, obj.Name, target_obj, 'Procedural', obj )

		return result

	def create_additive_simple_constraint( self, constraint = None, control_label = '', twist_bone = None, constraint_label = '', align_obj = None ):
		"""
		Creates an additive control for the procedural constraints. Allows for editing of the procedural results in mobu.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``constraint``  <pyfbsdk.FBConstraint>
			* ``control_label`` <str> name of the control for the constraint
			* ``twist_bone`` <pyfbsdk.FBModelSkeleton> associated with the constraint
			* ``constraint_label`` <str> what to name the constraint
			* ``align_obj`` <pyfbsdk.FBModel> object to align the control to

		*Returns:*
			* ``none``
		"""

		#Create null_holder and control
		control, null_holder = self._create_procedural_control( self.namespace, control_label, align_obj, simple = True )

		# Lock attributes on the control and null_holder
		#vmobu.core.lock_property_members( control, 'Lcl Translation', ( 0, 1, 2 ) )
		#vmobu.core.lock_property_members( null_holder, 'Lcl Scaling', ( 0, 1, 2 ) )

		# Get the anim node for this property, forcing it to be animated so we can connect it in the constraint.
		vmobu.core.get_animnode( constraint, 'Rotation', force_animateable = True)
		vmobu.core.get_animnode( control, 'Lcl Rotation', force_animateable = True )

		vmobu.core.evaluate()

		# Create relation constraint
		side         = self._extract_side_from_name( constraint.LongName, constraint_label )
		r_name       = self._create_new_constraint_name( constraint, constraint_label )
		r_constraint = vmobu.core.create_constraint( "Relation", long_name=r_name )
		r_constraint.Active = True
		assert isinstance( r_constraint, pyfbsdk.FBConstraintRelation )

		# Set source ( Marker ) and destination ( Constraint )
		source_sender_box = r_constraint.SetAsSource( control )
		source_sender_box.UseGlobalTransforms = False
		constraint_box = r_constraint.ConstrainObject( constraint )

		# Create function boxes
		vector_to_number_box = r_constraint.CreateFunctionBox( 'Converters', 'Vector to Number' )
		number_to_vector_box = r_constraint.CreateFunctionBox( 'Converters', 'Number to Vector' )

		add_box    = r_constraint.CreateFunctionBox( 'Number', 'Add (a + b)' )
		is_identical_box = r_constraint.CreateFunctionBox( 'Number', 'Is Identical (a == b)')
		if_conditional_box = r_constraint.CreateFunctionBox( 'Number', 'IF Cond Then A Else B')

		## Create function box inputs and outputs

		# Add box connections
		add_box_in_a = vmobu.core.get_node_connection( add_box, 'a' )
		add_box_in_b = vmobu.core.get_node_connection( add_box, 'b' )
		add_box_in_b.WriteData( [0.0] )
		add_box_out  = vmobu.core.get_node_connection( add_box, 'Result', 'out' )

		# Is Identical connections
		is_identical_in_a = vmobu.core.get_node_connection( is_identical_box, 'a' )
		is_identical_in_b = vmobu.core.get_node_connection( is_identical_box, 'b' )
		is_identical_in_b.WriteData( [0.0] )
		is_identical_out  = vmobu.core.get_node_connection( is_identical_box, 'Result', 'out' )

		# If conditional connections
		if_conditional_a_in    = vmobu.core.get_node_connection( if_conditional_box, 'a' )
		if_conditional_a_in.WriteData( [0.0] )
		if_conditional_b_in    = vmobu.core.get_node_connection( if_conditional_box, 'b' )
		if_conditional_cond_in = vmobu.core.get_node_connection( if_conditional_box, 'Cond')
		if_conditional_out     = vmobu.core.get_node_connection( if_conditional_box, 'Result', 'out')

		#Number to vector box/Vector to number box connections
		number_to_vector_box_in_x = vmobu.core.get_node_connection( number_to_vector_box, 'X' )
		number_to_vector_box_out  = vmobu.core.get_node_connection( number_to_vector_box, 'Result', 'out' )

		vector_to_number_box_in   = vmobu.core.get_node_connection( vector_to_number_box, 'V' )
		vector_to_number_box_x    = vmobu.core.get_node_connection( vector_to_number_box, 'X', 'out' )

		# Sender and reciever box connections
		source_sender_box_out     = vmobu.core.get_node_connection( source_sender_box, 'Lcl Rotation', 'out')
		destination_box_in        = vmobu.core.get_node_connection( constraint_box, 'Rotation' )

		vmobu.core.evaluate()


		# Connect function boxes
		pyfbsdk.FBConnect( source_sender_box_out, vector_to_number_box_in )
		pyfbsdk.FBConnect( vector_to_number_box_x, add_box_in_a )
		pyfbsdk.FBConnect( vector_to_number_box_x, is_identical_in_a )

		pyfbsdk.FBConnect( add_box_out, if_conditional_b_in )
		pyfbsdk.FBConnect( is_identical_out, if_conditional_cond_in )

		pyfbsdk.FBConnect( if_conditional_out, number_to_vector_box_in_x )
		pyfbsdk.FBConnect( number_to_vector_box_out, destination_box_in )

		vmobu.core.evaluate()

		return True

	def create_additive_twist_constraint( self, procedural_constraint = None, twist_bone = None, parent = None, box_from_procedural = None,  box_to_procedural = None, control_label = '' ):
		"""
		Creates an additive control for the procedural constraints. Allows for editing of the procedural results in mobu.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``procedural_constraint``  <pyfbsdk.FBConstraintRelation>
			* ``twist_bone``     <pyfbsdk.FBModelSkeleton>
			* ``parent`` <pyfbsdk.FBModelSkeleton>
			* ``box_from_procedural`` <pyfbsdk.FBBox> Relation constraint function box that we begin the edit with
			* ``box_to_procedural`` <pyfbsdk.FBBox> Relation constraint function box that we finish the edit with
			* ``control_label`` - <str> name of the control

		*Returns:*
			* ``True`` - If successful
		"""
		#Create nullholder and control
		control, null_holder = self._create_procedural_control( self.namespace, control_label, twist_bone )

		# Move the control down the joint to be more centered
		control_shift = -15
		control_translation = control.Translation.Data
		if 'left' in control_label.lower():
			control_shift = control_shift * -1

		# Depending on variety of control, adjust it's orientation and position relative to the driven bone
		if 'leg' in control_label.lower():
			#control.Rotation.Data = pyfbsdk.FBVector3d( -90, 0, 0 )
			control_translation[ 0 ] = control_translation[ 0 ] + control_shift
			control.Translation.Data = control_translation
		else:
			#control.Rotation.Data = pyfbsdk.FBVector3d( 0, -90, 0 )
			control_translation[ 0 ] = control_translation[ 0 ] + control_shift * 0.5
			control.Translation.Data = control_translation

		# Lock attributes on the control and null_holder
		vmobu.core.lock_property_members( control, 'Lcl Translation', ( 0, 1, 2 ) )
		#vmobu.core.lock_property_members( null_holder, 'Lcl Translation', ( 0, 1, 2 ) )
		#vmobu.core.lock_property_members( null_holder, 'Lcl Rotation', ( 0, 1, 2 ) )
		#vmobu.core.lock_property_members( null_holder, 'Lcl Scaling', ( 0, 1, 2 ) )

		vmobu.core.evaluate()

		# Create parent child constraint from the holder to the twist_bone
		parent_constraint = self.create_parent_constraint( '*{0}'.format( null_holder.Name ), '*skel:{0}'.format( twist_bone.Name ), snap=True, label='Holder', reject=('tag',), symmetry=True )[ 0 ]
		parent_constraint.Snap()
		parent_constraint.Active = True

		vmobu.core.evaluate()

		if procedural_constraint:
			# Constrain the parent constraint and add get its input fbox
			control_box      = procedural_constraint.SetAsSource( control )
			control_box.UseGlobalTransforms = False
			control_box_rotate_out = vmobu.core.get_node_connection( control_box, 'Lcl Rotation', 'out' )

			# Create function boxes for relation constraint to connect to parent child constraint
			vector_to_number_box = procedural_constraint.CreateFunctionBox( 'Converters', 'Vector to Number' )
			number_to_vector_box = procedural_constraint.CreateFunctionBox( 'Converters', 'Number to Vector' )

			divide_box = procedural_constraint.CreateFunctionBox( 'Number', 'Divide (a/b)' )
			add_box    = procedural_constraint.CreateFunctionBox( 'Number', 'Add (a + b)' )
			is_identical_box = procedural_constraint.CreateFunctionBox( 'Number', 'Is Identical (a == b)')
			if_conditional_box = procedural_constraint.CreateFunctionBox( 'Number', 'IF Cond Then A Else B')

			#Division box connections
			divide_box_in_a  = vmobu.core.get_node_connection( divide_box, 'a' )
			divide_box_in_b  = vmobu.core.get_node_connection( divide_box, 'b' )
			divide_box_out = vmobu.core.get_node_connection( divide_box, 'Result', 'out' )

			# Add box connections
			add_box_in_a = vmobu.core.get_node_connection( add_box, 'a' )
			add_box_in_b = vmobu.core.get_node_connection( add_box, 'b' )
			add_box_out  = vmobu.core.get_node_connection( add_box, 'Result', 'out' )

			# Is Identical connections
			is_identical_in_a = vmobu.core.get_node_connection( is_identical_box, 'a' )
			is_identical_in_b = vmobu.core.get_node_connection( is_identical_box, 'b' )
			is_identical_out  = vmobu.core.get_node_connection( is_identical_box, 'Result', 'out' )

			# If conditional connections
			if_conditional_a_in    = vmobu.core.get_node_connection( if_conditional_box, 'a' )
			if_conditional_b_in    = vmobu.core.get_node_connection( if_conditional_box, 'b' )
			if_conditional_cond_in = vmobu.core.get_node_connection( if_conditional_box, 'Cond')
			if_conditional_out     = vmobu.core.get_node_connection( if_conditional_box, 'Result', 'out')

			#Number to vector box/Vector to number box connections
			vector_to_number_box_in   = vmobu.core.get_node_connection( vector_to_number_box, 'V' )
			vector_to_number_box_x    = vmobu.core.get_node_connection( vector_to_number_box, 'X', 'out' )

			# Connect all the boxes
			pyfbsdk.FBConnect( box_from_procedural, add_box_in_a )
			pyfbsdk.FBConnect( box_from_procedural, if_conditional_a_in )
			pyfbsdk.FBConnect( add_box_out, if_conditional_b_in )

			#From the control to the conditional
			pyfbsdk.FBConnect( control_box_rotate_out, vector_to_number_box_in )
			pyfbsdk.FBConnect( vector_to_number_box_x, divide_box_in_a )
			pyfbsdk.FBConnect( vector_to_number_box_x, is_identical_in_a )
			pyfbsdk.FBConnect( divide_box_out, add_box_in_b )
			pyfbsdk.FBConnect( is_identical_out, if_conditional_cond_in )

			# End connection
			pyfbsdk.FBConnect( if_conditional_out, box_to_procedural )

			# Set static values
			is_identical_in_b.WriteData( [ 0.0 ] )
			divide_box_in_b.WriteData( [ 2.0 ] )

		return True

	# noinspection PyArgumentList
	def create_bend_constraint(self, constraint_label, out_node_name, label='Procedural', snap=True ):
		"""
		Creates a 'bend constraint', i.e. the type used on the elbow or knee.

		*Arguments:*
			* ``constraint_label``  <str>
			* ``out_node_name``     <str>

		*Keyword Arguments:*
			* ``label``             <str>    label to be used when naming the constraint
			* ``snap``              <bool>   When the constraint is activated, should it be via 'Snap'(True) or 'Active'(False)

		*Returns:*
			* ``none``
		"""
		# find the parent constraints
		constraints = [ constraint['constraint'] for name, constraint in self.constraints.iteritems() if constraint_label in name ]
		if constraints:
			for constraint in constraints:
				# animate constraints weights
				for prop in constraint.PropertyList:
					if ".Weight" in prop.Name:
						prop.Data = 0.0
						prop.SetAnimated( True )

				# create/set relation constraint
				side         = self._extract_side_from_name( constraint.LongName, constraint_label )
				r_name       = self._create_new_constraint_name( constraint, label )
				# r_name       = "{0}:{1}".format( ":".join( label, constraint.LongName.split(":")[:-1] ) )
				r_constraint = vmobu.core.create_constraint( "Relation", long_name=r_name )
				assert isinstance( r_constraint, pyfbsdk.FBConstraintRelation )
				self.constraints[ r_constraint.LongName ] = { 'constraint':constraint, 'snap':snap }

				# Create function boxes for relation constraint
				vector_to_number        = r_constraint.CreateFunctionBox( 'Converters','Vector to Number' )
				is_greater_or_equal_a   = r_constraint.CreateFunctionBox( 'Number',    'Is Greater or Equal (a >= b)' )
				divide_a                = r_constraint.CreateFunctionBox( 'Number',    'Divide (a/b)' )
				subtract_a              = r_constraint.CreateFunctionBox( 'Number',    'Subtract (a - b)' )
				is_greater_or_equal_b   = r_constraint.CreateFunctionBox( 'Number',    'Is Greater or Equal (a >= b)' )
				scale_and_offset_a      = r_constraint.CreateFunctionBox( 'Number',    'Scale And Offset (Number)' )
				is_greater_or_equal_c   = r_constraint.CreateFunctionBox( 'Number',    'Is Greater or Equal (a >= b)' )
				divide_b                = r_constraint.CreateFunctionBox( 'Number',    'Divide (a/b)' )
				scale_and_offset_b      = r_constraint.CreateFunctionBox( 'Number',    'Scale And Offset (Number)' )
				is_greater_or_equal_d   = r_constraint.CreateFunctionBox( 'Number',    'Is Greater or Equal (a >= b)' )
				add_a                   = r_constraint.CreateFunctionBox( 'Number',    'Add (a + b)' )
				divide_c                = r_constraint.CreateFunctionBox( 'Number',    'Divide (a/b)' )
				subtract_b              = r_constraint.CreateFunctionBox( 'Number',    'Subtract (a - b)' )
				scale_and_offset_c      = r_constraint.CreateFunctionBox( 'Number',    'Scale And Offset (Number)' )
				if_cond_a               = r_constraint.CreateFunctionBox( 'Number',    'IF Cond Then A Else B' )
				add_b                   = r_constraint.CreateFunctionBox( 'Number',    'Add (a + b)' )
				is_greater_or_equal_e   = r_constraint.CreateFunctionBox( 'Number',    'Is Greater or Equal (a >= b)' )
				divide_d                = r_constraint.CreateFunctionBox( 'Number',    'Divide (a/b)' )
				scale_and_offset_d      = r_constraint.CreateFunctionBox( 'Number',    'Scale And Offset (Number)' )
				if_cond_b               = r_constraint.CreateFunctionBox( 'Number',    'IF Cond Then A Else B' )
				if_cond_c               = r_constraint.CreateFunctionBox( 'Number',    'IF Cond Then A Else B' )
				if_cond_d               = r_constraint.CreateFunctionBox( 'Number',    'IF Cond Then A Else B' )
				if_cond_e               = r_constraint.CreateFunctionBox( 'Number',    'IF Cond Then A Else B' )
				if_cond_f               = r_constraint.CreateFunctionBox( 'Number',    'IF Cond Then A Else B' )
				is_greater_a 				= r_constraint.CreateFunctionBox( 'Number',    'Is Greater (a > b)'		)
				is_greater_b 				= r_constraint.CreateFunctionBox( 'Number',    'Is Greater (a > b)'		)
				is_greater_c 				= r_constraint.CreateFunctionBox( 'Number',    'Is Greater (a > b)'		)
				is_greater_d 				= r_constraint.CreateFunctionBox( 'Number', 	  'Is Greater (a > b)'		)
				is_greater_e 				= r_constraint.CreateFunctionBox( 'Number', 	  'Is Greater (a > b)'		)
				is_less_or_equal_a		= r_constraint.CreateFunctionBox( 'Number',    'Is Less or Equal (a <= b)' )
				and_a							= r_constraint.CreateFunctionBox( 'Boolean',	  'AND'							)
				and_b 						= r_constraint.CreateFunctionBox( 'Boolean',	  'AND'							)
				or_a 							= r_constraint.CreateFunctionBox( 'Boolean',	  'OR'							)
				or_b 							= r_constraint.CreateFunctionBox( 'Boolean',	  'OR'							)
				or_c 							= r_constraint.CreateFunctionBox( 'Boolean',   'OR'							)
				or_d 							= r_constraint.CreateFunctionBox( 'Boolean',   'OR'							)

				# eg: side + out_node_name == 'LeftLeg'
				out_node = self._filtered_get_obj_by_wildcard( self.namespace, '*{0}{1}'.format( side, out_node_name ),  reject=['Ctrl','tag','Up'] )[0]
				source_sender_out_node = r_constraint.SetAsSource( out_node )
				source_sender_out_node.UseGlobalTransforms = False

				master_node = vmobu.core.get_top_node_of_hierarchy(out_node)
				p_rig_version = master_node.PropertyList.Find('p_rig_version')

				source_sender_out                   = vmobu.core.get_node_connection( source_sender_out_node,'Lcl Rotation','out' ) # was 'Lcl Rotation', but didn't have it

				vector_to_number_v_in               = vmobu.core.get_node_connection( vector_to_number,      'V' )
				if p_rig_version.Data < 2:
					vector_to_number_out             = vmobu.core.get_node_connection( vector_to_number,      'Z',            'out' )
				else:
					if out_node_name == 'Leg' or out_node_name == 'Foot':
						vector_to_number_out 			= vmobu.core.get_node_connection( vector_to_number, 		'Z', 				 'out' )
					elif out_node_name == 'ForeArm':
						vector_to_number_out 			= vmobu.core.get_node_connection( vector_to_number, 		'Y', 				 'out' )

					vector_to_number_x_out				= vmobu.core.get_node_connection( vector_to_number,		'X',				'out' )

				is_greater_or_equal_a_a_in          = vmobu.core.get_node_connection( is_greater_or_equal_a, 'a' )
				is_greater_or_equal_a_b_in          = vmobu.core.get_node_connection( is_greater_or_equal_a, 'b' )
				is_greater_or_equal_a_result_out    = vmobu.core.get_node_connection( is_greater_or_equal_a, 'Result',      'out' )

				divide_a_a_in                       = vmobu.core.get_node_connection( divide_a,              'a' )
				divide_a_b_in                       = vmobu.core.get_node_connection( divide_a,              'b' )
				divide_a_result_out                 = vmobu.core.get_node_connection( divide_a,              'Result',      'out' )

				subtract_a_a_in                     = vmobu.core.get_node_connection( subtract_a,            'a' )
				subtract_a_b_in                     = vmobu.core.get_node_connection( subtract_a,            'b' )
				subtract_a_result_out               = vmobu.core.get_node_connection( subtract_a,            'Result',      'out' )

				is_greater_or_equal_b_a_in          = vmobu.core.get_node_connection( is_greater_or_equal_b, 'a' )
				is_greater_or_equal_b_b_in          = vmobu.core.get_node_connection( is_greater_or_equal_b, 'b' )
				is_greater_or_equal_b_result_out    = vmobu.core.get_node_connection( is_greater_or_equal_b, 'Result',      'out' )

				scale_and_offset_a_offset_in        = vmobu.core.get_node_connection( scale_and_offset_a,    'Offset' )
				scale_and_offset_a_scale_factor_in  = vmobu.core.get_node_connection( scale_and_offset_a,    'Scale Factor' )
				scale_and_offset_a_x_in             = vmobu.core.get_node_connection( scale_and_offset_a,    'X' )
				scale_and_offset_a_result_out       = vmobu.core.get_node_connection( scale_and_offset_a,    'Result',      'out' )

				is_greater_or_equal_c_a_in          = vmobu.core.get_node_connection( is_greater_or_equal_c, 'a' )
				is_greater_or_equal_c_b_in          = vmobu.core.get_node_connection( is_greater_or_equal_c, 'b' )
				is_greater_or_equal_c_result_out    = vmobu.core.get_node_connection( is_greater_or_equal_c, 'Result',      'out' )

				divide_b_a_in                       = vmobu.core.get_node_connection( divide_b,              'a' )
				divide_b_b_in                       = vmobu.core.get_node_connection( divide_b,              'b' )
				divide_b_result_out                 = vmobu.core.get_node_connection( divide_b,              'Result',      'out' )

				scale_and_offset_b_offset_in        = vmobu.core.get_node_connection( scale_and_offset_b,    'Offset' )
				scale_and_offset_b_scale_factor_in  = vmobu.core.get_node_connection( scale_and_offset_b,    'Scale Factor' )
				scale_and_offset_b_x_in             = vmobu.core.get_node_connection( scale_and_offset_b,    'X' )
				scale_and_offset_b_result_out       = vmobu.core.get_node_connection( scale_and_offset_b,    'Result',      'out' )

				is_greater_or_equal_d_a_in          = vmobu.core.get_node_connection( is_greater_or_equal_d, 'a' )
				is_greater_or_equal_d_b_in          = vmobu.core.get_node_connection( is_greater_or_equal_d, 'b' )
				is_greater_or_equal_d_result_out    = vmobu.core.get_node_connection( is_greater_or_equal_d, 'Result',      'out' )

				add_a_a_in                          = vmobu.core.get_node_connection( add_a,                 'a' )
				add_a_b_in                          = vmobu.core.get_node_connection( add_a,                 'b' )
				add_a_result_out                    = vmobu.core.get_node_connection( add_a,                 'Result',      'out' )

				divide_c_a_in                       = vmobu.core.get_node_connection( divide_c,              'a' )
				divide_c_b_in                       = vmobu.core.get_node_connection( divide_c,              'b' )
				divide_c_result_out                 = vmobu.core.get_node_connection( divide_c,              'Result',      'out' )

				subtract_b_a_in                     = vmobu.core.get_node_connection( subtract_b,            'a' )
				subtract_b_b_in                     = vmobu.core.get_node_connection( subtract_b,            'b' )
				subtract_b_result_out               = vmobu.core.get_node_connection( subtract_b,            'Result',      'out' )

				scale_and_offset_c_offset_in        = vmobu.core.get_node_connection( scale_and_offset_c,    'Offset' )
				scale_and_offset_c_scale_factor_in  = vmobu.core.get_node_connection( scale_and_offset_c,    'Scale Factor' )
				scale_and_offset_c_x_in             = vmobu.core.get_node_connection( scale_and_offset_c,    'X' )
				scale_and_offset_c_result_out       = vmobu.core.get_node_connection( scale_and_offset_c,    'Result',      'out' )

				if_cond_a_a_in                      = vmobu.core.get_node_connection( if_cond_a,             'a' )
				if_cond_a_b_in                      = vmobu.core.get_node_connection( if_cond_a,             'b' )
				if_cond_a_cond_in                   = vmobu.core.get_node_connection( if_cond_a,             'Cond' )
				if_cond_a_result_out                = vmobu.core.get_node_connection( if_cond_a,             'Result',      'out' )

				add_b_a_in                          = vmobu.core.get_node_connection( add_b,                 'a' )
				add_b_b_in                          = vmobu.core.get_node_connection( add_b,                 'b' )
				add_b_result_out                    = vmobu.core.get_node_connection( add_b,                 'Result',      'out' )

				is_greater_or_equal_e_a_in          = vmobu.core.get_node_connection( is_greater_or_equal_e, 'a' )
				is_greater_or_equal_e_b_in          = vmobu.core.get_node_connection( is_greater_or_equal_e, 'b' )
				is_greater_or_equal_e_result_out    = vmobu.core.get_node_connection( is_greater_or_equal_e, 'Result',      'out' )

				divide_d_a_in                       = vmobu.core.get_node_connection( divide_d,              'a' )
				divide_d_b_in                       = vmobu.core.get_node_connection( divide_d,              'b' )
				divide_d_result_out                 = vmobu.core.get_node_connection( divide_d,              'Result',      'out' )

				scale_and_offset_d_offset_in        = vmobu.core.get_node_connection( scale_and_offset_d,    'Offset' )
				scale_and_offset_d_scale_factor_in  = vmobu.core.get_node_connection( scale_and_offset_d,    'Scale Factor' )
				scale_and_offset_d_x_in             = vmobu.core.get_node_connection( scale_and_offset_d,    'X' )
				scale_and_offset_d_result_out       = vmobu.core.get_node_connection( scale_and_offset_d,    'Result',      'out' )

				if_cond_b_a_in                      = vmobu.core.get_node_connection( if_cond_b,             'a' )
				if_cond_b_b_in                      = vmobu.core.get_node_connection( if_cond_b,             'b' )
				if_cond_b_cond_in                   = vmobu.core.get_node_connection( if_cond_b,             'Cond' )
				if_cond_b_result_out                = vmobu.core.get_node_connection( if_cond_b,             'Result',      'out' )

				if_cond_c_a_in                      = vmobu.core.get_node_connection( if_cond_c,             'a' )
				if_cond_c_b_in                      = vmobu.core.get_node_connection( if_cond_c,             'b' )
				if_cond_c_result_out                = vmobu.core.get_node_connection( if_cond_c,             'Result',      'out' )

				if_cond_d_a_in                      = vmobu.core.get_node_connection( if_cond_d,             'a' )
				if_cond_d_b_in                      = vmobu.core.get_node_connection( if_cond_d,             'b' )
				if_cond_d_cond_in                   = vmobu.core.get_node_connection( if_cond_d,             'Cond' )
				if_cond_d_result_out                = vmobu.core.get_node_connection( if_cond_d,             'Result',      'out' )

				if_cond_e_a_in                      = vmobu.core.get_node_connection( if_cond_e,             'a' )
				if_cond_e_b_in                      = vmobu.core.get_node_connection( if_cond_e,             'b' )
				if_cond_e_cond_in                   = vmobu.core.get_node_connection( if_cond_e,             'Cond' )
				if_cond_e_result_out                = vmobu.core.get_node_connection( if_cond_e,             'Result',      'out' )

				if_cond_f_a_in                      = vmobu.core.get_node_connection( if_cond_f,             'a' )
				if_cond_f_b_in                      = vmobu.core.get_node_connection( if_cond_f,             'b' )
				if_cond_f_cond_in                   = vmobu.core.get_node_connection( if_cond_f,             'Cond' )
				if_cond_f_result_out                = vmobu.core.get_node_connection( if_cond_f,             'Result',      'out' )

				is_greater_a_a_in							= vmobu.core.get_node_connection( is_greater_a,				'a' )
				is_greater_a_b_in 						= vmobu.core.get_node_connection( is_greater_a,				'b' )
				is_greater_a_result_out 				= vmobu.core.get_node_connection( is_greater_a,				'Result',		'out' )

				is_greater_b_a_in 						= vmobu.core.get_node_connection( is_greater_b, 			'a')
				is_greater_b_b_in 						= vmobu.core.get_node_connection( is_greater_b, 			'b')
				is_greater_b_result_out 				= vmobu.core.get_node_connection( is_greater_b, 			'Result', 'out')

				is_greater_c_a_in 						= vmobu.core.get_node_connection( is_greater_c, 			'a')
				is_greater_c_b_in 						= vmobu.core.get_node_connection( is_greater_c, 			'b')
				is_greater_c_result_out 				= vmobu.core.get_node_connection( is_greater_c, 			'Result', 'out')

				is_greater_d_a_in 						= vmobu.core.get_node_connection(is_greater_d, 'a')
				is_greater_d_b_in 						= vmobu.core.get_node_connection(is_greater_d, 'b')
				is_greater_d_result_out 				= vmobu.core.get_node_connection(is_greater_d, 'Result', 'out')

				is_greater_e_a_in 						= vmobu.core.get_node_connection(is_greater_e, 'a')
				is_greater_e_b_in 						= vmobu.core.get_node_connection(is_greater_e, 'b')
				is_greater_e_result_out 				= vmobu.core.get_node_connection(is_greater_e, 'Result', 'out')

				is_less_or_equal_a_a_in					= vmobu.core.get_node_connection( is_less_or_equal_a,		'a' )
				is_less_or_equal_a_b_in					= vmobu.core.get_node_connection( is_less_or_equal_a,		'b' )
				is_less_or_equal_a_result_out			= vmobu.core.get_node_connection( is_less_or_equal_a,		'Result', 'out' )

				and_a_a_in									= vmobu.core.get_node_connection( and_a,						'a' )
				and_a_b_in									= vmobu.core.get_node_connection( and_a,						'b' )
				and_a_result_out 							= vmobu.core.get_node_connection( and_a,						'Result',	'out' )

				and_b_a_in									= vmobu.core.get_node_connection( and_b,						'a' )
				and_b_b_in									= vmobu.core.get_node_connection( and_b,						'b' )
				and_b_result_out 							= vmobu.core.get_node_connection( and_b,						'Result',	'out' )

				or_a_a_in 									= vmobu.core.get_node_connection( or_a,						'a' )
				or_a_b_in 									= vmobu.core.get_node_connection( or_a,						'b' )
				or_a_result_out 							= vmobu.core.get_node_connection( or_a,						'Result',	'out' )

				or_b_a_in	 								= vmobu.core.get_node_connection( or_b, 						'a')
				or_b_b_in 									= vmobu.core.get_node_connection( or_b, 						'b')
				or_b_result_out		 					= vmobu.core.get_node_connection( or_b, 						'Result', 'out')

				or_c_a_in 									= vmobu.core.get_node_connection(or_c, 'a')
				or_c_b_in 									= vmobu.core.get_node_connection(or_c, 'b')
				or_c_result_out 							= vmobu.core.get_node_connection(or_c, 'Result', 'out')

				or_d_a_in 									= vmobu.core.get_node_connection(or_d, 'a')
				or_d_b_in 									= vmobu.core.get_node_connection(or_d, 'b')
				or_d_result_out 							= vmobu.core.get_node_connection(or_d, 'Result', 'out')

				constraint_box = r_constraint.ConstrainObject( constraint )

				pos_const_weight_a = constraint.ReferenceGet( 1, 0 )
				pos_const_weight_b = constraint.ReferenceGet( 1, 1 )
				pos_const_weight_c = constraint.ReferenceGet( 1, 2 )

				pos_a_in = vmobu.core.get_node_connection( constraint_box, '{0}.Weight'.format( pos_const_weight_a.LongName ) )
				pos_b_in = vmobu.core.get_node_connection( constraint_box, '{0}.Weight'.format( pos_const_weight_b.LongName ) )
				if pos_const_weight_c:
					pos_c_in = vmobu.core.get_node_connection( constraint_box, '{0}.Weight'.format( pos_const_weight_c.LongName ) )

				vmobu.core.evaluate()

				# Set values for specific function box inputs (specific to this relation constraint)
				if p_rig_version.Data < 2 or out_node_name == 'Leg':
					is_greater_or_equal_a_a_in.WriteData(           [ -45.0  ] )
					divide_a_b_in.WriteData(                        [ -45.0  ] )
					if_cond_b_b_in.WriteData(                       [ 100.0  ] )
					scale_and_offset_a_offset_in.WriteData(         [ 100.0  ] )
					scale_and_offset_a_scale_factor_in.WriteData(   [ -100.0 ] )
					if_cond_a_a_in.WriteData(                       [ 0.0    ] )
					is_greater_or_equal_b_a_in.WriteData(           [ -90.0  ] )
					is_greater_or_equal_c_a_in.WriteData(           [ -45.0  ] )
					divide_b_b_in.WriteData(                        [ -45.0  ] )
					scale_and_offset_b_offset_in.WriteData(         [ -100.0 ] )
					scale_and_offset_b_scale_factor_in.WriteData(   [ 100.0  ] )
					add_a_a_in.WriteData(                           [ 90.0   ] )
					divide_c_b_in.WriteData(                        [ -90.0  ] )
					subtract_b_b_in.WriteData(                      [ 1.0    ] )
					scale_and_offset_c_offset_in.WriteData(         [ -100.0 ] )
					scale_and_offset_c_scale_factor_in.WriteData(   [ -100.0 ] )
					if_cond_c_a_in.WriteData(                       [ 100.0  ] )
					if_cond_d_b_in.WriteData(                       [ 0.0    ] )
					add_b_a_in.WriteData(                           [ 90.0   ] )
					divide_d_b_in.WriteData(                        [ -90.0  ] )
					scale_and_offset_d_offset_in.WriteData(         [ 0.0    ] )
					scale_and_offset_d_scale_factor_in.WriteData(   [ 100.0  ] )
					if_cond_f_b_in.WriteData(                       [ 0.0    ] )
					is_greater_or_equal_e_a_in.WriteData(           [ -90.0  ] )
					is_greater_or_equal_d_a_in.WriteData(           [ -100.0 ] )
					subtract_a_b_in.WriteData(                      [ 1.0    ] )

					vmobu.core.evaluate()

					# Make the connections of the inputs and outputs
					result = list() #just a simple debugger tool to quickly see if anything fails
					result.append(pyfbsdk.FBConnect(source_sender_out, vector_to_number_v_in))
					result.append(pyfbsdk.FBConnect(vector_to_number_out, is_greater_or_equal_a_b_in))
					result.append(pyfbsdk.FBConnect(is_greater_or_equal_a_result_out, if_cond_b_cond_in))
					result.append(pyfbsdk.FBConnect(if_cond_b_result_out, pos_a_in))
					result.append(pyfbsdk.FBConnect(vector_to_number_out, divide_a_a_in))
					result.append(pyfbsdk.FBConnect(divide_a_result_out, subtract_a_a_in))
					result.append(pyfbsdk.FBConnect(subtract_a_result_out, scale_and_offset_a_x_in))
					result.append(pyfbsdk.FBConnect(scale_and_offset_a_result_out, if_cond_a_b_in))
					result.append(pyfbsdk.FBConnect(if_cond_a_result_out, if_cond_b_a_in))
					result.append(pyfbsdk.FBConnect(vector_to_number_out, is_greater_or_equal_b_b_in))
					result.append(pyfbsdk.FBConnect(is_greater_or_equal_b_result_out, if_cond_a_cond_in))
					result.append(pyfbsdk.FBConnect(vector_to_number_out, is_greater_or_equal_c_b_in))
					result.append(pyfbsdk.FBConnect(is_greater_or_equal_c_result_out, if_cond_e_cond_in))
					result.append(pyfbsdk.FBConnect(if_cond_e_result_out, pos_b_in))
					result.append(pyfbsdk.FBConnect(vector_to_number_out, divide_b_a_in))
					result.append(pyfbsdk.FBConnect(divide_b_result_out, scale_and_offset_b_x_in))
					result.append(pyfbsdk.FBConnect(scale_and_offset_b_result_out, if_cond_e_a_in))
					result.append(pyfbsdk.FBConnect(vector_to_number_out, add_a_b_in))
					result.append(pyfbsdk.FBConnect(add_a_result_out, divide_c_a_in))
					result.append(pyfbsdk.FBConnect(divide_c_result_out, subtract_b_a_in))
					result.append(pyfbsdk.FBConnect(subtract_b_result_out, scale_and_offset_c_x_in))
					result.append(pyfbsdk.FBConnect(scale_and_offset_c_result_out, if_cond_c_b_in))
					result.append(pyfbsdk.FBConnect(if_cond_c_result_out, if_cond_d_a_in))
					result.append(pyfbsdk.FBConnect(if_cond_d_result_out, if_cond_e_b_in))
					result.append(pyfbsdk.FBConnect(vector_to_number_out, add_b_b_in))
					result.append(pyfbsdk.FBConnect(add_b_result_out, divide_d_a_in))
					result.append(pyfbsdk.FBConnect(divide_d_result_out, scale_and_offset_d_x_in))
					result.append(pyfbsdk.FBConnect(scale_and_offset_d_result_out, if_cond_f_a_in))
					result.append(pyfbsdk.FBConnect(if_cond_f_result_out, pos_c_in))
					result.append(pyfbsdk.FBConnect(vector_to_number_out, is_greater_or_equal_e_b_in))
					result.append(pyfbsdk.FBConnect(is_greater_or_equal_e_result_out, if_cond_f_cond_in))
					result.append(pyfbsdk.FBConnect(vector_to_number_out, is_greater_or_equal_d_b_in))
					result.append(pyfbsdk.FBConnect(is_greater_or_equal_d_result_out, if_cond_d_cond_in))

				elif out_node_name == 'ForeArm':
					#15
					is_greater_or_equal_a_b_in.WriteData(				[ 45.0	] )
					divide_a_b_in.WriteData(								[ 45.0	] )
					if_cond_b_a_in.WriteData(								[ 0.0		] )
					scale_and_offset_a_offset_in.WriteData(			[ 100.0	] )
					scale_and_offset_a_scale_factor_in.WriteData(	[ -100.0	] )
					if_cond_a_a_in.WriteData(								[ 0.0		] )
					#16
					is_greater_or_equal_b_b_in.WriteData(				[ 90.0	] )
					#17
					is_greater_or_equal_c_b_in.WriteData(				[ 45.0	] )
					divide_b_b_in.WriteData(								[ -45.0	] )
					scale_and_offset_b_offset_in.WriteData(			[ -100.0	] )
					scale_and_offset_b_scale_factor_in.WriteData(	[ -100.0	] )
					add_a_a_in.WriteData(									[ 90.0	] )
					divide_c_b_in.WriteData(								[ -90.0	] )
					subtract_b_b_in.WriteData(								[ 1.0		] )
					scale_and_offset_c_offset_in.WriteData(			[ -100.0	] )
					scale_and_offset_c_scale_factor_in.WriteData(	[ -100.0	] )
					if_cond_c_a_in.WriteData(								[ 100.0	] )
					if_cond_d_a_in.WriteData(								[ 0.0		] )
					add_b_a_in.WriteData(									[ 90.0	] )
					divide_d_b_in.WriteData(								[ -90.0	] )
					scale_and_offset_d_offset_in.WriteData(			[ -20.0	] )
					scale_and_offset_d_scale_factor_in.WriteData(	[ -20.0	] )
					if_cond_f_b_in.WriteData(								[ 0.0		] )
					#18
					is_greater_or_equal_e_b_in.WriteData(				[ 90.0	] )
					#19
					is_greater_or_equal_d_a_in.WriteData(				[ 100.0	] )
					subtract_a_b_in.WriteData(								[ 1.0		] )

					is_greater_a_b_in.WriteData(							[ 90.0	] )
					is_greater_b_b_in.WriteData(							[ 90.0	] )
					is_greater_c_b_in.WriteData(							[ 90.0	] )
					is_greater_d_a_in.WriteData(							[ -140.0 ] )
					is_greater_e_a_in.WriteData(							[ -140.0 ] )
					is_less_or_equal_a_b_in.WriteData(					[ 90.0	] )

					vmobu.core.evaluate()

					# Make the connections of the inputs and outputs
					result = list() #just a simple debugger tool to quickly see if anything fails
					result.append(pyfbsdk.FBConnect(source_sender_out, vector_to_number_v_in))
					result.append(pyfbsdk.FBConnect(vector_to_number_out, is_greater_or_equal_a_a_in))

					#Depending on the side, the connections into the greater than checks of the X are swapped
					result.append(pyfbsdk.FBConnect(vector_to_number_x_out, is_greater_a_a_in))
					result.append(pyfbsdk.FBConnect(vector_to_number_x_out, is_greater_b_a_in))
					result.append(pyfbsdk.FBConnect(vector_to_number_x_out, is_greater_c_a_in))

					result.append(pyfbsdk.FBConnect(is_greater_or_equal_a_result_out, and_a_a_in))
					result.append(pyfbsdk.FBConnect(is_greater_a_result_out, and_a_b_in))
					result.append(pyfbsdk.FBConnect(and_a_result_out, or_a_a_in))
					result.append(pyfbsdk.FBConnect(is_greater_b_result_out, or_a_b_in))
					result.append(pyfbsdk.FBConnect(vector_to_number_x_out, is_greater_d_b_in))
					result.append(pyfbsdk.FBConnect(is_greater_d_result_out, or_c_b_in))
					result.append(pyfbsdk.FBConnect(or_a_result_out, or_c_a_in))
					result.append(pyfbsdk.FBConnect(or_c_result_out, if_cond_b_cond_in))
					result.append(pyfbsdk.FBConnect(vector_to_number_out, divide_a_a_in))
					result.append(pyfbsdk.FBConnect(divide_a_result_out, subtract_a_a_in))
					result.append(pyfbsdk.FBConnect(subtract_a_result_out, scale_and_offset_a_x_in))
					result.append(pyfbsdk.FBConnect(scale_and_offset_a_result_out, if_cond_a_b_in))
					result.append(pyfbsdk.FBConnect(if_cond_a_result_out, if_cond_b_b_in))
					result.append(pyfbsdk.FBConnect(vector_to_number_out, is_greater_or_equal_b_a_in))
					result.append(pyfbsdk.FBConnect(is_greater_or_equal_b_result_out, if_cond_a_cond_in))
					result.append(pyfbsdk.FBConnect(vector_to_number_out, is_greater_or_equal_c_a_in))
					result.append(pyfbsdk.FBConnect(is_greater_or_equal_c_result_out, if_cond_e_cond_in))
					result.append(pyfbsdk.FBConnect(vector_to_number_out, divide_b_a_in))
					result.append(pyfbsdk.FBConnect(divide_b_result_out, scale_and_offset_b_x_in))
					result.append(pyfbsdk.FBConnect(scale_and_offset_b_result_out, if_cond_e_a_in))
					result.append(pyfbsdk.FBConnect(vector_to_number_out, add_a_b_in))
					result.append(pyfbsdk.FBConnect(add_a_result_out, divide_c_a_in))
					result.append(pyfbsdk.FBConnect(divide_c_result_out, subtract_b_a_in))
					result.append(pyfbsdk.FBConnect(subtract_b_result_out, scale_and_offset_c_x_in))
					result.append(pyfbsdk.FBConnect(scale_and_offset_c_result_out, if_cond_c_b_in))
					result.append(pyfbsdk.FBConnect(if_cond_c_result_out, if_cond_d_b_in))
					result.append(pyfbsdk.FBConnect(if_cond_d_result_out, if_cond_e_b_in))
					result.append(pyfbsdk.FBConnect(vector_to_number_out, add_b_b_in))
					result.append(pyfbsdk.FBConnect(add_b_result_out, divide_d_a_in))
					result.append(pyfbsdk.FBConnect(divide_d_result_out, scale_and_offset_d_x_in))
					result.append(pyfbsdk.FBConnect(scale_and_offset_d_result_out, if_cond_f_a_in))
					result.append(pyfbsdk.FBConnect(vector_to_number_out, is_greater_or_equal_e_a_in))
					result.append(pyfbsdk.FBConnect(vector_to_number_out, is_less_or_equal_a_a_in))
					result.append(pyfbsdk.FBConnect(is_greater_or_equal_e_result_out, and_b_a_in))
					result.append(pyfbsdk.FBConnect(is_less_or_equal_a_result_out, and_b_b_in))
					result.append(pyfbsdk.FBConnect(and_b_result_out, or_b_a_in))
					result.append(pyfbsdk.FBConnect(vector_to_number_x_out, is_greater_e_b_in))
					result.append(pyfbsdk.FBConnect(is_greater_e_result_out, or_d_b_in))
					result.append(pyfbsdk.FBConnect(is_greater_c_result_out, or_b_b_in))
					result.append(pyfbsdk.FBConnect(or_b_result_out, or_d_a_in))
					result.append(pyfbsdk.FBConnect(or_d_result_out, if_cond_f_cond_in))
					result.append(pyfbsdk.FBConnect(vector_to_number_out, is_greater_or_equal_d_b_in))
					result.append(pyfbsdk.FBConnect(is_greater_or_equal_d_result_out, if_cond_d_cond_in))

					pyfbsdk.FBSystem().Scene.Evaluate()

					result.append(pyfbsdk.FBConnect(if_cond_b_result_out, pos_a_in))
					result.append(pyfbsdk.FBConnect(if_cond_e_result_out, pos_b_in))
					result.append(pyfbsdk.FBConnect(if_cond_f_result_out, pos_c_in))
				elif out_node_name == 'Foot' and p_rig_version.Data >= 4 :
					#15
					is_greater_or_equal_a_b_in.WriteData(				[ 15.0	] )
					divide_a_b_in.WriteData(								[ 15.0	] )
					if_cond_b_a_in.WriteData(								[ 0.0		] )
					scale_and_offset_a_offset_in.WriteData(			[ 100.0	] )
					scale_and_offset_a_scale_factor_in.WriteData(	[ -100.0	] )
					if_cond_a_a_in.WriteData(								[ 0.0		] )
					#16
					is_greater_or_equal_b_b_in.WriteData(				[ 55.0	] )
					#17
					is_greater_or_equal_c_b_in.WriteData(				[ 15.0	] )
					divide_b_b_in.WriteData(								[ -15.0	] )
					scale_and_offset_b_offset_in.WriteData(			[ -100.0	] )
					scale_and_offset_b_scale_factor_in.WriteData(	[ -100.0	] )
					add_a_a_in.WriteData(									[ 55.0	] )
					divide_c_b_in.WriteData(								[ -55.0	] )
					subtract_b_b_in.WriteData(								[ 1.0		] )
					scale_and_offset_c_offset_in.WriteData(			[ -100.0	] )
					scale_and_offset_c_scale_factor_in.WriteData(	[ -100.0	] )
					if_cond_c_a_in.WriteData(								[ 100.0	] )
					if_cond_d_a_in.WriteData(								[ 0.0		] )
					add_b_a_in.WriteData(									[ 55.0	] )
					divide_d_b_in.WriteData(								[ -55.0	] )
					scale_and_offset_d_offset_in.WriteData(			[ -20.0	] )
					scale_and_offset_d_scale_factor_in.WriteData(	[ -20.0	] )
					if_cond_f_b_in.WriteData(								[ 0.0		] )
					#18
					is_greater_or_equal_e_b_in.WriteData(				[ 55.0	] )
					#19
					is_greater_or_equal_d_a_in.WriteData(				[ 100.0	] )
					subtract_a_b_in.WriteData(								[ 1.0		] )

					is_greater_a_b_in.WriteData(							[ 55.0	] )
					is_greater_b_b_in.WriteData(							[ 55.0	] )
					is_greater_c_b_in.WriteData(							[ 55.0	] )
					is_greater_d_a_in.WriteData(							[ -100.0 ] )
					is_greater_e_a_in.WriteData(							[ -100.0 ] )
					is_less_or_equal_a_b_in.WriteData(					[ 55.0	] )

					vmobu.core.evaluate()

					# Make the connections of the inputs and outputs
					result = list() #just a simple debugger tool to quickly see if anything fails
					result.append(pyfbsdk.FBConnect(source_sender_out, vector_to_number_v_in))
					result.append(pyfbsdk.FBConnect(vector_to_number_out, is_greater_or_equal_a_a_in))

					#Depending on the side, the connections into the greater than checks of the X are swapped
					result.append(pyfbsdk.FBConnect(vector_to_number_x_out, is_greater_a_a_in))
					result.append(pyfbsdk.FBConnect(vector_to_number_x_out, is_greater_b_a_in))
					result.append(pyfbsdk.FBConnect(vector_to_number_x_out, is_greater_c_a_in))

					result.append(pyfbsdk.FBConnect(is_greater_or_equal_a_result_out, and_a_a_in))
					result.append(pyfbsdk.FBConnect(is_greater_a_result_out, and_a_b_in))
					result.append(pyfbsdk.FBConnect(and_a_result_out, or_a_a_in))
					result.append(pyfbsdk.FBConnect(is_greater_b_result_out, or_a_b_in))
					result.append(pyfbsdk.FBConnect(vector_to_number_x_out, is_greater_d_b_in))
					result.append(pyfbsdk.FBConnect(is_greater_d_result_out, or_c_b_in))
					result.append(pyfbsdk.FBConnect(or_a_result_out, or_c_a_in))
					result.append(pyfbsdk.FBConnect(or_c_result_out, if_cond_b_cond_in))
					result.append(pyfbsdk.FBConnect(vector_to_number_out, divide_a_a_in))
					result.append(pyfbsdk.FBConnect(divide_a_result_out, subtract_a_a_in))
					result.append(pyfbsdk.FBConnect(subtract_a_result_out, scale_and_offset_a_x_in))
					result.append(pyfbsdk.FBConnect(scale_and_offset_a_result_out, if_cond_a_b_in))
					result.append(pyfbsdk.FBConnect(if_cond_a_result_out, if_cond_b_b_in))
					result.append(pyfbsdk.FBConnect(vector_to_number_out, is_greater_or_equal_b_a_in))
					result.append(pyfbsdk.FBConnect(is_greater_or_equal_b_result_out, if_cond_a_cond_in))
					result.append(pyfbsdk.FBConnect(vector_to_number_out, is_greater_or_equal_c_a_in))
					result.append(pyfbsdk.FBConnect(is_greater_or_equal_c_result_out, if_cond_e_cond_in))
					result.append(pyfbsdk.FBConnect(vector_to_number_out, divide_b_a_in))
					result.append(pyfbsdk.FBConnect(divide_b_result_out, scale_and_offset_b_x_in))
					result.append(pyfbsdk.FBConnect(scale_and_offset_b_result_out, if_cond_e_a_in))
					result.append(pyfbsdk.FBConnect(vector_to_number_out, add_a_b_in))
					result.append(pyfbsdk.FBConnect(add_a_result_out, divide_c_a_in))
					result.append(pyfbsdk.FBConnect(divide_c_result_out, subtract_b_a_in))
					result.append(pyfbsdk.FBConnect(subtract_b_result_out, scale_and_offset_c_x_in))
					result.append(pyfbsdk.FBConnect(scale_and_offset_c_result_out, if_cond_c_b_in))
					result.append(pyfbsdk.FBConnect(if_cond_c_result_out, if_cond_d_b_in))
					result.append(pyfbsdk.FBConnect(if_cond_d_result_out, if_cond_e_b_in))
					result.append(pyfbsdk.FBConnect(vector_to_number_out, add_b_b_in))
					result.append(pyfbsdk.FBConnect(add_b_result_out, divide_d_a_in))
					result.append(pyfbsdk.FBConnect(divide_d_result_out, scale_and_offset_d_x_in))
					result.append(pyfbsdk.FBConnect(scale_and_offset_d_result_out, if_cond_f_a_in))
					result.append(pyfbsdk.FBConnect(vector_to_number_out, is_greater_or_equal_e_a_in))
					result.append(pyfbsdk.FBConnect(vector_to_number_out, is_less_or_equal_a_a_in))
					result.append(pyfbsdk.FBConnect(is_greater_or_equal_e_result_out, and_b_a_in))
					result.append(pyfbsdk.FBConnect(is_less_or_equal_a_result_out, and_b_b_in))
					result.append(pyfbsdk.FBConnect(and_b_result_out, or_b_a_in))
					result.append(pyfbsdk.FBConnect(vector_to_number_x_out, is_greater_e_b_in))
					result.append(pyfbsdk.FBConnect(is_greater_e_result_out, or_d_b_in))
					result.append(pyfbsdk.FBConnect(is_greater_c_result_out, or_b_b_in))
					result.append(pyfbsdk.FBConnect(or_b_result_out, or_d_a_in))
					result.append(pyfbsdk.FBConnect(or_d_result_out, if_cond_f_cond_in))
					result.append(pyfbsdk.FBConnect(vector_to_number_out, is_greater_or_equal_d_b_in))
					result.append(pyfbsdk.FBConnect(is_greater_or_equal_d_result_out, if_cond_d_cond_in))

					pyfbsdk.FBSystem().Scene.Evaluate()

					result.append(pyfbsdk.FBConnect(if_cond_b_result_out, pos_a_in))
					result.append(pyfbsdk.FBConnect(if_cond_e_result_out, pos_b_in))
					#result.append(pyfbsdk.FBConnect(if_cond_f_result_out, pos_c_in))


			vmobu.core.evaluate()

	# noinspection PyArgumentList
	def create_upper_armroll_constraint(self, limb_bone_pattern, limb_roll_pattern, armtwist_pattern, reject=None, snap=True, mute=[], label='Procedural' ):
		"""
		Creates and returns a new 'upper armroll constraint'(s)

		*Arguments:*
			* ``limb_bone_pattern`` <str>   e.e. '*Arm'
			* ``limb_roll_pattern`` <str>   e.g. '*ArmRoll'
			* ``armtwist_pattern``  <str>   e.g. '*ArmTwist'

		*Keyword Arguments:*
			* ``reject``            <list> or <tuple>, e.g. ('tag','Ctrl')
			* ``snap``              <bool>   When the constraint is activated, should it be via 'Snap'(True) or 'Active'(False)
			* ``label``             <str>    label to be used when naming the constraint

		*Returns:*
			* ``none``
		"""
		result = [] # to be returned

		limb_bone_key  = limb_bone_pattern.replace( "*", "" )
		limb_roll_key  = limb_roll_pattern.replace( "*", "" )
		armtwist_key   = armtwist_pattern.replace( "*", "" )

		limb_bones  = self._filtered_get_obj_by_wildcard( self.namespace, limb_bone_pattern,   reject=reject )
		limb_rolls  = self._filtered_get_obj_by_wildcard( self.namespace, limb_roll_pattern,   reject=reject )
		armtwists   = self._filtered_get_obj_by_wildcard( self.namespace, armtwist_pattern,    reject=reject )
		self.object_cache[ limb_bone_key ]  = [ obj for obj in limb_bones if isinstance( obj, pyfbsdk.FBModelSkeleton ) ]
		self.object_cache[ limb_roll_key ]  = [ obj for obj in limb_rolls if isinstance( obj, pyfbsdk.FBModelSkeleton ) ]
		self.object_cache[ armtwist_key ]   = [ obj for obj in armtwists  if isinstance( obj, pyfbsdk.FBModelSkeleton ) ]

		# mute specific properties on the roll bones
		for roll in self.object_cache[ limb_roll_key ]:
			vmobu.core.mute_property_members( roll, 'Lcl Rotation', (1,2) )

		# create and setup the Relation constraint here...
		for limb_bone in self.object_cache[ limb_bone_key ]:
			# constraint = vmobu.core.create_constraint( 'Relation', long_name="{1}:{0}".format( limb_bone.LongName, label ) )
			constraint = vmobu.core.create_constraint( 'Relation', long_name=self._create_new_constraint_name( limb_bone, label ) )
			assert isinstance( constraint, pyfbsdk.FBConstraintRelation )
			self.constraints[ constraint.LongName ] = {'constraint':constraint, 'snap':snap }
			side = self._extract_side_from_name( limb_bone.LongName, limb_bone_key )

			vector_to_number_box1 = constraint.CreateFunctionBox( 'Converters',  'Vector to Number'            )
			divide_box1				 = constraint.CreateFunctionBox( 'Number',		'Divide (a/b)'						)
			scale_and_offset_box1 = constraint.CreateFunctionBox( 'Number',		'Scale And Offset (Number)'	)
			scale_and_offset_box2 = constraint.CreateFunctionBox( 'Number', 		'Scale And Offset (Number)'	)
			scale_and_offset_box3 = constraint.CreateFunctionBox( 'Number', 		'Scale And Offset (Number)'	)
			is_greater_or_equal_box1 = constraint.CreateFunctionBox( 'Number',	'Is Greater or Equal (a >= b)'	)
			is_less_or_equal_box1 =	constraint.CreateFunctionBox( 'Number',		'Is Less or Equal (a <= b)'		)
			if_cond_box1			 =	constraint.CreateFunctionBox( 'Number',		'IF Cond Then A Else B'			)
			if_cond_box2 			 = constraint.CreateFunctionBox( 'Number', 		'IF Cond Then A Else B'			)
			number_to_vector_box1 = constraint.CreateFunctionBox( 'Converters',  'Number to Vector'            )

			source_sender_out_node = constraint.SetAsSource( limb_bone )
			source_sender_out_node.UseGlobalTransforms = False
			source_sender_out = vmobu.core.get_node_connection(         source_sender_out_node, 'Lcl Rotation',  'out' )


			for twist in self.object_cache[ armtwist_key ]:
				if side in twist.Name:
					twist_bone = twist
					if mute:
						vmobu.core.mute_property_members(twist, 'Lcl Rotation', (mute))

					cobject_result_in_node = constraint.ConstrainObject( twist )
					cobject_result_in_node.UseGlobalTransforms = False
					cobject_result_in = vmobu.core.get_node_connection(  cobject_result_in_node, 'Lcl Rotation' )

			vector_to_number_box1_v_in             = vmobu.core.get_node_connection( vector_to_number_box1, 'V' )
			vector_to_number_box1_x_out            = vmobu.core.get_node_connection( vector_to_number_box1, 'X',              'out' )
			vector_to_number_box1_y_out 				= vmobu.core.get_node_connection( vector_to_number_box1, 'Y', 					'out')
			vector_to_number_box1_z_out 				= vmobu.core.get_node_connection( vector_to_number_box1, 'Z', 					'out')

			divide_box1_a_in								= vmobu.core.get_node_connection( divide_box1,				'a' )
			divide_box1_b_in								= vmobu.core.get_node_connection( divide_box1,				'b' )
			divide_box1_result_out						= vmobu.core.get_node_connection( divide_box1,				'Result',			'out' )

			scale_and_offset_box1_scale_factor_in	= vmobu.core.get_node_connection( scale_and_offset_box1, 'Scale Factor' )
			scale_and_offset_box1_offset_in			= vmobu.core.get_node_connection( scale_and_offset_box1, 'Offset'			)
			scale_and_offset_box1_clamp_max_in		= vmobu.core.get_node_connection( scale_and_offset_box1,	'Clamp Max'		)
			scale_and_offset_box1_clamp_min_in 		= vmobu.core.get_node_connection( scale_and_offset_box1, 'Clamp Min'		)
			scale_and_offset_box1_x_in					= vmobu.core.get_node_connection( scale_and_offset_box1,	'X'				)
			scale_and_offset_box1_result_out			= vmobu.core.get_node_connection( scale_and_offset_box1,	'Result',			'out' )

			scale_and_offset_box2_scale_factor_in 	= vmobu.core.get_node_connection(scale_and_offset_box2, 'Scale Factor')
			scale_and_offset_box2_offset_in 			= vmobu.core.get_node_connection(scale_and_offset_box2, 'Offset'		)
			scale_and_offset_box2_clamp_max_in		= vmobu.core.get_node_connection(scale_and_offset_box2,'Clamp Max'		)
			scale_and_offset_box2_clamp_min_in 		= vmobu.core.get_node_connection( scale_and_offset_box2,'Clamp Min'		)
			scale_and_offset_box2_x_in					= vmobu.core.get_node_connection(scale_and_offset_box2,	'X'				)
			scale_and_offset_box2_result_out			= vmobu.core.get_node_connection( scale_and_offset_box2,	'Result',			'out' )

			scale_and_offset_box3_scale_factor_in 	= vmobu.core.get_node_connection(scale_and_offset_box3, 'Scale Factor')
			scale_and_offset_box3_offset_in 			= vmobu.core.get_node_connection(scale_and_offset_box3, 'Offset'		)
			scale_and_offset_box3_clamp_max_in		= vmobu.core.get_node_connection(scale_and_offset_box3,'Clamp Max'		)
			scale_and_offset_box3_clamp_min_in 		= vmobu.core.get_node_connection( scale_and_offset_box3,'Clamp Min'		)
			scale_and_offset_box3_x_in					= vmobu.core.get_node_connection(scale_and_offset_box3,	'X'				)
			scale_and_offset_box3_result_out			= vmobu.core.get_node_connection( scale_and_offset_box3,	'Result',			'out' )

			is_greater_or_equal_box1_a_in				= vmobu.core.get_node_connection( is_greater_or_equal_box1, 'a'		)
			is_greater_or_equal_box1_b_in				= vmobu.core.get_node_connection( is_greater_or_equal_box1, 'b'		)
			is_greater_or_equal_box1_result_out		= vmobu.core.get_node_connection( is_greater_or_equal_box1, 'Result',			'out'	)

			is_less_or_equal_box1_a_in					= vmobu.core.get_node_connection( is_less_or_equal_box1, 'a'			)
			is_less_or_equal_box1_b_in					= vmobu.core.get_node_connection( is_less_or_equal_box1, 'b'			)
			is_less_or_equal_box1_result_out			= vmobu.core.get_node_connection( is_less_or_equal_box1, 'Result',				'out'	)

			if_cond_box1_a_in								= vmobu.core.get_node_connection( if_cond_box1, 'a'						)
			if_cond_box1_b_in								= vmobu.core.get_node_connection( if_cond_box1, 'b'						)
			if_cond_box1_cond_in							= vmobu.core.get_node_connection( if_cond_box1, 'Cond'					)
			if_cond_box1_result_out						= vmobu.core.get_node_connection( if_cond_box1, 'Result',							'out'	)

			if_cond_box2_a_in	 							= vmobu.core.get_node_connection( if_cond_box2, 'a'						)
			if_cond_box2_b_in								= vmobu.core.get_node_connection( if_cond_box2, 'b'						)
			if_cond_box2_cond_in							= vmobu.core.get_node_connection( if_cond_box2, 'Cond'					)
			if_cond_box2_result_out						= vmobu.core.get_node_connection( if_cond_box2, 'Result',							'out'	)

			number_to_vector_box1_x_in             = vmobu.core.get_node_connection( number_to_vector_box1, 'X' )
			number_to_vector_box1_y_in 				= vmobu.core.get_node_connection( number_to_vector_box1, 'Y' )
			number_to_vector_box1_z_in 				= vmobu.core.get_node_connection( number_to_vector_box1, 'Z' )
			number_to_vector_box1_result_out       = vmobu.core.get_node_connection( number_to_vector_box1, 'Result',         'out' )

			master_node = vmobu.core.get_top_node_of_hierarchy(limb_bone)
			p_rig_version = master_node.PropertyList.Find('p_rig_version')

			if not p_rig_version.Data < 2:
				if side == 'Left':
					scale_and_offset_box1_scale_factor_in.WriteData([-1.0])
				elif side == 'Right':
					scale_and_offset_box1_scale_factor_in.WriteData([-1.0])
			else:
				scale_and_offset_box1_scale_factor_in.WriteData([-1.0])
				if side == 'Left':
					divide_box1_b_in.WriteData([1.0])
				elif side == 'Right':
					divide_box1_b_in.WriteData([-1.0])

			scale_and_offset_box1_clamp_max_in.WriteData([60.0])
			scale_and_offset_box1_clamp_min_in.WriteData([-30.0])

			if source_sender_out and cobject_result_in:
				#pyfbsdk.FBConnect( source_sender_out,                 vector_to_number_box1_v_in )
				#pyfbsdk.FBConnect( vector_to_number_box1_x_out,       scale_and_offset_box1_x_in )
				#pyfbsdk.FBConnect( scale_and_offset_box1_result_out,	number_to_vector_box1_x_in )
				#pyfbsdk.FBConnect( vector_to_number_box1_y_out,			number_to_vector_box1_y_in )
				#pyfbsdk.FBConnect( vector_to_number_box1_z_out, 		number_to_vector_box1_z_in )
				#pyfbsdk.FBConnect( vector_to_number_box1_z_out,			divide_box1_a_in				)
				#if not p_rig_version.Data > 1:
				#	pyfbsdk.FBConnect( divide_box1_result_out,				scale_and_offset_box1_offset_in )
				#pyfbsdk.FBConnect( number_to_vector_box1_result_out,  cobject_result_in          )

				#New addition
				scale_and_offset_box2_clamp_max_in.WriteData([30.0])
				scale_and_offset_box2_clamp_min_in.WriteData([-30.0])
				scale_and_offset_box2_scale_factor_in.WriteData([-0.5])

				scale_and_offset_box3_clamp_max_in.WriteData([60.0])
				scale_and_offset_box3_clamp_min_in.WriteData([-60.0])
				scale_and_offset_box3_scale_factor_in.WriteData([-0.2])

				is_greater_or_equal_box1_b_in.WriteData([90.0])

				is_less_or_equal_box1_b_in.WriteData([-120.0])

				pyfbsdk.FBConnect(source_sender_out, vector_to_number_box1_v_in)
				pyfbsdk.FBConnect(vector_to_number_box1_x_out, scale_and_offset_box1_x_in)
				pyfbsdk.FBConnect(vector_to_number_box1_y_out, number_to_vector_box1_y_in)
				pyfbsdk.FBConnect(vector_to_number_box1_z_out, number_to_vector_box1_z_in)
				pyfbsdk.FBConnect(vector_to_number_box1_z_out, divide_box1_a_in			)
				if not p_rig_version.Data > 1:
					pyfbsdk.FBConnect( divide_box1_result_out,				scale_and_offset_box1_offset_in )

				pyfbsdk.FBConnect(	vector_to_number_box1_x_out, 		scale_and_offset_box2_x_in	)
				pyfbsdk.FBConnect(	vector_to_number_box1_x_out, 		scale_and_offset_box3_x_in	)
				pyfbsdk.FBConnect(	vector_to_number_box1_x_out,		is_greater_or_equal_box1_a_in )
				pyfbsdk.FBConnect(	vector_to_number_box1_x_out,		is_less_or_equal_box1_a_in	)
				pyfbsdk.FBConnect(	is_greater_or_equal_box1_result_out, if_cond_box1_cond_in	)
				pyfbsdk.FBConnect(	is_less_or_equal_box1_result_out, if_cond_box2_cond_in		)
				pyfbsdk.FBConnect(	if_cond_box2_result_out,			if_cond_box1_b_in				)
				pyfbsdk.FBConnect(	scale_and_offset_box1_result_out, if_cond_box2_b_in			)
				pyfbsdk.FBConnect(	scale_and_offset_box2_result_out, if_cond_box1_a_in			)
				pyfbsdk.FBConnect(	scale_and_offset_box3_result_out, if_cond_box2_a_in			)
				#pyfbsdk.FBConnect(	if_cond_box1_result_out,			number_to_vector_box1_x_in	)
				pyfbsdk.FBConnect( 	number_to_vector_box1_result_out,  cobject_result_in        )

			self.create_additive_twist_constraint( constraint, twist_bone, '{0}Arm'.format( side ), if_cond_box1_result_out, number_to_vector_box1_x_in, control_label=twist_bone.Name )
			vmobu.core.evaluate()

			result.append( constraint )

		return result

	# noinspection PyArgumentList
	def create_forearm_roll_constraint(self, forearm_pattern, forearm_roll_pattern, hand_pattern, reject=('Ctrl',), snap=True, label='Procedural' ):
		"""
		Creates and returns a new 'forearm roll constraint'(s)

		*Arguments:*
			* ``forearm_pattern``      <str>   e.e. '*ForeArm'
			* ``forearm_roll_pattern`` <str>   e.g. '*ForeArmRoll'
			* ``hand_pattern``         <str>   e.g. '*Hand'

		*Keyword Arguments:*
			* ``reject``            <list> or <tuple>, e.g. ('tag','Ctrl')
			* ``snap``              <bool>   When the constraint is activated, should it be via 'Snap'(True) or 'Active'(False)
			* ``label``             <str>    label to be used when naming the constraint

		*Returns:*
			* ``none``
		"""
		result = [] # to be returned

		forearm_key       = forearm_pattern.replace( "*", "" )
		forearm_roll_key  = forearm_roll_pattern.replace( "*", "" )
		hand_key          = hand_pattern.replace( "*", "" )

		forearms       = self._filtered_get_obj_by_wildcard( self.namespace, forearm_pattern,           reject=reject )
		forearm_rolls  = self._filtered_get_obj_by_wildcard( self.namespace, forearm_roll_pattern,      reject=reject )
		hands          = self._filtered_get_obj_by_wildcard( self.namespace, hand_pattern,              reject=reject )
		self.object_cache[ forearm_key ]       = [ obj for obj in forearms      if isinstance( obj, pyfbsdk.FBModelSkeleton ) ]
		self.object_cache[ forearm_roll_key ]  = [ obj for obj in forearm_rolls if isinstance( obj, pyfbsdk.FBModelSkeleton ) ]
		self.object_cache[ hand_key ]          = [ obj for obj in hands         if isinstance( obj, pyfbsdk.FBModelSkeleton ) ]

		# mute specific properties on the forearm_roll bones
		for obj in self.object_cache[ forearm_roll_key ]:
			vmobu.core.mute_property_members( obj, 'Lcl Rotation', (1,2) )

		# create and setup the Relation constraint here...
		for forearm in self.object_cache[ forearm_key ]:
			# constraint = vmobu.core.create_constraint( 'Relation', long_name="{1}:{0}".format( forearm.LongName, label ) )
			constraint = vmobu.core.create_constraint( 'Relation', long_name=self._create_new_constraint_name( forearm, label ) )
			assert isinstance( constraint, pyfbsdk.FBConstraintRelation )
			self.constraints[ constraint.LongName ] = {'constraint':constraint, 'snap':snap }
			side = self._extract_side_from_name( forearm.LongName, forearm_key )

			for forearm_roll in self.object_cache[ forearm_roll_key ]:
				forearm_roll.SetVector
				if side in forearm_roll.Name:
					cobject_result_in_node = constraint.ConstrainObject( forearm_roll )
					cobject_result_in_node.UseGlobalTransforms = False
					cobject_result_in = vmobu.core.get_node_connection( cobject_result_in_node, 'Lcl Rotation' )

					vector_to_number_box = constraint.CreateFunctionBox( 'Converters',   'Vector to Number'   )
					is_less_box				= constraint.CreateFunctionBox( 'Number',			'Is Less (a < b)' 	)
					scale_and_offset_box = constraint.CreateFunctionBox( 'Number', 		'Scale And Offset (Number)' )
					if_cond_box				= constraint.CreateFunctionBox( 'Number',			'IF Cond Then A Else B' )
					multiply_box         = constraint.CreateFunctionBox( 'Number',       'Multiply (a x b)'   )
					number_to_vector_box = constraint.CreateFunctionBox( 'Converters',   'Number to Vector'   )


					for hand in self.object_cache[ hand_key ]:
						if side in hand.Name:
							source_sender_out_node = constraint.SetAsSource( hand )
							source_sender_out_node.UseGlobalTransforms = False
							source_sender_out = vmobu.core.get_node_connection( source_sender_out_node, 'Lcl Rotation',  'out' )

					vector_to_number_box_v_in              = vmobu.core.get_node_connection( vector_to_number_box,     'V'                  )
					vector_to_number_box_x_out             = vmobu.core.get_node_connection( vector_to_number_box,     'X',           'out' )

					is_less_box_a_in								= vmobu.core.get_node_connection( is_less_box,					'a'						)
					is_less_box_b_in								= vmobu.core.get_node_connection( is_less_box,					'b'						)
					is_less_box_result_out						= vmobu.core.get_node_connection( is_less_box,					'Result',		'out' )

					scale_and_offset_box_offset_in			= vmobu.core.get_node_connection( scale_and_offset_box,		'Offset'					)
					scale_and_offset_box_scale_factor_in	= vmobu.core.get_node_connection( scale_and_offset_box,		'Scale Factor'			)
					scale_and_offset_box_x_in					= vmobu.core.get_node_connection( scale_and_offset_box,		'X'						)
					scale_and_offset_box_result_out			= vmobu.core.get_node_connection( scale_and_offset_box,		'Result',		'out' )

					if_cond_box_a_in								= vmobu.core.get_node_connection( if_cond_box,					'a'						)
					if_cond_box_b_in								= vmobu.core.get_node_connection( if_cond_box,					'b'						)
					if_cond_box_cond_in							= vmobu.core.get_node_connection( if_cond_box,					'Cond'					)
					if_cond_box_result_out						= vmobu.core.get_node_connection( if_cond_box,					'Result',		'out' )

					multipy_box_a_in                       = vmobu.core.get_node_connection( multiply_box,             'a'                  )
					multipy_box_b_in                       = vmobu.core.get_node_connection( multiply_box,             'b'                  )
					multiply_box_result_out                = vmobu.core.get_node_connection( multiply_box,             'Result',      'out' )

					number_to_vector_box_x_in              = vmobu.core.get_node_connection( number_to_vector_box,     'X'                  )
					number_to_vector_box_result_out        = vmobu.core.get_node_connection( number_to_vector_box,     'Result',      'out' )

					is_less_box_a_in.WriteData					( [0.0]  )
					multipy_box_b_in.WriteData             ( [0.50] )
					scale_and_offset_box_offset_in.WriteData ( [360.0] )
					scale_and_offset_box_scale_factor_in.WriteData ( [0.50] )

					if source_sender_out and cobject_result_in:
						pyfbsdk.FBConnect( source_sender_out,                 vector_to_number_box_v_in )
						pyfbsdk.FBConnect( vector_to_number_box_x_out,        multipy_box_a_in          )
						pyfbsdk.FBConnect( vector_to_number_box_x_out, 			is_less_box_b_in			  )
						pyfbsdk.FBConnect( vector_to_number_box_x_out, 			scale_and_offset_box_x_in )
						pyfbsdk.FBConnect( scale_and_offset_box_result_out,	if_cond_box_a_in			  )
						pyfbsdk.FBConnect( is_less_box_result_out,				if_cond_box_cond_in		  )
						pyfbsdk.FBConnect( multiply_box_result_out,				if_cond_box_b_in			  )
						pyfbsdk.FBConnect( if_cond_box_result_out,           number_to_vector_box_x_in )
						pyfbsdk.FBConnect( number_to_vector_box_result_out,   cobject_result_in         )


				self.create_additive_twist_constraint(constraint, forearm_roll, forearm, number_to_vector_box_result_out, control_label='{0}_Control'.format( forearm.Name ) )
			vmobu.core.evaluate()

			result.append( constraint )

		return result



	# noinspection PyArgumentList
	def create_upper_leg_roll_constraint(self, upper_leg_pattern, up_leg_roll_pattern, reject=None, snap=True, label='Procedural' ):
		"""
		Creates and returns a new 'upper leg roll constraint'(s).

		*Arguments:*
			* ``upper_leg_pattern``    <str>   e.e. '*UpLeg'
			* ``up_leg_roll_pattern``  <str>   e.g. '*UpLegRoll'

		*Keyword Arguments:*
			* ``reject``            <list> or <tuple>, e.g. ('tag','Ctrl')
			* ``snap``              <bool>   When the constraint is activated, should it be via 'Snap'(True) or 'Active'(False)
			* ``label``             <str>    label to be used when naming the constraint

		*Returns:*
			* ``none``
		"""
		result = [] # to be returned

		upper_leg_key  = upper_leg_pattern.replace( "*", "" )
		up_leg_roll_key= up_leg_roll_pattern.replace( "*", "" )

		upper_legs     = self._filtered_get_obj_by_wildcard( self.namespace, upper_leg_pattern,   reject=reject )
		up_leg_rolls   = self._filtered_get_obj_by_wildcard( self.namespace, up_leg_roll_pattern, reject=reject )
		self.object_cache[ upper_leg_key ]  = [ obj for obj in upper_legs    if isinstance( obj, pyfbsdk.FBModelSkeleton ) ]
		self.object_cache[ up_leg_roll_key ]= [ obj for obj in up_leg_rolls  if isinstance( obj, pyfbsdk.FBModelSkeleton ) ]

		# mute specific properties on the up_leg_roll bones
		for obj in self.object_cache[ up_leg_roll_key ]:
			vmobu.core.mute_property_members( obj, 'Lcl Rotation', (1,2) )

		# create and setup the Relation constraint here...
		for upper_leg in self.object_cache[ upper_leg_key ]:
			constraint = vmobu.core.create_constraint( 'Relation', long_name=self._create_new_constraint_name( upper_leg, label ) )
			# constraint = vmobu.core.create_constraint( 'Relation', long_name="{1}:{0}".format( upper_leg.LongName, label ) )
			assert isinstance( constraint, pyfbsdk.FBConstraintRelation )
			self.constraints[ constraint.LongName ] = {'constraint':constraint, 'snap':snap }
			side = self._extract_side_from_name( upper_leg.LongName, upper_leg_key )

			source_sender_out_node = constraint.SetAsSource( upper_leg )
			source_sender_out_node.UseGlobalTransforms = False
			source_sender_out1 = vmobu.core.get_node_connection( source_sender_out_node, 'Lcl Rotation', 'out' )

			for up_leg_roll in self.object_cache[ up_leg_roll_key ]:
				if side in up_leg_roll.Name:
					roll_bone = up_leg_roll
					cobject_result_in_node = constraint.ConstrainObject( up_leg_roll )
					cobject_result_in_node.UseGlobalTransforms = False
					cobject_result_in = vmobu.core.get_node_connection( cobject_result_in_node, 'Lcl Rotation' )

			vector_to_number_box1            = constraint.CreateFunctionBox( 'Converters', 'Vector to Number'      )
			multiply_box1							= constraint.CreateFunctionBox( 'Number',     'Multiply (a x b)'      )
			scale_and_offset_box1				= constraint.CreateFunctionBox( 'Number', 	 'Scale And Offset (Number)' )
			scale_and_offset_box2 				= constraint.CreateFunctionBox( 'Number', 	 'Scale And Offset (Number)' )
			scale_and_offset_box3 				= constraint.CreateFunctionBox( 'Number', 	 'Scale And Offset (Number)' )
			is_greater_or_equal_box1			= constraint.CreateFunctionBox( 'Number',		 'Is Greater or Equal (a >= b)' )
			is_less_or_equal_box1				= constraint.CreateFunctionBox( 'Number',		 'Is Less or Equal (a <= b)' )
			if_cond_box1							= constraint.CreateFunctionBox( 'Number',		 'IF Cond Then A Else B'	)
			if_cond_box2							= constraint.CreateFunctionBox( 'Number',		 'IF Cond Then A Else B'	)
			number_to_vector_box1            = constraint.CreateFunctionBox( 'Converters', 'Number to Vector'      )

			vector_to_number_box1_v_in       = vmobu.core.get_node_connection( vector_to_number_box1,   'V')
			vector_to_number_box1_x_out      = vmobu.core.get_node_connection( vector_to_number_box1,   'X',      'out' )

			multiply_box1_a_in					= vmobu.core.get_node_connection( multiply_box1,				'a')
			multiply_box1_b_in					= vmobu.core.get_node_connection( multiply_box1,				'b')
			multiply_box1_result_out			= vmobu.core.get_node_connection( multiply_box1,				'Result', 'out' )

			scale_and_offset_box1_offset_in	= vmobu.core.get_node_connection( scale_and_offset_box1, 	'Offset' )
			scale_and_offset_box1_x_in			= vmobu.core.get_node_connection( scale_and_offset_box1, 	'X' )
			scale_and_offset_box1_scale_in	= vmobu.core.get_node_connection( scale_and_offset_box1,		'Scale Factor' )
			scale_and_offset_box1_clamp_max_in = vmobu.core.get_node_connection( scale_and_offset_box1, 	'Clamp Max'		)
			scale_and_offset_box1_clamp_min_in = vmobu.core.get_node_connection( scale_and_offset_box1,	'Clamp Min'		)
			scale_and_offset_box1_result_out = vmobu.core.get_node_connection( scale_and_offset_box1, 	'Result', 'out' )

			scale_and_offset_box2_offset_in 	= vmobu.core.get_node_connection(scale_and_offset_box2, 'Offset')
			scale_and_offset_box2_x_in 		= vmobu.core.get_node_connection(scale_and_offset_box2, 'X')
			scale_and_offset_box2_scale_in 	= vmobu.core.get_node_connection(scale_and_offset_box2, 'Scale Factor')
			scale_and_offset_box2_clamp_max_in = vmobu.core.get_node_connection(scale_and_offset_box2, 'Clamp Max'	)
			scale_and_offset_box2_clamp_min_in = vmobu.core.get_node_connection( scale_and_offset_box2,	'Clamp Min'		)
			scale_and_offset_box2_result_out = vmobu.core.get_node_connection(scale_and_offset_box2, 'Result', 'out')

			scale_and_offset_box3_offset_in 	= vmobu.core.get_node_connection(scale_and_offset_box3, 'Offset')
			scale_and_offset_box3_x_in 		= vmobu.core.get_node_connection(scale_and_offset_box3, 'X')
			scale_and_offset_box3_scale_in 	= vmobu.core.get_node_connection(scale_and_offset_box3, 'Scale Factor')
			scale_and_offset_box3_clamp_max_in = vmobu.core.get_node_connection(scale_and_offset_box3, 'Clamp Max'	)
			scale_and_offset_box3_clamp_min_in = vmobu.core.get_node_connection( scale_and_offset_box3,	'Clamp Min'		)
			scale_and_offset_box3_result_out = vmobu.core.get_node_connection(scale_and_offset_box3, 'Result', 'out')

			is_greater_or_equal_box1_a_in		= vmobu.core.get_node_connection( is_greater_or_equal_box1, 'a'	)
			is_greater_or_equal_box1_b_in		= vmobu.core.get_node_connection( is_greater_or_equal_box1, 'b'	)
			is_greater_or_equal_box1_result_out = vmobu.core.get_node_connection( is_greater_or_equal_box1, 'Result', 'out' )

			is_less_or_equal_box1_a_in			= vmobu.core.get_node_connection( is_less_or_equal_box1, 'a'	)
			is_less_or_equal_box1_b_in			= vmobu.core.get_node_connection( is_less_or_equal_box1, 'b'	)
			is_less_or_equal_box1_result_out = vmobu.core.get_node_connection( is_less_or_equal_box1, 'Result', 'out')

			if_cond_box1_a_in						= vmobu.core.get_node_connection( if_cond_box1, 'a'	)
			if_cond_box1_b_in						= vmobu.core.get_node_connection( if_cond_box1, 'b'	)
			if_cond_box1_cond_in					= vmobu.core.get_node_connection( if_cond_box1, 'Cond' )
			if_cond_box1_result_out				= vmobu.core.get_node_connection( if_cond_box1, 'Result', 'out' )

			if_cond_box2_a_in 					= vmobu.core.get_node_connection( if_cond_box2, 'a')
			if_cond_box2_b_in 					= vmobu.core.get_node_connection( if_cond_box2, 'b')
			if_cond_box2_cond_in 				= vmobu.core.get_node_connection( if_cond_box2, 'Cond')
			if_cond_box2_result_out 			= vmobu.core.get_node_connection( if_cond_box2, 'Result', 'out')

			number_to_vector_box1_x_in       = vmobu.core.get_node_connection( number_to_vector_box1,   'X')
			number_to_vector_box1_result_out = vmobu.core.get_node_connection( number_to_vector_box1,   'Result', 'out' )

			master_node = vmobu.core.get_top_node_of_hierarchy(upper_leg)
			p_rig_version = master_node.PropertyList.Find('p_rig_version')

			if not p_rig_version.Data < 1:
				scale_and_offset_box1_scale_in.WriteData([-1.0])
			else:
				multiply_box1_b_in.WriteData(		[ -2.0 ]  )

			scale_and_offset_box1_clamp_max_in.WriteData([60.0])
			scale_and_offset_box1_clamp_min_in.WriteData([-60.0])
			scale_and_offset_box2_clamp_max_in.WriteData([60.0])
			scale_and_offset_box2_clamp_min_in.WriteData([-60.0])
			scale_and_offset_box2_scale_in.WriteData([0.0])
			scale_and_offset_box3_clamp_max_in.WriteData([60.0])
			scale_and_offset_box3_clamp_min_in.WriteData([-60.0])
			scale_and_offset_box3_scale_in.WriteData([0.0])

			is_greater_or_equal_box1_b_in.WriteData([120.0])

			is_less_or_equal_box1_b_in.WriteData([-120.0])

			if source_sender_out1 and cobject_result_in:
				pyfbsdk.FBConnect( source_sender_out1,                vector_to_number_box1_v_in )
				pyfbsdk.FBConnect( vector_to_number_box1_x_out,			multiply_box1_a_in			)
				pyfbsdk.FBConnect( vector_to_number_box1_x_out,			scale_and_offset_box1_x_in )
				pyfbsdk.FBConnect( vector_to_number_box1_x_out,			scale_and_offset_box2_x_in )
				pyfbsdk.FBConnect( vector_to_number_box1_x_out, 		scale_and_offset_box3_x_in )
				pyfbsdk.FBConnect( vector_to_number_box1_x_out,			is_greater_or_equal_box1_a_in )
				pyfbsdk.FBConnect( vector_to_number_box1_x_out,			is_less_or_equal_box1_a_in )
				pyfbsdk.FBConnect( is_greater_or_equal_box1_result_out, if_cond_box1_cond_in		)
				pyfbsdk.FBConnect( is_less_or_equal_box1_result_out,	if_cond_box2_cond_in			)
				pyfbsdk.FBConnect( scale_and_offset_box1_result_out,	if_cond_box2_b_in				)
				pyfbsdk.FBConnect( if_cond_box2_result_out,				if_cond_box1_b_in				)
				pyfbsdk.FBConnect( scale_and_offset_box2_result_out,	if_cond_box1_a_in				)
				pyfbsdk.FBConnect( scale_and_offset_box3_result_out,	if_cond_box2_a_in				)
				#pyfbsdk.FBConnect( if_cond_box1_result_out,				number_to_vector_box1_x_in	)
				#if not p_rig_version.Data > 1:
				#	pyfbsdk.FBConnect( multiply_box1_result_out,				scale_and_offset_box1_offset_in )
				#pyfbsdk.FBConnect( scale_and_offset_box1_result_out,	number_to_vector_box1_x_in )
				pyfbsdk.FBConnect( number_to_vector_box1_result_out,  cobject_result_in          )

			vmobu.core.evaluate()

			self.create_additive_twist_constraint( constraint, roll_bone, '{0}UpLeg'.format( side ),if_cond_box1_result_out, number_to_vector_box1_x_in, roll_bone.Name )

			result.append( constraint )

		return result

	# noinspection PyArgumentList
	def create_lower_leg_roll_constraint(self, leg_roll_pattern, foot_pattern, reject=None, snap=True, label='Procedural' ):
		"""
		Creates and returns a new 'lower leg roll constraint'(s).

		*Arguments:*
			* ``leg_roll_pattern``  <str>   e.g. '*LegRoll'
			* ``foot_pattern``      <str>   e.g. '*Foot'

		*Keyword Arguments:*
			* ``reject``            <list> or <tuple>, e.g. ('tag','Ctrl')
			* ``snap``              <bool>   When the constraint is activated, should it be via 'Snap'(True) or 'Active'(False)
			* ``label``             <str>    label to be used when naming the constraint

		*Returns:*
			* ``none``
		"""
		result = [] # to be returned

		leg_roll_key  = leg_roll_pattern.replace( "*", "" )
		foot_key      = foot_pattern.replace( "*", "" )

		leg_rolls= self._filtered_get_obj_by_wildcard( self.namespace, leg_roll_pattern, reject=reject )
		feet     = self._filtered_get_obj_by_wildcard( self.namespace, foot_pattern,     reject=reject )
		self.object_cache[ leg_roll_key ]= [ obj for obj in leg_rolls  if isinstance( obj, pyfbsdk.FBModelSkeleton ) ]
		self.object_cache[ foot_key ]    = [ obj for obj in feet       if isinstance( obj, pyfbsdk.FBModelSkeleton ) ]

		# create and setup the Relation constraint here...
		for leg_roll in self.object_cache[ leg_roll_key ]:
			# constraint = vmobu.core.create_constraint( 'Relation', long_name="{1}:{0}".format( leg_roll.LongName, label ) )
			constraint = vmobu.core.create_constraint( 'Relation', long_name=self._create_new_constraint_name( leg_roll, label ) )
			side = self._extract_side_from_name( leg_roll.LongName, leg_roll_key )

			cobject_result_in_node = constraint.ConstrainObject( leg_roll )
			cobject_result_in_node.UseGlobalTransforms = False
			cobject_result_in = vmobu.core.get_node_connection( cobject_result_in_node, 'Lcl Rotation' )

			for foot in self.object_cache[ foot_key ]:
				if side in foot.Name:
					roll_foot = foot
					source_sender_out_node = constraint.SetAsSource( foot )
					source_sender_out_node.UseGlobalTransforms = False
					source_sender_out = vmobu.core.get_node_connection( source_sender_out_node, 'Lcl Rotation', 'out' )

			vector_to_number_box1                  = constraint.CreateFunctionBox( 'Converters',   'Vector to Number'            )
			multiply_box1									= constraint.CreateFunctionBox(	'Number',		'Multiply (a x b)'				)
			number_to_vector_box1                  = constraint.CreateFunctionBox( 'Converters',   'Number to Vector'            )

			vector_to_number_box1_v_in             = vmobu.core.get_node_connection( vector_to_number_box1, 'V'                  )
			vector_to_number_box1_x_out            = vmobu.core.get_node_connection( vector_to_number_box1, 'X', 'out'           )

			multiply_box1_a_in							= vmobu.core.get_node_connection( multiply_box1, 'a'									)
			multiply_box1_b_in							= vmobu.core.get_node_connection( multiply_box1, 'b'									)
			multiply_box1_result_out					= vmobu.core.get_node_connection( multiply_box1, 'Result', 'out'					)

			number_to_vector_box1_x_in             = vmobu.core.get_node_connection( number_to_vector_box1, 'X'                  )
			number_to_vector_box1_result_out       = vmobu.core.get_node_connection( number_to_vector_box1, 'Result', 'out'      )

			multiply_box1_b_in.WriteData( [0.5] )

			if source_sender_out and cobject_result_in:
				pyfbsdk.FBConnect( source_sender_out, 						vector_to_number_box1_v_in		)
				pyfbsdk.FBConnect( vector_to_number_box1_x_out, 		multiply_box1_a_in 				)
				#pyfbsdk.FBConnect( multiply_box1_result_out, 			number_to_vector_box1_x_in 	)
				pyfbsdk.FBConnect( number_to_vector_box1_result_out, 	cobject_result_in 				)

			self.constraints[ constraint.LongName ] = {'constraint':constraint, 'snap':snap }
			vmobu.core.evaluate()

			self.create_additive_twist_constraint( constraint, leg_roll, '{0}Leg'.format( side ), multiply_box1_result_out, number_to_vector_box1_x_in, control_label=leg_roll.Name )

			result.append( constraint )

		return result

	# noinspection PyArgumentList
	def create_foot_twist_constraint(self, foot_twist_pattern, foot_pattern, reject=None, snap=True, label='Procedural' ):
		"""
		Creates and returns a new 'lower leg roll constraint'(s).

		*Arguments:*
			* ``foot_twist_pattern``  <str>   e.g. '*FootTwist'
			* ``foot_pattern``      <str>   e.g. '*Foot'

		*Keyword Arguments:*
			* ``reject``            <list> or <tuple>, e.g. ('tag','Ctrl')
			* ``snap``              <bool>   When the constraint is activated, should it be via 'Snap'(True) or 'Active'(False)
			* ``label``             <str>    label to be used when naming the constraint

		*Returns:*
			* ``none``
		"""
		result = [] # to be returned

		foot_twist_key  = foot_twist_pattern.replace( "*", "" )
		foot_key      = foot_pattern.replace( "*", "" )

		foot_twists = self._filtered_get_obj_by_wildcard( self.namespace, foot_twist_pattern, reject = reject )
		feet     = self._filtered_get_obj_by_wildcard( self.namespace, foot_pattern,     reject = reject )
		self.object_cache[ foot_twist_key ]= [ obj for obj in foot_twists  if isinstance( obj, pyfbsdk.FBModelSkeleton ) ]
		self.object_cache[ foot_key ]    = [ obj for obj in feet       if isinstance( obj, pyfbsdk.FBModelSkeleton ) ]

		if self.object_cache[ foot_twist_key ] and self.object_cache[ foot_key ]:

			# create and setup the Relation constraint here...
			for foot_twist in self.object_cache[ foot_twist_key ]:
				# constraint = vmobu.core.create_constraint( 'Relation', long_name="{1}:{0}".format( foot_twist.LongName, label ) )
				constraint = vmobu.core.create_constraint( 'Relation', long_name=self._create_new_constraint_name( foot_twist, label ) )
				side = self._extract_side_from_name( foot_twist.LongName, foot_twist_key )

				cobject_result_in_node = constraint.ConstrainObject( foot_twist )
				cobject_result_in_node.UseGlobalTransforms = False
				cobject_result_in = vmobu.core.get_node_connection( cobject_result_in_node, 'Lcl Rotation' )

				for foot in self.object_cache[ foot_key ]:
					if side in foot.Name:
						roll_foot = foot
						source_sender_out_node = constraint.SetAsSource( foot )
						source_sender_out_node.UseGlobalTransforms = False
						source_sender_out = vmobu.core.get_node_connection( source_sender_out_node, 'Lcl Rotation', 'out' )

				vector_to_number_box1                  = constraint.CreateFunctionBox( 'Converters',   'Vector to Number'            )
				multiply_box1									= constraint.CreateFunctionBox(	'Number',		'Multiply (a x b)'				)
				multiply_box2									= constraint.CreateFunctionBox(	'Number',		'Multiply (a x b)'				)
				multiply_box3									= constraint.CreateFunctionBox(	'Number',		'Multiply (a x b)'				)
				greater_than_equal_to_box1	= constraint.CreateFunctionBox( 'Number', 'Is Less or Equal (a <= b)' )
				number_to_vector_box1                  = constraint.CreateFunctionBox( 'Converters',   'Number to Vector'            )

				vector_to_number_box1_v_in             = vmobu.core.get_node_connection( vector_to_number_box1, 'V'                  )
				vector_to_number_box1_z_out            = vmobu.core.get_node_connection( vector_to_number_box1, 'Z', 'out'           )

				multiply_box1_a_in							= vmobu.core.get_node_connection( multiply_box1, 'a'									)
				multiply_box1_b_in							= vmobu.core.get_node_connection( multiply_box1, 'b'									)
				multiply_box1_result_out					= vmobu.core.get_node_connection( multiply_box1, 'Result', 'out'					)

				multiply_box2_a_in							= vmobu.core.get_node_connection( multiply_box2, 'a'									)
				multiply_box2_b_in							= vmobu.core.get_node_connection( multiply_box2, 'b'									)
				multiply_box2_result_out					= vmobu.core.get_node_connection( multiply_box2, 'Result', 'out'					)

				greater_than_equal_to_box1_a_in	= vmobu.core.get_node_connection( greater_than_equal_to_box1, 'a'									)
				greater_than_equal_to_box1_b_in	= vmobu.core.get_node_connection( greater_than_equal_to_box1, 'b'									)
				greater_than_equal_to_box1_result_out	= vmobu.core.get_node_connection( greater_than_equal_to_box1, 'Result', 'out'									)

				multiply_box3_a_in							= vmobu.core.get_node_connection( multiply_box3, 'a'									)
				multiply_box3_b_in							= vmobu.core.get_node_connection( multiply_box3, 'b'									)
				multiply_box3_result_out					= vmobu.core.get_node_connection( multiply_box3, 'Result', 'out'					)

				number_to_vector_box1_z_in             = vmobu.core.get_node_connection( number_to_vector_box1, 'Z'                  )
				number_to_vector_box1_result_out       = vmobu.core.get_node_connection( number_to_vector_box1, 'Result', 'out'      )

				multiply_box1_b_in.WriteData( [ -1.0 ] )
				multiply_box2_b_in.WriteData( [ -1.0 ] )
				greater_than_equal_to_box1_b_in.WriteData( [ 0.0 ] )

				if source_sender_out and cobject_result_in:
					pyfbsdk.FBConnect( source_sender_out, 						vector_to_number_box1_v_in		)

					pyfbsdk.FBConnect( vector_to_number_box1_z_out, 		multiply_box1_a_in 				)
					pyfbsdk.FBConnect( vector_to_number_box1_z_out, 		greater_than_equal_to_box1_a_in 				)

					pyfbsdk.FBConnect( multiply_box1_result_out, 		multiply_box3_a_in 				)
					pyfbsdk.FBConnect( greater_than_equal_to_box1_result_out, 		multiply_box3_b_in 				)

					pyfbsdk.FBConnect( multiply_box3_result_out, 			number_to_vector_box1_z_in 	)
					pyfbsdk.FBConnect( number_to_vector_box1_result_out, 	cobject_result_in 				)

				self.constraints[ constraint.LongName ] = {'constraint':constraint, 'snap':snap }
				vmobu.core.evaluate()

				self.create_additive_twist_constraint( constraint, foot_twist, '{0}Foot'.format( side ), multiply_box1_result_out, number_to_vector_box1_z_in, control_label = foot_twist.Name )

				result.append( constraint )

		return result

	def create_optional_constraint( self, constraint_type = None ):
		"""
		Runs the generation of optional constraints.

		Some characters will not have all constraints (peds will be bare bone constraints ) This method could probably be changed/refactored to include a switch statement for those constraints.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``constraint_type`` - type of constraint to build. Types are ['lat', 'scapula']

		*Returns:*
			* ``True`` <bool> upon completion
		"""
		driver_names = []

		# LAT && SCAPULA CONSTRAINTS
		if constraint_type.lower( ) == 'lat' or constraint_type.lower( ) == 'scapula':
			# Get the lat effectors that were made
			effectors = vmobu.core.get_objects_from_wildcard('{0}:Ctrl:*{1}_Effector'.format( self.namespace, constraint_type ), use_namespace = True, single_only = False, models_only= True, case_sensitive= False )
			# Check to see if we got them ( if they exist )
			if not effectors:
				# If not, we don't need to make them for this character
				return False, 'No {0} constraints were made'.format( constraint_type )

			# These are the parents for this constraint
			driver_names = [ 'Arm', 'Spine2' ]

			for effector in effectors:
				# Get side
				side = None
				if 'right' in effector.Name.lower( ):
					side = 'right'
				if 'left' in effector.Name.lower( ):
					side = 'left'

				# We get each effectors parent ( it's holder )
				holder = effector.Parent

				# Make the constraint and add the holder as the driven obj
				constraint = vmobu.core.create_constraint( 'Parent/Child', long_name = self._create_new_constraint_name( holder, 'PosConst' ) ) #'Parent/Child', long_name = self._create_new_constraint_name( holder, 'ParentConst' ) )
				constraint.ReferenceAdd( 0, holder )
				# Find and add the parents to the constraint
				for parent_name in driver_names:
					if 'arm' in parent_name.lower():
						search_string = '{0}:*skel:{1}{2}*'.format( self.namespace, side, parent_name )
					else:
						search_string = '{0}:*skel:{1}*'.format( self.namespace, parent_name )
					parent = vmobu.core.get_objects_from_wildcard( search_string, use_namespace=True, case_sensitive=False, single_only=True, models_only=True )
					if parent:
						constraint.ReferenceAdd( 1, parent )
				constraint.Weight = 50.0

				# Add the constraint to the master constraint list to be turned on later
				self.constraints[ constraint.LongName ] = { 'constraint': constraint, 'snap': True }

		return True

	def run( self ):
		"""
		Runs the constraint builder for the character already specified in self.character, creating the constraints and then activating them.

		*Arguments:*
			* ``none``

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``True`` <bool> upon completion
		"""
		##############################################
		#          CREATE the Constraints            #
		##############################################
		# Ensure that the character has been moved to stance pose.
		self.character.GoToStancePose( )

		### AIM Constraints ---------------------- ###
		self.create_aim_constraint(   '*Arm_UpVector',  '*Shoulder',   '*ForeArm' )

		### POSITION Constraints ------------------- ###
		self.create_position_constraint( '*Knee',                   '*KneeTarget*',  reject=['Ctrl'],     			label='PosConst', animated=True )
		self.create_position_constraint( '*Elbow',                  '*ElbowTarget*', reject=['Ctrl'],     			label='PosConst', animated=True )
		self.create_position_constraint( '*FootArmor',                  '*FootArmorTarget*', reject=['Tag', 'Ctrl'],     			label='PosConst', animated=True )

		vmobu.core.evaluate( )

		### ROTATION CONSTRAINTS ------------------- ###
		self.create_rotation_constraint( '*ForeArmRoll', '*Hand', reject=['Ctrl', 'tag'], label='RotConst', mute=[1, 2], weight=50, roll_constraint = True )
		#self.create_rotation_constraint( '*ArmTwist',					'*Shoulder',	  reject=['Ctrl', 'tag'],		label='RotConst',	affectx=True, 	affecty=False, affectz=False, snap=True)
		#self.create_rotation_constraint(	'*ArmTwist', 					'*Arm', 	  		  reject=['Ctrl', 'tag', 'Fore'], 		label='RotConst', affectx=False, affecty=True, 	affectz=True, 	snap=True)
		self.create_rotation_constraint( '*ArmRoll', 					'*Arm', 	  		  reject=['Ctrl', 'tag', 'Fore'], 		label='RotConst', snap=True, weight=100, roll_constraint = True )

		### PARENT Constraints ------------------- ###
		self.create_position_constraint( '*SpineBend', '*skel:Hips*' )

		### Camera Constraint
		camera_constraint = self.create_position_constraint( '*_skel:Camera', '*_skel:AnimationController', symmetry=False)[ 0 ]

		vmobu.core.evaluate( )

		# Create a Camera look at object
		mobu_camera_target = pyfbsdk.FBModelNull( '{0}:CameraLookAt'.format( self.namespace ) )
		self.create_parent_constraint( '*CameraLookAt', '*skel:AnimationController', symmetry= False)
		mobu_camera_target.Show = True
		# Get the camera from the constraint reference list
		camera = camera_constraint.ReferenceGet( 0, 0 )
		camera.Interest = mobu_camera_target
		self.create_aim_constraint( '*skel:Camera', '*CameraLookAt', None, snap = False )

		### Optional Constraints

		# These methods create the lat/scapula which are optional constraints.
		# They can be passed on within the method if those bones/effectors are not found in the character
		self.create_optional_constraint( constraint_type='scapula' )

		### RELATION Constraints ----------------- ###

		vmobu.core.evaluate( )

		# BEND constraints
		self.create_bend_constraint( 'Knee',   'Leg' )
		self.create_bend_constraint( 'Elbow',  'ForeArm' )
		self.create_bend_constraint( 'FootArmor', 'Foot' )

		vmobu.core.evaluate( )

		# ROLL constraints: arm_rolls, forearm_rolls, leg_rolls, up_leg_rolls
		self.create_upper_armroll_constraint   ( '*Arm',      '*ArmRoll',      '*ArmTwist', reject=['Fore'], mute=[1, 2]  )
		#self.create_forearm_roll_constraint    ( '*ForeArm',  '*ForeArmRoll',  '*Hand'                       )
		self.create_upper_leg_roll_constraint  ( '*UpLeg',    '*UpLegRoll'                       				  )
		self.create_lower_leg_roll_constraint  ( '*LegRoll',  '*Foot',                      reject=['Up']    )
		self.create_foot_twist_constraint ( '*FootTwist', '*Foot' )

		vmobu.core.evaluate( )

		##############################################
		#          ACTIVATE the Constraints          #
		##############################################
		self.activate_constraints( )

		self.organize_constraints( character_name=self.namespace, body_part='Arm', keywords=[ 'elbow', 'arm', 'scapula', 'lat' ] )
		self.organize_constraints( character_name=self.namespace, body_part='Leg', keywords=[ 'knee',  'leg', 'foot' ] )
		self.organize_constraints( character_name=self.namespace, body_part='Utility', keywords=[ 'spine', 'camera' ] )

		vmobu.core.evaluate( )

		return True

class Dummy_Character_Rig_Constraint_Builder( Character_Rig_Constraint_Builder ):
	def __init__(self, character, data):
		Character_Rig_Constraint_Builder.__init__( self, character )
		self.namespace = data['name']
		self.asset_type = data['type']
		self.control_look_dictionary = { 'capsule' : pyfbsdk.FBMarkerLook.kFBMarkerLookCapsule,
		                                'sphere' : pyfbsdk.FBMarkerLook.kFBMarkerLookSphere,
		                                'cube': pyfbsdk.FBMarkerLook.kFBMarkerLookCube,
		                                'light_cross': pyfbsdk.FBMarkerLook.kFBMarkerLookLightCross,
		                                'hard_cross': pyfbsdk.FBMarkerLook.kFBMarkerLookHardCross }

	def run( self ):
		"""
		Main logic for the dummy rig constraint builder.
		"""

		self._organize_ctrl_hierarchy()

		root_bone = self._find_root_bone( )
		if not root_bone:
			return False, "Can't determine root bone"
		size_multiplier = 10
		if 'weapon' in self.asset_type.lower( ):
			size_multiplier = 1

		# Create a marker for the root
		root_marker, root_null = self._create_control_marker( root_bone, control_look='hard_cross', size = 200 * size_multiplier, color = ( 1, 1, 1 ), v_inheritance = False, null = True )
		vmobu.core.evaluate( )

		# Get the refernce obj
		root_marker.Parent = root_null
		root_null.Parent = vmobu.core.get_object_by_name( '{0}:Ctrl:Reference'.format( self.namespace ), use_namespace = True, case_sensitive = False, single_only = True, models_only = True )

		# Get the hierarchy for the weapon/item/vehicle
		hierarchy = [ bone for bone in vmobu.core.get_hierarchy( root_bone ) if isinstance( bone, pyfbsdk.FBModelSkeleton ) ]

		extension_list = self.character.CharacterExtensions

		# Grab the appropriate character extensions
		control_extension = None
		holder_extension    = None

		for extension in extension_list:
			if extension.Name.lower( ) == 'controlnodesextension':
				control_extension = extension

			if extension.Name.lower( ) == 'holderextension':
				holder_extension = extension

			if holder_extension and control_extension:
				break

		matched_nulls = [ ]
		for child in hierarchy:
			# If the bone name is the root_bone, we skip because we've already processed it.
			if child.LongName == root_bone.LongName:
				continue
			marker, null = self._create_control_marker( child, control_look='sphere', size = 100 * size_multiplier, v_inheritance = False, null = True )

			# Match the nulls with the bone they're associated with for later parenting.
			matched_nulls.append( ( null, child ) )

			# Connect the marker to the control extension
			pyfbsdk.FBConnect( marker, control_extension )

		# Add the nulls to their own extension
		for _tuple in matched_nulls:
			null = _tuple[ 0 ]
			matched_bone = _tuple[ 1 ]

			parent = matched_bone.Parent.Name
			if not parent:
				continue

			reference_prop = self.character.PropertyList.Find( parent )

			# The bone matches a bone in the control rig. This shouldnt happen, but just in case we need to search for the effector, not just find it in the prop list.
			if not reference_prop and parent in vmobu.const.MOBU_CHAR_TO_LEGACY_CHARACTER_BIP.keys( ):
				for prop in self.character.PropertyList:
					if not prop.IsUserProperty( ):
						continue

					if parent.lower( ) in prop.Name.lower( ):
						reference_prop = prop

			if not reference_prop:
				print 'Failed on {0}'.format( parent )
				continue

			null.Parent = reference_prop.GetSrc( 0 ).GetOwner( )

			# Connect the null to the extension
			pyfbsdk.FBConnect( null, holder_extension )

		# Add the root_marker to the control nodes extension
		pyfbsdk.FBConnect( root_marker, control_extension )
		control_extension.UpdateStancePose( )
		holder_extension.UpdateStancePose( )

		# Get all the constraints
		constraints = [ constraint_dict[ 'constraint' ] for constraint_dict in self.constraints.values() ]

		self.organize_constraints( constraints )

		if 'weapon' in self.asset_type.lower( ):
			root_marker.Visibility = False
			return root_marker

	def _find_root_bone( self ):
		"""
		Finds the root bone of the rig we are processing

		**Returns:**

			:``root_bone``:	`pyfbsdk.FBModelSkeleton` The root bone of the rig.
		"""

		vmobu.core.evaluate( )
		root_bone = None
		if 'vehicle' in self.asset_type.lower( ):
			# Look first if it's a vehicle that's being characterized and constraints built for
			root_bone = vmobu.core.get_objects_from_wildcard( "{0}:*bone:body".format( self.namespace ), use_namespace = True, case_sensitive = False, single_only = True, models_only = True )

		# If no bone is found within the character, continue on and look for the weapon/gadget namespace
		if 'weapon' in self.asset_type.lower( ):
			root_bone = vmobu.core.get_objects_from_wildcard( "{0}:*bone:root".format( self.namespace ), use_namespace = True, case_sensitive = False, single_only = True, models_only = True )

		# Still no root bone? Return False.
		if not root_bone:
			return False

		return root_bone

	def _create_control_marker( self, bone, control_look = 'capsule', size = 100, length = 10, color = (.2, 1, .2), v_inheritance = True, null = False ):
		"""
		Creates control pyfbsdk.FBModelMarkers for the dummy control rig.

		**Arguments:**

			:``bone``:	`pyfbsdk.FBModelSkeleton` skeleton obj we are constraining to the control

		**Keyword Arguments:**

			:``control_look``:	`str` the control type we want. default is 'capsule'.
			Options| what they relate to
						- { 'capsule' : pyfbsdk.FBMarkerLook.kFBMarkerLookCapsule,
							'sphere' : pyfbsdk.FBMarkerLook.kFBMarkerLookSphere,
							'cube': pyfbsdk.FBMarkerLook.kFBMarkerLookCube,
							'light_cross': pyfbsdk.FBMarkerLook.kFBMarkerLookLightCross,
							'hard_cross': pyfbsdk.FBMarkerLook.kFBMarkerLookHardCross }
			:``size``: `int` size of the new control
			:``length``: `int` optional - length of the new control
			:``color``: `tuple` rgb of the desired control color
			:``v_inheritance``: `bool` visibility inheritance of the control
			:``null``: `bool` should the control be the child of a holder object, null

		**Returns:**

			:``control``:	`pyfbsdk.FBModelMarker`
			:``holder``: `pyfbsdk.FBModelNull` if the null kwarg was flagged as True
		"""

		# Create and edit look of control
		control = pyfbsdk.FBModelMarker( '{0}:Ctrl:{1}Effector'.format( self.namespace, bone.Name ) )
		control.Length = length
		control.Size = size
		control.Show = True
		control.Color = pyfbsdk.FBColor( color )
		vmobu.core.add_property_obj( control, 'effector_type', 'dummy', force = True )

		if not control_look in self.control_look_dictionary.keys():
			print '{0} not found in control look dictionary. Reverting to default capsule'.format( control_look )
			control_look = 'capsule'

		control.Look = self.control_look_dictionary[ control_look ]
		control.ResLevel = pyfbsdk.FBMarkerResolutionLevel.kFBMarkerLowResolution
		control.VisibilityInheritance = v_inheritance

		# Position to the align_object and parent to the control
		vmobu.core.align_objects( control, bone, False, True, True )

		reference_name = control.Name

		vmobu.core.create_property_reference( control, self.character, control.PropertyList.Find( 'effector_type' ), name = reference_name.replace( 'Effector', '' ) )

		if null:
			null = pyfbsdk.FBModelNull( '{0}:Ctrl:{1}Null'.format( self.namespace, bone.Name ) )
			vmobu.core.align_objects( null, bone, False, True, True )

			control.Parent = null

			# Constrain the bone to the control
			parent_constraint = vmobu.core.create_constraint_parent( bone, control )
			parent_constraint.Snap( )
			self.constraints[ parent_constraint.LongName ] = { 'constraint': parent_constraint }

			return control, null

		return control

	def _organize_ctrl_hierarchy( self ):
		"""
		Organize the control hierarchy of the HIK control rig so that we aren't cluttering the navigator with meaningless controls.

		**Arguments:**

			:``Argument``:	`arg_type` Enter a description for the argument here.

		**Keyword Arguments:**

			:``Argument``:	`arg_type` Enter a description for the keyword argument here.

		**Returns:**

			:``Value``:	`arg_type` If any, enter a description for the return value here.
		"""

		ctrl_reference = vmobu.core.get_object_by_name( '{0}:Ctrl:Reference'.format( self.namespace ), use_namespace = True, case_sensitive = False, single_only = True, models_only = True )

		ctrl_hierarchy = vmobu.core.get_hierarchy( ctrl_reference )
		ctrl_holder = pyfbsdk.FBModelNull( '{0}:Ctrl:IrrelevantControls'.format( self.namespace ) )
		ctrl_holder.Parent = ctrl_reference

		for obj in ctrl_hierarchy:
			if obj.LongName == '{0}:Ctrl:Reference'.format( self.namespace ):
				continue
			obj.Parent = ctrl_holder

		return True

	def organize_constraints( self, constraints ):
		"""
		Organize constraints into folders for easier viewing in mobu's Navigator

		**Arguments:**

			:``constraints``:	`list` of constraints we want to process related to the character. Most likely, all of them.
		"""

		# Make the master constraint folder
		self.character_constraint_folder = pyfbsdk.FBFolder( '{0}:Constraints'.format( self.namespace ), constraints[ 0 ] )

		# Declare sub folders variables to compare later so we can be sure they're made
		left_folder = None
		right_folder = None
		center_folder = None

		# Organize common constraints and left and right constraints.
		for constraint in constraints:
			# If left, l_ or _l in the name of the item
			if 'left' in constraint.Name.lower( ) or constraint.Name.startswith( ( 'l_', 'L_' ) ) or  constraint.Name.endswith( ( '_l', '_L' ) ):
				# Add to the left constraints
				if not left_folder:
					# Create the folder if it hasn't been created yet
					left_folder = pyfbsdk.FBFolder( '{0}:Left_Constraints'.format( self.namespace ), constraint )
					continue

				left_folder.Items.append( constraint )

			elif 'right' in constraint.Name.lower( ) or constraint.Name.startswith( ( 'r_', 'R_' ) ) or constraint.Name.endswith( ( '_R', '_r' ) ):
				# Add to the right constraints
				if not right_folder:
					# Create the folder if it hasn't been created yet
					right_folder = pyfbsdk.FBFolder( '{0}:Right_Constraints'.format( self.namespace ), constraint )
					continue

				right_folder.Items.append( constraint )

			else:
				if not center_folder:
					# Create the folder if it hasn't been created yet
					center_folder = pyfbsdk.FBFolder( '{0}:Center_Constraints'.format( self.namespace ), constraint )
					continue

				center_folder.Items.append( constraint )

		# Parent the sub folders to the master folder if they were created
		for folder in [ left_folder, right_folder, center_folder ]:
			if folder:
				self.character_constraint_folder.Items.append( folder )

		# Remove the first item ( generated only to make the folder properly )
		self.character_constraint_folder.Items.pop(0)

		return True

@vmobu.decorators.without_callbacks_obj
def rebuild_character_constraints( character = None ):
	confirmation = vmobu.core.confirm_dialog( 'Constraint Rebuild Notification', 'Be sure your character is properly selected and in a T-POSE before continuing! \n \nYour work will be saved to a temp directory in case there are any problems. Contact a TA if you need to access this.', 'Continue', 'Cancel' )
	if not confirmation:
		return False, 'User cancelled'

	# Hold the file in case we break it.
	vmobu.mobu_file.Mobu_File( ).file_hold( swap = True )
	if not character:
		# Get the current character and verify that it's valid
		character = vmobu.core.get_current_character( )
		if not character:
			return False, 'Character not found'

	character_namespace = character.LongName.split(':')[0]
	character_type = character.PropertyList.Find( 'character_type' )
	if character_type:
		if character_type.Data == 'dummy':
			vmobu.core.confirm_dialog( 'Constraint Rebuild Error', 'Weapon/Vehicle character is currently set as the active character. Please switch this to a biped character.', 'OK' )
			return False, 'Dummy character passed in'

	# Get the master constraint folder
	constraint_folder = vmobu.core.get_objects_from_wildcard('{0}:Constraints'.format( character_namespace ), use_namespace=True, case_sensitive=False, models_only=False, single_only=True )

	if not constraint_folder:
		return False, 'No constraint folder found for {0}'.format( character_namespace )

	# Iterate through the constraint folder
	objs_to_delete = [ constraint_folder ]
	objs_to_delete = _recursive_fb_folder_search( constraint_folder, objs_to_delete, [ 'face_constraints' ] )

	# Delete all the constraints
	vmobu.core.safe_delete_object( objs_to_delete )
	vmobu.core.logger.info('REBUILD : Deleted all the constraints!', extra = '{0}'.format( len( objs_to_delete ) ) )

	vmobu.core.evaluate( )
	Character_Rig_Constraint_Builder( character ).run( )

	vmobu.core.evaluate( )

	return True, 'Character constraint rebuild successful'


def _recursive_fb_folder_search( folder, children = None, skip_strings = None ):
	"""
	Looks through MotionBuilder FB Folder objects for all sub components

	**Arguments:**

		:``folder``:	`pyfbsdk.FBFolder` Folder to start your search in.

	**Keyword Arguments:**

		:``children``:	`list` list we are going to use to return all children
		:``skip_strings``:	`list` strings we want to check if a folders name contains. if it does, we skip it

	**Returns:**

		:``Value``:	`arg_type` If any, enter a description for the return value here.
	"""

	# Check to be sure the folder is actually of type FBFolder
	if not isinstance( folder, pyfbsdk.FBFolder ):
		return [ ]

	if not skip_strings:
		skip_strings = [ ]

	if not children:
		children = [ ]

	# Iterate through all the sub objects of the folder
	for sub_obj in folder.Items:
		# If it's a folder, we run the method again on the folder
		if isinstance( sub_obj, pyfbsdk.FBFolder ) and sub_obj.Name.lower( ) not in skip_strings:
			children.extend( _recursive_fb_folder_search( sub_obj, children, skip_strings ) )

		# Add the item to children list
		children.append( sub_obj )

	return children