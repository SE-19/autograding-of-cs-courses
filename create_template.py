def create_template(function_name, docstring, parameters):
    with open('./template/assignment.py','a') as tp:
        tp.write(f"def {function_name}({parameters}):\n    \"\"\"\n    {docstring}\n    \"\"\"\n    return None\n\n")

if __name__ == "__main__":
    function_name = "factorial"
    docstring = "Returns the factorial of a num"
    parameters = "num"

    create_template(function_name, docstring, parameters)
