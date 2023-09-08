from flask import Flask, request, jsonify
import pandas as pd
from googlesearch import search
### This file will connect to an api
## instal googlesearch and beautfulsoup4
## python3 -m pip install googlesearch-python
app = Flask(__name__)

State = "California"
#Run python app.py
def get_domain_from_google(company_name, street_address):
    query = f"{company_name} official website based in {State} with {street_address}"
    try:
        for j in search(query):
            return j
    except Exception as e:
        return {"error": str(e)}

@app.route('/search_domain', methods=['POST'])
def search_domain():
    data = request.json
    company_name = data.get("company_name", "")
    street_address = data.get("street_address", "")
    result = get_domain_from_google(company_name, street_address)

    if "error" in result:
        return jsonify({"status": "error", "message": result["error"]}), 400

    return jsonify({"status": "success", "domain": result})

@app.route('/process_csv', methods=['GET'])
def process_csv():
    csv_path = 'csvFiles/orgs-3.csv.errors.csv'
    output_csv_path = 'csvFiles/updatedFile.csv'
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        return jsonify({"status": "error", "message": f"File {csv_path} not found."}), 400

    for index, row in df.iterrows():
        company_name = row['Company Name']
        street_address = row['Street Address']
        domain = get_domain_from_google(company_name, street_address)
        df.at[index, 'Company Domain Name'] = domain

    df.drop(['Error code', 'Reason'], axis=1, inplace=True)

    try:
        df.to_csv(output_csv_path, index=False)
    except Exception as e:
        return jsonify({"status": "error", "message": f"An error occurred while writing to the CSV: {e}"}), 400

    return jsonify({"status": "success", "message": "CSV processed successfully"})


if __name__ == '__main__':
    app.run(debug=True)
