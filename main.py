        # ==========================================
        # STEP 5: 调用阶段21 (生成 live_state_features)
        # ==========================================
        logging.info("🔄 [STEP 5] 启动阶段21：实时状态融合层 (stage21_live_fusion)...")
        live_features = stage21_live_fusion.run_fusion()
        
        # 引入健康监控验证数据质量
        from monitoring import health_monitor
        health_monitor.check_data_quality(live_features, "live_state_features")

        # ==========================================
        # STEP 6: 调用阶段22 (生成 final_game_prediction)
        # ==========================================
        logging.info("📈 [STEP 6] 启动阶段22：盘口市场融合层 (stage22_market_fusion)...")
        final_predictions = stage22_market_fusion.run_fusion(live_features)
        
        # 引入健康监控验证预测结果边界
        health_monitor.check_prediction_results(final_predictions)
