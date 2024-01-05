#!/usr/bin/env python3

import ast
import sys
import logging

logger = logging.getLogger(__name__)


class ProtocolExtractor(ast.NodeVisitor):
    def __init__(self):
        self.current_class_name = None
        self.methods = []

    def visit_ClassDef(self, node):
        logger.info(f"Visiting class: {node.name}")
        self.current_class_name = node.name
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        self.handle_method(node, is_async=False)

    def visit_AsyncFunctionDef(self, node):
        self.handle_method(node, is_async=True)

    def handle_method(self, node, is_async):
        logger.info(
            f"Visiting {'async ' if is_async else ''}function: {node.name} in class {self.current_class_name}"
        )
        if self.current_class_name:
            params = ["self"]
            for arg in node.args.args:
                if arg.arg != "self":
                    # Include type hints if available
                    if arg.annotation:
                        arg_type = ast.unparse(arg.annotation)
                        params.append(f"{arg.arg}: {arg_type}")
                    else:
                        params.append(arg.arg)
            # Include return type if available
            return_type = "Any"
            if node.returns:
                return_type = ast.unparse(node.returns)
            params_str = ", ".join(params)
            async_prefix = "async " if is_async else ""
            self.methods.append(
                f"    {async_prefix}def {node.name}({params_str}) -> {return_type}: ..."
            )

    def create_protocol(self):
        if self.current_class_name and self.methods:
            protocol_name = f"{self.current_class_name}Protocol"
            protocol = (
                f"from typing import Protocol\n\nclass {protocol_name}(Protocol):\n"
            )
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


if __name__ == "__main__":
    if len(sys.argv) != 2:
        # print("Usage: python extract_protocol.py [FILENAME]")
        # sys.exit(1)
        filename = "/Users/littlehome/projects/risk-glass/src/open-investing/src/open_investing/strategy/data_manager/strategy_session.py"
    else:
        filename = sys.argv[1]
    protocol = extract_protocol_from_file(filename)
    if protocol:
        print(protocol)
    else:
        print("No class found to extract a protocol from.")
