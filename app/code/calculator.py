# -*- coding: utf-8 -*-
"""
File: calculator.py
Authors: Veaceslav Kunitki<tumikosha@fmail.com>
Description: This is module for simple & safe math calculations.
"""
import ast
from typing import Tuple

ALLOWED_NAMES_AND_OPS = {'abs', "len", "+", "-", "*", "/"}


# EXPRESSION PARSING SERVICE FUNCTIONS
def is_builtin_function(node) -> bool:
    """check if func has is builtin name"""
    return isinstance(node, ast.Name) and node.id in dir(__builtins__)


def get_variables(expression) -> list[str]:
    """walker for extract all names from expression"""
    tree = ast.parse(expression)
    variables = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            # if isinstance(node, ast.Constant):
            variables.append(node.id)
            pass

    # return tuple(v for v in set(variables) if v not in vars(builtins))
    return [v for v in set(variables)]


def get_function_names(code) -> list[str]:
    """Walker for extract all function names  from expression"""
    tree = ast.parse(code)
    # all_names = [node.id for node in ast.walk(tree) if isinstance(node, ast.Name) and node.id]
    all_names = [node.id for node in ast.walk(tree) if isinstance(node, ast.Name)]
    builtin_function_names = [node.id for node in ast.walk(tree) if
                              isinstance(node, ast.Name) and node.id in dir(__builtins__)]
    non_builtin_function_names = [node.id for node in ast.walk(tree) if
                                  isinstance(node, ast.Name) and node.id not in dir(__builtins__)]
    return all_names  # , builtin_function_names, non_builtin_function_names


def get_operations(code: str) -> list[str]:
    """
    Walker for extract all operations and their symbols from a given Python code string.

    Parameters:
    - code (str): Python code string.

    Returns:
    - list: List of operation_symbol.
    """
    # Parse the code string into an abstract syntax tree (AST)
    tree = ast.parse(code)

    # Helper function to extract information about operations
    def extract_operation(node_):
        if isinstance(node, (ast.BinOp, ast.UnaryOp, ast.Compare)):
            operation_symbol = get_operation_symbol(node_)
            operands = get_operands(node_)
            # operations.append((operation_symbol, operands))
            operations.append(operation_symbol)

    def get_operation_symbol(op_node):
        if isinstance(op_node, ast.BinOp):
            return get_binary_operation_symbol(op_node.op)
        elif isinstance(op_node, ast.UnaryOp):
            return get_unary_operation_symbol(op_node.op)
        elif isinstance(op_node, ast.Compare):
            return get_comparison_operation_symbol(
                op_node.ops[0])  # For simplicity, considering only the first comparison

    def get_binary_operation_symbol(op_node):
        if isinstance(op_node, ast.Add):
            return '+'
        elif isinstance(op_node, ast.Sub):
            return '-'
        elif isinstance(op_node, ast.Mult):
            return '*'
        elif isinstance(op_node, ast.Div):
            return '/'
        # Add more cases for other binary operation types as needed

    def get_unary_operation_symbol(op_node):
        if isinstance(op_node, ast.UAdd):
            return '+'
        elif isinstance(op_node, ast.USub):
            return '-'
        # Add more cases for other unary operation types as needed

    def get_comparison_operation_symbol(op_node):
        if isinstance(op_node, ast.Eq):
            return '=='
        elif isinstance(op_node, ast.NotEq):
            return '!='
        elif isinstance(op_node, ast.Lt):
            return '<'
        elif isinstance(op_node, ast.LtE):
            return '<='
        elif isinstance(op_node, ast.Gt):
            return '>'
        elif isinstance(op_node, ast.GtE):
            return '>='
        # Add more cases for other comparison operation types as needed

    def get_operands(op_node):
        if isinstance(op_node, ast.BinOp):
            return (ast.dump(op_node.left), ast.dump(op_node.right))
        elif isinstance(op_node, ast.UnaryOp):
            return (ast.dump(op_node.operand),)
        elif isinstance(op_node, ast.Compare):
            return tuple(ast.dump(operand) for operand in op_node.comparators)

    operations = []

    # Traverse the AST and extract operation information
    for node in ast.walk(tree):
        extract_operation(node)

    return operations


def check(code_: str) -> Tuple[bool, set]:
    """ check if expression contains only allowed symbols"""
    names_and_ops = set(get_operations(code_) + get_function_names(code_) + get_variables(code_))
    diff = names_and_ops.difference(ALLOWED_NAMES_AND_OPS)
    if len(diff) > 0:
        return False, set(diff)
    else:
        return True, set()


def calculate_expression(expression: str) -> Tuple[bool, str]:
    """ do math
    return:  Tuple(have_error, result)
    where
        have_error:bool - error Flag
        result:str -  operation result or error message
    Usage: calculate_expression("2+2") ->(False, "4")
    Usage: calculate_expression("2+QQQQ") ->(True, "Undefined words: {'QQQQ'}")

    """
    try:
        is_good, wrong_names = check(expression)
        if not is_good:
            return True, "Undefined words: " + str(wrong_names)

        return False, eval(expression)
    except Exception as e:
        return True, "Error: " + str(e)
