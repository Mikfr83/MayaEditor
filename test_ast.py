#!/usr/bin/env python
import ast
import sys
from collections import namedtuple

code_model_data = namedtuple("CodeModel", "type line_number name")
class_model_data = namedtuple("Class", "name line_number")
is_class = False


def extract_classes_and_functions(node_to_traverse, current_object):
    global is_class
    for node in node_to_traverse.body:
        if isinstance(node, ast.ClassDef):
            is_class = True
            current_object.append({class_model_data(node.name, node.lineno): []})
            extract_classes_and_functions(
                node, current_object[-1:][0][class_model_data(node.name, node.lineno)]
            )
            is_class = False
        if isinstance(node, ast.FunctionDef):
            func = "function"
            if is_class:
                func = "method"
            current_object.append(
                code_model_data(type=func, line_number=node.lineno, name=node.name)
            )


file = open(sys.argv[1], "r")
f = file.read()
node_to_traverse = ast.parse(f)
class_and_functions = []


extract_classes_and_functions(node_to_traverse, class_and_functions)
# pprint.pprint(class_and_functions)
for item in class_and_functions:
    if isinstance(item, code_model_data):
        print("Functions :")
        print(item)
    elif isinstance(item, dict):
        class_info = list(item.keys())[0]
        print(f"class {class_info.name} {class_info.line_number}")
        methods = list(item.values())
        for m in methods[0]:
            print(m)
