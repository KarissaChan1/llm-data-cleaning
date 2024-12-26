# Data Cleaning with Gemini AI

This tool uses Google's Gemini AI to automatically identify and clean placeholder values in datasets. It is particularly useful for cleaning clinical data where missing values might be represented in various formats, especially if the data is aggregated from multiple dataset sources.

## Installation

1. Install required packages:
```
pip install -r requirements.txt
```

2. Set up your Google API key:
   - Get an API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a `.env` file in the project root
   - Add your API key to the `.env` file:
```
   GOOGLE_API_KEY=your_api_key_here
```

## Usage

Basic command structure:
```
python llm_clean_data.py <file_path> [--columns <column_name>] [--output_dir <output_directory>]
```

Example:
```
python llm_clean_data.py ./tests/data/ondri_beam_biomarkers.xlsx --columns SEX MOCA_TOTAL AB40 AB42 PTAU181 --output_dir ./tests/cleaned_outputs
```

This command will analyze the specified columns in the `ondri_beam_biomarkers.xlsx` file and save the cleaned data to the `cleaned_outputs` directory.
Specifying columns is preferred, in order to optimize the Gemini API call and reduce token usage. Otherwise, all columns will be analyzed.

