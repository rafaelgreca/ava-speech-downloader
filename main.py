from src.core import download_files, download_labels_file

import argparse
import os
import pandas as pd
import logging

## create the log file
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler = logging.FileHandler("./logging.log")
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AVA-Speech dataset downloader")
    parser.add_argument("-labels_file", "--labels_file", type=str, help="Labels file directory (str)")
    parser.add_argument("-fs", "--fs", type=int, help="Sample rate in Hz (int). Default: 16000")
    parser.add_argument("-o", "--o", type=str, help="Output directory (str). Default: root_directory_folder/dataset")
    parser.add_argument("-multiprocessing", "--multiprocessing", action="store_true", dest="multiprocessing", help="Use multiprocessing (bool). Default: False")
    parser.add_argument("-overwrite", "--overwrite", action="store_true", dest="overwrite", help="Overwrite existing files (bool). Default: False")
    parser.add_argument("-c", "--c", nargs="+", type=str.lower, help="Specify the classes you want to download (str). Default: all")    
    parser.add_argument("-max_files", "--max_files", type=int, help="Max files to download from each class (int). Default: None (all of them)")
    parser.add_argument("-channels", "--channels", type=int, help="Channels audio output (int). Default: 1")
    parser.set_defaults(
        fs=16000,
        multiprocessing=False,
        overwrite=False,
        o=os.path.join(os.getcwd(), "dataset"),
        labels_file=None,
        c="all",
        max_files=None,
        channels=1
    )
    args = parser.parse_args()
    
    all_classes = ["clean-speech", "speech-noise", "speech-music", "no-speech"]
    available_fs = [8000, 16000]
    map_classes = {
        "clean-speech": "CLEAN_SPEECH",
        "no-speech": "NO_SPEECH",
        "speech-noise": "SPEECH_WITH_NOISE",
        "speech-music": "SPEECH_WITH_MUSIC"
    }

    assert args.fs in available_fs, f"The fs must be {available_fs}"
    assert ((args.max_files == None) or ((type(args.max_files) == int) and (args.max_files > 0))), f"You must provide a valid value for max_files or let it empty to download everything"

    ## mapping the chosen classes
    if args.c != "all":
        assert all([c in all_classes for c in args.c]), f"The class(es) must be {all_classes}"
        all_classes = [map_classes[c] for c in args.c]
    else:
        all_classes = [map_classes[c] for c in all_classes]

    ## creating the output path folder if doesn't exists already
    os.makedirs(args.o, exist_ok=True)

    ## if the labels_file path is None, then download the main csv file
    if args.labels_file == None:
        download_labels_file()
        labels_files_dir = os.path.join(os.getcwd(), "ava_speech_labels_v1.csv")
    else:
        ## check if the labels_file path exists
        assert os.path.exists(args.labels_file)

        ## check if the main csv is in the labels_file path
        assert os.path.exists(os.path.join(args.labels_file, "ava_speech_labels_v1.csv")), f"You need to download the ava_speech_labels_v1 csv file or keep the labels_file param None"
    
        labels_files_dir = os.path.join(args.labels_file, "ava_speech_labels_v1.csv")

    ## filter the classes to keep only what we want to download
    df = pd.read_csv(labels_files_dir, sep=",", header=None)
    df = df[df[3].isin(all_classes)]
    
    ## download the files
    download_files(df=df,
                   use_multiprocessing=args.multiprocessing,
                   output_path=args.o,
                   fs=args.fs,
                   max_files=args.max_files,
                   classes=all_classes,
                   overwrite=args.overwrite,
                   channels=args.channels)