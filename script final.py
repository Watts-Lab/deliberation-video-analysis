import argparse
import glob
import os
import re
import subprocess

def main(folder):
    files = glob.glob(f'files/{folder}/*')
    files.sort()
    print("Files to process:", files)

    # Using ffprobe to get the audio/video start times (this is needed for offsetting/adelay)
    group_data = {}
    for filepath in files:
        if ".webm" not in filepath:
            continue
        basename = os.path.basename(filepath)
        participant_id = "-".join(basename.split("-")[1:-3])
        track_type = basename.split("-")[-2]
        track_start = int(basename.split("-")[-1].split(".")[0])
        group_start = int(basename.split("-")[0])

        if participant_id not in group_data:
            group_data[participant_id] = {
                "participant_id": participant_id,
                "group_start": group_start,
                "dirname": os.path.dirname(filepath),
            }

        result = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'a:0', '-show_entries', 'stream=start', '-of', 'default=noprint_wrappers=1:nokey=1', filepath], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        start = float(result.stdout.strip())
        group_data[participant_id][track_type+"_track_start"] = start

        if track_type == "video":
            result = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height', '-of', 'csv=s=x:p=0', filepath], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            resolution = result.stdout.strip()
            group_data[participant_id][track_type+"_resolution"] = resolution

        group_data[participant_id][track_type] = filepath
        group_data[participant_id][track_type+"_start"] = track_start
        group_data[participant_id][track_type+"_offset"] = track_start - group_start

    # Process each video and audio file
    for participant, data in group_data.items():
        if "video" in data and "audio" in data:
            video_file = data["video"].replace(".webm", ".mp4")
            audio_file = data["audio"]
            outfile = os.path.join(data["dirname"], f"{participant}-merged.mp4")
            cmd = [
                'ffmpeg', '-i', video_file, '-i', audio_file,
                '-filter_complex', f'[0:v]scale={data["video_resolution"]}[v];[1:a]adelay={int(data["audio_track_start"]*1000)}|{int(data["audio_track_start"]*1000)}[a]',
                '-map', '[v]', '-map', '[a]', outfile, '-y'
            ]
            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Generate a combined video
    input_cmd = []
    filter_complex = []
    for i, (participant, data) in enumerate(group_data.items()):
        if "video" in data:
            input_cmd.extend(['-i', data["video"].replace(".webm", ".mp4")])
            filter_complex.append(f'[{i}:v]scale=1280:720[v{i}]')

    filter_complex.append(f"{''.join(f'[v{i}]' for i in range(len(filter_complex)))}hstack=inputs={len(filter_complex)}[v]")
    output_file = f'files/{folder}/output_video.mp4'
    full_cmd = ['ffmpeg'] + input_cmd + ['-filter_complex', ';'.join(filter_complex), '-map', '[v]', output_file, '-y']
    subprocess.run(full_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process videos and audios into a single merged file.")
    parser.add_argument('folder', type=str, help='Folder containing the video and audio files')
    args = parser.parse_args()

    main(args.folder)
