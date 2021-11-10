__licence__ = 'MIT'
__author__ = 'lyriccoder'
__credits__ = ['lyriccoder, kuyaki']
__maintainer__ = 'lyriccoder'
__date__ = '2021/11/08'

from pathlib import Path

import tqdm

from integration_tests.integration_slicing import run_check
from program_slicing.file_manager.reader import read_file, read_json
from program_slicing.decomposition.variable.slicing import get_variable_slices
from program_slicing.decomposition.slice_predicate import SlicePredicate
from program_slicing.graph.parse import Lang


def main():
    cur_dir = Path(__file__).parent
    expected_emos = read_json(Path(cur_dir, 'files', 'expected_variable_slices.json'))
    observable_emos = {}
    for java_file in tqdm.tqdm(Path(cur_dir, 'files').glob('*.java')):
        code = read_file(java_file)
        found_opportunities = {
            tuple(r[0].line_number + 1 for r in program_slice.ranges)
            for program_slice in get_variable_slices(
                code,
                Lang.JAVA,
                slice_predicate=SlicePredicate(
                    min_amount_of_lines=4,
                    min_amount_of_statements=2,
                    max_percentage_of_lines=0.8,
                    max_amount_of_exit_statements=1,
                    cause_code_duplication=False,
                    lang_to_check_parsing=Lang.JAVA,
                    lines_are_full=True,
                    has_returnable_variable=True,
                )
            )
        }
        observable_emos[java_file.name] = tuple(found_opportunities)
    run_check(expected_emos, observable_emos)


if __name__ == '__main__':
    main()
