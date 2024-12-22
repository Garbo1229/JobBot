from scraper.job_scraper import JobScraper
from utils.search_code import search_code
from config.config import QUERY
if __name__ == "__main__":
    search_name = input("请输入中文名称进行搜索: ").strip()
    site_code = search_code('site.json', search_name)

    if site_code == 0:
        site_code = 101280600  # 默认城市代码

    scraper = JobScraper(query=QUERY, site_code=site_code)
    scraper.scrape_jobs()