import difflib
from fuzzywuzzy import fuzz
from rapidfuzz import fuzz as rapid_fuzz
import textdistance

# Define your model input and the list of product codes
model_input = "43 inch OLED TV"
product_codes = [
    "32N4000", "32T4500", "43N5380", "43TE50", "49RU7100", "55NU7100", "55RU8000", 
    "65NU7470", "65RU7100", "75Q80R", "32N4003", "32T4550", "43N5470", "43TU7200", 
    "50LS03T", "55NU7470", "55TU7200", "65NU8000", "65RU7470", "75Q900R", "32N4010", 
    "32T4700", "43NU6100", "43TU8000", "50NU6100", "55NU8000", "55TU8000", "65Q60R", 
    "65RU8000", "75Q950TS", "32N4100", "32T4750", "43NU7090", "43TU8200", "50NU7090", 
    "55Q60R", "55TU8200", "65Q60T", "65TU8000", "75Q95T", "32N4200", "32TE40", "43NU7100",
    "43TU8570", "50NU7470", "55Q60T", "55TU8570", "65Q6FN", "65TU8200", "75RU7100", 
    "32N4300", "40N5000", "43NU7470", "43TUE60", "50Q60T", "55Q6FN", "55TUE60", "65Q70R",
    "65TU8570", "75TU8000", "32N4305", "40N5200", "40N5200", "43Q60R", "49LS01T", "50RU7470", 
    "55Q70R", "58Q60T", "65Q70T", "65TUE60", "75TU8200", "32N4310", "43LS003", "43Q60T", 
    "49N5100", "50TU7200", "55Q70T", "58RU7100", "65Q7FN", "70TU7200", "82Q60R", "32N5200", 
    "43LS01T", "43R5570", "49N5300", "50TU8000", "55Q7FN", "58TU7200", "65Q800T", "75LS03T", 
    "82Q800T", "32R4500", "43N5002", "43N5002", "43RU7100", "49N5370", "50TUE60", "55Q80R", 
    "58TU8200", "65Q80R", "75NU7100", "82Q900R", "32T4010", "43N5005", "43RU7470", "49N5370A",
    "55LS01T", "55Q80T", "65LS003", "65Q80T", "75NU8000", "85Q80T", "32T4050", "43N5010", 
    "43T5310", "49NU7100", "55LS03R", "55Q8CN", "65LS03R", "65Q8CN", "75Q60R", "85Q950TS", 
    "32T4310", "43N5100", "43N5100", "43T5350", "49NU8000", "55LS03T", "55Q95T", "65LS03T", 
    "65Q900R", "75Q70T", "98Q900R", "32T4340", "43N5300", "43T5500", "49Q60R", "55NU6100", 
    "55RU7100", "65NU7090", "65Q90R", "75Q7FN", "32T4350", "43N5370", "43T5770", "49Q80T", 
    "55NU7090", "55RU7470", "65NU7100", "65Q95T", "75Q800T", "43LS01", "55LS03", "55Q8CN", 
    "65Q7FN", "65Q7FN", "75Q7FN", "43Q60R", "55Q60R", "55Q95T", "65Q80R", "75Q80R", "43Q60T", 
    "55Q60T", "58Q60T", "65Q80T", "75Q95T", "49LS01", "55Q6FN", "65LS03", "65Q8CN", "82Q60R", 
    "49Q60R", "55Q70R", "65Q60R", "65Q90R", "85Q80T", "49Q80T", "55Q70T", "65Q60T", "65Q95T", 
    "50LS03", "55Q7FN", "65Q6FN", "75LS03", "50Q60T", "50Q60T", "55Q80R", "65Q70R", "75Q60R", 
    "55LS01", "55Q80T", "65Q70T", "75Q70T3"
]

# Function to get top 5 matches
def get_top_matches(model_input, product_codes):
    # FuzzyWuzzy
    fuzzy_matches = [(code, fuzz.partial_ratio(model_input, code)) for code in product_codes]
    fuzzy_matches_sorted = sorted(fuzzy_matches, key=lambda x: x[1], reverse=True)
    
    # RapidFuzz
    rapid_matches = [(code, rapid_fuzz.partial_ratio(model_input, code)) for code in product_codes]
    rapid_matches_sorted = sorted(rapid_matches, key=lambda x: x[1], reverse=True)
    
    # Difflib
    difflib_matches = [(code, difflib.SequenceMatcher(None, model_input, code).ratio()) for code in product_codes]
    difflib_matches_sorted = sorted(difflib_matches, key=lambda x: x[1], reverse=True)
    
    # TextDistance (Levenshtein)
    textdistance_matches = [(code, textdistance.levenshtein(model_input, code)) for code in product_codes]
    textdistance_matches_sorted = sorted(textdistance_matches, key=lambda x: x[1], reverse=False)  # Lower distance is better

    return {
        "FuzzyWuzzy": fuzzy_matches_sorted[:5],
        "RapidFuzz": rapid_matches_sorted[:5],
        "Difflib": difflib_matches_sorted[:5],
        "TextDistance": textdistance_matches_sorted[:5]
    }

# Get the top 5 matches for all methods
matches = get_top_matches(model_input, product_codes)

# Print the results
for method, match_list in matches.items():
    print(f"\n{method} Matches:")
    for match in match_list:
        print(f"Model: {match[0]}, Match: {match[1]}%")
