from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime

# get_seconds_from_midnight(t) -> int takes in a str representing the time
#     and outputs the amount of time since midnight in seconds
def get_seconds_from_midnight(t):
    dt = datetime.strptime(t, '%I:%M %p')
    midnight = dt.replace(hour=0, minute=0, second=0, microsecond=0)
    time_difference = dt - midnight
    return int(time_difference.total_seconds() / 60)
    
class ScheduleScraper:

    class_row_path = '//*[@id="root"]/div[4]/div[2]/div[1]/div[1]/div[2]/div/div/div/div/div[2]/div/div/div[2]/div'
    
    def __init__(self):
        chrome_driver_path = 'chromedriver.exe'
        service = Service(chrome_driver_path)

        self.driver = webdriver.Chrome(service=service)
        self.url_prefix = 'https://uwflow.com/course/'

    def handle_course(self, course):
        course_url = self.url_prefix + course[:-1]
        self.driver.get(course_url)

        classes_have_loaded = EC.presence_of_element_located((By.XPATH, ScheduleScraper.class_row_path))
        try:
            WebDriverWait(self.driver, timeout=5).until(classes_have_loaded)
        except:
            print("Problem with ", course[:-1])
            return None

        rows = self.driver.find_elements(By.XPATH, ScheduleScraper.class_row_path)
        result = {}
        seen = set()
        for row in rows:
            class_type_elem = None
            class_time_elem = None
            class_days_elem = None
            try:
                class_type_elem = row.find_element(By.XPATH, './div[1]/div/div[2]')
                class_time_elem = row.find_element(By.XPATH, './div[4]/div/div[1]')
                class_days_elem = row.find_element(By.XPATH, './div[5]/div/div[1]')
            except:
                continue
            
            class_type = class_type_elem.text.split()[0]

            start, end = class_time_elem.text.split(' - ')
            class_time = [get_seconds_from_midnight(start), get_seconds_from_midnight(end)]

            days = class_days_elem.find_elements(By.TAG_NAME, 'span')
            class_days = [span.text for span in days if span.value_of_css_property('font-weight') == '700']
            if (class_type, (start, end), tuple(class_days)) in seen:
                continue

            seen.add((class_type, (start, end), tuple(class_days)))
            if class_type == 'TST':
                continue
            if len(class_days) == 0:
                continue

            time_obj = {'time': class_time, 'days': class_days}
            if not class_type in result:
                result[class_type] = []
            result[class_type].append(time_obj)

        return result
    
    def run(self):
        all_data = {}
        with open('courses.txt', 'r') as f:
            courses = f.readlines()
            for course in courses:
                info = self.handle_course(course)
                if info == None:
                    continue
                all_data[course[:-1]] = info
                
        with open("info2.json", "w") as f:
            f.write(str(all_data).replace("'", "\""))

    def quit(self):
        self.driver.quit()

if __name__ == '__main__':
    scraper = ScheduleScraper()
    scraper.run()
    scraper.quit()