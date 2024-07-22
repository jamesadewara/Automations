from utils import WebScrapingMachine

def run():
    max_tokens = 1000
    api_key = None

    url = input("Enter the URL to scrape: ")
    driver_name = input("Enter the driver name (default is 'chrome'): ") or 'chrome'
    file_type = input("Enter the file type to save (csv, excel, json): ")
    file_name = input("Enter the file name (without extension): ") + '.' + file_type
    file_dir = input("Enter the directory to save the file:")
    mode = input("Enter the mode of scraping (static, dynamic, ai, default is dynamic): ") or 'dynamic'

    if (mode == "ai"):
        api_key = input("Your openAi API key:  ")
        max_tokens = input("Max number of tokens to scrape: ")

    scraper = WebScrapingMachine(url, driver_name, mode, api_key=api_key)
    scraper.scrapeWebsite(file_type, file_name, file_dir, max_tokens=max_tokens)

if __name__ == '__main__':
    run()