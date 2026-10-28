# 🎯 OpusHunt

**OpusHunt** is a smart job hunting aggregator designed for modern professionals, particularly focusing on remote, relocation, and visa-sponsored opportunities across the globe.

Instead of manually browsing dozens of different job boards, OpusHunt brings them all into one clean interface. It even utilizes **Gemini AI** to read your CV (PDF) and filter out irrelevant positions (like HR, QA, Customer Success when you are looking for iOS roles) from the search results, saving you hours of time.

## 🌟 Features

* **Multi-Platform Aggregation:** Fetches jobs simultaneously from 10+ different job boards.
* **Visa & Relocation Focus:** Includes specialized boards for UK visa sponsorships and global relocation packages.
* **AI-Powered Filtering:** Upload your resume (PDF) and let Gemini AI evaluate the fit for each job description.
* **Search Filters:** Filter results from every source by location and detected job-description language.
* **Application Tracking:** Built-in history to keep track of jobs you've already applied for, preventing duplicate efforts.
* **Session Management:** Save your workspace (CV, History, Settings) locally to resume your hunt later.

## 🌐 Supported Platforms

OpusHunt currently aggregates jobs from the following platforms:

* **RemoteOK** (Global Remote)
* **WeWorkRemotely** (Global Remote)
* **Remotive** (Global Remote)
* **Arbeitnow** (Europe & Remote)
* **Jobicy** (Global Remote)
* **TheHub** (Nordic/European Startups)
* **Hacker News** ("Who is hiring?" threads)
* **FindAJob DWP** (UK Government Official Job Search)
* **NAV Arbeidsplassen** (Norwegian job listings)
* **Cognizant Careers** (Global company vacancies)
* **Hunt UK Visa Sponsors** (UK Visa Sponsored Jobs)
* **VisaSponsor.jobs** (Global Visa Sponsored Jobs)
* **Relocate.me** (Tech jobs with Relocation Packages)
* **SwissDevJobs** (Swiss technology jobs)
* **Jobgether** (Remote jobs)

Use the optional location and language fields in Search Settings to filter listings across all selected platforms. Leave either blank to disable that filter. Remote listings remain included when a location is set. Language filtering uses the job description, so very short descriptions may be excluded.

## 🚀 Getting Started

### Prerequisites

* Python 3.9+
* A Gemini API Key (from Google AI Studio)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/eraydiler/opushunt.git
   cd opushunt
   ```

2. **Set up a virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables**
   Create a `.env` file in the root directory and add your Gemini API Key:
   ```env
   GEMINI_API_KEY="your_api_key_here"
   ```

### Running the App

Start the Streamlit application:
```bash
streamlit run src/presentation/app.py
```

The app will be available in your browser at `http://localhost:8501`.

## 🏗 Architecture

OpusHunt is built using **Clean Architecture** principles to ensure maintainability and ease of adding new job sources.

* **`src/domain/`**: Contains core business entities (`Job`, `Resume`) and repository interfaces.
* **`src/application/`**: Contains Use Cases (`SearchJobsUseCase`, `AIFilterJobsUseCase`) that orchestrate the business logic.
* **`src/infrastructure/`**: Contains concrete implementations of repositories (the actual web scrapers and API callers for each job board).
* **`src/presentation/`**: Contains the Streamlit user interface (`app.py`).

Adding a new job board is as simple as creating a new class in `infrastructure/repositories/` that implements the `JobRepository` interface and adding it to the `AVAILABLE_PLATFORMS` dictionary in `app.py`.

## 📝 License

This project is open-source and available under the [MIT License](LICENSE).
