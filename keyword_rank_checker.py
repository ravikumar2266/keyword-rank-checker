import streamlit as st
import requests
from bs4 import BeautifulSoup

def get_google_domain(country):
    google_domains = {
        "India": "google.co.in",
        "United States": "google.com",
        "United Kingdom": "google.co.uk",
        "Canada": "google.ca",
        "Australia": "google.com.au"
    }
    return google_domains.get(country, "google.com")

def get_keyword_ranking(keyword, website, domain):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"
    }
    query = keyword.replace(" ", "+")
    search_url = f"https://www.{domain}/search?q={query}&num=100"

    try:
        response = requests.get(search_url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        results = soup.find_all("div", class_="yuRUbf")

        for index, result in enumerate(results):
            link = result.find("a")["href"]
            if website in link:
                return index + 1, link
        return "NR", ""
    except Exception as e:
        return "Error", str(e)

st.title("Keyword Rank Checker")

st.markdown("Upload a CSV file with a column named `keyword`.")
uploaded_file = st.file_uploader("Upload CSV", type="csv")
website = st.text_input("Enter your website domain (e.g., example.com)")
country = st.selectbox("Select Country", ["India", "United States", "United Kingdom", "Canada", "Australia"])
google_domain = get_google_domain(country)

if uploaded_file is not None and website:
    import pandas as pd
    df = pd.read_csv(uploaded_file)
    if "keyword" not in df.columns:
        st.error("CSV must contain a column named 'keyword'")
    else:
        if st.button("Check Rankings"):
            rankings = []
            for idx, row in df.iterrows():
                keyword = row["keyword"]
                rank, url = get_keyword_ranking(keyword, website, google_domain)
                rankings.append({
                    "Keyword": keyword,
                    "Rank": rank,
                    "Ranking URL": url
                })
                st.write(f"{idx+1}/{len(df)} done...")

            result_df = pd.DataFrame(rankings)
            st.dataframe(result_df)

            csv = result_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download Results as CSV",
                data=csv,
                file_name="keyword_rankings.csv",
                mime="text/csv",
            )