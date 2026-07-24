# Executable Class Model Parser

<p align="center">
  <img src="https://raw.githubusercontent.com/modelint/xcm-parser/main/docs/images/xcm_parser.png"
       alt="Parses an .xcm executable class model file into an abstract syntax tree for downstream Blueprint modules"
       width="720">
</p>

Parses an *.xcm file (Executable Class Model) to yield an abstract syntax tree using python named tuples

### Why you need this

You need to process an *.xcm file in preparation for populating a database or some other purpose

### Installation

Create or use a python 3.11+ environment. Then

% pip install xcm-parser

At this point you can invoke the parser via the command line or from your python script.

#### From your python script

You need this import statement at a minimum:

    from xcm_parser.class_model_parser import ClassModelParser

You can then specify a path as shown:

    result = ClassModelParser.parse_file(file_input=path_to_file, debug=False)

In either case, `result` will be a `Subsystem_a` named tuple holding the parsed class model elements
(`subsystem`, `domain`, `classes`, `rels`, and `metadata`). You may find the header of the
`class_model_visitor.py` file helpful in interpreting these results.

#### From the command line

This is not the intended usage scenario, but may be helpful for testing or exploration. Since the parser
may generate some diagnostic info you may want to create a fresh working directory and cd into it
first. From there...

    % xcm elevator.xcm

The .xcm extension is not necessary, but the file must contain xcm text. See this repository's wiki for
more about the xcm language. The grammar is defined in the [class_model.peg](https://github.com/modelint/xcm-parser/blob/main/src/xcm_parser/class_model.peg) file. (if the link breaks after I do some update to the code, 
just browse through the code looking for the class_model.peg file, and let me know so I can fix it)

You can also specify a debug option like this:

    % xcm elevator.xcm -D

This will create a `diagnostics` folder in your current working directory and deposit a couple of PDFs defining
the parse of both the class model grammar: `class_model.pdf` and your supplied text: `class_parse_tree.pdf`.

You should also see a file named `xcm_parser.log` in your current working directory
