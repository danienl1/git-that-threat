import os
from git import Repo

class GitHubRepoDownloader:
    def __init__(self, repo_url, download_path):
        self.repo_url = repo_url
        self.download_path = download_path

    def download_repo(self):
        if os.path.exists(self.download_path):
            print(f"Directory '{self.download_path}' already exists. Removing it.")
            for root, dirs, files in os.walk(self.download_path, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            os.rmdir(self.download_path)
        print(f"Cloning repository from {self.repo_url} to {self.download_path}...")
        Repo.clone_from(self.repo_url, self.download_path)
        print("Cloning completed!")

    def list_files(self):
        file_list = []
        for root, _, files in os.walk(self.download_path):
            for file in files:
                relative_path = os.path.relpath(os.path.join(root, file), self.download_path)
                file_list.append(relative_path)
        return file_list

