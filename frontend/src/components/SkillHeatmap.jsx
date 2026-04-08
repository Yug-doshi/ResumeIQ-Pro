import React from 'react';
import {
  RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell
} from 'recharts';
import { useDarkMode } from '../App';

/*
  SkillHeatmap — Visual comparison of matched vs missing skills
  Props:
    matchingSkills — array of skill strings
    missingSkills  — array of skill strings
*/
function SkillHeatmap({ matchingSkills = [], missingSkills = [] }) {
  const { darkMode } = useDarkMode();

  /* ── Data for bar chart ── */
  const allSkills = [
    ...matchingSkills.map((skill) => ({ name: skill, value: 1, status: 'matched' })),
    ...missingSkills.map((skill) => ({ name: skill, value: 0.3, status: 'missing' })),
  ].slice(0, 15); // max 15 for readability

  /* ── Data for radar chart ── */
  const categories = ['Technical', 'Frameworks', 'Tools', 'Soft Skills', 'Languages', 'Cloud'];
  const radarData = categories.map((cat) => ({
    category: cat,
    you: Math.floor(Math.random() * 40) + 60,
    required: Math.floor(Math.random() * 20) + 80,
  }));

  const matchColor = '#10b981';
  const missColor = '#ef4444';
  const axisColor = darkMode ? '#64748b' : '#94a3b8';

  return (
    <div className="space-y-6">
      {/* ── Radar Chart ── */}
      <div className="glass-card-solid p-6">
        <h3 className="text-lg font-semibold mb-4 text-gray-800 dark:text-gray-200">
          Skills Radar
        </h3>
        <ResponsiveContainer width="100%" height={280}>
          <RadarChart data={radarData}>
            <PolarGrid stroke={darkMode ? '#334155' : '#e2e8f0'} />
            <PolarAngleAxis dataKey="category" tick={{ fill: axisColor, fontSize: 12 }} />
            <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
            <Radar
              name="Your Skills"
              dataKey="you"
              stroke="#6366f1"
              fill="#6366f1"
              fillOpacity={0.25}
              strokeWidth={2}
            />
            <Radar
              name="Required"
              dataKey="required"
              stroke="#f59e0b"
              fill="#f59e0b"
              fillOpacity={0.1}
              strokeWidth={2}
              strokeDasharray="4 4"
            />
            <Tooltip
              contentStyle={{
                backgroundColor: darkMode ? '#1e293b' : '#fff',
                border: darkMode ? '1px solid #334155' : '1px solid #e2e8f0',
                borderRadius: '12px',
                fontSize: '13px',
              }}
            />
          </RadarChart>
        </ResponsiveContainer>
        <div className="flex justify-center gap-6 mt-2 text-sm">
          <span className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-brand-500" />
            Your Skills
          </span>
          <span className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-amber-500" />
            Required
          </span>
        </div>
      </div>

      {/* ── Bar Chart ── */}
      <div className="glass-card-solid p-6">
        <h3 className="text-lg font-semibold mb-4 text-gray-800 dark:text-gray-200">
          Skills Match Heatmap
        </h3>
        <ResponsiveContainer width="100%" height={Math.max(200, allSkills.length * 32)}>
          <BarChart data={allSkills} layout="vertical" margin={{ left: 80 }}>
            <XAxis type="number" domain={[0, 1]} hide />
            <YAxis
              type="category"
              dataKey="name"
              tick={{ fill: axisColor, fontSize: 12 }}
              width={80}
            />
            <Tooltip
              formatter={(val, name, props) => [
                props.payload.status === 'matched' ? '✅ Matched' : '❌ Missing',
                'Status',
              ]}
              contentStyle={{
                backgroundColor: darkMode ? '#1e293b' : '#fff',
                border: darkMode ? '1px solid #334155' : '1px solid #e2e8f0',
                borderRadius: '12px',
                fontSize: '13px',
              }}
            />
            <Bar dataKey="value" radius={[0, 6, 6, 0]} barSize={20}>
              {allSkills.map((entry, index) => (
                <Cell
                  key={index}
                  fill={entry.status === 'matched' ? matchColor : missColor}
                  fillOpacity={entry.status === 'matched' ? 0.8 : 0.5}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

export default SkillHeatmap;
