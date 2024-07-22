# import all necessary modules/libraries
# built in libraries
import os
import time
import shutil
import json
import logging
import warnings
from pathlib import Path
from typing import Dict, List
from datetime import datetime
import requests
import json
# 3rd party libraries
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import pandas as pd
from tqdm import tqdm
from webdriver_manager.chrome import ChromeDriverManager
import openai

class FileAutomation:
    def __init__(self, input_dir: str, output_dir: str, config_path: str):
        """
        Initialize the FileAutomation class with directories and configuration.

        Parameters
        ----------
        input_dir : str
            Path to the input directory.
        output_dir : str
            Path to the output directory.
        config_path : str
            Path to the configuration JSON file.
        """
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.config = self.loadConfig(config_path)
        self.categories = self.config.get("categories", [])
        self.strict_mode = self.config.get("strict_mode", {})
        self.unspecified_extension_handling = self.config.get("unspecified_extension_handling", "do_nothing")
        self.time_conscious = self.config.get("time_conscious", False)
        self.commit_log_path = self.output_dir / "file_commits.json"
        self.file_commits = []

        if not self.output_dir.exists():
            self.output_dir.mkdir(parents=True)
            warnings.warn(f"Output directory {self.output_dir} created.")
        
        self.setupLogging()

    def loadConfig(self, config_path: str) -> Dict:
        """
        Load the configuration from a JSON file.

        Parameters
        ----------
        config_path : str
            Path to the configuration JSON file.

        Returns
        -------
        dict
            Configuration dictionary.
        """
        try:
            with open(config_path, 'r') as file:
                config = json.load(file)
                return config
        except Exception as e:
            logging.error(f"Error loading config file: {e}")
            return {}

    def setupLogging(self):
        """Set up logging configuration."""
        log_file = self.output_dir / "file_automation.log"
        logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        logging.info("File automation started.")

    def organizeFiles(self):
        """Organize files in the input directory based on the configuration."""
        files = list(self.input_dir.iterdir())
        for file in tqdm(files, desc="Organizing files"):
            if file.is_file():
                start_time = datetime.now()
                self.handleFile(file)
                duration = datetime.now() - start_time
                logging.info(f"Processed file: {file}, Duration: {duration}")

        if files != []:
            self.saveFileCommits()
            logging.info("File automation completed.")
        else:
            logging.info("It seems like there are no files or resources here.")


    def handleFile(self, file: Path):
        """
        Handle individual file organization.

        Parameters
        ----------
        file : Path
            Path to the file to be organized.
        """
        file_extension = file.suffix[1:].lower()  # Get extension without dot
        category = self.getCategory(file_extension)
        
        if category:
            category_path = self.output_dir / category
            if self.time_conscious:
                timestamp_folder = datetime.fromtimestamp(file.stat().st_mtime).strftime('%Y-%m-%d')
                category_path = category_path / timestamp_folder

            if not category_path.exists():
                category_path.mkdir(parents=True)
            
            destination = category_path / file.name
            self.moveOrHandleDuplicate(file, destination)
        else:
            self.handleUnspecifiedExtension(file)

    def getCategory(self, extension: str) -> str:
        """
        Get the category for a given file extension.

        Parameters
        ----------
        extension : str
            File extension.

        Returns
        -------
        str
            Category name or None if not found.
        """
        for category_info in self.categories:
            if extension in [ext.lower() for ext in category_info["extensions"]]:
                return category_info["category"]
        return None

    def moveOrHandleDuplicate(self, source: Path, destination: Path):
        """
        Move a file or handle duplicates according to the configuration.

        Parameters
        ----------
        source : Path
            Path to the source file.
        destination : Path
            Path to the destination file.
        """
        if destination.exists():
            logging.warning(f"Duplicate found for {source}.")
            action = self.strict_mode.get("duplicate_handling", "do_nothing") if self.strict_mode else self.askUserForAction()
            
            if action == "merge":
                self.mergeFiles(source, destination)
            elif action == "replace":
                self.replaceFile(source, destination)
            else:
                logging.info(f"Skipping {source}.")
        else:
            shutil.move(str(source), str(destination))
            self.file_commits.append({"previous": str(source), "current": str(destination)})

    def askUserForAction(self) -> str:
        """
        Ask the user for an action to take on duplicate files.

        Returns
        -------
        str
            User-selected action.
        """
        print("Options: [merge, replace, do_nothing]")
        action = input("Choose an action for duplicates: ").strip().lower()
        while action not in ["merge", "replace", "do_nothing"]:
            action = input("Invalid option. Choose an action for duplicates: ").strip().lower()
        return action

    def mergeFiles(self, source: Path, destination: Path):
        """
        Merge source file into destination file.

        Parameters
        ----------
        source : Path
            Path to the source file.
        destination : Path
            Path to the destination file.
        """
        logging.info(f"Merging {source} into {destination}.")
        # Implement your merge logic here

    def replaceFile(self, source: Path, destination: Path):
        """
        Replace the destination file with the source file.

        Parameters
        ----------
        source : Path
            Path to the source file.
        destination : Path
            Path to the destination file.
        """
        logging.info(f"Replacing {destination} with {source}.")
        destination.unlink()
        shutil.move(str(source), str(destination))
        self.file_commits.append({"previous": str(source), "current": str(destination)})

    def handleUnspecifiedExtension(self, file: Path):
        """
        Handle files with unspecified extensions.

        Parameters
        ----------
        file : Path
            Path to the file.
        """
        if self.unspecified_extension_handling == "move_to_other":
            other_path = self.output_dir / "Other"
            if self.time_conscious:
                timestamp_folder = datetime.fromtimestamp(file.stat().st_mtime).strftime('%Y-%m-%d')
                other_path = other_path / timestamp_folder
            
            if not other_path.exists():
                other_path.mkdir(parents=True)
            destination = other_path / file.name
            self.moveOrHandleDuplicate(file, destination)
        else:
            logging.info(f"File {file} does not match any category and will not be moved.")

    def saveFileCommits(self):
        """Save the file commit history to a JSON file."""
        with open(self.commit_log_path, 'w') as file:
            json.dump(self.file_commits, file, indent=4)
        logging.info(f"File commits saved to {self.commit_log_path}.")

    def reverseChanges(self):
        """Reverse the changes by moving files back to their original locations."""
        if self.commit_log_path.exists():
            with open(self.commit_log_path, 'r') as file:
                commits = json.load(file)
                for commit in commits:
                    source = Path(commit["current"])
                    destination = Path(commit["previous"])
                    if source.exists():
                        destination.parent.mkdir(parents=True, exist_ok=True)
                        shutil.move(str(source), str(destination))
                        logging.info(f"Reversed {source} to {destination}.")
            logging.info("Reversal of changes completed.")
        else:
            logging.warning(f"No commit log found at {self.commit_log_path}.")


