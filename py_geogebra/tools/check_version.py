import requests
from ..tools.version import __version__


# https://docs.github.com/en/rest/releases/releases?apiVersion=2022-11-28
def check_version():
    url = "https://api.github.com/repos/brunovskyoliver/py-geogebra/releases/latest"
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    response = requests.get(url=url, headers=headers, timeout=5)
    return response.json()["tag_name"].replace("v", "")


def handle_version():
    local_version = __version__
    servers_version = check_version()
    assert len(servers_version) > 0
    if local_version != servers_version:
        print("nesedia nam verzie")
    else:
        print("all good")
