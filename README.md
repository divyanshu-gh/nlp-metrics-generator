# NLP Text Analyzer

## 🔍 About the Project

This project is part of the Data Scientist Associate test assignment. The objective was to build a Python-based solution that:

- Extracts article content from URLs
- Cleans and preprocesses the text
- Calculates 13 NLP metrics like polarity, subjectivity, word count, etc.
- Outputs everything into a clean Excel file in the required format

---

##  My Approach:

Before jumping into coding, I spent time understanding the objective, data structure, and expected output format. I broke the assignment into three core components:
1. Scraping the content
2. Text preprocessing and analysis
3. Exporting structured output

I wanted this solution to feel natural and real — like something I’d genuinely build in a project setting, So I kept my code clean, minimal and modular.

---

### 1. Starting Point

I created a logical folder structure with:
- `input/` for `Input.xlsx`
- `articles/` to store scraped content
- `stopwords/` and `dictionary/` for external text processing assets

---

### 2. Scraper Design – Multi-Browser Friendly 🖥️

One of the first things I implemented was **support for multiple web browsers** (Edge and Chrome). Rather than locking the solution to one specific browser like Chrome, I designed the scraper to work with either browser through a command-line argument:

```bash
python main.py --browser edge 
```

This makes the tool much more flexible and usable across different environments — especially in cases where ChromeDriver or EdgeDriver compatibility becomes an issue.

Initially, I started with ChromeDriver, but due to driver version mismatches and availability, I shifted to Microsoft Edge, which turned out to be more reliable for my setup. I made sure that this switch could be easily handled through the command line by any user.

---

### 3. Handling Repetitive Downloads

To avoid re-downloading and reprocessing articles, I implemented a smart check that skips already-saved articles. This speeds up re-runs and saves unnecessary network overhead.

---

### 4. The Biggest Hurdle – `punkt_tab` 🔥

A major blocker I faced was the `punkt_tab` error from NLTK when using `sent_tokenize()` and `word_tokenize()`. The required resource `punkt_tab` wasn't downloadable, and it caused the script to fail during runtime.

To solve this, I used custom-built alternatives:
- For sentence splitting: `re.split(r'[.!?]+', text)`
- For word tokenization: `re.findall(r'\b\w+\b', text.lower())`

This made the project **completely independent from any external NLTK downloads**, making it more robust and portable.

---

### 5 Metric Calculations

All 13 text analysis metrics were computed, including:
- POSITIVE & NEGATIVE SCORE
- POLARITY & SUBJECTIVITY
- FOG INDEX, AVERAGE WORD LENGTH, etc.

I added supporting utility functions for syllable counting, complexity detection, and pronoun detection.

---

##  Features

- ✅ Article scraping from 147 URLs
- ✅ Skip already scraped files to save time
- ✅ Multi-browser scraping support (Chrome + Edge)
- ✅ Custom text tokenization (no punkt_tab bugs)
- ✅ Saves final output in `Output.xlsx` with all required columns

---

## 🛠️ How to Run

1. Place `Input.xlsx` inside the `input/` folder
2. Ensure you have:
   - `stopwords/` folder with all `.txt` files
   - `dictionary/` folder with `positive-words.txt` and `negative-words.txt`
   - Either `chromedriver.exe` or `msedgedriver.exe` in the project root

3. Open terminal and run:

```bash
python main.py --browser edge
```

Or for Chrome:

```bash
python main.py --browser chrome
```

This will generate:
```
output/Output.xlsx
```

---

##  Dependencies

Install all required packages with:

```bash
pip install pandas openpyxl selenium nltk
```

Make sure your Python version is **3.7 or higher**.

---

##  Notes

- Designed with flexibility and ease of use in mind.
- Minimal external dependencies.
- Avoids known NLTK issues like `punkt_tab` with regex-based logic.
- Can easily be extended to support other browsers or websites.
