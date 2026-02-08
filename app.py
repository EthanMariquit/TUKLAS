import streamlit as st
from PIL import Image
import os
import random
import requests
import time
from streamlit_lottie import st_lottie
from fpdf import FPDF
import datetime
# --- VOICE IMPORTS ---
import speech_recognition as sr
from streamlit_mic_recorder import mic_recorder
import io

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="TUKLAS Professional",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. SESSION STATE INITIALIZATION ---
if 'page' not in st.session_state:
    st.session_state.page = "🔍 Lesion Scanner"

# --- 3. ANIMATION LOADER ---
def load_lottieurl(url):
    try:
        r = requests.get(url, timeout=3)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

# --- 4. CUSTOM STYLING FUNCTIONS ---
def custom_box(text, color_class):
    st.markdown(f'<div class="{color_class}">{text.strip()}</div>', unsafe_allow_html=True)

def st_purple(text): custom_box(text, "purple-box")
def st_blue(text):   custom_box(text, "blue-box")
def st_red(text):    custom_box(text, "red-box")
def st_yellow(text): custom_box(text, "yellow-box")
def st_green(text):  custom_box(text, "green-box")

# Load Assets
lottie_microscope = load_lottieurl("https://lottie.host/0a927e36-6923-424d-8686-2484f4791e84/9z4s3l4Y2C.json") 
lottie_scanning = load_lottieurl("https://lottie.host/5a0c301c-6685-4841-8407-1e0078174f46/7Q1a54a72d.json") 

# --- 5. MEDICAL DATA ---
medical_data = {
    "Diamond-shaped Plaques (Erysipelas)": {
        "severity": "CRITICAL (High Mortality Risk)",
        "cause": "Caused by Erysipelothrix rhusiopathiae. Bacteria persists in soil for years.",
        "harm": "Rapid onset of high fever (40-42°C), septicemia, abortion, and sudden death.",
        "materials": "- Penicillin (Injectable)\n- Sterile Syringes\n- Digital Thermometer\n- Disinfectant",
        "prevention": "- Vaccinate breeding herd twice yearly.\n- Quarantine new animals for 30 days.",
        "steps": [
            "IMMEDIATE: Isolate the affected animal.",
            "TREATMENT: Administer Penicillin (1mL/10kg BW) every 12-24 hours.",
            "SUPPORT: Provide electrolytes to combat dehydration.",
            "MONITOR: Check temperature twice daily."
        ],
        "drug_name": "Penicillin G", "dosage_rate": 1.0, "dosage_per_kg": 10.0
    },
    "Hyperkeratosis / Crusting (Sarcoptic Mange)": {
        "severity": "MODERATE (Chronic / Contagious)",
        "cause": "Caused by the mite Sarcoptes scabiei var. suis. Highly contagious via direct contact.",
        "harm": "Intense itching causes weight loss and secondary bacterial infections.",
        "materials": "- Ivermectin or Doramectin\n- Knapsack Sprayer (Amitraz)\n- Skin Scraping Kit",
        "prevention": "- Treat sows 7-14 days before farrowing.\n- Treat boars every 3 months.",
        "steps": [
            "INJECT: Administer Ivermectin (1mL/33kg BW) subcutaneously.",
            "SPRAY: Apply Amitraz solution to the entire herd.",
            "REPEAT: Repeat treatment after 14 days.",
            "CLEAN: Scrub the pig with mild soap to remove crusts."
        ],
        "drug_name": "Ivermectin (1%)", "dosage_rate": 1.0, "dosage_per_kg": 33.0
    },
    "Greasy / Exudative Skin (Greasy Pig Disease)": {
        "severity": "HIGH (Especially in Piglets)",
        "cause": "Caused by Staphylococcus hyicus entering through skin abrasions.",
        "harm": "Toxins damage liver and kidneys. Mortality can reach 90% in piglets.",
        "materials": "- Antibiotics (Amoxicillin)\n- Antiseptic Soap\n- Electrolyte Solution",
        "prevention": "- Clip needle teeth within 24 hours.\n- Provide soft bedding.",
        "steps": [
            "WASH: Wash the pig with antiseptic soap daily.",
            "MEDICATE: Inject Amoxicillin for 3-5 days.",
            "HYDRATE: Oral rehydration is critical.",
            "ENVIRONMENT: Ensure the pen is dry and draft-free."
        ],
        "drug_name": "Amoxicillin LA", "dosage_rate": 1.0, "dosage_per_kg": 20.0
    },
    "Healthy": {
        "severity": "OPTIMAL",
        "cause": "Good husbandry and nutrition.",
        "harm": "N/A",
        "materials": "- Routine Vitamins\n- Vaccination Record",
        "prevention": "- Continue current vaccination program.\n- Monitor feed intake.",
        "steps": [
            "MAINTENANCE: Continue providing clean water and balanced feed.",
            "MONITORING: Observe for changes in appetite.",
            "RECORD: Log healthy status."
        ],
        "drug_name": "Multivitamins", "dosage_rate": 1.0, "dosage_per_kg": 10.0
    }
}

