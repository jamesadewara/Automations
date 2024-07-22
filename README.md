# Automations

Automations is a comprehensive project that includes two main features: file automation and web scraping. Each feature has its own script and set of functionalities.

## Features

### File Automation

- **File Categorization**: Organizes files based on categories specified in a JSON configuration file.
- **Strict Mode**: Handles duplicate files by renaming or moving them to a specified location.
- **Unspecified Extensions Handling**: Moves files with extensions not specified in the configuration to an 'Other' directory or does nothing based on configuration.
- **Time-Based Organization**: Optionally organizes files into folders based on their timestamps.
- **Progress Bar**: Displays a progress bar for ongoing operations.
- **Logging**: Logs all operations with their durations and times.
- **Reversible Changes**: Commits previous and current paths to enable reverting changes to the previous state.
- **Clean Code Principles**: Follows clean code principles with proper naming conventions.

### Web Scraping

- **AI-Powered Scraping**: Utilizes AI methods for web scraping.
- **Customizable Scraping**: Allows customization of scraping parameters and targets.
- **Data Extraction**: Extracts relevant data from websites and saves it in a structured format.
- **Logging**: Logs the scraping process and results.
- **Error Handling**: Robust error handling to manage various scraping challenges.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/jamesadewara/Automations.git
   cd Automations
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
3. Run the web scraping script:
   ```bash
   python web_scraping.py
4. Run the file automation script:
   ```bash
   python file_automation.py