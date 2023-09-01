from flask import Flask, request, jsonify
import pandas as pd
from googlesearch import search as gs_search
#### run python app.py
app = Flask(__name__)

State = "California"


def get_domain_from_google(company_name, street_address):
    query = f"{company_name} official website based in {State} with {street_address}"
    try:
        for j in gs_search(query):
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


if __name__ == '__main__':
    app.run(debug=True)
