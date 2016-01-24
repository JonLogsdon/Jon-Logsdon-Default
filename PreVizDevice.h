#pragma once


//--- SDK include
#include <fbsdk/fbsdk.h>

//--- Class declaration
#include "PreVizHardware.h"

//--- Registration defines
#define PREVIZ_CLASSNAME		PreVizDevice
#define PREVIZ_CLASSSTR			"PreVizDevice"

//! Simple skeleton device.
class PreVizDevice : public FBDevice
{
	//--- Declaration
	FBDeviceDeclare( PreVizDevice, FBDevice );

public:
	virtual bool FBCreate() override;
	virtual void FBDestroy() override;

	
    //--- Standard device virtual functions evaluation
	virtual bool DeviceOperation	( kDeviceOperations pOperation									) override;		//!< Operate device.
	virtual bool AnimationNodeNotify( HFBAnimationNode pAnimationNode,HFBEvaluateInfo pEvaluateInfo	) override;		//!< Real-time evaluation function.
	virtual void DeviceIONotify		( kDeviceIOs  pAction, FBDeviceNotifyInfo &pDeviceNotifyInfo	) override;		//!< Hardware I/O notification.
	virtual void DeviceTransportNotify( kTransportMode pMode, FBTime pTime, FBTime pSystem ) override;				//!< Transport notification.

	//--- Recording of frame information
	virtual void	RecordingDoneAnimation( HFBAnimationNode pAnimationNode) override;
	void	DeviceRecordFrame			(FBTime &pTime,FBDeviceNotifyInfo &pDeviceNotifyInfo);

	//--- Load/Save.
	virtual bool FbxStore	( HFBFbxObject pFbxObject, kFbxObjectStore pStoreWhat ) override;	//!< FBX Storage.
	virtual bool FbxRetrieve( HFBFbxObject pFbxObject, kFbxObjectStore pStoreWhat ) override;	//!< FBX Retrieval.

	//--- Initialisation/Shutdown
    bool	Init	();		//!< Initialize device.
    bool	Start	();		//!< Start device.
    bool	Stop	();		//!< Stop device.
    bool	Reset	();		//!< Reset device.
    bool	Done	();		//!< Device removal.

	bool	ReadyForCharacterize		();				//!< Test if characterization process can be start.

	//--- Stop displaying process to local message on model unbind
	void	EventUIIdle( HISender pSender, HKEvent pEvent );

	PreVizHardware				mHardware;					//!< Hardware abstraction object.
	FBModelTemplate*			mRootTemplate;				//!< Root model binding.
private:

	FBPropertyBool				UseReferenceTransformation;	// !< Apply reference transformation on incoming global data.
	bool						mHierarchyIsDefined;		//!< True if the hierarchy is already defined

	FBPlayerControl				mPlayerControl;				//!< To get play mode for recording.
	FBSystem					mSystem;
	FBApplication				mApplication;
	bool						mHasAnimationToTranspose;
	bool						mPlotting;

	// Process global data on template models to local
	void ProcessGlobalToLocal();
	void SetupLocalGlobal(bool pGlobal);

	typedef std::vector< std::string > FileList;
	bool ReadDirectory(FileList& files, std::string directory);

	void CreateNameMappings();

	std::map<std::string, std::string> m_NameMap;
};
