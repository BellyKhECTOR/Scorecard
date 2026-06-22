
import { Category, ManagerData } from './types';

export const questionTemplate: Category[] = [
    {
        name: "GOVERNANCE",
        questions: [
            { id: 4, text: "What is your organisation’s overall approach to responsible investment?", guidance: "Score 1-5. 5 = fully integrated, 1 = no approach.", availablePoints: 5, pillar: "Principles" },
            { id: 5, text: "Does your organisation have a formal policy or policies covering your approach to responsible investment?", guidance: "5 = Yes and public, 3 = Yes but private, 0 = No.", availablePoints: 5, pillar: "Policy" },
            { id: 6, text: "If yes, is your policy or policies publicly available?", guidance: "Auto-scored based on selection.", availablePoints: 0, pillar: "Policy" },
            { id: 7, text: "If you said yes, please provide a link to your policy", guidance: "No score. For info only.", availablePoints: 0, pillar: "Policy" },
            { id: 8, text: "When was your policy last reviewed and updated", guidance: "No score. For info only.", availablePoints: 0, pillar: "Policy" },
            { id: 9, text: "Does your organisation have an exclusion policy?", guidance: "5 = Yes, 0 = No.", availablePoints: 5, pillar: "Policy" },
            { id: 10, text: "Is your organisation a signatory of the PRI?", guidance: "5 = Yes, 0 = No.", availablePoints: 5, pillar: "Principles" },
            { id: 11, text: "When did you become a signatory to the PRI", guidance: "No score. For info.", availablePoints: 0, pillar: "Principles" },
            { id: 12, text: "What international standards, industry (association) guidelines, reporting frameworks, or initiatives that promote responsible investment practices has your organisation committed to, participates in or supports? ", guidance: "1 point per selection (max 5)", availablePoints: 5, pillar: "Principles" },
            { id: 13, text: "Do your organisation's board, C-Suite, investment committee and/or head of department have formal oversight and accountability for responsible investment?", guidance: "5 = Yes, 0 = No.", availablePoints: 5, pillar: "People" },
            { id: 14, text: "Who has ultimate oversight of responsible investment at your organisation?", guidance: "Score 1-5. 5 = Dedicated committee/Board, 1 = No oversight.", availablePoints: 5, pillar: "People" }
        ]
    },
    {
        name: "ESG INTEGRATION",
        questions: [
            { id: 15, text: "How does your organisation integrate ESG factors into its investment decision-making processes?", guidance: "Score 1-5 based on depth of integration.", availablePoints: 5, pillar: "Process" },
            { id: 16, text: "Does your organisation use ESG data providers (e.g. MSCI, Sustainalytics, etc.)?", guidance: "No score. For info.", availablePoints: 0, pillar: "Process" },
            { id: 17, text: "How does your organisation use third-party ESG data providers? ", guidance: "Score 1-5. 5 = Input to proprietary model, 3 = Used directly, 1 = Not used.", availablePoints: 5, pillar: "Process" },
            { id: 18, text: "Does your organisation systematically identify and manage material ESG risks and opportunities?", guidance: "5 = Yes (systematic), 3 = Ad-hoc, 0 = No.", availablePoints: 5, pillar: "Process" },
            { id: 19, text: "Does your organisation engage with its investee companies on ESG issues?", guidance: "5 = Yes, 0 = No.", availablePoints: 5, pillar: "Process" },
            { id: 20, text: "How does your organisation typically engage with investee companies on ESG issues? ", guidance: "1 point per selection (max 5)", availablePoints: 5, pillar: "Process" },
            { id: 21, text: "What is your organisation's escalation strategy if engagement with an investee company is unsuccessful?", guidance: "1 point per selection (max 5)", availablePoints: 5, pillar: "Process" },
            { id: 22, text: "Does your organisation have a formal stewardship or proxy voting policy?", guidance: "5 = Yes, 0 = No.", availablePoints: 5, pillar: "Policy" },
            { id: 23, text: "Is your stewardship or proxy voting policy publicly available?", guidance: "Auto-scored.", availablePoints: 0, pillar: "Policy" },
            { id: 24, text: "In which instances does your organisation vote against management?", guidance: "Score 1-5. 5 = Clear detailed criteria, 3 = Vague, 1 = Never.", availablePoints: 5, pillar: "Process" },
            { id: 25, text: "Has your organisation ever filed or co-filed an ESG-related resolution?", guidance: "5 = Yes, 0 = No.", availablePoints: 5, pillar: "Policy" },
            { id: 26, text: "Does your organisation have dedicated ESG staff/a dedicated ESG team?", guidance: "5 = Yes, 0 = No.", availablePoints: 5, pillar: "People" },
            { id: 27, text: "What ESG training does your organisation provide to its staff?", guidance: "Score 1-5. 5 = Systematic/mandatory, 3 = Ad-hoc, 1 = None.", availablePoints: 5, pillar: "People" }
        ]
    },
    {
        name: "TRANSPARENCY",
        questions: [
            { id: 28, text: "How does your organisation report on its responsible investment and stewardship activities?", guidance: "5 = Detailed, public report. 3 = Client-only. 1 = None.", availablePoints: 5, pillar: "Performance" },
            { id: 29, text: "Is your organisation's reporting on responsible investment and stewardship activities publicly available?", guidance: "Auto-scored.", availablePoints: 0, pillar: "Performance" },
            { id: 30, text: "Does your organisation measure and report on the outcomes of its ESG engagements?", guidance: "5 = Yes (detailed outcomes), 3 = Yes (activity only), 0 = No.", availablePoints: 5, pillar: "Performance" },
            { id: 31, text: "Does your organisation provide case studies of its ESG engagements and their outcomes?", guidance: "5 = Yes, 0 = No.", availablePoints: 5, pillar: "Performance" },
            { id: 32, text: "Does your organisation report on its proxy voting records?", guidance: "5 = Yes (publicly), 3 = Yes (to clients), 0 = No.", availablePoints: 5, pillar: "Performance" },
            { id: 33, text: "How frequently does your organisation report on its proxy voting records?", guidance: "Score 1-5. 5 = Quarterly/Live, 3 = Annually, 1 = Ad-hoc.", availablePoints: 5, pillar: "Performance" },
            { id: 34, text: "Does your organisation undergo any external verification or assurance of its responsible investment processes?", guidance: "5 = Yes, 0 = No.", availablePoints: 5, pillar: "Performance" }
        ]
    },
    {
        name: "CLIMATE CHANGE",
        questions: [
            { id: 35, text: "Does your organisation's responsible investment policy explicitly address climate change?", guidance: "5 = Yes, 0 = No.", availablePoints: 5, pillar: "Policy" },
            { id: 36, text: "Does your organisation measure the carbon footprint/financed emissions of its portfolios?", guidance: "5 = Yes (all/systematic), 3 = Yes (partial/ad-hoc), 0 = No.", availablePoints: 5, pillar: "Performance" },
            { id: 37, text: "How does your organisation measure the carbon footprint of its portfolios?", guidance: "Score 1-5. 5 = Detailed proprietary/third party, 1 = Basic.", availablePoints: 5, pillar: "Performance" },
            { id: 38, text: "Does your organisation conduct climate-related scenario analysis (e.g. TCFD) on its portfolios?", guidance: "5 = Yes, 0 = No.", availablePoints: 5, pillar: "Performance" },
            { id: 39, text: "Does your organisation have any climate-related targets for its portfolios?", guidance: "5 = Yes (clear targets), 3 = Vague goals, 0 = No.", availablePoints: 5, pillar: "Performance" },
            { id: 40, text: "Has your organisation calculated its financed emissions (for relevant asset classes)?", guidance: "5 = Yes (all), 3 = Yes (partial), 0 = No.", availablePoints: 5, pillar: "Performance" }
        ]
    },
    {
        name: "ADDITIONAL INFORMATION",
        questions: [
            { id: 74, text: "How does your organisation manage its internal ESG risks, opportunities and impacts?", guidance: "N/A", availablePoints: 0, pillar: "Process" },
            { id: 75, text: "Is there any information on your organisation’s responsible investment approach, not otherwise covered in the DDQ, that you would like to share? ", guidance: "N/A", availablePoints: 0, pillar: "Process" },
            { id: 76, text: "Document Checklist - Please select which of the following documentation you have provided to support your answers to this DDQ.", guidance: "N/A", availablePoints: 0, pillar: "Policy" }
        ]
    }
];