# --- 6. VOICE RECOGNITION HELPER ---
def recognize_audio(audio_bytes):
    r = sr.Recognizer()
    try:
        audio_file = io.BytesIO(audio_bytes)
        with sr.AudioFile(audio_file) as source:
            audio_data = r.record(source)
            text = r.recognize_google(audio_data)
            return text.lower()
    except:
        return None

# --- 7. PDF GENERATOR ---
class PDFReport(FPDF):
    def header(self):
        self.set_fill_color(0, 51, 102) 
        self.rect(0, 0, 210, 5, 'F')
        self.ln(5)
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'TUKLAS VETERINARY DIAGNOSTICS', 0, 1, 'L')
        self.set_font('Arial', '', 10)
        self.cell(0, 5, 'Rizal National Science High School (RiSci)', 0, 1, 'L')
        self.ln(10)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()} - Generated by Tuklas AI', 0, 0, 'C')

def clean_text(text):
    if not isinstance(text, str): return str(text)
    return text.encode('latin-1', 'ignore').decode('latin-1')

def create_pdf(img_path, diagnosis, confidence, info):
    pdf = PDFReport()
    pdf.add_page()
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, f"DIAGNOSIS: {clean_text(diagnosis)}", 0, 1)
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 10, f"Confidence: {confidence:.1f}%", 0, 1)
    
    # Add Image
    try:
        pdf.image(img_path, x=10, y=pdf.get_y(), w=100)
        pdf.ln(80) 
    except:
        pdf.cell(0, 10, "[Image Error]", 1, 1)

    # Treatment Info
    pdf.ln(5)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 10, "Treatment Protocol:", 0, 1)
    pdf.set_font("Arial", "", 10)
    for step in info['steps']:
        pdf.multi_cell(0, 5, f"- {clean_text(step)}")
        pdf.ln(1)
        
    return pdf.output(dest='S').encode('latin-1')

# --- 8. DIRECTORY DATA ---
contacts_data = [
    {"LGU": "Angono", "Office": "Municipal Veterinary Office", "Contact": "(02) 8451-1033"},
    {"LGU": "Antipolo City", "Office": "City Veterinary Office", "Contact": "(02) 8689-4514"},
    {"LGU": "Binangonan", "Office": "Municipal Agriculture Office", "Contact": "(02) 8234-2124"},
    {"LGU": "Cainta", "Office": "Municipal Agriculture Office", "Contact": "(02) 8696-2583"},
    {"LGU": "Morong", "Office": "Municipal Agriculture Office", "Contact": "(02) 8236-0428"},
    {"LGU": "Tanay", "Office": "Municipal Agriculture Office", "Contact": "(02) 8655-1773"},
    {"LGU": "Taytay", "Office": "Municipal Agriculture Office", "Contact": "(02) 8284-4700"},
]

