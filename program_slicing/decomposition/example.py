import math
from sys import argv
from pathlib import Path
from collections import defaultdict
from typing import List, Dict, Tuple

from pebble import ProcessPool
import tqdm
import pandas as pd
from functools import reduce
from veniq.baselines.semi.recommend import recommend_for_method
from veniq.dataset_collection.augmentation import method_body_lines
from veniq.utils.encoding_detector import read_text_with_autodetected_encoding
from veniq.ast_framework import AST, ASTNodeType
from pathlib import Path
import numpy as np

from javalang import parse
from javalang.parser import JavaSyntaxError
from javalang.tokenizer import LexerError
from veniq.ast_framework import AST, ASTNodeType, ASTNode
from veniq.utils.ast_builder import build_ast

from extract_method_dataset.inline_dataset.utils import (
    method_body_lines,
    read_text_with_autodetected_encoding)
from extract_method_dataset.inline_dataset.inline_types import (
    InlineTypesAlgorithms,
    InlineWithoutReturnWithoutArguments,
    InlineWithReturnWithoutArguments,
    AlgorithmFactory)
from program_slicing.decomposition.slicing import get_complete_computation_slices
from program_slicing.graph.parse.parse import LANG_JAVA

from program_slicing.decomposition.block_slicing import get_block_slices

NUM_METHODS_PER_GROUP = 16
NUM_DISCONT_PER_GROUP = 10

LEN_RANGE_1 = [20, 35]
LEN_RANGE_2 = [40, 55]

EMO_LEN_LOWER = lambda x: x > 5
EMO_LEN_UPPER = lambda x, method_ncss: x < method_ncss * 0.8

# TODO
NUM_EMOS_RANGE_1 = lambda x: x > 1 and x <= 4
NUM_EMOS_RANGE_2 = lambda x: x > 5 and x <= 10

CC_RANGE_1 = lambda x: x in range(1, 5)
CC_RANGE_2 = lambda x: x in range(6, 100)


def _get_lines(filename, m_node):
    text = read_text_with_autodetected_encoding(filename)
    return method_body_lines(m_node, text)


def get_emos(filename, m_node):
    s_c = read_text_with_autodetected_encoding(filename).split('\n')
    start_line, end_line = method_body_lines(m_node, '\n'.join(s_c))
    m_b = s_c[int(start_line) - 1: int(end_line)]

    try:
        emos = recommend_for_method(m_b)
    except:
        return None, None

    try:
        slices = []
        for _, _, cc_slice in get_complete_computation_slices(''.join(m_b), LANG_JAVA):
            slices_list = [(x[0][0], x[1][0]) for x in cc_slice.get_ranges()]
            slices.append(slices_list)
        filtered_slices_single, filtered_slices_non_single = clean_up_slices(slices)
    except:
        return None, None

    total_emos = list(set(emos + filtered_slices_single))
    return total_emos, filtered_slices_non_singleton


def clean_up_slices(dirty_slices):
    result_single = set()
    for sl in dirty_slices:
        if len(sl) == 1:
            result_single.add(sl[0])

    result_non_single = []
    for sl in dirty_slices:
        if len(sl) > 1:
            squashed = list(set(x))
            if len(squashed) == 1:
                result_single.add(squashed[0])
            else:
                result_non_single.append(squashed)

    return list(result_single), result_non_single


def filter_cont_emos(list_emos, m_ncss):
    return [x for x in list_emos if EMO_LEN_LOWER(x[1] - x[0] + 1) and EMO_LEN_UPPER(x[1] - x[0] + 1, m_ncss)]


def filter_discont_emos(list_emos, m_ncss):
    result = []
    for x in list_emos:
        l = 0
        for p in x:
            l += p[1] - p[0] + 1
        if EMO_LEN_LOWER(l) and EMO_LEN_UPPER(l, m_ncss):
            result.append(x)

    return result


