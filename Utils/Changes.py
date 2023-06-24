import requests
from datetime import datetime
from .Format import truncate_string

def format_commit(commit):
    time = commit['commit']['author']['date']
    author = commit['commit']['author']['name']
    msg = commit['commit']['message']
    message = ' '.join(msg.split('\n')).strip()
    sha = commit['sha']
    url = commit['html_url']
    author_url = commit['author']['html_url']
    dt = datetime.fromisoformat(time[:-1])
    date = dt.strftime('%d/%m/%Y')
    return f"[{sha[:7]}]({url}) by [{author}]({author_url})\n`{truncate_string(message, 40)}` at {date}"

def get_last_commits():
    url = "https://api.github.com/repos/himangshu147-git/ChickBot/commits"
    response = requests.get(url, params={"per_page": 5})
    commits = response.json()
    commit_strings = [format_commit(commit) for commit in commits]
    return commit_strings


# value="\n".join(get_last_commits())