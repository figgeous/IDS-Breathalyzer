import json

from pyscripts.objects import Drinker

# This is just to demonstrate how you can retrieve a drinker from the database,
# make changes to it, and save it back to the database.
username = "user123"
drinker = Drinker.get_from_db(username=username)
drinker.sex = "female"
print(drinker.sex)
drinker.save_to_db()
