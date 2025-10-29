import streamlit as st
from PIL import Image
import random
import pandas as pd

# ---------------- PAGE SETUP ----------------
st.set_page_config(page_title="💧 WaterBuddy", page_icon="🐢", layout="wide")

# --------------- CSS MAGIC (for custom wave bar & colors) ---------------
page_bg = """
<style>
body {
    background: linear-gradient(120deg, #b2fefa, #0ed2f7);
    font-family: 'Comic Sans MS', 'Poppins', sans-serif;
}
h1, h2, h3 {
    color: #034078;
}
.block-container {
    padding-top: 1.5rem;
}
.wave {
  height: 22px;
  width: 100%;
  background: linear-gradient(to right, #00c6fb 0%, #005bea 100%);
  border-radius: 10px;
  position: relative;
  overflow: hidden;
}
.wave::after {
  content: "";
  position: absolute;
  top: 0;
  left: -50%;
  width: 200%;
  height: 100%;
  background: rgba(255, 255, 255, 0.4);
  animation: waveAnimation 2s linear infinite;
}
@keyframes waveAnimation {
  0% { left: -50%; }
  100% { left: 0%; }
}
</style>
"""
st.markdown(page_bg, unsafe_allow_html=True)

# --------------- APP STATE ---------------
if "intake" not in st.session_state:
    st.session_state.intake = 0
if "goal" not in st.session_state:
    st.session_state.goal = 2000
if "logs" not in st.session_state:
    st.session_state.logs = []

# --------------- HEADER ---------------
st.markdown("""
<h1 style='text-align:center;'>💧 WaterBuddy Ultra+ 🐢</h1>
<h3 style='text-align:center; color:#045a8d;'>Your colourful daily hydration companion</h3>
""", unsafe_allow_html=True)

st.divider()

# Sidebar Navigation
menu = st.sidebar.radio("📘 Menu", ["Tracker", "Tips & Fun", "Stats"])

# Mascot mood images
mascots = {
    "default": "https://i.imgur.com/MR2M4YJ.png",
    "sipping": "https://i.imgur.com/8KX6y2Q.gif",
    "happy": "https://i.imgur.com/Vq6v2dI.gif",
    "sleepy": "https://i.imgur.com/9Y6bIhD.gif",
}

# --------------- TRACKER PAGE ---------------
if menu == "Tracker":
    st.subheader("🌊 Daily Tracker")

    col1, col2 = st.columns([2, 1])

    with col1:
        name = st.text_input("Enter your name:", value="Dhwanan")
        st.write(f"👋 Hey {name}, let's stay hydrated today!")

        age_group = st.selectbox("Select Age Group:", ["6–12", "13–18", "19–50", "65+"])
        goal_values = {"6–12": 1600, "13–18": 2000, "19–50": 2500, "65+": 2000}
        st.session_state.goal = st.number_input(
            "Your daily goal (ml):", min_value=1000, max_value=4000,
            value=goal_values[age_group], step=100
        )

        st.write("#### Log Your Water Intake 💧")
        colA, colB, colC = st.columns(3)
        if colA.button("+250 ml"):
            st.session_state.intake += 250
            st.session_state.logs.append(("250 ml", "Quick log"))
        if colB.button("+500 ml"):
            st.session_state.intake += 500
            st.session_state.logs.append(("500 ml", "Big sip"))
        if colC.button("Reset Day 🔁"):
            st.session_state.intake = 0
            st.session_state.logs.clear()

        custom = st.slider("Add custom amount (ml)", 50, 1000, 250, 50)
        if st.button("Add custom amount"):
            st.session_state.intake += custom
            st.session_state.logs.append((f"{custom} ml", "Custom log"))

        # Progress section
        progress = st.session_state.intake / st.session_state.goal
        progress = min(progress, 1.0)
        remaining = st.session_state.goal - st.session_state.intake

        st.write("#### 🧮 Progress Summary")
        st.metric("Total Intake", f"{st.session_state.intake} ml")
        st.metric("Goal", f"{st.session_state.goal} ml")
        st.metric("Remaining", f"{remaining if remaining>0 else 0} ml")

        # Wave bar
        st.markdown('<div class="wave"></div>', unsafe_allow_html=True)
        st.progress(progress)

        # Messages
        if progress == 0:
            msg = "Time for your first sip! 💦"
            mood = mascots["default"]
        elif progress < 0.5:
            msg = "Good job! You’re halfway there 😎"
            mood = mascots["sipping"]
        elif progress < 1:
            msg = "Almost done! A few more sips 💧"
            mood = mascots["happy"]
        else:
            msg = "🎉 You did it! Aqua is dancing in joy 🐢"
            mood = mascots["happy"]

        st.success(msg)

    with col2:
        st.image(mood, caption="Aqua the Turtle", use_column_width=True)

# --------------- TIPS PAGE ---------------
elif menu == "Tips & Fun":
    st.subheader("🎯 Hydration Tips & Mini Quiz")

    tips = [
        "Drink water right after waking up 🌞",
        "Keep a bottle on your desk 🧴",
        "Add fruits like lemon or mint 🍋",
        "Small sips > big gulps 🚰",
        "Drink more when it's hot ☀️",
    ]
    st.info(random.choice(tips))

    st.markdown("### 🧠 Quick Quiz!")
    question = "What percent of the human body is water?"
    answer = st.radio(question, ["30%", "50%", "70%", "90%"])
    if answer == "70%":
        st.success("✅ Correct! About 70% of your body is water.")
    else:
        st.error("❌ Oops! It’s about 70%. Stay hydrated!")

    st.markdown("### 🐢 Fun Fact:")
    facts = [
        "Drinking enough water improves memory and focus 🧠",
        "Even mild dehydration can cause fatigue 😴",
        "Water helps regulate body temperature 🌡️",
        "Hydrated skin = healthy glow ✨"
    ]
    st.write(random.choice(facts))

# --------------- STATS PAGE ---------------
elif menu == "Stats":
    st.subheader("📊 Your Hydration Stats")

    if not st.session_state.logs:
        st.info("No logs yet — start tracking in the Tracker tab!")
    else:
        data = pd.DataFrame(st.session_state.logs, columns=["Amount", "Type"])
        st.dataframe(data[::-1], use_container_width=True)

        total = st.session_state.intake
        goal = st.session_state.goal
        diff = total - goal
        if diff >= 0:
            st.success(f"You're {diff} ml above your goal! Excellent 🌟")
        else:
            st.warning(f"You're {abs(diff)} ml below your goal — drink up!")

    st.markdown("---")
    st.markdown("<p style='text-align:center;'>💧 Keep sipping — small sips make big wins!</p>", unsafe_allow_html=True)
