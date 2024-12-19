import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.multioutput import MultiOutputClassifier
from sklearn.metrics import classification_report
import joblib

# Load data (you can load your dataset from a CSV file)
data = {
    "COMPANY": ["VISE", "VISE", "HAIER", "SAMSUNG", "LG", "LG", "SONY", "SANSUI", "TCL", "TCL", "METZ", "SKYWORTH", "PANASONIC", "AMSTRAD", "TOSHIBA", "PHILIPS", "XIAOMI"],
    "OFFER": [
        "2 YEARS COMPREHENSIVE WARRANTY",
        "1 YEARS COMPREHENSIVE WARRANTY",
        "2 Years Warranty i.e. 1 Year Standard Warranty+ 1 Years Extended Warranty (Comprehensive) exclusively on LED TV’s measuring 80cm and above purchased in India except Kerala. Labor charge will be paid by customer for extended warranty period.",
        "1+ 1 year Extended Warranty is applicable from the date of expiry of 1st year warranty, i.e. 1+1 year Applicable on SELL OUT with Invoice date as mentioned in consumer coverage details The 2nd year Extended Warranty is applicable only on panel.",
        "1 + 1 Year Warranty. (1 Year Comprehensive warranty & 2nd Year Only on panel)",
        "1+2 Comprehensive Year Warranty.",
        "2 Year Warranty (1 Year Comprehensive & 1 Year Only on Panel)",
        "1+1 YEAR Comprehensive Warranty",
        "2 YEARS COMPREHENSIVE WARRANTY",
        "3 YEARS Comprehensive WARRANTY",
        "2 YEARS COMPREHENSIVE WARRANTY",
        "2 YEARS COMPREHENSIVE WARRANTY",
        "1 Year Comprehensive Warranty",
        "2 Years Comprehensive Warranty.",
        "1 Year Comprehensive Warranty",
        "2 Years Comprehensive Warranty.",
        "1 Year Comprehensive Warranty"
    ],
    "BCW PERIOD": ["2Y", "1Y", "2Y", "1Y", "1Y", "3Y", "2Y", "1Y", "2Y", "3Y", "2Y", "2Y", "1Y", "2Y", "1Y", "2Y", "1Y"],
    "CW PERIOD": ["NA", "NA", "NA", "2Y", "2Y", "NA", "2Y", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA"],
    "OFFER CONDITIONS": [
        "NA", "NA", "Labor charge will be paid by customer for extended warranty period.", 
        "2nd year Extended Warranty is applicable only on panel.", "On all models except 32D310.", 
        "On OLED models only.", "On all Sony Bravia OLED TVs.", "NA", "NA", "Except 32D310, on all models.", 
        "NA", "NA", "NA", "NA", "NA", "NA", "On Select Models."
    ]
}

df = pd.DataFrame(data)

# Combine OFFER and OFFER CONDITIONS columns as a single text feature for classification
df['OFFER_TEXT'] = df['OFFER'] + " " + df['OFFER CONDITIONS']

# Vectorize the text using TF-IDF Vectorizer (more suitable for longer text)
vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
X = vectorizer.fit_transform(df['OFFER_TEXT'])

# Target variables
y = df[['BCW PERIOD', 'CW PERIOD']]

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Multi-output classifier using RandomForest
model = MultiOutputClassifier(RandomForestClassifier(n_estimators=100, random_state=42))
model.fit(X_train, y_train)

# Predictions
y_pred = model.predict(X_test)

# Evaluate the model
print("Classification Report (for BCW and CW Period):")
print(classification_report(y_test, y_pred, target_names=["BCW PERIOD", "CW PERIOD"]))

# Save the trained model and vectorizer
joblib.dump(model, 'multi_output_warranty_classifier.pkl')
joblib.dump(vectorizer, 'vectorizer.pkl')

print("Model training complete and saved.")
