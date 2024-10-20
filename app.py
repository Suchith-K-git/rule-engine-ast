from flask import Flask, request, jsonify
import pyodbc
from rule_engine import evaluate_rule, convert_dict_to_node, combine_rules

app = Flask(__name__)

# Database connection setup
def get_db_connection():
    return pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=DESKTOP-605868F\\SQLEXPRESS;'
        'DATABASE=Python;'
        'Trusted_Connection=yes;'
    )

@app.route('/')
def index():
    return "Welcome to the Flask Rule Engine API!"

@app.route('/create_rule', methods=['POST'])
def create_rule_api():
    rule_string = request.json.get('rule_string')
    if not rule_string:
        return jsonify({"error": "Rule string is required"}), 400

    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO dbo.rules (rule_name, rule_string) VALUES (?, ?)", 
                       ("default_rule_name", rule_string))
        connection.commit()
    except Exception as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        cursor.close()
        connection.close()

    return jsonify({"message": "Rule created successfully!"})

@app.route('/evaluate_rule', methods=['POST'])
def evaluate_rule_api():
    ast_dict = request.json.get('ast')
    data = request.json.get('data')

    if ast_dict is None or data is None:
        return jsonify({"error": "AST and data are required"}), 400

    try:
        ast = convert_dict_to_node(ast_dict)
    except Exception as e:
        return jsonify({"error": f"Error converting AST: {str(e)}"}), 400

    valid, error_message = validate_data(data, ast)
    if not valid:
        return jsonify({"error": error_message}), 400

    try:
        result = evaluate_rule(data, ast)
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": "An error occurred during rule evaluation: " + str(e)}), 500

@app.route('/combine_rules', methods=['POST'])
def combine_rules_api():
    rules = request.json.get('rules')
    if not rules or not isinstance(rules, list):
        return jsonify({"error": "A list of rule strings is required"}), 400
    
    try:
        combined_ast = combine_rules(rules)
        return jsonify({"combined_ast": combined_ast})
    except Exception as e:
        return jsonify({"error": f"Error combining rules: {str(e)}"}), 500

def validate_data(data, ast):
    required_attributes = get_required_attributes(ast)
    missing_attributes = required_attributes - data.keys()
    
    if missing_attributes:
        return False, f"Missing attributes: {', '.join(missing_attributes)}"
    
    return True, None

def get_required_attributes(ast):
    required_attributes = set()

    if ast.node_type == 'operand':
        field = ast.value.split()[0].strip()
        required_attributes.add(field)
    
    elif ast.node_type == 'operator':
        required_attributes.update(get_required_attributes(ast.left))
        required_attributes.update(get_required_attributes(ast.right))

    return required_attributes

if __name__ == '__main__':
    app.run(debug=True)
