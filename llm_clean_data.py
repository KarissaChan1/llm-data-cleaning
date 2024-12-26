import os
import google.generativeai as genai
from dotenv import load_dotenv
import pandas as pd
import argparse

# Load environment variables from .env file
load_dotenv()

# Configure the API key
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
if not GOOGLE_API_KEY:
    raise ValueError("Please set GOOGLE_API_KEY in .env file")
genai.configure(api_key=GOOGLE_API_KEY)

def identify_placeholder_strings(df, columns_to_check):
    """
    Use Gemini Pro to identify potential placeholder strings in specified columns
    
    Args:
        df (pd.DataFrame): Input DataFrame
        columns_to_check (list): List of column names to analyze
        sample_size (int): Number of rows to sample
    """
    # Validate columns exist in DataFrame
    invalid_cols = [col for col in columns_to_check if col not in df.columns]
    if invalid_cols:
        raise ValueError(f"Columns not found in DataFrame: {invalid_cols}")
    
    # Sample the DataFrame
    sample_df = df[columns_to_check]
    
    # Get value counts for specified columns
    value_counts = {}
    for col in columns_to_check:
        # Convert to string to capture all values
        series = sample_df[col].astype(str)
        # Get all value counts
        counts = series.value_counts()
        # Only include columns that have some non-numeric values
        if any(~counts.index.str.match(r'^[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?$')):
            # Limit numeric values to top 5 to avoid overwhelming the prompt
            numeric_mask = counts.index.str.match(r'^[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?$')
            numeric_counts = counts[numeric_mask].head(5)
            non_numeric_counts = counts[~numeric_mask]
            # Combine both with a clear separator
            value_counts[col] = {
                'numeric_examples': numeric_counts.to_dict(),
                'non_numeric_values': non_numeric_counts.to_dict()
            }
    print(value_counts)
    
    prompt = """
    Analyze these columns and their value frequencies. Each column shows:
    - 'numeric_examples': A sample of the normal numeric values in the column
    - 'non_numeric_values': All non-numeric values found in the column
    
    Identify ONLY placeholder strings that represent missing data or invalid measurements.
    Examples of what to include: 'N/A', 'missing', 'nan', 'M_OTHER', '-', 'Unknown','not_answered','BLOD'
    Examples of what NOT to include: valid categorical values (like 'Male'/'Female'), normal numeric numbers if applicable
    
    Return only a Python list of strings that are placeholder values.
    Include case variations if present.
    
    Important: Use the numeric examples to understand what normal values look like in each column. If a column has numeric examples, it is likely that most of the associated non-numeric string values are noise/placeholders for missing values which should be included in the list to remove.
    """
    
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(f"{prompt}\n\nColumn frequencies:\n{value_counts}")
    print("Response: \n", response.text)
    return eval(response.text)

def clean_dataframe(df, placeholder_list, columns_to_clean):
    """
    Replace identified placeholder strings with NaN in specified columns
    
    Args:
        df (pd.DataFrame): Input DataFrame
        placeholder_list (list): List of strings to replace with NaN
        columns_to_clean (list): List of column names to clean
    """
    df_clean = df.copy()
    
    # Only process specified columns
    for col in columns_to_clean:
        for placeholder in placeholder_list:
            df_clean[col] = df_clean[col].replace(placeholder, pd.NA)
    
    return df_clean

def main():
    # Set up command line arguments
    parser = argparse.ArgumentParser(description='Clean placeholder strings from data files using Gemini API')
    parser.add_argument('file_path', help='Path to the CSV or Excel file to clean')
    parser.add_argument('--columns', nargs='+', help='Specific columns to check (optional)')
    parser.add_argument('--output_dir', help='Directory to save cleaned files')
    args = parser.parse_args()
    
    file_path = args.file_path
    
    try:
        # Load the data file based on extension
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_path.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file_path)
        else:
            raise ValueError("Unsupported file format. Please use CSV or Excel files.")
        
        # Specify columns to check for placeholders
        # You can modify this list based on your data
        columns_to_check = args.columns if args.columns else df.select_dtypes(include=['object']).columns.tolist()
        
        print(f"Analyzing {len(columns_to_check)} string columns for placeholders...")
        
        # Identify placeholder strings
        placeholder_strings = identify_placeholder_strings(df, columns_to_check)
        print("\nIdentified placeholder strings:")
        print(placeholder_strings)
        
        # Clean the dataframe
        df_clean = clean_dataframe(df, placeholder_strings, columns_to_check)
        
        # Print some statistics about the cleaning
        for col in columns_to_check:
            # Check for remaining placeholders and count NaN values
            remaining_placeholders = df_clean[col].isin(placeholder_strings).sum()
            # missing_after = df_clean[col].isna().sum()
            print(f"\nColumn: {col}")
            print(f"Remaining placeholders: {remaining_placeholders}")
        
        # Optionally save the cleaned dataframe
        os.makedirs(args.output_dir, exist_ok=True)
        output_path = os.path.join(args.output_dir, os.path.basename(file_path.rsplit('.', 1)[0]) + '_cleaned.' + file_path.rsplit('.', 1)[1])
        if file_path.endswith('.csv'):
            df_clean.to_csv(output_path, index=False)
        else:
            df_clean.to_excel(output_path, index=False)
        print(f"\nCleaned data saved to: {output_path}")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
