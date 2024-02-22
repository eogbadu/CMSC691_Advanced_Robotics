import os
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import scipy.stats as stats
import numpy as np
from pandas.plotting import table 



# Constants
ANALYSIS_PATH = 'analysis'

def read_results():
   # Get the current directory
   current_directory = os.getcwd()

   processed_path = os.path.join(current_directory, 'processed_data')

   #create excel from the results_df
   results_df = pd.read_excel(os.path.join(processed_path,'mturk_results.xlsx'))
   
   return results_df

def by_image_analyze(mturk_results):
    # Count the total number of entries with and without images
    total_with_image = mturk_results[mturk_results['with_image'] == 1]['matching'].count()
    total_without_image = mturk_results[mturk_results['with_image'] == 0]['matching'].count()

    # Count the number of matches with and without images
    matches_with_image = mturk_results[(mturk_results['with_image'] == 1) & (mturk_results['matching'] == 1)]['matching'].count()
    matches_without_image = mturk_results[(mturk_results['with_image'] == 0) & (mturk_results['matching'] == 1)]['matching'].count()

    # Calculate the percentage of matches for entries with images
    percentage_matches_with_image = (matches_with_image / total_with_image) * 100 if total_with_image > 0 else 0

    # Calculate the percentage of matches for entries without images
    percentage_matches_without_image = (matches_without_image / total_without_image) * 100 if total_without_image > 0 else 0

    # Calculate standard errors
    error_with_image = (percentage_matches_with_image / 100) * ((total_with_image - matches_with_image) / total_with_image)**0.5 if total_with_image > 0 else 0
    error_without_image = (percentage_matches_without_image / 100) * ((total_without_image - matches_without_image) / total_without_image)**0.5 if total_without_image > 0 else 0

    # (Total counts, matches, percentages, errors, DataFrame creation)

    # Create a 2x2 contingency table
    observed_matches_with_image = matches_with_image
    observed_non_matches_with_image = total_with_image - matches_with_image
    observed_matches_without_image = matches_without_image
    observed_non_matches_without_image = total_without_image - matches_without_image

    contingency_table = [
        [observed_matches_with_image, observed_non_matches_with_image],
        [observed_matches_without_image, observed_non_matches_without_image]
    ]

    is_significant = False
    
    try:
        # Perform the Chi-Square test
        chi2, p, _, _ = stats.chi2_contingency(contingency_table)

        print("Chi-Square Statistic:", chi2)
        print("P-value:", p)

        # Determine the significance level (e.g., 0.05)
        alpha = 0.05

        # Determine if the difference is significant based on the p-value
        is_significant = p < alpha
    except RuntimeWarning as warning:
            print("RuntimeWarning:", warning)
    except Exception as e:
        # Handle any other exceptions (generic Exception)
        print("Exception:", e)
        
    # Create a bar plot with error bars using Matplotlib
    categories = ['With Image', 'Without Image']
    percentages = [percentage_matches_with_image, percentage_matches_without_image]
    errors = [error_with_image, error_without_image]
    sample_sizes = [total_with_image, total_without_image]  # Add sample sizes here


    fig, ax = plt.subplots()
    x = range(len(categories))
    bar_width = 0.35

    bars = ax.bar(x, percentages, width=bar_width, align='center', alpha=0.7, yerr=errors, capsize=5)
    ax.set_xticks(x)
    ax.set_xticklabels(categories)
    ax.set_ylabel('Classification Accuracy %')
    ax.set_title('Classification Accuracy with and without Images')

    # Set y-axis limits to range from 0 to 100
    ax.set_ylim(0, 100)

    # Add sample size labels at the bottom of the bars
    #for i, bar in enumerate(bars):
    #    ax.text(bar.get_x() + bar.get_width() / 2, 0, f'n={sample_sizes[i]}', 
    #            ha='center', va='bottom', fontsize=12, color='black')
        
    # Add significance labels to the bars
    if is_significant:
        ax.annotate("*", (x[0], percentages[0] + 5), ha='center', fontsize=12, color='black')

    # Add percentages to the top of each bar
    for i, bar in enumerate(bars):
        ax.text(bar.get_x() + bar.get_width() / 2, percentages[i] + 5, f'{percentages[i]:.1f}%', 
                ha='center', va='bottom', fontsize=12, color='black')

    # Save the plot as an png
    plt.savefig(f'{ANALYSIS_PATH}/mturk_by_image_analysis.png')
    plt.show()



