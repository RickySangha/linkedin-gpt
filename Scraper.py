import streamlit as st
import pandas as pd
import os
import base64
from urllib.parse import urlparse
from scrapers.duckduckgo_scraper import DuckDuckGoScraper
from scrapers.linkedin_scraper import LinkedInScraper
from scrapers.scraper_config import ScraperConfig


# Function to update CSV with scraped data
from urllib.parse import urlparse


def update_csv(df, company_name_col, selections, config, row_limit, output_file):
    duck_scraper = DuckDuckGoScraper(config)
    linkedin_scraper = LinkedInScraper(config)

    # Ensure the necessary columns exist
    if "LinkedIn URL" in selections and "Company linkedin url" not in df.columns:
        df["Company linkedin url"] = None
    if "Company About Us" in selections and "Company About Us" not in df.columns:
        df["Company About Us"] = None
    if "Scraping Error" not in df.columns:
        df["Scraping Error"] = None
    if "Scrape attempted" not in df.columns:
        df["Scrape attempted"] = False

    # Improved logic for determining the start_index
    if os.path.exists(output_file):
        df_resume = pd.read_csv(output_file)
        completed_rows = df_resume[df_resume["Scrape attempted"] == True]
        start_index = completed_rows.index[-1] + 1 if not completed_rows.empty else 0
        df.loc[:start_index] = df_resume.loc[:start_index]
    else:
        start_index = 0

    progress_bar = st.progress(0)
    total_rows = min(row_limit, len(df))

    for index, row in enumerate(df.iterrows()):
        if index < start_index or index >= total_rows:
            continue

        company_name = row[1][company_name_col]

        # Check if a valid LinkedIn URL already exists
        linkedin_url = (
            str(df.at[index, "Company linkedin url"])
            if df.at[index, "Company linkedin url"] is not None
            else ""
        )
        parsed_url = urlparse(linkedin_url) if linkedin_url else None

        if "LinkedIn URL" in selections and (
            not parsed_url.scheme or not parsed_url.netloc
        ):
            df.at[index, "Scrape attempted"] = True
            result = duck_scraper.get_linkedin_url(company_name)
            if isinstance(result, dict) and "error" in result:
                df.at[index, "Scraping Error"] = result["error"]
            else:
                df.at[index, "Company linkedin url"] = result
                parsed_url = urlparse(result)

        if "Company About Us" in selections and parsed_url.scheme and parsed_url.netloc:
            df.at[index, "Scrape attempted"] = True
            linkedin_result = linkedin_scraper.get_company_data(
                df.at[index, "Company linkedin url"]
            )
            if isinstance(linkedin_result, dict) and "error" in linkedin_result:
                df.at[index, "Scraping Error"] = linkedin_result["error"]
            elif linkedin_result:
                df.at[index, "Company About Us"] = linkedin_result.get(
                    "about_us", "Data not found"
                )

        # Update the progress bar and save intermediate results
        progress = int((index + 1) / total_rows * 100)
        progress_bar.progress(progress)
        df.to_csv(output_file, index=False)

    return df


# Function to generate download link
def generate_download_link(file_path, label):
    with open(file_path, "rb") as f:
        bytes = f.read()
        b64 = base64.b64encode(bytes).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="{os.path.basename(file_path)}">{label}</a>'
        return href


# Title and Description
st.title("Company Data Scraper")
st.markdown(
    """
    This application helps you scrape company data like LinkedIn URLs and 'About Us' information.
    Upload a CSV file with company names and select the data you want to scrape. Start by uploading a CSV file with a list of company names to begin, then configure your settings in the sidebar.
    """
)

# File Upload Section
uploaded_file = st.file_uploader("Upload a CSV file", type="csv")
data = None
start_scraping = False
data_updated = False

# Sidebar for configurations
with st.sidebar:
    st.header("Configuration and Actions")

    # Configuration settings
    company_name_col = ""
    row_limit = 1
    options = []
    valid_columns = []
    if uploaded_file is not None:
        data = pd.read_csv(uploaded_file)
        valid_columns = [
            col
            for col in data.columns
            if "company" in col.lower()
            and ("domain" in col.lower() or "name" in col.lower())
        ]
        company_name_col = st.selectbox(
            "Select the column with company names or domains", [""] + list(data.columns)
        )

        if company_name_col and company_name_col not in valid_columns:
            st.warning(
                "This doesn't sound like the company name or domain. Are you sure you want to continue with this selection? Your scrape may not work correctly."
            )

        row_limit = st.number_input(
            "Enter the number of rows to scrape",
            min_value=1,
            max_value=len(data),
            value=len(data),
        )

        # Multi-select for data to scrape
        options = st.multiselect(
            "Select data to scrape:",
            ["LinkedIn URL", "Company About Us", "AI Response"],
        )

        # Button to start scraping
        start_scraping = st.button("Update CSV with Scraped Data")

# Main area for scraping process and results
if uploaded_file is not None:
    if start_scraping and company_name_col and not data_updated:
        config = ScraperConfig(use_proxy=False)
        with st.spinner("Scraping data... Please wait."):
            try:
                data = update_csv(
                    data,
                    company_name_col,
                    options,
                    config,
                    row_limit,
                    "temp_scraping_progress.csv",
                )
                data_updated = True
            except Exception as e:
                st.error(f"An error occurred: {e}")

    if data_updated:
        st.success("Scraping completed!")
        st.subheader("Updated Data Preview:")
        st.dataframe(data.head())

        # Download link for the final updated CSV
        csv = data.to_csv(index=False)
        st.download_button(
            label="Download updated CSV",
            data=csv,
            file_name="updated_company_data.csv",
            mime="text/csv",
        )
    else:
        st.subheader("Uploaded Data Preview:")
        st.dataframe(data.head())

# Download Temporary Output File Link
output_file = "temp_scraping_progress.csv"
if os.path.exists(output_file):
    st.sidebar.markdown(
        "Download the temporary file containing partially scraped data for review:"
    )
    st.sidebar.markdown(
        generate_download_link(output_file, "Download Temporary Output File"),
        unsafe_allow_html=True,
    )

# Footer
footer = """
<style>
.big-font {
    font-size:20px !important;
    font-weight: bold;
}
</style>
<p class="big-font">Created by Qrew</p>
"""
st.markdown(footer, unsafe_allow_html=True)
