import streamlit as st
import pandas as pd
import httpx
from parsel import Selector
from urllib.parse import quote_plus
import time

st.set_page_config(page_title="Keyword Rank Checker", layout="wide")
st.title("🔍 Free Google Keyword Rank Checker")

# Country selector
country = st.selectbox("🌍 Select Google Country", [
    "India", "United States", "United Kingdom", "Canada", "Australia"
])
domain_map = {
    "India": "google.co.in",
    "United States": "google.com",
    "United Kingdom": "google.co.uk",
    "Canada": "google.ca",
    "Australia": "google.com.au"
}
google_domain = domain_map[country]

# Input website
website = st.text_input("🔗 Enter your website (e.g. example.com)").lower().strip()

# Keyword entry
keywords = []
keywords_text = st.text_area("📝 Enter keywords (one per line)")
csv_file = st.file_uploader("📂 Or upload CSV with 'keyword' column", type='csv')

if csv_file:
    try:
        df = pd.read_csv(csv_file)
        if 'keyword' in df.columns:
            keywords = df['keyword'].dropna().astype(str).tolist()
        else:
            st.error("CSV must contain a 'keyword' column.")
    except Exception as e:
        st.error(f"Could not read file: {e}")
elif keywords_text:
    keywords = [k.strip() for k in keywords_text.strip().split("\n") if k.strip()]

# Scraper using parsel and httpx
def get_rank(keyword, website, domain):
    search_url = f"https://www.{domain}/search?q={quote_plus(keyword)}&num=100"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/113.0.0.0 Safari/537.36"
        )
    }
    try:
        resp = httpx.get(search_url, headers=headers, timeout=10)
        sel = Selector(text=resp.text)
        links = sel.xpath('//div[@class="yuRUbf"]/a/@href').getall()

        for i, link in enumerate(links, start=1):
            if website in link.lower():
                return i
        return "NR"
    except Exception as e:
        return "Error"

# Main action button
if st.button("🚀 Start Checking"):
    if not website or not keywords:
        st.warning("Please enter both website and keywords.")
    else:
        results = []
        progress = st.progress(0)
        status = st.empty()

        for i, kw in enumerate(keywords):
            status.text(f"Checking: {kw} ({i+1}/{len(keywords)})")
            rank = get_rank(kw, website, google_domain)
            results.append({"Keyword": kw, "Rank": rank})
            progress.progress((i + 1) / len(keywords))
            time.sleep(5)  # Delay between requests

        df_result = pd.DataFrame(results)
        st.success("✅ All done!")
        st.dataframe(df_result)

        csv_export = df_result.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Download Results as CSV", csv_export, "rank_results.csv", "text/csv")
