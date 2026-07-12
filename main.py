import sys
import logging
import traceback
from datetime import datetime
import config
from api import api_client, api_refresh_log
from monitoring import health_monitor
from pipeline import stage21_live_fusion
from pipeline import stage22_market_fusion
from pipeline import prediction_output

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_daily_pipeline():
    logging.info("🚀 [STEP 1] 启动 WNBA-Quant-Engine 自动化调度系统...")
    try:
        logging.info("⚙️ [STEP 2] 读取 config 配置...")
        if not config.API_BASKETBALL_KEY or not config.ODDS_API_KEY:
            raise ValueError("API 密钥缺失，请检查环境变量或 GitHub Secrets。")
            
        logging.info("🔌 [STEP 3] 检查 API 连接状态...")
        logging.info("📥 [STEP 4] 开始拉取最新外部数据...")
        
        api_data_cache = {}
        endpoints = ['games', 'teams', 'players', 'injuries']
        
        for endpoint in endpoints:
            try:
                if endpoint == 'players':
                    all_players = []
                    for team in api_data_cache.get('teams', []):
                        team_id = team.get('id')
                        if team_id:
                            p_data = api_client.get_wnba_basketball_data('players', params={'team': team_id})
                            all_players.extend(p_data.get('response', []))
                    response_list = all_players
                else:
                    data = api_client.get_wnba_basketball_data(endpoint=endpoint)
                    response_list = data.get("response", [])
                    
                api_data_cache[endpoint] = response_list
                data_count = len(response_list)
                api_refresh_log.log_api_request(f"Basketball-API:{endpoint}", "SUCCESS", data_count)
            except Exception as e:
                api_refresh_log.log_api_request(f"Basketball-API:{endpoint}", "FAILED", 0, str(e))
                logging.warning(f"获取 {endpoint} 数据出现异常: {e}")
                api_data_cache[endpoint] = []

        try:
            odds_data = api_client.get_wnba_odds_data()
            odds_count = len(odds_data)
            api_refresh_log.log_api_request("The-Odds-API:live_odds", "SUCCESS", odds_count)
        except Exception as e:
            api_refresh_log.log_api_request("The-Odds-API:live_odds", "FAILED", 0, str(e))
            logging.warning(f"获取实时盘口数据出现异常: {e}")

        logging.info("🔄 [STEP 5] 启动阶段21：实时状态融合层 (stage21_live_fusion)...")
        live_features = stage21_live_fusion.run_fusion(
            games_list=api_data_cache.get('games', []),
            injuries_list=api_data_cache.get('injuries', [])
        )
        health_monitor.check_data_quality(live_features, "live_state_features")
        logging.info("✅ live_state_features 生成完毕。")

        logging.info("📈 [STEP 6] 启动阶段22：盘口市场融合层 (stage22_market_fusion)...")
        final_predictions = stage22_market_fusion.run_fusion(live_features)
        health_monitor.check_prediction_results(final_predictions)
        logging.info("✅ final_game_prediction 生成完毕。")

        logging.info("📤 [STEP 7] 启动输出模块 (prediction_output)...")
        prediction_output.run_output(final_predictions)
        logging.info("✅ 预测结果分发完毕。")

        logging.info("🎉 [STEP 8] 每日自动化调度任务圆满完成！")

    except Exception as e:
        logging.error("🚨 自动化总调度执行过程中发生致命错误！")
        logging.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    run_daily_pipeline()
