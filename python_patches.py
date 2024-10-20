import os
import subprocess
import git
import pandas as pd

# Configure these variables
REPO_URL = "https://github.com/apache/airflow.git"
CLONE_DIR = "airflow"
BRANCH_NAME = "main"  # or the branch where you want to get the patches from
KEYWORDS = ["bug", "issue", "fix", "error", "patch"]  # Keywords to filter commit messages

def clone_repository(repo_url, clone_dir):
    if os.path.exists(clone_dir):
        print(f"Directory {clone_dir} already exists, pulling latest changes.")
        repo = git.Repo(clone_dir)
        repo.remotes.origin.pull()
    else:
        print(f"Cloning repository from {repo_url} into {clone_dir}.")
        git.Repo.clone_from(repo_url, clone_dir)

def get_commits(clone_dir, branch_name):
    repo = git.Repo(clone_dir)
    commits = list(repo.iter_commits(branch_name))
    return commits

def generate_patch(clone_dir, commit_hash, file_path):
    cmd = f"git show {commit_hash}:{file_path}"
    result = subprocess.run(cmd, shell=True, cwd=clone_dir, capture_output=True, text=True)
    return result.stdout

def commit_message_contains_keywords(message, keywords):
    message_lower = message.lower()
    return any(keyword in message_lower for keyword in keywords)

def main():
    clone_repository(REPO_URL, CLONE_DIR)
    commits = get_commits(CLONE_DIR, BRANCH_NAME)
    
    patches = []
    
    for commit in commits:
        if commit_message_contains_keywords(commit.message, KEYWORDS):
            diff_data = commit.diff(commit.parents or git.NULL_TREE, create_patch=True)
            for diff in diff_data:
                if diff.a_blob and diff.b_blob:  # Check if the blob exists
                    try:
                        patch_text = diff.diff.decode('utf-8', errors='replace')
                    except UnicodeDecodeError as e:
                        print(f"UnicodeDecodeError: {e}")
                        continue
                    
                    patches.append({
                        "project": os.path.basename(REPO_URL).replace(".git", ""),
                        "commit": commit.hexsha,
                        "file_path": diff.b_path,
                        "patch": patch_text
                    })
    
    df = pd.DataFrame(patches)
    df.to_csv("patches_airflow.csv", index=False)
    print("Patches have been saved to patches.csv")

if __name__ == "__main__":
    main()