from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time

chrome_driver_path = 'chromedriver.exe'
service = Service(chrome_driver_path)

driver = webdriver.Chrome(service=service)

course_explore_url = 'https://uwflow.com/explore'
driver.get(course_explore_url)

# Wait until courses have initially loaded
course_row_xpath = '//*[@id="root"]/div[4]/div/div[2]/div[1]/div/div/div[2]/div/div/div'
WebDriverWait(driver, timeout=5).until(EC.presence_of_element_located((By.XPATH, course_row_xpath)))

# The number of times we load more courses
course_batches = 12
for _ in range(course_batches):
    # Scroll to the bottom of the webpage to load more courses
    scroll_down_script = "window.scrollTo(0, document.body.scrollHeight);"
    driver.execute_script(scroll_down_script)

    # Wait 2 seconds for more courses to load
    time.sleep(2)

# Get all course elements
course_name_path = '//*[@id="root"]/div[4]/div/div[2]/div[1]/div/div/div[2]/div/div/div[2]/div/div[1]/a'
elements = driver.find_elements(By.XPATH, course_name_path)

courses = '\n'.join([element.text.replace(' ', '') for element in elements])
with open("courses.txt", "w") as f:
    f.write(courses)

driver.quit()