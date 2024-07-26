import os
import shutil

def delete_folders(folder_name, exclude=None):
    exclude = exclude or []
    for root, dirs, files in os.walk('.'):
        for dir in dirs:
            if dir == folder_name and all(exc not in root for exc in exclude):
                folder_path = os.path.join(root, dir)
                print(f"Deleting folder: {folder_path}")
                shutil.rmtree(folder_path)

# Διαγραφή των __pycache__ φακέλων, εκτός από συγκεκριμένους καταλόγους
delete_folders('__pycache__', exclude=['venv', 'antenv'])

# Διαγραφή των migrations φακέλων
delete_folders('migrations')
