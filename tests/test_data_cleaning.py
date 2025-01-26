import os
import shutil
import subprocess
from pathlib import Path

def test_llm_data_cleaning():
    tests_dir = Path(__file__).parent
    data_dir = tests_dir / "data/"
    save_path = tests_dir / 'test_outputs/'
    
    if save_path.exists():
        shutil.rmtree(save_path)

    # Construct the CLI command
    command = [
        "llm_clean_data",
        os.path.join(data_dir, "biomarkers_ALL.xlsx"),
        "--columns", "Cohort", "Age", "Sex", "MOCA",
        "--output_dir", save_path.as_posix()
    ]

    # Run the command and capture the result
    result = subprocess.run(command, capture_output=True, text=True)

    # Print command output for debugging
    print(result.stdout)
    print(result.stderr)

    # Assert the command ran successfully
    assert result.returncode == 0
    assert save_path.exists()  # Ensure the output directory is created