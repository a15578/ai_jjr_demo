import json
import manticoresearch
from langchain.agents import tool
from langchain.pydantic_v1 import Field

config = manticoresearch.Configuration(host="http://127.0.0.1:9312")
client = manticoresearch.ApiClient(config)
searchApi = manticoresearch.SearchApi(client)


@tool
def search_job(user_name: str = Field(description="用户的姓名")):

    "该函数根据用户的姓名对用户进行岗位匹配"

    with open("users_info.json", "r", encoding="utf-8") as f:
        users_info = json.load(f)

    user_info = users_info.get(user_name)

    if user_info is None:
        return f"未找到用户名为 {user_name} 的用户信息。"

    search_params = {
        "index": "job_desc",
        "query": {
            "bool": {
                "must": [{"match": {"degree_string": f"{user_info['基本信息']['学历']}"}},
                         {"match": {"job_msg": f"{user_info['深度信息']['技能掌握情况']}"}}],
                "should": [{"match": {"job_msg": f"{user_info['基本信息']['专业']}"}},
                           {"match": {"job_msg": f"{user_info['深度信息']['工作期望']}"}},
                           {"match": {"job_msg": f"{user_info['深度信息']['过往经历']}"}}]
            }
        },
        "size": 10
    }

    res = searchApi.search(search_params)
    print(res.hits)

    return "岗位匹配成功"