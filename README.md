# Decomposition
Set of methods for source code decomposition.
___
## Installation

1. ```$ git clone --recurse-submodules git@github.com:acheshkov/program_slicing.git```

2. ```$ pip3 install ./program_slicing```

You should have access to global network to use pip.
Python 3.9 with corresponding C compiler is required.
Run Python Console to check the version of C compiler.

___
## Usage

This project can be used via _Command Line Interface_, or
it can be included into any other Python project as a submodule.

### Command Line Interface

***slice***

Use this command if you want to decompose source files by
<a href="https://dl.acm.org/doi/abs/10.1016/j.jss.2011.05.016">
complete computation slice</a>
(<a href="https://dl.acm.org/profile/81100156989">Nikolaos Tsantalis</a> and
<a href="https://dl.acm.org/profile/81100540580">Alexander Chatzigeorgiou</a>.
<a href="https://en.wikipedia.org/wiki/2011">2011</a>.
<a href="https://en.wikipedia.org/wiki/Identification">Identification of</a>
<a href="https://en.wikipedia.org/wiki/Code_refactoring">extract method refactoring</a>
<a href="https://en.wikipedia.org/wiki/Opportunity">opportunities</a>
<a href="https://en.wikipedia.org/wiki/Decomposition">for the decomposition</a>
<a href="https://en.wikipedia.org/wiki/Method">of methods</a>).

```bash
$ python cli.py slice [-h]
                      [-o OUTPUT]
                      source
```

Positional arguments:

**source** - source folder, file or url

Optional arguments:

**-o**, **--output** OUTPUT -
output file or directory: depending on what you set as output, 
you will get folder full of slice decompositions or a single file with it.
It uses stdout if not specified

**-h**, **--help** - show this help message and exit

Examples:
```bash
$ python cli.py slice MyProjectPath
```

```bash
$ python cli.py slice MyFile.java
```

```bash
$ python cli.py slice MyProjectPath --output MyResultPath
```

```bash
$ python cli.py slice MyFile.java --output MyResultPath
```

___

### Submodule Interface

***Control Dependence Graph*** - structure that represents _Control Dependence Graph_ 
(inherited from _networkx.DiGraph_) with corresponding methods.

```python
from program_slicing.graph.cdg import ControlDependenceGraph
```

- **add_entry_point** - mark specified node as entry point.
- **get_entry_points** - return a set of nodes that where marked as an entry point.

___

***Control Flow Graph*** - structure that represents _Control Flow Graph_ 
(inherited from _networkx.DiGraph_) with corresponding methods.

```python
from program_slicing.graph.cfg import ControlFlowGraph
```

- **add_entry_point** - mark specified node as entry point.
- **get_entry_points** - return a set of nodes that where marked as an entry point.

___

***Data Dependence Graph*** - structure that represents _Data Dependence Graph_
(inherited from _networkx.DiGraph_) with corresponding methods.

```python
from program_slicing.graph.ddg import DataDependenceGraph
```

- **add_entry_point** - mark specified node as entry point.
- **get_entry_points** - return a set of nodes that where marked as an entry point.

___

***Program Dependence Graph*** - structure that represents _Program Dependence Graph_
(inherited from _networkx.DiGraph_) with corresponding methods.

```python
from program_slicing.graph.pdg import ProgramDependenceGraph
```

- **add_entry_point** - mark specified node as entry point.
- **get_entry_points** - return a set of nodes that where marked as an entry point.

___

***Statement*** - structure that represents _Control Dependence Graph_, _Data Dependence Graph_ or
_Program Dependence Graph_ nodes.

```python
from program_slicing.graph.statement import Statement
```

