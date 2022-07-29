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

def download_files(input_files: str,
                   use_multiprocessing: bool,
                   output_path: str,
                   fs: int):

    df = pd.read_csv(input_files, sep=',', header=None)

    if use_multiprocessing:
        num_workers = multiprocessing.cpu_count() - 1
        pool = multiprocessing.Pool(num_workers)

        for infos in zip(df[0], df[1], df[2], df[3], [output_path]*len(df[0]), [fs]*len(df[0])):
            pool.starmap_async(_aux_download_file, [infos])
        
        pool.close()
        pool.join()
    else:
        for video_id, start_timestamp, end_timestamp, label in zip(df[0], df[1], df[2], df[3]):
            _aux_download_file(video_id, start_timestamp, end_timestamp, label, output_path, fs)