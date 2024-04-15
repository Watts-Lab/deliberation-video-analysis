from os import path
import glob
import re

folder = 'test1'
files = glob.glob('*cam*')

group_data = {}
for filepath in files:
    if ".webm" not in filepath:
        continue
    basename = path.basename(filepath)
    participant_id = "-".join(basename.split("-")[1:-3])
    track_type = basename.split("-")[-2]
    track_start = int(basename.split("-")[-1].split(".")[0])
    group_start = int(basename.split("-")[0])

    if participant_id not in group_data:
        group_data[participant_id] = {
        "participant_id": participant_id,
        "group_start": int(basename.split("-")[0]),
        "dirname": path.dirname(filepath),
    }

    probe_output = subprocess.check_output(['ffprobe', filepath], stderr=subprocess.STDOUT, text=True)
    
    # get start offset
    line = [line  for line in probe if "start: " in line][0]
    start = re.search(r'start: (\d+\.\d+)', line).group(1)
    group_data[participant_id][track_type+"_track_start"] = start

    if track_type == "video":
        # get resolution
        line = [line  for line in probe if "Stream " in line][0]
        resolution = re.search(r'\d+x\d+', line).group(0)
        group_data[participant_id][track_type+"_resolution"] = resolution


    group_data[participant_id][track_type] = filepath
    group_data[participant_id][track_type+"_start"] = track_start
    group_data[participant_id][track_type+"_offset"] = track_start - group_start


for filepath in files:
    print(filepath)
    if filepath.endswith(".mp4") or "audio" in filepath:
        continue
    outfilePath = filepath.replace(".webm", ".mp4")
    print(filepath, outfilePath)
    cmd = ["ffmpeg", "-i", filepath, "-r", "24", outfilePath, "-y"]
    subprocess.call(cmd)

# format inputs
audio_inputs = [f'-itsoffset "{ group_data[i]["audio_track_start"] }" -i {group_data[i]["audio"]}' for i in group_data]
video_inputs = [f'-itsoffset "{ group_data[i]["video_track_start"] }" -i {group_data[i]["video"].replace(".webm", ".mp4")}' for i in group_data]

# format audio chain
audioChain = "".join([f'[{i}:a]' for i in range(len(audio_inputs))]) + \
    f'amerge=inputs={len(audio_inputs)},' + \
    f'pan=mono|c0<{ "+".join([f"c{j}" for j in range(len(audio_inputs)*2)])}|[a]'

# format video chain
videoChain = "".join([f'[{i+len(audio_inputs)}:v]scale=1280:720[v{i}];' for i in range(len(video_inputs))]) + \
    f'{"".join([f"[v{i}]" for i in range(len(video_inputs))])}hstack=inputs={len(video_inputs)}[v]'

cmd = f'ffmpeg {" ".join(audio_inputs)} {" ".join(video_inputs)} -filter_complex "{audioChain};{videoChain}" -map "[a]" -map "[v]" test_resampled.mp4'

subprocess.call(cmd, shell=True)
