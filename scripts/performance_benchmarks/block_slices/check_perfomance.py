import argparse
import datetime
import sys
import traceback
from pathlib import Path

import tqdm
from cchardet import detect
from numpy import mean, median, quantile

from program_slicing.decomposition.block_slicing.main import get_block_slices
from program_slicing.graph.parse import LANG_JAVA
import pandas as pd


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
    df = pd.DataFrame(columns=[
        'filename',
        'emos_number_final',
        'all_non_filtered_emos',
        'has_multiple_exit_nodes',
        'check_min_amount_of_lines',
        # 'does_slice_match_scope'
        'has_multiple_output_params',
        'check_parsing',
        'check_all_lines_are_full'])

    java_files = list(Path(args.dir).glob('*.java'))
    print(f'We are going to run performance tests for Block Slicing algorithm. '
          f'The algorithm will run {len(java_files)} java files with 100 ncss.'
          f'The procedure will be run {args.iterations} time(s) for more accurate calculations.')
    for _ in tqdm.tqdm(range(args.iterations)):
        for java_file in tqdm.tqdm(java_files):
            text = read_text_with_autodetected_encoding(str(java_file))
            try:
                start_datetime = datetime.datetime.now()
                time_dict, slices = get_block_slices(
                    text,
                    LANG_JAVA,
                    max_percentage_of_lines=0.8,
                    min_lines_number=6)
                a = list(slices)
                end_datetime = datetime.datetime.now()
                diff_datetime = end_datetime - start_datetime
                arr_with_datetime_in_seconds.append(diff_datetime.seconds)
                t = {
                    'filename': (java_file).name,
                    'emos_number_final': len(a),
                    'total_time': sum([x[1] for x in list(time_dict.values())])}
                df = df.append({**t, **time_dict}, ignore_index=True)
            except:
                print(f'Error while reading {java_file}')
                exc_type, exc_value, exc_traceback = sys.exc_info()
                traceback.print_exception(exc_type, exc_value, exc_traceback, file=sys.stdout)

    total_time_for_one_iteration = mean(arr_with_datetime_in_seconds) * len(java_files)
    df.to_csv('df.csv')
    print(f'Total time of running {len(java_files)} java methods is '
          f'{total_time_for_one_iteration} secs for 1 iteration. \n'
          f'Script was executed {args.iterations} times.\n'
          f'Average time for 1 method: {mean(arr_with_datetime_in_seconds):0.3f} secs. \n'
          f'Min time of 1 method: {min(arr_with_datetime_in_seconds):0.3f} secs, \n'
          f'max time of 1 method: {max(arr_with_datetime_in_seconds):0.3f} secs, \n'
          f'median: {median(arr_with_datetime_in_seconds):0.3f} secs, \n'
          f'quantile 75%: {quantile(arr_with_datetime_in_seconds, 0.75):0.3f} secs, \n'
          f'quantile 95%: {quantile(arr_with_datetime_in_seconds, 0.95):0.3f} secs')
