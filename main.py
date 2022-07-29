import argparse
import os
from src.core import download_files, download_labels_file

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AVA-Speech dataset downloader")
    parser.add_argument("-labels_file", "--labels_file", type=str, help="Labels file directory (str)")
    parser.add_argument("-fs", "--fs", type=int, help="Sample rate in Hz (int)")
    parser.add_argument("-o", "--o", type=str, help="Output directory (str)")
    parser.add_argument("-multiprocessing", "--multiprocessing", action='store_true', dest='multiprocessing', help="Use multiprocessing (bool)")
    parser.add_argument("-overwrite", "--overwrite", action='store_true', dest='overwrite', help="Overwrite existing files (bool)")
    parser.set_defaults(
        fs=16000,
        multiprocessing=False,
        overwrite=False,
        o=os.path.join(os.getcwd(), "dataset"),
        labels_file=None
    )
    args = parser.parse_args()
    
    assert args.fs in [8000, 16000, 44000]
    os.makedirs(args.o, exist_ok=True)

    if args.labels_file == None:
        download_labels_file()
        labels_files_dir = os.getcwd()
    else:
        assert os.path.exists(args.labels_file)
    
    download_files(input_files=os.path.join(os.getcwd(), "ava_speech_labels_v1.csv"),
                   use_multiprocessing=args.multiprocessing,
                   output_path=args.o,
                   fs=args.fs)