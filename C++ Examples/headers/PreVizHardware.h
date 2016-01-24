//--- SDK include
#include <fbsdk/fbsdk.h>

#include "ILiveDriver.h"
#include "ILoggingCallback.h"
#include "IOutputCallback.h"

#include <string>
#include <map>
#include <vector>

// Wrapper for the Live Driver SDK
// Responsible for:
// * Owns Live Driver object
// * Feeds images in on a timer
// * Returns latest output upon request
class PreVizHardware : public ImageMetrics::LiveDriverSDK::ILoggingCallback, public ImageMetrics::LiveDriverSDK::IOutputCallback
{
public:
	PreVizHardware();
	~PreVizHardware();

	void Tick();

	void StartVideo();
	void StopVideo();

	void StartProcessing();
	void StopProcessing();

	const ImageMetrics::LiveDriverSDK::IOutputFrame& GetLatestLiveDriverOutput() const;

	void SetJpegDirectory(std::string jpegDirectory);

private:
	FBSystem			mSystem;							//!< System interface.
    ImageMetrics::LiveDriverSDK::ILiveDriver * m_LiveDriver;
    ImageMetrics::LiveDriverSDK::IImage * m_Image;
	std::map<std::string, std::string> m_NameMap;
	typedef std::vector< std::string > FileList;
    FileList m_Images;
	bool m_FeedJpegs;

	bool ReadDirectory(FileList& files, std::string directory);

	///////////////////////////////////
	// ILoggingCallback implementation
    virtual void LogInfo(const char * message);
    virtual void LogWarning(const char * message);
    virtual void LogError(const char * message);

	///////////////////////////////////
	// IOutputCallback implementation
    virtual void OnFrameAvailable();

	void CreateNameMappings();

	std::map<std::string, std::string> m_NameMap;
};
