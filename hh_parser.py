from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
from PIL import Image, ImageEnhance
import io
import requests
import pandas as pd
import re
from urllib.parse import quote

def get_driver():
    options = Options()
    # options.add_argument("--headless=new")  # Run in headless mode
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--enable-unsafe-swiftshader")
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-features=VideoCapture")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")
    options.add_argument("--lang=en-US")
    options.add_argument("--window-size=1920,1080")  # Set window size to avoid rendering issues
    options.add_argument("--disable-blink-features=AutomationControlled")  # Avoid detection
    return webdriver.Chrome(options=options)

def solve_captcha(driver):
    try:
        # Click English language button if available
        try:
            print("Checking for English language button...")
            english_button = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@data-qa='captcha-language']"))
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", english_button)
            english_button.click()
            time.sleep(1)
            print("Clicked English language button.")
        except Exception as e:
            print(f"English button not found or clickable: {e}")
            try:
                english_button = driver.find_element(By.XPATH, "//button[@data-qa='captcha-language']")
                driver.execute_script("arguments[0].click();", english_button)
                time.sleep(1)
                print("Clicked English button using JavaScript.")
            except Exception as e2:
                print(f"JavaScript click failed: {e2}")
                print("Proceeding with default CAPTCHA (possibly Russian).")

        # Get CAPTCHA image
        print("Fetching CAPTCHA image...")
        captcha_img = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//img[@data-qa='account-captcha-picture']"))
        )
        captcha_src = captcha_img.get_attribute("src")
        print(f"CAPTCHA found with src: {captcha_src}")

        # Save CAPTCHA source
        with open("captcha_src.txt", "w", encoding="utf-8") as f:
            f.write(captcha_src or "No src found")
        print("CAPTCHA src saved as 'captcha_src.txt'.")

        # Download CAPTCHA image
        cookies = {c['name']: c['value'] for c in driver.get_cookies()}
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            "Referer": "https://hh.uz/account/login",
            "Accept": "image/png,image/jpeg,image/*,*/*;q=0.8"
        }
        response = requests.get(captcha_src, cookies=cookies, headers=headers, timeout=10)
        response.raise_for_status()
        print(f"CAPTCHA URL fetch status: {response.status_code}")
        image_data = response.content

        # Save and open raw image with minimal preprocessing
        raw_img = Image.open(io.BytesIO(image_data))
        img = ImageEnhance.Contrast(raw_img).enhance(1.5)
        img.save("captcha_image_raw.png")
        print("Raw CAPTCHA image saved as 'captcha_image_raw.png'.")
        # img.show()
        # print("Raw CAPTCHA image opened.")

        # Prompt for manual input with retries
        attempts = 0
        max_attempts = 3
        while attempts < max_attempts:
            captcha_text = input(f"Enter the CAPTCHA text (e.g., 'CREATE' or 'jota nonshatter') from 'captcha_image_raw.png' (max 20 characters, attempt {attempts+1}/{max_attempts}): ").strip()
            if len(captcha_text) > 20:
                print("Input too long! Please enter a CAPTCHA text (max 20 characters).")
                attempts += 1
                continue
            if len(captcha_text) < 4:
                print("Input too short! Please enter a CAPTCHA text (at least 4 characters).")
                attempts += 1
                continue
            if not re.match(r'^[A-Z0-9 ]+$', captcha_text.upper()):
                print("Invalid input! Use only letters, numbers, and spaces.")
                attempts += 1
                continue
            break
        if attempts >= max_attempts:
            print("Max CAPTCHA attempts reached. Exiting.")
            return None
        captcha_text = re.sub(r'[^A-Z0-9 ]', '', captcha_text.upper())
        print(f"Manually entered CAPTCHA text: {captcha_text}")

        return captcha_text

    except Exception as e:
        print(f"CAPTCHA solving error: {str(e)}")
        driver.save_screenshot("captcha_error.png")
        print("Saved screenshot as 'captcha_error.png'.")
        return None

def scrape_jobs(driver, query, salary_from, experience, employment, schedule, max_pages=2):
    jobs_data = []
    params = {
        "text": query,
        "area": "2759",  # Tashkent
        "hhtmFrom": "main"
    }
    if salary_from:
        params["salary"] = salary_from
    if experience:
        params["experience"] = experience
    if employment:
        params["employment"] = employment
    if schedule:
        params["schedule"] = schedule

    search_url = f"https://hh.uz/search/vacancy?{'&'.join(f'{k}={quote(str(v))}' for k, v in params.items())}"
    try:
        print(f"Navigating to job search page for '{query}' in Tashkent...")
        driver.get(search_url)
        time.sleep(2)  # Wait for initial load

        for page in range(max_pages):
            print(f"Scraping page {page + 1}...")
            try:
                WebDriverWait(driver, 15).until(
                    EC.presence_of_all_elements_located((By.XPATH, "//div[@data-qa='vacancy-serp__vacancy' and .//a[@data-qa='serp-item__title']]"))
                )
                job_cards = driver.find_elements(By.XPATH, "//div[@data-qa='vacancy-serp__vacancy' and .//a[@data-qa='serp-item__title']]")

                if not job_cards:
                    print("No job cards found on this page.")
                    break

                for job in job_cards:
                    job_info = {}
                    try:
                        # Job Title
                        try:
                            title_elem = job.find_element(By.XPATH, ".//a[@data-qa='serp-item__title']")
                            job_info["Job Title"] = title_elem.text.strip()
                            job_info["Link"] = title_elem.get_attribute("href").replace("hh.ru", "hh.uz")
                        except:
                            print("Job Title not found.")
                            continue  # Skip invalid job card

                        # Company
                        try:
                            company_elem = job.find_element(By.XPATH, ".//span[@data-qa='vacancy-serp__vacancy-employer-text'] | .//a[@data-qa='vacancy-serp__vacancy-employer']")
                            job_info["Company"] = company_elem.text.strip()
                        except:
                            print(f"Company not found for {job_info.get('Job Title', 'unknown')}.")
                            job_info["Company"] = "N/A"

                        # Experience
                        try:
                            experience_elem = job.find_element(By.XPATH, ".//span[contains(@data-qa, 'vacancy-serp__vacancy-work-experience')] | .//div[contains(@data-qa, 'vacancy-experience')]")
                            job_info["Experience"] = experience_elem.text.strip()
                        except:
                            print(f"Experience not found for {job_info.get('Job Title', 'unknown')}.")
                            job_info["Experience"] = "N/A"

                        # # Employment Type
                        # try:
                        #     employment_elem = job.find_element(By.XPATH, ".//p[@data-qa='common-employment-text'] | .//div[contains(@data-qa, 'vacancy-serp__vacancy-compensation')]//p")
                        #     job_info["Employment Type"] = employment_elem.text.strip()
                        # except:
                        #     print(f"⚠️ Employment Type not found for {job_info.get('Job Title', 'unknown')}.")
                        #     job_info["Employment Type"] = "N/A"

                        # # Schedule
                        # try:
                        #     schedule_elem = job.find_element(By.XPATH, ".//p[@data-qa='work-schedule-by-days-text'] | .//div[contains(@data-qa, 'vacancy-serp__vacancy-compensation')]//p[contains(text(), 'График')]")
                        #     job_info["Schedule"] = schedule_elem.text.replace("График: ", "").strip()
                        # except:
                        #     print(f"⚠️ Schedule not found for {job_info.get('Job Title', 'unknown')}.")
                        #     job_info["Schedule"] = "N/A"

                        # # Work Format
                        # try:
                        #     work_format_elem = job.find_element(By.XPATH, ".//p[@data-qa='work-formats-text'] | .//div[contains(@data-qa, 'vacancy-serp__vacancy-compensation')]//p[contains(text(), 'Формат')]")
                        #     job_info["Work Format"] = work_format_elem.text.replace("Формат работы: ", "").strip()
                        # except:
                        #     print(f"⚠️ Work Format not found for {job_info.get('Job Title', 'unknown')}.")
                        #     job_info["Work Format"] = "N/A"

                        # Email and Phone from Contacts
                        try:
                            if job_info["Link"] != "N/A":
                                driver.execute_script("window.open();")
                                driver.switch_to.window(driver.window_handles[-1])
                                driver.get(job_info["Link"])
                                WebDriverWait(driver, 15).until(
                                    EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'vacancy-description')]"))
                                )

                                # Check for Contacts button
                                contacts_buttons = driver.find_elements(By.XPATH, "//button[@data-qa='show-employer-contacts show-employer-contacts_top-button']")
                                if contacts_buttons:
                                    print(f"Contacts button found for {job_info.get('Job Title', 'unknown')}.")
                                    driver.execute_script("arguments[0].click();", contacts_buttons[0])
                                    time.sleep(1)  # Wait for drop-down
                                    contacts_elem = WebDriverWait(driver, 10).until(
                                        EC.presence_of_element_located((By.XPATH, "//div[@data-qa='vacancy-contacts__drop']"))
                                    )
                                    contacts = contacts_elem.text
                                    # Extract email
                                    email_pattern = r'[\w\.-]+@[\w\.-]+'
                                    emails = re.findall(email_pattern, contacts)
                                    job_info["Email"] = emails[0] if emails else "N/A"
                                    # Extract phone
                                    phone_pattern = r'(\+998|8)[\s-]?(\d{2})[\s-]?(\d{3})[\s-]?(\d{2})[\s-]?(\d{2})'
                                    phones = re.findall(phone_pattern, contacts)
                                    job_info["Phone"] = ";".join("".join(phone) for phone in phones) if phones else "N/A"
                                else:
                                    print(f"Contacts button not found for {job_info.get('Job Title', 'unknown')}.")
                                    job_info["Email"] = "N/A"
                                    job_info["Phone"] = "N/A"

                                driver.close()
                                driver.switch_to.window(driver.window_handles[0])
                            else:
                                job_info["Email"] = "N/A"
                                job_info["Phone"] = "N/A"
                        except Exception as e:
                            print(f"Failed to scrape contacts for {job_info.get('Job Title', 'unknown')}: {e}")
                            job_info["Email"] = "N/A"
                            job_info["Phone"] = "N/A"

                        jobs_data.append(job_info)
                    except Exception as e:
                        print(f"Error processing job card: {str(e)}")
                        continue

                # Navigate to next page
                try:
                    next_button = driver.find_element(By.XPATH, "//a[@data-qa='pager-next']")
                    driver.execute_script("arguments[0].click();", next_button)
                    time.sleep(2)
                except:
                    print("No more pages to scrape.")
                    break

            except Exception as e:
                print(f"Error loading page {page + 1}: {e}")
                break

        # Save to CSV with dynamic filename based on query
        if jobs_data:
            # Sanitize query for valid filename
            sanitized_query = re.sub(r'[<>:"/\\|?*]', '_', query.strip())
            csv_filename = f"{sanitized_query}.csv"
            df = pd.DataFrame(jobs_data)
            df.to_csv(csv_filename, index=False, encoding='utf-8')
            print(f"\nFound {len(jobs_data)} job(s). Results saved to {csv_filename}")
            print("Top 5 job listings:")
            for job in jobs_data[:5]:
                print([job.get(field, "N/A") for field in ["Job Title", "Link", "Company", "Experience", "Email", "Phone"]])
        else:
            print("\nNo jobs found.")

    except Exception as e:
        print(f"Error during scraping: {str(e)}")
        driver.save_screenshot("scrape_error.png")
        print("Saved screenshot as 'scrape_error.png'.")

    return jobs_data

def login_to_hh(email, password, query, salary_from, experience, employment, schedule):
    driver = get_driver()
    
    try:
        print("Navigating to login page...")
        driver.get("https://hh.uz/account/login?role=applicant&backurl=%2F&hhtmFrom=main")

        # Login flow
        print("Looking for 'Войти' button...")
        WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@data-qa='submit-button' and contains(., 'Войти')]"))
        ).click()

        print("Selecting email login...")
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//input[@data-qa='credential-type-EMAIL']"))
        )
        driver.find_element(By.XPATH, "//label[contains(., 'Почта')]").click()

        print("Entering email...")
        email_field = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//input[@data-qa='applicant-login-input-email']"))
        )
        email_field.clear()
        email_field.send_keys(email)

        print("Switching to password login...")
        WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@data-qa='expand-login-by-password']"))
        ).click()

        print("Entering password...")
        password_field = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//input[@data-qa='applicant-login-input-password']"))
        )
        password_field.clear()
        password_field.send_keys(password)

        print("Submitting login...")
        WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@type='submit' and @data-qa='submit-button']"))
        ).click()

        # CAPTCHA handling
        captcha_text = solve_captcha(driver)
        if captcha_text:
            print("Entering CAPTCHA...")
            try:
                captcha_input = WebDriverWait(driver, 15).until(
                    EC.element_to_be_clickable((By.XPATH, "//input[@data-qa='account-captcha-input']"))
                )
                captcha_input.clear()
                for char in captcha_text:
                    captcha_input.send_keys(char)
                    time.sleep(0.1)
                
                print("Submitting CAPTCHA...")
                WebDriverWait(driver, 15).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[@type='submit' and @data-qa='submit-button']"))
                ).click()
                driver.save_screenshot("captcha_submitted.png")
                print("Saved screenshot as 'captcha_submitted.png'.")
            except Exception as e:
                print(f"Failed to enter/submit CAPTCHA: {e}")
                driver.save_screenshot("captcha_submit_error.png")
                print("Saved screenshot as 'captcha_submit_error.png'.")
                return

        # Verify login with fallback
        try:
            WebDriverWait(driver, 20).until(
                EC.any_of(
                    EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/applicant/resumes')]")),
                    EC.url_contains("/applicant")
                )
            )
            print("Login successful!")
            # Scrape jobs after login
            scrape_jobs(driver, query, salary_from, experience, employment, schedule)
        except:
            print("Login verification failed")
            driver.save_screenshot("login_failed.png")
            print("Saved screenshot as 'login_failed.png'.")

    except Exception as e:
        print(f"Error during login: {str(e)}")
        driver.save_screenshot("error.png")
        print("Saved screenshot as 'error.png'.")
    finally:
        print("Closing browser...")
        driver.quit()

if __name__ == "__main__":
    # Prompt for email with basic validation
    while True:
        email = input("Enter your email: ").strip()
        if re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            break
        print("Invalid email format! Please enter a valid email (e.g., user@example.com).")
    
    password = os.getenv("HH_PASSWORD") or input("Enter your password: ")
    query = input("Enter job type: ").strip()
    salary_from = input("Enter minimum salary (e.g., 7799800) or press Enter to skip: ").strip()
    salary_from = int(salary_from) if salary_from else None
    print("\nExperience: [1] No experience, [2] 1-3 years, [3] 3-6 years, [4] 6+ years")
    exp_input = input("Choose: ").strip()
    experience_map = {"1": "noExperience", "2": "between1And3", "3": "between3And6", "4": "moreThan6"}
    experience = experience_map.get(exp_input)
    print("\nEmployment type: [1] Full-time, [2] Part-time, [3] Project, [4] Volunteering, [5] Internship")
    emp_input = input("Choose: ").strip()
    employment_map = {"1": "full", "2": "part", "3": "project", "4": "volunteer", "5": "probation"}
    employment = employment_map.get(emp_input)
    print("\nSchedule: [1] Full day, [2] Shift, [3] Flexible, [4] Remote, [5] Rotational")
    sch_input = input("Choose: ").strip()
    schedule_map = {"1": "fullDay", "2": "shift", "3": "flexible", "4": "remote", "5": "flyInFlyOut"}
    schedule = schedule_map.get(sch_input)
    login_to_hh(email, password, query, salary_from, experience, employment, schedule)