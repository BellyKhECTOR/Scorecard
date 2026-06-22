
import React, { useState } from 'react';
import { Category, ManagerData, ScoreEntry } from '../types';

interface QuestionCardProps {
  question: Category['questions'][0];
  isNonScored: boolean;
  entry: ScoreEntry;
  onEntryChange: (id: number, field: keyof ScoreEntry, value: string | number) => void;
}

const QuestionCard: React.FC<QuestionCardProps> = ({ question, isNonScored, entry, onEntryChange }) => {
    const handleScoreChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        onEntryChange(question.id, 'score', e.target.value);
    };
    
    const handleScoreBlur = (e: React.FocusEvent<HTMLInputElement>) => {
        let value = parseFloat(e.target.value);
        const max = question.availablePoints;
        const min = 0;
        
        if (isNaN(value)) value = min;
        if (value > max) value = max;
        if (value < min) value = min;

        onEntryChange(question.id, 'score', value);
    };

    const handleCommentChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
        onEntryChange(question.id, 'comments', e.target.value);
    };

    return (
        <div className="pt-6 first:pt-0">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-x-6">
                <div>
                    <p className={`text-sm font-medium ${isNonScored ? 'text-gray-400' : 'text-orange-600'}`}>{question.pillar} Pillar</p>
                    <p className={`text-base font-semibold ${isNonScored ? 'text-gray-500' : 'text-gray-900'} mt-1`}>{question.id}. {question.text}</p>
                    {entry.managerAnswer && (
                        <div className="mt-3 bg-gray-50 rounded-lg p-3">
                            <label className="text-xs font-semibold text-gray-500">Manager's Answer</label>
                            <p className="text-sm text-gray-800 whitespace-pre-wrap">{entry.managerAnswer}</p>
                        </div>
                    )}
                    {question.guidance && question.guidance.toLowerCase() !== 'n/a' && (
                        <div className="mt-2">
                            <label className="text-xs font-semibold text-gray-500">Guidance</label>
                            <p className="text-sm text-gray-600">{question.guidance}</p>
                        </div>
                    )}
                </div>
                <div>
                    {isNonScored ? (
                        <div className="h-full flex items-center justify-center">
                            <span className="text-sm text-gray-400 italic">Not scored</span>
                        </div>
                    ) : (
                        <>
                            <div className="flex space-x-4">
                                <div className="w-1/2">
                                    <label htmlFor={`score-${question.id}`} className="block text-sm font-medium text-gray-700">Actual Score</label>
                                    <input
                                        type="number"
                                        id={`score-${question.id}`}
                                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-orange-500 focus:ring-orange-500 sm:text-sm"
                                        value={entry.score}
                                        onChange={handleScoreChange}
                                        onBlur={handleScoreBlur}
                                        max={question.availablePoints}
                                        min="0"
                                        step="0.1"
                                    />
                                </div>
                                <div className="w-1/2">
                                    <label className="block text-sm font-medium text-gray-700">Points Available</label>
                                    <p className="mt-1 text-lg font-medium text-gray-800">{question.availablePoints}</p>
                                </div>
                            </div>
                            <div className="mt-4">
                                <label htmlFor={`comment-${question.id}`} className="block text-sm font-medium text-gray-700">Comments</label>
                                <textarea
                                    id={`comment-${question.id}`}
                                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-orange-500 focus:ring-orange-500 sm:text-sm"
                                    rows={3}
                                    value={entry.comments}
                                    onChange={handleCommentChange}
                                />
                            </div>
                        </>
                    )}
                </div>
            </div>
        </div>
    );
};


interface CategoryAccordionProps {
  category: Category;
  isExpanded: boolean;
  onToggle: () => void;
  managerData: ManagerData;
  onEntryChange: (id: number, field: keyof ScoreEntry, value: string | number) => void;
}

const CategoryAccordion: React.FC<CategoryAccordionProps> = ({ category, isExpanded, onToggle, managerData, onEntryChange }) => {
    const isAdditionalInfo = category.name.toUpperCase() === "ADDITIONAL INFORMATION";
    return (
        <div className="bg-white shadow-lg rounded-2xl overflow-hidden">
            <button
                className="w-full p-5 text-left bg-gray-50 border-b border-gray-200 flex justify-between items-center"
                onClick={onToggle}
            >
                <h3 className="text-xl font-semibold text-gray-800">{category.name}</h3>
                <svg
                    className={`w-6 h-6 text-gray-500 transition-transform duration-300 ${isExpanded ? 'rotate-180' : ''}`}
                    fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"></path>
                </svg>
            </button>
            <div
                className="transition-all duration-500 ease-in-out"
                style={{ maxHeight: isExpanded ? '10000px' : '0', overflow: 'hidden' }}
            >
                <div className="p-5 space-y-6 divide-y divide-gray-100">
                    {category.questions.map(q => (
                        <QuestionCard
                            key={q.id}
                            question={q}
                            isNonScored={q.availablePoints === 0 || isAdditionalInfo}
                            entry={managerData.entries[q.id] || { score: 0, comments: "" }}
                            onEntryChange={onEntryChange}
                        />
                    ))}
                </div>
            </div>
        </div>
    );
};


interface ScorecardViewProps {
  questionTemplate: Category[];
  managerData: ManagerData;
  onEntryChange: (id: number, field: keyof ScoreEntry, value: string | number) => void;
}

const ScorecardView: React.FC<ScorecardViewProps> = ({ questionTemplate, managerData, onEntryChange }) => {
    const [openAccordion, setOpenAccordion] = useState<string | null>(questionTemplate[0]?.name || null);

    const handleToggle = (categoryName: string) => {
        setOpenAccordion(prev => (prev === categoryName ? null : categoryName));
    };

    return (
        <div>
            <p className="text-gray-600 mb-6">Enter the `Actual Score` and `Comments` for each question. The Dashboard will update automatically. Click on a category name to expand or collapse it.</p>
            <div className="space-y-6">
                {questionTemplate.map(category => (
                    <CategoryAccordion
                        key={category.name}
                        category={category}
                        isExpanded={openAccordion === category.name}
                        onToggle={() => handleToggle(category.name)}
                        managerData={managerData}
                        onEntryChange={onEntryChange}
                    />
                ))}
            </div>
        </div>
    );
};

export default ScorecardView;