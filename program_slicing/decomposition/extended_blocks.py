__licence__ = 'MIT'
__author__ = 'KatGarmash'
__credits__ = ['KatGarmash']
__maintainer__ = 'KatGarmash'
__date__ = '2021/09/14'

from functools import reduce
from itertools import chain, combinations_with_replacement, filterfalse, combinations
from typing import Set, Tuple, Dict, Iterable, List
from heapq import heappush, heappop

from program_slicing.decomposition.block_slicing import __percentage_or_amount_exceeded
from program_slicing.decomposition.program_slice import ProgramSlice
from program_slicing.decomposition.slice_predicate import SlicePredicate
from program_slicing.graph.cdg import ControlDependenceGraph
from program_slicing.graph.ddg import DataDependenceGraph
from program_slicing.graph.manager import ProgramGraphsManager
from program_slicing.graph.pdg import ProgramDependenceGraph
from program_slicing.graph.statement import Statement, StatementType

Block = Set[Statement]
VariableDefinition = Statement
VariableUse = Statement


def __temp__get_block_slice_statements(
        source_code: str,
        lang: str,
        slice_predicate: SlicePredicate = None,
        max_percentage_of_lines: float = None,
        may_cause_code_duplication: bool = False) -> Iterable[ProgramSlice]:
    
    source_lines = source_code.split("\n")
    manager = ProgramGraphsManager(source_code, lang)
    for scope in manager.scope_statements:
        function_statement = manager.get_function_statement(scope)
        if function_statement is None:
            continue
        function_length = function_statement.end_point.line_number - function_statement.start_point.line_number + 1
        general_statements = sorted((
            statement
            for statement in manager.get_statements_in_scope(scope)
            if statement in manager.general_statements),
            key=lambda x: (x.start_point, -x.end_point))
        id_combinations = [
            c for c in combinations_with_replacement([idx for idx in range(len(general_statements))], 2)
        ]
        for ids in id_combinations:
            current_statements = general_statements[ids[0]: ids[1] + 1]
            if not current_statements:
                continue
            if max_percentage_of_lines is not None and __percentage_or_amount_exceeded(
                    function_length,
                    current_statements[-1].end_point.line_number - current_statements[0].start_point.line_number + 1,
                    max_percentage_of_lines):
                continue
            extended_statements = manager.get_statements_in_range(
                current_statements[0].start_point,
                current_statements[-1].end_point)
            if not may_cause_code_duplication:
                affecting_statements = manager.get_affecting_statements(extended_statements)
                if len(manager.get_used_variables(affecting_statements)) > 1 or \
                        manager.contain_redundant_statements(extended_statements):
                    continue
            if len(manager.get_exit_statements(extended_statements)) > 1:
                continue
            program_slice = ProgramSlice(source_lines).from_statements(extended_statements)
            if slice_predicate is None or slice_predicate(program_slice, scopes=manager.scope_statements):
                yield extended_statements

def expand_slices_ordered(top_k=None):
    pass



def __get_incoming_variables(block_statements: Block,
                             manager: ProgramGraphsManager,
                             require_variable_declaration: bool = False
                            ) -> Dict[str, VariableUse] :
    """
    :param block_statements: block to look for variables in
    :param manager: manage for graphs of the whole program
    :return: dictionary from name of varibable in the block to a statement
            in a block that uses it and is data-dependendent on a statement
            outside the block
    """
    ddg = manager.get_data_dependence_graph()
    incoming_variables = dict()
    for statement in block_statements:
        for data_dom in ddg.predecessors(statement):
            # can be 1-many map, but it's ok for our purposes
            if data_dom not in block_statements and data_dom.name not in incoming_variables:
                if __flow_dep_given_data_dep(statement, data_dom):
                #if not require_variable_declaration:
                #    if data_dom.name == statement.name:
                #        continue
                    incoming_variables[data_dom.name] = statement
    return incoming_variables


def __get_outgoing_variables(block_statements: Block,
                             manager: ProgramGraphsManager
                             ) -> Dict[str, VariableDefinition]:
    ddg = manager.get_data_dependence_graph()
    outgoing_variables: Dict[str, VariableDefinition] = dict()
    for statement in block_statements:
        for flow_dep in set(ddg.successors(statement)).difference(block_statements):
            if __flow_dep_given_data_dep(flow_dep, statement):
                outgoing_variables[statement.name] = statement
                break
    return outgoing_variables


def __flow_dep_given_data_dep(statement_1, statement_2, variable_name = None) -> bool:
    """
    Check if statement_1 is flow-dependent on statement_2
    """
    if statement_2.statement_type not in [StatementType.ASSIGNMENT,
                                          StatementType.VARIABLE,
                                          StatementType.FUNCTION]:
        return False

    if statement_1.name != statement_2.name:
        if variable_name is not None:
            return statement_2.name == variable_name
        return True

    return False


def __compute_backward_slice_recursive(statement: Statement,
                                       variable_name: str,
                                       original_block: Set[Statement],
                                       cdg: ControlDependenceGraph,
                                       ddg: DataDependenceGraph,
                                       backward_slice: Set):
    backward_slice.add(statement)
    cdg_predecessors = cdg.predecessors(statement)
    flow_predecessors = filter(lambda x: __flow_dep_given_data_dep(statement, x, variable_name=variable_name),
                                                ddg.predecessors(statement))
    for predecessor in set(chain(cdg_predecessors, flow_predecessors)):
        if predecessor.statement_type == StatementType.FUNCTION:
            continue
        new_variable_name = None
        if predecessor in original_block:
            new_variable_name = variable_name
        __compute_backward_slice_recursive(predecessor, new_variable_name, original_block, cdg, ddg, backward_slice)