def format_values(val):
    if isinstance(val, float):
        # For p-values
        if val < 1:
            return f"{val:.3f}"
        # For accuracy
        else:
            return f"{val:.2f}"
    return val


def render_mpl_table(df, filename): 
    col_width = 3.0  # adjust as necessary
    row_height = 0.625  # adjust as necessary
    font_size = 10
    bbox = [0, 0, 1, 1]
    ax = None

    size = (np.array(df.shape[::-1]) + np.array([0, 1])) * np.array([col_width, row_height])
    fig, ax = plt.subplots(figsize=size)
    ax.axis('off')

    mpl_table = table(ax, df, loc='center', bbox=bbox)
    mpl_table.auto_set_font_size(False)
    mpl_table.set_fontsize(font_size)

    # Apply styles to the table
    for k, cell in mpl_table._cells.items():
        cell.set_linewidth(0)
        cell.set_text_props(color='black')
        if k[0] == 0:
            cell.set_fontsize(font_size + 2)  # Make the header a bit larger
            cell.set_linewidth(0)  # No line for the header
            cell.set_text_props(weight='bold')
        elif k[1] == 0:
            cell.set_linewidth(1)  # Add line at the left of the table
        elif k[1] == len(df.columns) - 1:
            cell.set_linewidth(1)  # Add line at the right of the table

    # Add a horizontal line at the bottom of the header and above the last row
    for col, cell in enumerate(df.columns):
        mpl_table[(0, col)].set_edgecolor('black')  # Header bottom line
        mpl_table[(0, col)].set_linewidth(1)
        mpl_table[(len(df)-1, col)].set_edgecolor('black')  # Last row top line
        mpl_table[(len(df)-1, col)].set_linewidth(1)

    plt.savefig(f'{ANALYSIS_PATH}/{filename}.png', bbox_inches='tight')
    plt.show() 


def calculate_standard_error(matches, total):
    if total <= 0:
        return 0
    return (100 / total) * np.sqrt((matches / total) * (1 - matches / total))