- **statement_type** - _StatementType_ object.
- **start_point** - line and column numbers of the _Statement's_ start.
- **end_point** - line and column numbers of the _Statement's_ end.
- **affected_by** - set of strings with names of variables that may affect the current _Statement_.
- **name** - string with the name of the _Statement_. Not all _Statements_ are named.
- **ast_node_type** - string with additional information about node (e.g. an AST root's class).

___

***StatementType*** - structure that enumerates _Statement_ types.

```python
from program_slicing.graph.statement import StatementType
```

- **FUNCTION** - function declaration _Statement_.
- **VARIABLE** - variable declaration _Statement_.
- **ASSIGNMENT** - variable assignment _Statement_ (such as `i = 0`, `i += 1`, `i++`, etc).
- **CALL** - function call _Statement_.
- **SCOPE** - scope _Statement_ (such as braces `{}` or empty body in `if (...) a = 0`).
- **BRANCH** - _Statement_ that branches the flow (such as `if`, `try`, `catch`, `switch`).
- **LOOP** - branch _Statement_ that generates backward flow (such as `for` and `while`).
- **GOTO** - _Statement_ that lead flow to a concrete _Statement_ 
  (such as `break`, `continue`, `throw`, `return` and even `else`).
- **UNKNOWN** - all the other _Statements_.
- **EXIT** - special _Statement_ that is placed in the end of function declaration, has zero size and 
  all the 'return' and 'throw' nodes leads flow into it (as well as the last _Statement_ in the flow).

___

***Basic Block*** - structure that represents _Control Flow Graph_ nodes.

```python
from program_slicing.graph.basic_block import BasicBlock
```

- **statements** - get the content of the _Basic Block_, i.e a list of  _Statements_.
- **root** - get the first _Statement_ from the _Basic Block_. None if it is empty.
- **append** - add a specified _Statement_ to the _Basic Block_.
- **is_empty** - return True if there are no statements in the _Basic Block_, otherwise - False.
- **split** - split content by the given index, left first part of the split at the original _Basic Block_
  and return a new _Basic Block_ which contains all the rest _Statements_.

___

***Program Graphs Manager*** - structure that contains different types of program graphs
(such as _Control Flow Graph_ or _Control Dependence Graph_) based on same source code
and provides a set of methods for their analysis.

```python
from program_slicing.graph.parse import LANG_JAVA
from program_slicing.graph.parse import control_dependence_graph
from program_slicing.graph.parse import control_flow_graph
from program_slicing.graph.manager import ProgramGraphsManager

manager_by_source = ProgramGraphsManager(source_code, LANG_JAVA)

manager_by_cdg = ProgramGraphsManager.from_control_dependence_graph(control_dependence_graph(source_code, LANG_JAVA))

manager_by_cfg = ProgramGraphsManager.from_control_flow_graph(control_flow_graph(source_code, LANG_JAVA))
```
****Properties:****

- **control_dependence_graph** - return the _Control Dependence Graph_.
- **control_flow_graph** - return the _Control Flow Graph_.
- **data_dependence_graph** - return the _Data Dependence Graph_.
- **program_dependence_graph** - return the _Program Dependence Graph_.
- **sorted_statements** - return _Statements_ that are sorted first by increasing of their `start_point`,
  then by decreasing of their `end_point`.
- **general_statements** - return general _Statements_ 
  (those which are not contained in any non `SCOPE`, `BRANCH`, `LOOP`, `FUNCTION` or `EXIT` _Statement_).
- **scope_statements** - return all the `SCOPE`, `BRANCH`, `LOOP` or `FUNCTION` _Statements_.

****Public methods:****

- **get_basic_block** - return a _Basic Block_ (that is a node of the _Control Flow Graph_)
  that contains a given _Statement_.
- **get_boundary_blocks** - return a set of _Basic Blocks_ which intersection of dominated and reach blocks
  contain the given one block.
- **get_boundary_blocks_for_statement** - return a set of boundary blocks for _Basic Block_
  in which the given _Statement_ is placed.
- **get_dominated_blocks** return a set of _Basic Blocks_ that are dominated by the given one (i.e. their
  _Statements_ are placed in a _control Dependence Graph_ subtree of the root of the given _Basic Block_).
- **get_reach_blocks** - return a set of _Basic Blocks_ that are reachable 
  from the given one in the _Control Flow Graph_.
- **get_statement_line_numbers** - return a set of line numbers in which the given _Statement_ is placed.
- **get_function_statement** - return the minimal `FUNCTION` _Statement_ in which the given _Statement_ is placed.
- **get_function_statement_by_range** - return the minimal FUNCTION _Statement_ in which the given range is placed.
- **get_scope_statement** - return a minimal 'scope-like' (`SCOPE`, `LOOP`, `BRANCH`) _Statement_
  that contains a given _Statement_.
- **get_statements_in_scope** - return all the _Statements_ in the given scope _Statement_.
- **get_statements_in_range** - return all the _Statements_ in the given range.
- **get_exit_statements** - return _Statements_ that are _Flow Dependence_ children of the given statements 
  but not one of them.
- **get_affecting_statements** - return _Statements_ from the given set of _Statements_ that affect 
  some _Statement_ not form the given set.
- **get_changed_variables** - return `VARIABLE` _Statements_ that represent variables changed 
  in the given set of _Statements_.
- **get_involved_variables** - return `VARIABLE` _Statements_ that represent variables involved (including usage) 
  in the given set of _Statements_.
- **contain_redundant_statements** - check if the given set of _Statements_ contain part of some construction 
  not fully included in the given set.

****Class methods:****

- **from_source_code** - build all the graphs by a given source code string and a language description.
- **from_control_dependence_graph** - build all the graphs by a given _Control Dependence Graph_.
- **from_control_flow_graph** - build all the graphs by a given _Control Flow Graph_.
- **from_data_dependence_graph** - build all the graphs by a given _Data Dependence Graph_.
- **from_program_dependence_graph** - build all the graphs by a given _Program Dependence Graph_.
___

***parse*** - set of functions that allow to build different graphs from the specified source code string
and programming language specification.

- **control_dependence_graph** - parse a _Control Dependence Graph_:

```python
from program_slicing.graph.cdg import ControlDependenceGraph
from program_slicing.graph.parse import control_dependence_graph, LANG_JAVA

cdg: ControlDependenceGraph = control_dependence_graph(source_code, LANG_JAVA)
```

- **control_flow_graph** - parse a _Control Flow Graph_:

```python
from program_slicing.graph.cfg import ControlFlowGraph
from program_slicing.graph.parse import control_flow_graph, LANG_JAVA

cfg: ControlFlowGraph = control_flow_graph(source_code, LANG_JAVA)
```

- **data_dependence_graph** - parse a _Data Dependence Graph_:

```python
from program_slicing.graph.ddg import DataDependenceGraph
from program_slicing.graph.parse import data_dependence_graph, LANG_JAVA

ddg: DataDependenceGraph = data_dependence_graph(source_code, LANG_JAVA)
```

- **program_dependence_graph** - parse a _Program Dependence Graph_:

```python
from program_slicing.graph.pdg import ProgramDependenceGraph
from program_slicing.graph.parse import program_dependence_graph, LANG_JAVA

pdg: ProgramDependenceGraph = program_dependence_graph(source_code, LANG_JAVA)
```

___

***convert*** - there is also an option to convert one type of graph to another:

```python
from program_slicing.graph import convert
from program_slicing.graph.cdg import ControlDependenceGraph
from program_slicing.graph.cfg import ControlFlowGraph

cdg: ControlDependenceGraph = ControlDependenceGraph()
cfg: ControlFlowGraph = convert.cdg.to_cfg(cdg)
new_cdg: ControlDependenceGraph = convert.cfg.to_cdg(cfg)
```
