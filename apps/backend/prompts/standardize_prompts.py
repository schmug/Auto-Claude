import os
import re

replacements = {
    r'(\b)Auto-Sleuth(\b)': r'\1Auto Sleuth\2',
    r'(\b)AutoClaude(\b)': r'\1Auto Sleuth\2',
    r'(\b)auto-sleuth(\b)': r'\1auto-sleuth\2',
    r'(\b)\.auto-sleuth(\b)': r'\1.auto-sleuth\2',
    r'(\b)Case Directory(\b)': r'\1Case Directory\2',
    r'(\b)case directory(\b)': r'\1case directory\2',
    r'(\b)case.md(\b)': r'\1case.md\2',
    r'(\b)CASE_DIR(\b)': r'\1CASE_DIR\2',
    r'(\b)case_dir(\b)': r'\1case_dir\2',
    r'(\b)case_file(\b)': r'\1case_file\2',
    r'(\b)case_path(\b)': r'\1case_path\2',
    r'(\b)case_folder(\b)': r'\1case_folder\2',
    r'(\b)case_name(\b)': r'\1case_name\2',
    r'(\b)investigation_plan.json(\b)': r'\1investigation_plan.json\2',
    r'(\b)investigation_plan\.json(\b)': r'\1investigation_plan.json\2',
    r'(\b)Investigation Plan(\b)': r'\1Investigation Plan\2',
    r'(\b)implementation plan(\b)': r'\1investigation plan\2',
    r'(\b)investigation_plan(\b)': r'\1investigation_plan\2',
    r'(\b)ImplementationPlan(\b)': r'\1InvestigationPlan\2',
    r'(\b)build-progress.txt(\b)': r'\1investigation-progress.txt\2',
    r'(\b)Build Progress(\b)': r'\1Investigation Progress\2',
    r'(\b)build progress(\b)': r'\1investigation progress\2',
    r'(\b)Feature(\b)': r'\1Remediation\2',
    r'(\b)feature(\b)': r'\1remediation\2',
    r'(\b)Development(\b)': r'\1Investigation\2',
    r'(\b)development(\b)': r'\1investigation\2',
}

prompts_dir = '/Users/cory/Auto-Sleuth-1/apps/backend/prompts'

for root, dirs, files in os.walk(prompts_dir):
    for file in files:
        if file.endswith('.md'):
            file_path = os.path.join(root, file)
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            new_content = content
            for pattern, replacement in replacements.items():
                new_content = re.sub(pattern, replacement, new_content)
            
            if new_content != content:
                print(f"Updating {file_path}")
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
