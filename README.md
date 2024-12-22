# JobBot

这是一个用于爬取Boss直聘职位信息的 Python 项目。它通过 Selenium 自动抓取指定条件下的职位列表和详细信息，并将数据保存为 Excel 文件，同时支持数据库存取。

## 背景
- 课程：广州商学院爬虫课程
- 作业：期末作业——爬取招聘网站职位信息

## 功能

- **职位列表抓取**：根据关键词和城市筛选职位，抓取职位名称、地点、薪资、公司名称、职位描述等信息。
- **职位详情更新**：抓取每个职位的详细描述、学历要求和工作经验，并更新到现有的职位数据中。
- **数据存储**：抓取的数据会保存到 Excel 文件中，并支持后续更新。
- **数据库支持**：支持将抓取到的职位数据存储到数据库中，避免数据丢失。

## 项目结构

```plaintext
JobBot/  
│
├── scraper/                # 存放爬虫脚本
│   ├── job_scraper.py      # 爬虫核心逻辑
│
├── config/                 # 配置文件
│   └── config.py           # 配置文件，包含User Agent等参数
│
├── data/                   # 存放数据库操作脚本
│   └── db_connector.py     # 数据库连接与操作
│
├── utils/                  # 工具文件夹
│   └── utils.py            # 存放常用工具函数
│
├── .venv/                  # 虚拟环境目录
├── requirements.txt        # 项目依赖
└── main.py                 # 启动脚本
```

## 安装与使用
1. 克隆项目
    ```
    git clone https://github.com/Garbo1229/JobBot.git
    cd JobBot
   ```
2. 设置虚拟环境
    ``` 
   python3 -m venv .venv
   source .venv/bin/activate   # Linux/macOS
    .venv\Scripts\activate      # Windows
   ```
3. 安装依赖
    ```
   pip install -r requirements.txt
   ```
4. 配置
    在 `config/config.py` 中配置需要爬取的关键词、数据库配置等参数。
5. 启动爬虫
    运行 `python main.py` 命令启动爬虫，开始抓取数据

## 依赖
- Python 3.x
- Selenium
- Pandas
- openpyxl
- MySQL

## 注意
- 请求频率：为了避免 Boss 直聘限制访问，请避免过高频率的请求。
- 抓取频率：爬取时请合理控制请求频率，避免对服务器造成不必要的负担。