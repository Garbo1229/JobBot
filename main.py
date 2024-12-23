from scraper.job_scraper import JobScraper
from utils.search_code import search_code
from config.config import QUERY,CITY_NAME
if __name__ == "__main__":
    if CITY_NAME == "":
        search_name = input("请输入城市名称进行搜索: ").strip()
        site_code = search_code('site.json', search_name)
    else:
        site_code = search_code('site.json', CITY_NAME)

    if site_code == 0:
        site_code = 101280600  # 默认城市代码

    scraper = JobScraper(query=QUERY, site_code=site_code)
    scraper.scrape_jobs()