import streamlit as st
import os
import sys
import html
from bs4 import BeautifulSoup

# Add project root to path so we can import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from dotenv import load_dotenv
from src.domain.entities import Resume
from src.infrastructure.repositories.remoteok_repo import RemoteOKJobRepository
from src.infrastructure.repositories.rss_repo import RSSJobRepository
from src.infrastructure.repositories.remotive_repo import RemotiveJobRepository
from src.infrastructure.repositories.arbeitnow_repo import ArbeitnowJobRepository
from src.infrastructure.repositories.csv_repo import CSVApplicationRepository
from src.infrastructure.services.gemini_service import GeminiLLMService
from src.infrastructure.services.pdf_service import PDFService
from src.application.use_cases import SearchJobsUseCase, GenerateCoverLetterUseCase, ApplyJobUseCase

# --- Setup & Injection ---
load_dotenv()

# Repositories & Services
remoteok_repo = RemoteOKJobRepository()
weworkremotely_repo = RSSJobRepository(feed_url="https://weworkremotely.com/categories/remote-programming-jobs.rss", platform_name="WeWorkRemotely")
remotive_repo = RemotiveJobRepository()
arbeitnow_repo = ArbeitnowJobRepository()

app_repo = CSVApplicationRepository()
llm_service = GeminiLLMService()
pdf_service = PDFService()

# Services Map (for UI selection)
AVAILABLE_PLATFORMS = {
    "RemoteOK": remoteok_repo,
    "WeWorkRemotely": weworkremotely_repo,
    "Remotive": remotive_repo,
    "Arbeitnow": arbeitnow_repo,
    # "LinkedIn": None, # Placeholder for future
}

# Use Cases (Initialized dynamically in UI)
generate_cl_uc = GenerateCoverLetterUseCase(llm_service)
apply_job_uc = ApplyJobUseCase(app_repo)

# --- UI Helper Functions ---
def load_resume():
    try:
        with open("resume.txt", "r") as f:
            return f.read()
    except FileNotFoundError:
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
    clean_text = soup.get_text(separator=' ', strip=True)
    return clean_text

# --- Streamlit App ---
st.set_page_config(page_title="OpusHunt | Find Your Masterpiece", page_icon="🎯", layout="wide")

st.title("🎯 OpusHunt")
st.markdown("Find the job that fits your masterpiece.")

# Sidebar: Configuration & Resume
with st.sidebar:
    st.header("👤 Your Profile")
    
    # File Uploader for PDF
    uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
    
    current_resume = load_resume()
    
    if uploaded_file is not None:
        with st.spinner("Extracting text from PDF..."):
            extracted_text = pdf_service.extract_text(uploaded_file.getvalue())
            if extracted_text:
                current_resume = extracted_text
                st.success("PDF loaded successfully!")
    
    resume_content = st.text_area("Resume Content (Editable)", value=current_resume, height=300)
    
    if st.button("Save Resume"):
        with open("resume.txt", "w") as f:
            f.write(resume_content)
        st.success("Resume saved!")
    
    st.divider()
    st.header("⚙️ Search Settings")
    
    # Platform Selection
    st.subheader("Platforms")
    selected_platform_names = []
    
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        if st.checkbox("RemoteOK", value=True):
            selected_platform_names.append("RemoteOK")
        if st.checkbox("WeWorkRemotely", value=True):
            selected_platform_names.append("WeWorkRemotely")
    with col_p2:
        if st.checkbox("Remotive", value=True):
            selected_platform_names.append("Remotive")
        if st.checkbox("Arbeitnow", value=True):
            selected_platform_names.append("Arbeitnow")
        if st.checkbox("LinkedIn (Soon)", value=False, disabled=True):
            pass
            
    # Keywords
    st.subheader("Keywords")
    search_tag = st.text_input("Enter tags (comma separated)", value="ios, swift")

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
        tags = [t.strip() for t in search_tag.split(',') if t.strip()]
        if tags:
            st.markdown(" ".join([f"`{t}`" for t in tags]))
        else:
            st.caption("No keywords entered")

    st.divider()

    if st.button("Fetch Jobs", type="primary"):
        # Explicitly clear the jobs from session state before fetching new ones
        if 'jobs' in st.session_state:
            del st.session_state['jobs']
            
        if not selected_platform_names:
            st.warning("Please select at least one platform.")
        else:
            # Prepare Use Case with selected repos
            selected_repos = [AVAILABLE_PLATFORMS[name] for name in selected_platform_names if AVAILABLE_PLATFORMS.get(name)]
            search_jobs_uc = SearchJobsUseCase(selected_repos)
            
            with st.spinner(f"Fetching jobs from {', '.join(selected_platform_names)}..."):
                jobs = search_jobs_uc.execute(search_tag)
                st.session_state['jobs'] = jobs
                st.success(f"Found {len(jobs)} jobs.")

    if 'jobs' in st.session_state:
        for job in st.session_state['jobs']:
            # Skip invalid/empty jobs
            if not job.position or job.position == "Unknown" or not job.company:
                continue
                
            # Safely get source to prevent AttributeError from old cached objects
            job_source = getattr(job, 'source', 'Unknown')
            job_date = getattr(job, 'date', None)
                
            with st.expander(f"{job.position} @ {job.company} ({job.location})"):
                st.caption(f"Source: **{job_source}** | Date: {job_date if job_date else 'N/A'}")
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"**Description Snippet:**")
                    # Clean HTML tags and decode HTML entities for display
                    clean_desc = clean_html_text(job.description)
                    st.text(clean_desc[:500] + ("..." if len(clean_desc) > 500 else ""))
                    st.markdown(f"[View Full Job Listing]({job.url})")
                
                with col2:
                    if st.button(f"Generate Cover Letter ✨", key=f"btn_{job.id}"):
                        resume_obj = Resume(content=resume_content)
                        with st.spinner("AI is writing your letter..."):
                            letter = generate_cl_uc.execute(job, resume_obj)
                            st.session_state[f"cl_{job.id}"] = letter
                
                # Show Cover Letter if generated
                if f"cl_{job.id}" in st.session_state:
                    st.subheader("📝 Draft Cover Letter")
                    st.text_area("Edit before applying:", value=st.session_state[f"cl_{job.id}"], height=200, key=f"txt_{job.id}")
                    
                    if st.button("Mark as Applied ✅", key=f"apply_{job.id}"):
                        apply_job_uc.execute(job, status="Applied")
                        st.success(f"Application recorded for {job.company}!")
                        # Optionally open URL
                        # st.write(f"Go apply here: {job.url}")

with tab2:
    st.header("History")
    history = apply_job_uc.get_history()
    if history:
        st.dataframe(history)
    else:
        st.info("No applications recorded yet.")

