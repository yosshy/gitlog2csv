#!/usr/bin/python3

import argparse
import os
import os.path

import git
from github import Github


GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]


def main(github_org=None):

    g = Github(GITHUB_TOKEN)
    org = g.get_organization(github_org)
    for repo in org.get_repos():
        print(repo.clone_url, repo.name)
        target_path = os.path.join(github_org, repo.name)
        if not os.path.isdir(target_path):
            os.makedirs(target_path)
        git.Git().clone(repo.clone_url, target_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("github_org")
    args = parser.parse_args()

    main(**args.__dict__)
