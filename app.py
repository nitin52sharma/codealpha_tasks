import tkinter as tk
from tkinter import ttk, messagebox
import requests

# ---------------- LANGUAGE DATA ----------------
LANGUAGES = {
    "English": "en",
    "Hindi": "hi",
    "Punjabi": "pa",
    "French": "fr",
    "Spanish": "es",
    "German": "de",
    "Italian": "it",
    "Portuguese": "pt",
    "Russian": "ru",
    "Japanese": "ja"
}


# ---------------- TRANSLATION FUNCTION ----------------
def translate_text():
    text = input_box.get("1.0", tk.END).strip()

    if not text:
        messagebox.showwarning("Input Required", "Please enter some text first.")
        return

    source = source_language.get()
    target = target_language.get()

    if source == target:
        output_box.delete("1.0", tk.END)
        output_box.insert(tk.END, text)
        return

    translate_button.config(state="disabled", text="Translating...")
    root.update()

    try:
        url = "https://api.mymemory.translated.net/get"

        params = {
            "q": text,
            "langpair": f"{LANGUAGES[source]}|{LANGUAGES[target]}"
        }

        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()

        data = response.json()

        translated_text = data["responseData"]["translatedText"]

        output_box.delete("1.0", tk.END)
        output_box.insert(tk.END, translated_text)

    except requests.exceptions.RequestException:
        messagebox.showerror(
            "Connection Error",
            "Internet connection or translation service is unavailable."
        )

    except Exception as error:
        messagebox.showerror(
            "Translation Error",
            f"Something went wrong:\n{error}"
        )

    finally:
        translate_button.config(state="normal", text="Translate")


# ---------------- COPY FUNCTION ----------------
def copy_translation():
    text = output_box.get("1.0", tk.END).strip()

    if not text:
        messagebox.showwarning("Nothing to Copy", "There is no translated text.")
        return

    root.clipboard_clear()
    root.clipboard_append(text)
    root.update()

    messagebox.showinfo("Copied", "Translation copied to clipboard!")


# ---------------- CLEAR FUNCTION ----------------
def clear_text():
    input_box.delete("1.0", tk.END)
    output_box.delete("1.0", tk.END)


# ---------------- MAIN WINDOW ----------------
root = tk.Tk()
root.title("AI Language Translation Tool")
root.geometry("850x700")
root.resizable(False, False)

# ---------------- HEADER ----------------
header = tk.Frame(root)
header.pack(fill="x", pady=(20, 10))

title = tk.Label(
    header,
    text="AI Language Translation Tool",
    font=("Arial", 24, "bold")
)
title.pack()

subtitle = tk.Label(
    header,
    text="Translate text between multiple languages",
    font=("Arial", 11)
)
subtitle.pack(pady=5)


# ---------------- LANGUAGE SELECTION ----------------
language_frame = tk.Frame(root)
language_frame.pack(pady=15)

tk.Label(
    language_frame,
    text="Source Language:",
    font=("Arial", 11, "bold")
).grid(row=0, column=0, padx=10)

source_language = ttk.Combobox(
    language_frame,
    values=list(LANGUAGES.keys()),
    state="readonly",
    width=18
)
source_language.set("English")
source_language.grid(row=0, column=1, padx=10)

tk.Label(
    language_frame,
    text="Target Language:",
    font=("Arial", 11, "bold")
).grid(row=0, column=2, padx=10)

target_language = ttk.Combobox(
    language_frame,
    values=list(LANGUAGES.keys()),
    state="readonly",
    width=18
)
target_language.set("Hindi")
target_language.grid(row=0, column=3, padx=10)


# ---------------- INPUT ----------------
tk.Label(
    root,
    text="Enter Text",
    font=("Arial", 13, "bold")
).pack(anchor="w", padx=65)

input_box = tk.Text(
    root,
    height=9,
    width=82,
    font=("Arial", 12),
    wrap="word"
)
input_box.pack(pady=(5, 15))


# ---------------- TRANSLATE BUTTON ----------------
translate_button = tk.Button(
    root,
    text="Translate",
    command=translate_text,
    font=("Arial", 12, "bold"),
    padx=25,
    pady=8,
    cursor="hand2"
)
translate_button.pack(pady=5)


# ---------------- OUTPUT ----------------
tk.Label(
    root,
    text="Translated Text",
    font=("Arial", 13, "bold")
).pack(anchor="w", padx=65, pady=(15, 0))

output_box = tk.Text(
    root,
    height=9,
    width=82,
    font=("Arial", 12),
    wrap="word"
)
output_box.pack(pady=(5, 10))


# ---------------- BUTTONS ----------------
button_frame = tk.Frame(root)
button_frame.pack(pady=5)

copy_button = tk.Button(
    button_frame,
    text="Copy Translation",
    command=copy_translation,
    font=("Arial", 11, "bold"),
    padx=15,
    pady=6,
    cursor="hand2"
)
copy_button.grid(row=0, column=0, padx=10)

clear_button = tk.Button(
    button_frame,
    text="Clear",
    command=clear_text,
    font=("Arial", 11, "bold"),
    padx=25,
    pady=6,
    cursor="hand2"
)
clear_button.grid(row=0, column=1, padx=10)


# ---------------- FOOTER ----------------
footer = tk.Label(
    root,
    text="Powered by MyMemory Translation API",
    font=("Arial", 9)
)
footer.pack(pady=15)


# ---------------- START APP ----------------
root.mainloop()