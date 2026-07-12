import os
import json
import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account

# 导入配置中心
# 注意：这需要确保您的项目在运行时能正确将根目录加入 PYTHONPATH
try:
    import config
except ImportError:
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    import config

def get_bigquery_client() -> bigquery.Client:
    """
    初始化并返回 BigQuery 客户端对象。
    优先解析 GitHub Actions 注入的 JSON 凭证字符串。
    """
    if config.GCP_CREDENTIALS_JSON_STR:
        try:
            # 将 JSON 字符串解析为字典
            credentials_info = json.loads(config.GCP_CREDENTIALS_JSON_STR)
            # 使用 service_account_info 直接生成认证对象
            credentials = service_account.Credentials.from_service_account_info(credentials_info)
            return bigquery.Client(project=config.GCP_PROJECT_ID, credentials=credentials)
        except Exception as e:
            raise RuntimeError(f"GCP 凭证解析失败，请检查 Secret 格式: {e}")
    else:
        # 如果没有环境变量中的 JSON，尝试使用默认环境变量（本地运行环境）
        return bigquery.Client(project=config.GCP_PROJECT_ID)

def query_table(query: str) -> pd.DataFrame:
    """
    执行 BigQuery 查询并返回 Pandas DataFrame。
    当前阶段实施严格的安全控制，仅允许 SELECT 操作。
    """
    # 1. 严格权限控制：强制拦截修改/删除操作
    forbidden_keywords = ['DELETE', 'UPDATE', 'INSERT', 'DROP', 'CREATE', 'ALTER', 'TRUNCATE', 'MERGE']
    query_upper = query.upper()
    
    # 简单的分词检查，防止关键词被直接调用
    for keyword in forbidden_keywords:
        if keyword in query_upper:
            raise PermissionError(
                f"🚨 安全拦截: 当前阶段系统处于严格只读模式。"
                f"禁止执行包含 '{keyword}' 的破坏性或写入型 SQL 语句。"
            )
            
    # 2. 必须以 SELECT 开头或包含 SELECT (基础校验)
    if 'SELECT' not in query_upper:
        raise ValueError("🚨 安全拦截: 无法识别读取指令，查询语句必须是合法的 SELECT 语句。")

    # 3. 初始化客户端并执行读取
    client = get_bigquery_client()
    query_job = client.query(query)
    
    # 4. 返回 DataFrame 格式
    return query_job.to_dataframe()

