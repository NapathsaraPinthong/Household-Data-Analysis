import os
import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, f1_score, classification_report

os.environ["LOKY_MAX_CPU_COUNT"] = "8" 

# Load the preprocessed data
data = pd.read_excel('./preprocessed_data.xlsx')
data = data[~data['fg_level'].isin([-1, 0])]

# Separate features and target variable
X = data[['x', 'y']]
y = data['fg_level']

# Split the data into training and testing sets (e.g., 80% train, 20% test)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# Set up the SVC model and define the hyperparameter grid for tuning
param_grid = {
    'C': [0.1, 1, 10],       # Regularization parameter
    'gamma': ['scale', 0.1, 1]  # Kernel coefficient
}
svm_model = SVC(kernel='rbf', random_state=42)

# Use GridSearchCV for hyperparameter tuning with parallelism
grid_search = GridSearchCV(svm_model, param_grid, cv=5, n_jobs=-1, scoring='f1_weighted')
grid_search.fit(X_train, y_train)

# Get the best model from grid search
best_model = grid_search.best_estimator_

# Predict on the test set using the best model
y_pred = best_model.predict(X_test)

# Evaluate the model using accuracy and F1-score
accuracy = accuracy_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred, average='weighted')

# Display results
print("Best Parameters:", grid_search.best_params_)
print("Accuracy:", accuracy)
print("F1-Score:", f1)
print("\nClassification Report:\n", classification_report(y_test, y_pred, zero_division=0))
