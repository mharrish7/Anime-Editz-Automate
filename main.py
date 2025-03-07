import tkinter as tk
from tkinter import filedialog, ttk
import threading
import os

from utils.beats import extract_and_save_high_beats
from utils.video import create_video_with_beat_transitions

VERSION = "1.1"

def browse_folder(entry):
    folder_selected = filedialog.askdirectory()
    entry.delete(0, tk.END)
    entry.insert(0, folder_selected)

def browse_file(entry):
    file_selected = filedialog.askopenfilename()
    entry.delete(0, tk.END)
    entry.insert(0, file_selected)

def start_process():
    start_button.config(state=tk.DISABLED)
    threshold_entry.config(state=tk.DISABLED)
    auto_check.config(state=tk.DISABLED)

    with open("progress.txt", "w") as f:
        f.write('')
    with open("beats.txt", "w") as f:
        f.write('')
    image_folder = image_folder_entry.get()
    beat_file = "beats.txt"
    audio_file = audio_file_entry.get()
    output_video = output_video_entry.get()
    threshold = float(threshold_entry.get())
    image_count = len(os.listdir(image_folder))
    beats_text.set(f"Found Images: {image_count} total \nStarting Up Beat Finder...")
    def process_video():
        if auto_var.get():
            threshold = find_optimal_threshold(audio_file, image_folder)

        extract_and_save_high_beats(audio_file, threshold)
        beat_count = len(open("beats.txt").read().split('\n')) - 1
        beats_text.set(f"Found Images: {image_count} total \nFound Beats: {beat_count} total \nCreating Video...")
        create_video_with_beat_transitions(image_folder, beat_file, audio_file, output_video)
        beats_text.set(beats_text.get() + "\n\nVideo creation complete.")
        start_button.config(state=tk.NORMAL)
        threshold_entry.config(state=tk.NORMAL)
        auto_check.config(state=tk.NORMAL)
        if auto_var.get():
            threshold_entry.config(state=tk.DISABLED)

    threading.Thread(target=process_video).start()

    def update_progress():
        if os.path.exists("progress.txt"):
            try:
                with open("progress.txt", "r") as f:
                    line = f.readline().strip()
                    if line:
                        value, maxvalue = map(float, line.split(","))
                        progress_var.set((value / maxvalue) * 100)
                        window.update_idletasks()
            except Exception as e:
                print(f"Error reading progress.txt: {e}")
        window.after(100, update_progress)

    update_progress()

def find_optimal_threshold(audio_file, image_folder):
    image_count = len(os.listdir(image_folder))
    low = 0
    high = 100
    best_threshold = 0.0

    while high >= low:
        mid = (low + high) // 2
        extract_and_save_high_beats(audio_file, mid / 100)
        beat_count = len(open("beats.txt").read().split('\n')) - 1
        if beat_count >= image_count:
            best_threshold = mid
            threshold_entry.config(state=tk.NORMAL)
            threshold_entry.delete(0, tk.END)
            threshold_entry.insert(0, str(best_threshold / 100))
            threshold_entry.config(state=tk.DISABLED)
            low = mid + 1
        else:
            high = mid - 1
    return best_threshold / 100

window = tk.Tk()
window.title(f"Beat-Synced Video Creator v{VERSION}")
window.geometry("600x500")
window.configure(bg="#f0f0f0")

# Image Folder
tk.Label(window, text="Image Folder:", bg="#f0f0f0").grid(row=0, column=0, sticky="w", padx=10, pady=5)
image_folder_entry = tk.Entry(window, width=50)
image_folder_entry.grid(row=0, column=1, padx=10, pady=5)
tk.Button(window, text="Browse", command=lambda: browse_folder(image_folder_entry)).grid(row=0, column=2, padx=10, pady=5)

# Audio File
tk.Label(window, text="Audio File:", bg="#f0f0f0").grid(row=1, column=0, sticky="w", padx=10, pady=5)
audio_file_entry = tk.Entry(window, width=50)
audio_file_entry.grid(row=1, column=1, padx=10, pady=5)
tk.Button(window, text="Browse", command=lambda: browse_file(audio_file_entry)).grid(row=1, column=2, padx=10, pady=5)

# Output Video
tk.Label(window, text="Output Video:", bg="#f0f0f0").grid(row=2, column=0, sticky="w", padx=10, pady=5)
output_video_entry = tk.Entry(window, width=50)
output_video_entry.grid(row=2, column=1, padx=10, pady=5)

# Threshold
tk.Label(window, text="Threshold:", bg="#f0f0f0").grid(row=3, column=0, sticky="w", padx=10, pady=5)
threshold_entry = tk.Entry(window, width=10)
threshold_entry.grid(row=3, column=1, sticky="w", padx=10, pady=5)
threshold_entry.insert(0, "0.85")

# Auto Threshold Checkbox
auto_var = tk.BooleanVar()
auto_check = tk.Checkbutton(window, text="Auto Threshold", variable=auto_var, bg="#f0f0f0", command=lambda: toggle_threshold_entry())
auto_check.grid(row=3, column=2, padx=10, pady=5, sticky="w")

def toggle_threshold_entry():
    if auto_var.get():
        threshold_entry.config(state=tk.DISABLED)
    else:
        threshold_entry.config(state=tk.NORMAL)

# Progress Bar
progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(window, variable=progress_var, maximum=100)
progress_bar.grid(row=4, column=0, columnspan=3, pady=10, padx=10, sticky="ew")

# Start Button
start_button = tk.Button(window, text="Start", command=start_process)
start_button.grid(row=5, column=1, pady=15)

# Beats Display
beats_text = tk.StringVar()
beats_label = tk.Label(window, textvariable=beats_text, justify="left", bg="#f0f0f0")
beats_label.grid(row=6, column=0, columnspan=3, pady=10, padx=10, sticky="w")

# Youtube Link and Version
youtube_link = tk.Label(window, text=f"v{VERSION} | My YouTube Channel", fg="blue", cursor="hand2", bg="#f0f0f0")
youtube_link.grid(row=7, column=2, pady=5, sticky="se") # Bottom right corner
youtube_link.bind("<Button-1>", lambda e: os.system("start https://www.youtube.com/channel/UC-46Gf3UvZevmTLTZbXtlUg"))

window.grid_columnconfigure(1, weight=1)
window.mainloop()