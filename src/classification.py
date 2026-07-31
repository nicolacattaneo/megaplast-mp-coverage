
EQUIVALENT_CODES = {"V": "VIRGEN", "P": "PELLET"}
# missing codes??


def normalize_configuration(raw_value):
    if raw_value is None:
        return None
    normalized = raw_value.upper().strip().replace(" ", "")
    return EQUIVALENT_CODES.get(normalized, normalized)

def build_classification_key(item_number, configuration_id, size_id=None, color_id=None):
    if configuration_id is None or item_number is None:
        raise ValueError(f"Missing configuration for item {item_number}")
    key = item_number.upper().strip() + "|" + normalize_configuration(configuration_id)
    if size_id is not None:
        key = key + "|" + str(size_id)
    if color_id is not None:
        key = key + "|" + str(color_id)
    return key

def add_keys_to_data(data, item_field, config_field, size_field=None, color_field=None):
    faulty_rows = 0 # remove later on
    for row in data:
        try:
            key = build_classification_key(row.get(item_field), row.get(config_field), row.get(size_field), row.get(color_field))
            row['classification_key'] = key
        except ValueError:
            faulty_rows += 1 # type: ignore | remove later on
            continue
    return data, faulty_rows ## remove faulty_rows later on
