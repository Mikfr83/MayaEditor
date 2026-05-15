#!/usr/bin/env python
import os
import sys

sys.path.insert(0, os.getcwd() + "/plug-ins/MayaEditorCore")
import PythonCodeModel

if __name__ == "__main__":
    model = PythonCodeModel.PythonCodeMode(sys.argv[1])
    print(f"{model.defs}")
    print(f"{model.sigs}")
    for name in model.names:
        print(f"{name.get_signatures()}")
        print(f"{name.infer()}")
        print("*****************************************")
