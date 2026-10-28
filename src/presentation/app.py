import streamlit as st
import os
import sys
import html
import json
import importlib
from bs4 import BeautifulSoup

# Add project root to path so we can import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from dotenv import load_dotenv
from src.domain.entities import Resume
from src.infrastructure.repositories.remoteok_repo import RemoteOKJobRepository
from src.infrastructure.repositories.rss_repo import RSSJobRepository
from src.infrastructure.repositories.remotive_repo import RemotiveJobRepository
from src.infrastructure.repositories.arbeitnow_repo import ArbeitnowJobRepository
from src.infrastructure.repositories.jobicy_repo import JobicyJobRepository
from src.infrastructure.repositories.thehub_repo import TheHubJobRepository
from src.infrastructure.repositories.hn_repo import HackerNewsJobRepository
from src.infrastructure.repositories.findajobdwp_repo import FindAJobDWPJobRepository
from src.infrastructure.repositories.huntukvisasponsors_repo import HuntUKVisaSponsorsJobRepository
from src.infrastructure.repositories.visasponsor_repo import VisaSponsorJobRepository
from src.infrastructure.repositories.relocateme_repo import RelocateMeJobRepository
from src.infrastructure.repositories.swissdevjobs_repo import SwissDevJobsRepository
from src.infrastructure.repositories.jobgether_repo import JobgetherJobRepository
from src.infrastructure.repositories.nav_arbeidsplassen_repo import (
    NavArbeidsplassenJobRepository,
)
from src.infrastructure.repositories.cognizant_repo import CognizantJobRepository
import src.infrastructure.repositories.csv_repo as csv_repo_module

# Force reload to ensure latest class definition is used
importlib.reload(csv_repo_module)
from src.infrastructure.repositories.csv_repo import SessionApplicationRepository
from src.infrastructure.services.gemini_service import GeminiLLMService
from src.infrastructure.services.pdf_service import PDFService
from src.application.use_cases import (
    SearchJobsUseCase,
    GenerateCoverLetterUseCase,
    ApplyJobUseCase,
    AIFilterJobsUseCase,
)

# --- Setup & Injection ---
load_dotenv()

# Repositories & Services
remoteok_repo = RemoteOKJobRepository()
weworkremotely_repo = RSSJobRepository(
    feed_url="https://weworkremotely.com/categories/remote-programming-jobs.rss", platform_name="WeWorkRemotely"
)
remotive_repo = RemotiveJobRepository()
arbeitnow_repo = ArbeitnowJobRepository()
jobicy_repo = JobicyJobRepository()
thehub_repo = TheHubJobRepository()
hn_repo = HackerNewsJobRepository()
findajobdwp_repo = FindAJobDWPJobRepository()
huntuk_repo = HuntUKVisaSponsorsJobRepository()
visasponsor_repo = VisaSponsorJobRepository()
relocateme_repo = RelocateMeJobRepository()
swissdevjobs_repo = SwissDevJobsRepository()
jobgether_repo = JobgetherJobRepository()
nav_arbeidsplassen_repo = NavArbeidsplassenJobRepository()
cognizant_repo = CognizantJobRepository()

app_repo = SessionApplicationRepository()
llm_service = GeminiLLMService()
pdf_service = PDFService()

# Services Map (for UI selection)
AVAILABLE_PLATFORMS = {
    "RemoteOK": remoteok_repo,
    "WeWorkRemotely": weworkremotely_repo,
    "Remotive": remotive_repo,
    "Arbeitnow": arbeitnow_repo,
    "Jobicy": jobicy_repo,
    "TheHub": thehub_repo,
    "Hacker News": hn_repo,
    "FindAJob DWP": findajobdwp_repo,
    "Hunt UK Visa Sponsors": huntuk_repo,
    "VisaSponsor.jobs": visasponsor_repo,
    "Relocate.me": relocateme_repo,
    "SwissDevJobs": swissdevjobs_repo,
    "Jobgether": jobgether_repo,
    "NAV Arbeidsplassen": nav_arbeidsplassen_repo,
    "Cognizant": cognizant_repo,
    # "LinkedIn": None, # Placeholder for future
}

