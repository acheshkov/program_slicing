import datetime
import os
from pathlib import Path
from time import time_ns, time

import pandas as pd

from program_slicing.decomposition.block_slicing import get_block_slices
from program_slicing.decomposition.slice_predicate import SlicePredicate
from program_slicing.graph.parse import LANG_JAVA
from numpy import mean
from veniq.utils.encoding_detector import read_text_with_autodetected_encoding
import tqdm

time_arr = []
datetime_arr = []
i = 0
work_dir = os.getcwd()
# for n in tqdm.tqdm(range(1000)):
java_files = Path(work_dir).glob('*.java')
# java_files = [r'D:\git\program_slicing2\dataset\CertificateServiceImpl_getTrustManager_20.0_7.0_142.0_8.java']
for java_file in java_files:
    print(java_file)
    text = read_text_with_autodetected_encoding(str(java_file))
    start_time = time()
    start_datetime = a = datetime.datetime.now()
    slices = get_block_slices(
        text,
        LANG_JAVA,
        max_percentage_of_lines=0.8,
        slice_predicate=SlicePredicate(
            min_amount_of_lines=6,
            lang_to_check_parsing=LANG_JAVA,
            lines_are_full=True,
            filter_by_scope=False,
        ))
    end_time = time()
    end_datetime = datetime.datetime.now()
    diff = end_time - start_time
    diff_datetime = end_datetime - start_datetime
    list(slices)
    datetime_arr.append(diff_datetime.microseconds)
    time_arr.append(diff)
    print(java_file)
    # for x in slices:
    #     print('##############################', x)
    # # break
    i += 1

# mean_secs = (mean(time_arr) / 1000) % 60
mean_secs = mean(time_arr)
mean_date_time_secs = mean(datetime_arr)
print(f'{mean_secs:0.10f} secs or {mean_date_time_secs:0.10f} microseconds for {i} methods')
