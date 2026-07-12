import sys
import logging
import traceback
from datetime import datetime

# 导入系统模块
import config
from api import api_client, api_refresh_log

# 导入业务流水线模块 (当前为预留存根，后续阶段填充)
from pipeline import stage21_live_fusion
from pipeline import stage22_market_fusion
from pipeline import prediction_output

# 配置基础日志记录
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def run_daily_pipeline():
    """
    WNBA 量化系统每日自动化总调度入口
    执行顺序：配置读取 -> API拉取 -> 阶段21 -> 阶段22 -> 结果输出
    """
    logging.info("🚀 [STEP 1] 启动 WNBA-Quant-Engine 自动化调度系统...")
    
    try:
        # ==========================================
        # STEP 2 & 3: 读取配置与检查 API 连接
        # ==========================================
        logging.info("⚙️ [STEP 2] 读取 config 配置...")
        if not config.API_BASKETBALL_KEY or not config.ODDS_API_KEY:
            raise ValueError("API 密钥缺失，请检查环境变量或 GitHub Secrets。")
            
        logging.info("🔌 [STEP 3] 检查 API 连接状态...")
        # ==========================================
        # STEP 4: 拉取最新数据
        # ==========================================
        logging.info("📥 [STEP 4] 开始拉取最新外部数据...")
        
        # 4.1 拉取 API-Basketball 数据 (比赛、球队、球员、伤病)
        endpoints = ['games', 'teams', 'players', 'injuries']
        for endpoint in endpoints:
            try:
                data = api_client.get_wnba_basketball_data(endpoint=endpoint, params={"season": config.CURRENT_SEASON})
                data_count = len(data.get("response", []))
                api_refresh_log.log_api_request(f"Basketball-API:{endpoint}", "SUCCESS", data_count)
            except Exception as e:
                api_refresh_log.log_api_request(f"Basketball-API:{endpoint}", "FAILED", 0, str(e))
                logging.warning(f"获取 {endpoint} 数据出现异常: {e}")

        # 4.2 拉取 The Odds API 数据 (实时盘口)
        try:
            odds_data = api_client.get_wnba_odds_data()
            odds_count = len(odds_data)
            api_refresh_log.log_api_request("The-Odds-API:live_odds", "SUCCESS", odds_count)
        except Exception as e:
            api_refresh_log.log_api_request("The-Odds-API:live_odds", "FAILED", 0, str(e))
            logging.warning(f"获取实时盘口数据出现异常: {e}")

        # ==========================================
        # STEP 5: 调用阶段21 (生成 live_state_features)
        # ==========================================
        logging.info("🔄 [STEP 5] 启动阶段21：实时状态融合层 (stage21_live_fusion)...")
        # 预留调用接口，等待 stage21 业务代码填入
        if hasattr(stage21_live_fusion, 'run_fusion'):
            live_features = stage21_live_fusion.run_fusion()
            logging.info("✅ live_state_features 生成完毕。")
        else:
            logging.info("⚠️ stage21_live_fusion 业务代码暂未实装，跳过执行。")

        # ==========================================
        # STEP 6: 调用阶段22 (生成 final_game_prediction)
        # ==========================================
        logging.info("📈 [STEP 6] 启动阶段22：盘口市场融合层 (stage22_market_fusion)...")
        # 预留调用接口，等待 stage22 业务代码填入
        if hasattr(stage22_market_fusion, 'run_fusion'):
            final_predictions = stage22_market_fusion.run_fusion()
            logging.info("✅ final_game_prediction 生成完毕。")
        else:
            logging.info("⚠️ stage22_market_fusion 业务代码暂未实装，跳过执行。")

        # ==========================================
        # STEP 7: 调用结果输出模块
        # ==========================================
        logging.info("📤 [STEP 7] 启动输出模块 (prediction_output)...")
        if hasattr(prediction_output, 'export_results'):
            prediction_output.export_results()
            logging.info("✅ 预测结果分发完毕。")
        else:
            logging.info("⚠️ prediction_output 业务代码暂未实装，跳过执行。")

        # ==========================================
        # STEP 8: 记录运行日志
        # ==========================================
        logging.info("🎉 [STEP 8] 每日自动化调度任务圆满完成！")

    except Exception as e:
        logging.error("🚨 自动化总调度执行过程中发生致命错误！")
        logging.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    run_daily_pipeline()
