import tkinter as tk
from tkinter import scrolledtext
from datetime import datetime
import speech_recognition as sr
import pyttsx3

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ---------------- FAQ DATA ---------------- #

faq_data = {
    "what is artificial intelligence":
        "Artificial Intelligence enables machines to perform tasks that require human intelligence.",

    "what is machine learning":
        "Machine Learning is a branch of AI that learns from data.",

    "what is deep learning":
        "Deep Learning is a subset of Machine Learning based on neural networks.",

    "what is nlp":
        "NLP stands for Natural Language Processing.",

    "what is computer vision":
        "Computer Vision helps computers understand images and videos.",

    "what is chatbot":
        "A chatbot is a software program that simulates conversation.",

    "what is tensorflow":
        "TensorFlow is an open-source machine learning framework.",

    "what is python":
        "Python is a popular programming language used in AI and Machine Learning.",

    "what is neural network":
        "A neural network is inspired by the structure of the human brain.",

    "what is generative ai":
        "Generative AI creates new content such as text, images, and music."
}

questions = list(faq_data.keys())

vectorizer = TfidfVectorizer()
question_vectors = vectorizer.fit_transform(questions)

# ---------------- TEXT TO SPEECH ---------------- #

engine = pyttsx3.init()

def speak(text):
    engine.say(text)
    engine.runAndWait()

# ---------------- CHATBOT LOGIC ---------------- #

def get_response(user_input):

    user_input = user_input.lower()

    user_vector = vectorizer.transform([user_input])

    similarity = cosine_similarity(
        user_vector,
        question_vectors
    )

    best_index = similarity.argmax()
    confidence = similarity[0][best_index]

    if confidence > 0.25:

        answer = faq_data[questions[best_index]]

        return (
            answer,
            round(confidence * 100, 2)
        )

    return (
        "Sorry, I could not find a matching answer.",
        0
    )

# ---------------- SAVE HISTORY ---------------- #

def save_history(text):
    with open("chat_history.txt", "a", encoding="utf-8") as file:
        file.write(text + "\n")

# ---------------- SEND MESSAGE ---------------- #

def send_message():

    user_text = user_entry.get().strip()

    if not user_text:
        return

    timestamp = datetime.now().strftime("%H:%M:%S")

    chat_area.config(state=tk.NORMAL)

    chat_area.insert(
        tk.END,
        f"\n[{timestamp}] You: {user_text}\n"
    )

    answer, confidence = get_response(user_text)

    chat_area.insert(
        tk.END,
        f"[{timestamp}] Bot: {answer}\n"
    )

    chat_area.insert(
        tk.END,
        f"Confidence: {confidence}%\n"
    )

    chat_area.config(state=tk.DISABLED)
    chat_area.see(tk.END)

    save_history(
        f"[{timestamp}] You: {user_text}\n"
        f"[{timestamp}] Bot: {answer}\n"
    )

    speak(answer)

    user_entry.delete(0, tk.END)

# ---------------- VOICE INPUT ---------------- #

def voice_input():

    recognizer = sr.Recognizer()

    try:
        with sr.Microphone() as source:

            chat_area.config(state=tk.NORMAL)
            chat_area.insert(
                tk.END,
                "\n🎤 Listening...\n"
            )
            chat_area.config(state=tk.DISABLED)

            root.update()

            audio = recognizer.listen(
                source,
                timeout=5
            )

        text = recognizer.recognize_google(audio)

        user_entry.delete(0, tk.END)
        user_entry.insert(0, text)

        send_message()

    except Exception as e:

        chat_area.config(state=tk.NORMAL)
        chat_area.insert(
            tk.END,
            f"\nVoice Error: {e}\n"
        )
        chat_area.config(state=tk.DISABLED)

# ---------------- CLEAR CHAT ---------------- #

def clear_chat():

    chat_area.config(state=tk.NORMAL)
    chat_area.delete(1.0, tk.END)
    chat_area.config(state=tk.DISABLED)

# ---------------- GUI ---------------- #

root = tk.Tk()

root.title("Voice Enabled AI FAQ Chatbot")
root.geometry("850x650")
root.configure(bg="#1e1e1e")

title = tk.Label(
    root,
    text="🤖 Voice AI FAQ Chatbot",
    font=("Arial", 18, "bold"),
    bg="#1e1e1e",
    fg="white"
)

title.pack(pady=10)

chat_area = scrolledtext.ScrolledText(
    root,
    wrap=tk.WORD,
    font=("Arial", 11),
    bg="#2b2b2b",
    fg="white"
)

chat_area.pack(
    padx=10,
    pady=10,
    fill=tk.BOTH,
    expand=True
)

chat_area.config(state=tk.DISABLED)

welcome = """
Welcome to Voice AI FAQ Chatbot!

Try:
- What is AI?
- What is NLP?
- What is Machine Learning?
- What is TensorFlow?

Use the microphone button to speak.
"""

chat_area.config(state=tk.NORMAL)
chat_area.insert(tk.END, welcome)
chat_area.config(state=tk.DISABLED)

entry_frame = tk.Frame(
    root,
    bg="#1e1e1e"
)

entry_frame.pack(
    fill=tk.X,
    padx=10,
    pady=10
)

user_entry = tk.Entry(
    entry_frame,
    font=("Arial", 12)
)

user_entry.pack(
    side=tk.LEFT,
    fill=tk.X,
    expand=True,
    padx=(0, 10)
)

send_btn = tk.Button(
    entry_frame,
    text="Send",
    command=send_message
)

send_btn.pack(side=tk.LEFT)

voice_btn = tk.Button(
    entry_frame,
    text="🎤 Voice",
    command=voice_input
)

voice_btn.pack(side=tk.LEFT, padx=5)

clear_btn = tk.Button(
    root,
    text="Clear Chat",
    command=clear_chat
)

clear_btn.pack(pady=5)

user_entry.bind(
    "<Return>",
    lambda event: send_message()
)

root.mainloop()