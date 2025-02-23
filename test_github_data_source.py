from brainboost_data_source_package.data_source_addons.BBGitHubDataSource import BBGitHubDataSource
from brainboost_configuration_package.BBConfig import BBConfig

def main():
    github_ds = BBGitHubDataSource()
    
    username = "your-github-username"
    target_directory = "/path/to/clone/repositories"
    token = "your-personal-access-token"  # Optional

    try:
        github_ds.fetch(username, target_directory, token)
    except Exception as e:
        print(f"An error occurred during fetch: {e}")

if __name__ == "__main__":
    main()