import argparse
import datetime
from pathlib import Path
from time import time
import traceback
import sys

import tqdm
from numpy import mean, median, quantile
from veniq.utils.encoding_detector import read_text_with_autodetected_encoding

from program_slicing.decomposition.block_slicing import get_block_slices
from program_slicing.decomposition.slice_predicate import SlicePredicate
from program_slicing.graph.parse import LANG_JAVA

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
        help="Number of iterations to run benchmark script for all files. "
    )
    parser.add_argument(
        "-csv", "--dataset_csv",
        help='Csv file location with benchmark data',
        type=Path
    )

    args = parser.parse_args()

    arr_with_time_in_seconds = []
    arr_with_datetime_in_seconds = []

    java_files = list(Path(args.dir).glob('*.java'))
    sc = SlicePredicate(
        min_amount_of_lines=6,
        lang_to_check_parsing=LANG_JAVA,
        lines_are_full=True,
        filter_by_scope=False
    )
    for _ in tqdm.tqdm(range(args.iterations)):
        for java_file in tqdm.tqdm(java_files):
            text = read_text_with_autodetected_encoding(str(java_file))
            start_time = time()
            start_datetime = datetime.datetime.now()
            try:
                slices = get_block_slices(
                    text,
                    LANG_JAVA,
                    max_percentage_of_lines=0.8,
                    slice_predicate=sc)
                a = list(slices)
                end_time = time()
                end_datetime = datetime.datetime.now()
                diff = end_time - start_time
                diff_datetime = end_datetime - start_datetime

                arr_with_datetime_in_seconds.append(diff_datetime.microseconds)
                arr_with_time_in_seconds.append(diff)
            except:
                print(f'Error while reading {java_file}')
                exc_type, exc_value, exc_traceback = sys.exc_info()
                #traceback.print_tb(exc_traceback, file=sys.stdout)
                traceback.print_exception(exc_type, exc_value, exc_traceback, file=sys.stdout)

    avg_sec = mean(arr_with_time_in_seconds)
    print(f'Average time: {avg_sec:0.10f} secs '
          f'or {mean(arr_with_datetime_in_seconds):0.10f} microseconds '
          f'for {len(java_files)} methods  (script was executed {args.iterations} times). \n'
          f'Min time {min(arr_with_time_in_seconds):0.10f} secs, \n'
          f'max time: {max(arr_with_time_in_seconds):0.10f} secs, \n'
          f'median: {median(arr_with_time_in_seconds):0.10f} secs, \n'
          f'quantile 75% {quantile(arr_with_time_in_seconds, 0.75):0.10f} secs, \n'
          f'quantile 95% {quantile(arr_with_time_in_seconds, 0.95):0.10f} secs')

    previous_best_time = 0.17  # in secs for laptop
    assert avg_sec < 0.18
