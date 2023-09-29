import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import SessionNotCreatedException, WebDriverException


# Initialize the Chrome driver
driver = webdriver.Chrome()

# Navigate to Google
driver.get("https://www.google.com/search?q=test")

try:
    # Find all elements that match the 'cite' tag
    elements = driver.find_elements(By.CSS_SELECTOR, 'cite')
    # Print the number of elements found
    print(f"Found {len(elements)} 'cite' elements.")

    # Print the outer HTML of each element
    for i, element in enumerate(elements):
        print(f"Element {i + 1}: {element.get_attribute('outerHTML')}")

except Exception as e:
    print("An exception occurred:", e)

finally:
    # Quit the driver
    driver.quit()