class WebScrapingMachine:
    """
    A class to represent a web scraping automation machine.

    Attributes
    ----------
    url : str
        The URL of the website to be scraped.
    driver_name : str
        The name of the driver to be used for dynamic scraping.
    mode : str
        The mode of scraping ('static', 'dynamic', 'ai').
    driver : webdriver
        The initialized webdriver.
    data : list
        The list to store scraped data.

    Methods
    -------
    installDriver():
        Installs the required driver if it doesn't exist.
    getDriver():
        Initializes and returns the appropriate webdriver.
    detectWebsiteType():
        Detects if a website is dynamic or static.
    scrapeStatic():
        Scrapes a static website.
    scrapeDynamic():
        Scrapes a dynamic website.
    scrapeAi():
        Scrapes a website using AI-based methods.
    saveData(file_type, file_name):
        Saves the scraped data in the specified format.
    scrapeWebsite(file_type='csv', file_name='scraped_data'):
        Main function to scrape the website.
    """

    def __init__(self, url, driver_name='chrome', mode='dynamic', api_key=None):
        """
        Constructs all the necessary attributes for the WebScrapingMachine object.

        Parameters
        ----------
        url : str
            The URL of the website to be scraped.
        driver_name : str, optional
            The name of the driver to be used for dynamic scraping (default is 'chrome').
        mode : str, optional
            The mode of scraping (default is 'dynamic').
        api_key=None: str, optional
            The  api_key from openai
        """
        self.url = url
        self.driver_name = driver_name
        self.mode = mode
        self.driver = None
        self.data = []
        self.api_key = api_key
        openai.api_key = self.api_key

    def installDriver(self):
        """
        Installs the required driver if it doesn't exist.

        Returns
        -------
        str
            The path to the installed driver.
        """
        try:
            with tqdm(total=100, desc="Installing driver", unit='%', ncols=100) as pbar:
                for i in range(10):
                    time.sleep(0.1)  # Simulating the progress
                    pbar.update(10)
                driver_path = ChromeDriverManager().install()
                pbar.update(100 - pbar.n)
            return driver_path
        except Exception as e:
            warnings.warn(f"Driver installation failed: {e}")
            return None

    def getDriver(self):
        """
        Initializes and returns the appropriate webdriver.

        Raises
        ------
        ValueError
            If the specified driver is not supported.

        Returns
        -------
        webdriver
            The initialized webdriver.
        """
        if self.driver_name.lower() == 'chrome':
            driver_path = self.installDriver()
            if driver_path:
                service = Service(driver_path)
                options = Options()
                options.headless = True
                try:
                    self.driver = webdriver.Chrome(service=service, options=options)
                except Exception as e:
                    warnings.warn(f"Failed to initialize the Chrome driver: {e}")
            else:
                warnings.warn("Chrome driver installation failed.")
        else:
            raise ValueError(f"Driver '{self.driver_name}' is not supported.")

    def detectWebsiteType(self):
        """
        Detects if a website is dynamic or static.

        Returns
        -------
        str
            'dynamic' if the website is dynamic, otherwise 'static'.
        """
        try:
            response = requests.get(self.url)
            if 'application/json' in response.headers.get('Content-Type', ''):
                return 'dynamic'
            return 'static'
        except requests.RequestException as e:
            warnings.warn(f"Failed to access the website: {e}")
            return 'static'

    def scrapeStatic(self):
        """
        Scrapes a static website and stores the data in the data attribute.
        """
        try:
            response = requests.get(self.url)
            soup = BeautifulSoup(response.content, 'html.parser')
            self.data = [item.get_text() for item in soup.find_all('p')]
        except requests.RequestException as e:
            warnings.warn(f"Failed to scrape static content: {e}")

    def scrapeDynamic(self):
        """
        Scrapes a dynamic website and stores the data in the data attribute.
        """
        self.getDriver()
        if self.driver:
            try:
                self.driver.get(self.url)
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                self.data = [item.get_text() for item in soup.find_all('p')]
            except Exception as e:
                warnings.warn(f"Failed to scrape dynamic content: {e}")
            finally:
                self.driver.quit()

    def scrapeAi(self, max_tokens):
        """
        Scrapes a website using AI-based methods and stores the data in the data attribute.
        """
        try:
            session = requests.Session()
            response = session.get(self.url, headers={'User-Agent': 'Mozilla/5.0'})
            if response.status_code == 200:
                page_content = response.text
                ai_response = openai.Completion.create(
                    model="text-davinci-003",
                    prompt=f"Extract and summarize the main text content from this webpage: {page_content}",
                    max_tokens=max_tokens
                )
                self.data = ai_response.choices[0].text.strip().split('\n')
            else:
                warnings.warn(f"Failed to fetch the page content, status code: {response.status_code}")
        except Exception as e:
            warnings.warn(f"Failed to scrape AI content: {e}")

    def saveData(self, file_type, file_name):
        """
        Saves the scraped data in the specified format.

        Parameters
        ----------
        file_type : str
            The format to save the data ('csv', 'excel', or 'json').
        file_name : str
            The name of the file.
        """
        
        try:
            df = pd.DataFrame(self.data, columns=['Data'])
            if file_type.lower() == 'csv':
                df.to_csv(file_name, index=False)
            elif file_type.lower() == 'excel':
                df.to_excel(file_name, index=False)
            elif file_type.lower() == 'json':
                with open(file_name, 'w') as f:
                    json.dump(self.data, f)
            else:
                raise ValueError(f"File type '{file_type}' is not supported.")
        except Exception as e:
            warnings.warn(f"Failed to save data: {e}")

    def scrapeWebsite(self, file_type='csv', file_name='scraped_data', file_dir=None, max_tokens=1000):
        """
        Main function to scrape the website and save the data.

        Parameters
        ----------
        file_type : str, optional
            The format to save the data (default is 'csv').
        file_name : str, optional
            The name of the file (default is 'scraped_data').
        """
        try:
            with tqdm(total=100, desc="Scraping progress", unit='%') as pbar:
                if self.mode == 'static':
                    self.scrapeStatic()
                elif self.mode == 'dynamic':
                    self.scrapeDynamic()
                elif self.mode == 'ai':
                    self.scrapeAi(max_tokens)
                else:
                    warnings.warn(f"Invalid mode '{self.mode}', defaulting to dynamic.")
                    self.scrapeDynamic()

                pbar.update(100)
            try:
                os.makedirs(file_dir)
                if file_dir != None:
                    warnings.warn(f"created this dir {file_dir} for the file {file_name}")
            except:
                pass
            self.saveData(file_type, os.path.join(file_dir, file_name))
        except Exception as e:
            warnings.warn(f"An error occurred during the scraping process: {e}")


