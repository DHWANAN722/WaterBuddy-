# app.py
import streamlit as st
from PIL import Image
import random
import math
import io

# -------- Page setup --------
st.set_page_config(
    page_title="💧 WaterBuddy Deluxe",
    page_icon="🐢💦",
    layout="centered",
    initial_sidebar_state="expanded"
)

# -------- Helper assets (external images are used for mascots) --------
# If any image fails to load the app still works.
MASCO_T_GIF_HAPPY = "https://i.imgur.com/Vq6v2dI.gif"   # playful turtle celebrating
MASCO_T_GIF_SIP = "https://i.imgur.com/8KX6y2Q.gif"     # sipping turtle
MASCO_T_GIF_SLEEP = "https://i.imgur.com/9Y6bIhD.gif"   # sleepy turtle
MASCO_T_PNG = "https://i.imgur.com/MR2M4YJ.png"         # fallback static buddy

# Playful color blocks and header using HTML (Streamlit allows limited HTML)
banner_html = """
<div style="background: linear-gradient(90deg,#7ee8fa 0%, #80ff72 100%);
            padding: 18px; border-radius: 12px; text-align:center;">
  <h1 style="font-family: 'Comic Sans MS', 'Chalkboard', 'Segoe UI', sans-serif; color:#05386B;">
    💧 WaterBuddy Deluxe — Aqua the Goofy Turtle 🐢
  </h1>
  <p style="font-size:14px; color:#045A8D; margin-top:-12px;">
    Colourful, animated, and silly — let’s sip our way to a healthy day!
  </p>
</div>
"""
st.markdown(banner_html, unsafe_allow_html=True)

# -------- Initialize app state --------
if "intake" not in st.session_state:
    st.session_state.intake = 0
if "goal" not in st.session_state:
    st.session_state.goal = 2000
if "logs" not in st.session_state:
    st.session_state.logs = []  # store (amount, note)
if "mascot" not in st.session_state:
    st.session_state.mascot = MASCO_T_PNG

# -------- Age group and goal logic --------
st.write("")  # spacing
age_col, goal_col = st.columns([2, 3])

with age_col:
    age_group = st.selectbox(
        "Choose your age group 👶👧🧑🧓",
        ["6-12 years", "13-18 years", "19-50 years", "65+ years"]
    )

age_goals = {
    "6-12 years": 1600,
    "13-18 years": 2000,
    "19-50 years": 2500,
    "65+ years": 2000
}

with goal_col:
    suggested = age_goals[age_group]
    # allow user to adjust, but default shows suggested
    st.session_state.goal = st.number_input(
        "Daily goal (ml) — change if you like:",
        min_value=500, max_value=6000, value=suggested, step=100
    )

# -------- Quick logging area --------
st.markdown("### Quick log — one click sips 🥤")
c1, c2, c3, c4, c5 = st.columns(5)

if c1.button("+100 ml"):
    st.session_state.intake += 100
    st.session_state.logs.append((100, "Quick 100 ml"))
    st.session_state.mascot = MASCO_T_GIF_SIP

if c2.button("+200 ml"):
    st.session_state.intake += 200
    st.session_state.logs.append((200, "Quick 200 ml"))
    st.session_state.mascot = MASCO_T_GIF_SIP

if c3.button("+250 ml"):
    st.session_state.intake += 250
    st.session_state.logs.append((250, "Quick 250 ml"))
    st.session_state.mascot = MASCO_T_GIF_SIP

if c4.button("+500 ml"):
    st.session_state.intake += 500
    st.session_state.logs.append((500, "Big 500 ml"))
    st.session_state.mascot = MASCO_T_GIF_SIP

if c5.button("+Custom"):
    # show input in a modal-like area below
    st.session_state.mascot = MASCO_T_PNG
    with st.form("custom_log_form", clear_on_submit=True):
        amt = st.number_input("Custom amount (ml):", min_value=10, max_value=5000, value=250, step=10)
        note = st.text_input("Optional note (e.g., 'after sport'):")
        submitted = st.form_submit_button("Log custom amount")
        if submitted:
            st.session_state.intake += int(amt)
            st.session_state.logs.append((int(amt), note or "Custom"))
            st.session_state.mascot = MASCO_T_GIF_SIP

# -------- Manual log and reset --------
st.markdown("---")
st.markdown("### Manual log & controls")
mcol1, mcol2, mcol3 = st.columns([2,2,2])

with mcol1:
    add_amt = st.number_input("Add amount (ml):", min_value=0, max_value=5000, value=0, step=50)
    if st.button("Add this amount"):
        if add_amt > 0:
            st.session_state.intake += int(add_amt)
            st.session_state.logs.append((int(add_amt), "Manual add"))
            st.session_state.mascot = MASCO_T_GIF_SIP

