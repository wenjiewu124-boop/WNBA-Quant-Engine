# pipeline/team_strength_engine.py
# ============================================================
#  WNBA-Quant-Engine  —  Stage 24.1
#  Module : team_strength_engine
#  Tables : teams / team_stats / team_stats_clean
#           team_features / team_features_clean / team_strength_base
# ============================================================

from __future__ import annotations
import logging
from typing import List
import pandas as pd

logger = logging.getLogger("wnba.stage24.team_strength")
logger.setLevel(logging.INFO)
if not logger.handlers:
    _h = logging.StreamHandler()
    _h.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
    logger.addHandler(_h)

# 1. 严格基于真实表结构的 Schema 定义
TEAMS_COLUMNS = ["team_id", "team_name", "league_id"]
TEAM_STATS_COLUMNS = ["game_id", "team_id", "points", "rebounds", "assists", "steals", "blocks", "turnovers"]
TEAM_STATS_CLEAN_COLUMNS = ["espn_game_id", "season", "game_date", "team_name", "team_pts", "team_reb", "team_ast", "team_stl", "team_blk", "team_fgm", "team_fga", "team_tpm", "team_tpa", "team_ftm", "team_fta", "team_fg_pct", "team_tp_pct", "team_ft_pct"]
TEAM_FEATURES_COLUMNS = ["espn_game_id", "season", "game_date", "team_name", "team_pts", "team_reb", "team_ast", "team_stl", "team_blk", "team_fgm", "team_fga", "team_tpm", "team_tpa", "team_ftm", "team_fta", "opp_team_name", "opp_pts", "opp_fga", "opp_fta", "poss", "opp_poss", "ortg", "drtg", "net_rating", "pace", "fg_pct", "tp_pct", "ft_pct", "efg_pct", "ts_pct", "oreb", "dreb", "turnovers", "ast_tov_ratio", "l5_pts_avg", "l5_opp_pts_avg", "l5_net_pts", "l5_ortg_avg", "l5_drtg_avg", "l10_pts_avg", "l10_ortg_avg"]
TEAM_STRENGTH_BASE_COLUMNS = ["team_id", "team_name", "season", "update_date", "ORTG", "DRTG", "Net_Rating", "Pace", "eFG_pct", "TS_pct", "last_5_net_rating", "last_10_net_rating", "season_net_rating", "home_rating", "away_rating", "home_advantage", "scoring_consistency", "defensive_consistency", "team_power_rating", "Offensive_Grade", "Defensive_Grade", "Overall_Rank"]

WNBA_LEAGUE_ID = 13

