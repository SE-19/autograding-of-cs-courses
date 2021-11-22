def create_template(function_name, docstring, parameters):
    params = ', '.join(parameters)
    with open('assignment.py','w') as tp:
        tp.write(f"def {function_name}({params}):\n    \"\"\"{docstring}\"\"\"\n    return None\n")


function_name = "factorial"
docstring = "Returns the factorial of a number\n    The number must be zero or greater than zero."
parameters = ["num", "iter", "alpha"]

create_template(function_name, docstring, parameters)
