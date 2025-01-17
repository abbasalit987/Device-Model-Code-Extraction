import pandas as pd
import re
from datetime import datetime
import os

samsung_regex_patterns = {
    "LED" : r"^[Uu][A-Za-z][\s-]*\d{2}[\s-]*[a-zA-Z0-9\-()+]*$",
    "Neo QLED" : r"^[Qq][A-Za-z][\s-]*\d{2}[\s-]*QN[a-zA-Z0-9\-()+]*$"
}

file_path = 'component_warranty_model/Data/Samsung/extracted_models_samsung.xlsx'
output_file_path = 'component_warranty_model/Data/Samsung/output_with_matches.xlsx'

df = pd.read_excel(file_path, sheet_name='Extracted Models 001')

def match_tags(model_code):
    tags = [tag for tag, pattern in samsung_regex_patterns.items() if re.match(pattern, str(model_code.strip().replace(' ','')))]
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