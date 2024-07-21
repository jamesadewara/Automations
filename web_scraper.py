from utils import WebScrapingMachine

def run():
    url = input("Enter the URL to scrape: ")
    driver_name = input("Enter the driver name (default is 'chrome'): ") or 'chrome'
    file_type = input("Enter the file type to save (csv, excel, json): ")
    file_name = input("Enter the file name (without extension): ") + '.' + file_type
    mode = input("Enter the mode of scraping (static, dynamic, ai, default is dynamic): ") or 'dynamic'

    scraper = WebScrapingMachine(url, driver_name, mode)
    scraper.scrapeWebsite(file_type, file_name)

if __name__ == '__main__':
    run()