# Use Cases (Initialized dynamically in UI)
generate_cl_uc = GenerateCoverLetterUseCase(llm_service)
apply_job_uc = ApplyJobUseCase(app_repo)
ai_filter_uc = AIFilterJobsUseCase(llm_service)


# --- UI Helper Functions ---
def load_resume():
    # Load from session state instead of file
    if "resume_content" in st.session_state:
        return st.session_state["resume_content"]
    return ""


def clean_html_text(raw_html: str) -> str:
    """Removes HTML tags and unescapes HTML entities to fix garbled characters."""
    if not raw_html:
        return ""
    # Unescape HTML entities (e.g., &amp;, &#8217;)
    unescaped = html.unescape(raw_html)
    # Use BeautifulSoup to strip all HTML tags gracefully
    soup = BeautifulSoup(unescaped, "html.parser")
    # Get text, separating blocks with a space
    clean_text = soup.get_text(separator=" ", strip=True)
    return clean_text


# --- Streamlit App ---
st.set_page_config(page_title="OpusHunt | Find Your Masterpiece", page_icon="🎯", layout="wide")

# --- Session Management Logic (Must run before widgets) ---
# Initialize session state keys if not present
if "resume_content" not in st.session_state:
    st.session_state["resume_content"] = ""
if "search_keywords" not in st.session_state:
    st.session_state["search_keywords"] = ""
if "search_location" not in st.session_state:
    st.session_state["search_location"] = ""
if "search_language" not in st.session_state:
    st.session_state["search_language"] = ""
if "use_ai_filter" not in st.session_state:
    st.session_state["use_ai_filter"] = True

# Define available platforms for cleaner rendering
platforms_list = [
    "RemoteOK",
    "WeWorkRemotely",
    "Remotive",
    "Arbeitnow",
    "Jobicy",
    "TheHub",
    "Hacker News",
    "FindAJob DWP",
    "Hunt UK Visa Sponsors",
    "VisaSponsor.jobs",
    "Relocate.me",
    "SwissDevJobs",
    "Jobgether",
    "NAV Arbeidsplassen",
    "Cognizant",
]
default_disabled_platforms = {"NAV Arbeidsplassen", "Cognizant"}
for platform in platforms_list:
    platform_key = f"platform_{platform}"
    if platform_key not in st.session_state:
        st.session_state[platform_key] = platform not in default_disabled_platforms

# Handle Session Import
if "uploaded_session_file" not in st.session_state:
    st.session_state["uploaded_session_file"] = None


def load_session_callback():
    uploaded_file = st.session_state.get("session_uploader")
    if uploaded_file is not None:
        try:
            data = json.load(uploaded_file)

            # Update Session State
            st.session_state["resume_content"] = data.get("resume_content", "")
            st.session_state["search_keywords"] = data.get("search_keywords", "")
            st.session_state["search_location"] = data.get("search_location", "")
            st.session_state["search_language"] = data.get("search_language", "")
            st.session_state["use_ai_filter"] = data.get("use_ai_filter", True)

            p_states = data.get("platform_states", {})
            for p, state in p_states.items():
                st.session_state[f"platform_{p}"] = state

            history = data.get("application_history", [])
            if hasattr(app_repo, "load_history"):
                app_repo.load_history(history)

            st.toast("Session loaded successfully! 🎉", icon="✅")
        except Exception as e:
            st.error(f"Error loading session: {e}")


st.title("🎯 OpusHunt")
st.markdown("Find the job that fits your masterpiece.")

