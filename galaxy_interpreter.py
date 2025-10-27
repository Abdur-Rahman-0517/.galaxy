# galaxy_interpreter.py

import re

class GalaxyClass:
    def __init__(self, name):
        self.name = name
        self.methods = {}

class GalaxyObject:
    def __init__(self, galaxy_class):
        self.galaxy_class = galaxy_class

variables = {}
classes = {}

def run_galaxy(file_path):
    global variables, classes
    with open(file_path) as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]

    current_class = None
    inside_function = None
    function_body = []

    for line in lines:
        # Class definition
        if line.startswith("class "):
            class_name = line.split()[1]
            current_class = GalaxyClass(class_name)
            classes[class_name] = current_class
        # Function definition
        elif line.startswith("function "):
            func_name = line.split()[1].split("(")[0]
            inside_function = func_name
            function_body = []
        # End of function or class
        elif line == "}":
            if inside_function:
                current_class.methods[inside_function] = function_body
                inside_function = None
            else:
                current_class = None
        # Inside function
        elif inside_function:
            function_body.append(line)
        # Outside class
        else:
            # print statement
            if line.startswith("print("):
                msg = line[6:-1]
                # Check for variables
                for var in variables:
                    msg = msg.replace(var, str(variables[var]))
                print(msg)
            # object creation
            elif " = new " in line:
                var_name, class_name = line.split(" = new ")
                obj = GalaxyObject(classes[class_name.strip()])
                variables[var_name.strip()] = obj
            # method call
            elif "." in line and "(" in line:
                var_name, method_call = line.split(".")
                method_name = method_call.split("(")[0]
                obj = variables[var_name.strip()]
                if method_name in obj.galaxy_class.methods:
                    for method_line in obj.galaxy_class.methods[method_name]:
                        # simple print support in method
                        if method_line.startswith("print("):
                            msg = method_line[6:-1]
                            print(msg)
            # variable assignment
            elif "=" in line:
                var_name, value = line.split("=")
                variables[var_name.strip()] = eval(value.strip())
            # if condition
            elif line.startswith("if "):
                condition = line[3:-1]
                if not eval(condition, {}, variables):
                    # Skip next line (assume one-line body)
                    continue
            # for loop (1 to N)
            elif line.startswith("for "):
                match = re.match(r"for (\w+) = (\d+) to (\d+)", line)
                if match:
                    var, start, end = match.groups()
                    for i in range(int(start), int(end)+1):
                        variables[var] = i
                        # assume next line is body
                        idx = lines.index(line)
                        next_line = lines[idx+1]
                        if next_line.startswith("print("):
                            msg = next_line[6:-1].replace(var, str(i))
                            print(msg)
