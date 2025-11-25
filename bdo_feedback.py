import streamlit as st
import pandas as pd
from datetime import datetime
import os
from transformers import pipeline
import requests
import json

# -----------------------------
# Load sentiment analysis pipeline
# -----------------------------
@st.cache_resource
def load_sentiment_model():
    return pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment-latest")

sentiment_pipeline = load_sentiment_model()


def predict_sentiment(text: str) -> str:
    if not text or text.strip() == "":
        return "Neutral"
    max_length = 512
    truncated_text = text[:max_length]
    result = sentiment_pipeline(truncated_text)[0]
    label = result['label'].lower()
    if label == 'positive':
        return "Positive"
    elif label == 'negative':
        return "Negative"
    else:
        return "Neutral"

# -----------------------------
# Streamlit UI
# -----------------------------
st.title("🧭 Team Morale & Feedback Survey")
st.markdown("Please answer the following questions honestly to help improve our team.")

with st.form("team_survey_form", clear_on_submit=True):
    q1 = st.selectbox(
        "1. How would you describe the overall morale and positivity within our team?",
        ["Excellent", "Good", "Fair", "Needs improvement"]
    )

    q2 = st.selectbox(
        "2. How clear are your current goals and priorities for ongoing projects?",
        ["Very clear", "Somewhat clear", "Neutral", "Not very clear", "Not clear at all"]
    )

    q3 = st.selectbox(
        "3. How supported do you feel by the team when facing challenges?",
        ["Always supported", "Usually supported", "Sometimes supported", "Rarely supported"]
    )

    q4 = st.selectbox(
        "4. How effectively does our team share information and keep everyone informed?",
        ["Very effectively", "Effectively", "Somewhat effectively", "Ineffectively"]
    )

    q5 = st.selectbox(
        "5. How would you rate our team’s workload and time management?",
        ["Very manageable", "Manageable", "Occasionally overwhelming", "Often overwhelming"]
    )

    q6 = st.selectbox(
        "6. How well do you think we handle feedback and continuous improvement?",
        ["Very well", "Well", "Needs improvement", "Poorly"]
    )

    q7 = st.selectbox(
        "7. How satisfied are you with opportunities for professional growth and skill development?",
        ["Very satisfied", "Satisfied", "Neutral", "Dissatisfied"]
    )

    q8 = st.selectbox(
        "8. How confident are you in the direction our projects are heading over the next few months?",
        ["Very confident", "Somewhat confident", "Neutral", "Not confident"]
    )

    q9 = st.selectbox(
        "9. How well do you think the team recognizes and celebrates achievements?",
        ["Very well", "Well", "Needs improvement", "Poorly"]
    )

    q10 = st.text_area(
        "10. 💬 What one change or improvement do you think would make the biggest positive difference for our team?"
    )

    submitted = st.form_submit_button("Submit Feedback")

# -----------------------------
# Power Automate Connection
# -----------------------------
POWER_AUTOMATE_URL = "https://default37d6c2dc481348e3a84228cab8171c.98.environment.api.powerplatform.com:443/powerautomate/automations/direct/workflows/1fc00c0d6b0e4966b81adf312d4d1c7c/triggers/manual/paths/invoke?api-version=1&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=PcXv8uwlQWGh65LNuoKpRVrDefJGZjlm50WPBSpQhic"

def send_to_online_excel(data: dict):
    headers = {"Content-Type": "application/json"}
    response = requests.post(POWER_AUTOMATE_URL, headers=headers, data=json.dumps(data))
    if response.status_code in [200, 202]:
        st.success("✅ Feedback sent successfully!")
    else:
        st.error(f"⚠️ Failed: {response.status_code}\n{response.text}")

# -----------------------------
# On Submit
# -----------------------------
if submitted:
    sentiment = predict_sentiment(q10)

    payload = {
        "Q1_Morale": q1,
        "Q2_GoalsClarity": q2,
        "Q3_Support": q3,
        "Q4_Communication": q4,
        "Q5_Workload": q5,
        "Q6_FeedbackHandling": q6,
        "Q7_Growth": q7,
        "Q8_Confidence": q8,
        "Q9_Recognition": q9,
        "Q10_OpenEnded": q10,
        "Sentiment": sentiment,
        "Timestamp": str(datetime.now())
    }

    send_to_online_excel(payload)

    st.success(f"Thank you for your response! Sentiment detected: **{sentiment}**")

