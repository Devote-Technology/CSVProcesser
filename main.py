from googlesearch import search as gs_search
import pandas as pd
## This is file a file to process csv files, it does not connect to flask and is used to process.
csv_path = 'csvFiles/orgs-3.csv.errors.csv'
output_csv_path = 'csvFiles/updatedFile.csv'
State = "California"


def get_domain_from_google(company_name, street_address):
    query = f"{company_name} official website based in {State} with {street_address}"
    try:
        for j in gs_search(query):
            return j
    except Exception as e:
        print(f"Error while searching: {e}")
        return None


try:
    df = pd.read_csv(csv_path)
except FileNotFoundError:
    print(f"File {csv_path} not found.")
    exit(1)
except pd.errors.EmptyDataError:
    print(f"File {csv_path} is empty.")
    exit(1)
except Exception as e:
    print(f"An error occurred while reading the CSV: {e}")
    exit(1)

drop_indices = []

for index, row in df.iterrows():
    company_name = row['Company Name']
    street_address = row['Street Address']
    domain = get_domain_from_google(company_name, street_address)

    if domain:  # If a domain is found
        drop_indices.append(index)
        df.at[index, 'Company Domain Name'] = domain

df.drop(drop_indices, inplace=True)  # Drop rows
df.drop(['Error code', 'Reason'], axis=1, inplace=True)  # Drop columns

try:
    df.to_csv(output_csv_path, index=False)
except Exception as e:
    print(f"An error occurred while writing to the CSV: {e}")
