import pandas as pd
from typing import Dict, Any, List
from domain.models import Stock, Theme, ThemeGroup
from domain.value_objects import MarketCap, ChangeRatio
from domain.services import ThemeStatisticsService
from domain.theme_config import THEME_HIERARCHY, PRIORITY_THEMES, THEME_RENAME
from infrastructure.krx_repository import KrxRepository
from infrastructure.file_repository import ThemeFileRepository

class HeatmapService:
    """히트맵 데이터 처리 서비스
    
    Application 레이어로서 유스케이스를 조율합니다.
    - Repository로부터 데이터 로드
    - Domain Model로 변환
    - Domain Service 활용
    """
    
    def __init__(self):
        self.krx_repo = KrxRepository()
        self.file_repo = ThemeFileRepository()
        self.theme_stats_service = ThemeStatisticsService()

    def get_heatmap_data(self) -> pd.DataFrame:
        """히트맵 생성을 위한 최종 데이터를 반환합니다.
        
        하위 호환성을 위해 DataFrame을 반환하지만,
        내부적으로는 Domain Model을 사용합니다.
        """
        # 1. 도메인 모델로 변환
        themes = self._build_theme_models()
        
        if not themes:
            print("데이터 로드 실패")
            return pd.DataFrame()
        
        # 2. Domain Model -> DataFrame 변환 (하위 호환)
        return self._convert_themes_to_dataframe(themes)

    def get_themes(self) -> List[Theme]:
        """도메인 모델로 테마 목록을 반환합니다."""
        return self._build_theme_models()

    def calculate_group_stats(self, df_final: pd.DataFrame) -> Dict[str, Dict[str, float]]:
        """테마 그룹별 통계를 계산합니다. (기존 API 유지)"""
        # DataFrame -> Domain Model 변환
        themes = self._dataframe_to_themes(df_final)
        
        # Domain Service 사용
        group_stats_models = self.theme_stats_service.calculate_group_stats(themes)
        
        # Domain Model -> Dict 변환 (하위 호환)
        result = {}
        for group_name, group in group_stats_models.items():
            result[group_name] = {
                'cap': group.market_cap.in_trillion,
                'change_sum': group.change_sum
            }
        
        return result
    
    def get_group_stats_models(self, themes: List[Theme]) -> Dict[str, ThemeGroup]:
        """도메인 모델로 그룹 통계를 반환합니다."""
        return self.theme_stats_service.calculate_group_stats(themes)

    # === Private Methods ===
    
    def _build_theme_models(self) -> List[Theme]:
        """Repository로부터 데이터를 로드하여 Domain Model로 변환합니다."""
        # 1. 데이터 로드
        df_krx = self.krx_repo.fetch_listing()
        df_theme = self.file_repo.load_themes()
        
        if df_krx.empty or df_theme.empty:
            return []
        
        # 2. 데이터 병합
        merged_df = pd.merge(df_theme, df_krx, left_on='종목명', right_on='Name', how='left')
        df_final = merged_df.dropna(subset=['Code']).copy()
        
        # 3. 테마명 변경 적용
        df_final['테마'] = df_final['테마'].replace(THEME_RENAME)
        
        # 4. Domain Model로 변환
        return self._dataframe_to_themes(df_final)
    
    def _dataframe_to_themes(self, df: pd.DataFrame) -> List[Theme]:
        """DataFrame을 Domain Model(Theme 리스트)로 변환합니다."""
        themes_dict: Dict[str, Theme] = {}
        
        for _, row in df.iterrows():
            theme_name = str(row.get('테마', ''))
            stock_name = str(row.get('종목명', row.get('Name', '')))
            code = str(row.get('Code', ''))
            
            # MarketCap Value Object 생성
            marcap_value = float(row.get('Marcap', 0))
            market_cap = MarketCap(marcap_value) if marcap_value > 0 else MarketCap.zero()
            
            # ChangeRatio Value Object 생성
            change_value = float(row.get('ChagesRatio', 0))
            try:
                change_ratio = ChangeRatio(change_value)
            except ValueError:
                # 범위 초과 시 0으로 처리
                change_ratio = ChangeRatio.zero()
            
            # Stock 엔티티 생성
            try:
                stock = Stock(
                    code=code,
                    name=stock_name,
                    market_cap=market_cap,
                    change_ratio=change_ratio
                )
            except ValueError:
                # 유효하지 않은 데이터는 스킵
                continue
            
            # Theme 엔티티에 Stock 추가
            if theme_name not in themes_dict:
                theme = Theme(
                    name=theme_name,
                    parent_group=THEME_HIERARCHY.get(theme_name)
                )
                themes_dict[theme_name] = theme
            
            themes_dict[theme_name].add_stock(stock)
        
        return list(themes_dict.values())
    
    def _convert_themes_to_dataframe(self, themes: List[Theme]) -> pd.DataFrame:
        """Domain Model을 DataFrame으로 변환합니다. (하위 호환)"""
        rows = []
        
        for theme in themes:
            for stock in theme.stocks:
                rows.append({
                    '테마': theme.name,
                    '종목명': stock.name,
                    'Code': stock.code,
                    'Name': stock.name,
                    'Marcap': stock.market_cap.value_in_won,
                    '시가총액_조': stock.market_cap.in_trillion,
                    'ChagesRatio': stock.change_ratio.value
                })
        
        return pd.DataFrame(rows)
