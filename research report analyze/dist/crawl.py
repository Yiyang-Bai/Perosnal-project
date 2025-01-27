import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import mysql.connector
import re


def setup_driver(driver_path):
    """Set up and return a Selenium WebDriver instance."""
    service = Service(driver_path)
    driver = webdriver.Chrome(service=service)
    driver.implicitly_wait(5)
    return driver

def setup_db_connection():
    """Set up and return a MySQL database connection."""
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Byy200402191017",
        database="report",
        charset="utf8mb4"
    )
    return conn

def collect_links(driver, url, number):
    """Collect a specified number of unique links from the given URL."""
    links = set()
    old_count = 0

    driver.get(url)

    while len(links) < number:
        news_items = driver.find_elements(
            By.CSS_SELECTOR,
            "#nimbus-app > section > section > section > article > section.mainContent.yf-tnbau3 > section > "
            "div > div > div > div > ul > li > section > div > a"
        )

        for item in news_items:
            href = item.get_attribute("href")
            if href and href not in links:
                links.add(href)

        if len(links) >= number:
            break

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

        if len(links) == old_count:
            print("No more new links found. Stopping...")
            break
        old_count = len(links)

    return list(links)[:number]




def fetch_article_content(url):
    try:

        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        paragraphs = soup.find_all('p', class_='yf-1pe5jgt')
        content = []

        for para in paragraphs:

            para_text = []
            for elem in para.contents:
                if elem.name == 'a':
                    link_text = f"{elem.get_text(strip=True)} ({elem['href']})"
                    para_text.append(link_text)
                else:
                    para_text.append(elem.strip() if isinstance(elem, str) else elem.get_text(strip=True))
            content.append(" ".join(para_text))

        return "\n".join(content)

    except Exception as e:
        return f"Error fetching content: {e}"


def fetch_article_links(links):
    result = []
    for link in links:
        content = fetch_article_content(link)
        if content:
            result.append([content])
    return result


def fetch_non_empty_links(links):
    result_links = []
    for link in links:
        content = fetch_article_content(link)
        if content:
            result_links.append([link])
    return result_links





def clean_list_of_list_content(raw_contents):
    """
    Cleans a list of list content by removing placeholders, unnecessary whitespace,
    and formatting for readability.

    Args:
        raw_contents (list of lists): Each sublist contains a string of raw content.

    Returns:
        list of lists: Each sublist contains a single cleaned and formatted string.
    """
    cleaned_contents = []

    for sublist in raw_contents:
        # Check if sublist has content
        if not sublist or not isinstance(sublist[0], str):
            cleaned_contents.append(["No valid content provided."])
            continue

        raw_text = sublist[0]

        cleaned_text = re.sub(r'HTML_TAG_START|HTML_TAG_END', '', raw_text)

        cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()

        paragraphs = cleaned_text.split('. ')
        formatted_content = "\n\n".join(paragraphs)

        cleaned_contents.append([formatted_content])

    return cleaned_contents


def insert_content_to_db(conn, record_id, list_content, non_empty_links):
    """Insert content and links into the database."""
    cursor = conn.cursor()
    try:
        for i, (content_list, link) in enumerate(zip(list_content, non_empty_links)):

            if not content_list:
                print(f"No content for News {i + 1}, skipping...")
                continue

            content = " ".join(
                item if isinstance(item, str) else str(item) for item in content_list
            )
            content = content.encode("utf-8", "ignore").decode("utf-8")
            content.replace("HTML_TAG_START", "").replace("HTML_TAG_END", "").strip()
            #content.replace("HTML_TAG_START", "").replace("HTML_TAG_END", "").strip()

            if isinstance(link, list):
                link = " ".join(link)
            link = link.encode("utf-8", "ignore").decode("utf-8")

            sql_insert = """
                INSERT INTO NEWS (Record_id, News_link, content)
                VALUES (%s, %s, %s);
            """

            cursor.execute(sql_insert, (record_id, link, content))
            conn.commit()
            print(f"Data inserted successfully for News {i + 1}")
    except Exception as e:
        conn.rollback()
        print("Error while inserting data:", e)
    finally:
        cursor.close()


def get_content(company, number, record_id):
    """Main function to get content from Yahoo Finance and store it in the database."""
    url = f'https://finance.yahoo.com/quote/{company}/news/'
    driver_path = r'C:\Users\AAA\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe'

    driver = setup_driver(driver_path)
    conn = setup_db_connection()

    try:

        links = collect_links(driver, url, number)
        print("Collected Links:", links)

        non_empty_links = fetch_non_empty_links(links)
        print("Non Empty Links:", non_empty_links)

        list_content = fetch_article_links(links)
        print(f"=== Collected {len(list_content)} Contents ===")

        insert_content_to_db(conn, record_id, list_content, non_empty_links)
    finally:
        driver.quit()
        conn.close()




#get_content("MS", 5, 1)