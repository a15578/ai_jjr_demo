import json
from langchain.agents import tool
from langchain.pydantic_v1 import Field


@tool
def save_basic_info(user_info:dict = Field(description="包含用户个人信息的dict格式数据,"
                                                       "eg: {'user_info':{'用户姓名':'张三','基本信息': {...},'深度信息': {...},'信息汇总': {...}}}")):
    "该函数用于保存用户的个人信息"

    if user_info:
        # 确保用户信息字典中包含 '用户姓名' 字段
        if '用户姓名' not in user_info:
            return "用户信息必须包含 '用户姓名' 字段。"

        # 尝试加载现有的用户信息，如果文件不存在则创建一个新字典
        try:
            with open("users_info.json", "r", encoding="utf-8") as f:
                users_info = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            users_info = {}

        # 添加或更新用户信息
        users_info[user_info['用户姓名']] = user_info

        # 将用户信息保存到 'user_info.json' 文件
        with open("users_info.json", "w", encoding="utf-8") as f:
            json.dump(users_info, f, ensure_ascii=False, indent=4)

        return "用户基本信息保存成功"
    else:
        return "没有用户基本信息，不需要保存"


@tool
def is_basic_info_enough(user_name:str = Field(description="用户的姓名,"
                                                           "eg:{'user_name':'张三'}")):
    "该函数用于检查用户信息是否足够"

    try:
        with open("users_info.json", "r", encoding="utf-8") as f:
            users_info = json.load(f)

        user_info = users_info.get(user_name)

        if user_info is None:
            return f"未找到用户名为 {user_name} 的用户信息。"

        # 检查基本信息的每个值是否都不是 "none"
        for value in user_info.get('基本信息', {}).values():
            if value == "none":
                return "基本信息不够"

        # 如果需要，可以在这里添加对深度信息的检查
        # for value in user_info.get('深度信息', {}).values():
        #     if value == "none":
        #         return "深度信息不够"

        return "信息足够"

    except FileNotFoundError:
        return "用户信息文件未找到。"
    except json.JSONDecodeError:
        return "用户信息文件格式错误。"







