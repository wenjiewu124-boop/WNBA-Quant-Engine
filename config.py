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

# BigQuery 数据集名称
BQ_DATASET = "wnba_quant_dataset" 

# BigQuery 常用表名配置
BQ_TABLE_LIVE_FEATURES = "stage21_live_features"
BQ_TABLE_MARKET_FEATURES = "stage22_market_features"
BQ_TABLE_PREDICTIONS = "final_predictions"

# ==========================================
# 3. 认证环境配置
# ==========================================
GCP_CREDENTIALS_JSON_STR = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

# ==========================================
# 4. 系统全局参数
# ==========================================
CURRENT_SEASON = 2026 
# 修复：WNBA 在 API-Basketball 中的真实官方 League ID 为 59
WNBA_LEAGUE_ID = 59
