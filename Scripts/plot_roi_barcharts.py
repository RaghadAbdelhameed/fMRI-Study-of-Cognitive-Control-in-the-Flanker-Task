import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import os

# List of all the regions we generated masks for
regions = [
    "Fusiform_Gyrus_Right",
    "LOC_sup_Right",
    "PCG",
    "LOC_inf_Right1",
    "Fusiform_Gyrus_Left",
    "LOC_sup_Left",
    "Insular_Cortex_Left",
    "LOC_inf_Right2"
]

# Labels for the X-axis
conditions = ['incong', 'cong', 'incong - cong']
copes = ['cope1', 'cope2', 'cope3']

print("Generating bar charts...")

for region in regions:
    data_means = []
    data_ci = []
    data_pvals = []
    
    # Read data for all 3 copes for the current region
    for cope in copes:
        filename = f"Stats_{region}_{cope}.txt"
        
        if not os.path.exists(filename):
            print(f"Warning: {filename} not found. Skipping {region}.")
            continue
            
        # Load the 26 subjects' data
        data = np.loadtxt(filename)
        
        # Calculate Mean
        mean_val = np.mean(data)
        
        # Calculate 95% Confidence Interval (1.96 * Standard Error)
        se = stats.sem(data)
        ci = 1.96 * se
        
        # Calculate 1-sample t-test against 0 for significance
        t_stat, p_val = stats.ttest_1samp(data, 0)
        
        data_means.append(mean_val)
        data_ci.append(ci)
        data_pvals.append(p_val)
    
    # Skip plotting if data is missing
    if len(data_means) < 3:
        continue

    # Create the figure and axis
    fig, ax = plt.subplots(figsize=(8, 6))
    positions = [1, 2, 3]
    
    # Draw bars and error lines
    for i in range(3):
        pos = positions[i]
        mean = data_means[i]
        ci = data_ci[i]
        p_val = data_pvals[i]
        
        # Absolute mean for the bar height (as done in the study's script)
        abs_mean = abs(mean)
        y_min = abs_mean - ci
        y_max = abs_mean + ci
        
        # Draw the bar
        ax.bar(pos, abs_mean, color='gray', width=0.4, alpha=0.7)
        
        # Draw the error line (95% CI)
        ax.plot([pos, pos], [y_min, y_max], color='black', linewidth=1.5)
        
        # Determine the number of stars based on p-value
        if p_val <= 0.001:
            stars = '**'
        elif p_val <= 0.05:
            stars = '*'
        else:
            stars = ''
            
        # Draw the stars slightly above the highest point of the error bar
        if stars:
            ax.text(pos, y_max + 0.05, stars, ha='center', va='bottom', color='green', fontsize=20)
            
    # Formatting the plot
    ax.set_title(f"{region.replace('_', ' ')} using Spherical Mask")
    ax.set_xticks(positions)
    ax.set_xticklabels(conditions)
    ax.set_ylabel('Mean Z-Statistic')
    
    # Set y-axis lower limit to 0 for better visualization
    ax.set_ylim(bottom=0)
    
    # Save the plot
    output_filename = f"BarChart_{region}.png"
    plt.savefig(output_filename, bbox_inches='tight')
    plt.close() # Close the figure to free memory
    
    print(f"Saved {output_filename}")

print("All charts generated successfully!")
