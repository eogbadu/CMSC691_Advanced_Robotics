import os
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import scipy.stats as stats
import numpy as np


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
    ax.set_ylabel('Percentage of Matches')
    ax.set_title('Comparison of Matches with and without Images')

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
    significance = []


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
        significance = []

        try:
            # Perform a t-test to check for significance between the two categories
            _, p = stats.ttest_ind(
                group[group['with_image'] == 1]['matching'],
                group[group['with_image'] == 0]['matching']
            )

            # Determine the significance level (e.g., 0.05)
            alpha = 0.05

            # Determine if the difference is significant based on the p-value
            is_significant = p < alpha
        except RuntimeWarning as warning:
            print("RuntimeWarning:", warning)
        except Exception as e:
            # Handle any other exceptions (generic Exception)
            print("Exception:", e)
        finally:
            significance.append(is_significant)

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
    plt.ylabel('Percentage of Matches')
    plt.title('Comparison of Matches by Control Signal Categories')
    plt.xticks([i + width / 2 for i in x], categories, rotation=45, ha='right')
    plt.legend()

    # Increase the top margin of the plot to have more space for p-values and asterisks
    plt.subplots_adjust(top=0.85)

    # Set the y-axis limit higher to accommodate the significance markers
    plt.ylim(0, max(max(percentages_with_image), max(percentages_without_image)) + 10)  # Adjust as needed for your data

   # Iterate over each category for calculating significance and plotting
    for i, category in enumerate(categories):
        
        group = grouped_by_real_output.get_group(category)

        try:
            # Perform a t-test to check for significance
            _, p_value = stats.ttest_ind(
                group[group['with_image'] == 1]['matching'],
                group[group['with_image'] == 0]['matching'],
                equal_var=False  # assuming unequal variance
            )
            
            # Determine if the difference is significant
            alpha = 0.05
            is_significant = p_value < alpha
            
        except RuntimeWarning as warning:
            print("RuntimeWarning:", warning)
            is_significant = False
        except Exception as e:
            print("Exception:", e)
            is_significant = False
        finally:
            # Append the result to the significance list
            significance.append(is_significant)

        # Coordinates for the significance line
        x1, x2 = i - width/2, i + width/2
        y, h, col = max(percentages_with_image[i], percentages_without_image[i]) + 1, 1, 'black'  # Increased h for more padding

        # Sample size at the bottom of the bar
        #bottom_offset = 3  # Adjust this value as needed to position the text below the bars
        #plt.text(x1, bottom_offset, f'n={sample_sizes_with_image[i]}', ha='center', va='top', color='black')
        #plt.text(x2, bottom_offset, f'n={sample_sizes_without_image[i]}', ha='center', va='top', color='black')


        if is_significant:
            # Draw the significance line
            plt.plot([x1, x1, x2, x2], [y, y+h, y+h, y], lw=1.5, c=col)
            
            # Add asterisk(s) based on the level of significance
            sig_str = '*' * int(-np.log10(p_value) // 1)  # Single '*', '**', or '***' depending on significance level
            plt.text((x1+x2)*.5, y+h, sig_str, ha='center', va='bottom', color=col)
            
            # Print the p-value above the asterisk
            plt.text((x1+x2)*.5, y+h*2+3, f'p={p_value:.3f}', ha='center', va='bottom', color=col)


    # Save the plot as an png
    plt.savefig(f'{ANALYSIS_PATH}/mturk_category_analysis.png')
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
    significance = []


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
        significance = []

        try:
            # Perform a t-test to check for significance between the two categories
            _, p = stats.ttest_ind(
                group[group['with_image'] == 1]['matching'],
                group[group['with_image'] == 0]['matching']
            )

            # Determine the significance level (e.g., 0.05)
            alpha = 0.05

            # Determine if the difference is significant based on the p-value
            is_significant = p < alpha
        except RuntimeWarning as warning:
            print("RuntimeWarning:", warning)
        except Exception as e:
            # Handle any other exceptions (generic Exception)
            print("Exception:", e)
        finally:
            significance.append(is_significant)

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
    plt.ylabel('Percentage of Matches')
    plt.title('Comparison of Matches by Submitted Answer Categories')
    plt.xticks([i + width / 2 for i in x], categories, rotation=45, ha='right')
    plt.legend()

    # Increase the top margin of the plot to have more space for p-values and asterisks
    plt.subplots_adjust(top=0.85)

    # Set the y-axis limit higher to accommodate the significance markers
    plt.ylim(0, max(max(percentages_with_image), max(percentages_without_image)) + 15)  # Adjust as needed for your data

   # Iterate over each category for calculating significance and plotting
    for i, category in enumerate(categories):
        
        group = grouped_by_submitted_answer.get_group(category)

        try:
            # Perform a t-test to check for significance
            _, p_value = stats.ttest_ind(
                group[group['with_image'] == 1]['matching'],
                group[group['with_image'] == 0]['matching'],
                equal_var=False  # assuming unequal variance
            )
            
            # Determine if the difference is significant
            alpha = 0.05
            is_significant = p_value < alpha
            
        except RuntimeWarning as warning:
            print("RuntimeWarning:", warning)
            is_significant = False
        except Exception as e:
            print("Exception:", e)
            is_significant = False
        finally:
            # Append the result to the significance list
            significance.append(is_significant)

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
            sig_str = '*' * int(-np.log10(p_value) // 1)  # Single '*', '**', or '***' depending on significance level
            plt.text((x1+x2)*.5, y+h, sig_str, ha='center', va='bottom', color=col)
            
            # Print the p-value above the asterisk
            plt.text((x1+x2)*.5, y+h*2+3, f'p={p_value:.3f}', ha='center', va='bottom', color=col)


    # Save the plot as an png
    plt.savefig(f'{ANALYSIS_PATH}/mturk_submitted_answer_analysis.png')
    plt.show()

def calculate_standard_error(matches, total):
    if total <= 0:
        return 0
    return (100 / total) * np.sqrt((matches / total) * (1 - matches / total))



if __name__ == "__main__":    
   # Now read the results from the mturk results file
   mturk_results = read_results()

   #Analyze results
   by_image_analyze(mturk_results)
   by_response_analyze(mturk_results)
   
   by_category_analyze(mturk_results)

