import json
import os

# Load the beverages database from a JSON file
try:
    with open('beverages.json', encoding='utf-8') as f:
        beverages = json.load(f)
        print("Loaded beverages:", beverages) # Debugging statement
except FileNotFoundError:
    print("Error: Could not find 'beverages.json' file")
    exit()
except json.JSONDecodeError as e:
    print("Error: Could not parse 'beverages.json' file")
    print("Reason:", e)
    exit()

# Calculate the total alcohol volume for each entry in the database
for beverage in beverages:
    if not isinstance(beverage, dict):
        print("Error: Invalid format for beverage entry:", beverage)
        continue
    total_alcohol_volume = beverage.get('volume', 0) * beverage.get('alcohol_percentage', 0) / 100
    beverage['total_alcohol_volume'] = round(total_alcohol_volume, 2)

# Save the updated database to a JSON file
output_file = os.path.join(os.getcwd(), 'beverages_updated.json')
try:
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(beverages, f, indent=2)
except IOError:
    print("Error: Could not save 'beverages_updated.json' file")
    exit()

print("Database successfully updated!")
