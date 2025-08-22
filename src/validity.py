import re

def get_device_category(device, category_rules):
    for category, pattern in category_rules.items():
        if re.fullmatch(pattern, device):
            return category
    return "Not categorized"

def check_device_validity(row, validity_rules):
    if validity_rules.empty() or row["category"] not in validity_rules.keys():
        return True
    for tool, rule in validity_rules[row["category"]]:
        if rule != 2 and row[tool] != rule:
            return False
    return True
