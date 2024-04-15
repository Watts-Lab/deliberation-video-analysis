import glob
import subprocess

video_files = glob.glob("files/set_two/*video-*")
output_file = "output_video.webm"
# Create the input part of the command with `-i` flags for each video file
inputs = ' '.join(f'-i "{file}"' for file in video_files)

# The number of inputs for the vstack filter
num_inputs = len(video_files)

# Assemble and return the full FFmpeg command
command = f'ffmpeg {inputs} -filter_complex "vstack=inputs={num_inputs}" {output_file}'

print(command)
subprocess.call(command, shell=True)

# ffmpeg -i output_video.webm -i output_amix.webm -c copy -map 0:v:0 -map 1:a:0 combined_file.webm
# ffmpeg -i output_video.webm -i output_amix.webm -map 0:v -map 0:a new_combined_file.webm