# OpusHunt Architecture Documentation

This project follows the **Clean Architecture** principles to ensure separation of concerns, scalability, and maintainability. The codebase is organized into four main layers: Domain, Application, Infrastructure, and Presentation.

## 🏗️ Directory Structure

```
src/
├── domain/                 # Enterprise Business Rules (Entities & Interfaces)
├── application/            # Application Business Rules (Use Cases)
├── infrastructure/         # Frameworks & Drivers (External APIs, DBs, UI Adapters)
└── presentation/           # User Interface (Streamlit App)
```

---

## 1. Domain Layer (`src/domain`)
The core of the application. It contains the business objects and the contracts (interfaces) that the application uses. This layer is independent of any external frameworks or libraries.

*   **`entities.py`**: Defines the core data models.
    *   `Job`: Represents a job listing (company, position, url, etc.).
    *   `Resume`: Represents the user's resume content.
*   **`interfaces.py`**: Defines abstract base classes (protocols) for repositories and services.
    *   `JobRepository`: Contract for fetching jobs.
    *   `LLMService`: Contract for generating content via AI.
    *   `ApplicationRepository`: Contract for saving application history.

## 2. Application Layer (`src/application`)
Contains the business logic (Use Cases). It orchestrates the flow of data between the Domain and Infrastructure layers. It depends only on the Domain layer.

*   **`use_cases.py`**:
    *   `SearchJobsUseCase`: Coordinates fetching jobs from multiple repositories.
    *   `AIFilterJobsUseCase`: Coordinates the AI-driven semantic filtering of jobs based on the user's resume and keywords.
    *   `GenerateCoverLetterUseCase`: Uses the LLM service to create a tailored cover letter.
    *   `ApplyJobUseCase`: Handles the logic of recording a job application.

## 3. Infrastructure Layer (`src/infrastructure`)
Implements the interfaces defined in the Domain layer. This layer interacts with external systems like APIs, files, and databases.

*   **Repositories (`src/infrastructure/repositories`)**:
    *   `remoteok_repo.py`: Implements `JobRepository`. Fetches jobs from the RemoteOK API.
    *   `remotive_repo.py`: Implements `JobRepository`. Fetches jobs from the Remotive API.
    *   `arbeitnow_repo.py`: Implements `JobRepository`. Fetches jobs from the Arbeitnow API.
    *   `jobicy_repo.py`: Implements `JobRepository`. Fetches global remote jobs from the Jobicy API (Aggregator).
    *   `rss_repo.py`: Implements `JobRepository`. A generic XML/RSS feed parser for platforms like WeWorkRemotely.
    *   `csv_repo.py`: Implements `ApplicationRepository`. Manages application history using **Session State** (in-memory) for privacy, instead of a persistent CSV file. Supports import/export of session data.
*   **Services (`src/infrastructure/services`)**:
    *   `gemini_service.py`: Implements `LLMService`. Uses Google's Gemini models to generate cover letters and perform AI semantic filtering of jobs.
    *   `pdf_service.py`: Handles PDF file parsing (e.g., extracting text from uploaded resumes).

## 4. Presentation Layer (`src/presentation`)
The entry point for the user. It interacts with the Application layer to execute commands and display data.

*   **`app.py`**: A **Streamlit** web application that:
    *   Initializes the dependencies (Dependency Injection).
    *   Provides the UI for searching jobs, uploading resumes, and viewing history.
    *   Calls the Use Cases to perform actions.

---

## 🔄 Dependency Rule
Dependencies always point **inwards**.
*   `Presentation` -> `Application` -> `Domain`
*   `Infrastructure` -> `Domain`

The Domain layer knows nothing about the outer layers (UI, Database, APIs). This makes the core logic easy to test and independent of external changes.
