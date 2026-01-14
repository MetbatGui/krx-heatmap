"""
Domain Services

도메인 로직을 담당하는 서비스 레이어입니다.
여러 엔티티에 걸친 비즈니스 로직을 처리합니다.
"""
from typing import List, Dict
from .models import Theme, ThemeGroup, Stock
from .theme_config import THEME_HIERARCHY
from .value_objects import MarketCap


class ThemeStatisticsService:
    """테마 통계 계산 도메인 서비스"""
    
    @staticmethod
    def calculate_group_stats(themes: List[Theme]) -> Dict[str, ThemeGroup]:
        """계층 구조를 고려한 그룹 통계 계산
        
        Args:
            themes: 테마 목록
            
        Returns:
            그룹명을 키로, ThemeGroup 통계를 값으로 하는 딕셔너리
        """
        group_stats: Dict[str, Dict[str, float]] = {}
        
        for theme in themes:
            # parent_group은 theme 객체의 속성 또는 THEME_HIERARCHY에서 가져올 수 있음
            parent_group = theme.parent_group or THEME_HIERARCHY.get(theme.name)
            
            if not parent_group:
                continue
            
            theme_mkt_cap = theme.total_market_cap
            theme_change_sum = sum(stock.weighted_change() for stock in theme.stocks)
            
            if parent_group not in group_stats:
                group_stats[parent_group] = {'cap': 0, 'change_sum': 0}
            
            group_stats[parent_group]['cap'] += theme_mkt_cap.in_trillion
            group_stats[parent_group]['change_sum'] += theme_change_sum
        
        # ThemeGroup 객체로 변환
        result = {}
        for group_name, stats in group_stats.items():
            result[group_name] = ThemeGroup(
                name=group_name,
                market_cap=MarketCap.from_trillion(stats['cap']),
                change_sum=stats['change_sum']
            )
        
        return result
    
    @staticmethod
    def sort_themes_by_market_cap(themes: List[Theme], descending: bool = True) -> List[Theme]:
        """시가총액 순으로 테마 정렬
        
        Args:
            themes: 테마 목록
            descending: True면 내림차순, False면 오름차순
            
        Returns:
            정렬된 테마 목록
        """
        return sorted(
            themes,
            key=lambda t: t.total_market_cap.value_in_won,
            reverse=descending
        )
    
    @staticmethod
    def filter_themes_by_min_stocks(themes: List[Theme], min_stocks: int) -> List[Theme]:
        """최소 종목 수로 테마 필터링
        
        Args:
            themes: 테마 목록
            min_stocks: 최소 종목 수
            
        Returns:
            필터링된 테마 목록
        """
        return [theme for theme in themes if theme.stock_count >= min_stocks]
    
    @staticmethod
    def get_top_stocks_by_market_cap(theme: Theme, top_n: int) -> List[Stock]:
        """테마 내 시가총액 상위 N개 종목 반환
        
        Args:
            theme: 테마
            top_n: 상위 N개
            
        Returns:
            시가총액 상위 종목 목록
        """
        return sorted(
            theme.stocks,
            key=lambda s: s.market_cap.value_in_won,
            reverse=True
        )[:top_n]
