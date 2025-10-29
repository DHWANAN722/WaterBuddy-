# app.py  — WaterBuddy (Goofy Comic Edition)
import streamlit as st
import random
import math
import pandas as pd
from PIL import Image
import requests
from io import BytesIO
import base64

# ---------------- Page setup ----------------
st.set_page_config(page_title="WaterBuddy", page_icon="🐢", layout="centered", initial_sidebar_state="expanded")

# ---------------- CSS: comic fonts + pastel gradient background + styles ----------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Luckiest+Guy&family=Patrick+Hand&display=swap');

    /* Pastel multicolor background */
    .stApp {
      background: linear-gradient(135deg, #FFDEE9 0%, #B5FFFC 25%, #E6FFDA 50%, #FDE6FF 75%, #FFF6BD 100%);
      background-attachment: fixed;
      font-family: 'Patrick Hand', 'Comic Sans MS', sans-serif;
    }

    /* Header styles */
    .comic-title {
      font-family: 'Luckiest Guy', 'Comic Sans MS', cursive;
      font-size: 48px;
      color: #063e78;
      text-align: center;
      text-shadow: 3px 3px 0 #ffd166;
      margin-bottom: 6px;
    }
    .comic-sub {
      font-family: 'Patrick Hand', sans-serif;
      font-size: 16px;
      color: #073b4c;
      text-align:center;
      margin-bottom: 14px;
    }

    /* Cards */
    .card {
      background: linear-gradient(180deg, rgba(255,255,255,0.95), rgba(255,255,255,0.85));
      border-radius: 16px;
      padding: 14px;
      box-shadow: 0 8px 30px rgba(0,0,0,0.10);
      border: 4px dashed rgba(255,209,102,0.9);
    }

    /* Mascot floaty animation */
    .mascot {
      display:block;
      margin-left:auto;
      margin-right:auto;
      width: 260px;
      border-radius: 12px;
      box-shadow: 0 10px 30px rgba(0,0,0,0.18);
      transform-origin: 50% 50%;
      animation: floaty 3.5s ease-in-out infinite;
    }
    @keyframes floaty {
      0% { transform: translateY(0px) rotate(-3deg); }
      50% { transform: translateY(-12px) rotate(3deg); }
      100% { transform: translateY(0px) rotate(-3deg); }
    }

    /* Big playful buttons */
    .stButton>button {
      font-family: 'Luckiest Guy', cursive;
      font-size:16px;
      padding:10px 16px;
      border-radius:12px;
    }

    /* Progress bar color */
    .stProgress > div > div > div > div {
      background: linear-gradient(90deg,#ff9a9e,#fecfef,#fef9a7) !important;
    }

    .log-item {
      background: rgba(255,255,255,0.9);
      border-radius: 10px;
      padding: 8px;
      margin-bottom:6px;
      border: 2px dotted #ffd166;
    }

    .muted { color:#444; font-size:13px; }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------------- Mascot image URLs (external) ----------------
M_HAPPY = "https://i.imgur.com/Vq6v2dI.gif"   # dancing
M_SIP = "https://i.imgur.com/8KX6y2Q.gif"     # sipping
M_SLEEP = "https://i.imgur.com/9Y6bIhD.gif"   # sleepy
M_STATIC = "https://i.imgur.com/MR2M4YJ.png"  # fallback static

# ---------------- Initialize session state ----------------
if "intake" not in st.session_state:
    st.session_state.intake = 0
if "goal" not in st.session_state:
    st.session_state.goal = 2000
if "logs" not in st.session_state:
    st.session_state.logs = []  # list of (amount, note)
if "mascot" not in st.session_state:
    st.session_state.mascot = M_STATIC
if "name" not in st.session_state:
    st.session_state.name = "Buddy"

# ---------------- Header ----------------
st.markdown(f"<div class='comic-title'>💧 WaterBuddy</div>", unsafe_allow_html=True)
st.markdown("<div class='comic-sub'>Big fonts. Big vibes. Tiny sips. Let’s be goofy and hydrated!</div>", unsafe_allow_html=True)

# ---------------- Top layout ----------------
left, right = st.columns([2,1])

with left:
    st.markdown("<div class='card'>", unsafe_allow_html=True)

    # Name and greeting
    name = st.text_input("What's your name?", value=st.session_state.name)
    st.session_state.name = name
    st.markdown(f"<div style='font-family:Patrick Hand; font-size:15px;'>Hi <b>{name}</b>! Aqua the turtle is ready to cheer you on 🐢</div>", unsafe_allow_html=True)

    # Age group + suggested goal
    age_group = st.selectbox("Pick your age group:", ["6-12 years", "13-18 years", "19-50 years", "65+ years"])
    age_defaults = {"6-12 years":1600, "13-18 years":2000, "19-50 years":2500, "65+ years":2000}
    st.session_state.goal = st.number_input("Daily goal (ml):", min_value=500, max_value=6000, value=age_defaults[age_group], step=100)

    st.markdown("<hr>", unsafe_allow_html=True)

    # Quick log buttons (goofy)
    st.markdown("<div style='font-family:Luckiest Guy; font-size:20px; color:#073b4c;'>Quick Sips 🥤</div>", unsafe_allow_html=True)
    b1, b2, b3, b4 = st.columns(4)
    if b1.button("+100 ml"):
        st.session_state.intake += 100
        st.session_state.logs.append((100, "Tiny sip"))
        st.session_state.mascot = M_SIP
    if b2.button("+250 ml"):
        st.session_state.intake += 250
        st.session_state.logs.append((250, "Little gulp"))
        st.session_state.mascot = M_SIP
    if b3.button("+500 ml"):
        st.session_state.intake += 500
        st.session_state.logs.append((500, "Big chug"))
        st.session_state.mascot = M_SIP
    if b4.button("+Custom"):
        with st.form("custom_form", clear_on_submit=True):
            c_amt = st.number_input("Custom ml:", min_value=10, max_value=5000, value=250, step=10)
            c_note = st.text_input("Note (optional):", value="")
            c_submit = st.form_submit_button("Log custom")
            if c_submit:
                st.session_state.intake += int(c_amt)
                st.session_state.logs.append((int(c_amt), c_note or "Custom"))
                st.session_state.mascot = M_SIP

    st.markdown("<hr>", unsafe_allow_html=True)

    # Manual add + reset + cheer
    st.markdown("<div style='font-weight:bold;'>Manual Controls</div>", unsafe_allow_html=True)
    mcol1, mcol2, mcol3 = st.columns([2,1,1])
    with mcol1:
        add_amt = st.number_input("Add amount (ml):", min_value=0, max_value=5000, value=0, step=10)
        if st.button("Add this amount"):
            if add_amt > 0:
                st.session_state.intake += int(add_amt)
                st.session_state.logs.append((int(add_amt), "Manual add"))
                st.session_state.mascot = M_SIP
    with mcol2:
        if st.button("Reset Day 🔁"):
            st.session_state.intake = 0
            st.session_state.logs = []
            st.session_state.mascot = M_SLEEP
            st.success("Reset! Fresh new day 🎉")
    with mcol3:
        if st.button("Cheer me 🎉"):
            st.balloons()
            st.session_state.mascot = M_HAPPY

    st.markdown("<hr>", unsafe_allow_html=True)

    # Silly pledge + checkboxes for extras
    pledge = st.checkbox("I promise to take small sips every hour (silly pledge)")
    if pledge:
        st.markdown("<div class='muted'>Aqua: Yay! You get a virtual sticker 🏷️</div>", unsafe_allow_html=True)

    # Unit converter quick
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("**Units converter** — cups ≈ 250 ml")
    cups = st.number_input("Cups:", min_value=0.0, max_value=20.0, value=0.0, step=0.25)
    if cups > 0:
        st.markdown(f"{cups} cups ≈ {int(cups * 250)} ml")

    st.markdown("</div>", unsafe_allow_html=True)

with right:
    st.markdown("<div class='card' style='text-align:center;'>", unsafe_allow_html=True)
    # Show mascot (reactive)
    try:
        st.image(st.session_state.mascot, caption="Aqua — your goofy turtle", use_column_width=False, output_format="auto", width=260)
    except Exception:
        st.image(M_STATIC, caption="Aqua (fallback)", use_column_width=False, width=260)
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- Progress calculations (center area) ----------------
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<div class='card'>", unsafe_allow_html=True)

total = int(st.session_state.intake)
goal = int(st.session_state.goal)
pct = 0.0
if goal > 0:
    pct = total / goal
pct_clamped = max(0.0, min(pct, 1.0))
remaining = max(goal - total, 0)

# Big display
st.markdown(f"<div style='font-family:Luckiest Guy; font-size:26px; color:#073b4c; text-align:center;'>Total: {total} ml  —  Goal: {goal} ml</div>", unsafe_allow_html=True)
st.markdown("<div style='text-align:center; margin-top:6px;'>", unsafe_allow_html=True)
st.progress(pct_clamped)
st.markdown("</div>", unsafe_allow_html=True)

# Mascot reactions & milestone behavior
if total == 0:
    st.info("🌊 Aqua says: Take the first sip — it's the bravest sip!")
    st.session_state.mascot = M_STATIC
elif pct_clamped < 0.25:
    st.warning("Nice start! Keep sipping — small steps 🐢")
    st.session_state.mascot = M_SIP
elif pct_clamped < 0.5:
    st.success("Great! You're near 50% — Aqua is proud 🐢")
    st.session_state.mascot = M_SIP
elif pct_clamped < 0.9:
    st.success("Awesome — above halfway! You're doing great ✨")
    st.session_state.mascot = M_HAPPY
elif pct_clamped < 1.0:
    st.info("So close! One more push to hit the goal 💪")
    st.session_state.mascot = M_HAPPY
else:
    # reached or overshot
    st.success("🎉 Goal met! Aqua dances and confetti appears 🐢🎊")
    st.balloons()
    st.session_state.mascot = M_HAPPY

# Encourage small sip habit
st.markdown("<div style='text-align:center; margin-top:6px;'><span class='muted'>Tip: use +250 ml to log fast and build momentum.</span></div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# ---------------- Logs & Stats ----------------
st.markdown("<br>", unsafe_allow_html=True)
log_col1, log_col2 = st.columns([2,1])

with log_col1:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### 📝 Water Log (latest first)")
    if st.session_state.logs:
        for amt, note in reversed(st.session_state.logs[-30:]):
            st.markdown(f"<div class='log-item'><b>{amt} ml</b> — {note}</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='muted'>No logs yet — start with a quick sip!</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with log_col2:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### 📊 Quick Stats")
    st.metric("Today total", f"{total} ml")
    st.metric("Goal", f"{goal} ml")
    diff = total - goal
    if diff >= 0:
        st.success(f"{abs(diff)} ml above goal — wow!")
    else:
        st.info(f"{abs(diff)} ml to go — keep sipping!")
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- Sidebar: Tips, Quiz, Mood ----------------
st.sidebar.markdown("<div style='font-family:Luckiest Guy; font-size:20px; color:#063e78;'>WaterBuddy Tools</div>", unsafe_allow_html=True)
st.sidebar.markdown("---")

# Mood selector that forces mascot
mood = st.sidebar.selectbox("Mascot mood (auto reacts by default):", ["Auto (reactive)", "Happy", "Sipping", "Sleepy"])
if mood == "Happy":
    st.session_state.mascot = M_HAPPY
elif mood == "Sipping":
    st.session_state.mascot = M_SIP
elif mood == "Sleepy":
    st.session_state.mascot = M_SLEEP
# Auto leaves current behavior

st.sidebar.markdown("---")
# Random daily tip
tips = [
    "Drink a glass after waking up 🌞",
    "Keep a bottle on your desk — sight = sip 🧴",
    "Add mint or lemon to flavor it 🍋",
    "Sip slowly — small sips help absorb water better",
    "Increase water on hot or active days ☀️"
]
st.sidebar.info(random.choice(tips))

# Mini quiz
st.sidebar.markdown("### 🧠 Mini Quiz")
q = "What percent of the human adult body is water?"
ans = st.sidebar.radio(q, ["30%", "50%", "70%", "90%"])
if ans == "70%":
    st.sidebar.success("✅ Correct! About 70% of the body is water.")
elif ans:
    st.sidebar.error("❌ Not quite — it's about 70%.")

# Export logs (CSV download)
def convert_df_to_csv(df: pd.DataFrame):
    return df.to_csv(index=False).encode('utf-8')

if st.sidebar.button("Export logs as CSV"):
    if st.session_state.logs:
        df = pd.DataFrame(st.session_state.logs, columns=["Amount_ml", "Note"])
        csv = convert_df_to_csv(df)
        st.sidebar.download_button("Download CSV", data=csv, file_name="water_logs.csv", mime="text/csv")
    else:
        st.sidebar.warning("No logs to export yet!")

st.sidebar.markdown("---")
st.sidebar.markdown("<div class='muted'>Made with 💧 by WaterBuddy — goofy & helpful.</div>", unsafe_allow_html=True)
