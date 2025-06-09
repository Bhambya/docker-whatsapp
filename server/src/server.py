from flask import Flask, request, jsonify
import time
from selenium import webdriver
import shutil
from whatsapp import WhatsApp
from threading import Lock
from functools import wraps
import logging

import selenium.common.exceptions
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException


app = Flask(__name__)
service = webdriver.ChromeService(executable_path=shutil.which("chromedriver"))

chrome_options = Options()
chrome_options.binary_location = shutil.which("chromium")
chrome_options.add_argument("--no-first-run")
chrome_options.add_argument("--user-data-dir=/config/whatsapp")

mutex = Lock()

LOGGER = logging.getLogger()
handler = logging.StreamHandler()
handler.setFormatter(
    logging.Formatter(
        "%(asctime)s - %(name)s -- [%(levelname)s] >> %(message)s"
    )
)
LOGGER.addHandler(handler)
LOGGER.setLevel(logging.INFO)


def locked(f):
    @wraps(f)
    def run_locked():
        with mutex:
            return f()
    return run_locked


@app.route('/api/login', methods=['POST'])
@locked
def login():
    browser = webdriver.Chrome(options=chrome_options, service=service)
    try:
        messenger = WhatsApp(LOGGER, browser=browser, time_out=30)
        browser.get(messenger.BASE_URL)
        WebDriverWait(browser, 120).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "[aria-label^='New chat']")
            )
        )

        return jsonify({'status': 'success'})
    except (NoSuchElementException, Exception) as e:
        return jsonify({'status': 'failed'}), 500
    finally:
        browser.quit()


@app.route('/api/dry_run_message', methods=['POST'])
@locked
def dry_run_message():
    data = request.get_json()

    # Validate input
    if not data or 'phone_number' not in data:
        return jsonify({'error': 'Missing required fields'}), 400

    phone_number = data['phone_number']

    browser = webdriver.Chrome(options=chrome_options, service=service)
    try:
        messenger = WhatsApp(LOGGER, browser=browser, time_out=30)

        messenger.find_user(phone_number)

        return jsonify({'status': 'success'})
    except (NoSuchElementException, Exception) as e:
        return jsonify({'status': 'failed'}), 500
    finally:
        browser.quit()


@app.route('/api/message', methods=['POST'])
@locked
def send_message():
    data = request.get_json()

    # Validate input
    if not data or 'phone_number' not in data or 'message' not in data:
        return jsonify({'error': 'Missing required fields'}), 400

    phone_number = data['phone_number']
    message = data['message']

    browser = webdriver.Chrome(options=chrome_options, service=service)
    try:
        messenger = WhatsApp(LOGGER, browser=browser, time_out=30)

        result = messenger.send_direct_message(phone_number, message)
        if result:
            time.sleep(2)
        else:
            return jsonify({'status': 'failed'}), 500

        return jsonify({'status': 'success'})
    finally:
        browser.quit()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
