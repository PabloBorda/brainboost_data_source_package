from brainboost_data_source_package.data_source_addons.BBGitHubDataSource import BBGitHubDataSource
from brainboost_configuration_package.BBConfig import BBConfig




def main():

    BBConfig.configure('local.conf')
    
    params_github = {
        'username' : 'PabloBorda',
        'target_directory' : 'tests/data/github',
        'token': BBConfig.get('github_token')# Optional
    }
    github_ds = BBGitHubDataSource(params=params_github)

    try:
        github_ds.fetch()
    except Exception as e:
        print(f"An error occurred during github fetch: {e}")

    params_gitlab = {
        'username' : 'brainboost',
        'target_directory' : 'tests/data/gitlab',
        'token':BBConfig.get('gitlab_token')  # Optional
    }
    gitlab_ds = BBGitLabDataSource(params=params_gitlab)

    try:
        gitlab_ds.fetch()
    except Exception as e:
        print(f"An error occurred during gitlab fetch: {e}")

if __name__ == "__main__":
    main()