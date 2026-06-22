
import React, { useState, useMemo, useRef } from 'react';
import { questionTemplate, preloadedData, archetypeMap, getArchetypeNumber } from './constants';
import { ManagerData, ManagerInfo, ScoreEntry, View, CalculatedScores, ParsedManager } from './types';
import ScorecardView from './components/ScorecardView';
import DashboardView from './components/DashboardView';
import { parseManagersFromXLSX, suggestScoresFromManagerAnswers } from './services/geminiService';

const App: React.FC = () => {
    const [currentManagerData, setCurrentManagerData] = useState<ManagerData>(
        JSON.parse(JSON.stringify(preloadedData.prescient))
    );
    const [activeView, setActiveView] = useState<View>('scorecard');
    const [isLoadingAi, setIsLoadingAi] = useState<boolean>(false);
    const [parsedManagers, setParsedManagers] = useState<ParsedManager[] | null>(null);
    const [selectedParsedManagerId, setSelectedParsedManagerId] = useState<string | number | null>(null);
    const [managerSelectValue, setManagerSelectValue] = useState('prescient');
    const [errorMessage, setErrorMessage] = useState<string | null>(null);

    const scores = useMemo<CalculatedScores>(() => {
        const riCategoryScores: { [key: string]: number } = {};
        const riCategoryTotals: { [key: string]: number } = {};
        const pillarScores: { [key: string]: number } = {};
        const pillarTotals: { [key: string]: number } = {};

        const allPillars = new Set<string>();
        questionTemplate.forEach(cat => {
            riCategoryScores[cat.name] = 0;
            riCategoryTotals[cat.name] = 0;
            cat.questions.forEach(q => {
                if (q.availablePoints > 0) allPillars.add(q.pillar);
            });
        });
        allPillars.forEach(p => {
            pillarScores[p] = 0;
            pillarTotals[p] = 0;
        });

        questionTemplate.forEach(cat => {
            cat.questions.forEach(q => {
                const points = q.availablePoints || 0;
                const entry = currentManagerData.entries[q.id] || { score: 0 };
                const score = entry.score || 0;

                if (points > 0) {
                    riCategoryScores[cat.name] += score;
                    riCategoryTotals[cat.name] += points;
                    if (pillarScores.hasOwnProperty(q.pillar)) {
                        pillarScores[q.pillar] += score;
                        pillarTotals[q.pillar] += points;
                    }
                }
            });
        });
        
        const finalRiScores: { [key: string]: number } = {};
        for (const catName in riCategoryScores) {
            const total = riCategoryTotals[catName];
            const score = riCategoryScores[catName];
            finalRiScores[catName] = total > 0 ? (score / total) * 4 + 1 : 1;
        }

        const finalPillarScores: { [key: string]: number } = {};
        for (const pillarName in pillarScores) {
            const total = pillarTotals[pillarName];
            const score = pillarScores[pillarName];
            finalPillarScores[pillarName] = total > 0 ? (score / total) * 4 + 1 : 1;
        }
        
        let totalRatingSum = 0;
        let totalRatingCount = 0;
        for (const [name, score] of Object.entries(finalRiScores)) {
            if (name.toUpperCase() !== "CLIMATE CHANGE" && name.toUpperCase() !== "ADDITIONAL INFORMATION") {
                if (riCategoryTotals[name] > 0) {
                    totalRatingSum += score;
                    totalRatingCount++;
                }
            }
        }
        const totalRating = totalRatingCount > 0 ? totalRatingSum / totalRatingCount : 1;

        const archetypeNum = getArchetypeNumber(totalRating);
        const archetype = archetypeMap[archetypeNum];

        return { riCategories: finalRiScores, pillars: finalPillarScores, totalRating, archetype };
    }, [currentManagerData]);

    const handleManagerInfoChange = (field: keyof ManagerInfo, value: string) => {
        setCurrentManagerData(prev => ({
            ...prev,
            managerInfo: { ...prev.managerInfo, [field]: value }
        }));
    };

    const handleEntryChange = (id: number, field: keyof ScoreEntry, value: string | number) => {
        const processedValue = field === 'score' && typeof value === 'string' ? parseFloat(value) : value;
        setCurrentManagerData(prev => ({
            ...prev,
            entries: {
                ...prev.entries,
                [id]: { ...(prev.entries[id] || { score: 0, comments: '' }), [field]: processedValue }
            }
        }));
    };

    const generateBlankScorecard = () => {
        const blankData: ManagerData = {
            managerInfo: { name: "New Manager", level: "", type: "", marker: "" },
            entries: {}
        };
        questionTemplate.forEach(category => {
            category.questions.forEach(q => {
                blankData.entries[q.id] = { score: 0, comments: "", managerAnswer: "" };
            });
        });
        return blankData;
    };
    
    const handleManagerSelectChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
        const selected = e.target.value;
        setManagerSelectValue(selected);
        setParsedManagers(null);
        setSelectedParsedManagerId(null);

        if (selected === 'blank') {
            setCurrentManagerData(generateBlankScorecard());
        } else if (selected === 'prescient') {
            setCurrentManagerData(JSON.parse(JSON.stringify(preloadedData.prescient)));
        }
    };
    
    const handleExport = () => {
        const managerName = currentManagerData.managerInfo.name || "Untitled_Manager";
        const filename = `${managerName.replace(/ /g, '_')}_ESG_Scorecard.json`;
        const dataStr = JSON.stringify(currentManagerData, null, 2);
        const dataBlob = new Blob([dataStr], { type: "application/json" });
        
        const link = document.createElement('a');
        link.href = URL.createObjectURL(dataBlob);
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };

    const handleJsonFileImport = (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];
        if (!file) return;
        setErrorMessage(null);
        
        const reader = new FileReader();
        reader.onload = (e) => {
            try {
                const loadedData = JSON.parse(e.target?.result as string);
                if (loadedData.managerInfo && loadedData.entries) {
                    setCurrentManagerData(loadedData);
                    setManagerSelectValue('custom');
                    setParsedManagers(null);
                    setSelectedParsedManagerId(null);
                } else {
                    setErrorMessage("Invalid JSON file. Must be a valid scorecard file.");
                }
            } catch (error) {
                if (error instanceof Error) {
                     setErrorMessage("Error reading file: " + error.message);
                } else {
                     setErrorMessage("An unknown error occurred while reading the file.");
                }
            }
        };
        reader.readAsText(file);
        event.target.value = ''; 
    };

    const scoreManager = async (manager: ParsedManager) => {
        setErrorMessage(null);
        setIsLoadingAi(true);
    
        try {
            const newBlank = generateBlankScorecard();
            setCurrentManagerData(prev => ({
                ...newBlank,
                managerInfo: { 
                    ...prev.managerInfo, 
                    name: manager.name,
                    level: '', 
                    type: '',
                }
            }));
    
            const suggestedEntries = await suggestScoresFromManagerAnswers(manager.answers, questionTemplate);
            
            setCurrentManagerData(prev => ({
                ...prev,
                entries: { ...prev.entries, ...suggestedEntries }
            }));
    
        } catch (error) {
            const errorMessage = error instanceof Error ? error.message : "An unknown error occurred.";
            setErrorMessage(`AI Scoring Failed: ${errorMessage}`);
        } finally {
            setIsLoadingAi(false);
        }
    };

    const handleXlsxUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];
        if (!file) return;

        setErrorMessage(null);
        setIsLoadingAi(true);
        try {
            const managers = await parseManagersFromXLSX(file);
            setParsedManagers(managers);
            if (managers.length > 0) {
                const firstManager = managers[0];
                setManagerSelectValue('xlsx');
                setSelectedParsedManagerId(firstManager.id);
                await scoreManager(firstManager);
            }
        } catch (error) {
            const errorMessage = error instanceof Error ? error.message : "An unknown error occurred.";
            setErrorMessage(`Error processing XLSX file: ${errorMessage}`);
            setParsedManagers(null);
        } finally {
            setIsLoadingAi(false);
            event.target.value = '';
        }
    };
    
    const handleParsedManagerChange = async (e: React.ChangeEvent<HTMLSelectElement>) => {
        const selectedId = e.target.value;
        const selectedManager = parsedManagers?.find(m => m.id.toString() === selectedId);
        
        if (selectedManager) {
            setSelectedParsedManagerId(selectedManager.id);
            await scoreManager(selectedManager);
        }
    };

    const ErrorBanner = () => (
        <div className="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 rounded-md relative mb-6" role="alert">
            <div className="flex">
                <div className="py-1">
                    <svg className="fill-current h-6 w-6 text-red-500 mr-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20"><path d="M2.93 17.07A10 10 0 1 1 17.07 2.93 10 10 0 0 1 2.93 17.07zM11.414 10l2.829-2.828a1 1 0 1 0-1.415-1.415L10 8.586 7.172 5.757a1 1 0 0 0-1.415 1.415L8.586 10l-2.829 2.828a1 1 0 1 0 1.415 1.415L10 11.414l2.828 2.829a1 1 0 0 0 1.415-1.415L11.414 10z"/></svg>
                </div>
                <div>
                    <p className="font-bold">An error occurred</p>
                    <p className="text-sm">{errorMessage}</p>
                </div>
            </div>
            <button
                onClick={() => setErrorMessage(null)}
                className="absolute top-0 bottom-0 right-0 px-4 py-3"
                aria-label="Close"
            >
                <svg className="fill-current h-6 w-6 text-red-400 hover:text-red-600" role="button" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20"><title>Close</title><path d="M14.348 14.849a1.2 1.2 0 0 1-1.697 0L10 11.819l-2.651 3.029a1.2 1.2 0 1 1-1.697-1.697l2.758-3.15-2.759-3.152a1.2 1.2 0 1 1 1.697-1.697L10 8.183l2.651-3.031a1.2 1.2 0 1 1 1.697 1.697l-2.758 3.152 2.758 3.15a1.2 1.2 0 0 1 0 1.698z"/></svg>
            </button>
        </div>
    );

    return (
      <>
        <div className="container mx-auto p-4 md:p-8 max-w-7xl">
            {errorMessage && <ErrorBanner />}
            {/* Header Card */}
            <div className="bg-white shadow-xl rounded-2xl p-6 md:p-8 mb-6">
                <h1 className="text-3xl font-bold text-gray-900">ESG Due Diligence Scorecard</h1>
                <p className="mt-2 text-lg text-gray-600">A web-based tool for scoring manager ESG performance based on the RisCura framework.</p>

                <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4 border-t border-gray-200 pt-6">
                    {(Object.keys(currentManagerData.managerInfo) as Array<keyof ManagerInfo>).map(key => (
                        <div key={key}>
                            <label htmlFor={`info-${key}`} className="text-sm font-medium text-gray-500 capitalize">{key === 'type' ? 'Asset Class' : key}</label>
                            <input
                                type="text"
                                id={`info-${key}`}
                                className="info-input text-lg font-semibold text-gray-900 border-0 border-b-2 border-transparent focus:border-orange-500 focus:ring-0 p-0 w-full"
                                value={currentManagerData.managerInfo[key]}
                                onChange={(e) => handleManagerInfoChange(key, e.target.value)}
                            />
                        </div>
                    ))}
                </div>
            </div>

             {/* Data Management Bar */}
            <div className="bg-white shadow-lg rounded-2xl p-4 mb-6 flex flex-col md:flex-row items-center justify-between gap-4">
                <div className="flex flex-wrap items-center gap-4">
                    <div className="flex items-center gap-2">
                        <label htmlFor="manager-select" className="text-sm font-medium text-gray-700">Load:</label>
                        <select id="manager-select" value={managerSelectValue} onChange={handleManagerSelectChange} className="rounded-md border-gray-300 shadow-sm focus:border-orange-500 focus:ring-orange-500 text-sm">
                            <option value="prescient">Prescient (Demo)</option>
                            <option value="blank">New Blank Scorecard</option>
                            {managerSelectValue === 'custom' && <option value="custom">Imported (JSON)</option>}
                             {managerSelectValue === 'xlsx' && <option value="xlsx">From XLSX File</option>}
                        </select>
                    </div>
                    {managerSelectValue === 'xlsx' && parsedManagers && parsedManagers.length > 0 && (
                         <div className="flex items-center gap-2">
                            <label htmlFor="parsed-manager-select" className="text-sm font-medium text-gray-700">Manager:</label>
                            <select id="parsed-manager-select" value={selectedParsedManagerId ?? ''} onChange={handleParsedManagerChange} className="rounded-md border-gray-300 shadow-sm focus:border-orange-500 focus:ring-orange-500 text-sm">
                                {parsedManagers.map(manager => (
                                    <option key={manager.id} value={manager.id}>
                                        ID: {manager.id} - {manager.name}
                                    </option>
                                ))}
                            </select>
                        </div>
                    )}
                </div>
                <div className="flex items-center gap-3">
                    <input type="file" id="xlsx-upload" onChange={handleXlsxUpload} className="hidden" accept=".xlsx, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" disabled={isLoadingAi} />
                    <label htmlFor="xlsx-upload" className={`inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 ${isLoadingAi ? 'bg-gray-400 cursor-not-allowed' : 'bg-green-600 hover:bg-green-700 cursor-pointer'}`}>
                        {isLoadingAi && selectedParsedManagerId === null ? (
                             <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                            </svg>
                        ) : (
                            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor"><path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" /></svg>
                        )}
                        {isLoadingAi ? 'Processing...' : 'Auto-score with AI (XLSX)'}
                    </label>
                    <input type="file" id="json-upload" onChange={handleJsonFileImport} className="hidden" accept=".json,application/json" />
                    <label htmlFor="json-upload" className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md shadow-sm text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-orange-500 cursor-pointer">
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2"><path strokeLinecap="round" strokeLinejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" /></svg>
                        Import JSON
                    </label>
                    <button onClick={handleExport} className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-orange-600 hover:bg-orange-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-orange-500">
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2"><path strokeLinecap="round" strokeLinejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" /></svg>
                        Export to JSON
                    </button>
                </div>
            </div>

            {/* Tab Navigation */}
            <div className="mb-6">
                <nav className="flex space-x-4 border-b border-gray-300">
                    <button onClick={() => setActiveView('scorecard')} className={`text-lg font-medium py-3 px-5 border-b-2 transition-colors duration-200 ${activeView === 'scorecard' ? 'border-orange-500 text-orange-600' : 'border-transparent text-gray-600 hover:text-gray-800'}`}>
                        Scorecard
                    </button>
                    <button onClick={() => setActiveView('dashboard')} className={`text-lg font-medium py-3 px-5 border-b-2 transition-colors duration-200 ${activeView === 'dashboard' ? 'border-orange-500 text-orange-600' : 'border-transparent text-gray-600 hover:text-gray-800'}`}>
                        Dashboard
                    </button>
                </nav>
            </div>
            
            {/* Tab Content */}
            <div>
                {activeView === 'scorecard' && (
                    <ScorecardView 
                        questionTemplate={questionTemplate} 
                        managerData={currentManagerData}
                        onEntryChange={handleEntryChange}
                    />
                )}
                {activeView === 'dashboard' && <DashboardView scores={scores} />}
            </div>
        </div>
      </>
    );
};

export default App;