"""Credential-free local CLI. Input is read interactively to avoid shell history."""

import json
from c4l.workforce.navigator import prepare

if __name__ == "__main__":
    print("Texas Workforce Benefits Navigator (reference version)")
    print("Do not enter SSNs, bank details or identification numbers. No message is saved.")
    question = input("Your question: ")
    print(json.dumps(prepare(question).public(), indent=2))
