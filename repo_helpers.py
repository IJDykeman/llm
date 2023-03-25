import subprocess
def get_git_repo_root():
    """Get the root directory of the git repo."""
    return subprocess.run(["git", "rev-parse", "--show-toplevel"], stdout=subprocess.PIPE).stdout.decode().strip()  