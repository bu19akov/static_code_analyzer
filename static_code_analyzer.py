import re
import sys
from os import path, listdir, chdir
import ast


class StaticCodeAnalyzer:

    def __init__(self):
        self.errors = ("S001 Too long", "S002 Indentation is not a multiple of four", "S003 Unnecessary semicolon",
                       "S004 At least two spaces required before inline comments", "S005 TODO found",
                       "S006 More than two blank lines used before this line", "S007 Too many spaces after param")
        self.found_errors = dict()
        self.current_file = None

    def check_length(self, num, line):
        if len(line) > 79:
            print(f"{self.current_file}: Line {num}: S001 Too long")

    def check_indent(self, num, line):
        counter = 0
        for i in line:
            if i == " ":
                counter += 1
            else:
                break
        if counter % 4 != 0:
            print(f"{self.current_file}: Line {num}: S002 Indentation is not a multiple of four")

    def check_semicolon(self, num, line):
        line = line.split("#")[0]
        comments = re.findall("'.*'", line)
        for c in comments:
            line = line.replace(c, "")
        if ";" in line:
            print(f"{self.current_file}: Line {num}: S003 Unnecessary semicolon")

    def two_spaces(self, num, line):
        line = line[:line.find("#") + 1]
        for i in range(len(line)):
            if line[i] == "#" and i != 0 and (line[i - 1] != " " or line[i - 2] != " "):
                print(f"{self.current_file}: Line {num}: S004 At least two spaces required before inline comments")

    def todo(self, num, line):
        line = line[line.find("#"):]
        if "todo" in line.lower():
            print(f"{self.current_file}: Line {num}: S005 TODO found")

    def class_spaces(self, num, line):
        if "class" in line:
            line = line.split("class")
            if line[1].startswith("  "):
                print(f"{self.current_file}: Line {num}: S007 Too many spaces after class")
        elif "def" in line:
            line = line.split("def")
            if line[1].startswith("  "):
                print(f"{self.current_file}: Line {num}: S007 Too many spaces after def")

    def camel_case(self, num, line):
        if "class" in line:
            line = line.split("class")
            line[1] = line[1].replace(line[1][line[1].find("("):], "").replace(":", "")
            if not re.match(" *([A-Z]+[a-z]+)+", line[1]):
                print(f"{self.current_file}: Line {num}: S008 Class name {line[1]} should be written in CamelCase")

    def snake_case(self, num, line):
        if "def" in line:
            line = line.split("def")
            line[1] = line[1].replace(line[1][line[1].find("("):], "")
            if not re.match(" *_*([a-z]+(_[a-z]+)*)+_*", line[1]):
                print(f"{self.current_file}: Line {num}: S009 Function name {line[1]} should be written in snake_case")

    def check_args(self, path):
        file = open(path, "r")
        code = file.read()
        file.close()
        tree = ast.parse(code)
        nodes = ast.walk(tree)
        variables = []
        for n in nodes:
            if isinstance(n, ast.FunctionDef):
                for arg in [a.arg for a in n.args.args]:
                    if not re.match(" *_*([a-z]+(_[a-z]+)*)+_*", arg):
                        print(f"{self.current_file}: Line {n.lineno}: S010 Argument name {arg} should be written in snake_case")
                for item in n.args.defaults:
                    if isinstance(item, ast.List):
                        print(f"{self.current_file}: Line {n.lineno}: S012 The default argument value is mutable")
            if isinstance(n, ast.Name):
                if not re.match(" *_*([a-z]+(_[a-z]+)*)+_*", n.id) and n.id not in variables:
                    print(f"{self.current_file}: Line {n.lineno}: S011 Variable {n.id} should be written in snake_case")
                    variables.append(n.id)

    def check_files(self):
        args = sys.argv
        file_path = args[1]
        if path.isfile(file_path) and file_path.endswith(".py"):
            self.current_file = file_path
            self.check_errors(file_path)
            self.check_args(file_path)
        elif path.isdir(file_path):
            chdir(file_path)
            files = sorted(listdir(file_path))
            for file in files:
                if path.isfile(file) and file.endswith(".py") and file != "tests.py":
                    self.current_file = file_path + "/" + file
                    self.check_errors(file)
                    self.check_args(file)

    def check_errors(self, cl_file):
        with open(cl_file, "r") as file:
            counter = 0
            for num, line in enumerate(file, start=1):
                line = line.rstrip("\n")
                self.check_length(num, line)
                self.check_indent(num, line)
                self.check_semicolon(num, line)
                self.two_spaces(num, line)
                self.todo(num, line)
                if counter >= 3 and line.strip() != "":
                    print(f"{self.current_file}: Line {num}: S006 More than two blank lines used before this line")
                    counter = 0
                if line.strip() == "":
                    counter += 1
                else:
                    counter = 0
                self.class_spaces(num, line)
                self.camel_case(num, line)
                self.snake_case(num, line)


s = StaticCodeAnalyzer()
s.check_files()

