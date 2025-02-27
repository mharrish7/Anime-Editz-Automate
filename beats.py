import librosa
import numpy as np
import soundfile as sf 

def find_high_decibel_beats(audio_file, threshold_percentage=0.7):
    try:
        y, sr = librosa.load(audio_file)
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        peaks = librosa.util.peak_pick(onset_env, pre_max=3, post_max=3, pre_avg=3, post_avg=5, delta=0.5, wait=0.3)
        times = librosa.frames_to_time(peaks)
        db = librosa.amplitude_to_db(np.abs(librosa.stft(y)), ref=np.max)
        beat_dbs = []

        for time in times:
            frame = librosa.time_to_frames(time, sr=sr)
            start_frame = max(0, frame - 2)
            end_frame = min(db.shape[1], frame + 3)
            beat_db = np.mean(db[:, start_frame:end_frame])
            beat_dbs.append(beat_db)

        min_db = np.min(beat_dbs)
        max_db = np.max(beat_dbs)
        print(f"Beat decibels: {beat_dbs}")
        threshold_db = min_db + (max_db - min_db) * threshold_percentage
        print(f"Threshold dB: {threshold_db}")
        high_db_beats = [time for i, time in enumerate(times) if beat_dbs[i] >= threshold_db]

        return high_db_beats, y, sr

    except Exception as e:
        print(f"Error processing audio: {e}")
        return [], None, None

def extract_and_save_high_beats(audio_file, output_file="high_beats.wav", time_file="beats.txt"): #added time_file
    high_beats, y, sr = find_high_decibel_beats(audio_file)

    if high_beats and y is not None and sr is not None:
        high_beat_segments = []
        segment_duration = 0.5

        for beat_time in high_beats:
            start_time = max(0, beat_time - segment_duration / 2)
            end_time = min(librosa.get_duration(y=y, sr=sr), beat_time + segment_duration / 2)
            start_sample = int(start_time * sr)
            end_sample = int(end_time * sr)
            high_beat_segments.extend(y[start_sample:end_sample])

        if high_beat_segments:
            sf.write(output_file, np.array(high_beat_segments), sr)
            print(f"High-decibel beat segments saved to {output_file}")

            with open(time_file, "w") as f:
                for beat_time in high_beats:
                    f.write(f"{beat_time:.6f}\n")
            print(f"High-decibel beat times saved to {time_file}")
        else:
            print("No high-decibel beat segments to save.")
    else:
        print("Could not extract high beats.")

audio_file = "audio2.mp3"
extract_and_save_high_beats(audio_file)