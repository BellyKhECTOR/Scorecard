
import { GoogleGenAI } from "@google/genai";
// We no longer import xlsx here, we will access it from the window object.
import { Category, ScoreEntry, ParsedManager } from '../types';

const ai = new GoogleGenAI({ apiKey: process.env.API_KEY as string });

export const parseManagersFromXLSX = (file: File): Promise<ParsedManager[]> => {
  return new Promise((resolve, reject) => {
      const XLSX = (window as any).XLSX;

      if (!XLSX) {
        return reject(new Error("The XLSX library failed to load. Please check your internet connection and refresh."));
      }

      const reader = new FileReader();
      reader.onload = (event) => {
          try {
              const data = event.target?.result;
              if (!data) {
                  throw new Error("File could not be read.");
              }
              const workbook = XLSX.read(data, { type: 'array' });
              const inputSheetName = workbook.SheetNames.find(name => name.toLowerCase() === 'input');
              const sheetName = inputSheetName || workbook.SheetNames[0];
              
              if (!sheetName) {
                  throw new Error("No sheets found in the XLSX file.");
              }
              const worksheet = workbook.Sheets[sheetName];
              const jsonData = XLSX.utils.sheet_to_json(worksheet) as Array<{[key: string]: string | number}>;

              if (jsonData.length === 0) {
                throw new Error("The selected sheet contains no data.");
              }

              const originalHeaders = Object.keys(jsonData[0]);
              
              const managerNameHeaderKey = "Full name of person(s) completing this form";
              const idHeaderKey = "id";

              let managerNameHeader = originalHeaders.find(h => h.trim().toLowerCase() === managerNameHeaderKey.toLowerCase());
              let idHeader = originalHeaders.find(h => h.trim().toLowerCase() === idHeaderKey.toLowerCase());

              if (!managerNameHeader) {
                  throw new Error(`Could not find the required manager name column: "${managerNameHeaderKey}". Please ensure your XLSX file has this column.`);
              }
              if (!idHeader) {
                  throw new Error(`Could not identify an 'ID' column. An 'ID' column is required to uniquely identify each manager.`);
              }
              
              const metadataHeadersToExclude = [
                idHeader.trim().toLowerCase(),
                managerNameHeader.trim().toLowerCase(),
                "start time",
                "completion time",
                "email",
                "name",
                "last modified time",
              ];

              const parsedData = jsonData.map(row => {
                  const managerName = row[managerNameHeader!]?.toString().trim();
                  const managerId = row[idHeader!];
                  if (!managerName || managerId === undefined || managerId === null) {
                      return null;
                  }

                  const answers: { [key: string]: string | number } = {};
                  Object.keys(row).forEach(header => {
                      if (!metadataHeadersToExclude.includes(header.trim().toLowerCase())) {
                          answers[header] = row[header];
                      }
                  });

                  return {
                      id: managerId,
                      name: managerName,
                      answers: answers,
                  };
              }).filter((p): p is ParsedManager => p !== null);

              if (parsedData.length === 0) {
                  throw new Error("No managers with both an ID and a name were found in the file.");
              }

              resolve(parsedData);
          } catch (error) {
              if (error instanceof Error) {
                 reject(new Error(`Failed to parse XLSX file: ${error.message}`));
              } else {
                 reject(new Error("An unknown error occurred while parsing the XLSX file."));
              }
          }
      };
      reader.onerror = (error) => reject(new Error("Error reading file."));
      reader.readAsArrayBuffer(file);
  });
};


export const suggestScoresFromManagerAnswers = async (
  managerAnswers: { [questionHeader: string]: string | number },
  questionTemplate: Category[]
): Promise<{ [questionId: number]: ScoreEntry }> => {
  try {
    const prompt = `
      You are an expert ESG analyst. Your task is to analyze a manager's responses from a Due Diligence Questionnaire (DDQ) and score them against a predefined scoring framework.

      Here is the scoring framework, which contains the official questions, guidance, and question IDs:
      ${JSON.stringify(questionTemplate, null, 2)}

      Here is the manager's completed DDQ, extracted from a spreadsheet. The keys are the questions as they appeared in the spreadsheet, and the values are the manager's answers:
      ${JSON.stringify(managerAnswers, null, 2)}

      Your task is to:
      1. For each question in the scoring framework, find the BEST matching question from the manager's DDQ answers. The wording might not be identical, so use your understanding of the topics to find the correct correspondence.
      2. Once you have matched a question, analyze the manager's answer for it.
      3. Based on the scoring 'guidance' in the framework for that question, assign a numerical score. The score must be between 0 and the 'availablePoints'.
      4. Provide a brief, concise comment justifying your score.
      5. Include the manager's answer that you used for scoring in the response object under the key "managerAnswer". If you cannot find a matching answer, this should be an empty string.
      6. For questions in the framework with 'availablePoints' of 0, set the score to 0 and the comment to an empty string. Still provide the manager's answer in the "managerAnswer" field if you find one.

      Return your complete analysis as a single JSON object where keys are the question IDs from the scoring framework (as strings) and values are objects with "score", "comments", and "managerAnswer" properties. Do not include any other text, explanations, or markdown formatting in your response. Ensure you provide an entry for EVERY question ID in the framework.
      Example for question ID 4: { "4": { "score": 4, "comments": "The manager states a fully integrated approach, which aligns with the higher end of the scoring guidance.", "managerAnswer": "Our approach is integrated..." } }
    `;

    const response = await ai.models.generateContent({
      model: 'gemini-2.5-flash',
      contents: prompt,
      config: {
        responseMimeType: 'application/json',
      },
    });

    const text = response.text;
    if (!text) {
      throw new Error("The AI returned an empty response.");
    }

    try {
        const result = JSON.parse(text) as { [questionId: string]: ScoreEntry };
        // Convert keys from string to number
        const formattedResult: { [questionId: number]: ScoreEntry } = {};
        for (const key in result) {
            if (Object.prototype.hasOwnProperty.call(result, key)) {
                formattedResult[Number(key)] = result[key];
            }
        }
        return formattedResult;
    } catch (parseError) {
        console.error("Error parsing AI response JSON:", parseError);
        console.error("Raw AI response:", text);
        throw new Error("The AI returned a response that was not valid JSON. Please check the console for the raw response.");
    }

  } catch (error) {
    console.error("Error analyzing manager answers with Gemini:", error);
    if (error instanceof Error) {
        throw new Error(`Failed to get scoring suggestions from AI: ${error.message}`);
    }
    throw new Error("Failed to get scoring suggestions from AI due to an unknown error. Please check the console for details.");
  }
};