library(dplyr)
library(readxl)
library(knitr)
library(kableExtra)

# Function to read results
read_results <- function() {
  results_df <- readxl::read_excel("processed_data/mturk_results.xlsx")
  return(results_df)
}

by_real_output_analyze <- function(mturk_results) {
  # Group data by 'real_output'
  grouped_results <- mturk_results %>%
    group_by(real_output) %>%
    summarise(
      total_with_image = sum(with_image == 1),
      total_without_image = sum(with_image == 0),
      matches_with_image = sum(with_image == 1 & matching == 1),
      matches_without_image = sum(with_image == 0 & matching == 1),
      .groups = 'drop'
    ) %>%
    rowwise() %>%
    mutate(
      percentage_with_image = (matches_with_image / total_with_image) * 100,
      percentage_without_image = (matches_without_image / total_without_image) * 100,
      p_value = ifelse(total_with_image >= 5 & total_without_image >= 5,
                       chisq.test(matrix(c(matches_with_image, total_with_image - matches_with_image,
                                           matches_without_image, total_without_image - matches_without_image), ncol = 2))$p.value,
                       NA_real_)
    ) %>%
    transmute(
      Category = real_output,
      `Accuracy %_Without` = round((matches_without_image / total_without_image) * 100, 2),
      `No. Correct_Without` = as.integer(matches_without_image),
      `No. Total_Without` = as.integer(total_without_image),
      `Accuracy %_With` = round((matches_with_image / total_with_image) * 100, 2),
      `No. Correct_With` = as.integer(matches_with_image),
      `No. Total_With` = as.integer(total_with_image), 
      P_Value = round(p_value,3)
    )
  
  # Ensure the column names are consistent for grouped_results
  grouped_results <- grouped_results %>%
    select(Category, `Accuracy %_Without`, `No. Correct_Without`, `No. Total_Without`,
           `Accuracy %_With`, `No. Correct_With`, `No. Total_With`, P_Value)
  
  # Calculate overall totals outside the group_by summarise
  overall_total_with_image <- sum(mturk_results$with_image == 1)
  overall_total_without_image <- sum(mturk_results$with_image == 0)
  overall_matches_with_image <- sum(mturk_results$with_image == 1 & mturk_results$matching == 1)
  overall_matches_without_image <- sum(mturk_results$with_image == 0 & mturk_results$matching == 1)
  
  # Calculate overall p-value
  overall_p_value <- ifelse(overall_total_with_image >= 5 & overall_total_without_image >= 5,
                            chisq.test(matrix(c(overall_matches_with_image, overall_total_with_image - overall_matches_with_image,
                                                overall_matches_without_image, overall_total_without_image - overall_matches_without_image), ncol = 2))$p.value,
                            NA_real_)
  
  # Create a row for overall results
  overall_results <- data.frame(
    Category = "Totals",
    `Accuracy %_Without` = round((overall_matches_without_image / overall_total_without_image) * 100, 2),
    `No. Correct_Without` = overall_matches_without_image,
    `No. Total_Without` = overall_total_without_image,
    `Accuracy %_With` = round((overall_matches_with_image / overall_total_with_image) * 100, 2),
    `No. Correct_With` = overall_matches_with_image,
    `No. Total_With` = overall_total_with_image, 
    P_Value = round(overall_p_value, 3)
  )
  
  # Ensure the column names of overall_results match those of grouped_results
  names(overall_results) <- names(grouped_results)
  
  # Combining group-specific and overall results
  combined_results <- rbind(grouped_results, overall_results)
  
  return(combined_results)
  
}

# Function to create a LaTeX table using kable
create_real_output_table <- function(df, filename) {
  # Rename columns for uniformity under the meta-columns
  names(df)[2:4] <- c("Accuracy %", "No. Correct", "No. Total")  # Without Image
  names(df)[5:7] <- c("Accuracy %", "No. Correct", "No. Total")  # With Image
  
  
  kable(df, format = "latex", booktabs = TRUE) %>%
    kable_styling(latex_options = c("striped", "scale_down")) %>%
    add_header_above(c(" " = 1, "Without Image" = 3, "With Image" = 3)) %>%
    save_kable(file = paste0(filename, ".tex"))
}

