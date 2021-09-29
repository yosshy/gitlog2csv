import argparse
import copy
import csv
from datetime import date

MONTH_BY_SECOND = 2 * 30 * 24 * 60 * 60


def main(inputfile=None, outputfile=None):

    source = []
    for line in inputfile.readlines():
        epoc, email = line.split(" ")
        # print(epoc, email)
        source.append((int(epoc), email.lower()))
    source = sorted(source, key=lambda x: x[0])

    emails = []
    c_emails = dict(
        google={}, redhat={}, huawei={}, fujitsu={}, ibm={}, vmware={}, intel={}, microsoft={}, amazon={}, apple={}, facebook={}, others={}
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
            c_emails_copy = copy.deepcopy(c_emails)
            for c in c_emails_copy.keys():
                for _email, _epoc in c_emails_copy[c].items():
                    if _epoc < epoc - MONTH_BY_SECOND:
                        del(c_emails[c][_email])
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
                c_emails[c][email] = epoc
                break
        else:
            c_emails["others"][email] = epoc


    c_emails_copy = copy.deepcopy(c_emails)
    for c in c_emails_copy.keys():
        for _email, _epoc in c_emails_copy[c].items():
            if _epoc < epoc - MONTH_BY_SECOND:
                del(c_emails[c][_email])
    print(last, len(emails), [(x, len(y)) for x, y in c_emails.items()])
    writer.writerow([last] + [len(y) for x, y in c_emails.items()])
    outputfile.close()        

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("inputfile", type=argparse.FileType("r", encoding="utf8"))
    parser.add_argument("outputfile", type=argparse.FileType("w", encoding="utf8"))
    args = parser.parse_args()
    main(**args.__dict__)