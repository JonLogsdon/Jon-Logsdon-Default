//--- Class declaration
#include "PreVizDevice.h"

//--- Registration defines
#define PREVIZ_CLASS		PREVIZ_CLASSNAME
#define PREVIZ_NAME		    PREVIZ_CLASSSTR
#define PREVIZ_LABEL		"PreViz"
#define PREVIZ_DESC		    "Live Driver PreViz Device"
#define PREVIZ_PREFIX	    "PreViz"
#define PREVIZ_ICON		    ""

//--- FiLMBOX implementation and registration
FBDeviceImplementation	(	PREVIZ_CLASS	);
FBRegisterDevice		(	PREVIZ_NAME,
							PREVIZ_CLASS,
							PREVIZ_LABEL,
							PREVIZ_DESC,
							PREVIZ_ICON	);

/************************************************
 *	FiLMBOX Constructor.
 ************************************************/
bool PreVizDevice::FBCreate()
{
	// Add model templates
	mRootTemplate =  new FBModelTemplate(PREVIZ_PREFIX, "Reference", kFBModelTemplateRoot);
	ModelTemplate.Children.Add(mRootTemplate);
	mHierarchyIsDefined = false;
	mHasAnimationToTranspose = false;
	mPlotting = false;

	// TODO: Investigate these
	// Device sampling information
	SamplingMode = kFBHardwareTimestamp;
	SamplingPeriod = FBTime(0,0,1)/30.0; // sSKDataBuffer::SIM_FPS;

	FBPropertyPublish( this, UseReferenceTransformation, "UseReferenceTransformation", NULL, NULL );
	UseReferenceTransformation = true;

	// TIFF image of your device's icon
	IconFilename = PREVIZ_ICON;

	// Probably don't need this
	FBSystem().TheOne().OnUIIdle.Add( this,(FBCallback) &PreVizDevice::EventUIIdle );

	TReal x, y, z;
    outputFrame.GetHeadPosition(x, y, z);

	for(int i = 0; i < outputFrame.GetAnimationControls().GetCount(); ++i)
    {
      const IAnimationControl & control = outputFrame.GetAnimationControls().GetControl(i);

//      Log("\t %s %f\n", control.GetName(), control.GetValue());
	  // Look up motion builder node name based on control name
	  std::map<std::string, std::string>::const_iterator it = m_NameMap.find(control.GetName());
	  if(it != m_NameMap.end())
	  {
		  std::string mobuName = it->second;
	  }

    }

	return true;

}

