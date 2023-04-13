from objects import Drinker
import json
import math

with open('pyscripts\\beverages_updates.json') as f:
    data = json.load(f)

beverages = data['beverages']


def user_bac_increase_per_drink(sex: str, weight: float):
    if sex == "male":
        bac_increase_per_drink = 0.0662 * math.exp(-0.014 * weight)
    else: #Female
        bac_increase_per_drink = 0.1004 * math.exp(-0.016 * weight)

    return bac_increase_per_drink



def recommend_drink(sex: str, weight: float, current_bac: float, max_bac: float):
    current_bac = round(current_bac, 2)
    max_bac = round(max_bac, 2)

    if current_bac >= max_bac:
        return "You've had too much to drink! You can't drink more without going over your set limit {}% BAC".format(max_bac)
    
    bac_increase_per_drink = user_bac_increase_per_drink(sex, weight)

    # Determine the maximum number of drinks the user can have before reaching max_bac
    max_drinks = (max_bac - current_bac) / bac_increase_per_drink

    # Create a list to store the recommended drinks
    recommended_drinks = []

    # Loop through the list of drinks and check if the user can have that many drinks
    for drink in beverages: 
        if float(drink["total_drinks"]) <= max_drinks:
            recommended_drinks.append(drink)

    # Sort the recommenended_drinks list by total_drinks
    recommended_drinks.sort(key=lambda x: float(x["total_drinks"]), reverse=True)

    # Get the top three recommened drinks
    top_three_drinks = [drink["name"] for drink in recommended_drinks[:3]]

    if not top_three_drinks:
        return "There are no drinks you can have without going over your set limit {}% BAC".format(max_bac)
    else: 
        return "Recommended drinks: {}, {} or {}".format(top_three_drinks[0], top_three_drinks[1], top_three_drinks[2])





print(recommend_drink("Male", 81.3, 0.085, 0.1))












def can_user_drive(
    weight: int, sex: str, current_bac: float, user_time: int) -> float:
    """
    Calculates the current BAC and time to sober for a person
    """


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
