import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus

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
# Input fields
# -------------------------------
website = st.text_input("🔗 Enter Your Website (e.g., example.com)", "")
keywords_text = st.text_area("📝 Enter Keywords (one per line)", "")

# Button to start check
if st.button("Check Rankings"):
    if not website or not keywords_text.strip():
        st.warning("⚠️ Please enter both website and at least one keyword.")
    else:
        keywords = [kw.strip() for kw in keywords_text.strip().split('\n') if kw.strip()]
        results = []

        # Display progress
        progress_bar = st.progress(0)
        status_text = st.empty()

        for i, keyword in enumerate(keywords):
            encoded_kw = quote_plus(keyword)
            url = f"https://www.{selected_google_domain}/search?q={encoded_kw}&num=100"

            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                              "(KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
            }

            try:
                response = requests.get(url, headers=headers, timeout=10)
                soup = BeautifulSoup(response.text, "html.parser")
                results_blocks = soup.find_all("div", class_="g")

                rank = "NR"
                for idx, block in enumerate(results_blocks, start=1):
                    link = block.find("a")
                    if link and website.lower() in link["href"]:
                        rank = idx
                        break

            except Exception as e:
                rank = "Error"

            results.append({"Keyword": keyword, "Rank": rank})
            progress_bar.progress((i + 1) / len(keywords))
            status_text.text(f"{i+1} of {len(keywords)} keywords checked")

        # -------------------------------
        # Display results
        # -------------------------------
        st.success("✅ Keyword Ranking Completed!")
        st.dataframe(results, use_container_width=True)
