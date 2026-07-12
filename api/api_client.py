import requests
import os

try:
    import config
except ImportError:
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    import config

BASKETBALL_API_URL = "https://v1.basketball.api-sports.io"
BASKETBALL_HEADERS = {
    'x-apisports-key': config.API_BASKETBALL_KEY
}

ODDS_API_URL = "https://api.the-odds-api.com/v4/sports/basketball_wnba/odds"

_WNBA_LEAGUE_ID_CACHE = None

def _get_wnba_league_id() -> int:
    """
    精确锁定美国目录下的 "NBA W" (即 WNBA) 联赛 ID。
    """
    global _WNBA_LEAGUE_ID_CACHE
    if _WNBA_LEAGUE_ID_CACHE is not None:
        return _WNBA_LEAGUE_ID_CACHE
        
    url = f"{BASKETBALL_API_URL}/leagues"
    
    try:
        # 既然确认了在 USA 下，直接请求美国的联赛名单
        params = {"country": "USA"}
        response = requests.get(url, headers=BASKETBALL_HEADERS, params=params)
        response.raise_for_status()
        
        # 遍历返回的联赛，精准匹配 "NBA W"
        for item in response.json().get("response", []):
            if str(item.get("name", "")).strip().upper() == "NBA W":
                _WNBA_LEAGUE_ID_CACHE = item.get("id")
                return _WNBA_LEAGUE_ID_CACHE
                
    except Exception as e:
        raise ValueError(f"拉取联赛 ID 失败: {str(e)}")
        
    raise ValueError("🚨 无法在 API-Sports 美国 (USA) 目录下找到 'NBA W'。")

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
        
    # 动态注入真实的联赛 ID 和当前赛季
    if endpoint != 'leagues':
        params['league'] = _get_wnba_league_id()
        if 'season' not in params:
            params['season'] = config.CURRENT_SEASON
    
    response = requests.get(url, headers=BASKETBALL_HEADERS, params=params)
    response.raise_for_status()
    return response.json()

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
        'bookmakers': 'pinnacle,draftkings,fanduel' 
    }
    
    response = requests.get(ODDS_API_URL, params=params)
    response.raise_for_status()
    return response.json()