def get_data(filename: str,
             m_node: ASTNode,
             cc: int):
    result = {}
    # cc
    if CC_RANGE_1(cc):
        result['cc_range'] = 1
    elif CC_RANGE_2(cc):
        result['cc_range'] = 2
    else:
        return None

    # num emos
    cont_emos, discont_emos = get_emos(filename, m_node)
    if cont_emos is None:
        return None
    cont_emos_filtered = filter_cont_emos(cont_emos)
    discont_emos_filtered = filter_discont_emos(discont_emos)
    num_emos = len(cont_emos_filtered) + len(discont_emos_filtered)
    if NUM_EMOS_RANGE_1(num_emos):
        result['num_emos_range'] = 1
    if NUM_EMOS_RANGE_2(num_emos):
        result['num_emos_range'] = 2
    else:
        return None

    # ranges itself
    result['emos_cont'] = cont_emos_filtered
    result['emos_discont'] = discont_emos_filtered

    # discont
    result['has_disont'] = len(discont_emos_filtered)

    # scruct
    for_control_uses = list(m.get_proxy_nodes(ASTNodeType.FOR_CONTROL))
    for_statement_uses = list(m.get_proxy_nodes(ASTNodeType.FOR_STATEMENT))
    result['has_for'] = len(for_control_uses + for_statement_uses)
    while_uses = list(m.get_proxy_nodes(ASTNodeType.WHILE_STATEMENT))
    result['has_while'] = len(while_uses)
    try_uses = list(m.get_proxy_nodes(ASTNodeType.TRY_STATEMENT))
    result['has_try'] = len(try_uses)
    if_mentions = list(m.get_proxy_nodes(ASTNodeType.IF_STATEMENT))
    result['has_if'] = len(if_mentions)
    class_cr_mentions = list(m.get_proxy_nodes(ASTNodeType.CLASS_CREATOR))
    anon_classes = 0
    if class_cr_mentions:
        for x in class_cr_mentions:
            lst = list(example_ast.get_subtree(x).get_proxy_nodes(ASTNodeType.METHOD_DECLARATION))
            if lst:
                anon_classes += 1

    result['anon_class'] = anon_classes

    return result


def collect_methods(df):
    df = df.reset_index()
    NUM_SAMPLE = 1000
    shuffle_index = df.sample(frac=1, random_state=42).reset_index(drop=True)

    filename_to_methods = defaultdict(dict)

    result = []
    for ind, row in df.iterrows():
        filepath = row['File']
        m_name = row['method_name']
        m_line = row['Line']
        row = df.iloc[ind]
        сс = row['cyclo']

        if filepath not in filename_to_methods:
            example_ast = AST.build_from_javalang(build_ast(filepath))
            class_node = [node for node in ast.get_root().types
                          if node.node_type == ASTNodeType.CLASS_DECLARATION]
            filename_to_methods[filepath] = defaultdict(dict)
            for m in example_ast.get_subtree(class_node).get_proxy_nodes(
                    ASTNodeType.METHOD_DECLARATION, ASTNodeType.CONSTRUCTOR_DECLARATION):
                filename_to_methods[filepath][m.name][m_line] = m

        m_node = filename_to_methods[filepath][m_name][m_line]
        data_dict = get_data(filepath, m_node, cc)
        result.append(data_dict)

    # df = pd.DataFrame(columns=result[0].keys())
    df = pd.DataFrame(result, columns=result[0].keys())


if __name__ == "__main__":
    df = pd.read_csv(argv[1])

    df_methods_small = collect_methods(df[(df['ncss'] > LEN_RANGE_1[0]) & (df['ncss'] < LEN_RANGE_1[1])])
    df_methods_large = collect_methods(df[(df['ncss'] > LEN_RANGE_2[0]) & (df['ncss'] < LEN_RANGE_2[1])])

    df_methods_small.to_csv("methods_small.csv")
    df_methods_large.to_csv("methods_large.csv")

