import argparse
from datetime import datetime
import pickle
import re

FROM_UNTIL_PATTERN = re.compile(r"(.*) from (.*) until (.*)")
FROM_PATTERN = re.compile(r"(.*) from (.*)")
UNTIL_PATTERN = re.compile(r"(.*) until (.*)")

def main(inputfiles=None):
    print(inputfiles)

    emailmap = {}
    companymap = {}
    currentepoc = datetime.now().timestamp()
    for f in inputfiles:
        for line in f.readlines():
            if line.strip()[0] == "#":
                continue
            if not line.startswith("\t"):
                # print(line)
                if ":" not in line:
                    continue
                name, emails = line.split(":", 1)
                for email in emails.split(","):
                    email = email.strip()
                    # print(f"'{email}' -> '{name}'")
                    email = email.replace("!", "@")
                    emailmap[email] = name
            else:
                line = line.strip()
                # print(line)
                companymap.setdefault(name, [])
                m = FROM_UNTIL_PATTERN.match(line)
                if m is not None:
                    _company = m.group(1)
                    _from = int(datetime.strptime(m.group(2), "%Y-%m-%d").timestamp())
                    _until = int(datetime.strptime(m.group(3), "%Y-%m-%d").timestamp())
                    companymap[name].append((_company, _from, _until))
                    # print(f"{_company} from {_from} until {_until}")
                    continue

                m = UNTIL_PATTERN.match(line)
                if m is not None:
                    _company = m.group(1)
                    _from = 0
                    _until = int(datetime.strptime(m.group(2), "%Y-%m-%d").timestamp())
                    companymap[name].append((_company, _from, _until))
                    # print(f"{_company} until {_until}")
                    continue

                m = FROM_PATTERN.match(line)
                if m is not None:
                    _company = m.group(1)
                    _from = int(datetime.strptime(m.group(2), "%Y-%m-%d").timestamp())
                    _until = currentepoc
                    companymap[name].append((_company, _from, _until))
                    # print(f"{_company} from {_from}")
                    continue

                _company = line
                _from = 0
                _until = currentepoc
                companymap[name].append((_company, _from, _until))
                # print(f"{_company}")

    print(len(emailmap))
    print(len(companymap))
    with open("emailmap.pickle", "wb") as f:
        pickle.dump(emailmap, f)
    with open("companymap.pickle", "wb") as f:
        pickle.dump(companymap, f)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("inputfiles", type=argparse.FileType("r", encoding="utf8"), nargs="+")
    args = parser.parse_args()
    main(**args.__dict__)