__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/03/23'

from program_slicing.parser import cg_java
from program_slicing.parser.cg import ControlGraph

FILE_EXT_JAVA = ".java"


def control_graph(source_code: str, file_ext: str) -> ControlGraph:
    """
    Parse the source code in a specified format into a Control Graph that contains Control Dependence and Control Flow.
    :param source_code: string with the source code in it
    :param file_ext: string with the source code format described as a file ext (like '.java' or '.xml')
    :return: Control Graph
    """
    if file_ext == FILE_EXT_JAVA:
        return cg_java.parse(source_code)
