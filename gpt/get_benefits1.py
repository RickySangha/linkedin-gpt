from openai import OpenAI
import re
import pandas as pd
from dotenv import load_dotenv

from prompt_templates.prompt_template import prompt_template, get_prompt

load_dotenv()

client = OpenAI()


def clean_string(input_string):
    # Replace newline characters and other special characters
    cleaned_string = re.sub(
        r"\s+", " ", input_string
    )  # Replace all whitespace characters (including newlines) with a single space
    cleaned_string = re.sub(
        r"[^\w\s]", "", cleaned_string
    )  # Remove non-word characters (keeps only letters, digits, and spaces)

    return cleaned_string


def get_response(description):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": prompt_template["system_prompt"],
            },
            {
                "role": "user",
                "content": clean_string(prompt_template["example_1"]["input"]),
            },
            {"role": "system", "content": prompt_template["example_1"]["output"]},
            {
                "role": "user",
                "content": clean_string(prompt_template["example_2"]["input"]),
            },
            {"role": "system", "content": prompt_template["example_2"]["output"]},
            # {"role": "user", "content": clean_string(prompt_template.example_3["input"])},
            # {"role": "system", "content": prompt_template.example_3["output"]},
            {"role": "user", "content": get_prompt(description)},
        ],
    )
    return response


def gpt_responses_to_csv(input_csv_path, output_csv_path):
    # Read CSV into DataFrame
    df = pd.read_csv(input_csv_path)

    # Scrape data for each URL and handle errors
    for index, row in df.iterrows():
        try:
            description = row["About us"]
            if description:
                response = get_response(description)
                df.at[index, "First line"] = response.choices[0].message.content[
                    "First Line"
                ]
                df.at[index, "Benefit_1"] = response.choices[0].message.content[
                    "Benefit_1"
                ]
                df.at[index, "Benefit_2"] = response.choices[0].message.content[
                    "Benefit_2"
                ]
                df.at[index, "Benefit_3"] = response.choices[0].message.content[
                    "Benefit_3"
                ]
            else:
                df.at[index, "First line"] = "N/A"  # No error
                df.at[index, "Benefit_1"] = "N/A"  # No error
                df.at[index, "Benefit_2"] = "N/A"  # No error
                df.at[index, "Benefit_3"] = "N/A"  # No error
        except Exception as e:
            print(f"Error occurred: {e}")
            df.at[index, "Error"] = str(e)  # Log the error
        finally:
            print(response)
            df.to_csv(
                output_csv_path, index=False
            )  # Append without header for subsequent rows
