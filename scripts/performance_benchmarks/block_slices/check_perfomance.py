import argparse
import datetime
import sys
import traceback
from pathlib import Path

import tqdm
from numpy import mean, median, quantile

from program_slicing.file_manager.reader import read_file
from program_slicing.decomposition.block.slicing import get_block_slices
from program_slicing.decomposition.slice_predicate import SlicePredicate
from program_slicing.graph.parse import Lang


def main():
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
    print(f'\rWe are going to run performance tests for Block Slicing algorithm. '
          f'The algorithm will run {len(java_files)} java files with 100 ncss. '
          f'The procedure will be run {args.iterations} time(s) for more accurate calculations.')
    sp = SlicePredicate(
        min_amount_of_lines=6,
        min_amount_of_statements=5,
        max_percentage_of_lines=0.8,
        max_amount_of_exit_statements=1,
        cause_code_duplication=False,
        lang_to_check_parsing=Lang.JAVA,
        lines_are_full=True
    )
    for i in range(args.iterations):
        print(f"\rIteration: {i+1}/{args.iterations}")
        for java_file in tqdm.tqdm(java_files):
            text = read_file(java_file)
            try:
                start_datetime = datetime.datetime.now()
                list(get_block_slices(
                    text,
                    Lang.JAVA,
                    slice_predicate=sp
                ))
                end_datetime = datetime.datetime.now()
                diff_datetime = end_datetime - start_datetime
                arr_with_datetime_in_seconds.append(diff_datetime.seconds + diff_datetime.microseconds / 1e6)
            except Exception as e:
                print(f'Error while reading {java_file}: {e}')
                exc_type, exc_value, exc_traceback = sys.exc_info()
                traceback.print_exception(exc_type, exc_value, exc_traceback, file=sys.stdout)
    total_time_for_one_iteration = mean(arr_with_datetime_in_seconds) * len(java_files)
    print(f'Total time of running {len(java_files)} java methods is '
          f'{total_time_for_one_iteration} secs for 1 iteration. \n'
          f'Script was executed {args.iterations} times.\n'
          f'Average time for 1 method: {mean(arr_with_datetime_in_seconds):0.3f} secs. \n'
          f'Min time of 1 method: {min(arr_with_datetime_in_seconds):0.3f} secs, \n'
          f'max time of 1 method: {max(arr_with_datetime_in_seconds):0.3f} secs, \n'
          f'median: {median(arr_with_datetime_in_seconds):0.3f} secs, \n'
          f'quantile 75%: {quantile(arr_with_datetime_in_seconds, 0.75):0.3f} secs, \n'
          f'quantile 95%: {quantile(arr_with_datetime_in_seconds, 0.95):0.3f} secs')


if __name__ == '__main__':
    main()
