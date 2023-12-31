from openai import OpenAI
import pandas as pd
import re
import json
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()


def load_prompt_template(file_path):
    with open(file_path, "r") as file:
        return json.load(file)


def clean_string(input_string):
    cleaned_string = re.sub(r"\s+", " ", input_string)
    cleaned_string = re.sub(r"[^\w\s]", "", cleaned_string)
    return cleaned_string


def replace_variables(prompt, variables):
    for key, value in variables.items():
        prompt = prompt.replace(f"{{{{{key}}}}}", value)
    return prompt


def get_response(prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": prompt["system_prompt"],
                },
                {
                    "role": "user",
                    "content": clean_string(prompt["example_1"]["input"]),
                },
                {"role": "system", "content": prompt["example_1"]["output"]},
                {
                    "role": "user",
                    "content": clean_string(prompt["example_2"]["input"]),
                },
                {
                    "role": "system",
                    "content": clean_string(prompt["example_2"]["output"]),
                },
                # {"role": "user", "content": clean_string(prompt_template.example_3["input"])},
                # {"role": "system", "content": prompt_template.example_3["output"]},
                {"role": "user", "content": clean_string(prompt["prompt"])},
            ],
        )
        print(list(json.loads(response.choices[0].message.content).values()))
        return list(json.loads(response.choices[0].message.content).values())
    except Exception as e:
        error_message = f"Error occurred while getting AI Response: {e}"
        print(error_message)
        return {"error": error_message}


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
