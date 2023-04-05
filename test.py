import json

from pyscripts.objects import Drinker


username = "user123"

drinker = Drinker.get_drinker(username=username)
drinker.sex = "female"
print(drinker.sex)
drinker.save_to_db()