export const preloadedData: { prescient: ManagerData } = {
    prescient: {
        managerInfo: {
            name: "Prescient",
            level: "Developed",
            type: "Listed Equity",
            marker: "Hector",
        },
        entries: {
            4: { score: 4, comments: "RI is integrated into their investment process and they have a philosophy document to support this. ", managerAnswer: "Our approach is integrated, with RI forming a core part of our investment process." },
            5: { score: 5, comments: "Prescient has a RI policy. ", managerAnswer: "Yes" },
            6: { score: 0, comments: "", managerAnswer: "Yes" },
            7: { score: 0, comments: "", managerAnswer: "https://www.prescient.co.za/responsible-investing/" },
            8: { score: 0, comments: "", managerAnswer: "2024-03-01" },
            9: { score: 5, comments: "", managerAnswer: "Yes" },
            10: { score: 5, comments: "", managerAnswer: "Yes" },
            11: { score: 0, comments: "", managerAnswer: "2019-05-01" },
            12: { score: 3, comments: "They are supporters of the TCFD, UNSDGs and CRISA", managerAnswer: "(B) Task Force on Climate-related Financial Disclosures (TCFD) Supporter;(C) UN Sustainable Development Goals (SDGs);(E) Code for Responsible Investing in South Africa (CRISA) Supporter;" },
            13: { score: 5, comments: "", managerAnswer: "Yes" },
            14: { score: 5, comments: "Prescient has a dedicated RI committee ", managerAnswer: "The Prescient Holdings Board has ultimate oversight of responsible investment. The Board has delegated the day-to-day oversight and implementation to the Group RI Committee." },
            15: { score: 4, comments: "This is a good approach - it ensures that those making the investment decisions are the ones thinking about ESG. ", managerAnswer: "We follow an integrated approach where ESG factors are incorporated into our investment decision-making and ownership practices. We do not have a separate ESG team but rather believe that ESG considerations should be integrated within the research and analysis function performed by our investment professionals." },
            16: { score: 0, comments: "", managerAnswer: "Yes" },
            17: { score: 5, comments: "", managerAnswer: "We use it as an input into our proprietary ESG scoring model." },
            18: { score: 5, comments: "", managerAnswer: "Yes, this is part of our risk management framework." },
            19: { score: 5, comments: "", managerAnswer: "Yes" },
            20: { score: 2, comments: "They engage directly and collaboratively ", managerAnswer: "(A) We engage directly with the company's management;(B) We engage collaboratively with other investors;" },
            21: { score: 2, comments: "", managerAnswer: "(A) We will continue to engage with the company;(C) We will vote against management at the AGM/EGM;" },
            22: { score: 5, comments: "", managerAnswer: "Yes" },
            23: { score: 0, comments: "", managerAnswer: "Yes" },
            24: { score: 3, comments: "This is a generic answer - does not provide specific instances. ", managerAnswer: "We assess each resolution on its merits and vote in the manner which we believe is in the best interest of our clients, taking into account, inter alia, the principles of good corporate governance (e.g. King IV) and the long-term sustainability of the company." },
            25: { score: 0, comments: "", managerAnswer: "No" },
            26: { score: 0, comments: "", managerAnswer: "No" },
            27: { score: 3, comments: "", managerAnswer: "We have ad-hoc training sessions on responsible investment, including developments in the ESG space. We also encourage staff to attend external RI/ESG events and webinars." },
            28: { score: 5, comments: "", managerAnswer: "We produce an annual Stewardship Report." },
            29: { score: 0, comments: "", managerAnswer: "Yes" },
            30: { score: 3, comments: "The report details the engagements but not necessarily the outcomes. ", managerAnswer: "Yes, this is included in our annual Stewardship Report." },
            31: { score: 5, comments: "", managerAnswer: "Yes, this is included in our annual Stewardship Report." },
            32: { score: 5, comments: "", managerAnswer: "Yes" },
            33: { score: 3, comments: "", managerAnswer: "Annually" },
            34: { score: 0, comments: "", managerAnswer: "No" },
            35: { score: 5, comments: "", managerAnswer: "Yes" },
            36: { score: 3, comments: "", managerAnswer: "Yes" },
            37: { score: 3, comments: "", managerAnswer: "We use a third-party data provider." },
            38: { score: 0, comments: "", managerAnswer: "No" },
            39: { score: 0, comments: "", managerAnswer: "No" },
            40: { score: 0, comments: "", managerAnswer: "No" },
            74: { score: 0, comments: "", managerAnswer: "Our organisation manages internal ESG risks, opportunities, and impacts through a combination of governance oversight, internal policies, and continuous improvement." },
            75: { score: 0, comments: "", managerAnswer: "No" },
            76: { score: 0, comments: "", managerAnswer: "A) Responsible investment policy;C) Proxy voting policy;" }
        }
    }
};

export const archetypeMap: { [key: number]: string } = {
    1: "Not Present",
    2: "Limited",
    3: "Developing",
    4: "Intermediate",
    5: "Advanced"
};

export const getArchetypeNumber = (score: number) => {
    if (score < 1.5) return 1;
    if (score < 2.5) return 2;
    if (score < 3.5) return 3;
    if (score < 4.5) return 4;
    return 5;
};