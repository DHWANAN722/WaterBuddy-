import streamlit as st

# ---- Title ----
st.title("💧 WaterBuddy: Your Daily Hydration Companion")

# ---- Age Group ----
age_group = st.selectbox(
    "Select your age group:",
    ["6-12 years", "13-18 years", "19-50 years", "65+ years"]
)

# ---- Suggested Goal ----
if age_group == "6-12 years":
    daily_goal = 1600
elif age_group == "13-18 years":
    daily_goal = 2000
elif age_group == "19-50 years":
    daily_goal = 2500
else:
    daily_goal = 2000

# ---- Allow user to adjust goal ----
goal = st.number_input("Your daily goal (ml):", value=daily_goal, step=100)

# ---- Session state ----
if "total_intake" not in st.session_state:
    st.session_state.total_intake = 0

# ---- Add water button ----
if st.button("+250 ml"):
    st.session_state.total_intake += 250

# ---- Reset button ----
if st.button("🔄 Reset"):
    st.session_state.total_intake = 0

# ---- Calculations ----
remaining = max(goal - st.session_state.total_intake, 0)
percent = int((st.session_state.total_intake / goal) * 100)

# ---- Progress ----
st.progress(min(percent, 100))
st.write(f"💧 Total intake: {st.session_state.total_intake} ml")
st.write(f"🎯 Goal: {goal} ml")
st.write(f"🩵 Remaining: {remaining} ml")

# ---- Motivational messages ----
if percent == 0:
    st.info("Let's start hydrating! 🥤")
elif percent < 50:
    st.info("Good start! Keep sipping 💦")
elif percent < 100:
    st.success("Almost there! Great work 🌊")
else:
    st.balloons()
    st.success("You reached your goal! 💧 Stay healthy!")
