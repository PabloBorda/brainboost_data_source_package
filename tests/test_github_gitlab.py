import os
import pytest
from brainboost_data_source_package.data_source_addons.BBGitHubDataSource import BBGitHubDataSource
from brainboost_configuration_package.BBConfig import BBConfig


@pytest.fixture
def cleanup_directories():
    BBConfig.configure('local.conf')
    github_dir = 'tests/data/github'
    gitlab_dir = 'tests/data/gitlab'
    yield github_dir, gitlab_dir
    for directory in [github_dir, gitlab_dir]:
        if os.path.exists(directory):
            for root, dirs, files in os.walk(directory, topdown=False):
                for file in files:
                    os.remove(os.path.join(root, file))
                for dir in dirs:
                    os.rmdir(os.path.join(root, dir))
            os.rmdir(directory)

def test_fetch_data_sources(cleanup_directories):
    github_dir, gitlab_dir = cleanup_directories

    # GitHub data source parameters
    params_github = {
        'username': 'PabloBorda',
        'target_directory': github_dir,
        'token': BBConfig.get('github_token')  # Optional
    }
    github_ds = BBGitHubDataSource(params=params_github)

    try:
        github_ds.fetch()
    except Exception as e:
        pytest.fail(f"GitHub fetch failed: {e}")

    # GitLab data source parameters
    params_gitlab = {
        'username': 'brainboost',
        'target_directory': gitlab_dir,
        'token': BBConf.get([gitlab_token])  # Replace with a valid token
    }
    gitlab_ds = BBGitLabDataSource(params=params_gitlab)

    try:
        gitlab_ds.fetch()
    except Exception as e:
        pytest.fail(f"GitLab fetch failed: {e}")

    # Assert that directories contain cloned repositories
    assert os.path.exists(github_dir) and len(os.listdir(github_dir)) > 0, "GitHub target directory is empty."
    assert os.path.exists(gitlab_dir) and len(os.listdir(gitlab_dir)) > 0, "GitLab target directory is empty."