def by_response_analyze(mturk_results):
    # Group the data by the 'submitted_answer' column
    grouped_by_submitted_answer = mturk_results.groupby('submitted_answer')

    categories = []
    percentages_with_image = []
    percentages_without_image = []
    sample_sizes_with_image = []
    sample_sizes_without_image = []
    errors_with_image = []
    errors_without_image = []
    p_values = {}


    # Prepare a dictionary for the DataFrame
    data = {
        'Accuracy Without Image (%)': [],
        'No. Correct Without Image': [],
        'No. Chosen Without Image': [],
        'Accuracy With Image (%)': [],
        'No. Correct With Image': [],
        'No. Chosen With Image': [],
        'p-value': []
    }

    for submitted_answer, group in grouped_by_submitted_answer:
        total_with_image = group[group['with_image'] == 1]['matching'].count()
        total_without_image = group[group['with_image'] == 0]['matching'].count()

        matches_with_image = group[(group['with_image'] == 1) & (group['matching'] == 1)]['matching'].count()
        matches_without_image = group[(group['with_image'] == 0) & (group['matching'] == 1)]['matching'].count()

        # Calculate the percentage of matches for entries with and without images
        percentage_matches_with_image = (matches_with_image / total_with_image) * 100 if total_with_image > 0 else 0
        percentage_matches_without_image = (matches_without_image / total_without_image) * 100 if total_without_image > 0 else 0

        categories.append(submitted_answer)
        percentages_with_image.append(percentage_matches_with_image)
        percentages_without_image.append(percentage_matches_without_image)
        sample_sizes_with_image.append(total_with_image)
        sample_sizes_without_image.append(total_without_image)
        errors_with_image.append(calculate_standard_error(matches_with_image, total_with_image))
        errors_without_image.append(calculate_standard_error(matches_without_image, total_without_image))

        try:
            _, p_value = stats.ttest_ind(
                group[group['with_image'] == 1]['matching'],
                group[group['with_image'] == 0]['matching'],
                equal_var=False
            )
            p_values[submitted_answer] = p_value
        except RuntimeWarning as warning:
            print("RuntimeWarning:", warning)
            p_values[submitted_answer] = 'N/A'
        except Exception as e:
            print("Exception:", e)
            p_values[submitted_answer] = 'N/A'
        
        # Store values in the data dictionary
        data['Accuracy Without Image (%)'].append(round(percentage_matches_without_image, 2))
        data['No. Correct Without Image'].append(matches_without_image)
        data['No. Chosen Without Image'].append(total_without_image)
        data['Accuracy With Image (%)'].append(round(percentage_matches_with_image, 2))
        data['No. Chosen With Image'].append(total_with_image)
        data['No. Correct With Image'].append(matches_with_image)
        
        data['p-value'].append(round(p_values[submitted_answer], 3) if isinstance(p_values[submitted_answer], float) else p_values[submitted_answer])

    # Create a bar plot with error bars
    plt.figure(figsize=(12, 6))
    x = np.arange(len(categories))
    width = 0.35

    # Plotting bars for 'with image' and 'without image' with error bars
    bar1 = plt.bar(x - width/2, percentages_with_image, width, label='With Image', yerr=errors_with_image, capsize=5)
    bar2 = plt.bar(x + width/2, percentages_without_image, width, label='Without Image', yerr=errors_without_image, capsize=5)

    # Set y-axis limits to range from 0 to 100, with some padding
    #plt.ylim(0, 110)  # Adjusted to provide some space for labels

    plt.xlabel('Submitted Answer Categories')
    plt.ylabel('Classification Accuracy %')
    plt.title('Classification Accuracy by Submitted Answer Categories')
    
    # Adjust the bottom margin to accommodate the rotated category labels and the x-axis title
    plt.subplots_adjust(bottom=0.2)  # Increase the bottom margin to provide more space for labels and title

    # Set x-ticks and rotate the labels to ensure they fit and are readable
    plt.xticks([i + width / 2 for i in x], categories, rotation=45, ha='right')

    plt.legend()

    # Use tight_layout to automatically adjust the plot to fit into the figure area neatly
    plt.tight_layout()

    # Increase the top margin of the plot to have more space for p-values and asterisks
    plt.subplots_adjust(top=0.85)

    # Set the y-axis limit higher to accommodate the significance markers
    plt.ylim(0, max(max(percentages_with_image), max(percentages_without_image)) + 15)  # Adjust as needed for your data

   # Iterate over each category for calculating significance and plotting
    for i, category in enumerate(categories):
        
        is_significant = isinstance(p_values[category], float) and p_values[category] < 0.05

        # Coordinates for the significance line
        x1, x2 = i - width/2, i + width/2
        y = max(percentages_with_image[i], percentages_without_image[i]) + 3  # Top of the highest bar for this category
        h = 2  # Increase this for more height
        col = 'black'  # Color of the significance line

        # Sample size at the bottom of the bar
        #bottom_offset = 6  # Adjust this value as needed to position the text below the bars
        #plt.text(x1, bottom_offset, f'n={sample_sizes_with_image[i]}', ha='center', va='top', color='black')
        #plt.text(x2, bottom_offset, f'n={sample_sizes_without_image[i]}', ha='center', va='top', color='black')

        if is_significant:
            # Draw the significance line
            plt.plot([x1, x1, x2, x2], [y, y+h, y+h, y], lw=1.5, c=col)
            
            # Add asterisk(s) based on the level of significance
            sig_str = '*' * int(-np.log10(p_values[category]) // 1)
            plt.text((x1+x2)*.5, y+h, sig_str, ha='center', va='bottom', color=col)
            
            # Print the p-value above the asterisk
            plt.text((x1+x2)*.5, y+h*2+3, f'p={p_values[category]:.3f}', ha='center', va='bottom', color=col)

    # Create a DataFrame
    response_analysis_df = pd.DataFrame(data, index=grouped_by_submitted_answer.groups.keys())

    # Apply formatting to the entire DataFrame
    #response_analysis_df = df.applymap(format_values)

    # Save the plot as an png
    plt.savefig(f'{ANALYSIS_PATH}/mturk_submitted_answer_analysis.png')
    plt.show()

    response_analysis_df['p-value'] = response_analysis_df['p-value'].apply(append_significance_asterisks)

    return response_analysis_df

def calculate_standard_error(matches, total):
    if total <= 0:
        return 0
    return (100 / total) * np.sqrt((matches / total) * (1 - matches / total))

def by_category_analyze(mturk_results):
    
    # Group the data by the 'real_output' column
    grouped_by_real_output = mturk_results.groupby('real_output')

    categories = []
    percentages_with_image = []
    percentages_without_image = []
    sample_sizes_with_image = []
    sample_sizes_without_image = []
    errors_with_image = []
    errors_without_image = []
    p_values = {}

    # Prepare a dictionary for the DataFrame
    data = {
        'Accuracy Without Image (%)': [],
        'No. Correct Without Image': [],
        'No. Total Without Image': [],
        'Accuracy With Image (%)': [],
        'No. Correct With Image': [],
        'No. Total With Image': [],
        'p-value': []
    }

    for real_output, group in grouped_by_real_output:
        total_with_image = group[group['with_image'] == 1]['matching'].count()
        total_without_image = group[group['with_image'] == 0]['matching'].count()

        matches_with_image = group[(group['with_image'] == 1) & (group['matching'] == 1)]['matching'].count()
        matches_without_image = group[(group['with_image'] == 0) & (group['matching'] == 1)]['matching'].count()

        # Calculate the percentage of matches for entries with and without images
        percentage_matches_with_image = (matches_with_image / total_with_image) * 100 if total_with_image > 0 else 0
        percentage_matches_without_image = (matches_without_image / total_without_image) * 100 if total_without_image > 0 else 0

        categories.append(real_output)
        percentages_with_image.append(percentage_matches_with_image)
        percentages_without_image.append(percentage_matches_without_image)
        sample_sizes_with_image.append(total_with_image)
        sample_sizes_without_image.append(total_without_image)
        errors_with_image.append(calculate_standard_error(matches_with_image, total_with_image))
        errors_without_image.append(calculate_standard_error(matches_without_image, total_without_image))

        # Perform a t-test to check for significance between the two categories
        try:
            _, p_value = stats.ttest_ind(
                group[group['with_image'] == 1]['matching'],
                group[group['with_image'] == 0]['matching'],
                equal_var=False
            )
            p_values[real_output] = p_value
        except RuntimeWarning as warning:
            print("RuntimeWarning:", warning)
            p_values[real_output] = 'N/A'
        except Exception as e:
            print("Exception:", e)
            p_values[real_output] = 'N/A'

        # Store values in the data dictionary
        data['Accuracy Without Image (%)'].append(round(percentage_matches_without_image, 2))
        data['No. Correct Without Image'].append(matches_without_image)
        data['No. Total Without Image'].append(total_without_image)
        data['Accuracy With Image (%)'].append(round(percentage_matches_with_image, 2))
        data['No. Correct With Image'].append(matches_with_image)
        data['No. Total With Image'].append(total_with_image)
        data['p-value'].append(round(p_values[real_output], 3) if isinstance(p_values[real_output], float) else p_values[real_output])

    # Create a bar plot with error bars
    plt.figure(figsize=(12, 6))
    x = np.arange(len(categories))
    width = 0.35

    # Plotting bars for 'with image' and 'without image' with error bars
    bar1 = plt.bar(x - width/2, percentages_with_image, width, label='With Image', yerr=errors_with_image, capsize=5)
    bar2 = plt.bar(x + width/2, percentages_without_image, width, label='Without Image', yerr=errors_without_image, capsize=5)

    # Set y-axis limits to range from 0 to 100, with some padding
    #plt.ylim(0, 110)  # Adjusted to provide some space for labels

    plt.xlabel('Control Signal Categories')
    plt.ylabel('Classification Accuracy %')
    plt.title('Classification Accuracy by Control Signal Categories')
    
    # Adjust the bottom margin to accommodate the rotated category labels and the x-axis title
    plt.subplots_adjust(bottom=0.2)  # Increase the bottom margin to provide more space for labels and title

    # Set x-ticks and rotate the labels to ensure they fit and are readable
    plt.xticks([i + width / 2 for i in x], categories, rotation=45, ha='right')

    plt.legend()

    # Use tight_layout to automatically adjust the plot to fit into the figure area neatly
    plt.tight_layout()
    
    # Increase the top margin of the plot to have more space for p-values and asterisks
    plt.subplots_adjust(top=0.85)

    # Set the y-axis limit higher to accommodate the significance markers
    plt.ylim(0, max(max(percentages_with_image), max(percentages_without_image)) + 10)  # Adjust as needed for your data

    
   # Iterate over each category for calculating significance and plotting
    for i, category in enumerate(categories):
        
        is_significant = isinstance(p_values[category], float) and p_values[category] < 0.05

        # Coordinates for the significance line
        x1, x2 = i - width/2, i + width/2
        y, h, col = max(percentages_with_image[i], percentages_without_image[i]) + 1, 1, 'black'

        if is_significant:
            # Draw the significance line
            plt.plot([x1, x1, x2, x2], [y, y+h, y+h, y], lw=1.5, c=col)

            # Add asterisk(s) based on the level of significance
            sig_str = '*' * int(-np.log10(p_values[category]) // 1)  # Single '*', '**', or '***' depending on significance level
            plt.text((x1+x2)*.5, y+h, sig_str, ha='center', va='bottom', color=col)

            # Print the p-value above the asterisk
            plt.text((x1+x2)*.5, y+h*2+3, f'p={p_values[category]:.3f}', ha='center', va='bottom', color=col)

    # Create a DataFrame
    category_analysis_df = pd.DataFrame(data, index=grouped_by_real_output.groups.keys())

    # Improve layout
    plt.tight_layout()

    # Save the plot as an png
    plt.savefig(f'{ANALYSIS_PATH}/mturk_category_analysis.png')
    plt.show()

    category_analysis_df['p-value'] = category_analysis_df['p-value'].apply(append_significance_asterisks)

    return category_analysis_df

def append_significance_asterisks(p_value):
    # Append asterisks based on the significance level
    if isinstance(p_value, float):
        if p_value <= 0.001:
            return f"{p_value:.3f}***"  # Highly significant
        elif p_value <= 0.01:
            return f"{p_value:.3f}**"  # Very significant
        elif p_value <= 0.05:
            return f"{p_value:.3f}*"  # Significant
    return p_value  # Return original value if not significant or not a float

def save_table_as_png(category_analysis_df, filename):
    # Estimate the required figure width: more columns -> wider figure
    # You may need to adjust these numbers based on your actual data
    fig_width = max(12, len(category_analysis_df.columns) * 1.5)
    fig_height = max(4, len(category_analysis_df) * 0.5)
    
   # Set up the figure
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    ax.axis('off')  # Hide the axes

    # Add a table at the bottom of the axes
    the_table = ax.table(cellText=category_analysis_df.values,
                         colLabels=category_analysis_df.columns,
                         rowLabels=category_analysis_df.index,
                         cellLoc='center',
                         loc='center',
                         edges='horizontal')

    # Manually set column widths to prevent overlapping
    col_width = 1 / len(category_analysis_df.columns)
    for (i, j), cell in the_table.get_celld().items():
        if i == 0:  # Only the first row (column headers)
            cell.set_width(col_width)

    # Drawing a horizontal line below the column headers
    for cell in the_table._cells:
        if cell[0] == 0:  # For the first row (column labels)
            the_table._cells[cell].visible_edges = 'open'
            the_table._cells[cell].get_text().set_weight('bold')  # Make the column labels bold
        elif cell[0] == -1:  # For the last row (if any)
            the_table._cells[cell].visible_edges = 'open'
        elif cell[1] == -1:  # For the first column (row labels)
            the_table._cells[cell].visible_edges = 'open'
        else:  # For all other cells
            the_table._cells[cell].visible_edges = 'horizontal'

    # Adjust font size based on the number of columns
    font_size = min(7, max(8, 16 - len(category_analysis_df.columns) // 2))
    the_table.auto_set_font_size(False)
    the_table.set_fontsize(font_size)

    # Improve layout
    plt.tight_layout()

    # Get the bounding box of the table
    renderer = fig.canvas.get_renderer()
    bbox = the_table.get_window_extent(renderer).transformed(fig.dpi_scale_trans.inverted())

    # Save the table as a .png file
    plt.savefig(f"{ANALYSIS_PATH}/{filename}.png", bbox_inches=bbox, dpi=300)

    # Display the plot if needed
    plt.show()
    plt.close(fig)
    

if __name__ == "__main__":    
   # Now read the results from the mturk results file
   mturk_results = read_results()

   #Analyze results
   #by_image_analyze(mturk_results)
   #by_response_analyze(mturk_results)
   
   #by_category_analyze(mturk_results)
   real_ouput_df = by_category_analyze(mturk_results)
   real_output_table = save_table_as_png(real_ouput_df,'mturk_by_real_output_table')
   by_response_df = by_response_analyze(mturk_results)
   by_response_df_table = save_table_as_png(by_response_df,'mturk_by_response_table')


