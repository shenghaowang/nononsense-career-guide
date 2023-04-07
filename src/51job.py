from typing import Dict

from loguru import logger
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


def main(url):

    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(
        options=options, service=Service(ChromeDriverManager().install())
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
            logger.info("No job is available.")

        jobs_container = jobs_container[0]

        driver.implicitly_wait(30)

        jobs = jobs_container.find_elements(By.CLASS_NAME, "sensors_exposure")
        logger.info(f"Number of jobs: {len(jobs)}")

        for job in jobs:
            job_specs = extract_job_info(job)
            logger.debug(job_specs)

    finally:
        driver.quit()


def extract_job_info(job) -> Dict[str, str]:
    job_specs = {}

    jname = job.find_element(By.CLASS_NAME, "jname").text
    cname = job.find_element(By.CLASS_NAME, "cname").text
    time = job.find_element(By.CLASS_NAME, "time").text
    salary = job.find_element(By.CLASS_NAME, "sal").text
    # logger.debug(f"{jname} - {cname} - {time} - {salary}")
    job_specs["job_title"] = jname
    job_specs["companny_name"] = cname
    job_specs["post_date"] = time
    job_specs["salary"] = salary

    job_requirements = ""
    requirement_container = job.find_element(By.XPATH, "//span[@class='d at']")
    for requirement in requirement_container.find_elements(By.TAG_NAME, "span"):
        job_requirements += requirement.text

    # logger.debug(f"job requirement: {job_requirements}")
    job_specs["requirements"] = job_requirements

    job_tags = []
    tags_container = job.find_element(By.XPATH, "//p[@class='tags']")
    for tag in tags_container.find_elements(By.TAG_NAME, "span"):
        job_tags.append(tag.get_attribute("title"))

    # logger.debug(f"Tags: {'|'.join(job_tags)}")
    job_specs["tags"] = job_tags

    size_container = job.find_element(By.XPATH, "//p[@class='dc at']")
    firm_size = size_container.text
    # logger.debug(f"Firm size: {firm_size}")
    job_specs["firm_size"] = firm_size

    industry_container = job.find_element(By.XPATH, "//p[@class='int at']")
    industry = industry_container.text
    # logger.debug(f"industry: {industry}")
    job_specs["industry"] = industry

    return job_specs


if __name__ == "__main__":
    keyword = "化学工程师"
    url = f"https://we.51job.com/pc/search?keyword={keyword}&searchType=2&sortType=0&metro="  # noqa: E501

    # keyword = "python"
    # page_no = 1

    main(url)

    logger.info("Job completed!")
