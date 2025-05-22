import json
import random
import pandas as pd

def randomize_features(features, num_groups=5, num_iterations=50):
    results = []
    for iteration in range(num_iterations):
        shuffled_features = features[:]
        random.shuffle(shuffled_features)
        groups = [shuffled_features[i::num_groups] for i in range(num_groups)]
        
        # Store each iteration's groups in a dictionary
        results.append({f'Group {i+1}': group for i, group in enumerate(groups)})

    return results

features = [
    "Total Lines", "Total Words", "Total Tokens", "Total URLs", "Total Base64", "Total IPs",
    "Bracket Mean", "Bracket Std Dev", "Bracket Max", "Bracket Q3",
    "Equal Mean", "Equal Std Dev", "Equal Max", "Equal Q3",
    "Plus Mean", "Plus Std Dev", "Plus Max", "Plus Q3",
    "Identifier Entropy Mean", "Identifier Entropy Std Dev", "Identifier Entropy Max", "Identifier Entropy Q3",
    "String Entropy Mean", "String Entropy Std Dev", "String Entropy Max", "String Entropy Q3",
    "Homogeneous Identifiers", "Heterogeneous Identifiers", "Homogeneous Strings", "Heterogeneous Strings",
    "Setup Total Lines", "Setup Total Words", "Setup Total Tokens", "Setup Total URLs", "Setup Total Base64", "Setup Total IPs",
    "Setup Identifier Entropy Mean", "Setup Identifier Entropy Std Dev", "Setup Identifier Entropy Max", "Setup Identifier Entropy Q3",
    "Setup String Entropy Mean", "Setup String Entropy Std Dev", "Setup String Entropy Max", "Setup String Entropy Q3",
    "Setup Homogeneous Identifiers", "Setup Heterogeneous Identifiers", "Setup Homogeneous Strings", "Setup Heterogeneous Strings",
    "Total Install Script in .py", "Total Dangerous Install Commands Count"
]

# Generate the random groupings
randomized_results = randomize_features(features)

# Save to JSON file
with open("randomized_feature_groups.json", "w") as f:
    json.dump(randomized_results, f, indent=4)

print("Randomized feature groups saved successfully!")
