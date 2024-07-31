"""
This program is a personlized text to speech program.
This uses the ARPABET which is a set of phonetic transcription codes,
and represents English with sequences of ASCII characters.
 
The audio clips are recorded and formatted with the .wav,
    can also work with .mp3.

"""

import tkinter as tk
from tkinter import filedialog
import pronouncing
import re
import time
from playsound import playsound
import os

# Constants
TIME_BETWEEN_WORDS = 0.5  # Time to pause between words
PAUSE_TOKEN = "pause_here"  # Token used to represent a pause

def speak(sounds, audio_dir):
    """
    Plays the audio files based on the list of sounds and handles pauses.
    
    Args:
        sounds (list): List of phoneme or pause tokens.
        audio_dir (str): Directory where audio files are stored.
    """
    to_play = []
    for word in sounds:
        if word == PAUSE_TOKEN:
            to_play.append(PAUSE_TOKEN)
            continue
        phonemes = word.split(' ')
        for phoneme in phonemes:
            file = os.path.join(audio_dir, phoneme + ".wav")
            if os.path.isfile(file):
                to_play.append(file)
            else:
                print(f"Audio file not found: {file}")

    for sound in to_play:
        if sound == PAUSE_TOKEN:
            time.sleep(TIME_BETWEEN_WORDS)  # Pause between words
        else:
            playsound(sound)  # Play the audio file

def split_string_and_clean(user_input):
    """
    Splits the input text into words, handles punctuation, and removes 
    duplicates.
    
    Args:
        user_input (str): The input text to process.
    
    Returns:
        list: A list of cleaned and processed words.
    """
    pause_delimiters = [",", "!", "?", ":", ";", "."]  # Delimiters 
    # that indicate a pause
    
    # Split input text into words based on spaces and other delimiters
    word_list = re.split(r" |\n|\t|\"", user_input)

    clean_counter = 0
    while clean_counter != len(word_list):
        if word_list[clean_counter][-1] in pause_delimiters:
            word_list[clean_counter] = word_list[clean_counter][:-1]  # Remove trailing punctuation
            word_list.insert(clean_counter + 1, PAUSE_TOKEN)  # Insert pause token
            clean_counter += 1
        clean_counter += 1

    # Remove duplicate words
    clean = False
    rem1 = ''
    rem2 = ' '
    while not clean:
        clean = True
        for word in word_list:
            if word == rem1:
                word_list.remove(rem1)
                clean = False
            elif word == rem2:
                word_list.remove(rem2)
                clean = False
    
    # Convert words to lowercase
    word_list = [word.lower() for word in word_list]

    return word_list

def generate_fallback_phonemes(word):
    """
    Generates a fallback phoneme representation for unrecognized words.
    
    Args:
        word (str): The word to generate phonemes for.
    
    Returns:
        str: Phoneme representation of the word.
    """
    phoneme_map = {
        'a': 'AE', 'e': 'EH', 'i': 'IH', 'o': 'OW', 'u': 'UH',
        'b': 'B', 'c': 'CH', 'd': 'D', 'f': 'F', 'g': 'G',
        'h': 'HH', 'j': 'JH', 'k': 'K', 'l': 'L', 'm': 'M',
        'n': 'N', 'p': 'P', 'q': 'K', 'r': 'R', 's': 'S',
        't': 'T', 'v': 'V', 'w': 'W', 'x': 'K S', 'y': 'Y',
        'z': 'Z', ' ': PAUSE_TOKEN
    }

    phonemes = [phoneme_map.get(char, 'UNKNOWN') for char in word]
    return ' '.join(phonemes)

def get_word_sounds(words):
    """
    Retrieves phoneme representations for words, falling back to generated 
    phonemes for unrecognized words.
    
    Args:
        words (list): List of words to convert to phonemes.
    
    Returns:
        tuple: (list of phoneme representations, list of unrecognized words)
    """
    pronunciations = [] 
    unrecognized_words = []

    for word in words:
        if word == PAUSE_TOKEN:
            pronunciations.append(PAUSE_TOKEN)
            continue

        try:
            orig_pronun = pronouncing.phones_for_word(word)[0]  # Get 
            # the pronunciation from the pronouncing library
        except IndexError:
            unrecognized_words.append(word)
            fallback_phonemes = generate_fallback_phonemes(word)  # Generate 
            # fallback phonemes
            pronunciations.append(fallback_phonemes)
            continue
        
        # Clean the pronunciation by removing digits
        updated_pronun = ""
        for letter in orig_pronun:
            if not letter.isdigit():
                updated_pronun += letter

        pronunciations.append(updated_pronun)

    return pronunciations, unrecognized_words

