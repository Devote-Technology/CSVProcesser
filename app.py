from flask import Flask, request, jsonify
from io import StringIO
from flask_cors import CORS
import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from celery import Celery
from selenium.common.exceptions import SessionNotCreatedException, WebDriverException

app = Flask(__name__)
CORS(app)


app.config.update(
    CELERY_BROKER_URL='redis://localhost:6379/0',
    CELERY_RESULT_BACKEND='redis://localhost:6379/0'
)

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

GOOGLE_CHROME_BIN = os.environ.get("GOOGLE_CHROME_SHIM", None)
CHROMEDRIVER_PATH = os.environ.get("CHROMEDRIVER_PATH", "/chromedriver")


def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)
    return celery

app.config.update(
    CELERY_BROKER_URL='redis://localhost:6379/0',
    CELERY_RESULT_BACKEND='redis://localhost:6379/0'
)
celery = make_celery(app)

def get_domain_from_google(company_name, street_address, state):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    GOOGLE_CHROME_BIN = os.environ.get("GOOGLE_CHROME_SHIM", None)

    if GOOGLE_CHROME_BIN:
        chrome_options.binary_location = GOOGLE_CHROME_BIN

    driver = webdriver.Chrome(options=chrome_options)
    query = f"{company_name} official website based in {state} with {street_address}"
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


@app.route('/', methods=['GET'])
def hello_world():
    return jsonify("hello world")

@app.route('/process_csv', methods=['POST'])
def process_csv():
    data = request.json
    orgs = data.get("orgs", [])
    task_ids = []
    for org in orgs:
        task = get_domain_from_google.apply_async(
            args=[org['Company Name'], org['Street Address'], org['State']])
        task_ids.append(str(task.id))
    return jsonify({"status": "Tasks started", "task_ids": task_ids}), 202

@app.route('/task_status/<task_id>', methods=['GET'])
def task_status(task_id):
    task = get_domain_from_google.AsyncResult(task_id)
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'status': 'Task is still running'
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'result': task.result
        }
    else:
        response = {
            'state': task.state,
            'status': str(task.info)
        }
    return jsonify(response)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Use port 5000 if PORT isn't set
    app.run(host='0.0.0.0', port=port)
