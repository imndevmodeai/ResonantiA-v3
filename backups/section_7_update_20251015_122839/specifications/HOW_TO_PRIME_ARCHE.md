# How to Prime ArchE: A Keyholder's Guide to Mission Briefings

## 1. The Philosophy: The Mission Briefing

Priming ArchE is not like prompting a simple chatbot. It is the act of delivering a **comprehensive mission briefing** to a specialized, intelligent agent.

-   **Without Priming**: You are giving a soldier one order at a time in the middle of a battle. The soldier lacks context and cannot act with initiative.
-   **With Priming**: You are giving a commander the full strategic overview—maps, objectives, intelligence, rules of engagement—*before* the first boot hits the ground. The commander can then execute with full autonomy and intelligence.

A well-structured prime is the single most effective way to guarantee a high-quality, relevant, and efficient outcome.

## 2. The Core Components of a Prime

Every prime you deliver should be structured using these five components. Think of them as the essential paragraphs of a military order.

### Component 1: `Objective` (The "What We're Doing")

This is the single, clear statement of the desired end state. What does success look like? It should be concise and unambiguous.

**Format**:
`Objective: [Your clear and specific goal]`

**Example**:
`Objective: Analyze the provided `Q3_sales_data.csv` to identify the top-performing product category and the region with the lowest sales growth, and generate a two-paragraph summary for an executive email.`

---

### Component 2: `SPRs to Activate` (The "Special Skills Required")

This is the most direct way you can interface with ArchE's core architecture. By listing Sparse Priming Representations (SPRs), you are telling the `KnowledgeNetworkOnenesS` (KnO) which cognitive circuits and specialized tools to activate. This is like telling the commander to bring the demolitions expert, the cryptographer, and the medic.

**Format**:
`SPRs to Activate:`
`- [SPR_Name_One]`
`- [SPR_Name_Two]`
`- [SPR_Name_Three]`

**Example**:
`SPRs to Activate:`
`- `FinancialDataAnalysiS`
`- `TemporalTrendDetectioN`
`- `ExecutiveSummaryGeneratioN`
`- `DataVisualizatioN`

*(You can find a list of common SPRs in the `ARCHE_TERMINOLOGY_QUICK_REFERENCE.md` file.)*

---

### Component 3: `Context` (The "Intelligence Briefing")

This is where you provide the essential background, constraints, definitions, and assumptions ArchE needs to understand the battlefield.

**Format**:
`Context:`
`- [Key piece of information 1]`
`- [Constraint or rule 2]`
`- [Definition of a special term 3]`

**Example**:
`Context:`
`- The sales data covers the period from July 1st to September 30th, 2025.`
`- "Sales growth" should be calculated month-over-month.`
`- The "EMEA" region in the data combines Europe, the Middle East, and Africa.`
`- Assume all sales figures are in USD.`

---

### Component 4: `Your Role` (The "Persona")

Instructing ArchE to adopt a specific professional persona helps it tailor its language, perspective, and the format of its output.

**Format**:
`Your Role: [The professional persona ArchE should adopt]`

**Example**:
`Your Role: Act as a Senior Financial Analyst reporting directly to the Chief Financial Officer.`

---

### Component 5: `Initial Command` (The "First Order")

This is the first concrete, executable step you want ArchE to take. It kicks off the mission.

**Format**:
`Initial Command: [The first specific action to perform]`

**Example**:
`Initial Command: Load the `Q3_sales_data.csv` file into a pandas DataFrame and provide a summary of the data types and check for any missing values in each column.`

---

## 3. Full Example: Putting It All Together

Here is a complete, well-formed prime that you can use as a template.

```
Objective: Analyze the attached customer feedback logs (`feedback_logs.jsonl`) to identify the top 3 most requested features and the most common complaint category. The final output should be a concise summary slide for a product strategy meeting.

SPRs to Activate:
- `NaturalLanguageProcessinG`
- `SentimentAnalysiS`
- `FeatureRequestExtractioN`
- `RootCauseAnalysiS`
- `StrategicCommunicatioN`

Context:
- The logs cover the period from September 1st to October 14th, 2025.
- The product is a project management tool for small businesses.
- A "complaint" is distinct from a "bug report." We are looking for usability issues and frustrations.
- The final output should be formatted in Markdown, ready to be copied into a presentation.

Your Role: Act as a Lead User Experience Researcher.

Initial Command: Begin by parsing the `feedback_logs.jsonl` file and confirming the total number of entries you've processed.
```

By using this structured briefing format, you are not just asking a question; you are launching a mission. This will always yield the best results.


