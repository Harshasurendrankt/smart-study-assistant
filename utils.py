from huggingface_hub import InferenceClient
import streamlit as st

# Initialize Hugging Face client
client = InferenceClient(
    model="meta-llama/Meta-Llama-3-8B-Instruct",
    token=st.secrets["HF_TOKEN"]
)

def get_study_response(user_question, subject, difficulty="Beginner", response_style="Normal"):
    """
    Generate study response based on level and response style.
    Bullet Points style is forced to start with '-' for proper formatting.
    """

    style_instruction = {
        "Normal": "Explain clearly with simple examples.",
        "Short Answer": "Give a short answer in 3 to 4 lines.",
        "Bullet Points": "Answer strictly in bullet points, start each line with '-' and separate each point with a new line. Example:\n- First point\n- Second point\n- Third point",
        "Exam Mode": "Give exam-ready points. Be concise. No extra explanation."
    }

    messages = [
        {
            "role": "system",
            "content": f"""
You are an AI StudyMate.

Level: {difficulty}
Response Style: {response_style}

Instructions:
{style_instruction[response_style]}
"""
        },
        {
            "role": "user",
            "content": f"Subject: {subject}\nQuestion: {user_question}"
        }
    ]

    response = client.chat.completions.create(
        messages=messages,
        max_tokens=250,
        temperature=0.6,
        top_p=0.9
    )

    return response.choices[0].message.content.strip()


def get_mcqs(topic, difficulty="Beginner"):
    """
    Generate 5 multiple choice questions (MCQs) for the given topic.
    """
    messages = [
        {
            "role": "system",
            "content": "You are an exam question generator."
        },
        {
            "role": "user",
            "content": f"""
Generate 5 multiple choice questions on the topic below.

Level: {difficulty}

Format strictly like this:
Q1. Question?
A. option
B. option
C. option
D. option
Answer: A

Topic:
{topic}
"""
        }
    ]

    response = client.chat.completions.create(
        messages=messages,
        max_tokens=400,
        temperature=0.7,
        top_p=0.9
    )

    return response.choices[0].message.content.strip()
