import json
from pathlib import Path

from program_slicing.decomposition.block_slicing import build_opportunities_filtered
from program_slicing.graph.parse import LANG_JAVA


def run_check(expected_EMOs, observable_EMOs):
    # print(json.dumps(observable_EMOs))
    for filename, ex_EMOs in expected_EMOs.items():
        observ_emos_set = set(observable_EMOs.get(filename))
        expect_emos_set = set(ex_EMOs)
        found_obj = observ_emos_set.difference(expect_emos_set)
        if found_obj:
            print(f'Objects which were not found in observable emos set: {json.dumps(tuple(found_obj))}')
        found_obj = expect_emos_set.difference(observ_emos_set)
        if found_obj:
            print(f'Objects which were not found in expect emos set emos set: {json.dumps(tuple(found_obj))}')


if __name__ == '__main__':

    cur_dir = Path(__file__).parent

    with open(Path(cur_dir, 'files', 'expected_EMOs.json')) as f:
        expected_EMOs = json.loads(f.read())
        observable_EMOs = {}
        for java_file in Path(cur_dir, 'files').glob('*.java'):
            with open(java_file) as f:
                code = f.read()
                found_opportunities = {
                    (program_slice.ranges[0][0].line_number, program_slice.ranges[-1][1].line_number)
                    for program_slice in build_opportunities_filtered(
                        code, LANG_JAVA, min_amount_of_lines=5, max_percentage_of_lines=0.8)
                }
            observable_EMOs[str(java_file)] = tuple(found_opportunities)

    run_check(expected_EMOs, observable_EMOs)

