//--- Class declarations
#include "PreVizDevice.h"
#include "PreVizLayout.h"

#define PREVIZ_LAYOUT	PreVizLayout

//--- FiLMBOX implementation and registration
FBDeviceLayoutImplementation(	PREVIZ_LAYOUT		);
FBRegisterDeviceLayout		(	PREVIZ_LAYOUT,
								PREVIZ_CLASSSTR,
								FB_DEFAULT_SDK_ICON			);	// Icon filename (default=Open Reality icon)

/************************************************
 *	FiLMBOX constructor.
 ************************************************/
bool PreVizLayout::FBCreate()
{
	// Get a handle on the device.
	mDevice = ((PreVizDevice *)(FBDevice *)Device);

	// Create/configure UI
	UICreate	();
	UIConfigure	();
	UIReset		();

	// Add device & system callbacks
	mDevice->OnStatusChange.Add	( this,(FBCallback)&PreVizLayout::EventDeviceStatusChange  );
	mSystem.OnUIIdle.Add		( this,(FBCallback)&PreVizLayout::EventUIIdle              );

	return true;
}


/************************************************
 *	FiLMBOX destructor.
 ************************************************/
void PreVizLayout::FBDestroy()
{
	// Remove device & system callbacks
	mSystem.OnUIIdle.Remove		( this,(FBCallback)&PreVizLayout::EventUIIdle              );
	mDevice->OnStatusChange.Remove	( this,(FBCallback)&PreVizLayout::EventDeviceStatusChange  );
}


/************************************************
 *	Create the UI.
 ************************************************/
void PreVizLayout::UICreate()
{
	int lS, lH;
	lS = 4;
	lH = 25;

	AddRegion	( "MainLayout", "MainLayout",	lS,		kFBAttachLeft,		"",		1.00,
												lS,		kFBAttachBottom,	"",		1.00,
												-lS,	kFBAttachRight,		"",		1.00,
												-lS,	kFBAttachBottom,	"",		1.00 );


	UICreateLayout0();
}


/************************************************
 *	Create the setup layout.
 ************************************************/
void PreVizLayout::UICreateLayout0()
{
	int lS, lW, lH;
	lS = 4;
	lW = 250;
	lH = 18;

	mLayoutSetup.AddRegion(	"StartStopButton",	"StartStopButton",
											lS,		kFBAttachLeft,	"",	1.00,
											lS,		kFBAttachBottom,	"",	1.00,
											lW,		kFBAttachNone,	NULL,	1.00,
											lW,		kFBAttachNone,	NULL,	1.00 );

	mLayoutSetup.SetControl( "StartStopButton",	mButtonStartStop );

	int lS_y	= -15;
	lW			= 100;
	lH			= 25;
	int lHlr	= 100;
	int lWlr	= 250;
	int lWrb	= 140;
	int lSlbx	= 30;
	int lSlby	= 12;
	int lWlb	= 80;
}