from pathlib import Path
from typing import Dict

import pandas as pd
from loguru import logger
from omegaconf import DictConfig
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

import hydra


@hydra.main(version_base=None, config_path="hydra", config_name="config")
def main(cfg: DictConfig):

    output_dir = Path.cwd() / "51job_output"
    output_dir.mkdir(exist_ok=True)

    datadir = Path(hydra.utils.get_original_cwd()) / cfg.datadir

    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(
        options=options, service=Service(ChromeDriverManager().install())
    )

    driver.get(cfg.url)
    logger.info(driver.title)

    try:
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, "j_joblist"))
        )

        jobs_container = driver.find_elements(By.CLASS_NAME, "j_joblist")

        if not jobs_container:
            logger.warning("No job is available.")

        jobs_container = jobs_container[0]

        driver.implicitly_wait(30)

        jobs = jobs_container.find_elements(By.CLASS_NAME, "sensors_exposure")
        logger.info(f"Number of jobs: {len(jobs)}")

        job_specs = []
        for job in jobs:
            job_obj = extract_job_info(job)
            job_specs.append(job_obj)

            logger.debug(job_obj)

    finally:
        driver.quit()

    df = pd.DataFrame(job_specs)
    df.to_csv(datadir / f"{cfg.keyword}.csv", index=False)

    logger.info("Job completed!")


def extract_job_info(job) -> Dict[str, str]:
    job_specs = {}

    job_specs["job_title"] = job.find_element(By.CLASS_NAME, "jname").text
    job_specs["companny_name"] = job.find_element(By.CLASS_NAME, "cname").text
    job_specs["post_date"] = job.find_element(By.CLASS_NAME, "time").text
    job_specs["salary"] = job.find_element(By.CLASS_NAME, "sal").text

    job_requirements = ""
    requirement_container = job.find_element(By.XPATH, "//span[@class='d at']")
    for requirement in requirement_container.find_elements(By.TAG_NAME, "span"):
        job_requirements += requirement.text

    job_specs["requirements"] = job_requirements

    job_tags = []
    tags_container = job.find_element(By.XPATH, "//p[@class='tags']")
    for tag in tags_container.find_elements(By.TAG_NAME, "span"):
        job_tags.append(tag.get_attribute("title"))

    job_specs["tags"] = "|".join(job_tags)

    size_container = job.find_element(By.XPATH, "//p[@class='dc at']")
    job_specs["firm_size"] = size_container.text

    industry_container = job.find_element(By.XPATH, "//p[@class='int at']")
    job_specs["industry"] = industry_container.text

    return job_specs


if __name__ == "__main__":
    main()
