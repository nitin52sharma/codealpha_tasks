import os
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import numpy as np
import soundfile as sf
import torch
from transformers import AutoProcessor, MusicgenForConditionalGeneration


# ============================================================
# AI MUSIC GENERATOR - CODEALPHA INTERNSHIP TASK 3
# ============================================================

MODEL_NAME = "facebook/musicgen-small"

model = None
processor = None


# ------------------------- COLORS ----------------------------

BG = "#0b1020"
CARD = "#151c32"
CARD_2 = "#1c2540"
TEXT = "#f5f7ff"
MUTED = "#9da8c7"
ACCENT = "#7c5cff"
ACCENT_HOVER = "#6948ee"
SUCCESS = "#45d483"
ERROR = "#ff647c"


# --------------------- LOAD AI MODEL -------------------------

def load_model():
    global model, processor

    status_label.config(
        text="⏳ Loading AI Music Model...",
        foreground=ACCENT
    )
    generate_button.config(state="disabled")

    try:
        processor = AutoProcessor.from_pretrained(MODEL_NAME)

        model = MusicgenForConditionalGeneration.from_pretrained(
            MODEL_NAME
        )

        status_label.config(
            text="✓ AI Model Ready",
            foreground=SUCCESS
        )
        generate_button.config(state="normal")

    except Exception as e:
        status_label.config(
            text="✕ Model loading failed",
            foreground=ERROR
        )
        generate_button.config(state="disabled")

        messagebox.showerror(
            "Model Error",
            "Could not load the AI music model.\n\n"
            f"Error:\n{str(e)}"
        )


# ---------------------- GENERATE MUSIC -----------------------

def generate_music():
    prompt = prompt_entry.get("1.0", tk.END).strip()

    if not prompt:
        messagebox.showwarning(
            "Missing Prompt",
            "Please enter a music description first."
        )
        return

    if model is None or processor is None:
        messagebox.showwarning(
            "AI Model Not Ready",
            "Please wait until the AI model is ready."
        )
        return

    try:
        duration = int(duration_var.get())

        generate_button.config(state="disabled")
        status_label.config(
            text="🎵 AI is generating your music...",
            foreground=ACCENT
        )

        progress.start(10)

        thread = threading.Thread(
            target=create_music,
            args=(prompt, duration),
            daemon=True
        )
        thread.start()

    except Exception as e:
        progress.stop()
        generate_button.config(state="normal")

        messagebox.showerror(
            "Generation Error",
            str(e)
        )


def create_music(prompt, duration):
    try:
        # Keep generation within a reasonable size.
        max_new_tokens = max(128, min(duration * 50, 512))

        inputs = processor(
            text=[prompt],
            padding=True,
            return_tensors="pt"
        )

        with torch.no_grad():
            audio_values = model.generate(
                **inputs,
                max_new_tokens=max_new_tokens
            )

        audio = audio_values[0, 0].cpu().numpy()

        sample_rate = model.config.audio_encoder.sampling_rate

        # Normalize audio safely.
        peak = np.max(np.abs(audio))

        if peak > 0:
            audio = audio / peak

        default_name = "ai_generated_music.wav"

        save_path = filedialog.asksaveasfilename(
            title="Save AI Generated Music",
            defaultextension=".wav",
            initialfile=default_name,
            filetypes=[
                ("WAV Audio", "*.wav"),
                ("All Files", "*.*")
            ]
        )

        if save_path:
            sf.write(
                save_path,
                audio,
                sample_rate
            )

            root.after(
                0,
                generation_success,
                save_path
            )
        else:
            root.after(
                0,
                generation_cancelled
            )

    except Exception as e:
        root.after(
            0,
            generation_failed,
            str(e)
        )


# ---------------------- UI CALLBACKS -------------------------

def generation_success(path):
    progress.stop()
    generate_button.config(state="normal")

    status_label.config(
        text="✓ Music generated successfully!",
        foreground=SUCCESS
    )

    messagebox.showinfo(
        "Success 🎵",
        "Your AI-generated music has been saved successfully!\n\n"
        f"File:\n{os.path.basename(path)}"
    )


def generation_cancelled():
    progress.stop()
    generate_button.config(state="normal")

    status_label.config(
        text="Generation completed. File was not saved.",
        foreground=MUTED
    )


def generation_failed(error):
    progress.stop()
    generate_button.config(state="normal")

    status_label.config(
        text="✕ Music generation failed",
        foreground=ERROR
    )

    messagebox.showerror(
        "Generation Error",
        f"Something went wrong:\n\n{error}"
    )


def clear_prompt():
    prompt_entry.delete("1.0", tk.END)

    prompt_entry.insert(
        "1.0",
        "Example: Calm cinematic piano music with a peaceful "
        "and emotional atmosphere"
    )


def use_example():
    examples = [
        "Peaceful piano melody with a relaxing cinematic atmosphere",
        "Energetic electronic music with a futuristic sci-fi feeling",
        "Emotional instrumental music with soft piano and strings",
        "Happy acoustic music with a bright and uplifting mood",
        "Dark cinematic background music for a mystery scene"
    ]

    import random

    prompt_entry.delete("1.0", tk.END)
    prompt_entry.insert(
        "1.0",
        random.choice(examples)
    )


