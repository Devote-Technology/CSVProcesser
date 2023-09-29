from flask import Flask, request, jsonify
from io import StringIO
from flask_cors import CORS
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import SessionNotCreatedException, WebDriverException

app = Flask(__name__)
CORS(app)

def get_domain_from_google(company_name, street_address, state):
    query = f"{company_name} official website based in {state} with {street_address}"

    driver = webdriver.Chrome()
    driver.get(f"https://www.google.com/search?q={query}")

    try:
        print("----- Page Source Start -----")
        print(driver.page_source)
        print("----- Page Source End -----")

        elements = WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "cite"))
        )

        valid_domains = []
        for element in elements:
            domain = element.text
            if domain:  # filter out empty or irrelevant domains
                valid_domains.append(domain.split(" ")[0])

        chosen_domain = valid_domains[0] if valid_domains else "No valid domain found"
        print(f"Chosen domain: {chosen_domain}")

        return chosen_domain

    except Exception as e:
        print(f"Exception while fetching domain: {e}")
        driver.save_screenshot("screenshot.png")
        return {"error": str(e)}

    finally:
        driver.quit()

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
    try:
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

        # Convert DataFrame to CSV string
        csv_buffer = StringIO()
        df.to_csv(csv_buffer, index=False)
        csv_str = csv_buffer.getvalue()

        # Return as part of the response
        print("CSV String:", csv_str)
        return jsonify({"status": "success", "csv": csv_str})

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"status": "error", "message": f"An error occurred: {e}"}), 400

if __name__ == '__main__':
    app.run(debug=True)
