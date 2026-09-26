"""Recreate the two views whose grouping cannot be updated via GraphQL."""

import json
import subprocess

from configure_project import OWNER, graphql


USER_ID = 65781172
TARGET = 3


def rest_create(name, layout, group_by, vertical_group_by):
    payload = {"name": name, "layout": layout,
               "group_by": group_by, "vertical_group_by": vertical_group_by}
    result = subprocess.run(
        ["gh", "api", "-X", "POST", "-H", "X-GitHub-Api-Version: 2026-03-10",
         f"users/{USER_ID}/projectsV2/{TARGET}/views", "--input", "-"],
        input=json.dumps(payload), text=True, capture_output=True,
    )
    if result.returncode:
        raise RuntimeError(f"GitHub view API rejected request: {result.stderr[:1000]}")
    return json.loads(result.stdout)


QUERY = """
query($owner:String!) {
  user(login:$owner) { projectV2(number:3) {
    fields(first:50) { nodes {
      ... on ProjectV2Field { name databaseId }
      ... on ProjectV2SingleSelectField { name databaseId }
    } }
    views(first:20) { nodes {
      id name layout
      groupBy(first:5) { nodes { name } }
      verticalGroupBy(first:5) { nodes { name } }
    } }
  } }
}
"""


def inspect():
    project = graphql(QUERY, owner=OWNER)["user"]["projectV2"]
    fields = {f["name"]: f["databaseId"] for f in project["fields"]["nodes"]
              if f and "databaseId" in f}
    views = {v["name"]: v for v in project["views"]["nodes"]}
    return fields, views


def correct(view, horizontal, vertical):
    return ([f["name"] for f in view["groupBy"]["nodes"]] == horizontal and
            [f["name"] for f in view["verticalGroupBy"]["nodes"]] == vertical)


def configure(name, horizontal, vertical):
    fields, views = inspect()
    if correct(views[name], horizontal, vertical):
        print(f"Already configured: {name}")
        return
    temp = f"{name} (configured)"
    if temp not in views:
        rest_create(temp, "board" if name == "Priority board" else "table",
                    [fields[n] for n in horizontal], [fields[n] for n in vertical])
        print(f"Created grouped replacement for {name}")
    _, views = inspect()
    if not correct(views[temp], horizontal, vertical):
        raise RuntimeError(f"Grouping verification failed for {temp}; original preserved")
    graphql("""mutation($input:DeleteProjectV2ViewInput!) {
      deleteProjectV2View(input:$input) { projectV2View { id } }
    }""", input={"viewId": views[name]["id"]})
    graphql("""mutation($input:UpdateProjectV2ViewInput!) {
      updateProjectV2View(input:$input) { projectV2View { id } }
    }""", input={"viewId": views[temp]["id"], "name": name})
    print(f"Configured: {name}")


if __name__ == "__main__":
    configure("Priority board", ["Priority"], ["Status"])
    configure("Team items", ["Status"], [])
    _, views = inspect()
    for name, horizontal, vertical in (("Priority board", ["Priority"], ["Status"]),
                                       ("Team items", ["Status"], [])):
        assert correct(views[name], horizontal, vertical)
    print("Both view groupings verified")
