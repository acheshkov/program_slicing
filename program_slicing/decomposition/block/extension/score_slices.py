from collections import defaultdict
from functools import reduce
from sys import argv
import os
import re

import pandas as pd

from program_slicing.graph.manager import ProgramGraphsManager
from program_slicing.graph.parse import Lang
from program_slicing.decomposition.slice_predicate import SlicePredicate
from program_slicing.decomposition.block.slicing import get_block_slices
from program_slicing.decomposition.block.extension.slicing import get_extended_block_slices
from program_slicing.decomposition.block.extension.scoring import length_score_hh,\
    nesting_depth_score_hh, nesting_area_score_hh, parameters_score_hh, aggregate_score_hh


def __traverse(root):
    yield root
    for child in root.children:
        for result in __traverse(child):
            yield result


def __score_slice(score_stats, slice, slice_type, code_lines, manager, method_statements, nesting_depth_dic):
    _length_score = length_score_hh(code_lines, slice)
    score_stats["length_score_hh"][_length_score].add(slice_type)
    _depth_score = nesting_depth_score_hh(slice, method_statements, nesting_depth_dic)
    score_stats["nesting_depth_score_hh"][_depth_score].add(slice_type)
    _area_score = nesting_area_score_hh(slice, method_statements, nesting_depth_dic)
    score_stats["nesting_area_score_hh"][_area_score].add(slice_type)
    _params_score = parameters_score_hh(slice)
    score_stats["parameters_score_hh"][_params_score].add(slice_type)
    _score_hh = aggregate_score_hh(code, slice, _area_score, _depth_score, _length_score, _params_score)
    score_stats["aggregate_score_hh"][_score_hh].add(slice_type)
    # _score_silva = score_silva_vars(slice)
    # score_stats["score_silva_vars"][_score_silva].add(slice_type)


if __name__ == "__main__":
    dir_with_slice_stats = argv[1]
    output_dir = argv[2]
    lang = Lang.JAVA
    min_amount_of_lines = 4
    min_amount_of_statements = 3

    block_predicate = SlicePredicate(
        min_amount_of_lines=min_amount_of_lines,
        min_amount_of_statements=min_amount_of_statements,
        max_percentage_of_lines=0.8,
        lang_to_check_parsing=Lang.JAVA,
        lines_are_full=True)
    ccs_predicate = SlicePredicate(
        min_amount_of_lines=min_amount_of_lines,
        min_amount_of_statements=min_amount_of_statements,
        max_percentage_of_lines=0.8,
        lang_to_check_parsing=Lang.JAVA,
        has_returnable_variable=True)
    extended_block_predicate = SlicePredicate(
        min_amount_of_lines=min_amount_of_lines,
        min_amount_of_statements=min_amount_of_statements,
        max_percentage_of_lines=0.8,
        lang_to_check_parsing=Lang.JAVA,
        lines_are_full=True)

    score_function_names = [
        "length_score_hh",
        "nesting_depth_score_hh",
        "nesting_area_score_hh",
        "parameters_score_hh",
        "aggregate_score_hh"]
    # "score_silva_vars"]
    output_dic = {"method": []}
    for score_f in score_function_names:
        output_dic[score_f + "_top_1_block"] = []
        output_dic[score_f + "_top_1_ext_block"] = []
        output_dic[score_f + "_top_1_shared"] = []
        output_dic[score_f + "_top_3_block"] = []
        output_dic[score_f + "_top_3_ext_block"] = []

    if os.path.isfile(os.path.join(dir_with_slice_stats, 'slice_stats.csv')):

        df = pd.read_csv(os.path.join(dir_with_slice_stats, 'slice_stats.csv'))
        for filepath, filepath_group in df.groupby('filepath'):
            if sum(filepath_group['diff_block_num']) == 0:
                continue
            with open(os.path.join("/home/katya/QualitasCorpus-20130901r/Systems/", filepath)) as f:
                code = f.read()
                code_lines = code.splitlines()
            manager = ProgramGraphsManager(code, lang)
            for _, row in filepath.iterrows():
                method = row['method']
                _start_line = int(re.sub(r"\.java_([0-9]+)_[0-9]+", r"\1", method))
                _end_line = int(re.sub(r"\.java_[0-9]+_([0-9]+)", r"\1", method))
                method_declaration = "\n".join(code_lines[_start_line:(_end_line + 1)])

                block_slices = set(get_block_slices(method_declaration, lang, ccs_predicate))
                extended_block_slices = set(
                    get_extended_block_slices(method_declaration, lang, slice_predicate=extended_block_predicate))
                diff_extended = extended_block_slices.difference(block_slices)
                method_statements = None
                nesting_depth_dic = None
                score_stats = {k: defaultdict(lambda: set()) for k in score_function_names}
                for _slice in block_slices:
                    __score_slice(
                        score_stats,
                        _slice,
                        'block',
                        code_lines,
                        manager,
                        method_statements,
                        nesting_depth_dic)
                for _slice in diff_extended:
                    __score_slice(score_stats, _slice, 'ext_block', code_lines, manager, method_statements,
                                  nesting_depth_dic)
                for k, _list in output_dic.items():
                    if k == 'method':
                        _list.append(method)
                    else:
                        _list.append(False)
                for score_f, score_dic in score_stats:
                    top_scores = list(sorted(score_dic.keys(), reverse=True))
                    if score_dic[top_scores[0]] == {'block', 'ext_block'}:
                        output_dic[score_f + "_top_1_shared"][-1] = True
                    elif score_dic[top_scores[0]] == {'block'}:
                        output_dic[score_f + "_top_1_block"][-1] = True
                    else:
                        output_dic[score_f + "_top_1_ext_block"][-1] = True
                    top_3_types = reduce(lambda x, y: x.union(score_dic[y]), top_scores[:3], set())
                    if 'block' in top_3_types:
                        output_dic[score_f + "_top_3_block"][-1] = True
                    if 'ext_block' in top_3_types:
                        output_dic[score_f + "_top_3_ext_block"][-1] = True

        output_df = pd.DataFrame(output_dic)
        output_df.to_csv(output_dir + "/slice_score_stats.csv")
