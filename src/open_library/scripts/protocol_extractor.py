#!/usr/bin/env python3

import ast
import sys


class ProtocolExtractor(ast.NodeVisitor):
    def __init__(self):
        self.current_class_name = None
        self.methods = []

    def visit_ClassDef(self, node):
        self.current_class_name = node.name
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        if self.current_class_name:
            params = ", ".join(arg.arg for arg in node.args.args if arg.arg != "self")
            self.methods.append(f"    def {node.name}({params}): ...")
        self.generic_visit(node)

    def create_protocol(self):
        if self.current_class_name and self.methods:
            protocol_name = f"{self.current_class_name}Protocol"
            protocol = f"class {protocol_name}(Protocol):\n"
            for method in self.methods:
                protocol += method + "\n"
            return protocol
        return ""


class ProtocolExtractor(ast.NodeVisitor):
    def __init__(self):
        self.current_class_name = None
        self.methods = []

    def visit_ClassDef(self, node):
        self.current_class_name = node.name
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        if self.current_class_name and isinstance(node, ast.FunctionDef):
            params = []
            for arg in node.args.args:
                if arg.arg != "self":
                    # Include type hints if available
                    if arg.annotation:
                        arg_type = ast.unparse(arg.annotation)
                        params.append(f"{arg.arg}: {arg_type}")
                    else:
                        params.append(arg.arg)
            params_str = ", ".join(params)
            self.methods.append(f"    def {node.name}({params_str}) -> Any: ...")
        self.generic_visit(node)

    def create_protocol(self):
        if self.current_class_name and self.methods:
            protocol_name = f"{self.current_class_name}Protocol"
            protocol = f"class {protocol_name}(Protocol):\n"
            for method in self.methods:
                protocol += method + "\n"
            return protocol
        return ""


def extract_protocol_from_file(filename):
    with open(filename, "r") as file:
        tree = ast.parse(file.read(), filename=filename)

    extractor = ProtocolExtractor()
    extractor.visit(tree)
    return extractor.create_protocol()


# protocol = extract_protocol_from_file("order.py")
# print(protocol)

# if __name__ == "__main__":
#     if len(sys.argv) != 2:
#         filename = "order.py"
#         # print("Usage: python extract_protocol.py [FILENAME]")
#         # sys.exit(1)

#     filename = sys.argv[1]
#     protocol = extract_protocol_from_file(filename)
#     if protocol:
#         print(protocol)
#     else:
#         print("No class found to extract a protocol from.")
