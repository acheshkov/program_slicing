import argparse
import datetime
import sys
import traceback
from pathlib import Path

import tqdm
from cchardet import detect
from numpy import mean, median, quantile

from program_slicing.decomposition.block_slicing import get_block_slices
from program_slicing.decomposition.slice_predicate import SlicePredicate
from program_slicing.graph.parse import LANG_JAVA


def detect_encoding_of_data(data: bytes):
    return detect(data)['encoding']


def read_text_with_autodetected_encoding(filename: str):
    with open(filename, 'rb') as target_file:
        data = target_file.read()

    if not data:
        return ''  # In case of empty file, return empty string

    encoding = detect_encoding_of_data(data) or 'utf-8'
    return data.decode(encoding)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run benchmark for block slicing')
    parser.add_argument(
        "-d", "--dir",
        required=True,
        help="Filepath to JAVA files"
    )
    parser.add_argument(
        "--iterations",
        "-i",
        type=int,
        default=1,
        help="Number of iterations to run benchmark script for all files. Default is 1"
    )

    args = parser.parse_args()

    arr_with_datetime_in_seconds = []

    java_files = list(Path(args.dir).glob('*.java'))
    
    print(f'We are going to run performance tests for Block Slicing algorithm. '
          f'The algorithm will run {len(java_files)} java files with 100 ncss.'
          f'The procedure will be run {args.iterations} time(s) for more accurate calculations.')
    sc = SlicePredicate(
        min_amount_of_lines=6,
        lang_to_check_parsing=LANG_JAVA,
        lines_are_full=True,
        filter_by_scope=False
    )
    for _ in tqdm.tqdm(range(args.iterations)):
        for java_file in tqdm.tqdm(java_files):
            text = read_text_with_autodetected_encoding(str(java_file))
            try:
                start_datetime = datetime.datetime.now()
                slices = get_block_slices(
                    text,
                    LANG_JAVA,
                    max_percentage_of_lines=0.8,
                    slice_predicate=sc)
                a = list(slices)
                end_datetime = datetime.datetime.now()
                diff_datetime = end_datetime - start_datetime

                arr_with_datetime_in_seconds.append(diff_datetime.seconds)
            except:
                print(f'Error while reading {java_file}')
                exc_type, exc_value, exc_traceback = sys.exc_info()
                traceback.print_exception(exc_type, exc_value, exc_traceback, file=sys.stdout)

    total_time_for_one_iteration = mean(arr_with_datetime_in_seconds) * len(java_files)
    print(f'Total time of running {len(java_files)} java methods (script was executed {args.iterations} times)'
          f' is {total_time_for_one_iteration} secs.\n'
          f'Average time for 1 method: {mean(arr_with_datetime_in_seconds):0.3f} secs. \n'
          f'Min time of 1 method: {min(arr_with_datetime_in_seconds):0.3f} secs, \n'
          f'max time of 1 method: {max(arr_with_datetime_in_seconds):0.3f} secs, \n'
          f'median: {median(arr_with_datetime_in_seconds):0.3f} secs, \n'
          f'quantile 75%: {quantile(arr_with_datetime_in_seconds, 0.75):0.3f} secs, \n'
          f'quantile 95%: {quantile(arr_with_datetime_in_seconds, 0.95):0.3f} secs')
