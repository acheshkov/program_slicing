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
