import requests
from bs4 import BeautifulSoup
import csv

def fetch_page_content():
    url = "https://scsa.org/classification/A148761"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
        return None

    return response.content

def find_target_table(soup, division_name):
    tables = soup.find_all('table')
    for index, table in enumerate(tables):
        if table.find('th', string=division_name):
            return table
    return None

def extract_headers(table, division_name):
    header_row = table.find('tr')
    headers = [th.text.strip() for th in header_row.find_all('th') if th.text.strip()]
    headers = [h for h in headers if h != 'Status']
    headers.insert(0, 'Division')
    return headers

def extract_data(table, headers, division_name):
    data = []
    extracting = False
    for row in table.find_all('tr')[1:]:
        th = row.find('th')
        if th:
            if th.text.strip() == division_name:
                extracting = True
            elif extracting:
                break

        if extracting:
            columns = row.find_all('td')
            if len(columns) >= len(headers) - 1:
                event_data = {headers[0]: division_name}
                for i in range(1, len(headers)):
                    event_data[headers[i]] = columns[i-1].text.strip()
                data.append(event_data)
    return data

def get_division_data(soup, division_name):
    target_table = find_target_table(soup, division_name)
    if not target_table:
        print(f"Could not find the table containing '{division_name}'.")
        return [], []

    headers = extract_headers(target_table, division_name)
    data = extract_data(target_table, headers, division_name)
    return headers, data

def print_division_data(data, division_name):
    print(f"{division_name} Division Data\n")
    for entry in data:
        print(f"  • Event: {entry.get('Event')}")
        print(f"  • Date: {entry.get('Date')}")
        print(f"  • Stage: {entry.get('Stage')}")
        print(f"  • Time: {entry.get('Time')}")
        print(f"  • Peak: {entry.get('Peak')}")
        print()

def export_to_csv(headers, data, filename):
    with open(filename, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        writer.writerows(data)
    print(f"Data exported to {filename}")

# Fetch the page content once
page_content = fetch_page_content()
if page_content:
    soup = BeautifulSoup(page_content, 'html.parser')

    # Specify the list of division names
    division_names = ['Rimfire Rifle Open', 'PCC Optics', 'Rimfire Pistol Open']

    # Loop through each division
    for division_name in division_names:
        print(f"\nFetching data for division: {division_name}")
        # Fetch the data for the specified division
        headers, division_data = get_division_data(soup, division_name)
        
        if division_data:  # Only proceed if data is found
            # Print the formatted data
            print_division_data(division_data, division_name)
            
            # Export the data to a CSV file
            csv_filename = f"{division_name.replace(' ', '_')}_data.csv"
            export_to_csv(headers, division_data, csv_filename)
        else:
            print(f"No data found for division: {division_name}")