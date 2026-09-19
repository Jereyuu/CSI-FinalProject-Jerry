import os
import re
from typing import List, Dict

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from google import genai

st.set_page_config(page_title="MedBot", page_icon="🩺", layout="wide")

load_dotenv("api.env")

print("Current folder:", os.getcwd())
print("api.env exists:", os.path.exists("api.env"))

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    st.error("GEMINI_API_KEY was not found. Add it to a .env file.")
    st.stop()

client = genai.Client(api_key=API_KEY)

#Gemini-inspired
st.markdown("""
<style>
.stApp {
    background:
        radial-gradient(circle at 85% 8%, rgba(190,20,35,.10), transparent 28%),
        radial-gradient(circle at 10% 70%, rgba(190,20,35,.055), transparent 25%),
        #ffffff;
    color: #111111;
}
[data-testid="stHeader"] {
    background: rgba(255,255,255,.92);
    backdrop-filter: blur(12px);
}
section[data-testid="stSidebar"] {
    background: #0b0b0b;
    border-right: 1px solid #242424;
}
section[data-testid="stSidebar"] .block-container {
    padding: 1.25rem 1rem;
}
.brand {
    font-size: 1.45rem;
    font-weight: 800;
    letter-spacing: -.04em;
    margin-bottom: 1.5rem;
    color: #fff;
}
.brand span { color: #e31b2d; }
.side-card {
    padding: 14px;
    border-radius: 16px;
    background: #151515;
    border: 1px solid #292929;
    margin-bottom: 12px;
    color: #fff;
    box-shadow: 0 8px 24px rgba(0,0,0,.18);
}
.side-muted {
    color: #b7b7b7;
    font-size: .78rem;
    line-height: 1.45;
}
section[data-testid="stSidebar"] h3 { color: #fff; }
section[data-testid="stSidebar"] hr { border-color: #292929; }
section[data-testid="stSidebar"] .stCaption { color: #888; }

.main-title {
    text-align: center;
    margin-top: 7vh;
    margin-bottom: .35rem;
    font-size: 2.8rem;
    font-weight: 800;
    letter-spacing: -.055em;
    color: #111;
}
.gradient-text {
    background: linear-gradient(90deg,#111 15%,#c91528 55%,#e31b2d 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.subtitle {
    text-align: center;
    color: #6b6b6b;
    font-size: 1rem;
    margin-bottom: 2.4rem;
}
.chat-wrap { max-width: 900px; margin: 0 auto; }
[data-testid="stChatMessage"] {
    border-radius: 20px;
    padding: .5rem .8rem;
    margin-bottom: .65rem;
}
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] {
    line-height: 1.65;
}
[data-testid="stChatInput"] { max-width: 900px; margin: 0 auto; }
[data-testid="stChatInput"] textarea {
    border-radius: 26px !important;
    border: 1.5px solid #d5d5d5 !important;
    background: #fff !important;
    color: #111 !important;
    padding: 14px 18px !important;
    font-size: 1rem !important;
    box-shadow: 0 6px 24px rgba(0,0,0,.07) !important;
}
[data-testid="stChatInput"] textarea:focus {
    border-color: #d51d31 !important;
    box-shadow: 0 0 0 2px rgba(213,29,49,.12),
                0 8px 28px rgba(0,0,0,.08) !important;
}
.stButton > button {
    min-height: 52px;
    border-radius: 17px;
    border: 1px solid #ddd;
    background: #fff;
    color: #171717;
    font-weight: 600;
    transition: all .18s ease;
    box-shadow: 0 5px 18px rgba(0,0,0,.055);
}
.stButton > button:hover {
    border-color: #d51d31;
    color: #b51225;
    background: #fff7f7;
    transform: translateY(-2px);
    box-shadow: 0 9px 24px rgba(190,20,35,.12);
}
section[data-testid="stSidebar"] .stButton > button {
    background: #e31b2d;
    color: #fff;
    border: 1px solid #e31b2d;
    box-shadow: 0 8px 20px rgba(227,27,45,.20);
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: #bd1223;
    color: #fff;
    border-color: #bd1223;
}
.stSpinner > div { border-top-color: #e31b2d !important; }
a { color: #c91528 !important; }
.disclaimer {
    max-width: 900px;
    margin: 18px auto 5rem;
    text-align: center;
    color: #858585;
    font-size: .75rem;
    line-height: 1.45;
}
/* Make general text black */
.stApp,
.stApp p,
.stApp span,
.stApp div,
.stApp label {
    color: #000000;
}
[data-testid="stChatMessage"] {
    color: #000000;
}

[data-testid="stChatMessage"] p {
    color: #000000;
}

/* "Thinking..." spinner */
[data-testid="stSpinner"] {
    color: #000000;
}

[data-testid="stSpinner"] p {
    color: #000000;
}

.answer {
    color: #000000;
}
#MainMenu, footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# Built-in first-aid kit
FIRST_AID_ITEMS = [
    ("Adhesive Bandages / Band-Aids", "Cover small cuts, scrapes, and minor wounds."),
    ("Sterile Gauze Pads", "Cover wounds and help absorb blood."),
    ("Roller / Crepe Bandages", "Secure dressings and provide light support."),
    ("Triangular Bandages", "Support or immobilize an injured arm."),
    ("Non-Stick Wound Dressings", "Cover wounds without sticking strongly to the wound."),
    ("Medical Tape", "Secure gauze and wound dressings."),
    ("Antiseptic wipes or solution", "Clean around minor wounds."),
    ("Saline solution", "Rinse wounds or flush the eyes when appropriate."),
    ("Antibiotic ointment", "May be used for some minor wounds according to its label."),
    ("Disposable non-latex (nitrile) gloves", "Protect the responder's hands during first aid."),
    ("Scissors", "Cut tape, dressings, or clothing when necessary."),
    ("Tweezers", "Remove small, accessible splinters."),
    ("CPR face mask/shield", "Provides a barrier during CPR."),
    ("Instant cold pack", "Apply cold to some minor injuries such as sprains or swelling."),
    ("Emergency thermal blanket", "Help keep a person warm."),
    ("Flashlight", "Provide light in an emergency."),
    ("Notepad and pen", "Record useful information during an emergency."),
]

#Built-in medical knowledge
MEDICAL_KNOWLEDGE_DATA = [
    {"category":"wound","situation":"minor cut scrape abrasion","what_to_do":"Wash hands, gently rinse the wound with clean running water or saline, control minor bleeding with gentle pressure, and cover with a clean dressing.","what_not_to_do":"Do not put dirt or unapproved substances into the wound. Do not pick at a healing wound.","when_to_seek_help":"Seek medical care for a deep or large wound, uncontrolled bleeding, a serious accident, or signs of infection."},
    {"category":"bleeding","situation":"minor bleeding","what_to_do":"Use clean gauze or a clean dressing and apply steady direct pressure.","what_not_to_do":"Do not repeatedly lift the dressing to check while bleeding continues.","when_to_seek_help":"Get urgent professional help if bleeding is severe, does not stop with pressure, or the person becomes very unwell."},
    {"category":"burn","situation":"minor burn heat burn","what_to_do":"Cool the burn with cool running water and remove nearby jewelry or tight items if they are not stuck.","what_not_to_do":"Do not apply ice directly to the burn and do not break blisters.","when_to_seek_help":"Seek medical care for extensive, deep, electrical, chemical, or facial burns."},
    {"category":"sprain_or_strain","situation":"twisted ankle sprain strain swelling","what_to_do":"Rest the injured area and use a wrapped cold pack for short periods to help with swelling.","what_not_to_do":"Do not force movement through significant pain.","when_to_seek_help":"Seek assessment for severe pain, major swelling, inability to use the limb, or concern for fracture."},
    {"category":"fracture_or_injury","situation":"possible broken bone serious injury","what_to_do":"Keep the injured area as still and comfortable as possible and seek professional medical assessment.","what_not_to_do":"Do not try to straighten a visibly deformed limb.","when_to_seek_help":"Prompt medical evaluation is important when a fracture is suspected."},
    {"category":"nosebleed","situation":"nose bleeding nosebleed","what_to_do":"Sit upright, lean slightly forward, and gently pinch the soft part of the nose continuously for several minutes.","what_not_to_do":"Do not tilt the head backward.","when_to_seek_help":"Seek medical help if bleeding is heavy, follows a significant injury, or does not stop."},
    {"category":"eye_problem","situation":"dust foreign object eye irritation","what_to_do":"Rinse the eye gently with clean water or saline if a small loose particle is present.","what_not_to_do":"Do not rub the eye or forcefully remove an embedded object.","when_to_seek_help":"Get medical care for vision changes, significant pain, chemical exposure, or an embedded object."},
    {"category":"bite_or_sting","situation":"insect bite sting","what_to_do":"Move away from the source, gently clean the area, and use a wrapped cold pack for swelling when appropriate.","what_not_to_do":"Do not scratch the area repeatedly.","when_to_seek_help":"Seek urgent help for signs of a severe allergic reaction or rapidly worsening symptoms."},
    {"category":"animal_bite","situation":"animal bite dog cat bite","what_to_do":"Clean the wound with running water and seek medical advice because animal bites can become infected.","what_not_to_do":"Do not ignore a bite just because the wound looks small.","when_to_seek_help":"Professional medical assessment is recommended for animal bites, especially if skin is broken."},
    {"category":"splinter","situation":"small splinter foreign object skin","what_to_do":"Clean the area and use clean tweezers to remove a small, easily accessible splinter.","what_not_to_do":"Do not dig deeply into the skin.","when_to_seek_help":"Seek help if the splinter is deeply embedded, difficult to remove, or becomes infected."},
    {"category":"blister","situation":"friction blister","what_to_do":"Protect the area with a clean dressing and reduce further friction.","what_not_to_do":"Do not deliberately pop a blister.","when_to_seek_help":"Seek medical advice if it becomes increasingly red, painful, swollen, or drains concerning fluid."},
    {"category":"heat_illness","situation":"heat exhaustion overheating","what_to_do":"Move to a cooler place, rest, and drink fluids if the person is awake and able to drink.","what_not_to_do":"Do not leave someone who is becoming confused or seriously unwell alone.","when_to_seek_help":"Confusion, fainting, seizures, or severe worsening symptoms require urgent professional help."},
    {"category":"hypothermia","situation":"cold exposure very cold","what_to_do":"Move to a warm, sheltered place and remove wet clothing if possible.","what_not_to_do":"Do not use extreme direct heat on a severely cold person.","when_to_seek_help":"Severe shivering, confusion, unusual drowsiness, or loss of consciousness requires urgent medical help."},
    {"category":"fainting","situation":"faint passed out dizziness","what_to_do":"Help the person lie down safely and check whether they respond normally.","what_not_to_do":"Do not give food or drink to someone who is not fully alert.","when_to_seek_help":"Seek urgent help if the person does not recover normally, has serious injury, chest symptoms, breathing problems, or repeated fainting."},
    {"category":"seizure","situation":"seizure convulsion","what_to_do":"Keep the area safe, protect the person from nearby hazards, and stay with them until they recover.","what_not_to_do":"Do not restrain the person or put objects in their mouth.","when_to_seek_help":"Urgent help is needed for a first seizure, prolonged seizure, repeated seizures without recovery, serious injury, or breathing problems."},
    {"category":"choking","situation":"choking cannot breathe airway blockage","what_to_do":"Treat choking as an emergency and follow recognized first-aid guidance while getting emergency help.","what_not_to_do":"Do not give food or drink to a person who is choking.","when_to_seek_help":"Choking with inability to breathe, speak, or cough effectively is an emergency."},
    {"category":"drowning","situation":"drowning near drowning water accident","what_to_do":"Get emergency help immediately and prioritize safe rescue. If the person is unresponsive and not breathing normally, follow emergency CPR guidance if trained.","what_not_to_do":"Do not put yourself in danger during a rescue.","when_to_seek_help":"A drowning incident requires urgent professional assessment, even if the person seems to recover."},
    {"category":"poisoning","situation":"poison swallowed toxic substance","what_to_do":"Get urgent advice from local emergency or poison-control services and keep the substance/container available for identification.","what_not_to_do":"Do not make someone vomit unless specifically instructed by a qualified professional.","when_to_seek_help":"Suspected poisoning can be urgent, especially with breathing problems, severe symptoms, altered alertness, or an unknown exposure."},
    {"category":"head_injury","situation":"head bump concussion injury","what_to_do":"Stop the activity and monitor the person. A responsible adult should help monitor a young person after a head injury.","what_not_to_do":"Do not ignore worsening symptoms after a head injury.","when_to_seek_help":"Urgent assessment is needed for worsening headache, repeated vomiting, unusual behavior, confusion, seizure, weakness, or loss of consciousness."},
    {"category":"wound_infection","situation":"infected wound redness swelling pus","what_to_do":"Keep the area clean and covered and seek medical advice if infection is suspected.","what_not_to_do":"Do not squeeze or repeatedly manipulate the wound.","when_to_seek_help":"Increasing redness, warmth, swelling, pain, pus, fever, or spreading redness should be medically assessed."},
    {"category":"minor_pain","situation":"minor pain discomfort","what_to_do":"Rest the affected area and monitor symptoms. Use appropriate first-aid measures when relevant.","what_not_to_do":"Do not ignore severe, sudden, or rapidly worsening pain.","when_to_seek_help":"Seek professional advice for severe, persistent, unexplained, or worsening pain."},
    {"category":"recovery","situation":"recovery after minor injury","what_to_do":"Allow the affected area to rest and gradually return to normal activity as symptoms improve.","what_not_to_do":"Do not return to demanding activity if symptoms are worsening.","when_to_seek_help":"Seek assessment if recovery is not progressing or symptoms become worse."},
]
medical_knowledge_df = pd.DataFrame(MEDICAL_KNOWLEDGE_DATA)

STOPWORDS = {"a","an","and","are","am","at","be","been","but","by","can","could","do","does","for","from","get","got","had","has","have","how","i","if","in","is","it","me","my","of","on","or","should","that","the","this","to","was","what","when","where","with","would","you","your"}

def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9\s]", " ", str(text).casefold())).strip()

def tokenize(text: str) -> set:
    return {w for w in re.findall(r"\b[a-z0-9]+\b", normalize_text(text)) if w not in STOPWORDS}

def get_kit_context(question: str, top_n: int = 5) -> str:
    q = tokenize(question)
    results = []
    for item, use in FIRST_AID_ITEMS:
        score = len(q & tokenize(item + " " + use))
        if score:
            results.append((score, item, use))
    results.sort(key=lambda x: (-x[0], x[1]))
    return "\n".join(f"- {item}: {use}" for _, item, use in results[:top_n]) or "No specific first-aid-kit item was matched."

def get_medical_knowledge_context(question: str, top_n: int = 5) -> str:
    q = tokenize(question)
    results = []
    for _, row in medical_knowledge_df.iterrows():
        text = " ".join(str(row[c]) for c in ["category","situation","what_to_do","what_not_to_do","when_to_seek_help"])
        score = len(q & tokenize(text))
        if score:
            results.append((score, row))
    results.sort(key=lambda x: (-x[0], x[1]["category"]))
    blocks = []
    for _, r in results[:top_n]:
        blocks.append(f"Category: {r['category']}\nSituation: {r['situation']}\nWhat to do: {r['what_to_do']}\nWhat not to do: {r['what_not_to_do']}\nWhen to seek help: {r['when_to_seek_help']}")
    return "\n\n".join(blocks) or "No specific medical-knowledge entry was matched."

SYSTEM_INSTRUCTION = """
You are MedBot, an educational first-aid and health-information assistant.
Provide general information, not a diagnosis. Do not claim certainty about a medical condition.
Prioritize urgent professional help for possible emergencies.
Use supplied medical knowledge and first-aid-kit information when relevant.
Do not invent first-aid-kit items. If information is missing, say so or ask a short clarifying question.
Answer in the user's language when possible.
"""

EMERGENCY_TERMS = [
    "cannot breathe","can't breathe","not breathing","difficulty breathing",
    "severe bleeding","uncontrolled bleeding","choking","drowning","unconscious",
    "passed out","seizure","poisoning","overdose","severe allergic reaction",
    "anaphylaxis","stroke","heart attack","chest pain","major injury","serious injury"
]

def check_for_emergency(question: str) -> bool:
    text = normalize_text(question)
    if any(term in text for term in EMERGENCY_TERMS):
        return True
    try:
        r = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=f"""Decide whether this health question describes a POTENTIAL MEDICAL EMERGENCY.
Consider the meaning even if it is not English. Return ONLY YES or NO.
Question: {question}"""
        )
        return r.text.strip().upper().startswith("YES")
    except Exception:
        return False

def emergency_response(question: str) -> str:
    try:
        r = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=f"""{SYSTEM_INSTRUCTION}
The user may be describing a medical emergency.
Respond briefly and calmly. Tell them to contact their local emergency service or get immediate help from a nearby responsible adult/person. Do not diagnose. Answer in the same language when possible.
User: {question}"""
        )
        return r.text.strip()
    except Exception:
        return "This may be an emergency. Please contact your local emergency service or get immediate help from a nearby responsible adult/person."

def generate_medbot_response(question: str) -> str:
    if check_for_emergency(question):
        return emergency_response(question)
    prompt = f"""{SYSTEM_INSTRUCTION}

Patient's question:
{question}

Relevant medical knowledge:
{get_medical_knowledge_context(question)}

Relevant first-aid-kit information:
{get_kit_context(question)}

Give a useful, understandable answer. Do not diagnose. Only mention kit items that appear above. Clearly say when professional medical assessment may be needed."""
    r = client.models.generate_content(model="gemini-3.6-flash", contents=prompt)
    return r.text.strip()

#Session State
if "messages" not in st.session_state:
    st.session_state.messages = []

#Sidebar
with st.sidebar:
    st.markdown('<div class="brand"><span>✦ MedBot</span></div>', unsafe_allow_html=True)
    if st.button("＋ New chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    st.markdown("### About")
    st.markdown('<div class="side-card"><strong>MedBot</strong><br><span class="side-muted">Educational first-aid and health-information assistant powered by Gemini.</span></div>', unsafe_allow_html=True)
    st.markdown("### Knowledge")
    st.markdown(f'<div class="side-card">🩹 <strong>{len(FIRST_AID_ITEMS)}</strong> first-aid kit items<br>📚 <strong>{len(medical_knowledge_df)}</strong> medical knowledge entries</div>', unsafe_allow_html=True)
    st.markdown("---")
    st.caption("MedBot is educational and does not replace professional medical care.")

#Main
if not st.session_state.messages:
    st.markdown('<div class="main-title"><span class="gradient-text">How can I help you today?</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Ask MedBot about first aid, health information, or your first-aid kit.</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    if c1.button("🩹 Minor cut", use_container_width=True):
        st.session_state.pending_question = "What should I do for a small cut?"
        st.rerun()
    if c2.button("🔥 Minor burn", use_container_width=True):
        st.session_state.pending_question = "What should I do for a minor burn?"
        st.rerun()
    if c3.button("🧰 First-aid kit", use_container_width=True):
        st.session_state.pending_question = "What items in my first-aid kit can help with a scrape?"
        st.rerun()
    if c4.button("🩸 Heavily-bleeding wound", use_container_width=True):
        st.session_state.pending_question = "What should I do if I have a wound that is bleeding out?"
        st.rerun()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

question = st.chat_input("Ask MedBot anything about health or first aid...")
question = question or st.session_state.pop("pending_question", None)

if question:
    st.session_state.messages.append({"role": "user", "content": question})

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                answer = generate_medbot_response(question)
            except Exception as e:
                st.error(f"Gemini Error: {e}")
                answer = "Sorry, I couldn't generate a response right now."

        st.markdown(
            f'<div class="answer">{answer}</div>',
            unsafe_allow_html=True
        )

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer
    })

st.markdown('<div class="disclaimer">MedBot can make mistakes. Information provided is educational and should not replace professional medical advice. If you think someone is experiencing an emergency, contact your local emergency service or get immediate help from a nearby responsible adult/person.</div>', unsafe_allow_html=True)
