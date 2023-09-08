from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
from googlesearch import search
from time import sleep

app = Flask(__name__)
CORS(app)

def get_domain_from_google(company_name, street_address, state):
    query = f"{company_name} official website based in {state} with {street_address}"
    sleep(2)
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
    state = data.get("state", "")
    result = get_domain_from_google(company_name, street_address, state)

    if "error" in result:
        return jsonify({"status": "error", "message": result["error"]}), 400

    return jsonify({"status": "success", "domain": result})

@app.route('/process_csv', methods=['POST'])
def process_csv():
    print("Starting Process")
    data = request.json
    orgs = data.get("orgs", [])

    df = pd.DataFrame(orgs)

    for index, row in df.iterrows():
        print(f"Processing row {index}")
        company_name = row['Company Name']
        street_address = row['Street Address']
        state = row['State']
        domain = get_domain_from_google(company_name, street_address, state)
        df.at[index, 'Company Domain Name'] = domain

    columns_to_drop = ['Error code', 'Reason']
    for col in columns_to_drop:
        if col in df.columns:
            df.drop([col], axis=1, inplace=True)

    try:
        output_csv_path = 'updatedFile.csv'
        df.to_csv(output_csv_path, index=False)
    except Exception as e:
        return jsonify({"status": "error", "message": f"An error occurred while writing to the CSV: {e}"}), 400

    output_data = df.to_dict('records')
    return jsonify({"status": "success", "orgs": output_data})

if __name__ == '__main__':
    app.run(debug=True)