# ============================================================
# MAIN WINDOW
# ============================================================

root = tk.Tk()

root.title("AI Music Generator | CodeAlpha Task 3")
root.geometry("850x650")
root.minsize(750, 580)
root.configure(bg=BG)


# ------------------------ HEADER -----------------------------

header = tk.Frame(
    root,
    bg=BG
)
header.pack(
    fill="x",
    padx=45,
    pady=(35, 10)
)

title = tk.Label(
    header,
    text="🎵 AI MUSIC GENERATOR",
    font=("Segoe UI", 26, "bold"),
    bg=BG,
    fg=TEXT
)
title.pack(anchor="w")

subtitle = tk.Label(
    header,
    text="Create original music using an AI-powered MusicGen model",
    font=("Segoe UI", 11),
    bg=BG,
    fg=MUTED
)
subtitle.pack(
    anchor="w",
    pady=(5, 0)
)


# ------------------------- CARD ------------------------------

card = tk.Frame(
    root,
    bg=CARD
)
card.pack(
    fill="both",
    expand=True,
    padx=45,
    pady=20
)


# Prompt label
prompt_label = tk.Label(
    card,
    text="Describe your music",
    font=("Segoe UI", 13, "bold"),
    bg=CARD,
    fg=TEXT
)
prompt_label.pack(
    anchor="w",
    padx=30,
    pady=(30, 8)
)


# Prompt box
prompt_entry = tk.Text(
    card,
    height=5,
    wrap="word",
    font=("Segoe UI", 11),
    bg=CARD_2,
    fg=TEXT,
    insertbackground=TEXT,
    relief="flat",
    padx=15,
    pady=12
)
prompt_entry.pack(
    fill="x",
    padx=30
)

prompt_entry.insert(
    "1.0",
    "Example: Calm cinematic piano music with a peaceful "
    "and emotional atmosphere"
)


# Example button
example_button = tk.Button(
    card,
    text="✨ Try Example",
    command=use_example,
    font=("Segoe UI", 10, "bold"),
    bg=CARD_2,
    fg=TEXT,
    activebackground=ACCENT,
    activeforeground=TEXT,
    relief="flat",
    cursor="hand2",
    padx=15,
    pady=7
)
example_button.pack(
    anchor="w",
    padx=30,
    pady=10
)


# -------------------- OPTIONS FRAME --------------------------

options = tk.Frame(
    card,
    bg=CARD
)
options.pack(
    fill="x",
    padx=30,
    pady=10
)


duration_title = tk.Label(
    options,
    text="Music Length",
    font=("Segoe UI", 11, "bold"),
    bg=CARD,
    fg=TEXT
)
duration_title.pack(
    side="left",
    padx=(0, 12)
)


duration_var = tk.StringVar(value="6")

duration_menu = ttk.Combobox(
    options,
    textvariable=duration_var,
    values=["4", "6", "8", "10"],
    state="readonly",
    width=8,
    font=("Segoe UI", 10)
)
duration_menu.pack(
    side="left"
)

seconds_label = tk.Label(
    options,
    text="seconds",
    font=("Segoe UI", 10),
    bg=CARD,
    fg=MUTED
)
seconds_label.pack(
    side="left",
    padx=8
)


# --------------------- GENERATE BUTTON -----------------------

generate_button = tk.Button(
    card,
    text="🎶  GENERATE AI MUSIC",
    command=generate_music,
    font=("Segoe UI", 13, "bold"),
    bg=ACCENT,
    fg="white",
    activebackground=ACCENT_HOVER,
    activeforeground="white",
    relief="flat",
    cursor="hand2",
    padx=35,
    pady=14
)
generate_button.pack(
    pady=(25, 12)
)


# Clear button
clear_button = tk.Button(
    card,
    text="Clear Prompt",
    command=clear_prompt,
    font=("Segoe UI", 10),
    bg=CARD_2,
    fg=MUTED,
    activebackground=CARD_2,
    activeforeground=TEXT,
    relief="flat",
    cursor="hand2",
    padx=18,
    pady=7
)
clear_button.pack()


# ----------------------- PROGRESS ----------------------------

progress = ttk.Progressbar(
    card,
    mode="indeterminate",
    length=300
)
progress.pack(
    pady=(20, 8)
)


status_label = tk.Label(
    card,
    text="⏳ Loading AI Model...",
    font=("Segoe UI", 10, "bold"),
    bg=CARD,
    fg=ACCENT
)
status_label.pack()


# ------------------------- FOOTER ----------------------------

footer = tk.Label(
    root,
    text="CodeAlpha Artificial Intelligence Internship • Task 3",
    font=("Segoe UI", 9),
    bg=BG,
    fg=MUTED
)
footer.pack(
    pady=(0, 20)
)


# Start loading model
root.after(
    300,
    lambda: threading.Thread(
        target=load_model,
        daemon=True
    ).start()
)

root.mainloop()
