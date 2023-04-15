from pyscripts.objects import Drinker
from pyscripts.objects import get_drink_candidates_for_drive_time
from pyscripts.objects import get_drink_candidates_less_than_max_alcohol

drinker = Drinker.get_drinker_from_db(user_id=1)
print(drinker)
current_session = drinker.get_current_session()
print(current_session.max_alcohol)
current_bac = 0.05
recommendations = get_drink_candidates_less_than_max_alcohol(
    drinker=drinker, current_bac=current_bac
)
print(recommendations)
