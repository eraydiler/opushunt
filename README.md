# 🎯 OpusHunt

**OpusHunt** started as a personal hobby project to meet my own job-search needs. The app helps search for opportunities around the world.

It is designed to be downloaded and run locally by each user; the project maintainer does not host the application or receive users' resumes or Gemini API keys.

Instead of manually browsing different job boards, OpusHunt brings job listings into one interface. It can use **Gemini AI** to compare your resume with job descriptions and help filter results. AI features are optional and use the Gemini API key that you configure on your own machine.

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
* **Europass / EURES** (European job listings)

Use the optional location and language fields in Search Settings to filter listings across selected platforms. Leave either blank to disable that filter. Remote listings remain included when a location is set. Language filtering uses the job description, so very short descriptions may be excluded.

Listings are retrieved from third-party services when you run a search. The app displays source names and links to the original listing where available. Availability, permitted use, and attribution requirements are controlled by each source and may change.

### Source terms review

The table below summarizes the public terms and source documentation reviewed on **2026-10-30** against the access method currently used by the app. It is not a legal determination that a source or use is “legal” or “illegal,” and it does not grant permission. “Conditions documented” means the source publishes specific API/feed conditions; users must still follow them. “Restriction / possible conflict” means a published restriction may conflict with the current integration. “Not verified” means no clear permission for this app's access and display method was confirmed. Public availability alone does not grant reuse rights. Re-check the linked terms before use.

