from pyscripts.objects import Drinker


def get_drink_recommendations(current_bac: float, drinker: Drinker):
    return ["Gin and tonic"]


def get_current_bac(
    weight: int, sex: str, drinks: int, seconds_since_start: int
) -> float:
    """
    Calculates the current BAC and time to sober for a person
    """
    import math

    # Calculate the BAC per drink for the person and the time it takes to metabolize one drink
    bac_increase_per_drink: float  # Amount BAC raises per 30 ml of pure alcohol
    seconds_to_metabolize_one_drink: float  # Seconds to metabolize 30 ml alc. by weight
    hours_to_seconds = 3600  # 1 hour = 3600 seconds
    if sex == "Male":
        bac_increase_per_drink = 0.0662 * math.exp(-0.014 * weight)
        seconds_to_metabolize_one_drink = (
            3.9584 * math.exp(-0.013 * weight) * hours_to_seconds
        )
    else:  # Female
        bac_increase_per_drink = 0.1004 * math.exp(-0.016 * weight)
        seconds_to_metabolize_one_drink = (
            5.1596 * math.exp(-0.014 * weight) * hours_to_seconds
        )

    # Calculate the current BAC and time to sober
    bac_metabolized_per_second = (
        1 / seconds_to_metabolize_one_drink
    ) * bac_increase_per_drink
    bac_metabolized = bac_metabolized_per_second * seconds_since_start
    bac_consumed = drinks * bac_increase_per_drink
    current_bac = bac_consumed - bac_metabolized
    seconds_to_sober = (current_bac - 0.05) / bac_metabolized_per_second

    return current_bac, seconds_to_sober


# Sample usage
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
)
