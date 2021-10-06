import json
from pathlib import Path

import tqdm

from program_slicing.file_manager.reader import read_file, read_json
from program_slicing.decomposition.block.slicing import get_block_slices
from program_slicing.decomposition.slice_predicate import SlicePredicate
from program_slicing.graph.parse import Lang


def run_check(expected_emos, observable_emos):
    for filename, ex_emos in expected_emos.items():
        print(filename, end="\t")
        observable_emos_set = set(observable_emos.get(filename))
        expect_emos_set = set([tuple(x) for x in ex_emos])
        message = ""
        found_obj = observable_emos_set.difference(expect_emos_set)
        if found_obj:
            message += f'Objects which were wrongly found: {json.dumps(tuple(sorted(found_obj)), indent=4)}\n'
        found_obj = expect_emos_set.difference(observable_emos_set)
        if found_obj:
            message += f'Objects which were not found: {json.dumps(tuple(sorted(found_obj)), indent=4)}\n'
        if message:
            raise Exception(message)
        print("OK")


def main():
    cur_dir = Path(__file__).parent
    expected_emos = read_json(Path(cur_dir, 'files', 'expected_EMOs.json'))
    observable_emos = {}
    for java_file in tqdm.tqdm(Path(cur_dir, 'files').glob('*.java')):
        code = read_file(java_file)
        found_opportunities = {
            (program_slice.ranges[0][0].line_number + 1, program_slice.ranges[-1][1].line_number + 1)
            for program_slice in get_block_slices(
                code,
                Lang.JAVA,
                slice_predicate=SlicePredicate(
                    min_amount_of_lines=6,
                    min_amount_of_statements=5,
                    max_percentage_of_lines=0.8,
                    lang_to_check_parsing=Lang.JAVA,
                    lines_are_full=True
                )
            )
        }
        observable_emos[java_file.name] = tuple(found_opportunities)
    run_check(expected_emos, observable_emos)


if __name__ == '__main__':
    main()
