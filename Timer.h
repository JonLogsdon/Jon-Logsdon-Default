#pragma once

namespace ImageMetrics
{
namespace LiveDriverSDKSample
{
  class Timer
  {
  public:
    Timer();

    bool Tick();
    double Read() const;

  private:
    double m_PerformanceFrequency;
    __int64 m_PerformanceCount;
  };
}
}
