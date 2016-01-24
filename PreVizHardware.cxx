//--- Class declaration
#include "PreVizHardware.h"

#include <fstream>
#include <Windows.h>

//#include <fbpython.h>

PreVizHardware::PreVizHardware()
	: m_FeedJpegs( false )
{
	// TODO: Read license key contents
	const std::string licenseFile = "C:/LiveDriverLicense.lic";
    std::ifstream file(licenseFile, std::ios_base::in);
    std::string licenseKey((std::istreambuf_iterator<char>(file)), std::istreambuf_iterator<char>());
	m_LiveDriver = CreateLiveDriver(licenseKey.c_str());

    // Set our callbacks. The Logging callback is called when there are new log messages.
    // The Output callback is called when there is new animation data available.
    m_LiveDriver->AddLoggingCallback(this);
    m_LiveDriver->AddOutputCallback(this);

    // Create a reusable image object.
    m_Image = m_LiveDriver->CreateImage();


	// TODO: Set correct model path
    // Set the tracking model. Use one of the ones that is shipped with the SDK
	const std::string trackingModel = "C:/Program Files/Image Metrics/LiveDriverSDK/Models/blah.imbin";
    m_LiveDriver->SetCurrentTrackingModel(trackingModel.c_str());
}

PreVizHardware::~PreVizHardware()
{
    // Stop processing
    m_LiveDriver->Stop();

    // Destroy the objects created for us by Live Driver.
    m_LiveDriver->DestroyImage(m_Image);
	m_Image = 0;
    DestroyLiveDriver(m_LiveDriver);
	m_LiveDriver = 0;
}

void PreVizHardware::Tick()
{
	// TODO: Feed in image into live driver. Only feed image if it's been more than 1000/ 30.0
	// ms since the last time it fed an image in. It also won't feed in an image if you've turned
	// the jpeg feeding off.

	// m_Image->SetFromImageFile(itr->c_str());
    m_LiveDriver->AddImage(m_Image);
}

void PreVizHardware::StartVideo()
{
	m_FeedJpegs = true;
}

void PreVizHardware::StopVideo()
{
	m_FeedJpegs = false;
}

void PreVizHardware::StartProcessing()
{
	// Turn on processing on live driver
	m_LiveDriver->Start();
}

void PreVizHardware::StopProcessing()
{
	m_LiveDriver->Stop();
}

const ImageMetrics::LiveDriverSDK::IOutputFrame& PreVizHardware::GetLatestLiveDriverOutput() const
{
	return m_LiveDriver->GetLatestOutput();
}

void PreVizHardware::SetJpegDirectory(std::string jpegDirectory)
{
	//  Read file
	ReadDirectory(m_Images, jpegDirectory);
}

bool PreVizHardware::ReadDirectory(FileList& files, std::string directory)
{
	if(directory.empty())
	{
		return false;
	}
    
	if(directory[directory.size() - 1] != '\\')
	{
		directory += '\\';
	}

	WIN32_FIND_DATA findFileData;
	HANDLE hFind = FindFirstFile((directory + '*').c_str(), &findFileData);
	if(hFind == INVALID_HANDLE_VALUE)
	{
		return false;
	}

	// Skip '.' and '..'
	FindNextFile(hFind, &findFileData);
            
	while(0 != FindNextFile(hFind, &findFileData))
	{
		files.push_back(directory + findFileData.cFileName);
	}

	return true;
}

///////////////////////////////////////////////////////////////////////////////////////////////////
void PreVizHardware::LogInfo(const char * message)
{
	// TODO: Figure out how to send logging messages to Motio Builders log window
}

///////////////////////////////////////////////////////////////////////////////////////////////////
void PreVizHardware::LogWarning(const char * message)
{
	// TODO: Figure out how to send logging messages to Motio Builders log window
}

///////////////////////////////////////////////////////////////////////////////////////////////////
void PreVizHardware::LogError(const char * message)
{
	// TODO: Figure out how to send logging messages to Motio Builders log window
}

///////////////////////////////////////////////////////////////////////////////////////////////////
void PreVizHardware::OnFrameAvailable()
{
	// Probably nothing to do here since we'll probably poll live driver for the latests
	// output whenever Motion Builder asks us to "update"
	
}

/*
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
*/

