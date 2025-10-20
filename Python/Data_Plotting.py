import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import classification_report, confusion_matrix

# ===============================================
# 1. Load, Label, and Prepare Data
# ===============================================

# NOTE: Using the file directory from your original query for consistency,
# but reading the files uploaded in the chat.

# --- 1.1 Normal Data ---
# This is your 'Normal' operating condition dataset
df_normal = pd.read_csv("C:\\Users\\farza\\MATLAB-SIMULINK\\Solar-Panel-Fault-Analysis\\Data_sets\\solar_sim_results_cleaned_valid.csv")

df_normal['Fault_Type'] = 'Normal'
df_normal['P_PV'] = df_normal['V_PV'] * df_normal['I_PV']

# --- 1.2 Open Circuit (OC) Data ---
df_oc = pd.read_csv("C:\\Users\\farza\\MATLAB-SIMULINK\\Solar-Panel-Fault-Analysis\\Data_sets\\open_circuit_results.csv")
df_oc['Fault_Type'] = 'Open Circuit'
df_oc['P_PV'] = df_oc['V_PV'] * df_oc['I_PV']

# --- 1.3 Short Circuit (SC) Data ---
df_sc= pd.read_csv("C:\\Users\\farza\\MATLAB-SIMULINK\\Solar-Panel-Fault-Analysis\\Data_sets\\short_circuit_results.csv")
df_sc['Fault_Type'] = 'Short Circuit'
df_sc['P_PV'] = df_sc['V_PV'] * df_sc['I_PV']

# --- 1.4 Combine all data ---
df_combined = pd.concat([df_normal, df_oc, df_sc], ignore_index=True)

# Clean up (handle any potential Inf/NaN from simulation edge cases)
df_combined.replace([np.inf, -np.inf], np.nan, inplace=True)
df_combined.dropna(inplace=True)

print(f"Total Combined Samples after cleaning: {len(df_combined)}")
print("Fault Type Distribution:")
print(df_combined['Fault_Type'].value_counts())

# ===============================================
# 2. Preprocessing
# ===============================================

# 2.1 Encode the categorical target variable (Fault_Type)
le = LabelEncoder()
df_combined['Fault_Type_Encoded'] = le.fit_transform(df_combined['Fault_Type'])
target_names = le.classes_
print(f"\nTarget Labels Encoded: {list(zip(target_names, le.transform(target_names)))}")

# 2.2 Define Features (X) and Target (y)
# We use key electrical parameters and environmental factors
X = df_combined[['Irradiance', 'Temperature', 'V_PV', 'I_PV', 'P_PV']]
y = df_combined['Fault_Type_Encoded']

# 2.3 Train/Test split (Stratified to ensure balanced classes in test set)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42, stratify=y
)

# 2.4 Standardize features (CRITICAL for KNN distance calculations)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# ===============================================
# 3. Train KNN Classifier
# ===============================================
knn_classifier = KNeighborsClassifier(n_neighbors=5)
knn_classifier.fit(X_train_scaled, y_train)

# Predictions
y_pred = knn_classifier.predict(X_test_scaled)

# ===============================================
# 4. Evaluation
# ===============================================

print("\n" + "="*40)
print("       KNN CLASSIFICATION RESULTS")
print("="*40)

# 4.1 Classification Report
print("\n--- Classification Report ---")
print(classification_report(y_test, y_pred, target_names=target_names))

# 4.2 Confusion Matrix (Visualization)
cm = confusion_matrix(y_test, y_pred)
plt.figure(figsize=(6, 5))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
            xticklabels=target_names, yticklabels=target_names)
plt.title('Confusion Matrix for KNN Fault Classification')
plt.xlabel('Predicted Label')
plt.ylabel('True Label')
plt.show()

# ===============================================
# 5. Visualization: I-V Curve for Fault Analysis
# ===============================================

plt.figure(figsize=(8, 6))
# Scatter plot of I_PV vs V_PV colored by Fault Type
scatter = plt.scatter(df_combined['V_PV'], df_combined['I_PV'],
                      c=df_combined['Fault_Type_Encoded'],
                      cmap='viridis', alpha=0.7)
plt.xlabel("PV Voltage ($V_{PV}$)")
plt.ylabel("PV Current ($I_{PV}$)")
plt.title("I-V Curve Points Colored by Fault Type")
# Create a legend using the actual fault names
plt.legend(handles=scatter.legend_elements()[0], labels=target_names, title="Fault Type")
plt.grid(True)
plt.show()