import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, classification_report

os.environ["LOKY_MAX_CPU_COUNT"] = "8" 

# Load the preprocessed data
data = pd.read_excel('./preprocessed_data.xlsx')
data = data[~data['fg_level'].isin([-1, 0])]

# Separate features and target variable
X = data[['x', 'y']]
y = data['fg_level']

# Split the data into training and testing sets (80% train, 20% test)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# Create a Random Forest model with parallel processing (using all available cores)
rf_model = RandomForestClassifier(n_estimators=100, n_jobs=-1, random_state=42, class_weight="balanced")
rf_model.fit(X_train, y_train)

# Predict on the test set
y_pred = rf_model.predict(X_test)

# Evaluate the model using accuracy and F1-score
accuracy = accuracy_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred, average='weighted')  # Weighted F1-score for multiclass

# Display results
print("Accuracy:", accuracy)
print("F1-Score:", f1)
print("\nClassification Report:\n", classification_report(y_test, y_pred, zero_division=0))