# --- 9. CSS STYLING ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; }
    .purple-box, .blue-box, .red-box, .yellow-box, .green-box { padding: 15px; border-radius: 5px; margin-bottom: 10px; border: 1px solid #ddd; }
    .purple-box { background-color: #f3e5f5; border-color: #6A0DAD; color: #4a148c; }
    .blue-box { background-color: #e3f2fd; border-color: #0056b3; color: #0d47a1; }
    .red-box { background-color: #ffebee; border-color: #FF4B4B; color: #b71c1c; }
    .yellow-box { background-color: #fff8e1; border-color: #FFAA00; color: #ff6f00; }
    .green-box { background-color: #e8f5e9; border-color: #00C853; color: #1b5e20; }
    .report-box { background-color: #f8f9fa; padding: 20px; border-radius: 10px; border-left: 5px solid #0056b3; }
    .footer { position: fixed; bottom: 0; width: 100%; background-color: #2c3e50; color: white; text-align: center; padding: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 10. LOAD AI MODEL ---
folder = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(folder, "best.pt")
try:
    from ultralytics import YOLO
    if os.path.exists(model_path):
        model = YOLO(model_path)
    else:
        model = None
        st.error("⚠️ 'best.pt' model not found.")
except ImportError:
    st.error("❌ System Error: Libraries missing.")
    st.stop()

# --- 11. SIDEBAR & VOICE NAV ---
with st.sidebar:
    if lottie_microscope: st_lottie(lottie_microscope, height=150)
    st.title("TUKLAS Diagnostics")
    
    st.markdown("---")
    st.subheader("🎙️ Voice Control")
    st.caption("Say 'Scanner' or 'Directory'")
    
    # Voice Button
    audio = mic_recorder(start_prompt="🎤 Speak", stop_prompt="⏹️ Stop", key='recorder')
    
    if audio:
        text_command = recognize_audio(audio['bytes'])
        if text_command:
            st.success(f"Heard: '{text_command}'")
            if "scan" in text_command or "lesion" in text_command:
                st.session_state.page = "🔍 Lesion Scanner"
                st.rerun()
            elif "directory" in text_command or "contact" in text_command:
                st.session_state.page = "📞 Local Directory"
                st.rerun()
            elif "dose" in text_command or "calc" in text_command:
                st.toast("💊 Dosage Calculator is below!")
    
    # Navigation Dropdown (Synced)
    page_options = ["🔍 Lesion Scanner", "📞 Local Directory"]
    try:
        idx = page_options.index(st.session_state.page)
    except:
        idx = 0
    selected = st.selectbox("Navigate", page_options, index=idx)
    if selected != st.session_state.page:
        st.session_state.page = selected
        st.rerun()

    # Dosage Calculator
    st.markdown("---")
    st.subheader("💊 Dosage Calculator")
    calc_weight = st.number_input("Pig Weight (kg)", min_value=1.0, value=50.0)
    drug_list = ["Select Drug..."] + [v['drug_name'] for k, v in medical_data.items()]
    sel_drug = st.selectbox("Medication", drug_list)
    
    if sel_drug != "Select Drug...":
        d_info = next((v for k, v in medical_data.items() if v['drug_name'] == sel_drug), None)
        if d_info:
            vol = (calc_weight / d_info['dosage_per_kg']) * d_info['dosage_rate']
            st.info(f"**Inject:** {vol:.2f} mL")

# --- 12. MAIN PAGES ---

# PAGE: SCANNER
if st.session_state.page == "🔍 Lesion Scanner":
    st.title("🔬 Smart Veterinary Scanner")
    uploaded_file = st.file_uploader("Upload Image", type=['jpg', 'png', 'jpeg'])

    if uploaded_file:
        img = Image.open(uploaded_file)
        with open("temp.jpg", "wb") as f:
            f.write(uploaded_file.getbuffer())

        c1, c2 = st.columns(2)
        with c1: st.image(img, use_container_width=True, caption="Specimen")
        
        if st.button("🔍 Analyze Specimen"):
            if model:
                with st.spinner("Analyzing..."):
                    if lottie_scanning: st_lottie(lottie_scanning, height=150, key="scan_anim")
                    results = model.predict(img)
                    res_plotted = results[0].plot()
                    
                    # Get Data
                    probs = results[0].boxes.conf.tolist()
                    conf = (sum(probs)/len(probs) * 100) if probs else 0
                    names = [model.names[int(c)] for c in results[0].boxes.cls]
                    top_dx = names[0] if names else "Healthy"
                
                with c2:
                    st.image(res_plotted, use_container_width=True, caption="AI Detection")
                    st.metric("Confidence", f"{conf:.1f}%")
                
                # Report Section
                st.markdown("---")
                if "Healthy" in top_dx:
                    st_green("✅ **Result:** Healthy Skin. No lesions detected.")
                else:
                    info = medical_data.get(top_dx)
                    if not info:
                         # Fallback search
                         for k in medical_data:
                             if k in top_dx: info = medical_data[k]; break
                    
                    if info:
                        st.subheader(f"⚠️ Detected: {top_dx}")
                        st_red(f"**Severity:** {info['severity']}")
                        
                        with st.expander("📋 Treatment Protocol", expanded=True):
                            st.write(f"**Cause:** {info['cause']}")
                            st.write("**Steps:**")
                            for s in info['steps']: st.write(f"- {s}")
                            
                            # PDF Download
                            pdf_data = create_pdf("temp.jpg", top_dx, conf, info)
                            st.download_button("📥 Download PDF Report", pdf_data, "Report.pdf", "application/pdf")

# PAGE: DIRECTORY
elif st.session_state.page == "📞 Local Directory":
    st.title("📞 Agricultural Directory")
    search = st.text_input("Search Municipality", "")
    
    c1, c2 = st.columns(2)
    found = [x for x in contacts_data if search.lower() in x['LGU'].lower()]
    
    for i, d in enumerate(found):
        with c1 if i % 2 == 0 else c2:
            with st.expander(f"📍 {d['LGU']}"):
                st.write(f"**Office:** {d['Office']}")
                st.write(f"**Phone:** `{d['Contact']}`")

# Footer
st.markdown("<br><br><br>", unsafe_allow_html=True)
st.markdown('<div class="footer">© 2025 Rizal National Science High School (RiSci) | TUKLAS Team</div>', unsafe_allow_html=True)
