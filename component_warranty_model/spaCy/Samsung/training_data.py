input_data = [
    ("Samsung LED 138CM QA55QN85BA NEO QLED 4K", {"entities": [("QA55QN85BA", "MODEL")]}),
    ("Samsung LED 138cm 55TU8200 UHD/4K", {"entities": [("55TU8200", "MODEL")]}),
    ("QA50Q60AAKLXL", {"entities": [("QA50Q60AAKLXL", "MODEL")]}),
    ("SAMSUNG UHD LED UA43TU800", {"entities": [("UA43TU800", "MODEL")]}),
    ("SAMSUNG UA43AU7700 - 43\" LED", {"entities": [("UA43AU7700", "MODEL")]}),
    ("UA32T4600AKBXL", {"entities": [("UA32T4600AKBXL", "MODEL")]}),
    ("SAMSUNG LED 55CU7700", {"entities": [("55CU7700", "MODEL")]}),
    ("SAMSUNG 4K UHD LED UA43AU8000", {"entities": [("UA43AU8000", "MODEL")]}),
    ("UA55AU8200KLXL", {"entities": [("UA55AU8200KLXL", "MODEL")]}),
    ("SAMSUNG LED UA43AU7700", {"entities": [("UA43AU7700", "MODEL")]}),
    ("UA43AU8000KLXL", {"entities": [("UA43AU8000KLXL", "MODEL")]}),
    ("UA43AU9070ULXL", {"entities": [("UA43AU9070ULXL", "MODEL")]}),
    ("SAMSUNG LED UA32T4450", {"entities": [("UA32T4450", "MODEL")]}),
    ("Samsung LED 125cm 50AU8000 UHD/4K", {"entities": [("50AU8000", "MODEL")]}),
    ("SAMSUNG UHD LED UA50TU8000", {"entities": [("UA50TU8000", "MODEL")]}),
    ("SAMSUNG SMART LED UA43T5500", {"entities": [("UA43T5500", "MODEL")]}),
    ("SAMSUNG 4K UHD UA55BU8000", {"entities": [("UA55BU8000", "MODEL")]}),
    ("Samsung LED 108cm 43TU8000 UHD/4K", {"entities": [("43TU8000", "MODEL")]}),
    ("Samsung LED 138cm 55TU8200 UHD/4K", {"entities": [("55TU8200", "MODEL")]}),
    ("SAMSUNG SMART LED UA32T4900", {"entities": [("UA32T4900", "MODEL")]}),
    ("QA55LS03AAKLXL", {"entities": [("QA55LS03AAKLXL", "MODEL")]}),
    ("SAMSUNG SMART LED UA32T4600", {"entities": [("UA32T4600", "MODEL")]}),
    ("UA75BU8000KXXL", {"entities": [("UA75BU8000KXXL", "MODEL")]}),
    ("SAMSUNG SMARTLED UA32T4500", {"entities": [("UA32T4500", "MODEL")]}),
    ("SAMSUNG SMART LED UA32T4600", {"entities": [("UA32T4600", "MODEL")]}),
    ("SAMSUNG SMART LED UA32T4600", {"entities": [("UA32T4600", "MODEL")]}),
    ("SAMSUNG 4K QLED QA43Q60A", {"entities": [("QA43Q60A", "MODEL")]}),
    ("QA55Q60RAKXXL", {"entities": [("QA55Q60RAKXXL", "MODEL")]}),
    ("UA55AU8200KLXL", {"entities": [("UA55AU8200KLXL", "MODEL")]}),
    ("Samsung LED 125cm 50AU8000 UHD/4K", {"entities": [("50AU8000", "MODEL")]}),
    ("SAMSUNG LED UA32T4450", {"entities": [("UA32T4450", "MODEL")]}),
    ("UA32T4600AKBXL", {"entities": [("UA32T4600AKBXL", "MODEL")]}),
    ("UA32T4600AKBXL", {"entities": [("UA32T4600AKBXL", "MODEL")]}),
    ("SAMSUNG LED UA32T4050", {"entities": [("UA32T4050", "MODEL")]}),
    ("UA55AU7700KLXL", {"entities": [("UA55AU7700KLXL", "MODEL")]}),
    ("SAMSUNG 4K UHD LED UA55AU7700", {"entities": [("UA55AU7700", "MODEL")]}),
    ("Samsung LED 80cm 32T4350 HD", {"entities": [("32T4350", "MODEL")]}),
    ("SAMSUNG SMARTLED UA32T4500", {"entities": [("UA32T4500", "MODEL")]}),
    ("SAMSUNG SMART LED UA32T4600", {"entities": [("UA32T4600", "MODEL")]}),
    ("SAMSUNG SMARTLED UA32T4500", {"entities": [("UA32T4500", "MODEL")]}),
    ("UA43AU7700KLXL", {"entities": [("UA43AU7700KLXL", "MODEL")]}),
    ("Samsung LED 80cm 32T4350 HD", {"entities": [("32T4350", "MODEL")]}),
    ("Samsung LED 138cm 55TU8200", {"entities": [("55TU8200", "MODEL")]}),
    ("UA55BU8000KLXL", {"entities": [("UA55BU8000KLXL", "MODEL")]}),
    ("UA43BU8000KLXL", {"entities": [("UA43BU8000KLXL", "MODEL")]}),
    ("SAMSUNG LED 80CM- 32N4200", {"entities": [("32N4200", "MODEL")]}),
    ("SAMSUNG 4K UHD LED UA55AU9070", {"entities": [("UA55AU9070", "MODEL")]}),
    ("SAMSUNG UHD LED UA43RU7100", {"entities": [("UA43RU7100", "MODEL")]}),
    ("SAMSUNG SMARTLED UA32T4500", {"entities": [("UA32T4500", "MODEL")]}),
    ("UA65AU8200KLXL", {"entities": [("UA65AU8200KLXL", "MODEL")]}),
]

def generate_annotated_data(input_data):
    annotated_data = []
    for text, model_info in input_data:
        # Extract the model number from the 'entities' field in the dictionary
        model_number = model_info['entities'][0][0]
        start_idx = text.find(model_number)
        end_idx = start_idx + len(model_number)
        annotated_data.append((text, {"entities": [(start_idx, end_idx, "MODEL")]}))
    return annotated_data

TRAIN_DATA = generate_annotated_data(input_data)

print(TRAIN_DATA)