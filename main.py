import os
from random import randint

import eel

dirname = os.path.dirname(__file__)
eel.init(dirname + "/web/")


# Exposing the random_python function to javascript
@eel.expose
def random_python():
    print("Random function running")
    return randint(1, 100)


eel.start("index.html", mode="firefox")
