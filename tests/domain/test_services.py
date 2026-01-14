"""
Domain Services 단위 테스트
"""
import pytest
from src.domain.models import Stock, Theme
from src.domain.value_objects import MarketCap, ChangeRatio
from src.domain.services import ThemeStatisticsService


class TestThemeStatisticsService:
    """ThemeStatisticsService 테스트"""
    
    @pytest.fixture
    def sample_themes(self):
        """테스트용 샘플 테마 데이터"""
        # 반도체 테마
        semiconductor = Theme(name="반도체")
        semiconductor.add_stock(Stock(
            code="005930",
            name="삼성전자",
            market_cap=MarketCap.from_trillion(400),
            change_ratio=ChangeRatio(2.0)
        ))
        semiconductor.add_stock(Stock(
            code="000660",
            name="SK하이닉스",
            market_cap=MarketCap.from_trillion(100),
            change_ratio=ChangeRatio(3.0)
        ))
        
        # 2차전지 테마
        battery = Theme(name="2차전지")
        battery.add_stock(Stock(
            code="006400",
            name="삼성SDI",
            market_cap=MarketCap.from_trillion(50),
            change_ratio=ChangeRatio(1.5)
        ))
        battery.add_stock(Stock(
            code="051910",
            name="LG화학",
            market_cap=MarketCap.from_trillion(70),
            change_ratio=ChangeRatio(2.5)
        ))
        
        # 바이오 테마
        bio = Theme(name="바이오")
        bio.add_stock(Stock(
            code="207940",
            name="삼성바이오로직스",
            market_cap=MarketCap.from_trillion(80),
            change_ratio=ChangeRatio(-1.0)
        ))
        
        return [semiconductor, battery, bio]
    
    def test_sort_themes_by_market_cap(self, sample_themes):
        """시가총액 순 정렬 테스트"""
        sorted_themes = ThemeStatisticsService.sort_themes_by_market_cap(sample_themes)
        
        # 반도체(500조) > 2차전지(120조) > 바이오(80조)
        assert sorted_themes[0].name == "반도체"
        assert sorted_themes[1].name == "2차전지"
        assert sorted_themes[2].name == "바이오"
    
    def test_sort_themes_ascending(self, sample_themes):
        """시가총액 오름차순 정렬"""
        sorted_themes = ThemeStatisticsService.sort_themes_by_market_cap(
            sample_themes,
            descending=False
        )
        
        # 바이오(80조) < 2차전지(120조) < 반도체(500조)
        assert sorted_themes[0].name == "바이오"
        assert sorted_themes[1].name == "2차전지"
        assert sorted_themes[2].name == "반도체"
    
    def test_filter_themes_by_min_stocks(self, sample_themes):
        """최소 종목 수로 필터링"""
        # 2개 이상 종목을 가진 테마만 추출
        filtered = ThemeStatisticsService.filter_themes_by_min_stocks(
            sample_themes,
            min_stocks=2
        )
        
        assert len(filtered) == 2
        assert all(theme.stock_count >= 2 for theme in filtered)
    
    def test_get_top_stocks_by_market_cap(self, sample_themes):
        """테마 내 시가총액 상위 종목 추출"""
        semiconductor = sample_themes[0]  # 반도체
        
        top_stocks = ThemeStatisticsService.get_top_stocks_by_market_cap(
            semiconductor,
            top_n=1
        )
        
        assert len(top_stocks) == 1
        assert top_stocks[0].name == "삼성전자"
    
    def test_calculate_group_stats(self, sample_themes):
        """그룹 통계 계산 테스트"""
        # parent_group 설정
        sample_themes[0].parent_group = "IT"
        sample_themes[1].parent_group = "IT"
        # 바이오는 parent_group 없음
        
        group_stats = ThemeStatisticsService.calculate_group_stats(sample_themes)
        
        # IT 그룹만 집계되어야 함
        assert "IT" in group_stats
        assert group_stats["IT"].name == "IT"
        
        # IT 그룹 시가총액 = 반도체(500조) + 2차전지(120조) = 620조
        assert group_stats["IT"].market_cap.in_trillion == pytest.approx(620.0, rel=0.01)
