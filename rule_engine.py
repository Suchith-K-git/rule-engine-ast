class Node:
    def __init__(self, node_type: str, value: str = None, left: 'Node' = None, right: 'Node' = None):
        self.node_type = node_type  # 'operand' or 'operator'
        self.value = value           # Holds the operation or operand
        self.left = left             # Holds the left child Node
        self.right = right           # Holds the right child Node

def evaluate_rule(data: dict, ast: Node) -> bool:
    operators = {
        '==': lambda a, b: a == b,
        '!=': lambda a, b: a != b,
        '>': lambda a, b: a > b,
        '<': lambda a, b: a < b,
        '>=': lambda a, b: a >= b,
        '<=': lambda a, b: a <= b,
        'AND': lambda a, b: a and b,
        'OR': lambda a, b: a or b
    }

    if ast.node_type == 'operand':
        parts = ast.value.split()
        field = parts[0].strip()
        operator = parts[1].strip()
        value = parts[2].strip()

        if field not in data:
            raise KeyError(f"Field '{field}' not found in data.")
        
        data_value = data[field]

        if isinstance(data_value, str):
            value = value.strip("'\"")

        try:
            if isinstance(data_value, int):
                value = int(value)
            elif isinstance(data_value, float):
                value = float(value)
        except ValueError:
            raise ValueError(f"Cannot compare '{data_value}' with '{value}' due to type mismatch.")
        
        return operators[operator](data_value, value)

    elif ast.node_type == 'operator':
        left_result = evaluate_rule(data, ast.left)
        right_result = evaluate_rule(data, ast.right)
        return operators[ast.value](left_result, right_result)

def convert_dict_to_node(ast_dict: dict) -> Node:
    if ast_dict['type'] == 'operand':
        return Node(node_type='operand', value=ast_dict['value'])
    elif ast_dict['type'] == 'operator':
        left_node = convert_dict_to_node(ast_dict['left'])
        right_node = convert_dict_to_node(ast_dict['right'])
        return Node(node_type='operator', left=left_node, right=right_node, value=ast_dict['value'])
    else:
        raise ValueError("Invalid AST type")

def combine_rules(rules: list) -> dict:
    if len(rules) == 0:
        raise ValueError("No rules provided to combine.")
    
    if len(rules) == 1:
        return convert_dict_to_node({'type': 'operand', 'value': rules[0]})

    combined_ast = {
        'type': 'operator',
        'value': 'AND',
        'left': {'type': 'operand', 'value': rules[0]},
        'right': {'type': 'operand', 'value': rules[1]}
    }

    for rule in rules[2:]:
        combined_ast = {
            'type': 'operator',
            'value': 'AND',
            'left': combined_ast,
            'right': {'type': 'operand', 'value': rule}
        }

    return combined_ast
