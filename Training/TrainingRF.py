import json
import pandas as pd
from sklearn.model_selection import train_test_split, cross_validate, GridSearchCV
from sklearn.model_selection import cross_val_predict
from sklearn.model_selection import cross_val_score
from sklearn.ensemble import RandomForestClassifier 
from sklearn.metrics import roc_curve, auc
import matplotlib.pyplot as plt
import csv
import os
import numpy as np

# Load the JSON file with all 20 randomized feature sets
with open("randomized_feature_groups.json", "r") as f:
    feature_sets = json.load(f)


# Create directory for ROC plots
os.makedirs("roc_plots", exist_ok=True)

# Open CSV file to save results
csv_filename_CV = "model_results_CV.csv"
with open(csv_filename_CV, mode="w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["Set", "Feature Group", "Accuracy", "Precision", "Recall", "F1-score", "max_depth", "n_estimators", "min_samples_split", "min_samples_leaf", "criterion"])

csv_filename_CT = "model_results_crosstab.csv"
with open(csv_filename_CT, mode="w", newline="") as file:
    writer2 = csv.writer(file)
    writer2.writerow(["Set", "Feature Group", "Pred_0_Actual_0", "Pred_1_Actual_0", "Pred_0_Actual_1", "Pred_1_Actual_1"])

roc_data_by_group = {i: {'y_true': [], 'y_proba': []} for i in range(1, 6)}

# Loop through all 20 randomized sets
for iteration_index, selected_groups in enumerate(feature_sets):
    print(f"\n=== Training on Randomized Set {iteration_index + 1} ===\n")
    
    # Incrementally train models from Group 1 to Group 5
    for i in range(1, 6):
        selected_features = ["Classification"]
        for j in range(i):  
            selected_features.extend(selected_groups[f'Group {j+1}'])
        # Read the CSV with the selected features
        print (selected_features)
        df = pd.read_excel("dataset.xlsx", usecols=selected_features)

        X = df.drop(columns=["Classification"])
        y = df["Classification"]
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)
        # Grid Search
        gridsearchmodel = RandomForestClassifier(random_state=0)
        param_grid = {
            'max_depth':[3, 4, 5, 6,],
            'n_estimators':[100, 150, 200, 250], 
            'min_samples_split':[6, 11, 16],
            'min_samples_leaf':[4, 6, 8],
            'criterion':('gini', 'log_loss', 'entropy'),
        }
        grid_search = GridSearchCV(estimator=gridsearchmodel, param_grid=param_grid, cv=5, n_jobs=-1)
        grid_search.fit(X_train, y_train)
        # Create ML model
        model = RandomForestClassifier(max_depth=grid_search.best_params_['max_depth'], n_estimators=grid_search.best_params_['n_estimators'], min_samples_split=grid_search.best_params_['min_samples_split'],min_samples_leaf=grid_search.best_params_['min_samples_leaf'], criterion=grid_search.best_params_['criterion'], random_state=0)
        #model.fit(X_train, y_train)
       
       
        # Cross-validation crosstab
        y_pred = cross_val_predict(model, X, y, cv=5)
        crosstab = pd.crosstab(y, y_pred, rownames=['Actual'], colnames=['Predicted'])
        # CV probabilities for ROC
        y_proba = cross_val_predict(model, X, y, cv=5, method='predict_proba')[:, 1]
        fpr, tpr, _ = roc_curve(y, y_proba)
        roc_auc = auc(fpr, tpr)
        # Store for aggregate ROC
        roc_data_by_group[i]['y_true'].extend(y)
        roc_data_by_group[i]['y_proba'].extend(y_proba)
        # 5-fold cross-validation
        accuracy = cross_val_score(model, X, y, cv=5, scoring="accuracy").mean()
        precision = cross_val_score(model, X, y, cv=5, scoring="precision_macro").mean()
        recall = cross_val_score(model, X, y, cv=5, scoring="recall_macro").mean()
        f1 = cross_val_score(model, X, y, cv=5, scoring="f1_macro").mean()

        # Generate group name for reference
        group_name = " + ".join([f'Group {j+1}' for j in range(i)])

        # ROC for individual models for each group, uncomment to add.
        '''Plot and save individual ROC curve for this group
        plt.figure(figsize=(6, 5))
        plt.plot(fpr, tpr, label=f'AUC = {roc_auc:.2f}')
        plt.plot([0, 1], [0, 1], 'k--')
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title(f'ROC Curve - Set {iteration_index + 1} - {group_name}')
        plt.legend(loc='lower right')
        plt.tight_layout()
        safe_group_name = group_name.replace(' + ', '_').replace(' ', '')
        plt.savefig(f"roc_plots/roc_set{iteration_index + 1}_{safe_group_name}.png")
        plt.close()
        '''
        # Needs to be fixed. Right now Prints np.int64("Number") instead of only number
        values = [
            crosstab.loc[0, 0], crosstab.loc[0, 1],
            crosstab.loc[1, 0], crosstab.loc[1, 1]
        ]
        print(f"Set {iteration_index + 1}, {group_name}: Accuracy={accuracy:.4f}, Precision={precision:.4f}, Recall={recall:.4f}, F1-score={f1:.4f}")
        # Save results to CSV
        with open(csv_filename_CT, mode="a", newline="") as file:
            writer2 = csv.writer(file)
            writer2.writerow([iteration_index + 1, group_name, values])
        
        with open(csv_filename_CV, mode="a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([iteration_index + 1, group_name, accuracy, precision, recall, f1,
                            grid_search.best_params_['max_depth'],
                            grid_search.best_params_['n_estimators'],
                            grid_search.best_params_['min_samples_split'],
                            grid_search.best_params_['min_samples_leaf'],
                            grid_search.best_params_['criterion']
            ])

for i in range(1, 6):
    y_true = np.array(roc_data_by_group[i]['y_true'])
    y_proba = np.array(roc_data_by_group[i]['y_proba'])
    fpr, tpr, _ = roc_curve(y_true, y_proba)  
    roc_auc = auc(fpr, tpr)

    plt.figure(figsize=(6, 5))
    plt.plot(fpr, tpr, label=f'AUC = {roc_auc:.2f}')
    plt.plot([0, 1], [0, 1], 'k--')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title(f'Aggregated ROC - Group {" + ".join([str(j+1) for j in range(i)])}')
    plt.legend(loc='lower right')
    plt.tight_layout()
    group_tag = "_".join([f"Group{j+1}" for j in range(i)])
    plt.savefig(f"roc_plots/roc_aggregated_{group_tag}.png")
    plt.close()
print("\n Training completed! All results saved in 'model_results_CV.csv' and 'model_results_crosstab.")