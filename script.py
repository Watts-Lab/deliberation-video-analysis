import glob
import subprocess

audio_files = glob.glob("audio_files/set_two/*audio-*")
print(audio_files)
output_file = "output_amix.webm"
# Create the input part of the command with `-i` flags for each audio file
inputs = ' '.join(f'-i "{file}"' for file in audio_files)

# The number of inputs for the amix filter
num_inputs = len(audio_files)

# Construct the filter_complex part
filter_complex = f'amix=inputs={num_inputs}' # first, longest, shortest duration

# Assemble and return the full FFmpeg command
command = f'ffmpeg {inputs} -filter_complex "{filter_complex}" {output_file}'
print(command)

