import os
import shutil
from pathlib import Path

from textual._languages import VALID_LANGUAGES

# The directory that contains the language folders
source_dir = Path(__file__).parent / "../../nvim-treesitter/queries"
# The directory to store the collected highlights files
target_dir = Path(__file__).parent / "highlights"

# Ensure the target directory exists
os.makedirs(target_dir, exist_ok=True)

# Walk through the source directory
for root, dirs, files in os.walk(source_dir):
    # If a highlights.scm file exists in the current directory
    if "highlights.scm" in files:
        # Get the name of the current language directory
        language = os.path.basename(root)
        if language in VALID_LANGUAGES:
            # Create the full path to the source and target files
            source_file = os.path.join(root, "highlights.scm")
            target_file = os.path.join(target_dir, f"{language}.scm")
            # Copy the file
            shutil.copyfile(source_file, target_file)

# Print a success message
print("Done!")