by_response_analyze <- function(mturk_results) {
   # Group data by 'response'
  grouped_results <- mturk_results %>%
    group_by(submitted_answer) %>%
    summarise(
      total_with_image = sum(with_image == 1),
      total_without_image = sum(with_image == 0),
      matches_with_image = sum(with_image == 1 & matching == 1),
      matches_without_image = sum(with_image == 0 & matching == 1),
      .groups = 'drop'
    ) %>%
    rowwise() %>%
    mutate(
      percentage_with_image = (matches_with_image / total_with_image) * 100,
      percentage_without_image = (matches_without_image / total_without_image) * 100,
      p_value = ifelse(total_with_image >= 5 & total_without_image >= 5,
                       chisq.test(matrix(c(matches_with_image, total_with_image - matches_with_image,
                                           matches_without_image, total_without_image - matches_without_image), ncol = 2))$p.value,
                       NA_real_)
    ) %>%
    transmute(
      Category = submitted_answer,
      `Accuracy %_Without` = round((matches_without_image / total_without_image) * 100, 2),
      `No. Correct_Without` = as.integer(matches_without_image),
      `No. Chosen_Without` = as.integer(total_without_image),
      `Accuracy %_With` = round((matches_with_image / total_with_image) * 100, 2),
      `No. Correct_With` = as.integer(matches_with_image),
      `No. Chosen_With` = as.integer(total_with_image),
      P_Value = round(p_value,3)
      
    )
  return(grouped_results)
}

# Function to create a LaTeX table using kable
create_response_table <- function(df, filename) {
  # Rename columns for uniformity under the meta-columns
  names(df)[2:4] <- c("Accuracy %", "No. Correct", "No. Chosen")  # Without Image
  names(df)[5:7] <- c("Accuracy %", "No. Correct", "No. Chosen")  # With Image
  
  
  kable(df, format = "latex", booktabs = TRUE) %>%
    kable_styling(latex_options = c("striped", "scale_down")) %>%
    add_header_above(c(" " = 1, "Without Image" = 3, "With Image" = 3)) %>%
    save_kable(file = paste0(filename, ".tex"))
}

overall_analyze <- function(mturk_results) {
  # Calculating totals and matches for with and without image
  total_with_image <- sum(mturk_results$with_image == 1)
  total_without_image <- sum(mturk_results$with_image == 0)
  matches_with_image <- sum(mturk_results$with_image == 1 & mturk_results$matching == 1)
  matches_without_image <- sum(mturk_results$with_image == 0 & mturk_results$matching == 1)
  
  # Calculating percentages
  percentage_with_image <- (matches_with_image / total_with_image) * 100
  percentage_without_image <- (matches_without_image / total_without_image) * 100
  
  # Calculating p-value using chi-squared test or Fisher's Exact Test
  p_value <- ifelse(total_with_image >= 5 & total_without_image >= 5,
                    chisq.test(matrix(c(matches_with_image, total_with_image - matches_with_image,
                                        matches_without_image, total_without_image - matches_without_image), ncol = 2))$p.value,
                    NA_real_)
  
  # Creating a data frame for the results
  results_df <- data.frame(
    `Question Type` = c("Without Image", "With Image"),
    `Accuracy (%)` = c(round(percentage_without_image, 2),round(percentage_with_image, 2)),
    `No. Correct` = c(as.integer(matches_without_image),as.integer(matches_with_image)),
    `No. Questions` = c(as.integer(total_without_image),as.integer(total_with_image)),
    `P-Value` = round(p_value, 3)
  )

  return(results_df)
}

# Function to create a LaTeX table using kable
create_overall_table <- function(df, filename) {
  custom_col_names <- c("Question Type", "Accuracy (%)", "No. Correct", "No. Questions", "P-Value")
  
  
  kable(df, format = "latex", booktabs = TRUE,col.names = custom_col_names) %>%
    kable_styling(latex_options = c("striped", "scale_down")) %>%
    save_kable(file = paste0(filename, ".tex"))
}

# Run the analysis and create the table
mturk_results <- read_results()

by_real_output_table <- by_real_output_analyze(mturk_results)
by_response_table <- by_response_analyze(mturk_results)
overall_results_table <- overall_analyze(mturk_results)


# Create and save the LaTeX table
create_real_output_table(by_real_output_table, "analysis/by_real_output_table")
create_response_table(by_response_table, "analysis/by_response_table")
create_overall_table(overall_results_table, "analysis/overall_results_table")
