import pandas as pd
import re
from datetime import datetime
import os

panasonic_4k_tv_pattern = r"^(TH)?[\s-]*\d{2}[\s-]*[A-Za-z]X[a-zA-Z0-9\-()+]*$"
panasonic_smart_tv_pattern = r"^(TH)?[\s-]*\d{2}[\s-]*[A-Za-z]S[a-zA-Z0-9\-()+]*$"

panasonic_regex_patterns = {
    "4K & Smart" : f"{panasonic_4k_tv_pattern}|{panasonic_smart_tv_pattern}",
    "OLED" : r"^(TH)?[\s-]*\d{2}[\s-]*[A-Za-z]Z[a-zA-Z0-9\-()+]*$",
    "55 & 65 OLED" : r"^(TH)?[\s-]*(55|65)[\s-]*[A-Za-z]Z[a-zA-Z0-9\-()+]*$",
}

file_path = 'component_warranty_model/Data/Panasonic/extracted_models_panasonic.xlsx'
output_file_path = 'component_warranty_model/Data/Panasonic/output_with_matches.xlsx'

df = pd.read_excel(file_path, sheet_name='Extracted Models 003')

def match_tags(model_code):
    tags = [tag for tag, pattern in panasonic_regex_patterns.items() if re.match(pattern, str(model_code.strip().replace(' ','')))]
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
