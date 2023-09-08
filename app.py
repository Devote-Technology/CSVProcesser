from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import base64
from googlesearch import search



app = Flask(__name__)
CORS(app)

def get_domain_from_google(company_name, street_address, state):
    query = f"{company_name} official website based in {state} with {street_address}"
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
    data = request.json
    encoded_csv = data.get("orgs", "")
    decoded_csv = base64.b64decode(encoded_csv)

    temp_csv_path = 'temp.csv'
    output_csv_path = 'updatedFile.csv'

    with open(temp_csv_path, "wb") as f:
        f.write(decoded_csv)

    try:
        df = pd.read_csv(temp_csv_path)
    except FileNotFoundError:
        return jsonify({"status": "error", "message": f"File {temp_csv_path} not found."}), 400

    for index, row in df.iterrows():
        company_name = row['Company Name']
        street_address = row['Street Address']
        state = row['State']
        domain = get_domain_from_google(company_name, street_address, state)
        df.at[index, 'Company Domain Name'] = domain

    df.drop(['Error code', 'Reason'], axis=1, inplace=True)

    try:
        df.to_csv(output_csv_path, index=False)
    except Exception as e:
        return jsonify({"status": "error", "message": f"An error occurred while writing to the CSV: {e}"}), 400

    with open(output_csv_path, "rb") as f:
        encoded_output = base64.b64encode(f.read()).decode()

    return jsonify({"status": "success", "encoded_csv": encoded_output})

if __name__ == '__main__':
    app.run(debug=True)