with mcol2:
    if st.button("Reset for new day 🔁"):
        st.session_state.intake = 0
        st.session_state.logs = []
        st.session_state.mascot = MASCO_T_GIF_SLEEP
        st.success("Reset successful — fresh day!")

with mcol3:
    if st.button("Cheer me 🎉"):
        # small celebratory action when user is happy
        st.balloons()
        st.session_state.mascot = MASCO_T_GIF_HAPPY

# -------- Calculations (exact) --------
total = st.session_state.intake
goal = st.session_state.goal
# protect against zero division
pct = 0.0
if goal > 0:
    pct = total / float(goal)
pct_clamped = min(max(pct, 0.0), 1.0)
remaining = max(goal - total, 0)

# show progress bar with a colourful badge
st.markdown("### Progress Tracker")
progress_col, mascot_col = st.columns([3,2])

with progress_col:
    # colourful progress using emoji blocks
    prog_percent = math.floor(pct_clamped * 100)
    st.metric(label="Goal completion", value=f"{prog_percent}%")
    st.progress(pct_clamped)

    st.markdown(
        f"**Total:** {total} ml  —  **Goal:** {goal} ml  —  **Remaining:** {remaining} ml"
    )

    # milestone messages with personality
    if total == 0:
        st.info("🌊 Aqua says: Take the first sip — it's the hardest but the best!")
        st.session_state.mascot = MASCO_T_PNG
    elif pct_clamped < 0.25:
        st.warning("Nice start! Keep going — make sipping a little habit ☺️")
    elif pct_clamped < 0.5:
        st.success("Great! You're nearing 50% — Aqua is proud 🐢")
        st.session_state.mascot = MASCO_T_GIF_SIP
    elif pct_clamped < 0.9:
        st.success("Awesome — you're above halfway! Keep the momentum 🔥")
    elif pct_clamped < 1.0:
        st.info("So close! One more push to hit the goal 💪")
    else:
        # reached or overshot goal
        st.success("🎉 Goal met! Time for a happy turtle dance 🐢💃")
        st.balloons()
        st.session_state.mascot = MASCO_T_GIF_HAPPY

with mascot_col:
    try:
        st.image(st.session_state.mascot, caption="Aqua — your goofy hydration buddy", use_column_width=True)
    except Exception:
        st.image(MASCO_T_PNG, caption="Aqua (fallback)", use_column_width=True)

# -------- Logs & small analytics --------
st.markdown("---")
st.markdown("### Water Log (latest first)")
if st.session_state.logs:
    # show reverse (latest first)
    for i, entry in enumerate(reversed(st.session_state.logs[-20:])):
        amt, note = entry
        st.write(f"- {amt} ml — {note}")
else:
    st.write("_No logs yet. Use the buttons above to start!_")

# show a small pie-like textual comparison
st.markdown("#### Quick compare")
std_target = age_goals[age_group]
diff = total - std_target
if diff >= 0:
    st.write(f"You're **{abs(diff)} ml above** the standard for {age_group}. Nice!")
else:
    st.write(f"You're **{abs(diff)} ml below** the standard for {age_group}. Almost there!")

# -------- Sidebar goodies --------
st.sidebar.markdown("## 💡 WaterBuddy Sidebar")
st.sidebar.markdown("**Mood selector** — pick one and see Aqua react.")
mood = st.sidebar.selectbox("Choose a mood:", ["Auto (reactive)", "Happy", "Sipping", "Sleepy"])
if mood == "Happy":
    st.session_state.mascot = MASCO_T_GIF_HAPPY
elif mood == "Sipping":
    st.session_state.mascot = MASCO_T_GIF_SIP
elif mood == "Sleepy":
    st.session_state.mascot = MASCO_T_GIF_SLEEP
# else auto -> keep current

st.sidebar.markdown("---")
st.sidebar.markdown("### 🎯 Tools")
# unit converter
st.sidebar.write("**Units converter**")
cups = st.sidebar.number_input("Cups (approx, 1 cup = 250 ml):", min_value=0.0, max_value=20.0, value=0.0, step=0.25)
if cups > 0:
    st.sidebar.write(f"{cups} cups ≈ {int(cups * 250)} ml")

st.sidebar.markdown("---")
st.sidebar.write("### 🌊 Daily Tip")
tips = [
    "After waking up: drink a glass to kickstart your body!",
    "Carry a bottle — sight = sip.",
    "Add fruits (lemon, berries) to make water tasty.",
    "Set a gentle reminder every 1-2 hours."
]
st.sidebar.info(random.choice(tips))

# -------- Footer + tiny instructions for user --------
st.markdown("---")
st.markdown(
    "<div style='text-align:center; font-size:12px; color:#555;'>"
    "Made with 💧 by WaterBuddy. Tip: Use the +250 ml button to log fast. "
    "If an image doesn't load, try again — the app still works without it."
    "</div>",
    unsafe_allow_html=True
)
