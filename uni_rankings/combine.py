# assumes i have dataframes df_qs, df_the, df_shanghai from previous steps

from fuzzywuzzy import fuzz, process
import pandas as pd

# Define a function to find the best match for a given university name
def find_best_match(name, choices, score):
    best_match, score = process.extractOne(name, choices)
    if score >= score:  # Adjust the threshold as needed
        return best_match
    else:
        return name

# Get unique university names from both dataframes
qs_universities = df_qs['University'].unique()
the_universities = df_the['University'].unique()

# Create a master list of all unique university names
all_universities = list(set(qs_universities))


# Standardize university names in df_the
df_the['New University'] = df_the.apply(lambda x: find_best_match(x['University'], all_universities, 95), axis=1)

# Merge the dataframes based on standardized university names
merged_df = pd.merge(df_qs, df_the, on=['University', 'Country'], how='outer')

# Get unique university names from both dataframes
shanghai_universities = df_shanghai['University'].unique()
merged_universities = merged_df['University'].unique()

# Create a master list of all unique university names
all_universities = list(set(merged_universities))

# Standardize university names in df_the
df_shanghai['new University'] = df_shanghai.apply(lambda x: find_best_match(x['University'], all_universities, 95), axis=1)

# Merge the dataframes based on standardized university names
new_merged_df = pd.merge(merged_df, df_shanghai, on=['University'], how='outer')

# Create a list of all unique university names
all_universities = new_merged_df['University'].unique()

# Standardize university names in the merged DataFrame
new_merged_df['University'] = new_merged_df.apply(lambda x: find_best_match(x['University'], all_universities, 93), axis=1)

# Combine values for similar university names
for idx, row in new_merged_df.iterrows():
    university_name = row['University']
    
    # Find similar matches in the merged DataFrame based on university name (excluding the current row)
    similarity_threshold = 97  # Adjust the similarity score threshold as needed
    similar_matches = new_merged_df[new_merged_df.apply(lambda x: fuzz.token_sort_ratio(x['University'], university_name), axis=1) >= similarity_threshold]
    similar_matches = similar_matches[similar_matches.index != idx]
    
    # Check if there are any similar matches
    if not similar_matches.empty:
        # Get the first similar match (you can implement a more sophisticated logic here)
        similar_row = similar_matches.iloc[0]
        
        # Iterate through the columns to fill in missing values with non-null values from either row
        for column in new_merged_df.columns:
            if pd.isnull(row[column]) and not pd.isnull(similar_row[column]):
                new_merged_df.at[idx, column] = similar_row[column]
            elif pd.isnull(similar_row[column]) and not pd.isnull(row[column]):
                new_merged_df.at[idx, column] = row[column]

# Fill NaN values with 0 for every row except 'country' column
country_column = new_merged_df['Country']
new_merged_df.drop('Country', axis=1, inplace=True)
new_merged_df.fillna(0, inplace=True)
new_merged_df['Country'] = country_column
new_merged_df[['University', 'Country', 'QS Citations per Paper', "Citations", 'CNCI', 'QS Academic Reputation',
              'QS Employer Reputation', 'Research', 'Teaching', 'TOP']]
new_merged_df['QS Citations per Paper'] = pd.to_numeric(new_merged_df['QS Citations per Paper'], errors='coerce')
new_merged_df['Citations'] = pd.to_numeric(new_merged_df['Citations'], errors='coerce')
new_merged_df['CNCI'] = pd.to_numeric(new_merged_df['CNCI'], errors='coerce')

# Calculate the "final citation score" for each row based on the specified logic
def calculate_final_score_citations(row):
    qs_citations_per_paper = row['QS Citations per Paper']
    citations = row['Citations']
    cnci = row['CNCI']

    if qs_citations_per_paper != 0 and citations != 0 and cnci != 0:
        final_score = (((qs_citations_per_paper + citations + cnci) / 3) / 100) * 0.8 + 0.2
    elif (qs_citations_per_paper != 0 and citations != 0) or (qs_citations_per_paper != 0 and cnci != 0) or (citations != 0 and cnci != 0):
        final_score = (((qs_citations_per_paper + citations + cnci) / 2) / 100) * 0.8 + 0.1
    elif qs_citations_per_paper != 0 or citations != 0 or cnci != 0:
        final_score = (max(qs_citations_per_paper, citations, cnci) / 100) * 0.8
    else:
        final_score = 0

    return (final_score*100)

# Apply the calculation to each row and create a new 'final citation score' column
new_merged_df['final citation score'] = new_merged_df.apply(calculate_final_score_citations, axis=1)

def calculate_final_score_rep(row):
    cols = ['TOP', 'QS Academic Reputation', 'QS Employer Reputation', 'Research', 'Teaching']
    non_zero_cols = [col for col in cols if row[col] != 0]
    non_zero_count = len(non_zero_cols)

    # Convert relevant columns to numeric
    numeric_cols = row[non_zero_cols].apply(pd.to_numeric, errors='coerce')

    if non_zero_count == 5:
        final_score = (((numeric_cols.sum() / 5) / 100) * 0.8) + 0.2
    elif non_zero_count == 4:
        final_score = (((numeric_cols.sum() / 4) / 100) * 0.8) + 0.15
    elif non_zero_count == 3:
        final_score = (((numeric_cols.sum() / 3) / 100) * 0.8) + 0.1
    elif non_zero_count == 2:
        final_score = (((numeric_cols.sum() / 2) / 100) * 0.8) + 0.05
    elif non_zero_count == 1:
        final_score = (numeric_cols[non_zero_cols[0]] / 100) * 0.8
    else:
        final_score = 0

    return (final_score * 100)

# Apply the calculation to each row and create a new 'final reputation score' column
new_merged_df['final reputation score'] = new_merged_df.apply(calculate_final_score_rep, axis=1)


new_merged_df['overall score'] = 0.2 * new_merged_df['final citation score'] + 0.8 * new_merged_df['final reputation score']
new_merged_df.sort_values(by='overall score', ascending=False, inplace=True)
new_merged_df.reset_index(drop=True, inplace=True)
new_merged_df.index += 1
new_merged_df.to_csv('FINAL_ranking_list.csv')