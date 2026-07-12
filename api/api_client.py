import requests
import os

# 导入配置中心
try:
    import config
except ImportError:
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    import config

# ==========================================
# API 基础配置
# ==========================================
BASKETBALL_API_URL = "https://v1.basketball.api-sports.io"
BASKETBALL_HEADERS = {
    'x-apisports-key': config.API_BASKETBALL_KEY
}

ODDS_API_URL = "https://api.the-odds-api.com/v4/sports/basketball_wnba/odds"

# ==========================================
# 1. API-Basketball 接口封装
# ==========================================
def get_wnba_basketball_data(endpoint: str, params: dict = None) -> dict:
    """
    通用 API-Basketball 请求函数。
    支持的 endpoint 示例: 'games', 'teams', 'players', 'injuries'
    """
    if not config.API_BASKETBALL_KEY:
        raise ValueError("🚨 安全拦截: 缺少 API-Basketball 密钥，请检查 config.py 或 Secrets。")
    
    url = f"{BASKETBALL_API_URL}/{endpoint}"
    
    if params is None:
        params = {}
        
    # 强制加上 WNBA 联赛 ID 和 当前赛季
    params['league'] = config.WNBA_LEAGUE_ID
    params['season'] = config.CURRENT_SEASON
    
    response = requests.get(url, headers=BASKETBALL_HEADERS, params=params)
    response.raise_for_status()
    return response.json()

# ==========================================
# 2. The Odds API 接口封装
# ==========================================
def get_wnba_odds_data(regions: str = 'us', markets: str = 'h2h,spreads') -> list:
    """
    请求 The Odds API 获取 WNBA 实时盘口与开盘赔率数据。
    """
    if not config.ODDS_API_KEY:
        raise ValueError("🚨 安全拦截: 缺少 The Odds API 密钥，请检查 config.py 或 Secrets。")
    
    params = {
        'apiKey': config.ODDS_API_KEY,
        'regions': regions,
        'markets': markets,
        'bookmakers': 'pinnacle,draftkings,fanduel' # 常用主流菠菜公司
    }
    
    response = requests.get(ODDS_API_URL, params=params)
    response.raise_for_status()
    return response.json()
