import React, { useEffect, useState } from 'react';

/*
  ScoreGauge — Animated circular gauge for displaying ATS scores
  Props:
    score      — number 0-100
    size       — pixel diameter (default 180)
    label      — text label below score
    color      — stroke color override
*/
function ScoreGauge({ score = 0, size = 180, label = 'ATS Score', color }) {
  const [animatedScore, setAnimatedScore] = useState(0);

  /* animate the number counting up */
  useEffect(() => {
    let start = 0;
    const step = Math.ceil(score / 40);
    const timer = setInterval(() => {
      start += step;
      if (start >= score) {
        start = score;
        clearInterval(timer);
      }
      setAnimatedScore(start);
    }, 30);
    return () => clearInterval(timer);
  }, [score]);

  /* SVG circle math */
  const strokeWidth = 12;
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const progress = ((100 - score) / 100) * circumference;

  /* color based on score */
  const getColor = () => {
    if (color) return color;
    if (score >= 75) return '#10b981';
    if (score >= 50) return '#f59e0b';
    if (score >= 25) return '#f97316';
    return '#ef4444';
  };

  const strokeColor = getColor();

  return (
    <div className="flex flex-col items-center">
      <div className="relative" style={{ width: size, height: size }}>
        <svg width={size} height={size} className="-rotate-90">
          {/* background track */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke="currentColor"
            strokeWidth={strokeWidth}
            className="text-gray-200 dark:text-gray-700"
          />
          {/* progress arc */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke={strokeColor}
            strokeWidth={strokeWidth}
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={progress}
            className="gauge-circle"
            style={{ filter: `drop-shadow(0 0 6px ${strokeColor}40)` }}
          />
        </svg>
        {/* center number */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-4xl font-bold" style={{ color: strokeColor }}>
            {animatedScore}
          </span>
          <span className="text-xs text-gray-500 dark:text-gray-400 mt-1 font-medium">{label}</span>
        </div>
      </div>
    </div>
  );
}

export default ScoreGauge;