// Control Mapping
void PreVizHardware::CreateNameMappings()
{
	m_NameMap["eyes_rotate_right"] = "MB_eyes_rotate_right";
	m_NameMap["eyes_rotate_left"] = "MB_eyes_rotate_left";
	m_NameMap["eyes_rotate_down"] = "MB_eyes_rotate_down";
	m_NameMap["eyes_rotate_up"] = "MB_eyes_rotate_up";
	m_NameMap["left_blink"] = "MB_left_blink";
	m_NameMap["right_blink"] = "MB_right_blink";
	m_NameMap["left_eye_wide"] = "MB_left_eye_wide";
	m_NameMap["right_eye_wide"] = "MB_right_eye_wide";
	m_NameMap["blink"] = "MB_blink";
	m_NameMap["eyes_wide"] = "MB_eyes_wide";
	m_NameMap["left_brow_up"] = "MB_left_brow_up";
	m_NameMap["left_brow_down"] = "MB_left_brow_down";
	m_NameMap["right_brow_up"] = "MB_right_brow_up";
	m_NameMap["right_brow_down"] = "MB_right_brow_down";
	m_NameMap["mid_brows_up"] = "MB_mid_brows_up";
	m_NameMap["mid_brows_down"] = "MB_mid_brows_down";
	m_NameMap["mouth_open"] = "MB_mouth_open";
	m_NameMap["jaw_rotate_y_min"] = "MB_jaw_rotate_y_min";
	m_NameMap["jaw_rotate_y_max"] = "MB_jaw_rotate_y_max";
	m_NameMap["jaw_rotate_z_min"] = "MB_jaw_rotate_z_min";
	m_NameMap["jaw_rotate_z_max"] = "MB_jaw_rotate_z_max";
	m_NameMap["oo_tight"] = "MB_oo_tight";
	m_NameMap["mouth_down"] = "MB_mouth_down";
	m_NameMap["mouth_up"] = "MB_mouth_up";
	m_NameMap["scrunch_right"] = "MB_scrunch_right";
	m_NameMap["scrunch_left"] = "MB_scrunch_left";
	m_NameMap["mbp"] = "MB_mbp";
	m_NameMap["normal_FV"] = "MB_normal_FV";
	m_NameMap["ch"] = "MB_ch";
	m_NameMap["upper_lip_left_up"] = "MB_upper_lip_left_up";
	m_NameMap["upper_lip_right_up"] = "MB_upper_lip_right_up";
	m_NameMap["lower_lip_left_down"] = "MB_lower_lip_left_down";
	m_NameMap["lower_lip_right_down"] = "MB_lower_lip_right_down";
	m_NameMap["smile_big_left"] = "MB_smile_big_left";
	m_NameMap["smile_big_right"] = "MB_smile_big_right";
	m_NameMap["upper_lip_roll_in"] = "MB_upper_lip_roll_in";
	m_NameMap["upper_lip_roll_out"] = "MB_upper_lip_roll_out";
	m_NameMap["lower_lip_roll_in"] = "MB_lower_lip_roll_in";
	m_NameMap["lower_lip_roll_out"] = "MB_lower_lip_roll_out";
	m_NameMap["left_frown"] = "MB_left_frown";
	m_NameMap["smile_left"] = "MB_smile_lefte";
	m_NameMap["right_frown"] = "MB_right_frown";
	m_NameMap["smile_right"] = "MB_smile_right";
}

/************************************************
 *	FiLMBOX Destructor.
 ************************************************/
void PreVizDevice::FBDestroy()
{
    // Propagate to parent
    ParentClass::FBDestroy();
	// Or this
	FBSystem().TheOne().OnUIIdle.Remove( this,(FBCallback) &PreVizDevice::EventUIIdle );
}

/************************************************
 *	Device operation.
 ************************************************/
bool PreVizDevice::DeviceOperation( kDeviceOperations pOperation )
{
	// Must return the online/offline status of device.
	switch (pOperation)
	{
		case kOpInit:	return Init();
		case kOpStart:	return Start();
		case kOpAutoDetect:	break;
		case kOpStop:	return Stop();
		case kOpReset:	return Reset();
		case kOpDone:	return Done();
	}
    return ParentClass::DeviceOperation(pOperation);
}


/************************************************
 *	Initialize the device.
 ************************************************/
bool PreVizDevice::Init()
{
    FBProgress	lProgress;

    lProgress.Caption	= "Device";
	lProgress.Text		= "Initializing device...";

	mHierarchyIsDefined = false;

//	Bind();

	return true;
}


/************************************************
 *	Removal of device.
 ************************************************/
bool PreVizDevice::Done()
{
	FBProgress	lProgress;

    lProgress.Caption	= "Device";
	lProgress.Text		= "Shutting down device...";

//	UnBind();
	
	/*
	*	Add device removal code here.
	*/

	return true;
}

/************************************************
 *	Reset of the device.
 ************************************************/
bool PreVizDevice::Reset()
{
    Stop();
    return Start();
}

/************************************************
 *	Device is star
 ted (online).
 ************************************************/
bool PreVizDevice::Start()
{
	FBProgress	Progress;

	Progress.Caption	= "Setting up device";

	mHardware.StartVideo();
	mHardware.StartProcessing();

	return true; // if true the device is online
}

/************************************************
 *	Device is stopped (offline).
 ************************************************/
bool PreVizDevice::Stop()
{
	FBProgress	lProgress;
	lProgress.Caption	= "Shutting down device";

	mHardware.StopVideo();
	mHardware.StopProcessing();

	// Step 2: Close down device
	lProgress.Text		= "Closing device communication";
	Information			= "Closing device communication";

    return false;
}


