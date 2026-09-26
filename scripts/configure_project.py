"""Copy the Travel Planner project field/view skeleton into the xG project.

Run only in the protected GitHub Actions workflow with PROJECT_TOKEN. Safe to rerun.
Existing items are kept; their three default statuses map to equivalent source states.
"""

import json
import subprocess


OWNER = "leovferreira13"
SOURCE_NUMBER = 2
TARGET_NUMBER = 3
TARGET_REPO = f"{OWNER}/sports-data-visualizer"


def graphql(query, **variables):
    result = subprocess.run(
        ["gh", "api", "graphql", "--input", "-"],
        input=json.dumps({"query": query, "variables": variables}),
        text=True, capture_output=True, check=True,
    )
    data = json.loads(result.stdout)
    if data.get("errors"):
        raise RuntimeError(data["errors"])
    return data["data"]


QUERY = """
query($owner:String!, $source:Int!, $target:Int!) {
  user(login:$owner) {
    source:projectV2(number:$source) {
      id title
      fields(first:50) { nodes {
        ... on ProjectV2Field { id name dataType }
        ... on ProjectV2SingleSelectField {
          id name dataType options { id name color description }
        }
        ... on ProjectV2IterationField { id name dataType }
      } }
      views(first:20) { nodes { id name layout filter } }
    }
    target:projectV2(number:$target) {
      id title
      fields(first:50) { nodes {
        ... on ProjectV2Field { id name dataType }
        ... on ProjectV2SingleSelectField {
          id name dataType options { id name color description }
        }
        ... on ProjectV2IterationField { id name dataType }
      } }
      views(first:20) { nodes { id name layout filter } }
      items(first:100) { nodes {
        id
        content { ... on Issue { number repository { nameWithOwner } } }
        fieldValueByName(name:"Status") {
          ... on ProjectV2ItemFieldSingleSelectValue { name }
        }
      } }
    }
  }
}
"""


def snapshot():
    user = graphql(QUERY, owner=OWNER, source=SOURCE_NUMBER, target=TARGET_NUMBER)["user"]
    if not user["source"] or not user["target"]:
        raise RuntimeError("Both user projects must be accessible")
    return user["source"], user["target"]


def fields(project):
    return {field["name"]: field for field in project["fields"]["nodes"] if field}


def copy_status(source, target):
    src = fields(source)["Status"]
    dst = fields(target)["Status"]
    existing = {opt["name"].casefold(): opt for opt in dst["options"]}
    options = []
    for option in src["options"]:
        copied = {key: option[key] for key in ("name", "color", "description")}
        prior = existing.get(option["name"].casefold())
        if prior:
            copied["id"] = prior["id"]
        options.append(copied)
    if [o["name"] for o in src["options"]] != [o["name"] for o in dst["options"]]:
        graphql("""mutation($input:UpdateProjectV2FieldInput!) {
          updateProjectV2Field(input:$input) { projectV2Field { ... on ProjectV2SingleSelectField { id } } }
        }""", input={"fieldId": dst["id"], "singleSelectOptions": options})
        print("Copied Status options")


def copy_custom_fields(source, target):
    current = fields(target)
    for name in ("Priority", "Size", "Estimate", "Start date", "Target date"):
        src = fields(source)[name]
        if name in current:
            if current[name]["dataType"] != src["dataType"]:
                raise RuntimeError(f"Field {name} has an incompatible type")
            continue
        data_type = src["dataType"]
        spec = {"projectId": target["id"], "name": name, "dataType": data_type}
        if data_type == "SINGLE_SELECT":
            spec["singleSelectOptions"] = [
                {key: option[key] for key in ("name", "color", "description")}
                for option in src["options"]
            ]
        graphql("""mutation($input:CreateProjectV2FieldInput!) {
          createProjectV2Field(input:$input) { projectV2Field { ... on ProjectV2Field { id } } }
        }""", input=spec)
        print(f"Created field: {name}")


def copy_views(source, target):
    existing = {view["name"]: view for view in target["views"]["nodes"]}
    source_views = source["views"]["nodes"]
    # Reuse the board already created by the owner; preserve its identity and URL.
    if "Backlog" not in existing and "View 1" in existing:
        graphql("""mutation($input:UpdateProjectV2ViewInput!) {
          updateProjectV2View(input:$input) { projectV2View { id } }
        }""", input={"viewId": existing["View 1"]["id"], "name": "Backlog"})
        existing["Backlog"] = existing.pop("View 1")
        print("Renamed default board: Backlog")
    for view in source_views:
        name = view["name"]
        if name not in existing:
            graphql("""mutation($input:CreateProjectV2ViewInput!) {
              createProjectV2View(input:$input) { projectV2View { id } }
            }""", input={"projectId": target["id"], "name": name, "layout": view["layout"]})
            print(f"Created view: {name}")
    # Copy filters only after adapting repository references. View grouping and
    # sort rules are configured in the GitHub UI; GraphQL cannot set them here.
    _, fresh = snapshot()
    by_name = {v["name"]: v for v in fresh["views"]["nodes"]}
    for view in source_views:
        target_view = by_name[view["name"]]
        adapted = (view["filter"] or "").replace(
            f"repo:{OWNER}/my-travel-planner", f"repo:{TARGET_REPO}"
        )
        changes = {"viewId": target_view["id"]}
        if target_view["layout"] != view["layout"]:
            changes["layout"] = view["layout"]
        if (target_view["filter"] or "") != adapted:
            changes["filter"] = adapted
        if len(changes) > 1:
            graphql("""mutation($input:UpdateProjectV2ViewInput!) {
              updateProjectV2View(input:$input) { projectV2View { id } }
            }""", input=changes)
            print(f"Updated view: {view['name']}")


def remap_items(target):
    _, fresh = snapshot()
    status = fields(fresh)["Status"]
    options = {o["name"]: o["id"] for o in status["options"]}
    mapping = {"Todo": "unrefined", "In Progress": "in progress", "Done": "done"}
    for item in target["items"]["nodes"]:
        content = item.get("content") or {}
        if content.get("repository", {}).get("nameWithOwner") != TARGET_REPO:
            continue
        old = (item.get("fieldValueByName") or {}).get("name")
        desired = mapping.get(old)
        if not desired or desired not in options:
            continue
        graphql("""mutation($input:UpdateProjectV2ItemFieldValueInput!) {
          updateProjectV2ItemFieldValue(input:$input) { projectV2Item { id } }
        }""", input={"projectId": fresh["id"], "itemId": item["id"],
                     "fieldId": status["id"],
                     "value": {"singleSelectOptionId": options[desired]}})
        print(f"Issue #{content['number']}: {desired}")


if __name__ == "__main__":
    source, target = snapshot()
    if source["title"] != "my-travel-planner" or target["title"] != "sports-data-visualizer":
        raise RuntimeError("Unexpected project titles; refusing changes")
    copy_status(source, target)
    copy_custom_fields(source, target)
    copy_views(source, target)
    remap_items(target)
    final_source, final_target = snapshot()
    print("Status:", [o["name"] for o in fields(final_target)["Status"]["options"]])
    print("Views:", [v["name"] for v in final_target["views"]["nodes"]])
    print("Custom fields:", [n for n in fields(final_target) if n in
          ("Priority", "Size", "Estimate", "Start date", "Target date")])
