import json
from pathlib import Path

from program_slicing.decomposition.block_slicing import build_opportunities_filtered
from program_slicing.graph.parse import LANG_JAVA


def run_check(expected_emos, observable_emos):
    for filename, ex_emos in expected_emos.items():
        print(filename)
        observable_emos_set = set(observable_emos.get(filename))
        expect_emos_set = set([tuple(x) for x in ex_emos])
        found_obj = observable_emos_set.difference(expect_emos_set)
        if found_obj:
            raise Exception(f'Objects which were wrongly found: {json.dumps(tuple(found_obj))}')
        found_obj = expect_emos_set.difference(observable_emos_set)
        if found_obj:
            raise Exception(f'Objects which were not found: {json.dumps(tuple(found_obj))}')


def main():
    cur_dir = Path(__file__).parent

    with open(Path(cur_dir, 'files', 'expected_EMOs.json')) as json_f:
        expected_emos = json.loads(json_f.read())
        observable_emos = {}
        for java_file in Path(cur_dir, 'files').glob('*.java'):
            with open(java_file) as java_f:
                code = java_f.read()
                found_opportunities = {
                    (program_slice.ranges[0][0].line_number + 1, program_slice.ranges[-1][1].line_number + 1)
                    for program_slice in build_opportunities_filtered(
                        code, LANG_JAVA, min_amount_of_lines=5, max_percentage_of_lines=0.8)
                }
            observable_emos[java_file.name] = tuple(found_opportunities)

    run_check(expected_emos, observable_emos)


if __name__ == '__main__':
    main()
