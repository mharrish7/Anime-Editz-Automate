from moviepy import *
import os

baseLayer = ColorClip((1080,1920), color=(0,0,0))

target_width = 1080

def zoom_in_cubic_ease_out(t, duration=0.3, slow_zoom_duration=1.0, slow_zoom_amount=0.2):
    
    if t <= duration:
        t_normalized = min(t / duration, 2)
        return 0.5 + ((t_normalized - 1)**3 + 1) * 0.3
    else:
        slow_t = t - duration 
        slow_t_normalized = slow_t / slow_zoom_duration
        return 0.5 + 0.3 + slow_t_normalized * slow_zoom_amount 

def zoom_out_cubic_ease_in(t, duration=0.3, slow_zoom_duration=1.0, slow_zoom_amount=-0.2):
   
    if t <= duration:
        t_normalized = min(t / duration, 2)
        return 2.5 - (t_normalized**3) * 0.3
    else:
        slow_t = t - duration
        slow_t_normalized = slow_t / slow_zoom_duration
        return 2.5 - 0.3 + slow_t_normalized * slow_zoom_amount 


def zoom_in_image(t):
    return 1.5 + t*0.1

def zoom_out_image(t):
    return 1.5 - t*0.1

def create_video_with_beat_transitions(image_folder, beat_file, audio_file, output_video="output.mp4", transition_duration=0.2):
    global baseLayer
    try:
        # Load images
        image_files = sorted([f for f in os.listdir(image_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))])
        images = []
        for f in image_files:
            img_clip = ImageClip(os.path.join(image_folder, f))
            img_clip = img_clip.resized(width=target_width) 
            images.append(img_clip.with_position("center")) 
        if not images:
            print("No images found in the specified folder.")
            return

        with open(beat_file, "r") as f:
            beat_times = [float(line.strip()) for line in f]

        if not beat_times:
            print("No beat times found in the specified file.")
            return

        audio_clip = AudioFileClip(audio_file)

        clips = []  
        last_beat = 0
        image_index = 0

        for beat in beat_times:
            if image_index >= len(images):
                break 
            if image_index == len(images)-1:
                current_image = images[image_index].with_duration(beat - last_beat + 3)
            else:
                current_image = images[image_index].with_duration(beat - last_beat)



            # if(image_index%2 == 0):
            #     current_image = current_image.with_effects(
            #     [vfx.Resize(zoom_in_cubic_ease_out)])
            # else:
            #     current_image = current_image.with_effects(
            #     [vfx.Resize(zoom_out_cubic_ease_in)])




                
            baseLayer = baseLayer.with_duration(current_image.duration)
            video1 = CompositeVideoClip([baseLayer, current_image])
            clips.append(video1)
            

            last_beat = beat
            image_index += 1


        final_clip = concatenate_videoclips(clips)

        audio_clip = audio_clip.with_duration(final_clip.duration + 3)
        final_clip = final_clip.with_audio(audio_clip)

        final_clip.write_videofile(output_video, fps=24)

        print(f"Video created successfully: {output_video}")

    except Exception as e:
        print(f"Error creating video: {e}")

image_folder = "images"
beat_file = "beats.txt"
audio_file = "audio2.mp3"
output_video = "output_with_audio_new2.mp4"

create_video_with_beat_transitions(image_folder, beat_file, audio_file, output_video)