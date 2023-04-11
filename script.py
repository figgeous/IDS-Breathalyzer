import json

# Load the beverages database from a JSON file
with open('beverages.json') as f:
    beverages = json.load(f)

# Calculate the total alcohol volume for each entry in the database
for beverage in beverages:
    total_alcohol_volume = beverage['volume'] * beverage['alcohol_percentage'] / 100
    beverage['total_alcohol_volume'] = round(total_alcohol_volume, 2)

# Save the updated database to a JSON file
with open('beverages_updated.json', 'w') as f:
    json.dump(beverages, f, indent=2)
