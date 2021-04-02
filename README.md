# Decomposition
Set of methods for source code decomposition.
___
## Installation
1. Clone this repo.

2. ```$ git submodule update --recursive --init```

3. ```$ pip install -r requirements.txt```

You should have access to global network to use pip. Python 3 is required.

___
## Usage

This project can be used via _Command Line Interface_ or 
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
$ python main.py slice [-h]
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
$ python main.py slice MyProjectPath
```

```bash
$ python main.py slice MyFile.java
```

```bash
$ python main.py slice MyProjectPath --output MyResultPath
```

```bash
$ python main.py slice MyFile.java --output MyResultPath
```

___

### Submodule Interface

***Control Dependence Graph*** - structure that represents _Control Dependence Graph_ 
(inherited from _networkx.DiGraph_) with corresponding methods.

```python
from program_slicing.graph.cdg import ControlDependenceGraph
```

- **add_root** - mark specified node as root.
- **get_roots** - return a set of nodes that where marked as a root.

___

***Control Dependence Graph Content*** - structure that represents _Control Dependence Graph_ nodes.

```python
from program_slicing.graph.cdg_content import CDGContent
```

- **label** - string with the node's label.
- **content_type** - string with a description af the node's type.
- **ids** - a tuple with two numbers:
indexes of rhe first and the last strings of the source code where the node is presented.

___

***Control Flow Graph*** - structure that represents _Control Flow Graph_ 
(inherited from _networkx.DiGraph_) with corresponding methods.

```python
from program_slicing.graph.cfg import ControlFlowGraph
```

- **add_root** - mark specified node as root.
- **get_roots** - return a set of nodes that where marked as a root.

___

***Control Flow Graph Content*** - structure that represents _Control Flow Graph_ nodes.

```python
from program_slicing.graph.cfg_content import CFGContent
```

- **get_content** - get the content of the _Control Flow Graph_ node, i.e a list of  _Control Dependence Graph_ nodes.
- **get_root** - get the first _Control Dependence Graph_ node from the content. None if content is empty.
- **append** - add a specified _Control Dependence Graph_ node to the content.
- **is_empty** - return True if content is empty, otherwise - False.

___

***Program Graphs Manager*** - structure that contains different types of program graphs
(such as _Control Flow Graph_ or _Control Dependence Graph_) based on same source code
and provides a set of methods for their analysis.

```python
from program_slicing.graph.manager import ProgramGraphsManager
```

- **get_control_dependence_graph** - return the _Control Dependence Graph_.
- **get_control_flow_graph** - return the _Control Flow Graph_.
- **get_simple_block** - return a simple block (that is a node of the _Control Flow Graph_) 
that contains a node from the _Control Dependence Graph_.
- **init_by_control_dependence_graph** - build all the graphs by a given _Control Dependence Graph_.
- **init_by_control_flow_graph** - build all the graphs by a given _Control Flow Graph_.

___

***parse*** - set of functions that allow to parse different graphs from the specified source code string
and programming language specification.

- **control_dependence_graph** - parse a _Control Dependence Graph_:

```python
from program_slicing.graph.cdg import ControlDependenceGraph
from program_slicing.graph.parse.parse import control_dependence_graph, LANG_JAVA

cdg: ControlDependenceGraph = control_dependence_graph(source_code, LANG_JAVA)
```

- **control_flow_graph** - parse a _Control Flow Graph_:

```python
from program_slicing.graph.cfg import ControlFlowGraph
from program_slicing.graph.parse.parse import control_flow_graph, LANG_JAVA

cfg: ControlFlowGraph = control_flow_graph(source_code, LANG_JAVA)
```

___

***convert*** - there is also an option to convert one type of graph to another:

```python
from program_slicing.graph.convert.cdg import to_cfg
from program_slicing.graph.convert.cfg import to_cdg
from program_slicing.graph.cdg import ControlDependenceGraph
from program_slicing.graph.cfg import ControlFlowGraph

cdg: ControlDependenceGraph = ControlDependenceGraph()
cfg: ControlFlowGraph = to_cfg(cdg)
new_cdg: ControlDependenceGraph = to_cdg(cfg)
```
