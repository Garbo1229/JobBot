import json

def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


# 递归查找中文名称对应的code
def find_code_by_name(data, name):
    if isinstance(data, dict):
        # 如果当前节点是字典，首先检查名字
        if data.get('name') == name:
            return data.get('code')

        # 获取subLevelModelList并确保它是一个有效的列表
        sub_level_model_list = data.get('subLevelModelList')
        if sub_level_model_list:
            for sub_data in sub_level_model_list:
                result = find_code_by_name(sub_data, name)
                if result:
                    return result

    return None  # 如果没有找到，返回None


def search_code(file_path, name):
    data = load_json(file_path)
    # 遍历所有siteList，进行递归查找
    for site in data.get('zpData', {}).get('siteList', []):
        code = find_code_by_name(site, name)
        if code:

            return code
    print(f"未找到中文名称 '{name}' 对应的 code 将会默认设置成 深圳")
    return  0

