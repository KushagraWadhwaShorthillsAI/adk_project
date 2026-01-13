# Resume + Job Market Analyzer Agent

## Overview
This project implements an intelligent agent, **"CareerPulse"**, designed to act as an elite Job Market Analyst & Career Coach. It requests a user's resume, analyses it, searches for relevant live job openings across the web, and computes detailed match scores to provide actionable career insights.

## Features
- **Resume Ingestion**: Parses PDF resumes to safely extract text and key information.
- **Profile Extraction**: Automatically identifies skills, experience level, and education from the resume text.
- **Live Job Search**: Integrates with the **JSearch API** (via RapidAPI) to find real-time job listings in specific locations (default: India).
- **Smart Filtering**: Automatically filters job results based on the user's actual years of experience to ensure relevance.
- **Deterministic Matching**: Uses a custom weighted scoring algorithm to compare resume skills against job requirements, producing a compatibility score.
- **Visual Reporting**: Generates ASCII-based bar charts for match scores to provide a quick visual assessment of fit.

## Project Structure
```
resume_agent/
├── agent.py                 # Main agent definition and execution pipeline
├── .env                     # Configuration for API keys (not committed)
├── tools/
│   ├── pdf_tool.py          # Tool for reading and extracting text from PDF resumes
│   ├── job_search_tool.py   # Tool for searching jobs via JSearch API
│   └── ds_match_tool.py     # Tool for computing match scores and generating stats
```

## Prerequisites
- Python 3.9+
- A [RapidAPI](https://rapidapi.com/) account with access to the **JSearch API**.
- Google ADK (Agent Development Kit) environment.

## Setup & Configuration

1. **Environment Variables**:
   Create a `.env` file in the `resume_agent` directory with the following keys:
   ```env
   RAPID_API_KEY=your_rapidapi_key
   RAPID_API_HOST=jsearch.p.rapidapi.com
   GOOGLE_API_KEY=your_gemini_api_key
   ```

2. **Dependencies**:
   Ensure the following Python packages are installed:
   - `pdfplumber` (for PDF text extraction)
   - `requests` (for API calls)
   - `python-dotenv` (for environment management)
   - `google-adk` (core agent framework)

## Usage Flow
The agent follows a strict, autonomous 5-step pipeline:

1.  **Ingest Resume**: The user uploads a PDF or provides a local file path.
    > **Note**: For CLI usage, verify your resume is in `resume_agent/data/`. For the Web UI, simply upload the file directly when prompted.
2.  **Analyze**: The agent extracts skills, total years of experience, and highest education level.
3.  **Search**: It performs a live search for jobs matching the extracted profile (e.g., "Software Engineer") and filters results by the user's experience.
4.  **Match**: It calls the matching tool to compute a weighted score for every job found.
5.  **Report**: It presents the top 10 matches with direct application links, salary info, and compatibility scores.

## Tool Deep Dive

### 1. Job Search Tool (`tools/job_search_tool.py`)
This tool is more than a simple API wrapper; it acts as a normalization layer between raw job data and the agent's logic.
- **Skill Extraction Engine**: Because raw API data often lacks structured tags, this tool uses a complex regex-based scanner (`TECH_ANCHORS`) to parse job descriptions. It identifies over 100+ technical keywords (e.g., "React", "Terraform", "K8s", "PyTorch") and standardizes them (e.g., mapping "Node.js" and "NodeJS" to "node.js").
- **Smart Experience Filtering**: The tool accepts a `user_experience_years` argument. It explicitly parses "Minimum Experience" from job descriptions and discards listings where the requirement exceeds the user's actual tenure, ensuring 100% relevant results.
- **Data Normalization**: Handles diverse salary formats (hourly, annually, ranges) and location data to provide a cleaner output for the LLM to read.

### 2. PDF Ingestion & Analysis (`tools/pdf_tool.py`)
Ensures robust handling of user-uploaded resumes before any analysis begins.
- **Smart File Resolution**: Features a recursive search algorithm `find_pdf_file` that locates documents even if the user provides an incomplete path or if the file waits in a subfolder (like `uploads/` or `data/`).
- **Robust Extraction**: Utilizes `pdfplumber` to extract structured text layout.
- **Safety & Validation**: 
  - Detects and flags scanned/image-only PDFs (empty text return).
  - Truncates extremely large files (15k+ chars) to prevent context window overflow.
  - Validates file extensions and existence before processing.

### 3. Matching Engine (`tools/ds_match_tool.py`)
A deterministic, non-hallucinating scoring system designed to give candidates a realistic view of their fit.
- **The Scoring Algorithm**:
  \[
  \text{Score} = (0.7 \times \text{Skill Match}) + (0.2 \times \text{Experience Fit}) + (0.1 \times \text{Education Fit})
  \]
- **Skill Match Application**: Calculates the intersection of skills found in the resume versus skills extracted from the job description.
- **Experience & Education Logic**: 
  - *Experience*: specific ratio calculation `min(user_exp / job_req, 1.0)`.
  - *Education*: Penalties applied if a Master's or PhD is strictly required but not held.
- **Visual Feedback**: Generates ASCII bar charts (e.g., `███████░░░ 72.5%`) included directly in the data object, allowing the agent to display rich visuals without needing markdown plugins.

## Troubleshooting
- **FileNotFoundError**: Ensure the PDF path is correct or the file is uploaded to the root directory.
- **API Errors**: Verify that your `RAPID_API_KEY` is valid and has remaining quota.
