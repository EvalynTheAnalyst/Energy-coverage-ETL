from scrape import scraping
from mongodb import push_data

def main():
    scraper = scraping()
    push_data = push_data(scraper)

if __name__ == "__main__":
    main()

