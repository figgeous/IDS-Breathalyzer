import json

from pyscripts.crud import get_drinker

with open("/databases/users.json", "r") as infile:
    drinkers = json.load(infile)


username = "user123"
get_drinker(username=username)
# get_drinker(drinkers=data, username="user123")
