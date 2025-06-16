# 🧾 HH Parser – Terminal-Based HeadHunter Vacancy Scraper

**HH Parser** is a command-line Python program that allows users to log into [hh.ru](https://hh.ru) using their email and password, solve a captcha, and download vacancy data into a `.csv` file.

## 📌 Features

- Login via email and password
- Captcha solving support
- Scrape specific vacancies from hh.ru
- Save parsed data into CSV format
- Terminal-based interface

## 🛠️ Requirements

- Python 3.8+
- Requests
- BeautifulSoup
- CSV
- [Optional] Selenium (if needed for captcha)

## 🚀 Installation

```bash
git clone https://github.com/your-username/hh-parser.git
cd hh-parser
pip install -r requirements.txt
````

## 📦 Usage

```bash
python main.py
```

The script will ask for:

* Your email
* Your password
* Captcha (if required)
* Keywords for the vacancy

After successful authentication, it will search and export results to `vacancies.csv`.

## 📄 Example Output

A sample `vacancies.csv` might look like:

| Title            | Company          | Location         | Salary    | Link                                                         |
| ---------------- | ---------------- | ---------------- | --------- | ------------------------------------------------------------ |
| Python Developer | XYZ Technologies | Moscow           | 150,000 ₽ | [https://hh.ru/vacancy/123456](https://hh.ru/vacancy/123456) |
| Data Analyst     | ABC Corp         | Saint-Petersburg | 100,000 ₽ | [https://hh.ru/vacancy/654321](https://hh.ru/vacancy/654321) |

## 🔐 Disclaimer

This project is for educational purposes only. Make sure to comply with HeadHunter’s [terms of service](https://hh.ru/article/terms) before scraping data.

## 🧑‍💻 Author

**Abdumuratov Maxmudjon**
GitHub: [@MahmudjonA](https://github.com/MahmudjonA)
