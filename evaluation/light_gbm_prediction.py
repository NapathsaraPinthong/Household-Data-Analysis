import os
import pandas as pd
import lightgbm as lgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score, classification_report

os.environ["LOKY_MAX_CPU_COUNT"] = "8"

# Load the preprocessed data
data = pd.read_excel('./preprocessed_data.xlsx')
data = data[~data['fg_level'].isin([-1, 0])]

# Map labels to start from 0
label_mapping = {1: 0, 2: 1, 3: 2}
data['fg_level'] = data['fg_level'].map(label_mapping)

# Separate features and target variable
X = data[['x', 'y']]
y = data['fg_level']

# Split the data into training and testing sets (80% train, 20% test)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# Create a LightGBM dataset
train_data = lgb.Dataset(X_train, label=y_train)
test_data = lgb.Dataset(X_test, label=y_test, reference=train_data)

# Set parameters for LightGBM
params = {
    'objective': 'multiclass',  # Multiclass classification
    'num_class': len(y.unique()),  # Number of classes
    'metric': 'multi_logloss',  # Log loss for multiclass
    'boosting_type': 'gbdt',  # Gradient boosting decision tree
    'is_unbalance': True,  # Handles class imbalance
    'num_leaves': 31,
    'learning_rate': 0.05,
    'n_jobs': -1,
    'seed': 42
}

# Train the LightGBM model with early stopping
lgb_model = lgb.train(params, 
                      train_data, 
                      num_boost_round=100, 
                      valid_sets=[test_data], 
                      valid_names=['test'], 
                      callbacks=[lgb.early_stopping(stopping_rounds=10)])

# Predict on the test set
y_pred = lgb_model.predict(X_test)
y_pred = [list(row).index(max(row)) for row in y_pred]  # Convert probabilities to class predictions

# Inverse mapping to revert labels back to their original values
inverse_label_mapping = {v: k for k, v in label_mapping.items()}
y_pred = [inverse_label_mapping[label] for label in y_pred]
y_test = y_test.map(inverse_label_mapping)  # Revert y_test for comparison

# Evaluate the model using accuracy and F1-score
accuracy = accuracy_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred, average='weighted')  # Weighted F1-score for multiclass

# Display results
print("Accuracy:", accuracy)
print("F1-Score:", f1)
print("\nClassification Report:\n", classification_report(y_test, y_pred, zero_division=0))