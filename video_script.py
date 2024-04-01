import glob
import subprocess

video_files = glob.glob("audio_files/set_two/*video-*")
print(video_files)
output_file = "output_video.webm"
# Create the input part of the command with `-i` flags for each audio file
inputs = ' '.join(f'-i "{file}"' for file in video_files)

# The number of inputs for the amix filter
num_inputs = len(video_files)
# Assemble and return the full FFmpeg command
command = f'ffmpeg {inputs} -filter_complex hstack=inputs=2 {output_file}'

print(command)
subprocess.call(command, shell=True)

# ffmpeg -i output_video.webm -i output_amix.webm -c copy -map 0:v:0 -map 1:a:0 combined_file.webm