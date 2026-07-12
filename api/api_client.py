import requests
import config

BASKETBALL_API_URL = "https://v1.basketball.api-sports.io"
BASKETBALL_HEADERS = {
    'x-apisports-key': config.API_BASKETBALL_KEY
}

ODDS_API_URL = "https://api.the-odds-api.com/v4/sports/basketball_wnba/odds"

def get_wnba_basketball_data(endpoint: str, params: dict = None) -> dict:
    """
    通用 API-Basketball 请求，自动携带 league 和 season 参数。
    """
    if not config.API_BASKETBALL_KEY:
        raise ValueError("API-Basketball 密钥缺失。")
    
    url = f"{BASKETBALL_API_URL}/{endpoint}"
    
    # 初始化参数
    query_params = params.copy() if params else {}
    
    # 强制注入 WNBA 联赛 ID 和赛季
    query_params.setdefault('league', config.WNBA_LEAGUE_ID)
    query_params.setdefault('season', config.CURRENT_SEASON)
        
    response = requests.get(url, headers=BASKETBALL_HEADERS, params=query_params)
    response.raise_for_status()
    return response.json()

def get_wnba_odds_data(regions: str = 'us', markets: str = 'h2h,spreads') -> list:
    if not config.ODDS_API_KEY:
        raise ValueError("The Odds API 密钥缺失。")
    
    params = {
        'apiKey': config.ODDS_API_KEY,
        'regions': regions,
        'markets': markets,
        'bookmakers': 'pinnacle,draftkings,fanduel'
    }
    response = requests.get(ODDS_API_URL, params=params)
    response.raise_for_status()
    return response.json()