# Sidebar: Configuration & Resume
with st.sidebar:
    st.header("👤 Your Profile")

    # Session Management (Moved to top for better UX)
    with st.expander("💾 Session Management", expanded=False):
        st.info("Save/Restore workspace (CV, History, Settings).")

        # Import
        st.file_uploader(
            "Import Session (JSON)", type=["json"], key="session_uploader", on_change=load_session_callback
        )

        # Placeholder for Export Button (populated at the end of script)
        export_placeholder = st.empty()

    st.divider()

    # File Uploader for PDF
    uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])

    current_resume = load_resume()

    if uploaded_file is not None:
        with st.spinner("Extracting text from PDF..."):
            extracted_text = pdf_service.extract_text(uploaded_file.getvalue())
            if extracted_text:
                current_resume = extracted_text
                st.session_state["resume_content"] = current_resume  # Update state directly
                st.success("PDF loaded successfully!")

    # Resume Text Area (Bound to session state)
    st.text_area("Resume Content (Editable)", key="resume_content", height=300)

    st.divider()
    st.header("⚙️ Search Settings")

    # Platform Selection
    st.subheader("Platforms")
    selected_platform_names = []

    # Dynamic column distribution
    cols = st.columns(2)
    for i, platform in enumerate(platforms_list):
        col = cols[i % 2]
        with col:
            # Bind checkbox state to session_state keys for persistence
            platform_key = f"platform_{platform}"
            if st.checkbox(platform, key=platform_key):
                selected_platform_names.append(platform)

    # Future placeholder
    with cols[1]:
        st.checkbox("LinkedIn (Soon)", value=False, disabled=True)

    # Keywords
    st.subheader("Keywords")
    # Bind to session_state key
    search_tag = st.text_input("Enter tags (comma separated)", key="search_keywords", placeholder="e.g. ios, swift")
    search_location = st.text_input(
        "Location (optional)", key="search_location", placeholder="e.g. Norway, London"
    )
    search_language = st.text_input(
        "Language (optional)",
        key="search_language",
        placeholder="e.g. English, Norwegian, en",
        help=(
            "Filters by detected language in the job description. "
            "Short descriptions may be excluded."
        ),
    )

    st.divider()
    st.header("🧠 Smart Features")
    use_ai_filter = st.checkbox(
        "AI Smart Filter",
        help="Uses Gemini to read the job description and compare it with your CV. Hides irrelevant jobs like HR, QA, Customer Success. (Takes a bit longer to fetch)",
        key="use_ai_filter",
    )

# Main Content
tab1, tab2 = st.tabs(["🔍 Search Jobs", "📜 Application History"])

