import argparse
import csv
from datetime import date


def main(inputfile=None, outputfile=None):

    source = []
    for line in inputfile.readlines():
        epoc, email = line.split(" ")
        # print(epoc, email)
        source.append((int(epoc), email.lower()))
    source = sorted(source, key=lambda x: x[0])

    emails = []
    c_emails = dict(
        redhat=[], google=[], amazon=[], facebook=[], apple=[], microsoft=[], ibm=[], vmware=[], intel=[], huawei=[], others=[]
    )
    last = None
    companies = list(c_emails.keys())
    companies.remove("others")

    writer = csv.writer(outputfile, quoting=csv.QUOTE_MINIMAL)
    writer.writerow(["month"] + companies)

    for epoc, email in source:
        _date = date.fromtimestamp(epoc)
        _month = _date.strftime("%Y/%m")
        if isinstance(last, str) and last != _month:
            print(last, len(emails), [(x, len(y)) for x, y in c_emails.items()])
            writer.writerow([last] + [len(y) for x, y in c_emails.items()])
            # print(c_emails)
        last = _month

        # Total count
        if email not in emails:
            emails.append(email)

        # Count by company
        if "@" in email:
            _, mx = email.split("@")
        else:
            mx = email
        domains = mx.split(".")
        for c in companies:
            if c in domains:
                if email not in c_emails[c]:
                    c_emails[c].append(email)
                break
        else:
            if email not in c_emails["others"]:
                c_emails["others"].append(email)

    print(last, len(emails), [(x, len(y)) for x, y in c_emails.items()])
    writer.writerow([last] + [len(y) for x, y in c_emails.items()])
    outputfile.close()        

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("inputfile", type=argparse.FileType("r", encoding="utf8"))
    parser.add_argument("outputfile", type=argparse.FileType("w", encoding="utf8"))
    args = parser.parse_args()
    main(**args.__dict__)