"""
Domain Models 단위 테스트
"""
import pytest
from src.domain.models import Stock, Theme, ThemeGroup
from src.domain.value_objects import MarketCap, ChangeRatio


class TestStock:
    """Stock 엔티티 테스트"""
    
    def test_create_stock(self):
        """종목 생성 테스트"""
        stock = Stock(
            code="005930",
            name="삼성전자",
            market_cap=MarketCap(400_000_000_000_000),  # 400조
            change_ratio=ChangeRatio(2.5)
        )
        
        assert stock.code == "005930"
        assert stock.name == "삼성전자"
        assert stock.market_cap_trillion == 400.0
        assert stock.change_ratio.value == 2.5
    
    def test_stock_requires_code(self):
        """종목 코드는 필수"""
        with pytest.raises(ValueError, match="종목 코드는 필수입니다"):
            Stock(
                code="",
                name="삼성전자",
                market_cap=MarketCap.zero(),
                change_ratio=ChangeRatio.zero()
            )
    
    def test_stock_requires_name(self):
        """종목명은 필수"""
        with pytest.raises(ValueError, match="종목명은 필수입니다"):
            Stock(
                code="005930",
                name="",
                market_cap=MarketCap.zero(),
                change_ratio=ChangeRatio.zero()
            )
    
    def test_weighted_change(self):
        """가중 등락률 계산"""
        stock = Stock(
            code="005930",
            name="삼성전자",
            market_cap=MarketCap(100_000_000_000_000),  # 100조
            change_ratio=ChangeRatio(3.0)  # 3%
        )
        
        weighted = stock.weighted_change()
        assert weighted == 300.0  # 3% * 100조 = 300


class TestTheme:
    """Theme 엔티티 테스트"""
    
    def test_create_theme(self):
        """테마 생성 테스트"""
        theme = Theme(name="반도체")
        assert theme.name == "반도체"
        assert theme.stock_count == 0
        assert theme.total_market_cap.value_in_won == 0
    
    def test_theme_requires_name(self):
        """테마명은 필수"""
        with pytest.raises(ValueError, match="테마명은 필수입니다"):
            Theme(name="")
    
    def test_add_stock_to_theme(self):
        """테마에 종목 추가"""
        theme = Theme(name="반도체")
        stock = Stock(
            code="005930",
            name="삼성전자",
            market_cap=MarketCap.from_trillion(400),
            change_ratio=ChangeRatio(2.5)
        )
        
        theme.add_stock(stock)
        
        assert theme.stock_count == 1
        assert stock in theme.stocks
        assert stock.theme == theme
    
    def test_remove_stock_from_theme(self):
        """테마에서 종목 제거"""
        theme = Theme(name="반도체")
        stock = Stock(
            code="005930",
            name="삼성전자",
            market_cap=MarketCap.from_trillion(400),
            change_ratio=ChangeRatio(2.5)
        )
        
        theme.add_stock(stock)
        theme.remove_stock(stock)
        
        assert theme.stock_count == 0
        assert stock not in theme.stocks
        assert stock.theme is None
    
    def test_total_market_cap(self):
        """테마 총 시가총액 계산"""
        theme = Theme(name="반도체")
        
        stock1 = Stock(
            code="005930",
            name="삼성전자",
            market_cap=MarketCap.from_trillion(400),
            change_ratio=ChangeRatio(2.5)
        )
        stock2 = Stock(
            code="000660",
            name="SK하이닉스",
            market_cap=MarketCap.from_trillion(100),
            change_ratio=ChangeRatio(1.5)
        )
        
        theme.add_stock(stock1)
        theme.add_stock(stock2)
        
        assert theme.total_market_cap.in_trillion == 500.0
    
    def test_weighted_change_ratio(self):
        """테마 가중 평균 등락률 계산"""
        theme = Theme(name="반도체")
        
        # 삼성전자: 400조, +2%
        stock1 = Stock(
            code="005930",
            name="삼성전자",
            market_cap=MarketCap.from_trillion(400),
            change_ratio=ChangeRatio(2.0)
        )
        # SK하이닉스: 100조, +4%
        stock2 = Stock(
            code="000660",
            name="SK하이닉스",
            market_cap=MarketCap.from_trillion(100),
            change_ratio=ChangeRatio(4.0)
        )
        
        theme.add_stock(stock1)
        theme.add_stock(stock2)
        
        # 가중 평균 = (400*2 + 100*4) / 500 = 1200 / 500 = 2.4%
        assert theme.weighted_change_ratio == pytest.approx(2.4, rel=0.01)


class TestThemeGroup:
    """ThemeGroup 데이터 클래스 테스트"""
    
    def test_create_theme_group(self):
        """테마 그룹 생성"""
        group = ThemeGroup(
            name="2차전지",
            market_cap=MarketCap.from_trillion(50),
            change_sum=150.0
        )
        
        assert group.name == "2차전지"
        assert group.market_cap.in_trillion == 50.0
        assert group.weighted_change_ratio == pytest.approx(3.0, rel=0.01)  # 150/50