| Source | Current access method | Review status and relevant links |
|---|---|---|
| RemoteOK | JSON API | **Conditions documented:** API asks for source credit and a link to the original listing; logo use requires written permission. [API terms](https://remoteok.com/api) |
| WeWorkRemotely | RSS feed | **Not verified:** RSS is available, but permission to reuse feed entries in this app was not confirmed. [Feed](https://weworkremotely.com/categories/remote-programming-jobs.rss) · [Website](https://weworkremotely.com/) |
| Remotive | JSON API | **Conditions documented:** credit Remotive and link each original listing; the notice restricts submitting jobs to third-party sites and using listings to collect signups. Check whether your use fits. [API notice](https://remotive.com/remote-jobs/api) |
| Arbeitnow | JSON API | **Not verified:** public endpoint is available; specific reuse and attribution permission was not confirmed. [API](https://www.arbeitnow.com/api/job-board-api) |
| Jobicy | JSON API | **Conditions documented:** provide clear Jobicy credit and direct link; application links must go to the original job URL. [API](https://jobicy.com/api/v2/remote-jobs) · [API documentation](https://jobi.cy/apidocs) |
| TheHub | JSON API | **Not verified:** platform terms are available, but permission to retrieve and republish job data through this endpoint was not confirmed. [API](https://thehub.io/api/jobs) · [Terms](https://thehub.io/terms) |
| Hacker News / Algolia | Algolia HN Search API | **Not verified:** specific reuse terms for the Algolia HN Search API were not confirmed. [API](https://hn.algolia.com/api) · [Algolia terms](https://www.algolia.com/policies/terms/) |
| FindAJob DWP | HTML search pages | **Not verified:** GOV.UK says much of its content is under the Open Government Licence, but whether these specific listings are covered was not confirmed. [FindAJob](https://findajob.dwp.gov.uk/) · [GOV.UK terms](https://www.gov.uk/help/terms-conditions) |
| NAV Arbeidsplassen | HTML search pages | **Not verified:** permission for automated retrieval and reuse of listing content was not confirmed. [Job search](https://arbeidsplassen.nav.no/stillinger) |
| Cognizant Careers | HTML search pages | **Restriction / possible conflict:** website terms restrict copying and distribution without permission and describe limited personal, non-commercial use; permission for this extraction/display method was not confirmed. [Careers site](https://careers.cognizant.com/uki-en/jobs/) · [Terms](https://www.cognizant.com/us/en/about-cognizant/terms-conditions) |
| Hunt UK Visa Sponsors | HTML search pages | **Restriction / direct conflict:** terms prohibit scraping outside their API, while the current integration scrapes HTML search pages. Disable this source or replace it with a method the site authorizes before using it. [Search page](https://huntukvisasponsors.com/jobs) · [Terms](https://huntukvisasponsors.com/terms) |
| VisaSponsor.jobs | `/api/jobs` endpoint parsed as HTML | **Not verified:** terms apply to use of the site; permission for this automated extraction and display method was not confirmed. [Endpoint](https://visasponsor.jobs/api/jobs?page=0) · [Terms](https://visasponsor.jobs/terms) |
| Relocate.me | HTML search and job pages | **Not verified:** permission for automated retrieval and reuse of listing content was not confirmed. [Search page](https://relocate.me/search) |
| SwissDevJobs | XML feed | **Not verified:** feed is available, but permission to reuse its entries was not confirmed; the terms page could not be reviewed. [Feed](https://swissdevjobs.ch/job_feed.xml) · [Terms](https://swissdevjobs.ch/terms) |
| Jobgether | HTML search pages | **Not verified:** permission to scrape and republish search results was not confirmed. [Search page](https://jobgether.com/search-offers) · [Terms](https://jobgether.com/terms-of-use) |
| Europass / EURES | JSON API | **Not verified:** the general EU legal notice is not an API-specific reuse licence; endpoint-specific permission was not confirmed. [API](https://europa.eu/eures/api/jv-searchengine/public/jv-search/search) · [EU legal notice](https://european-union.europa.eu/legal-notice_en) |

## 🚀 Getting Started

### Prerequisites

* Python 3.9+
* A Gemini API Key (from Google AI Studio)

### Installation

The app runs on your own computer. It is not a hosted service operated by the project maintainer.

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
   To use Gemini features, create a `.env` file in the project root and add your own Gemini API key:
   ```env
   GEMINI_API_KEY="your_api_key_here"
   ```
   Keep this key private. The `.env` file is ignored by Git; do not commit it or share it in screenshots or demo videos. If you do not configure a key, Gemini-powered features will not work.

### Resume and Gemini data

Your resume is processed by the app on your computer. When you use AI filtering or generate a cover letter, the app sends resume text and relevant job information to Google's Gemini API using the key you configured. This is a third-party data transfer, not a feature hosted by the project maintainer. Review Google's current Gemini API terms and privacy information before using it, and do not submit sensitive information if you are uncomfortable with the applicable data handling. Your API usage is subject to Google's terms, quotas, and any charges applicable to your account.

### Running the App

Start the Streamlit application:
```bash
streamlit run src/presentation/app.py
```

The app will be available in your browser at `http://localhost:8501`.

## 🏗 Architecture

OpusHunt is built using **Clean Architecture** principles to ensure maintainability and ease of adding new job sources.

For convenience and rapid development, the interface is built with Streamlit. The project prioritizes functionality over custom UI design.

* **`src/domain/`**: Contains core business entities (`Job`, `Resume`) and repository interfaces.
* **`src/application/`**: Contains Use Cases (`SearchJobsUseCase`, `AIFilterJobsUseCase`) that orchestrate the business logic.
* **`src/infrastructure/`**: Contains concrete implementations of repositories (the actual web scrapers and API callers for each job board).
* **`src/presentation/`**: Contains the Streamlit user interface (`app.py`).

Adding a new job board is as simple as creating a new class in `infrastructure/repositories/` that implements the `JobRepository` interface and adding it to the `AVAILABLE_PLATFORMS` dictionary in `app.py`.

## 📝 License

This project is licensed under the [MIT License](LICENSE). The license applies to the project's original code; it does not grant rights to third-party job listings, website content, APIs, feeds, or trademarks.

## ⚠️ Disclaimer

OpusHunt is an independent educational project and is not affiliated with, endorsed by, or sponsored by the job boards, employers, Google, or other services mentioned in the app. Names are used only to identify data sources and services. Their respective owners retain all rights to their names and content.

The app retrieves data from third-party sources directly when run by a user. Users should review and follow applicable laws and each source's current terms, including any access, attribution, and content-use requirements, and check listing details on the original source. The project is provided "as is", without warranties, to the extent permitted by law. Nothing in this notice guarantees that any particular use complies with third-party terms or applicable law.

## ☕ Support

If you find OpusHunt useful, your support would mean a lot and help motivate me to keep improving this project. Support is entirely optional and does not include any product or service.

[![Buy Me A Coffee](https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png)](https://www.buymeacoffee.com/d2vqt5wmcrw)
