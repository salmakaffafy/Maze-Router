import time
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service



print (time.time())

s = Service('/usr/local/bin/chromedriver')

chromeOptions = Options()

driver = webdriver.Chrome(service=s, options=chromeOptions)

driver.get("https://www.lyngsat.com/")
time.sleep(6)

table = driver.find_element(By.XPATH,"/html/body/div/table/tbody/tr/td[2]/table[3]/tbody/tr/td[2]/table/tbody/tr/td/table[1]/tbody")
rows = table.find_elements(By.TAG_NAME, "tr")

with open("satellites_regionss.csv", "w", newline="") as csvfile:
    # Create a CSV writer object
    csv_writer = csv.writer(csvfile)

    # Iterate through each row and write data to CSV file
    for row in rows[0:]:
        columns = row.find_elements(By.TAG_NAME, "td")
        region = columns[0].text
        satellites = [link.text for link in columns[1:] if link.text]

        # Write the data to the CSV file
        csv_writer.writerow([region] + satellites)