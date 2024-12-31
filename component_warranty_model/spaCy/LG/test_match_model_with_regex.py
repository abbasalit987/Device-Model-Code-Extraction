import pandas as pd
import re
from datetime import datetime
import os

lg_oled_pattern_01 = r"^(LG)?[\s-]*\d{2}[\s-]*[Ee][A-Za-z][a-zA-Z0-9\-()+]*$"
lg_oled_pattern_02 = r"^(OLED)?[\s-]*\d{2}[\s-]*[BCEGWZRbcegwzr][A-Za-z0-9][a-zA-Z0-9\-()+]*$"
lg_oled_77_to_97_inch_pattern_01 = r"^(LG)?[\s-]*(7[7-9]|8\d{1}|9[0-7])[\s-]*[Ee][A-Za-z][a-zA-Z0-9\-()+]*$"
lg_oled_77_to_97_inch_pattern_02 = r"^(OLED)?[\s-]*(7[7-9]|8\d{1}|9[0-7])[\s-]*[BCEGWZRbcegwzr][A-Za-z0-9][a-zA-Z0-9\-()+]*$"

lg_regex_patterns = {
    "OLED" : f"{lg_oled_pattern_01}|{lg_oled_pattern_02}",
    "32 inch & above" : r"^([A-Za-z]{2,4})?[\s-]*(3[2-9]|[4-9]\d{1,3}|[1-9]\d{3,})[\s-]*[a-zA-Z0-9\-()+]*$",
    "70 inch & above 4K LED" : r"^([A-Za-z]{2,4})?[\s-]*(7[0-9]|[8-9]\d{1,3}|[1-9]\d{3,})[\s-]*U[a-zA-Z0-9\-()+]*$",
    "QNED" : r"^\d{2,3}QNED[a-zA-Z0-9\-()+]*$",
    "77 - 97 inch OLED" : f"{lg_oled_77_to_97_inch_pattern_01}|{lg_oled_77_to_97_inch_pattern_02}",
}

file_path = 'component_warranty_model/Data/LG/extracted_models_lg.xlsx'
output_file_path = 'component_warranty_model/Data/LG/output_with_matches.xlsx'

df = pd.read_excel(file_path, sheet_name='Extracted Models 004')

def match_tags(model_code):
    tags = [tag for tag, pattern in lg_regex_patterns.items() if re.match(pattern, str(model_code.strip().replace(' ','')))]
    return tags

df['Tags'] = df['Model Code'].apply(lambda x: match_tags(x))

df = df[['Model Description', 'Model Code', 'Tags']]

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
sheet_name = f"Match_Results_{timestamp}"

if os.path.exists(output_file_path):
    with pd.ExcelWriter(output_file_path, engine='openpyxl', mode='a') as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=False)
else:
    with pd.ExcelWriter(output_file_path, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=False)

print(df[['Model Code', 'Tags']])