with tab1:
    # Active Filters Display
    active_filters_cols = st.columns([1, 3])
    with active_filters_cols[0]:
        st.markdown("**Active Platforms:**")
        for p in selected_platform_names:
            st.caption(f"✅ {p}")

    with active_filters_cols[1]:
        st.markdown("**Active Keywords:**")
        tags = [t.strip() for t in search_tag.split(",") if t.strip()]
        if tags:
            st.markdown(" ".join([f"`{t}`" for t in tags]))
        else:
            st.caption("No keywords entered")
        if search_location.strip():
            st.caption(f"Location: {search_location.strip()} (remote jobs included)")
        if search_language.strip():
            st.caption(f"Language: {search_language.strip()}")

    st.divider()

    if st.button("Fetch Jobs", type="primary"):
        # Explicitly clear the jobs from session state before fetching new ones
        if "jobs" in st.session_state:
            del st.session_state["jobs"]

        if not selected_platform_names:
            st.warning("Please select at least one platform.")
        else:
            # Prepare Use Case with selected repos
            selected_repos = [
                AVAILABLE_PLATFORMS[name] for name in selected_platform_names if AVAILABLE_PLATFORMS.get(name)
            ]
            search_jobs_uc = SearchJobsUseCase(selected_repos)

            with st.spinner(f"Fetching jobs from {', '.join(selected_platform_names)}..."):
                try:
                    jobs = search_jobs_uc.execute(
                        search_tag,
                        location=search_location,
                        language=search_language,
                    )
                except ValueError as error:
                    st.error(str(error))
                    jobs = []

            if use_ai_filter and jobs:
                # Use session state for resume content
                resume_text = st.session_state.get("resume_content", "")
                with st.spinner(f"🤖 AI is analyzing {len(jobs)} jobs to find the best match for your CV..."):
                    resume_obj = Resume(content=resume_text)
                    jobs = ai_filter_uc.execute(jobs, resume_obj, search_tag)

            st.session_state["jobs"] = jobs
            st.success(f"Found {len(jobs)} jobs.")

    if "jobs" in st.session_state:
        # Get history to check for duplicates
        history = apply_job_uc.get_history()
        # Create a set of applied job URLs for fast lookup
        applied_urls = set()
        for h in history:
            if h.get("URL"):
                applied_urls.add(h.get("URL"))

        for job in st.session_state["jobs"]:
            # Skip invalid/empty jobs
            if not job.position or job.position == "Unknown" or not job.company:
                continue

            # Safely get source to prevent AttributeError from old cached objects
            job_source = getattr(job, "source", "Unknown")
            job_date = getattr(job, "date", None)

            # Check if applied
            is_applied = job.url in applied_urls

            # Visual Indicator for Applied Jobs
            if is_applied:
                expander_title = f"✅ {job.position} @ {job.company} ({job_source})"
            else:
                expander_title = f"{job.position} @ {job.company} ({job_source})"

            # Keep expanded if a cover letter is being drafted
            should_expand = f"cl_{job.id}" in st.session_state

            with st.expander(expander_title, expanded=should_expand):
                if is_applied:
                    st.success("You have already applied to this position! (Check History)")

                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**Location:** {job.location}")
                with col2:
                    st.markdown(f"[Apply Now 🚀]({job.url})")

                # Description Handling
                if job.description:
                    # Create a tabbed view for Summary (Text) and Full (HTML)
                    tab_summary, tab_full = st.tabs(["📝 Summary", "📄 Full Description"])

                    with tab_summary:
                        clean_desc = clean_html_text(job.description)
                        st.write(clean_desc[:500] + "..." if len(clean_desc) > 500 else clean_desc)

                    with tab_full:
                        # Render HTML safely
                        st.markdown(job.description, unsafe_allow_html=True)
                else:
                    st.info("No description available.")

                st.divider()

                if st.button("Generate Cover Letter", key=f"btn_{job.id}"):
                    # Use session state for resume content
                    resume_text = st.session_state.get("resume_content", "")
                    resume_obj = Resume(content=resume_text)
                    with st.spinner("AI is writing your letter..."):
                        letter = generate_cl_uc.execute(job, resume_obj)
                        st.session_state[f"cl_{job.id}"] = letter
                        st.rerun()

                # Show Cover Letter if generated
                if f"cl_{job.id}" in st.session_state:
                    st.subheader("📝 Draft Cover Letter")
                    st.text_area(
                        "Edit before applying:", value=st.session_state[f"cl_{job.id}"], height=200, key=f"txt_{job.id}"
                    )

                    if st.button("Mark as Applied ✅", key=f"apply_{job.id}"):
                        apply_job_uc.execute(job, status="Applied")
                        st.success(f"Application recorded for {job.company}!")
                        st.rerun()
                        # Optionally open URL
                        # st.write(f"Go apply here: {job.url}")

with tab2:
    st.header("History")
    history = apply_job_uc.get_history()

    if history:
        st.dataframe(history)
    else:
        st.info("No applications recorded yet.")

    st.divider()
    # Old Import/Export features removed in favor of Full Session Management
    st.caption("Use the 'Session Management' in the sidebar to backup/restore your history along with settings.")

# --- Finalize Export Button (Populate placeholder with latest state) ---
with export_placeholder.container():
    # Export
    session_data = {
        "resume_content": st.session_state.get("resume_content", ""),
        "search_keywords": st.session_state.get("search_keywords", ""),
        "search_location": st.session_state.get("search_location", ""),
        "search_language": st.session_state.get("search_language", ""),
        "application_history": apply_job_uc.get_history(),
        "use_ai_filter": st.session_state.get("use_ai_filter", True),
        "platform_states": {p: st.session_state.get(f"platform_{p}", True) for p in platforms_list},
    }
    json_str = json.dumps(session_data, indent=2)
    st.download_button(
        label="Export Session (JSON)", data=json_str, file_name="opushunt_session.json", mime="application/json"
    )
