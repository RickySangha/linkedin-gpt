import streamlit as st
import pandas as pd
import os
import json
import re
import base64
import numpy as np
from gpt.get_benefits import get_response

import time

email_status_mapping = {
    "All": None,  # No filter applied
    "Valid": 50,  # Replace with the actual value for "Valid"
    "Catch All": 45,  # Replace with the actual value for "Catch All"
}


# Function to load prompt templates
def load_prompt_templates():
    templates = {}
    for file in os.listdir("prompt_templates"):
        if file.endswith(".json"):
            with open(f"prompt_templates/{file}", "r") as f:
                templates[file[:-5]] = json.load(f)
    return templates


# Function to extract variables from template
def extract_variables(template_str):
    return re.findall(r"\{\{(.*?)\}\}", template_str)


def create_full_prompt(template_str, variable_mapping):
    # Replaces variables in the template string with values provided by the user.
    # :param template_str: String with variables in triple curly braces (e.g., {{{variable}}}).
    # :param variable_mapping: Dictionary mapping variable names to their respective values.
    # :return: String with variables replaced by their corresponding values.
    for var_name, var_value in variable_mapping.items():
        template_str = re.sub(rf"\{{{{{var_name}}}}}", var_value, template_str)
    return template_str


def update_csv(df, row_limit, selected_email_status_value, output_file):
    # Improved logic for determining the start_index
    # Ensure the necessary columns for AI Response exist
    if "First Line" not in df.columns:
        df["First Line"] = None
    for i in range(1, 4):
        if f"Benefit {i}" not in df.columns:
            df[f"Benefit {i}"] = None
    if "GPT Error" not in df.columns:
        df["GPT Error"] = None

    if os.path.exists(output_file):
        df_resume = pd.read_csv(output_file)

        # Find the first row where 'First Line' is empty and there is no 'GPT Error'
        for index, row in df_resume.iterrows():
            if pd.isna(row.get("First Line")) and pd.isna(row.get("GPT Error")):
                start_index = index
                df.loc[:start_index] = df_resume.loc[:start_index]
                break
        else:
            # If no such row is found, start from the end of df_resume
            start_index = len(df_resume)
    else:
        start_index = 0

    progress_bar = st.progress(0)
    total_rows = min(row_limit, len(df))

    for index, row in df.iterrows():
        if index < start_index or index >= total_rows:
            continue

        # Skip rows based on email status selection
        email_status_in_row = str(row["Email status"])
        if (
            selected_email_status_value is not None
            and str(selected_email_status_value) not in email_status_in_row
        ):
            continue

        # Create a mapping for the variables in the current row
        current_mapping = {var: row[variable_cols[var]] for var in variables}

        # Check if all values in the mapping are valid
        if all(
            value not in [None, "N/A", np.nan, ""] for value in current_mapping.values()
        ):
            # Generate the full prompt for the current row
            full_prompt = create_full_prompt(
                selected_template["prompt"], current_mapping
            )
            full_prompt_template = selected_template.copy()
            full_prompt_template["prompt"] = full_prompt

            ai_response = get_response(full_prompt_template)

            if ai_response:
                if isinstance(ai_response, dict) and "error" in ai_response:
                    df.at[index, "GPT Error"] = ai_response["error"]
                else:
                    df.at[index, "First Line"] = ai_response[0]
                    df.at[index, "Benefit 1"] = ai_response[1]
                    df.at[index, "Benefit 2"] = ai_response[2]
                    df.at[index, "Benefit 3"] = ai_response[3]

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


def test():
    for i in range(1, 5):
        time.sleep(3)
        print("OK")
        progress_bar = st.progress(0)
        progress = int((i + 1) / 100 * 100)
        progress_bar.progress(progress)


# Title and Description
st.title("Sales Email Generator")
st.markdown(
    """
    This tool helps you generate sales emails using AI, based on company descriptions. 
    Start by uploading a CSV file containing company descriptions. You will then be able to select the relevant column and initiate AI-powered email generation.
    """
)

# File Upload Section
uploaded_file = st.file_uploader("Upload a CSV file", type="csv")
data = None
selected_template_name = ""
variable_cols = {}
data_updated = False

# Sidebar for configurations
with st.sidebar:
    st.header("Configuration and Actions")

    # Load prompt templates
    prompt_templates = load_prompt_templates()

    # Configuration settings
    if uploaded_file is not None:
        data = pd.read_csv(uploaded_file)
        row_limit = st.number_input(
            "Enter the number of rows to scrape",
            min_value=1,
            max_value=len(data),
            value=len(data),
        )
        selected_template_name = st.selectbox(
            "Select a prompt template", [""] + list(prompt_templates.keys()), index=0
        )
        email_status = st.selectbox(
            "Select Email Status", list(email_status_mapping.keys())
        )
        selected_template = prompt_templates.get(selected_template_name, {})
        variables = (
            extract_variables(json.dumps(selected_template["prompt"]))
            if selected_template
            else []
        )

        # Inputs for template variables
        for var in variables:
            variable_cols[var] = st.selectbox(
                f"Column for variable '{var}'", [""] + list(data.columns)
            )

        # Button to start email generation process
        start_generation = st.button("Generate Sales Emails")

if uploaded_file is not None and selected_template_name:
    if start_generation and variables:
        with st.spinner("Generating sales emails... Please wait."):
            selected_email_status_value = email_status_mapping[email_status]
            # Loop over each row in the data
            data = update_csv(
                data,
                row_limit,
                selected_email_status_value,
                "temp_gpt_progress.csv",
            )
            # test()
            data_updated = True

    if data_updated:
        st.success("Sales email generation completed!")
        st.subheader("Generated Sales Emails Preview:")
        st.dataframe(data.head())

        # Download link for the final updated CSV
        csv = data.to_csv(index=False)
        st.download_button(
            label="Download updated CSV",
            data=csv,
            file_name="updated_AI_responses.csv",
            mime="text/csv",
        )
    else:
        st.subheader("Uploaded Data Preview:")
        st.dataframe(data.head() if data is not None else "No data to display.")

# Download Temporary Output File Link
output_file = "temp_gpt_progress.csv"
if os.path.exists(output_file):
    st.sidebar.markdown(
        "Download the temporary file containing AI Responses for review:"
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
<p class="big-font">Powered by OpenAI</p>
"""
st.markdown(footer, unsafe_allow_html=True)
