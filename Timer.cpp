#include "Timer.h"

#include <Windows.h>

namespace ImageMetrics
{
namespace LiveDriverSDKSample
{
  ///////////////////////////////////////////////////////////////////////////////////////////////////
  Timer::Timer()
    : m_PerformanceFrequency(0.0),
      m_PerformanceCount(0)
  {
    LARGE_INTEGER performanceFrequency;
    QueryPerformanceFrequency(&performanceFrequency);
    m_PerformanceFrequency = double(performanceFrequency.QuadPart) / 1000.0;

    Tick();
  }

  ///////////////////////////////////////////////////////////////////////////////////////////////////
  bool Timer::Tick()
  {
    LARGE_INTEGER performanceCount;
    QueryPerformanceCounter(&performanceCount);
    m_PerformanceCount = performanceCount.QuadPart;

    return false;
  }

  ///////////////////////////////////////////////////////////////////////////////////////////////////
  double Timer::Read() const
  {
    LARGE_INTEGER performanceCount;
    QueryPerformanceCounter(&performanceCount);

    return double(performanceCount.QuadPart - m_PerformanceCount) / m_PerformanceFrequency;
  }

  ///////////////////////////////////////////////////////////////////////////////////////////////////
}
}
