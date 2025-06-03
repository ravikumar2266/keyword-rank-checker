import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
import pandas as pd
import time

st.set_page_config(page_title="Keyword Rank Checker", layout="wide")
st.title("🔍 Free Keyword Rank Checker (Google Top 100)")

# Country selection
country = st.selectbox("🌍 Select Google Country", [
    "India", "United States", "United Kingdom", "Canada", "Australia"
])
google_domains = {
    "India": "google.co.in",
    "United States": "google.com",
    "United Kingdom": "google.co.uk",
    "Canada": "google.ca",
    "Australia": "google.com.au"
}
selected_google_domain = google_domains[country]

# Website input
website = st.text_input("🔗 Enter Your Website (e.g., example.com)").lower().strip()

# Keyword input
keywords_text = st.text_area("📝 Enter Keywords (one per line)")
uploaded_file = st.file_uploader("📂 Or Upload a CSV File (with 'keyword' column)", type="csv")

# Prepare keywords
keywords = []
if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
        if 'keyword' in df.columns:
            keywords = df['keyword'].dropna().astype(str).tolist()
        else:
            st.error("CSV must have a 'keyword' column.")
    except Exception as e:
        st.error(f"Error reading CSV: {e}")
elif keywords_text.strip():
    keywords = [kw.strip() for kw in keywords_text.split('\n') if kw.strip()]

# Search function
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
        response = requests.get(search_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        results = soup.select("div.yuRUbf > a")

        for i, tag in enumerate(results, start=1):
            href = tag.get("href")
            if href and website in href:
                return i
        return "NR"
    except:
        return "Error"

# Button to trigger ranking check
if st.button("🔎 Check Rankings"):
    if not website or not keywords:
        st.warning("⚠️ Please enter both website and keywords.")
    else:
        progress_bar = st.progress(0)
        status = st.empty()
        results = []

        for i, keyword in enumerate(keywords):
            rank = get_rank(keyword, website, selected_google_domain)
            results.append({"Keyword": keyword, "Rank": rank})

            progress_bar.progress((i + 1) / len(keywords))
            status.text(f"Processed {i + 1} of {len(keywords)} keywords")

            time.sleep(5)  # ⏱️ Add delay to avoid getting blocked

        st.success("✅ Done! See the results below.")
        df_results = pd.DataFrame(results)
        st.dataframe(df_results, use_container_width=True)

        # Export to CSV
        csv = df_results.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Results as CSV",
            data=csv,
            file_name="rank_results.csv",
            mime="text/csv"
        )