class TeamStrengthEngine:
    def __init__(self, teams: pd.DataFrame, team_stats: pd.DataFrame, team_stats_clean: pd.DataFrame, team_features: pd.DataFrame, team_features_clean: pd.DataFrame, team_strength_base: pd.DataFrame):
        self.teams = teams
        self.team_stats = team_stats
        self.team_stats_clean = team_stats_clean
        self.team_features = team_features
        self.team_features_clean = team_features_clean
        self.team_strength_base = team_strength_base
        self._validate()

    def _validate(self):
        for name, df, cols in [
            ("teams", self.teams, TEAMS_COLUMNS),
            ("team_stats", self.team_stats, TEAM_STATS_COLUMNS),
            ("team_stats_clean", self.team_stats_clean, TEAM_STATS_CLEAN_COLUMNS),
            ("team_features", self.team_features, TEAM_FEATURES_COLUMNS),
            ("team_features_clean", self.team_features_clean, TEAM_FEATURES_COLUMNS),
            ("team_strength_base", self.team_strength_base, TEAM_STRENGTH_BASE_COLUMNS)
        ]:
            missing = [c for c in cols if c not in df.columns]
            if missing:
                raise ValueError(f"[{name}] 缺少字段: {missing}")

    def _off_grade(self, ortg: float) -> str:
        if ortg >= 113: return "S"
        elif ortg >= 110: return "A"
        elif ortg >= 106: return "B"
        return "C"

    def _def_grade(self, drtg: float) -> str:
        if drtg <= 102: return "S"
        elif drtg <= 106: return "A"
        elif drtg <= 110: return "B"
        return "D"

    def _power_rating(self, row: pd.Series) -> float:
        return (
            0.40 * (row["Net_Rating"] if pd.notna(row["Net_Rating"]) else 0.0) +
            0.25 * ((row["ORTG"] - row["DRTG"]) if pd.notna(row["ORTG"]) and pd.notna(row["DRTG"]) else 0.0) +
            0.15 * (row["TS_pct"] * 100 if pd.notna(row["TS_pct"]) else 0.0) +
            0.10 * (row["eFG_pct"] * 100 if pd.notna(row["eFG_pct"]) else 0.0) +
            0.10 * (row["home_advantage"] if pd.notna(row["home_advantage"]) else 0.0)
        )

    def run(self) -> pd.DataFrame:
        logger.info("启动 Stage 24.1 Team Strength Engine...")
        
        # 维表过滤
        teams_tbl = self.teams[self.teams["league_id"] == WNBA_LEAGUE_ID][["team_id", "team_name"]].drop_duplicates()
        
        # 特征表准备 (优先使用 clean 表)
        feat = self.team_features_clean.copy() if not self.team_features_clean.empty else self.team_features.copy()
        for c in feat.columns:
            if c not in ["espn_game_id", "season", "team_name", "game_date", "opp_team_name"]:
                feat[c] = pd.to_numeric(feat[c], errors="coerce")
        feat["game_date"] = pd.to_datetime(feat["game_date"], errors="coerce")
        feat = feat.dropna(subset=["team_name", "season"])
        
        # 映射 team_id
        mapping = dict(zip(teams_tbl["team_name"], teams_tbl["team_id"]))
        feat["team_id"] = feat["team_name"].map(mapping)
        feat = feat.dropna(subset=["team_id"])
        feat["team_id"] = feat["team_id"].astype(int)
        
        rows = []
        for (tid, tname, season), g in feat.groupby(["team_id", "team_name", "season"]):
            g_sorted = g.sort_values("game_date")
            last_row = g_sorted.iloc[-1]
            
            ortg = g_sorted["ortg"].mean()
            drtg = g_sorted["drtg"].mean()
            net = g_sorted["net_rating"].mean()
            pace = g_sorted["pace"].mean()
            efg = g_sorted["efg_pct"].mean()
            ts = g_sorted["ts_pct"].mean()
            
            l5_net = last_row.get("l5_net_pts")
            l10_ortg = last_row.get("l10_ortg_avg")
            l5_drtg = last_row.get("l5_drtg_avg")
            
            last_10_net = (l10_ortg - l5_drtg) if pd.notna(l10_ortg) and pd.notna(l5_drtg) else net
            
            base = {
                "team_id": int(tid),
                "team_name": tname,
                "season": int(season),
                "update_date": g_sorted["game_date"].max(),
                "ORTG": ortg,
                "DRTG": drtg,
                "Net_Rating": net,
                "Pace": pace,
                "eFG_pct": efg,
                "TS_pct": ts,
                "last_5_net_rating": l5_net if pd.notna(l5_net) else net,
                "last_10_net_rating": last_10_net,
                "season_net_rating": net,
                "home_rating": net,  # 无显式主客字段,近似
                "away_rating": net,
                "home_advantage": 0.0,
                "scoring_consistency": g_sorted["team_pts"].std(),
                "defensive_consistency": g_sorted["opp_pts"].std(),
            }
            base["team_power_rating"] = self._power_rating(base)
            base["Offensive_Grade"] = self._off_grade(ortg or 0.0)
            base["Defensive_Grade"] = self._def_grade(drtg or 200.0)
            rows.append(base)
            
        computed = pd.DataFrame(rows)
        computed["Overall_Rank"] = computed.groupby("season")["team_power_rating"].rank(method="min", ascending=False).astype(int)
        
        # 对账合并：以原 team_strength_base 为主，computed 补缺
        base = self.team_strength_base.copy()
        merged = base.merge(computed, on=["team_id", "season"], how="outer", suffixes=("_base", "_comp"))
        for c in TEAM_STRENGTH_BASE_COLUMNS:
            if c in ["team_id", "season"]: continue
            b_col, c_col = f"{c}_base", f"{c}_comp"
            if b_col in merged.columns and c_col in merged.columns:
                merged[c] = merged[b_col].where(merged[b_col].notna(), merged[c_col])
            elif b_col in merged.columns:
                merged[c] = merged[b_col]
            elif c_col in merged.columns:
                merged[c] = merged[c_col]
                
        final = merged[TEAM_STRENGTH_BASE_COLUMNS].sort_values(["season", "Overall_Rank"], ascending=[False, True]).reset_index(drop=True)
        logger.info(f"Stage 24.1 完成, 输出 {len(final)} 条记录。")
        return final

def build_team_strength(teams, team_stats, team_stats_clean, team_features, team_features_clean, team_strength_base) -> pd.DataFrame:
    return TeamStrengthEngine(teams, team_stats, team_stats_clean, team_features, team_features_clean, team_strength_base).run()