def __compute_backward_slice(variable_use: VariableUse,
                             variable_name: str,
                             original_block: Set[Statement],
                             manager: ProgramGraphsManager
                            ) -> Set[Statement]:
    backward_slice: Set[Statement] = set()
    cdg = manager.get_control_dependence_graph()
    ddg = manager.get_program_dependence_graph()
    __compute_backward_slice_recursive(variable_use, variable_name, original_block, cdg, ddg, backward_slice)
    return backward_slice


def __compute_forward_slice(variable_def: VariableDefinition,
                            manager: ProgramGraphsManager
                           ) -> Set[Statement]:
    ddg = manager.get_data_dependence_graph()
    forward_slice = set(ddg.successors(variable_def))
    return forward_slice


def __extend_block_singleton(block_statements: Block,
                             manager: ProgramGraphsManager
                            ) -> List[Tuple[Block,
                                            Dict[str, VariableUse],
                                            Dict[str, VariableDefinition],
                                            str]]:
    incoming_variables = __get_incoming_variables(block_statements, manager)
    outgoing_variables = __get_outgoing_variables(block_statements, manager)

    singleton_extensions: List[Tuple[Block,
                                     Dict[str, VariableDefinition],
                                     Dict[str, VariableUse],
                                     str]] = list()
    singleton_extensions.append((block_statements, incoming_variables, outgoing_variables, ''))

    for var_name in chain(incoming_variables.keys(), outgoing_variables.keys()):
        new_block = block_statements.copy()
        new_incoming_variables = incoming_variables.copy()
        new_outgoing_variables = outgoing_variables.copy()

        if var_name in incoming_variables:
            variable_use = incoming_variables[var_name]
            predecessor = next(manager.get_data_dependence_graph().predecessors(variable_use))
            #if predecessor.statement_type != StatementType.FUNCTION:
            if True:
                backward_slice = __compute_backward_slice(variable_use, var_name, block_statements, manager)
                new_block |= backward_slice
                del new_incoming_variables[var_name]

        if var_name in outgoing_variables:
            variable_def = outgoing_variables[var_name]
            forward_slice = __compute_forward_slice(variable_def, manager)
            new_block |= forward_slice
            del new_outgoing_variables[var_name]

        singleton_extensions.append((new_block, new_incoming_variables, new_outgoing_variables, var_name))

    return singleton_extensions


def __filter_anti_dependence(new_statements: Set, original_slice, manager):
    ddg = manager.get_data_dependence_graph()
    for statement in new_statements:
        if statement.end_point > original_slice.ranges[0][0]:
            continue
        data_successors = list(ddg.successors(statement))
        for data_successor in ddg.successors(statement):
            if data_successor.end_point > original_slice.ranges[0][0]:
                continue
            if __flow_dep_given_data_dep(data_successor, statement):
                return False

    return True


def __filter_control_dependence(new_statements: Set[Statement],
                                original_statements: Set[Statement],
                                original_slice: ProgramSlice,
                                manager: ProgramGraphsManager) -> bool:
    cdg = manager.get_control_dependence_graph()
    for statement in new_statements:
        if statement.end_point < original_slice.ranges[0][0]:
            for control_successor in cdg.successors(statement):
                if control_successor not in new_statements.union(original_statements):
                    return False
        else:
            for control_predecessor in cdg.predecessors(statement):
                if control_predecessor not in new_statements.union(original_statements):
                    return False
    return True


def __filter_more_than_one_outgoing(slice_candidate: Set[Statement],
                                    manager: ProgramGraphsManager) -> bool:
    outgoing_variables = __get_outgoing_variables(slice_candidate, manager)
    return len(outgoing_variables.keys()) <= 1


def __filter_valid(slice_candidate: Set[Statement],
                   original_statements: Set[Statement],
                   original_slice: ProgramSlice,
                   manager: ProgramGraphsManager) -> bool:
    new_statements = slice_candidate.difference(original_statements)

    # anti-dependence
    if not __filter_anti_dependence(new_statements, original_slice, manager):
        return False

    # more than 1 outgoing vars
    if not __filter_more_than_one_outgoing(slice_candidate, manager):
        return False

    # control dep
    if not __filter_control_dependence(new_statements, original_statements, original_slice, manager):
        return False

    return True


def __compute_cost(full_extension, param):
    pass


#def get_block_extensions_ordered(block_statements: Block,
#                                 manager: ProgramGraphsManager
#                                ) -> Iterable[ProgramSlice, float]:#
#
#    singleton_extensions = __extend_block_singleton(block_statements, manager)#
#
#    pq = []
#    for variable_id_subset in chain.from_iterable(combinations(singleton_extensions, r)
#                                                  for r in range(1, len(singleton_extensions) + 1)):
#        full_extension = reduce(lambda x, y: x.union(singleton_extensions[y][0]), variable_id_subset, set())
#        if __filter_valid(full_extension, block_statements, manager):
#            cost = __compute_cost(full_extension, [singleton_extensions[i] for i in variable_id_subset])
#            heappush(pq, (cost, full_extension))#
#
#    while pq:
#        yield heappop(pq)
