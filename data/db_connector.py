import mysql.connector
from mysql.connector import Error
from config.config import DB_CONFIG

def connect_to_db():
    """建立数据库连接"""
    try:
        connection = mysql.connector.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['database']
        )
        return connection
    except Error as e:
        print(f"连接数据库失败: {e}")
        return None

def insert_or_update_job_data(job_data):
    """插入或更新职位数据"""
    db_connection = connect_to_db()
    if db_connection is None:
        print("无法连接到数据库，跳过数据插入操作")
        return

    cursor = db_connection.cursor()

    try:
        # 检查职位是否已存在
        check_query = "SELECT COUNT(*) FROM jobs WHERE job_detail_url = %s"
        cursor.execute(check_query, (job_data['job_detail_url'],))
        result = cursor.fetchone()

        if result[0] > 0:
            # 如果数据已存在，更新数据
            update_query = """
            UPDATE jobs
            SET job_name = %s, job_area = %s, job_salary = %s, job_company = %s, job_info_desc = %s, 
                job_detail = %s, job_degree = %s, job_experience = %s
            WHERE job_detail_url = %s
            """
            cursor.execute(update_query, (
                job_data["job_name"] or '',
                job_data["job_area"] or '',
                job_data["job_salary"] or '',
                job_data["job_company"] or '',
                job_data["job_info_desc"] or '',
                job_data["job_detail"] or '',
                job_data["job_degree"] or '',
                job_data["job_experience"] or '',
                job_data["job_detail_url"]
            ))
            print(f"职位 {job_data['job_detail_url']} 已更新")
        else:
            # 如果数据不存在，进行插入
            insert_query = """
            INSERT INTO jobs (job_name, job_area, job_salary, job_company, job_info_desc, job_detail_url, 
                              job_detail, job_degree, job_experience)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (
                job_data["job_name"] or '',
                job_data["job_area"] or '',
                job_data["job_salary"] or '',
                job_data["job_company"] or '',
                job_data["job_info_desc"] or '',
                job_data["job_detail_url"],
                job_data["job_detail"] or '',
                job_data["job_degree"] or '',
                job_data["job_experience"] or ''
            ))
            print(f"职位 {job_data['job_detail_url']} 已插入")

        # 提交事务
        db_connection.commit()

    except Error as e:
        db_connection.rollback()  # 发生错误时回滚事务
        print(f"数据库操作失败: {e}")

    finally:
        cursor.close()
        db_connection.close()

def check_job_exists(job_detail_url):
    """检查职位是否已存在"""
    db_connection = connect_to_db()
    if db_connection is None:
        return False

    cursor = db_connection.cursor()
    query = "SELECT COUNT(*) FROM jobs WHERE job_detail_url = %s"
    cursor.execute(query, (job_detail_url,))
    result = cursor.fetchone()

    cursor.close()
    db_connection.close()

    return result[0] > 0

def update_job_details(job_detail_url, job_detail, job_degree, job_experience):
    """更新职位的详细信息"""
    db_connection = connect_to_db()
    if db_connection is None:
        print("无法连接到数据库，跳过数据更新操作")
        return

    cursor = db_connection.cursor()

    try:
        # 执行更新操作
        update_query = """
        UPDATE jobs
        SET job_detail = %s, job_degree = %s, job_experience = %s
        WHERE job_detail_url = %s
        """
        cursor.execute(update_query, (
            job_detail or '',
            job_degree or '',
            job_experience or '',
            job_detail_url
        ))
        print(f"职位 {job_detail_url} 的详细信息已更新")

        # 提交事务
        db_connection.commit()

    except Error as e:
        db_connection.rollback()  # 发生错误时回滚事务
        print(f"更新职位详情失败: {e}")

    finally:
        cursor.close()
        db_connection.close()
