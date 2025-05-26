def get_device_category(device):
    if device.startswith('lap0'):
        return "LAPTOP_FR"
    elif device.startswith('lap6'):
        return "LAPTOP_RO"
    elif device.startswith('arch'):
        return "Arch"
    elif device.startswith('cpc'):
        return "Windows VM"
    elif device.startswith('db') or device.startswith('ii') or device.startswith('md') or device.startswith('srv') or device in ['bo0001', 'bi0001', 'fs0001', 'nw0001', 'pki0001', 'pr0002', 'tx0001', 'frciamaccprdvm1']:
        return "Windows Server"
    elif 'azure' in device:
        return "Windows Azure Server"
    elif device.startswith('iphone'):
        return "Iphone"
    elif "intaro" in device:
        return "Intaro"
    elif device.startswith('pf'):
        return "Entra Device"
    elif device.startswith('w10'):
        return "Windows Autopilot"
    else:
        return "Not categorized"

def is_in(row, intune, endpoint, tenable, entra):
    return row["intune"] == intune and row["endpoint"] == endpoint and row["tenable"] == tenable and row["entra"] == entra

def check_device_validity(row, device_validity_rules):
    if row["category"] == "Not categorized":
        return False
    return is_in(row, *device_validity_rules[row["category"]])

def get_invalidity_reason(row, validity_rules):
    if row["validity"] == True:
        return "Valid"
    if row["category"] == "Not categorized":
        return "Not categorized"
    invalid_reason = ""
    for col in ["intune", "endpoint", "tenable", "entra"]:
        should_be_in = validity_rules[row["category"]][col] 
        if row[col] != should_be_in:
            if should_be_in:
                invalid_reason += f"Device should be in {col} "
            else:
                invalid_reason += f"Device shouldn't be in {col} "
    return invalid_reason
