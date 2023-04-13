import datetime

from pyscripts.objects import get_all_sessions_from_db, Session, get_session_from_db, get_session_object_from_db, \
    Drinker

# print(get_all_sessions_from_db())

# session = get_session_from_db(id=1)
# print(session)
#
# session_object = get_session_object_from_db(id=1)
# print(session_object)

# session = Session(
#         id=None, # This is set by the database
#         username="123",
#         mode=1,
#         max_alcohol=0.1,
#         start_time=datetime.datetime.now(),
#         drive_time=datetime.datetime.now()+datetime.timedelta(minutes=300),
#     )
# session.save_to_db()
#
# drinker = Drinker(
#     username="123",
#     password="123",
#     dob=datetime.datetime(2000, 1, 1),
#     sex="Male",
#     weight=123,
# )
# drinker.save_to_db()

drinker = Drinker.get_drinker_from_db(username="123")
print(drinker)

print(drinker.get_current_session())