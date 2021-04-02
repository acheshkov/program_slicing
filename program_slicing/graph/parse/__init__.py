__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/04/02'

import program_slicing.graph.parse.cdg_java  # noqa: F401
import program_slicing.graph.parse.cfg_java  # noqa: F401
from program_slicing.graph.parse.parse import control_dependence_graph  # noqa: F401
from program_slicing.graph.parse.parse import control_flow_graph  # noqa: F401
from program_slicing.graph.parse.parse import LANG_JAVA  # noqa: F401
