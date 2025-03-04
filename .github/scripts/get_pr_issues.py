"""
This script uses the Github Client to extract issues from recent PRs into Dev that have not yet been merged into main
It then outputs the issues to stdout for use in the next step
"""

import subprocess
import json
import re
import os

PATTERN = r"https:\/\/github\.com\/Police\-Data\-Accessibility\-Project\/data\-sources\-app\/issues\/\d+"


'git log origin/main..origin/dev --oneline --merges | grep "Merge pull request"'
git_log = subprocess.run(
    [
        "git",
        "log",
        "origin/main..origin/dev",
        "--oneline",
        "--merges",
    ],
    capture_output=True,
    text=True,
)

if git_log.returncode != 0:
    print("Error fetching PRs:", git_log.stderr)
    exit(1)

results = git_log.stdout.split("\n")

# Retrieve PRs
pr_only_requests = [result for result in results if "Merge pull request" in result]

# Retrieve PR numbers
pr_numbers = []

for result in pr_only_requests:
    pr_number = re.search(r"#(\d+)", result).group(1)
    pr_numbers.append(pr_number)


issue_urls = []
numbers = []

for number in pr_numbers:
    result = subprocess.run(
        [
            "gh",
            "pr",
            "view",
            number,
            "--json",
            "url,body",
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print("Error fetching PRs:", result.stderr)
        exit(1)

    text = result.stdout
    json_text = json.loads(text)

    number = json_text.get("url", "")
    numbers.append(str(number))
    body = json_text.get("body", "")
    issues_in_body = re.findall(PATTERN, body)
    issue_urls.extend(issues_in_body)

if not issue_urls:
    print("No issues found.")
    exit(0)


# Remove duplicates
issue_urls = list(set(issue_urls))

# Sort
issue_urls.sort()

issue_string = " * " + "\n * ".join(issue_urls)
number_string = " * " + "\n * ".join(numbers)

new_body = "\n\n### Resolves Issues:\n" + issue_string
new_body += "\n\n### Contains PRs:\n" + number_string


def edit_pr_body():
    # Get PR number from environment variable
    pr_number = os.environ.get("PR_NUMBER")

    if not pr_number:
        print("No PR number found in environment. Exiting.")
        exit(1)

    result = subprocess.run(
        [
            "gh",
            "pr",
            "edit",
            pr_number,
            "--body",
            new_body,
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print("Error updating PR body:", result.stderr)
        exit(1)


edit_pr_body()
# print(new_body)
print("Updated PR body successfully!")
