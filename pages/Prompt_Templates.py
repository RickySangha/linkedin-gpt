import streamlit as st
import json
import os
import glob


# Function to save prompt template
def save_prompt_template(prompt_template, template_name):
    with open(f"prompt_templates/{template_name}.json", "w") as file:
        json.dump(prompt_template, file)
    st.success(f"Prompt template '{template_name}' saved successfully!")


# Function to load prompt templates
def load_prompt_templates():
    files = glob.glob("prompt_templates/*.json")
    templates = {}
    for file in files:
        with open(file, "r") as f:
            templates[os.path.basename(file)[:-5]] = json.load(
                f
            )  # Updated to extract filename without path
    return templates


# Title and Description
st.title("Custom AI Prompt Configuration")
st.markdown(
    """
    Configure and save your custom AI prompt template. 
    Enter the various parts of your prompt template in the fields below and save it for use in AI-powered applications.
    """
)

# Sidebar for existing templates
existing_templates = load_prompt_templates()
selected_template = st.sidebar.selectbox(
    "Existing Templates", [""] + list(existing_templates.keys())
)

# Variables to hold form values
template_name = ""
prompt = ""
system_prompt = ""
example_1_input = example_1_output = ""
example_2_input = example_2_output = ""
example_3_input = example_3_output = ""

# Populate form if a template is selected
if selected_template:
    template = existing_templates[selected_template]
    template_name = selected_template
    prompt = template["prompt"]
    system_prompt = template["system_prompt"]
    example_1_input = template["example_1"]["input"]
    example_1_output = template["example_1"]["output"]
    example_2_input = template["example_2"]["input"]
    example_2_output = template["example_2"]["output"]
    example_3_input = template["example_3"]["input"]
    example_3_output = template["example_3"]["output"]

# User input for different parts of the prompt template
with st.form("prompt_form"):
    st.subheader("Configure Your Prompt Template")
    template_name = st.text_input("Template Name", value=template_name)
    prompt = st.text_area("Prompt", value=prompt, height=100)
    system_prompt = st.text_area("System Prompt", value=system_prompt, height=100)
    example_1_input = st.text_area("Example 1 Input", value=example_1_input, height=100)
    example_1_output = st.text_area(
        "Example 1 Output", value=example_1_output, height=100
    )
    example_2_input = st.text_area("Example 2 Input", value=example_2_input, height=100)
    example_2_output = st.text_area(
        "Example 2 Output", value=example_2_output, height=100
    )
    example_3_input = st.text_area("Example 3 Input", value=example_3_input, height=100)
    example_3_output = st.text_area(
        "Example 3 Output", value=example_3_output, height=100
    )

    # Submit button for the form
    submitted = st.form_submit_button("Save Prompt Template")

    if submitted and template_name:
        prompt_template = {
            "system_prompt": system_prompt,
            "prompt": prompt,
            "example_1": {"input": example_1_input, "output": example_1_output},
            "example_2": {"input": example_2_input, "output": example_2_output},
            "example_3": {"input": example_3_input, "output": example_3_output},
        }
        save_prompt_template(prompt_template, template_name)
    elif submitted and not template_name:
        st.error("Please provide a name for the template.")

# Footer
footer = """
<style>
.big-font {
    font-size:20px !important;
    font-weight: bold;
}
</style>
<p class="big-font">Custom AI Prompt Configuration Tool</p>
"""
st.markdown(footer, unsafe_allow_html=True)
