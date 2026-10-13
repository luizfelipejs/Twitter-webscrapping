from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from urllib.parse import quote_plus

import json
import time

from config import *


options = Options()
options.debugger_address = "127.0.0.1:9222"

driver = webdriver.Chrome(options=options)

tweets = []
texts = set()


def save():
    with open(OUTPUT_JSON, "w", encoding="utf-8") as file:
        json.dump(tweets, file, ensure_ascii=False, indent=2)


def collect(query):
    elements = driver.find_elements(
        By.CSS_SELECTOR,
        '[data-testid="tweetText"]'
    )

    novos = 0

    for element in elements:
        text = element.text.strip()

        if not text:
            continue

        if text in texts:
            continue

        texts.add(text)

        tweets.append({
            "id": len(tweets) + 1,
            "source": "x",
            "query": query,
            "text": text
        })

        novos += 1

    return novos


def open_tabs(queries):
    tabs = {}

    for i, query in enumerate(queries):

        url = (
            "https://x.com/search?"
            f"q={quote_plus(query)}"
            "&src=typed_query"
            "&f=live"
        )

        if i > 0:
            driver.switch_to.new_window("tab")

        driver.get(url)

        tabs[query] = driver.current_window_handle

        time.sleep(OPEN_TAB_DELAY)

    return tabs


def collect_tabs(queries, tabs):
    empty = {
        query: 0
        for query in queries
    }

    finished = set()

    for scroll in range(MAX_SCROLLS):

        for query in queries:

            if query in finished:
                continue

            driver.switch_to.window(tabs[query])

            novos = collect(query)

            print(
                f"[{query}] "
                f"scroll {scroll + 1}/{MAX_SCROLLS} "
                f"| novos: {novos} "
                f"| total: {len(tweets)}"
            )

            if novos == 0:
                empty[query] += 1
            else:
                empty[query] = 0

            if empty[query] >= MAX_EMPTY_SCROLLS:
                finished.add(query)
                continue

            driver.execute_script(
                "window.scrollBy(0, window.innerHeight * 0.8)"
            )

            time.sleep(SCROLL_DELAY)

        save()

        if len(finished) == len(queries):
            break


def main():
    quantidade = int(input("Quantidade de buscas: "))

    queries = []

    for _ in range(quantidade):
        query = input().strip()

        if query:
            queries.append(query)

    if not queries:
        return

    tabs = open_tabs(queries)

    collect_tabs(queries, tabs)

    save()

    print()
    print("COLETA FINALIZADA")
    print(f"Total: {len(tweets)} tweets")


if __name__ == "__main__":
    main()
