# Executable Class Model Parser

Parses an *.xcm file (Executable Class Model) to yield an abstract syntax tree using python named tuples

### Why you need this

You need to process an *.xcm file in preparation for populating a database or some other purpose

### Installation

Create or use a python 3.11+ environment. Then

% pip install xcm-parser

At this point you can invoke the parser via the command line or from your python script.

#### From your python script

You need this import statement at a minimum:

    from xcm-parser.parser import ClassModelParser

You can then either specify a path or a text variable using the appropriate method:

    result = ClassModelParser.parse_text(model_text, debug=False)

OR

    result = ClassModelParser.parse_file(file_input=path_to_file, debug=False)

Check the code in `parser.py` to verify I haven't changed these parameters on you wihtout updating the readme.

In either case, `result` will be a list of parsed scrall statements. You may find the header of the `visitor.py`
file helpful in interpreting these results.

#### From the command line

This is not the intended usage scenario, but may be helpful for testing or exploration. Since the parser
may generate some diagnostic info you may want to create a fresh working directory and cd into it
first. From there...

    % xcm elevator.xcm

The .xcm extension is not necessary, but the file must contain xcm text. See this repository's wiki for
more about the xcm language. The grammar is defined in the [class_model.peg](https://github.com/modelint/scrall/blob/master/src/scrall/scrall.peg) file. (if the link breaks after I do some update to the code, 
just browse through the code looking for the scrall.peg file, and let me know so I can fix it)

You can also specify a debug option like this:

    % xcm elevator.xcm -D

This will create a scrall-diagnostics folder in your current working directory and deposite a coupel of PDFs defining
the parse of both the scrall grammar: `class_model_tree.pdf` and your supplied text: `class_model.pdf`.

You should also see a file named `xcm-parser.log` in a diagnostics directory within your working directory
