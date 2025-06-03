import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
import pandas as pd
import io

# -------------------------------
# Page configuration
# -------------------------------
st.set_page_config(page_title="Keyword Rank Checker", layout="wide")
st.title("🔍 Keyword Rank Checker")

# -------------------------------
# Country dropdown selector
# -------------------------------
country = st.selectbox("🌎 Select Country", [
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

# -------------------------------
# Input: Website URL
# -------------------------------
website = st.text_input("🔗 Enter Your Website (e.g., example.com)", "")

# -------------------------------
# Input Option 1: Text area
# -------------------------------
keywords_text = st.text_area("📝 Enter Keywords (one per line)", "")

# -------------------------------
# Input Option 2: CSV Upload
# -------------------------------
uploaded_file = st.file_uploader("📂 Or Upload CSV (Column: keyword)", type=["csv"])

# -------------------------------
# Prepare Keyword List
# -------------------------------
keywords = []

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
        if 'keyword' in df.columns:
            keywords = df['keyword'].dropna().astype(str).tolist()
        else:
            st.error("Uploaded CSV must have a 'keyword' column.")
    except Exception as e:
        st.error(f"❌ Error reading CSV: {e}")

elif keywords_text.strip():
    keywords = [kw.strip() for kw in keywords_text.strip().split('\n') if kw.strip()]

# -------------------------------
# Start Search Button
# -------------------------------
if st.button("Check Rankings"):
    if not website or not keywords:
        st.warning("⚠️ Please enter your website and keywords (via text or CSV).")
    else:
        results = []
        progress_bar = st.progress(0)
        status_text = st.empty()

        for i, keyword in enumerate(keywords):
            encoded_kw = quote_plus(keyword)
            url = f"https://www.{selected_google_domain}/search?q={encoded_kw}&num=100"

            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                              "(KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
            }

            rank = "NR"
            try:
                response = requests.get(url, headers=headers, timeout=10)
                soup = BeautifulSoup(response.text, "html.parser")
                results_blocks = soup.find_all("div", class_="g")

                for idx, block in enumerate(results_blocks, start=1):
                    link = block.find("a")
                    if link and website.lower() in link["href"].lower():
                        rank = idx
                        break
            except Exception as e:
                rank = "Error"

            results.append({"Keyword": keyword, "Rank": rank})
            progress_bar.progress((i + 1) / len(keywords))
            status_text.text(f"{i+1} of {len(keywords)} keywords checked")

        # Convert results to DataFrame
        result_df = pd.DataFrame(results)

        st.success("✅ Keyword Ranking Completed!")
        st.dataframe(result_df, use_container_width=True)

        # -------------------------------
        # Export Results Button
        # -------------------------------
        csv = result_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download Results as CSV",
            data=csv,
            file_name="keyword_rank_results.csv",
            mime="text/csv"
        )
