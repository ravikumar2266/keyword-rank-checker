<details>
<summary>Click to expand full code</summary>
import streamlit as st
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import pandas as pd
import time
import random

ua = UserAgent()

def get_google_results(keyword, page=0):
    query = keyword.replace(' ', '+')
    start = page * 10
    url = f"https://www.google.com/search?q={query}&start={start}"
    headers = {"User-Agent": ua.random}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return None
    return BeautifulSoup(response.text, "html.parser")

def extract_links(soup):
    links = []
    for result in soup.select('div.yuRUbf > a'):
        href = result.get('href')
        if href:
            links.append(href)
    return links

def find_rank(keyword, website, pages_to_check=10):
    for page in range(pages_to_check):
        soup = get_google_results(keyword, page)
        if not soup:
            continue
        links = extract_links(soup)
        for idx, link in enumerate(links):
            if website.lower() in link.lower():
                return page * 10 + idx + 1, link
        time.sleep(random.uniform(1.5, 3.5))
    return "NR", "-"

def process_keywords(keywords, website):
    data = []
    for kw in keywords:
        rank, url = find_rank(kw.strip(), website.strip())
        data.append({
            "Keyword": kw,
            "Rank": rank,
            "Ranking URL": url
        })
    return pd.DataFrame(data)

# ------------------ Streamlit UI ------------------

st.set_page_config(page_title="Keyword Rank Checker", layout="wide")
st.title("🔍 Google Keyword Rank Checker")
st.markdown("**Check your website's ranking for multiple keywords on Google (Top 100 results)**")

website = st.text_input("Enter your website (e.g. `yourwebsite.com`):")

keyword_input = st.text_area("Enter keywords (one per line):")
uploaded_file = st.file_uploader("Or upload a .txt or .csv file", type=["txt", "csv"])

keywords = []

if uploaded_file:
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
        keywords = df.iloc[:, 0].dropna().tolist()
    else:
        content = uploaded_file.read().decode("utf-8")
        keywords = content.strip().splitlines()
elif keyword_input:
    keywords = keyword_input.strip().splitlines()

if st.button("Check Rankings") and website and keywords:
    with st.spinner("Checking rankings..."):
        results_df = process_keywords(keywords, website)
        st.success("Done!")
        st.dataframe(results_df)

        # Download as CSV
        csv = results_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download Results as CSV",
            data=csv,
            file_name="keyword_rankings.csv",
            mime="text/csv"
        )
elif st.button("Check Rankings"):
    st.warning("Please enter your website and at least one keyword.")
    </details>