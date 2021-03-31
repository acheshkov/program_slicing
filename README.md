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

This project may be used via _Command Line Interface_ or 
it may be used in an outer Python project as a submodule.

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

***Control Graph*** - structure that represents _Control Flow Graph_ and _Control Dependency Graph_ relations
with corresponding getters.

```python
from program_slicing.parse.cg import ControlGraph
```

- **get_root_node** - return the root node of a _Control Dependency Graph_.
- **get_root_blocks** - return a list of root blocks of a _Control Flow Graph_.
Each _Function Declaration_ contains its own _Control Flow Graph_ with its own root.

___

***Control Flow Graph*** - structure that represents _Control Flow Graph_ 
(inherited from _Control Graph_) with corresponding methods.

```python
from program_slicing.parse.cfg import ControlFlowGraph
```

- **get_reach** - return a set of blocks that are reachable from the specified block.

___

***Control Dependency Graph*** - structure that represents _Control Dependency Graph_ 
(inherited from _Control Graph_) with corresponding methods.

```python
from program_slicing.parse.cdg import ControlDependencyGraph
```

- **get_dom** - return a set of blocks that are recursively dominated by a parent node of a specified block.

___

***parse*** - set of functions that allow to parse different graphs from the specified source code string
and programming language specification.

- **control_graph** - parse a _Control Graph_:

```python
from program_slicing.parse.parse import control_graph, FILE_EXT_JAVA

cg: ControlGraph = control_graph(source_code, FILE_EXT_JAVA)
```

- **control_flow_graph** - parse a _Control Flow Graph_:

```python
from program_slicing.parse.parse import control_flow_graph, FILE_EXT_JAVA

cfg: ControlFlowGraph = control_flow_graph(source_code, FILE_EXT_JAVA)
```

- **control_dependency_graph** - parse a _Control Dependency Graph_:

```python
from program_slicing.parse.parse import control_dependency_graph, FILE_EXT_JAVA

cdg: ControlDependencyGraph = control_dependency_graph(source_code, FILE_EXT_JAVA)
```

***cast*** - there is also an option to cast one type of graph to another:

```python
from program_slicing.parse.cg import ControlGraph
from program_slicing.parse.cfg import ControlFlowGraph
from program_slicing.parse.cdg import ControlDependencyGraph
from program_slicing.parse.parse import control_graph, FILE_EXT_JAVA

cg: ControlGraph = control_graph(source_code, FILE_EXT_JAVA)
cfg: ControlFlowGraph = ControlFlowGraph(cg)
cdg: ControlDependencyGraph = ControlDependencyGraph(cfg)
```
