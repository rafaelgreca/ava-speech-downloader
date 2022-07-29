from typing import List, Union
import os
import pandas as pd
import multiprocessing

def download_labels_file():
    os.system("wget -c https://research.google.com/ava/download/ava_speech_labels_v1.csv -q")

def create_files_csv(input_files: str):
    pass

def _aux_download_file(video_id, start_timestamp, end_timestamp, label, output_path, fs):
    youtube_dl_command = f"youtube-dl --format 'bestaudio' --get-url https://www.youtube.com/watch?v={video_id}"
    ffmpeg_command = f"ffmpeg -ss {start_timestamp} -to {end_timestamp} -i $({youtube_dl_command}) -ar {fs} -hide_banner -v warning {output_path}/{video_id}-{start_timestamp}-{end_timestamp}-{label}.wav"
    os.system(ffmpeg_command)

def download_files(df: pd.DataFrame,
                   use_multiprocessing: bool,
                   output_path: str,
                   fs: int,
                   max_files: Union[None, int],
                   classes: list,
                   overwrite: bool):

    if max_files != None:
        count_classes = {c:0 for c in classes}

    if use_multiprocessing:
        num_workers = multiprocessing.cpu_count() - 1
        pool = multiprocessing.Pool(num_workers)

        # d[0] = youtube video id
        # d[1] = start timestamp
        # d[2] = end timestamp
        # d[3] = label
        for i, infos in enumerate(zip(df[0], df[1], df[2], df[3], [output_path]*len(df[0]), [fs]*len(df[0]))):
            if count_classes[df.iloc[i, 3]] < max_files:                
                pool.starmap_async(_aux_download_file, [infos])
                count_classes[df.iloc[i, 3]] += 1
            else:
                is_over = all([count_classes[c] > max_files for c in count_classes.keys()])
                if is_over: break;
        
        pool.close()
        pool.join()
    else:
        for i, (video_id, start_timestamp, end_timestamp, label) in enumerate(zip(df[0], df[1], df[2], df[3])):
            if count_classes[df.iloc[i, 3]] < max_files:           
                _aux_download_file(video_id, start_timestamp, end_timestamp, label, output_path, fs)
                count_classes[df.iloc[i, 3]] += 1
            else:
                is_over = all([count_classes[c] >= max_files for c in count_classes.keys()])
                if is_over: break