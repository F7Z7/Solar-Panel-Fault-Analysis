import matplotlib
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
matplotlib.use('TkAgg')
df=pd.read_csv("C:\\Users\\farza\\MATLAB-SIMULINK\\Solar-Panel-Fault-Analysis\\Data_sets\\solar_sim_results_cleaned_valid.csv")

# Optional: sort by Irradiance or Temperature
# Calculate Power (P_PV)
df['P_PV'] = df['V_PV'] * df['I_PV']

# Set the style for the plots
sns.set_style("whitegrid")

# Create a figure with two subplots in one row
fig, axes = plt.subplots(1, 2, figsize=(15,5))

# Plot 1: Performance (Power) vs. Irradiance
sns.lineplot(ax=axes[0], x='Irradiance', y='P_PV', data=df, hue='Temperature', palette='viridis', marker='o')
axes[0].set_title('Performance (Power) vs. Irradiance')
axes[0].set_xlabel('Irradiance')
axes[0].set_ylabel('Power (P_PV)')
axes[0].legend(title='Temperature')

# Plot 2: Performance (Power) vs. Temperature
sns.lineplot(ax=axes[1], x='Temperature', y='P_PV', data=df, hue='Irradiance', palette='magma', marker='o')
axes[1].set_title('Performance (Power) vs. Temperature')
axes[1].set_xlabel('Temperature')
axes[1].set_ylabel('Power (P_PV)')
axes[1].legend(title='Irradiance')

plt.tight_layout()

plt.show()