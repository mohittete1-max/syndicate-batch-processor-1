import os
import subprocess
import shutil

WORKSPACE_DIR = r"C:\Users\User\OneDrive\Desktop\Cricket\Syndicate_Batch_Processor"

def sync_to_github(commit_message="Initialize Syndicate Batch Processor ILP engine"):
    os.chdir(WORKSPACE_DIR)
    
    # Locate git executable explicitly
    git_path = shutil.which("git") or r"C:\Program Files\Git\cmd\git.exe"
    if not os.path.exists(git_path):
        print("Error: Git executable not found. Please verify your Git installation.")
        return

    commands = [
        [git_path, "init"],
        [git_path, "add", "syndicate_batch_processor.py"],
        [git_path, "commit", "-m", commit_message],
        [git_path, "branch", "-M", "main"],
        [git_path, "push", "-u", "origin", "main"]
    ]
    
    for cmd in commands:
        result = subprocess.run(cmd, capture_output=True, text=True)
        print(f"Executing {' '.join(cmd)}:\n{result.stdout.strip() or result.stderr.strip()}")

if __name__ == "__main__":
    sync_to_github()
