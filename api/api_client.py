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
    动态获取 WNBA 联赛 ID。
    取消强绑定 country="USA"（因 API-Sports 可能将其归类为 World 或无国家标签）。
    """
    global _WNBA_LEAGUE_ID_CACHE
    if _WNBA_LEAGUE_ID_CACHE is not None:
        return _WNBA_LEAGUE_ID_CACHE
        
    url = f"{BASKETBALL_API_URL}/leagues"
    
    try:
        # 第一步：直接用 search 关键词找（不加国家限制）
        response = requests.get(url, headers=BASKETBALL_HEADERS, params={"search": "WNBA"})
        response.raise_for_status()
        
        results = response.json().get("response", [])
        
        # 优先精确匹配
        for item in results:
            if str(item.get("name", "")).strip().upper() == "WNBA":
                _WNBA_LEAGUE_ID_CACHE = item.get("id")
                return _WNBA_LEAGUE_ID_CACHE
                
        # 其次模糊匹配 (防备叫 "WNBA (Women)" 之类的名字)
        for item in results:
            if "WNBA" in str(item.get("name", "")).upper():
                _WNBA_LEAGUE_ID_CACHE = item.get("id")
                return _WNBA_LEAGUE_ID_CACHE

        # 第二步：如果 search 没找到，拉取全球全部联赛进行地毯式搜索
        response_all = requests.get(url, headers=BASKETBALL_HEADERS)
        response_all.raise_for_status()
        all_leagues = response_all.json().get("response", [])
        
        for item in all_leagues:
            if str(item.get("name", "")).strip().upper() == "WNBA":
                _WNBA_LEAGUE_ID_CACHE = item.get("id")
                return _WNBA_LEAGUE_ID_CACHE
                
        for item in all_leagues:
            if "WNBA" in str(item.get("name", "")).upper():
                _WNBA_LEAGUE_ID_CACHE = item.get("id")
                return _WNBA_LEAGUE_ID_CACHE
                
    except Exception as e:
        raise ValueError(f"拉取 WNBA 联赛 ID 失败: {str(e)}")
        
    raise ValueError("🚨 全库地毯式搜索失败，无法在 API-Sports 中找到 WNBA，请检查 API 数据订阅情况。")

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
        
    # 动态注入真实的 WNBA 联赛 ID 和当前赛季
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
