from scrape import fetch_data
from mongodb import push_data

def main():
    df = fetch_data()
    push_data(df)

if __name__ == "__main__":
    main()

