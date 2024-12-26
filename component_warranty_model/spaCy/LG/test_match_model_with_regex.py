import pandas as pd
import re
from datetime import datetime
import os


lg_regex_patterns = {
    "Bravia OLED" : r"^(KD|XR)?[\s-]*\d{2}[\s-]*[aA]\d{1,4}[a-zA-Z0-9\-()+]*$",
    "32 inch" : r"^([A-Za-z]{2,4}?[\s-]*)?32[\s-]*[A-Za-z]{1,2}\d{1,4}[a-zA-Z0-9\-()+]*$",
    "43 inch & above" : r"^([A-Za-z]{2,4}?[\s-]*)?(4[3-9]|[5-9]\d{1,3}|[1-9]\d{3,})[\s-]*[A-Za-z]{1,2}\d{1,4}[a-zA-Z0-9\-()+]*$",
    "XR" : r"^XR[\s-]*[a-zA-Z0-9\-()+]*$",
    "LED" : r"^(KD|KDL|XR|KLV|K|UA)?[\s-]*\d{2}[\s-]*[xwrzspcXWRZSPU]{1,2}\d{1,4}[a-zA-Z0-9\-()+]*$",
    "A80J" : r"^([A-Za-z]{2,4}?[\s-]*)?\d{2,4}A80J[a-zA-Z0-9\-()+]*$",
    "A80K" : r"^([A-Za-z]{2,4}?[\s-]*)?\d{2,4}A80K[a-zA-Z0-9\-()+]*$",
    "A80K" : r"^([A-Za-z]{2,4}?[\s-]*)?\d{2,4}A80L[a-zA-Z0-9\-()+]*$",
    "A95K" : r"^([A-Za-z]{2,4}?[\s-]*)?\d{2,4}A95K[a-zA-Z0-9\-()+]*$",
    "A95L" : r"^([A-Za-z]{2,4}?[\s-]*)?\d{2,4}A95L[a-zA-Z0-9\-()+]*$",
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
