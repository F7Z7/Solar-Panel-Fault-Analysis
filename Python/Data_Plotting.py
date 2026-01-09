import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.lines import Line2D
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import classification_report, confusion_matrix
import joblib
import os

df_normal = pd.read_csv("C:\\Users\\farza\\MATLAB-SIMULINK\\Solar-Panel-Fault-Analysis\\Data_sets\\solar_sim_results_cleaned_valid.csv")

df_normal['Fault_Type'] = 'Normal'

df_oc = pd.read_csv("C:\\Users\\farza\\MATLAB-SIMULINK\\Solar-Panel-Fault-Analysis\\Data_sets\\open_circuit_results.csv")
df_oc['Fault_Type'] = 'Open Circuit'


df_sc= pd.read_csv("C:\\Users\\farza\\MATLAB-SIMULINK\\Solar-Panel-Fault-Analysis\\Data_sets\\short_circuit_results.csv")
df_sc['Fault_Type'] = 'Short Circuit'

df_combined = pd.concat([df_normal, df_oc, df_sc], ignore_index=True)

df_combined.replace([np.inf, -np.inf], np.nan, inplace=True)
df_combined.dropna(inplace=True)

print(f"Total Combined Samples after cleaning: {len(df_combined)}")
print("Fault Type Distribution:")
print(df_combined['Fault_Type'].value_counts())

le = LabelEncoder()
df_combined['Fault_Type_Encoded'] = le.fit_transform(df_combined['Fault_Type'])
target_names = le.classes_
print(f"\nTarget Labels Encoded: {list(zip(target_names, le.transform(target_names)))}")

X = df_combined[['Irradiance', 'Temperature', 'V_PV', 'I_PV']]
y = df_combined['Fault_Type_Encoded']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42, stratify=y
)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

knn_classifier = KNeighborsClassifier(n_neighbors=5)
knn_classifier.fit(X_train_scaled, y_train)

# Predictions
y_pred = knn_classifier.predict(X_test_scaled)




# 4.1 Classification Report
print(" Classification Report ")
print(classification_report(y_test, y_pred, target_names=target_names))

cm = confusion_matrix(y_test, y_pred)
plt.figure(figsize=(6, 5))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
            xticklabels=target_names, yticklabels=target_names)
plt.title('Confusion Matrix for KNN Fault Classification')
plt.xlabel('Predicted Label')
plt.ylabel('True Label')
plt.show()

plt.figure(figsize=(8, 6))
# Scatter plot of I_PV vs V_PV colored by Fault Type
scatter = plt.scatter(df_combined['V_PV'], df_combined['I_PV'],
                      c=df_combined['Fault_Type_Encoded'],
                      cmap='viridis', alpha=0.7)
plt.xlabel("PV Voltage ($V_{PV}$)")
plt.ylabel("PV Current ($I_{PV}$)")
plt.title("I-V Curve Points Colored by Fault Type")
colors = plt.cm.viridis(np.linspace(0, 1, len(target_names)))

legend_elements = [
    Line2D([0], [0], marker='o', color='w',
           label=target_names[i],
           markerfacecolor=colors[i], markersize=8)
    for i in range(len(target_names))
]

plt.legend(handles=legend_elements, title="Fault Type")
plt.grid(True)
plt.show()


## saveign the model and scaler

MODEL_DIR = "models"
os.makedirs(MODEL_DIR, exist_ok=True)

joblib.dump(knn_classifier, f"{MODEL_DIR}/knn_oc_sc_classifier.pkl")
joblib.dump(scaler, f"{MODEL_DIR}/oc_sc_scaler.pkl")
joblib.dump(le, f"{MODEL_DIR}/fault_label_encoder.pkl")