@staticmethod
	def key_reduce(object, mode=None, amount=50, keep_interpolation=True):
		"""
		Reduces the amount of keys in an animation, based on constant keys, and animation blending to preserve motions.

		*Arguments:*
			* ``character`` The source character for the retargeting

		*Keyword Arguments:*
			* ``none``

		*Returns:*
			* ``None``

		*Examples:*

			>>> character = pyfbsdk.FBSystem().Scene.Characters[0]
			>>> vmobu.core.key_reduce(pyfbsdk.FBSystem().Scene.Characters[0])

		*Author:*
			* Jon Logsdon, jon.logsdon@volition-inc.com, 11/5/2014 3:18:34 PM
		"""

		#Get the start frame, end frame, and timerange
		start = int(pyfbsdk.FBSystem().CurrentTake.LocalTimeSpan.GetStart().GetFrame())
		end = int(pyfbsdk.FBSystem().CurrentTake.LocalTimeSpan.GetStop().GetFrame())

		#Go to the start of the animation before key evaluation
		pyfbsdk.FBPlayerControl().GotoStart()

		#Iterate through frames
		for i in range(start, end):
			pyfbsdk.FBPlayerControl().Goto(pyfbsdk.FBTime(0, 0, 0, i))

			#Get the current frame
			curr_frame = pyfbsdk.FBSystem().LocalTime.GetFrame()

			#Set previous frame to the frame before current, and next frame to the frame after current
			prev_frame = int(curr_frame-1)
			next_frame = int(curr_frame+1)

			#Get the animation node based on keyword mode
			if mode == 'translation':
				curr_anim_node = object.Translation.GetAnimationNode()
			elif mode == 'rotation':
				curr_anim_node = object.Rotation.GetAnimationNode()
			elif mode == 'scale':
				curr_anim_node = object.Scaling.GetAnimationNode()

			#Iterate through animation node nodes
			for node in curr_anim_node.Nodes:
				#Get the FCurve
				curr_fcurve = node.FCurve
				if curr_fcurve:
					#Iterate through keys
					for key in curr_fcurve.Keys:
						#Check if key time matches the current frame
						print key.Time
						#Make sure it has a value
						if key.Value:
							#Go to the previous frame
							pyfbsdk.FBPlayerControl().Goto(pyfbsdk.FBTime(0, 0, 0, prev_frame))
							#Get the animation node of the previous frame
							prev_anim_node = object.Translation.GetAnimationNode()
							#Iterate through animation node nodes
							for node in prev_anim_node.Nodes:
								prev_fcurve = node.FCurve
								if prev_fcurve:
									for pkey in prev_fcurve.Keys:
										if pkey.Value:
											if pkey.Value == key.Value:
												#Go to the next frame of the original frame
												pyfbsdk.FBPlayerControl().Goto(pyfbsdk.FBTime(0, 0, 0, next_frame))
												next_anim_node = object.Translation.GetAnimationNode()
												for node in next_anim_node.Nodes:
													next_fcurve = node.FCurve
													if next_fcurve:
														for nkey in next_fcurve.Keys:
															if nkey.Value:
																#If the key value of the original frame match the previous and next frame, delete the key
																if nkey.Value == key.Value:
																	curr_anim_node.KeyRemoveAt(pyfbsdk.FBTime(0, 0, 0, curr_frame))
					#There is no FCurve, log a warning
					else:
						pass

		return True