from .objects import Drinker, get_all_beverages_from_db


def get_drink_recommendations(current_bac: float, drinker: Drinker):
    # For now return the first three beverages from the db
    # TODO: replace with proper drink recommendations
    return get_all_beverages_from_db()[:3]




def can_user_drive(
    weight: int, sex: str, current_bac: float, user_time: int) -> float:
    """
    Calculates the current BAC and time to sober for a person
    """
    import math

    # Calculate the BAC per drink for the person and the time it takes to metabolize one drink
    bac_increase_per_drink: float  # Amount BAC raises per 30 ml of pure alcohol
    hours_to_metabolize_one_drink: float  # Seconds to metabolize 30 ml alc. by weight
    if sex == "Male":
        bac_increase_per_drink = 0.0662 * math.exp(-0.014 * weight) 
        hours_to_metabolize_one_drink = (3.9584 * math.exp(-0.013 * weight))
    else:  # Female
        bac_increase_per_drink = 0.1004 * math.exp(-0.016 * weight)
        hours_to_metabolize_one_drink = (5.1596 * math.exp(-0.014 * weight))

    # Calculate the current BAC and time to sober
  
    drinks_metabolized_per_hour = 1 / hours_to_metabolize_one_drink
    
    bac_metabolized_per_Hour = drinks_metabolized_per_hour * bac_increase_per_drink

    hours_to_sober = (current_bac - 0.05) / bac_metabolized_per_Hour

    if hours_to_sober > user_time:
        can_drive = True
        print("Your current BAC is:", current_bac)
        print("Which means you CAN drive in ", user_time/3600, " hours.")
    else:
        can_drive = False
        print("Your current BAC is:", current_bac)
        print("Which means you  CANNOT drive in ", user_time/3600, " hours.")

    return can_drive

# can_user_drive(85, "Male", 0.1, 10000)


""" # Sample usage
weight = 84.1
sex = "Male"
drinks = 10  # number of drinks (30 ml pure alcohol)
seconds_since_start = 4 * 3600  # Time (hr) since the person started drinking
current_bac, seconds_to_sober = get_current_bac(
    weight=weight, sex=sex, drinks=drinks, seconds_since_start=seconds_since_start
)

print(
    "You're a "
    + str(sex)
    + ", And you've had "
    + str(drinks)
    + " drinks, over the last "
    + str(seconds_since_start / 3600)
    + " hour(s)."
)
print("This means your current BAC should be: " + str(round(current_bac, 2)))
print(
    "Because you're this drunk, you have to wait ",
    round(seconds_to_sober / 3600, 2),
    " hours before you can drive again.",
) """
