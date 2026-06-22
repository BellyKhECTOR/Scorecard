
export interface Question {
  id: number;
  text: string;
  guidance: string;
  availablePoints: number;
  pillar: string;
}

export interface Category {
  name: string;
  questions: Question[];
}

export interface ScoreEntry {
  score: number;
  comments: string;
  managerAnswer?: string;
}

export interface ManagerInfo {
  name: string;
  level: string;
  type: string;
  marker: string;
}

export interface ManagerData {
  managerInfo: ManagerInfo;
  entries: {
    [questionId: number]: ScoreEntry;
  };
}

export interface CalculatedScores {
  riCategories: { [key: string]: number };
  pillars: { [key: string]: number };
  totalRating: number;
  archetype: string;
}

export type View = 'scorecard' | 'dashboard';

export interface ParsedManager {
  id: string | number;
  name: string;
  answers: { [questionHeader: string]: string | number };
}