import requests
import re
import json
import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from loguru import logger


def main(url):
    
    driver_file = "../chromedriver_mac64/chromedriver"
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(
        options=options,
        service=Service(ChromeDriverManager().install())
    )
    
    # url = "https://shenghaowang.github.io/"
    driver.get(url)
    logger.info(driver.title)
    try:
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, "j_joblist"))
        )
        
        jobs_container = driver.find_elements(By.CLASS_NAME, "j_joblist")
        
        if not jobs_container:
            logger.info(f"No job is available.")
        
        jobs_container = jobs_container[0]
        
        driver.implicitly_wait(30)
        
        jobs = jobs_container.find_elements(By.CLASS_NAME, "sensors_exposure")
        logger.info(f"Number of jobs: {len(jobs)}")
        
        for job in jobs:
            extract_job_info(job)
        
    finally:
        driver.quit()


def extract_job_info(job):
    jname = job.find_element(By.CLASS_NAME, "jname").text
    cname = job.find_element(By.CLASS_NAME, "cname").text
    time = job.find_element(By.CLASS_NAME, "time").text
    salary = job.find_element(By.CLASS_NAME, "sal").text
    # location_container = job.find_element(By.CLASS_NAME, "at")
    
    # full_location = ""
    # for loc in location_container.find_elements(By.TAG_NAME, "span"):
    #     full_location += loc.text
    
    logger.debug(f"{jname} - {cname} - {time} - {salary}")


if __name__ == '__main__':
    url = 'https://we.51job.com/pc/search?keyword=化学工程师&searchType=2&sortType=0&metro='

    # keyword = "化学工程师"
    keyword = "python"
    page_no = 1
    
    main(url)

    logger.info("Job completed!")