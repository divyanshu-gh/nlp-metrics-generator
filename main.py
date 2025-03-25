import os
import time
import re
import argparse
import logging
import pandas as pd
import nltk
from nltk.tokenize import word_tokenize
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions

# Logging setup
logging.basicConfig(level=logging.INFO, format="%(message)s")

# Config paths
INPUT_FILE = 'input/Input.xlsx'
OUTPUT_FILE = 'output/Output.xlsx'
ARTICLES_DIR = 'articles'
STOPWORDS_DIR = 'stopwords'
DICTIONARY_DIR = 'dictionary'

os.makedirs(ARTICLES_DIR, exist_ok=True)
os.makedirs('output', exist_ok=True)

# Download punkt only for word_tokenize (not sent_tokenize)
nltk.download('punkt')

def load_input_data():
    df = pd.read_excel(INPUT_FILE)
    print(f"Loaded {len(df)} rows from Input.xlsx")
    return df

def load_stopwords():
    stopwords = set()
    for file in os.listdir(STOPWORDS_DIR):
        if file.endswith('.txt'):
            with open(os.path.join(STOPWORDS_DIR, file), 'r', encoding='ISO-8859-1') as f:
                words = [line.strip().lower() for line in f if line.strip()]
                stopwords.update(words)
                print(f"Loaded {len(words)} stopwords from {file}")
    return stopwords

def load_sentiment_words():
    with open(os.path.join(DICTIONARY_DIR, 'positive-words.txt'), 'r', encoding='ISO-8859-1') as f:
        pos = [w.strip().lower() for w in f if w.strip() and not w.startswith(';')]
    with open(os.path.join(DICTIONARY_DIR, 'negative-words.txt'), 'r', encoding='ISO-8859-1') as f:
        neg = [w.strip().lower() for w in f if w.strip() and not w.startswith(';')]
    print(f"Loaded {len(pos)} positive and {len(neg)} negative words")
    return set(pos), set(neg)

def get_driver(browser='chrome'):
    browser = browser.lower()
    if browser == 'edge':
        options = EdgeOptions()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        driver_path = os.path.join(os.getcwd(), 'msedgedriver.exe')
        service = EdgeService(executable_path=driver_path)
        return webdriver.Edge(service=service, options=options)
    elif browser == 'chrome':
        options = ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        driver_path = os.path.join(os.getcwd(), 'chromedriver.exe')
        service = ChromeService(executable_path=driver_path)
        return webdriver.Chrome(service=service, options=options)
    else:
        raise ValueError("Unsupported browser! Use chrome or edge.")

def scrape_articles(df, browser='chrome'):
    driver = get_driver(browser)
    for _, row in df.iterrows():
        url_id = row['URL_ID']
        url = row['URL']
        article_path = f"{ARTICLES_DIR}/{url_id}.txt"

        if os.path.exists(article_path):  # Skip if already scraped
            print(f"✔ Article already exists: {url_id}.txt — Skipping")
            continue

        print(f"Scraping {url}...")
        try:
            driver.get(url)
            time.sleep(2)
            title = driver.find_element(By.TAG_NAME, 'h1').text.strip()
            paragraphs = driver.find_elements(By.TAG_NAME, 'p')
            content = '\n'.join(p.text.strip() for p in paragraphs if p.text.strip())

            with open(article_path, 'w', encoding='utf-8') as f:
                f.write(title + '\n\n' + content)

            print(f"✔ Saved article: {url_id}.txt")
        except Exception as e:
            print(f"❌ Could not fetch {url_id}: {e}")
    driver.quit()

def count_syllables(word):
    word = word.lower()
    vowels = "aeiou"
    count, prev = 0, False
    for char in word:
        if char in vowels:
            if not prev:
                count += 1
            prev = True
        else:
            prev = False
    if word.endswith("es") or word.endswith("ed"):
        count -= 1
    return max(1, count)

def is_complex(word):
    return count_syllables(word) >= 3

def compute_metrics(text, stopwords, pos_words, neg_words):
    # Simple sentence split without punkt
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]

    # Simple word tokenizer using regex instead of nltk's word_tokenize
    words = re.findall(r'\b\w+\b', text.lower())
    words = [w for w in words if w.isalpha() and w not in stopwords]
    total_words = len(words)

    if total_words == 0 or len(sentences) == 0:
        return [0]*13

    pos_score = sum(1 for w in words if w in pos_words)
    neg_score = sum(1 for w in words if w in neg_words)
    polarity = (pos_score - neg_score) / ((pos_score + neg_score) + 1e-6)
    subjectivity = (pos_score + neg_score) / (total_words + 1e-6)
    avg_sent_len = total_words / len(sentences)
    complex_words = [w for w in words if is_complex(w)]
    perc_complex = len(complex_words) / total_words
    fog_index = 0.4 * (avg_sent_len + perc_complex)
    avg_words_per_sent = avg_sent_len
    complex_word_count = len(complex_words)
    syllables_per_word = sum(count_syllables(w) for w in words) / total_words
    pronouns = len(re.findall(r'\b(I|we|my|ours|us)\b', text, re.I))
    avg_word_len = sum(len(w) for w in words) / total_words

    return [
        pos_score, neg_score, polarity, subjectivity, avg_sent_len,
        perc_complex, fog_index, avg_words_per_sent, complex_word_count,
        total_words, syllables_per_word, pronouns, avg_word_len
    ]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--browser", default="chrome", help="Browser to use")
    parser.add_argument("--output", default=OUTPUT_FILE, help="Path to save the result")
    args = parser.parse_args()

    df = load_input_data()
    stopwords = load_stopwords()
    pos_words, neg_words = load_sentiment_words()

    scrape_articles(df, browser=args.browser)

    print("\nCalculating metrics...")
    metrics = []
    for _, row in df.iterrows():
        url_id = row['URL_ID']
        file_path = f"{ARTICLES_DIR}/{url_id}.txt"
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            metrics.append(compute_metrics(text, stopwords, pos_words, neg_words))
        else:
            print(f"⚠️ Article missing for {url_id}")
            metrics.append([0]*13)

    columns = [
        'POSITIVE SCORE', 'NEGATIVE SCORE', 'POLARITY SCORE', 'SUBJECTIVITY SCORE',
        'AVG SENTENCE LENGTH', 'PERCENTAGE OF COMPLEX WORDS', 'FOG INDEX',
        'AVG NUMBER OF WORDS PER SENTENCE', 'COMPLEX WORD COUNT', 'WORD COUNT',
        'SYLLABLE PER WORD', 'PERSONAL PRONOUNS', 'AVG WORD LENGTH'
    ]

    result_df = pd.concat([df, pd.DataFrame(metrics, columns=columns)], axis=1)
    result_df.to_excel(args.output, index=False)
    print(f"✅ Output saved to: {args.output}")

if __name__ == "__main__":
    main()

