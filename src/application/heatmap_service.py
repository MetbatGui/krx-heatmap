import pandas as pd
from typing import Dict, Any, List
from domain.models import Stock, ThemeGroup
from domain.theme_config import THEME_HIERARCHY, PRIORITY_THEMES, THEME_RENAME
from infrastructure.krx_repository import KrxRepository
from infrastructure.file_repository import ThemeFileRepository

class HeatmapService:
    """히트맵 데이터 처리 서비스"""
    
    def __init__(self):
        self.krx_repo = KrxRepository()
        self.file_repo = ThemeFileRepository()

    def get_heatmap_data(self) -> pd.DataFrame:
        """히트맵 생성을 위한 최종 데이터를 반환합니다."""
        # 1. 데이터 로드
        df_krx = self.krx_repo.fetch_listing()
        df_theme = self.file_repo.load_themes()
        
        if df_krx.empty or df_theme.empty:
            print("데이터 로드 실패")
            return pd.DataFrame()

        # 2. 데이터 병합
        merged_df = pd.merge(df_theme, df_krx, left_on='종목명', right_on='Name', how='left')
        
        # 3. 데이터 전처리
        df_final = merged_df.dropna(subset=['Code']).copy()
        
        # 시가총액: 조 단위 변환
        df_final['Marcap'] = df_final['Marcap'].fillna(0)
        df_final['시가총액_조'] = df_final['Marcap'] / 1_000_000_000_000
        
        # 등락률: NaN은 0으로 처리
        df_final['ChagesRatio'] = df_final['ChagesRatio'].fillna(0)
        
        # 테마명 변경 적용
        df_final['테마'] = df_final['테마'].replace(THEME_RENAME)
        
        return df_final

    def calculate_group_stats(self, df_final: pd.DataFrame) -> Dict[str, Dict[str, float]]:
        """테마 그룹별 통계를 계산합니다."""
        group_stats = {} # {group_name: {'cap': 0, 'change_sum': 0}}
        
        theme_groups = df_final.groupby('테마')
        
        for theme_name, group in theme_groups:
            parent_group = THEME_HIERARCHY.get(theme_name)
            
            theme_mkt_cap = group['시가총액_조'].sum()
            theme_change_sum = (group['ChagesRatio'] * group['시가총액_조']).sum()
            
            if parent_group:
                if parent_group not in group_stats:
                    group_stats[parent_group] = {'cap': 0, 'change_sum': 0}
                group_stats[parent_group]['cap'] += theme_mkt_cap
                group_stats[parent_group]['change_sum'] += theme_change_sum
                
        return group_stats
