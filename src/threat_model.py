import ast
import json
import os

from openai import OpenAI
from alive_progress import alive_bar


class AIThreatModel:
    ANALYSIS_REPORT_FILENAME = "outputs/analysis_report.json"
    def __init__(self, repo_path, openai_api_key):
        self.repo_path = repo_path
        self.openai_api_key = openai_api_key
        self.analysis = []
        self.model = 'gpt-4o' #'gpt-3.5-turbo'
        self.client = OpenAI(api_key=self.openai_api_key)

    def analyze_file(self, file_path):
        with open(file_path, "r") as file:
            try:
                tree = ast.parse(file.read(), filename=file_path)
                self.collect_metadata(tree, file_path)
            except Exception as e:
                print(f"Error analyzing {file_path}: {e}")

    def collect_metadata(self, tree, file_path):
        # collect metadata about the code structure
        for node in ast.walk(tree):
            # Collect function calls
            if isinstance(node, ast.Call):
                func_name = self._get_function_name(node.func)
                self.analysis.append({
                    "file": file_path,
                    "line": node.lineno,
                    "type": "Function Call",
                    "details": {"function": func_name, "args": len(node.args)}
                })

            # collect decorator-based information (routes)
            if isinstance(node, ast.FunctionDef):
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Call):
                        decorator_name = self._get_function_name(decorator.func)
                        self.analysis.append({
                            "file": file_path,
                            "line": node.lineno,
                            "type": "Decorator",
                            "details": {"decorator": decorator_name, "function": node.name}
                        })

            # collect input/output flow (request args/form)
            if isinstance(node, ast.Attribute):
                self.analysis.append({
                    "file": file_path,
                    "line": getattr(node, "lineno", None),
                    "type": "Attribute Access",
                    "details": {"attribute": f"{node.value}.{node.attr}"}
                })

    def _get_function_name(self, node):
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{node.value.id}.{node.attr}" if hasattr(node.value, "id") else node.attr
        return "Unknown"

# TODO language support
    def analyze_repo(self):
        for root, _, files in os.walk(self.repo_path):
            for file in files:
                if file.endswith(".py"):
                    self.analyze_file(os.path.join(root, file))

        return {"analysis": self.analysis}

#TODO fix path    
    def perform_analysis(self):
        analysis_report_path = os.path.join(os.path.dirname(self.repo_path), self.ANALYSIS_REPORT_FILENAME)
        with open(analysis_report_path, "r") as f:
            analysis_results = json.load(f)
            
        try:
            print("Doing stuff...")
            analysis_content = json.dumps(analysis_results, indent=2)  # Format the JSON nicely
            user_prompt = (
                "As a security expert, find vulnerabilities in the following report:\n"
                f"{analysis_content}"
            )

            with alive_bar(spinner='dots') as bar:
                chat__completion = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "user", "content": user_prompt}
                    ])
                response_text = chat__completion.choices[0].message.content.strip()
            return  response_text

        except Exception as e:
            print(f"Error generating threat modeling with OpenAI: {str(e)}")
            return f"Error generating threat modeling: {str(e)}"
