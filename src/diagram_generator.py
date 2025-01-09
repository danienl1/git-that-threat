import os
import ast

class DiagramGenerator:
    def __init__(self, repo_path):
        self.repo_path = repo_path
        self.file_dependencies = {}
        self.function_calls = {}
        self.routes = {}

    def scan_files(self):
        for root, _, files in os.walk(self.repo_path):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    try:
                        dependencies, calls, routes = self.analyze_file(file_path)  # Handle three values
                        self.file_dependencies[file_path] = dependencies
                        self.function_calls[file_path] = calls
                        self.routes[file_path] = routes
                    except Exception as e:
                        print(f"Failed to parse {file_path}: {e}")


    def analyze_file(self, file_path):
        with open(file_path, "r") as file:
            try:
                tree = ast.parse(file.read())
                dependencies = self.extract_dependencies(tree)
                calls, routes = self.extract_function_calls(tree)
                return dependencies, calls, routes
            except Exception as e:
                print(f"Failed to parse {file_path}: {e}")
                return [], [], []


    def extract_dependencies(self, tree):
        dependencies = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    dependencies.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                dependencies.append(module)
        return dependencies

    def extract_function_calls(self, tree):
        calls = []
        routes = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    calls.append(node.func.id)  # Direct function calls
                elif isinstance(node.func, ast.Attribute):
                    # Handle attributes like object.method()
                    value = getattr(node.func.value, "id", None)  # Check if value has an 'id' attribute
                    if value:
                        calls.append(f"{value}.{node.func.attr}")  # Object.method() calls
            elif isinstance(node, ast.FunctionDef):  # Check for decorators
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Attribute):
                        if decorator.func.attr == "route":  # Flask route
                            # Extract route URL from the decorator arguments
                            if decorator.args and isinstance(decorator.args[0], ast.Str):
                                routes.append({"route": decorator.args[0].s, "handler": node.name})

        return calls, routes

    def generate_mermaid(self):
        diagram = "```mermaid\nflowchart TD\n"

        # Initialization block
        diagram += "subgraph Initialization\n"
        diagram += "    init[\"Initialize Flask App\"]\n"
        diagram += "    init --> flask[\"Import Flask\"]\n"
        diagram += "    init --> sqlalchemy[\"Setup SQLAlchemy\"]\n"
        diagram += "    init --> cors[\"Setup CORS\"]\n"
        diagram += "end\n"

        # Routes block
        if any(routes for routes in self.routes.values()):
            diagram += "subgraph Routes\n"
            for file, routes in self.routes.items():
                for route in routes:
                    route_id = route["route"].replace("/", "_").replace("<", "_").replace(">", "_").replace("-", "_")
                    handler_id = route["handler"].replace(" ", "_")
                    diagram += f"    {route_id}[\"Route: {route['route']}\"] --> {handler_id}[\"Handler: {route['handler']}\"]\n"
            diagram += "end\n"

        # Models block
        diagram += "subgraph Models\n"
        diagram += "    models[\"Define Models\"]\n"
        diagram += "    models --> db_column[\"db.Column\"]\n"
        diagram += "    models --> db_foreignkey[\"db.ForeignKey\"]\n"
        diagram += "end\n"

        # Main workflow
        diagram += "main[\"Main Entry Point\"] --> run_app[\"Run Flask App\"]\n"
        diagram += "main --> init_db[\"Initialize Database\"]\n"
        diagram += "run_app --> Routes\n"
        diagram += "Routes --> Models\n"
        diagram += "Routes --> BusinessLogic[\"Business Logic\"]\n"

        diagram += "```\n"
        return diagram



    def save_mermaid_file(self, diagram, output_path="architecture_diagram.md"):
        with open(output_path, "w") as file:
            file.write(diagram)

    def run(self):
        self.scan_files()
        diagram = self.generate_mermaid()
        self.save_mermaid_file(diagram)
        print("Architecture diagram saved to architecture_diagram.md")


    