def browse_audio_directory():
    """
    Opens a dialog to select the audio directory and updates the entry field.
    """
    directory = filedialog.askdirectory(title="Select Audio Directory")
    if directory:
        audio_dir_entry.delete(0, tk.END)
        audio_dir_entry.insert(0, directory)

def process_text_to_speech():
    """
    Processes the input text, converts it to phonemes, and plays the 
    corresponding audio files.
    """
    text = text_input.get("1.0", tk.END).strip()
    audio_dir = audio_dir_entry.get().strip()

    if not text or not audio_dir:
        status_label.config(text="ERROR: Please enter both text and audio directory.")
        return

    words = split_string_and_clean(text)
    sounds, unrecognized_words = get_word_sounds(words)

    output_text = "\n".join(sounds)
    if unrecognized_words:
        output_text += "\n\nUnrecognized Words and Generated Phonemes:\n"
        for word in unrecognized_words:
            output_text += f"{word}: {generate_fallback_phonemes(word)}\n"

    output_area.delete("1.0", tk.END)  # Clear previous output
    output_area.insert(tk.END, output_text)  # Display the phonemes and unrecognized words

    status_label.config(text="Playing audio...")
    speak(sounds, audio_dir)  # Play the audio files
    status_label.config(text="Text-to-Speech conversion complete!")

# Create the main window
root = tk.Tk()
root.title("Pets - Personalized Text-to-Speech")
root.geometry("520x700")  # Set a fixed size for the window

# Define a modern color scheme
bg_color = "#2E3A4C"
fg_color = "#EAEAEA"
button_color = "#007BFF"
button_hover_color = "#0056b3"

root.configure(bg=bg_color)

# Create and place widgets
tk.Label(root, text="Welcome to Pets (Personalized Text-to-Speech)",
         font=("Helvetica Neue", 18), bg=bg_color, fg=fg_color).pack(pady=10)

tk.Label(root, text="Enter text:", font=("Helvetica Neue", 14),
         bg=bg_color, fg=fg_color).pack(pady=5)
text_input = tk.Text(root, height=5, width=50,
                     font=("Helvetica Neue", 12), bg="#1C1C1C",
                     fg=fg_color, borderwidth=0, highlightthickness=0)
text_input.pack(pady=5)

tk.Label(root, text="Audio Directory:", font=("Helvetica Neue", 14),
         bg=bg_color, fg=fg_color).pack(pady=5)
audio_dir_frame = tk.Frame(root, bg=bg_color)
audio_dir_frame.pack(pady=5)
audio_dir_entry = tk.Entry(audio_dir_frame, width=40,
                           font=("Helvetica Neue", 12), bg="#1C1C1C",
                           fg=fg_color, borderwidth=0, highlightthickness=0)
audio_dir_entry.pack(side=tk.LEFT, padx=5)
tk.Button(audio_dir_frame, text="Browse...", font=("Helvetica Neue", 12),
          bg=button_color, fg=fg_color, relief=tk.FLAT,
          command=browse_audio_directory).pack(side=tk.LEFT, padx=5)

tk.Button(root, text="Convert to Speech", font=("Helvetica Neue", 14),
          bg=button_color, fg=fg_color, relief=tk.FLAT,
          command=process_text_to_speech).pack(pady=10)

tk.Label(root, text="Output:", font=("Helvetica Neue", 14), bg=bg_color,
         fg=fg_color).pack(pady=5)
output_area = tk.Text(root, height=10, width=50,
                      font=("Helvetica Neue", 12), bg="#1C1C1C",
                      fg=fg_color, borderwidth=0, highlightthickness=0)
output_area.pack(pady=5)

status_label = tk.Label(root, text="", font=("Helvetica Neue", 12),
                        bg=bg_color, fg="lightblue")
status_label.pack(pady=10)

root.mainloop()