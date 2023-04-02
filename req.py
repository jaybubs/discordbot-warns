import requests
import urllib3
import logging
import sys
import config

urllib3.disable_warnings()

logging.basicConfig(stream=sys.stdout)
log = logging.getLogger(__name__)
log.setLevel(logging.WARN)
log.debug("hi")

host = "https://pb.example.com"

resp = requests.post(
        url=f"{host}/api/admins/auth-with-password",
        json={
            "identity":f"{config.pb_identity}",
            "password":f"{config.pb_password}"
            },
        verify=False,
        )
if resp.status_code == 200:
    pass
else:
    log.critical(resp.status_code)
    log.critical("fix yo shit")
    sys.exit()

# pocketbase token
token = resp.json()["token"]

# pocketbase url
base_url = f"{host}/api/collections/physusers/records"

# should be triggered to create a user if doesn't exist
def create_user(username: str) -> str:

    data = { "username" : f"{username}" }

    resp = requests.post(
            url=f"{base_url}",
            json=data,
            headers={"Authorization":f"Bearer {token}"},
            verify=False,
            )
    log.debug(resp.json())

    log.info(f"user {username} created")

    return resp.json()["id"]

# function to find a single user as we really just need to fetch the id and nothing else
def find_user(username: str) -> tuple[str, int]:

    log.debug(f"username is {username}")

    resp = requests.get(
            url=f"{base_url}?filter=(username='{requests.utils.quote(username)}')",
            headers={"Authorization":f"Bearer {token}"},
            verify=False,
            )
    log.debug(resp.json())

    items = resp.json()["items"]

    if not items:
        log.info(f"user {username} not found")
        return ("none", 0)

    log.info(f"user {username} found with {items[0]['warns']} warns")
    return (items[0]["id"], items[0]["warns"])

# we handle showing and modifying warn values in one
def modify_warns(username: str, modify: str) -> dict[str,int]:

    user_id, warns = find_user(username)

    # if doesn't exist, create and store id
    if user_id == "none":
        log.debug(f"creating new user {username}")
        user_id = create_user(username)

    match modify:
        case "+":
            warns += 1
        case "-":
            warns -= 1
        case "reset":
            warns = 0
        case "show":
            warns = warns
        # this should never happen, so let's just not modify a thing
        case _:
            log.warn("invalid modification, defaulting to nothing")
            warns = warns


    data = {
            "username" : f"{username}",
            "warns" : warns,
            }

    log.info(f"user {username} now has {warns} warns")

    resp = requests.patch(
            url=f"{base_url}/{user_id}",
            json=data,
            headers={"Authorization":f"Bearer {token}"},
            verify=False,
            )
    log.debug(resp.json())

    return data

# remove user, so we don't have too many unwanted persons in the db
def delete_user(username: str) -> str:

    user_id, _ = find_user(username)

    resp = requests.delete(
            url=f"{base_url}/{user_id}",
            headers={"Authorization":f"Bearer {token}"},
            verify=False,
            )
    # gotta use dict here because the response we want - 204 returns null, and json would fail
    log.debug(resp.__dict__)

    if resp.status_code == 204:
        return f"user {username} has been removed from the db"
    else:
        return f"user {username} already does not exist in the db"

# get all users and their warns in a {"user": X, ...} format
def list_users() -> dict[str,int]:

    resp = requests.get(
            url=f"{base_url}?sort=username",
            headers={"Authorization":f"Bearer {token}"},
            verify=False,
            )
    log.debug(resp.json())

    items = resp.json()["items"]

    return {item["username"] : item["warns"] for item in items}
