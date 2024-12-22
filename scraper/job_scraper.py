import time
import random
import re
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config.config import USER_AGENT, BASE_URL, MAX_PAGES,SLEEP_MIN_TIMA,SLEEP_MAX_TIMA,GET_DETAIL
from data.db_connector import insert_or_update_job_data, update_job_details, connect_to_db
from datetime import datetime

class JobScraper:
    def __init__(self, query, site_code, should_update_details=True):
        self.query = query
        self.site_code = site_code
        self.page = 1
        self.browser = None
        self.data = []
        self.should_update_details = should_update_details  # 是否更新职位详情
        self.db_connection = connect_to_db()  # 检查数据库连接
        # 获取当前时间并格式化为字符串
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        # 文件名包含时间戳和查询关键词
        self.file_name = f"职位数据_{self.query}_{current_time}.xlsx"

    def start_browser(self):
        option = webdriver.ChromeOptions()
        option.add_argument(f"user-agent={USER_AGENT}")
        option.add_argument("accept-language=en-US,en;q=0.9")
        option.add_experimental_option('detach', True)  # 保持浏览器打开
        self.browser = webdriver.Chrome(options=option)

    def stop_browser(self):
        if self.browser:
            self.browser.quit()

    def fetch_job_list(self):
        while self.page <= MAX_PAGES:
            self.browser.get(f"{BASE_URL}/web/geek/job?query={self.query}&city={self.site_code}&page={self.page}")
            job_name_elements = WebDriverWait(self.browser, 20).until(
                EC.presence_of_all_elements_located((By.XPATH, '//span[@class="job-name"]'))
            )
            job_area_elements = WebDriverWait(self.browser, 20).until(
                EC.presence_of_all_elements_located((By.XPATH, '//span[@class="job-area"]'))
            )
            job_salary_elements = WebDriverWait(self.browser, 20).until(
                EC.presence_of_all_elements_located((By.XPATH, '//span[@class="salary"]'))
            )
            job_company_elements = WebDriverWait(self.browser, 20).until(
                EC.presence_of_all_elements_located((By.XPATH, '//h3[@class="company-name"]/a'))
            )
            job_info_desc_elements = WebDriverWait(self.browser, 20).until(
                EC.presence_of_all_elements_located((By.XPATH, '//div[@class="info-desc"]'))
            )
            job_detail_href_elements = WebDriverWait(self.browser, 20).until(
                EC.presence_of_all_elements_located((By.XPATH, '//a[@class="job-card-left"]'))
            )

            # 遍历并打印职位数据
            for job_name, job_area, job_salary, job_company, job_info_desc, job_detail_href in zip(
                    job_name_elements, job_area_elements, job_salary_elements,
                    job_company_elements, job_info_desc_elements, job_detail_href_elements):
                job_data = {
                    'job_name': job_name.text if job_name else '无标题',
                    'job_area': job_area.text if job_area else '无地区',
                    'job_salary': job_salary.text if job_salary else '无薪资',
                    'job_company': job_company.text if job_company else '无公司',
                    'job_info_desc': job_info_desc.text if job_info_desc else '无描述',
                    'job_detail_url': job_detail_href.get_attribute("href") if job_detail_href else '无链接',
                    'job_detail': '',
                    'job_degree': '',
                    'job_experience': ''
                }
                self.data.append(job_data)

                # 插入或更新职位数据到数据库
                if self.db_connection:
                    insert_or_update_job_data(job_data)

            print(f"第{self.page}页完成")
            self.page += 1
            time.sleep(random.uniform(SLEEP_MIN_TIMA, SLEEP_MAX_TIMA))

        # 一次性导出Excel
        self.export_to_excel()

    def fetch_job_details(self):
        if not self.should_update_details:
            print("未设置更新详情，跳过更新")
            return

        for index, item in enumerate(self.data):
            print(f"准备更新第{index + 1}条职位数据")
            job_detail_url = item["job_detail_url"]
            self.browser.get(job_detail_url)

            # 获取职位详情的 HTML 元素
            try:
                job_desc_element = WebDriverWait(self.browser, 20).until(
                    EC.presence_of_element_located((By.XPATH, '//div[@class="job-sec-text"]'))
                )
            except:
                job_desc_element = None

            self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

            # 获取职位描述并清理 HTML 标签
            if job_desc_element:
                job_desc_html = job_desc_element.get_attribute('outerHTML')
                formatted_desc = job_desc_html.replace('<br>', '\n').replace('&nbsp;', '\n')
                cleaned_desc = re.sub(r'<.*?>', '', formatted_desc)
                # 更新 job_detail
                self.data[index]["job_detail"] = cleaned_desc

            # 获取工作经验
            try:
                job_experience_element = WebDriverWait(self.browser, 20).until(
                    EC.presence_of_element_located((By.XPATH, '//span[@class="text-desc text-experiece"]'))
                )
                job_experience_text = job_experience_element.text
            except:
                job_experience_text = ""

            # 获取学历要求
            try:
                job_degree_element = WebDriverWait(self.browser, 20).until(
                    EC.presence_of_element_located((By.XPATH, '//span[@class="text-desc text-degree"]'))
                )
                job_degree_text = job_degree_element.text
            except:
                job_degree_text = ""

            # 更新职位详情到数据中
            self.data[index]["job_degree"] = job_degree_text
            self.data[index]["job_experience"] = job_experience_text

            # 更新数据库中的职位详情
            if self.db_connection:
                update_job_details(item["job_detail_url"], cleaned_desc, job_degree_text, job_experience_text)

            # 更新 Excel 文件
            self.update_excel()

            time.sleep(random.uniform(SLEEP_MIN_TIMA, SLEEP_MAX_TIMA))
            self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    def export_to_excel(self):
        # 设置中文字段名
        columns = {
            'job_name': '职位名称',
            'job_area': '工作地点',
            'job_salary': '薪资',
            'job_company': '公司名称',
            'job_info_desc': '职位描述',
            'job_detail_url': '职位详情链接',
            'job_detail': '详细描述',
            'job_degree': '学历要求',
            'job_experience': '工作经验'
        }

        # 将数据转化为DataFrame并应用中文字段名
        df = pd.DataFrame(self.data)
        df.rename(columns=columns, inplace=True)

        # 将数据导出到Excel
        df.to_excel(self.file_name, index=False)
        print(f"职位列表已导出到 {self.file_name}")

    def update_excel(self):
        # 设置中文字段名
        columns = {
            'job_name': '职位名称',
            'job_area': '工作地点',
            'job_salary': '薪资',
            'job_company': '公司名称',
            'job_info_desc': '职位描述',
            'job_detail_url': '职位详情链接',
            'job_detail': '详细描述',
            'job_degree': '学历要求',
            'job_experience': '工作经验'
        }

        # 每次更新一条数据后保存Excel
        try:
            # 读取现有的Excel文件
            df = pd.read_excel(self.file_name)
        except FileNotFoundError:
            # 如果Excel文件不存在，则初始化一个新的DataFrame
            df = pd.DataFrame(self.data)

        # 确保只保留需要的列
        df = df[columns.values()]

        # 打印列名，确保列名正确
        print(f"当前Excel的列名: {df.columns}")

        # 显式将需要更新的列转换为字符串类型
        df["详细描述"] = df["详细描述"].astype(str)
        df["学历要求"] = df["学历要求"].astype(str)
        df["工作经验"] = df["工作经验"].astype(str)

        # 遍历每条数据并更新Excel
        for index, item in enumerate(self.data):
            job_url = item["job_detail_url"]

            # 查找已有的职位行，确保是用 job_detail_url 来匹配
            job_row_index = df[df["职位详情链接"] == job_url].index

            if not job_row_index.empty:
                # 如果找到已有行，直接替换
                row_index = job_row_index[0]
                df.loc[row_index, "职位名称"] = item["job_name"]
                df.loc[row_index, "工作地点"] = item["job_area"]
                df.loc[row_index, "薪资"] = item["job_salary"]
                df.loc[row_index, "公司名称"] = item["job_company"]
                df.loc[row_index, "职位描述"] = item["job_info_desc"]
                df.loc[row_index, "职位详情链接"] = item["job_detail_url"]
                df.loc[row_index, "详细描述"] = item["job_detail"]
                df.loc[row_index, "学历要求"] = item["job_degree"]
                df.loc[row_index, "工作经验"] = item["job_experience"]
            else:
                # 如果没有找到对应的职位，打印提示信息
                print(f"未找到职位 URL: {job_url}，跳过此条数据。")

        # 将数据转化为DataFrame并应用中文字段名
        df.rename(columns=columns, inplace=True)

        # 将更新后的DataFrame保存回Excel文件
        df.to_excel(self.file_name, index=False)
        print(f"职位详情已更新到 {self.file_name}")

    def scrape_jobs(self):
        self.start_browser()
        self.fetch_job_list()  # 先抓取职位列表
        if GET_DETAIL:
            self.fetch_job_details()  # 更新职位详情
        self.stop_browser()
