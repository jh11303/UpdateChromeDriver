import json
import os

CURRENT_PATH = os.getcwd()
PYTHON_PATH = os.path.join(CURRENT_PATH, "venv", "Scripts", "python.exe")

if not os.path.exists(".vscode"):
    os.makedirs(".vscode")

if not os.path.exists(".vscode/settings.json"):
    with open('.vscode/settings.json', 'w') as f:
        data = {
            "python.defaultInterpreterPath": PYTHON_PATH,
        }
        json.dump(data, f, indent=4)
else:
    with open('.vscode/settings.json', 'r+') as f:
        data = json.load(f)
        if 'python.defaultInterpreterPath' not in data:
            data['python.defaultInterpreterPath'] = PYTHON_PATH
        f.seek(0)
        json.dump(data, f, indent=4)
        f.truncate()
