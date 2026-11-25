"""Rewrite the pinned-repos section of README.md from the user's live GitHub pins."""
import json, os, re, urllib.request, html

USER = os.environ.get("GH_USER", "phaze7r")
TOKEN = os.environ["GITHUB_TOKEN"]
README = "README.md"

QUERY = """
query($login: String!) {
  user(login: $login) {
    pinnedItems(first: 6, types: REPOSITORY) {
      nodes { ... on Repository {
        name url description stargazerCount forkCount
        primaryLanguage { name }
      } }
    }
  }
}"""

def gql():
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": USER}}).encode(),
        headers={"Authorization": f"bearer {TOKEN}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as r:
        return json.load(r)["data"]["user"]["pinnedItems"]["nodes"]

def card(repo):
    lang = (repo.get("primaryLanguage") or {}).get("name", "")
    desc = html.escape(repo.get("description") or "No description yet.")
    meta = " · ".join(x for x in [lang, f"★ {repo['stargazerCount']}", f"⑂ {repo['forkCount']}"] if x)
    return (f'<td width="50%" valign="top">\n\n**[{repo["name"]}]({repo["url"]})**  \n'
            f'{desc}  \n<sub>{meta}</sub>\n\n</td>')

def render(repos):
    if not repos:
        return "_Pin some repositories on your profile and they will appear here._"
    rows = []
    for i in range(0, len(repos), 2):
        pair = [card(r) for r in repos[i:i + 2]]
        if len(pair) == 1:
            pair.append('<td width="50%"></td>')
        rows.append("<tr>\n" + "\n".join(pair) + "\n</tr>")
    return "<table>\n" + "\n".join(rows) + "\n</table>"

def main():
    block = render(gql())
    text = open(README, encoding="utf-8").read()
    new = re.sub(r"(<!--PINS:START-->).*?(<!--PINS:END-->)",
                 lambda m: f"{m.group(1)}\n{block}\n{m.group(2)}", text, flags=re.S)
    if new != text:
        open(README, "w", encoding="utf-8").write(new)

if __name__ == "__main__":
    main()
