#include "LDWrapper.h"

//#pragma once


//------------------------------------DEVICE SYNC---------------------------------------------------
	class FBSDK_DLL FBDeviceSync : public FBDevice
	{
		__FBClassDeclare( FBDeviceSync, FBDevice );
	public:
		FBDeviceSync(char* pName, HIObject pObject=NULL);
		virtual bool FBCreate();
		virtual HFBDeviceSyncPacket PacketLock();
	}


//------------------------------------GET LATEST OUTPUT---------------------------------------------
	void LDWrapper::OnFrameAvailable()
	{
		const IOutputFrame & outputFrame = m_LiveDriver->GetLatestOutput();
	}


//------------------------------------CONTROL MAPPING-----------------------------------------------
	void LDWrapper::CreateNameMappings(){
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