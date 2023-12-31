import csv


# TODO: writer should write row by row instead of overwriting entire file everytime.
# TODO: Do we need to make this class?
def read_urls_from_csv(file_path):
    urls = []
    with open(file_path, mode="r", newline="", encoding="utf-8") as file:
        reader = csv.reader(file)
        next(reader, None)  # Skip the header
        for row in reader:
            urls.append(row[0])  # Assuming URLs are in the first column
    return urls


def write_data_to_csv(file_path, data, header):
    with open(file_path, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(header)  # Write the header
        for record in data:
            writer.writerow(record)
