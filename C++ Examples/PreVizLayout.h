#pragma once

//--- Class declaration
#include "PreVizDevice.h"

#define PREVIZ_CLASS		PREVIZ_CLASSNAME

//! Simple device layout.
class PreVizLayout : public FBDeviceLayout
{
	//--- FiLMBOX declaration.
	FBDeviceLayoutDeclare( PreVizLayout, FBDeviceLayout );

public:
	//--- FiLMBOX Creation/Destruction.
	virtual bool FBCreate();			//!< FiLMBOX constructor.
	virtual void FBDestroy();			//!< FiLMBOX destructor.

private:
	// Create the UI.
	void UICreate ();
	void UICreateLayout0	();
	void UIConfigure ();
	void UIReset ();
	void UIRefresh ();

	void EventDeviceStatusChange		( HISender pSender, HKEvent pEvent );
	void EventUIIdle					( HISender pSender, HKEvent pEvent );

	// UI Callbacks
	void EventTabPanelChange			( HISender pSender, HKEvent pEvent );
	void EventButtonBrowseJpegSeq		( HISender pSender, HKEvent pEvent );
	void EventButtonStartStop			( HISender pSender, HKEvent pEvent );
	void EventButtonStartStopLD			( HISender pSender, HKEvent pEvent );

	// Tool Callbacks
	void EventToolShow	( HISender pSender, HKEvent pEvent );
	void EventToolIdle	( HISender pSender, HKEvent pEvent );

private:
	FBTabPanel			mTabPanel;
	FBLayout			mLayoutSetup;
		FBLabel				mLabelSetup;
		FBButton			mButtonStartStop;

private:
	FBSystem		mSystem;
	FBApplication	mApplication;

	FBLayout	mLayout[2];
	FBTabPanel	mTabPanel;

	FBLabel		mLabelStart;
	FBLabel		mLabelStop;
	FBLabel		mLabelStartLD;
	FBLabel		mLabelStopLD;

	FBEdit		mEditStart;
	FBEdit		mEditStop;

	FBButton	mButtonJpegSeq;
	FBButton	mButtonStartStop;
	FBButton	mButtonStartStopLD;

};