/************************************************
 *	Real-time Evaluation Engine.
 ************************************************/
bool PreVizDevice::AnimationNodeNotify(HFBAnimationNode pAnimationNode ,HFBEvaluateInfo pEvaluateInfo)
{
	mHardware.Tick();

	// THE "UPDATE" Function which Motion Builder calls repeatedly for you to "do your stuff". In our
	// case, doing our stuff is taking live driver animatio ncontrol values and setting them on
	// animation nodes in MoBu

	const ImageMetrics::LiveDriverSDK::IOutputFrame & latestFrame = mHardware.GetLatestLiveDriverOutput();
	/// ....

	void GetHeadPosition(TReal & x, TReal & y, TReal & z) const = 0;
	void GetHeadRotation(TReal & x, TReal & y, TReal & z) const = 0;
	

	kReference lReference = pAnimationNode->Reference;
	return ParentClass::AnimationNodeNotify( pAnimationNode , pEvaluateInfo);
}


/************************************************
 *	Real-Time Synchronous Device IO.
 ************************************************/
void PreVizDevice::DeviceIONotify( kDeviceIOs pAction,FBDeviceNotifyInfo &pDeviceNotifyInfo)
{
	FBTime lPacketTime;
    switch (pAction)
	{
		case kIOPlayModeWrite:
		case kIOStopModeWrite:
		{
			// Output devices
		}
		break;

		case kIOStopModeRead:
		case kIOPlayModeRead:
		{
			// Skeleton devices
	        FBTime		evalTime;
        
	        evalTime = pDeviceNotifyInfo.GetLocalTime();
	        while(mHardware.FetchDataPacket(evalTime))
	        {
		        DeviceRecordFrame(evalTime,pDeviceNotifyInfo);
				AckOneSampleReceived();
	        }
		}
		break;
	}
}

void PreVizDevice::RecordingDoneAnimation( HFBAnimationNode pAnimationNode )
{
	// Parent call
	FBDevice::RecordingDoneAnimation( pAnimationNode );
	mHasAnimationToTranspose = true;
}


/************************************************
 *	Record a frame of the device (recording).
 ************************************************
void PreVizDevice::DeviceRecordFrame(FBTime &pTime,FBDeviceNotifyInfo &pDeviceNotifyInfo)
{
	if( mPlayerControl.GetTransportMode() == kFBTransportPlay )
	{
		int i;
		HFBAnimationNode Data;

		FBTVector	Pos;
		FBRVector	Rot;
		bool		ApplyReferenceTransformation = UseReferenceTransformation && mRootTemplate->Model;
		
		FBMatrix	GlobalReferenceTransformation;
		if(ApplyReferenceTransformation)
			mRootTemplate->Model->GetMatrix(GlobalReferenceTransformation,kModelTransformation,true);

		for (i=0; i<GetChannelCount(); i++)
		{
			// Translation information.
			if (mChannels[i].mTAnimNode)
			{
				Data = mChannels[i].mTAnimNode->GetAnimationToRecord();
				if (Data)
				{
					Pos[0] = mHardware.GetDataTX(i);
					Pos[1] = mHardware.GetDataTY(i);
					Pos[2] = mHardware.GetDataTZ(i);

					if(ApplyReferenceTransformation)
						FBVectorMatrixMult(Pos,GlobalReferenceTransformation,Pos);

					Data->KeyAdd(pTime, Pos);
				}
			}

			// Rotation information.
			if (mChannels[i].mRAnimNode)
			{
				Data = mChannels[i].mRAnimNode->GetAnimationToRecord();
				if (Data)
				{
					Rot[0] = mHardware.GetDataRX(i);
					Rot[1] = mHardware.GetDataRY(i);
					Rot[2] = mHardware.GetDataRZ(i);

					if(ApplyReferenceTransformation)
					{
						FBMatrix GRM;
						FBRotationToMatrix(GRM,Rot);
						FBGetGlobalMatrix(GRM,GlobalReferenceTransformation,GRM);
						FBMatrixToRotation(Rot,GRM);
					}

					Data->KeyAdd(pTime, Rot);
				}
			}
		}
	}
}
*/