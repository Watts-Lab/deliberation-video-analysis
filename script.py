import glob
import subprocess
import re
import sys
import logging

# Set up basic configuration for logging
logging.basicConfig(level=logging.INFO)

def get_start(filepath):
    # Using subprocess to execute the ffprobe command and capture the output
    try:
        probe = subprocess.check_output(['ffprobe', filepath], stderr=subprocess.STDOUT, text=True)
    except subprocess.CalledProcessError as e:
        logging.error(f"ffprobe error: {e.output}")
        return 0.0

    # Search for the line that contains the start time
    line = next((line for line in probe.split('\n') if "start: " in line), None)
    if line:
        pattern = r"start:\s(\d+\.\d+)"
        match = re.search(pattern, line)
        if match:
            return float(match.group(1))
    logging.info("No start time listed, using 0.0")
    return 0.0

audio_files = glob.glob("files/set_two/*audio-*")

start_times = [get_start(path) for path in audio_files]
if start_times:
    lowest_start = start_times.index(min(start_times))
    print(f"Lowest start time among the given files: {lowest_start}")
else:
    print("No valid start times found.")
print(audio_files)
output_file = "output_amix.webm"
# Create the input part of the command with `-i` flags for each audio file
inputs = ' '.join(f'-i "{file}"' for file in audio_files)

# The number of inputs for the amix filter
num_inputs = len(audio_files)

# Construct the filter_complex part
filter_complex = f'amix=inputs={num_inputs}' # first, longest, shortest duration

# Assemble and return the full FFmpeg command
command = f'ffmpeg -isync {lowest_start} {inputs} -filter_complex "{filter_complex}" {output_file}'
# print(command)
subprocess.call(command)


ffmpeg -i "files/set_two/1677511696683-67eedcee-98bf-4f05-90f7-9e8ed2ce58cb-cam-audio-1677511704290" -isync 1 -i "audio_files/set_two/1677511696683-fc210681-bd73-4bfc-ac8d-1c5c606a9bd0-cam-audio-1677511697662" -isync 1  -filter_complex "amix=inputs=2" output_amix.webm