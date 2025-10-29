import React from 'react';
import { CalculatedScores } from '../types';
import { archetypeMap, getArchetypeNumber } from '../constants';

interface ScoreBreakdownProps {
  label: string;
  score: number;
  maxScore?: number;
}

const ScoreBreakdown: React.FC<ScoreBreakdownProps> = ({ label, score, maxScore = 5 }) => {
  const percentage = Math.max(0, (score / maxScore) * 100);
  return (
    <div className="mb-2">
      <div className="flex justify-between mb-1">
        <span className="text-sm font-medium text-gray-700">{label}</span>
        <span className="text-sm font-bold text-orange-600">{score.toFixed(2)} / {maxScore.toFixed(0)}</span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2.5">
        <div className="bg-orange-500 h-2.5 rounded-full" style={{ width: `${percentage}%` }}></div>
      </div>
    </div>
  );
};

interface DashboardViewProps {
  scores: CalculatedScores | null;
}

const DashboardView: React.FC<DashboardViewProps> = ({ scores }) => {
  if (!scores) {
    return (
      <div className="text-center p-8">
        <p className="text-gray-600">Calculating scores...</p>
      </div>
    );
  }

  const { riCategories, pillars, totalRating, archetype } = scores;
  const archetypeNum = getArchetypeNumber(totalRating);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div className="lg:col-span-1 space-y-6">
        <div className="bg-white shadow-lg rounded-2xl p-6 text-center">
          <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wider">Actual Total ESG Rating</h3>
          <p className="text-7xl font-bold text-orange-600 my-4">{totalRating.toFixed(2)}</p>
          <p className="text-2xl font-semibold px-6 py-3 rounded-full bg-orange-100 text-orange-800">
            {archetype}
          </p>
        </div>

        <div className="bg-white shadow-lg rounded-2xl p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">ESG Archetypes</h3>
          <ul className="space-y-2 text-sm">
            {[
              { num: 1, range: '0.0 - 1.4' },
              { num: 2, range: '1.5 - 2.4' },
              { num: 3, range: '2.5 - 3.4' },
              { num: 4, range: '3.5 - 4.4' },
              { num: 5, range: '4.5 - 5.0' },
            ].map(({ num, range }) => (
              <li key={num} className={`flex justify-between p-2 rounded-md ${archetypeNum === num ? 'bg-orange-100 font-semibold' : ''}`}>
                <span>{num}: {archetypeMap[num]}</span>
                <span className="font-medium">{range}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      <div className="lg:col-span-2 space-y-6">
        <div className="bg-white shadow-lg rounded-2xl p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">RI Category Scoring</h3>
          <div className="space-y-4">
            {Object.entries(riCategories)
              .filter(([name]) => name.toUpperCase() !== "CLIMATE CHANGE" && name.toUpperCase() !== "ADDITIONAL INFORMATION")
              .map(([name, score]) => (
                <ScoreBreakdown key={name} label={name} score={score} />
            ))}
            <div className="border-t border-gray-200 pt-4 mt-4">
              <ScoreBreakdown label="CLIMATE CHANGE (Informational)" score={riCategories["CLIMATE CHANGE"] || 1} />
            </div>
          </div>
        </div>

        <div className="bg-white shadow-lg rounded-2xl p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Five Pillar Scoring</h3>
          <div className="space-y-4">
            {Object.entries(pillars).map(([name, score]) => (
              <ScoreBreakdown key={name} label={name} score={score} />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardView;