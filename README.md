# 🧾 HH Parser – Terminal-Based HeadHunter Vacancy Scraper

**HH Parser** is a command-line Python program designed to log into [hh.uz](https://hh.uz) (HeadHunter Uzbekistan) using user credentials, handle captchas, scrape job vacancy data based on user-specified criteria, and export the results to a `.csv` file.

## 📌 Features

- **User Authentication**: Log in to hh.uz using email and password.
- **Captcha Handling**: Support for solving captchas (manual input with image display).
- **Job Search Filtering**: Search vacancies by keywords, minimum salary, experience level, employment type, and work schedule.
- **Data Export**: Save scraped job data (e.g., job title, company, experience, email, phone, link) to a CSV file.
- **Terminal-Based Interface**: Fully operable via command-line inputs.

## 🛠️ Requirements

- **Python Version**: Python 3.8 or higher
- **Dependencies**:
  - `selenium` (for browser automation and captcha handling)
  - `requests` (for downloading captcha images)
  - `pandas` (for CSV data handling)
  - `Pillow` (for image processing)
  - `urllib.parse` (for URL encoding)
- **Browser Driver**: Chrome WebDriver compatible with the installed Chrome browser version.
- **Optional Tools**:
  - A stable internet connection to handle web requests and captchas.
  - Environment variable support for secure password storage (e.g., `HH_PASSWORD`).

## 🚀 Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/hh-parser.git
   cd hh-parser
   ```

2. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Ensure Chrome WebDriver is installed and added to your system PATH or the project directory. Download it from [chromedriver.chromium.org](https://chromedriver.chromium.org/downloads).

4. (Optional) Set up an environment variable for the password:
   ```bash
   export HH_PASSWORD="your_password"
   ```

## 📦 Usage

Run the script from the terminal:

```bash
python main.py
```

### Input Prompts

The script will prompt for the following inputs:
- **Email**: Your hh.uz account email (e.g., `user@example.com`).
- **Password**: Your hh.uz account password (or use the `HH_PASSWORD` environment variable).
- **Job Type**: Keywords for the job search (e.g., `Python Developer`).
- **Minimum Salary**: Optional minimum salary (e.g., `7799800` UZS, press Enter to skip).
- **Experience Level**: Choose from:
  - [1] No experience
  - [2] 1-3 years
  - [3] 3-6 years
  - [4] 6+ years
- **Employment Type**: Choose from:
  - [1] Full-time
  - [2] Part-time
  - [3] Project
  - [4] Volunteering
  - [5] Internship
- **Schedule**: Choose from:
  - [1] Full day
  - [2] Shift
  - [3] Flexible
  - [4] Remote
  - [5] Rotational
- **Captcha**: If a captcha appears, the script will save the captcha image as `captcha_image_raw.png` and prompt for manual input (e.g., `CREATE` or `jota nonshatter`).

### Process

1. The script logs into hh.uz using the provided credentials.
2. If a captcha is required, it downloads and displays the captcha image for manual solving.
3. After successful login, it searches for vacancies in Tashkent based on the provided filters.
4. It scrapes job details (title, company, experience, email, phone, link) from up to 2 pages (configurable).
5. Results are saved to a CSV file named after the sanitized job query (e.g., `Python_Developer.csv`).

## 📄 Example Output

A sample CSV file (e.g., `Python_Developer.csv`) might look like:

| Job Title         | Company          | Experience       | Email                | Phone              | Link                                      |
|-------------------|------------------|------------------|----------------------|--------------------|-------------------------------------------|
| Python Developer  | XYZ Technologies | 1-3 years        | hr@xyztech.com       | +998901234567      | https://hh.uz/vacancy/123456             |
| Data Analyst      | ABC Corp         | No experience    | N/A                  | N/A                | https://hh.uz/vacancy/654321             |

## 🔐 Disclaimer

This project is for **educational purposes only**. Ensure compliance with HeadHunter’s [terms of service](https://hh.uz/article/terms) when using this script. Unauthorized scraping may violate platform policies.

## 🧑‍💻 Author

**Abdumuratov Maxmudjon**  
GitHub: [@MahmudjonA](https://github.com/MahmudjonA)
