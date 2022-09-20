from typing import List, Union

import os
import pandas as pd
import multiprocessing


def download_labels_file() -> None:
    """
    If the main csv file isn't in the root path, then download it.

    Param:
        None
    Return:
        None
    """
    os.system(
        "wget -c https://research.google.com/ava/download/ava_speech_labels_v1.csv -q"
    )


def _aux_download_file(
    video_id: str,
    start_timestamp: float,
    end_timestamp: float,
    label: str,
    video_extension: str,
) -> None:
    """
    Auxiliar function to download the videos.

    Param:
        :video_id: The YouTube's video id.
        :start_timestamp: The beggining of the video segment.
        :end_timestamp: The end of the video segment.
        :label: The corresponding label to that video segment.
    Return:
        None
    """
    os.makedirs(f"{PATH_OUTPUT}/{label}", exist_ok=True)
    download_command = f"https://s3.amazonaws.com/ava-dataset/trainval/{video_id}.{video_extension}"  # all credits to https://github.com/cvdfoundation/ava-dataset
    ffmpeg_command = (
        f"ffmpeg -{OVERWRITE_FILE} -ss {start_timestamp} -to {end_timestamp} -i {download_command} "
        + f"-ar {FRAME_SAMPLE} -ac {CHANNELS} -hide_banner -v warning {PATH_OUTPUT}/{label}/{video_id}-{start_timestamp}-{end_timestamp}.wav"
    )
    os.system(ffmpeg_command)


def download_files(
    df: pd.DataFrame,
    use_multiprocessing: bool,
    output_path: str,
    fs: int,
    max_files: Union[None, int],
    classes: List,
    overwrite: bool,
    channels: int,
) -> None:
    """
    Main function responsible to download the videos.

    Param:
        :df: The csv containing 
        :use_multiprocessing: Use multiprocessing or not.
        :output_path: Path where the downloaded videos will be saved.
        :fs: Frame sample of the video.
        :max_files: Max files to be downloaded for each class.
        :classes: Class(es) that will be downloaded.
        :overwrite: Overwrite or not the files (if already exists).
        :channels: How many channels the audio output will have.
    Return:
        None
    """
    global OVERWRITE_FILE
    global FRAME_SAMPLE
    global PATH_OUTPUT
    global CHANNELS

    if overwrite:
        OVERWRITE_FILE = "y"
    else:
        OVERWRITE_FILE = "n"

    FRAME_SAMPLE = fs
    PATH_OUTPUT = output_path
    CHANNELS = channels

    ## if max_files param isn't none, create a dictionary
    ## to keep track how many files have already been downloaded
    ## from each class
    if max_files != None:
        count_classes = {c: 0 for c in classes}

    if use_multiprocessing:
        num_workers = multiprocessing.cpu_count() - 1
        pool = multiprocessing.Pool(num_workers)

        # d[0] = youtube video id
        # d[1] = start timestamp
        # d[2] = end timestamp
        # d[3] = label
        # d[extension] = video's extension
        for i, infos in enumerate(zip(df[0], df[1], df[2], df[3], df["extension"])):

            if max_files != None:
                ## check if we have passed the max files amount for that class
                if count_classes[df.iloc[i, 3]] < max_files:
                    pool.starmap_async(_aux_download_file, [infos])
                    count_classes[df.iloc[i, 3]] += 1
                else:
                    ## check if we have passed the max files amount for all the classes
                    is_over = all(
                        [count_classes[c] > max_files for c in count_classes.keys()]
                    )
                    if is_over:
                        break
            else:
                pool.starmap_async(_aux_download_file, [infos])

        pool.close()
        pool.join()

    else:
        for i, (video_id, start_timestamp, end_timestamp, label) in enumerate(
            zip(df[0], df[1], df[2], df[3])
        ):

            if max_files != None:
                ## check if we have passed the max files amount for that class
                if count_classes[df.iloc[i, 3]] < max_files:
                    _aux_download_file(video_id, start_timestamp, end_timestamp, label)
                    count_classes[df.iloc[i, 3]] += 1
                else:
                    ## check if we have passed the max files amount for all the classes
                    is_over = all(
                        [count_classes[c] >= max_files for c in count_classes.keys()]
                    )
                    if is_over:
                        break
            else:
                _aux_download_file(video_id, start_timestamp, end_timestamp, label)
