import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.svm import LinearSVC
from sklearn.metrics import accuracy_score, f1_score, classification_report

os.environ["LOKY_MAX_CPU_COUNT"] = "8" 

# Load the preprocessed data
data = pd.read_excel('./preprocessed_data.xlsx')

# Separate features and target variable
X = data[['x', 'y']]
y = data['fg_level']

# Split the data into training and testing sets (80% train, 20% test)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# SVM model with parallel processing using LinearSVC (using all available cores)
svm_model = LinearSVC(random_state=42, max_iter=10000)
svm_model.fit(X_train, y_train)
svm_pred = svm_model.predict(X_test)

# Evaluate SVM model
svm_accuracy = accuracy_score(y_test, svm_pred)
svm_f1 = f1_score(y_test, svm_pred, average='weighted')
print("SVM Accuracy:", svm_accuracy)
print("SVM F1-Score:", svm_f1)
print("\nSVM Classification Report:\n", classification_report(y_test, svm_pred, zero_division=0))
