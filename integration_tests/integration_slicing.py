__licence__ = 'MIT'
__author__ = 'lyriccoder'
__credits__ = ['lyriccoder, kuyaki']
__maintainer__ = 'lyriccoder'
__date__ = '2021/11/08'

import json


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
