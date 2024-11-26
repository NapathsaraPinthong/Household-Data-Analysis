import os
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.metrics import f1_score, classification_report, confusion_matrix
from time import perf_counter

# Limit CPU usage for parallel processing
os.environ["LOKY_MAX_CPU_COUNT"] = "8"

def process_and_evaluate_node_embeddings(node_embedding_files, output_dir='./result/'):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    results = []
    
    for file in node_embedding_files:
        print(f"Processing {file}...")
        t_start = perf_counter()

        # Load node embeddings and household fragile level
        node_embeddings = pd.read_excel(file)
        hh_fg_level = pd.read_excel('../data/dataset/edge/hh-fg_level.xlsx', header=None, names=['id', 'fg_level'])

        # Filter rows where node_target == 'household'
        household_nodes = node_embeddings[node_embeddings['node_target'] == 'household'].copy()

        # Split 'value' into 128 dimensions (assuming comma-separated values)
        dimension_columns = [f'dim_{i}' for i in range(128)]
        new_columns = household_nodes['value'].str.strip('[]').str.split(',', expand=True).astype(float)
        new_columns.columns = dimension_columns

        # Concatenate the new columns to the original DataFrame
        household_nodes = pd.concat([household_nodes, new_columns], axis=1)

        # Remove 'hh' prefix from 'node_id' for matching and convert to integer
        household_nodes['id'] = household_nodes['node_id'].str.replace('hh', '').astype(int)

        # Merge with hh_fg_level on 'id'
        merged_data = pd.merge(household_nodes, hh_fg_level, on='id', how='inner')

        # Select the required columns
        data = merged_data[['node_id', *dimension_columns, 'fg_level']]

        # Filter out unwanted fragile levels (-1, 0)
        data = data[~data['fg_level'].isin([-1, 0])]

        # Separate features and target variable
        X = data[dimension_columns]
        y = data['fg_level']

        # Split the data into training and testing sets (e.g., 80% train, 20% test)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

        # Set up the SVC model with fixed parameters
        svc_model = SVC(kernel='rbf', C=10, gamma=0.1, random_state=42)
        svc_model.fit(X_train, y_train)

        # Predict on the test set
        y_pred = svc_model.predict(X_test)

        # Evaluate the model
        f1 = f1_score(y_test, y_pred, average='weighted')

        # Generate a classification report
        report_dict = classification_report(y_test, y_pred, zero_division=0, output_dict=True)
        results_df = pd.DataFrame(report_dict).transpose()

        # Extract walk length and window size from filename
        base_name = os.path.basename(file).replace('.xlsx', '')  # Remove the file extension
        walk_length, window_size = map(int, base_name.split('_')[2:4])

        # Save the classification report
        output_file = os.path.join(output_dir, f"classification_report_{walk_length}_{window_size}.xlsx")
        results_df.to_excel(output_file, index=True)

        # Generate a confusion matrix
        conf_matrix = confusion_matrix(y_test, y_pred)
        conf_matrix_df = pd.DataFrame(
            conf_matrix, 
            index=[f"Actual {label}" for label in sorted(y.unique())],
            columns=[f"Predicted {label}" for label in sorted(y.unique())]
        )

        # Combine the classification report and confusion matrix
        with pd.ExcelWriter(os.path.join(output_dir, f"classification_report_{walk_length}_{window_size}.xlsx")) as writer:
            results_df.to_excel(writer, sheet_name='Classification Report', index=True)
            conf_matrix_df.to_excel(writer, sheet_name='Confusion Matrix', index=True)

        t_stop = perf_counter()
        print("Elapsed time in seconds:", t_stop-t_start)
        print(f"Classification report and confusion matrix saved to {output_file}")
        
        results.append({'walk_length': walk_length, 'window_size': window_size, 'f1_score': f1})

    # Generate a plot of F1-scores
    plot_results(results, output_dir)

def plot_results(results, output_dir):
    results_df = pd.DataFrame(results)
    results_df['walk_window'] = results_df['walk_length'].astype(str) + '_' + results_df['window_size'].astype(str)
    
    plt.figure(figsize=(10, 6))
    plt.plot(results_df['walk_window'], results_df['f1_score'], marker='o')
    plt.xlabel('Walk Length & Window Size (walk_window)', fontsize=12)
    plt.ylabel('Weighted F1-Score', fontsize=12)
    plt.title('F1-Score vs Walk Length & Window Size', fontsize=14)
    plt.xticks(rotation=45, ha='right')
    plt.grid(True)
    plt.tight_layout()

    plot_file = os.path.join(output_dir, "f1_score_plot.png")
    plt.savefig(plot_file)
    print(f"F1-score plot saved to {plot_file}")

# List of node embedding files
node_embedding_files = [
    '../main/result/node_embeddings_50_5_128.xlsx',
    '../main/result/node_embeddings_70_5_128.xlsx',
    '../main/result/node_embeddings_100_5_128.xlsx',
    '../main/result/node_embeddings_50_10_128.xlsx',
    '../main/result/node_embeddings_70_10_128.xlsx',
    '../main/result/node_embeddings_100_10_128.xlsx',
    '../main/result/node_embeddings_50_15_128.xlsx',
    '../main/result/node_embeddings_70_15_128.xlsx',
    '../main/result/node_embeddings_100_15_128.xlsx'
]

# Run the function
process_and_evaluate_node_embeddings(node_embedding_files)
