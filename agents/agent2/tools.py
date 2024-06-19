import json
from langchain.agents import tool
from langchain.pydantic_v1 import Field

@tool
def query_user_basic_info(user_name = Field(description="用户的姓名")):

    "该函数可根据用户名查询用户基本信息。"

    try:
        with open("users_info.json", "r", encoding="utf-8") as f:
            # 加载用户信息字典
            users_info = json.load(f)

        # 检查用户名是否存在并返回用户信息
        return users_info.get(user_name, f"未找到用户名为 {user_name} 的用户信息。")

    except FileNotFoundError:
        return "用户信息文件未找到。"
    except json.JSONDecodeError:
        return "用户信息文件格式错误。"






