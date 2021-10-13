#!/usr/bin/python3

import argparse
import copy
import csv
from datetime import date
import os.path
import pickle

import git

MONTH_BY_SECOND = 2 * 30 * 24 * 60 * 60

COMPANY_MAP = {
    "Apple Inc.": "apple",
    "Amazon": "amazon",
    "Amazon AWS": "amazon",
    "Amazon Web Services Inc.": "amazon",
    "Fujistu": "fujitsu",
    "Fujitsu Limited": "fujitsu",
    "Fujitsu UK": "fujitsu",
    "Google LLC": "google",
    "Huawei Technologies Co. Ltd": "huawei",
    "Intel Corporation": "intel",
    "International Business Machines Corporation": "ibm",
    "Microsoft": "microsoft",
    "Microsoft Corporation": "microsoft",
    "Microsoft Research": "microsoft",
    "NEC Corporation": "nec",
    "Red Hat Inc.": "redhat",
    "VMware Inc.": "vmware",
    "VMware Tanzu": "vmware",
}


def parse(commits=None, outputfile=None, emailmap=None, companymap=None):

    emails = []
    c_emails = dict(
        google={},
        redhat={},
        huawei={},
        fujitsu={},
        ibm={},
        vmware={},
        intel={},
        microsoft={},
        amazon={},
        apple={},
        facebook={},
        nec={},
        others={},
    )
    last = None
    companies = list(c_emails.keys())
    companies.remove("others")

    writer = csv.writer(outputfile, quoting=csv.QUOTE_MINIMAL)
    writer.writerow(["month"] + list(c_emails.keys()))

    for commit in commits:
        epoc = commit.committed_datetime.timestamp()
        email = commit.author.email
        _company = None
        if email in emailmap:
            account = emailmap[email]
            if account in companymap:
                for _company, _from, _until in companymap[account]:
                    if _from <= epoc <= _until:
                        break
                else:
                    _company = None

        _date = date.fromtimestamp(epoc)
        _month = _date.strftime("%Y/%m")
        if isinstance(last, str) and last != _month:
            c_emails_copy = copy.deepcopy(c_emails)
            for c in c_emails_copy.keys():
                for _email, _epoc in c_emails_copy[c].items():
                    if _epoc < epoc - MONTH_BY_SECOND:
                        del c_emails[c][_email]
            print(last, [(x, len(y)) for x, y in c_emails.items()])
            writer.writerow([last] + [len(y) for x, y in c_emails.items()])
        last = _month

        # Total count
        if email not in emails:
            emails.append(email)

        # Count by company
        if "@" in email:
            _, mx = email.split("@", 1)
        else:
            mx = email
        domains = mx.split(".")

        if _company:
            if _company in COMPANY_MAP:
                c_emails[COMPANY_MAP[_company]][account] = epoc
                continue

        for c in companies:
            if c in domains:
                c_emails[c][email] = epoc
                break
        else:
            c_emails["others"][email] = epoc

    c_emails_copy = copy.deepcopy(c_emails)
    for c in c_emails_copy.keys():
        for _email, _epoc in c_emails_copy[c].items():
            if _epoc < epoc - MONTH_BY_SECOND:
                del c_emails[c][_email]
    print(last, [(x, len(y)) for x, y in c_emails.items()])
    writer.writerow([last] + [len(y) for x, y in c_emails.items()])
    outputfile.close()


def main(repo_dirs=None, outputfile=None, emailmapfile=None, companymapfile=None):
    emailmap = {}
    companymap = {}
    all_commits = []
    if emailmapfile:
        emailmap = pickle.load(emailmapfile)
        print(len(emailmap))
    if companymapfile:
        companymap = pickle.load(companymapfile)
        print(len(companymap))

    for repo_dir in repo_dirs:
        if not os.path.isdir(repo_dir):
            continue
        print(repo_dir)
        repo = git.Repo(repo_dir)
        try:
            commits = [x for x in repo.iter_commits("master")]
        except Exception as e:
            try:
                commits = [x for x in repo.iter_commits("main")]
            except:
                print(str(e))
                continue
        commits.sort(key=lambda x: x.committed_datetime)
        with open(repo_dir + ".csv", "w") as f:
            parse(commits, f, emailmap, companymap)
        all_commits += commits
    all_commits.sort(key=lambda x: x.committed_datetime)
    print("ALL REPOS")
    parse(all_commits, outputfile, emailmap, companymap)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("repo_dirs", nargs="+")
    parser.add_argument("outputfile", type=argparse.FileType("w", encoding="utf8"))
    parser.add_argument(
        "-c", "--companymapfile", dest="companymapfile", type=argparse.FileType("rb")
    )
    parser.add_argument(
        "-e", "--emailmapfile", dest="emailmapfile", type=argparse.FileType("rb")
    )
    args = parser.parse_args()
    main(**args.__dict__)
