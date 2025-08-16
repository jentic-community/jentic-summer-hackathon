import json

with open("sanitized_har.har", "r", encoding="utf-8", errors="ignore") as f:
    har_data = json.load(f)

base_urls = set()
auth_required = set()
print(1)

for entry in har_data["log"]["entries"]:
    request = entry["request"]
    url = request["url"]
    
    # extract base URL
    base_url = "/".join(url.split("/")[:3])
    base_urls.add(base_url)
    
    # check for auth headers
    headers = {h["name"].lower(): h["value"] for h in request["headers"]}
    if "authorization" in headers:
        auth_required.add(url)

print("Base URLs:", base_urls)
print("Endpoints requiring auth:", auth_required)

endpoints = set()
for entry in har_data["log"]["entries"]:
    request = entry["request"]
    path = "/" + "/".join(request["url"].split("/")[3:])
    endpoints.add((request["method"], path))

print("Discovered endpoints and methods:", endpoints)

for entry in har_data["log"]["entries"]:
    request = entry["request"]
    
    # Query params
    for param in request.get("queryString", []):
        print("Param:", param["name"], "Example value:", param["value"])
    
    # POST data
    post_data = request.get("postData", {}).get("text")
    if post_data:
        print("POST payload example:", post_data)

for entry in har_data["log"]["entries"]:
    response = entry["response"]
    content = response.get("content", {}).get("text")
    if content:
        print("Response for", entry["request"]["url"])
        print(content[:300])  # first 300 chars as example


