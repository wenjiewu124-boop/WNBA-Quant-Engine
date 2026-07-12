import os
import json

# ==========================================
# 1. API 密钥配置 (通过 GitHub Secrets 注入)
# ==========================================
ODDS_API_KEY = os.getenv("ODDS_API_KEY")
API_BASKETBALL_KEY = os.getenv("API_BASKETBALL_KEY")

# ==========================================
# 2. GCP & BigQuery 配置
# ==========================================
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")

# BigQuery 数据集名称 (您可以根据实际使用的名称修改)
BQ_DATASET = "wnba_quant_dataset" 

# BigQuery 常用表名配置
BQ_TABLE_LIVE_FEATURES = "stage21_live_features"
BQ_TABLE_MARKET_FEATURES = "stage22_market_features"
BQ_TABLE_PREDICTIONS = "final_predictions"

# ==========================================
# 3. 认证环境配置
# ==========================================
# 检查是否传入了 JSON 字符串格式的凭证 (GitHub Actions 常用)
# 如果有，我们在主程序中将其写入临时文件供 GCP SDK 调用
GCP_CREDENTIALS_JSON_STR = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")

# 本地运行或已存在凭证文件的路径
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

# ==========================================
# 4. 系统全局参数
# ==========================================
# 设置当前赛季，用于 API 请求过滤等
CURRENT_SEASON = 2026 
# ==========================================
# 4. 系统全局参数
# ==========================================
# 设置当前赛季，用于 API 请求过滤等
CURRENT_SEASON = 2026 
# WNBA 在 API-Basketball 中的官方联赛 ID 为 143
WNBA_LEAGUE_ID = 143
