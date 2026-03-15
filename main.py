import os
import requests
import json
import csv
from datetime import datetime
from google import genai
from dotenv import load_dotenv

# --- Configuration ---
# You need to get a FREE API key from: https://aistudio.google.com/app/apikey
# And set it in a .env file as GEMINI_API_KEY=...
GEMINI_MODEL_NAME = "gemini-1.5-flash" 
APPLICATIONS_FILE = "applications_history.csv"

def get_genai_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("UYARI: GEMINI_API_KEY bulunamadı. Akıllı özellikler çalışmayacak.")
        print("Lütfen https://aistudio.google.com/app/apikey adresinden ücretsiz bir anahtar alıp .env dosyasına ekleyin.")
        return None
    return genai.Client(api_key=api_key)

def read_resume(filepath: str) -> str:
    """Reads the user's resume to be used for matching later."""
    try:
        with open(filepath, 'r') as file:
            return file.read()
    except FileNotFoundError:
        print("Resume file not found.")
        return ""

def fetch_remoteok_jobs(tag="ios"):
    print(f"Fetching '{tag}' jobs from RemoteOK...")
    url = f"https://remoteok.com/api?tag={tag}"
    headers = {"User-Agent": "JobSearchAutomation/1.0"}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data[1:] if len(data) > 1 else []
    except Exception as e:
        print(f"Error fetching jobs: {e}")
        return []

def generate_cover_letter(client, job_details: dict, resume_text: str) -> str:
    """
    Generates a tailored cover letter using Gemini API (New SDK).
    Includes fallback to different models if one fails.
    """
    if not client:
        return "Cover letter oluşturulamadı (Client yok)."

    prompt = f"""
    Sen deneyimli bir iOS Geliştiricisisin. Aşağıdaki özgeçmişi (Resume) ve iş ilanını (Job Description) kullanarak,
    bu işe başvurmak için profesyonel, samimi ve etkileyici bir Cover Letter (Ön Yazı) yaz.
    
    Özgeçmiş:
    {resume_text}
    
    İş İlanı:
    Şirket: {job_details.get('company')}
    Pozisyon: {job_details.get('position')}
    Açıklama: {job_details.get('description')}
    
    Kurallar:
    1. Mektup İngilizce olsun.
    2. {job_details.get('company')} şirketine hitaben yaz.
    3. Özgeçmişteki en alakalı deneyimleri vurgula.
    4. Kısa ve öz olsun (maksimum 200-250 kelime).
    5. Placeholders (köşeli parantez) bırakma, bilgileri doldur.
    """
    
    # List of models to try in order of preference
    # Updated based on available models in the current environment
    models_to_try = [
        "gemini-2.5-flash",
        "gemini-2.0-flash",
        "gemini-flash-latest",
        "gemini-3-flash-preview",
        "gemini-2.5-pro",
        "gemini-pro-latest"
    ]
    
    last_error = None
    
    for model_name in models_to_try:
        try:
            # print(f"Trying model: {model_name}...") # Debug log (optional)
            response = client.models.generate_content(
                model=model_name,
                contents=prompt
            )
            return response.text
        except Exception as e:
            # print(f"Model {model_name} failed. Trying next...")
            last_error = e
            continue
            
    return f"Hata oluştu: Tüm modeller denendi ancak başarısız oldu.\nSon hata: {last_error}\nLütfen API'nin etkinleştirildiğinden emin olun."

def save_application_record(job: dict, status: str):
    """
    Saves the job application details to a CSV file.
    """
    file_exists = os.path.isfile(APPLICATIONS_FILE)
    
    with open(APPLICATIONS_FILE, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        
        # Write header if file is new
        if not file_exists:
            writer.writerow(['Date', 'Company', 'Position', 'Location', 'URL', 'Status'])
            
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            job.get('company'),
            job.get('position'),
            job.get('location', 'Remote'),
            job.get('url'),
            status
        ])
    print(f"   -> Kayıt eklendi: {APPLICATIONS_FILE}")

def apply_to_job(job: dict, cover_letter: str):
    """
    Simulates the application process. 
    In a real scenario, this would open the browser or send an email.
    """
    apply_url = job.get('apply_url') or job.get('url')
    print(f"\n--- Başvuru İşlemi ---")
    print(f"Başvuru Linki: {apply_url}")
    print("Otomatik başvuru henüz tarayıcı otomasyonu gerektiriyor.")
    print("Şimdilik linki panoya kopyaladım veya tarayıcıda açabilirim.")
    
    # Open link in browser
    os.system(f"open '{apply_url}'")
    
    # Save record
    save_application_record(job, status="Applied (Manual Trigger)")

def main():
    load_dotenv()
    print("Job Searcher Automation started...\n")
    
    client = get_genai_client()
    
    resume_path = os.path.join(os.path.dirname(__file__), "resume.txt")
    resume_text = read_resume(resume_path)
    
    jobs = fetch_remoteok_jobs(tag="ios")
    print(f"Total iOS jobs found: {len(jobs)}\n")
    
    # Process only top 3 jobs to save time/tokens for demo
    for job in jobs[:3]:
        company = job.get('company')
        position = job.get('position')
        location = job.get('location', '')
        url = job.get('url')
        
        print(f"--------------------------------------------------")
        print(f"İncelenen İlan: {position} @ {company}")
        print(f"Lokasyon: {location}")
        print(f"Link: {url}")
        
        if client:
            print("Cover Letter hazırlanıyor...")
            cover_letter = generate_cover_letter(client, job, resume_text)
            print("\n--- OLUŞTURULAN COVER LETTER TASLAĞI ---")
            print(cover_letter)
            print("----------------------------------------\n")
            
            if "Hata oluştu" in cover_letter:
                 print("API Hatası nedeniyle devam edilemiyor. Lütfen yukarıdaki hatayı kontrol edin.")
                 break

            choice = input(f"Bu ilana ({company}) başvurmak istiyor musun? [E]vet / [H]ayır / [G]eç: ").lower()
            
            if choice == 'e':
                apply_to_job(job, cover_letter)
                print("Başvuru sayfasına yönlendirildiniz.")
            elif choice == 'h':
                print("İlan pas geçildi.")
            else:
                continue
        else:
            print("API Key olmadığı için detaylı analiz yapılamadı.")
            print(f"URL: {job.get('url')}")

if __name__ == '__main__':
    main()
