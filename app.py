from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import pandas as pd

def scrape_jobs(url,driver):

    # Load the webpage
    driver.get(url)
    
    # Wait for job listings to be loaded
    WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.CLASS_NAME, 'job-item')))
    
    # Extract the HTML content after the page has fully loaded
    soup = BeautifulSoup(driver.page_source, 'html.parser')
        
    jobs = []
    
    job_elements = soup.find_all('div', class_='job-item media')
    
    # Get page
    page_elem = soup.find('div', class_='pagination-box pb text-center').find('span', class_='page-link oferta-link active')
    page = page_elem.text.strip() if page_elem else "N/A"
    
    # Iterate over each job listing
    for job in job_elements:
    # Extract job details
        job_elem = job.find('a', class_='oferta-link')
        title = job_elem.text.strip() if job_elem else "N/A"
        
        company_elem = job.find('li', style="font-weight:bold")
        company = company_elem.text.strip() if company_elem else "N/A"
        
        i_elem = job.find('i', class_='flaticon-calendar')
        date_elem = i_elem.find_parent('li') if i_elem else None
        date = date_elem.text.strip() if date_elem else "N/A"

    # Append job details to the list of jobs
        jobs.append({
            "Job Title": title,
            "Company": company,
            "Date": date,
            "Page": page
        })
    
    return jobs

def save_to_excel(jobs, filename='jobs.xlsx'):
    df = pd.DataFrame(jobs)
    df.to_excel(filename, index=False)
    
def main():
    # Configure Selenium WebDriver
    service = Service(executable_path=r'C:\Users\GMC4L\Downloads\chromedriver-win64\chromedriver.exe')
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run browser in headless mode (without opening GUI)
    driver = webdriver.Chrome(service=service, options=options)
    
    search_url = 'https://www.net-empregos.com/pesquisa-empregos.asp?page=1&categoria=5&zona=1&tipo=0'
    all_jobs = []
    previous_url = None

    while True:
        jobs = scrape_jobs(search_url, driver)
        
        # Extend the list of all jobs with jobs from the current page
        all_jobs.extend(jobs)

        # Save all jobs to Excel
        save_to_excel(all_jobs, filename='jobs.xlsx')

        # Use Selenium to find the next page URL
        try:
            next_page_elems = driver.find_elements(By.CSS_SELECTOR, 'a.page-link.oferta-link.d-none.d-lg-block')
            
            # Choose the appropriate element for the next page link
            if len(next_page_elems) >= 2:
                next_page_elem = next_page_elems[1]  # Select the second element
            else:
                next_page_elem = next_page_elems[0] if next_page_elems else None
                
            if next_page_elem:
                next_url = next_page_elem.get_attribute('href')
                if next_url != previous_url:  # Check if the next URL is different from the previous URL
                    previous_url = search_url  # Update the previous URL
                    search_url = next_url  # Update search URL for next page
                else:
                    break  # Break out of the loop if the next URL is the same as the previous URL
            else:
                break  # Exit the loop if there are no more pages
        except NoSuchElementException:
            break
    
    # Close the WebDriver
    driver.quit()
    
if __name__ == '__main__':
    main()
