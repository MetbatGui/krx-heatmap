"""
Domain Models (Entities)

엔티티는 식별자를 가지며 생명주기 동안 추적됩니다.
"""
from dataclasses import dataclass, field
from typing import Optional, List
from .value_objects import MarketCap, ChangeRatio


@dataclass
class Stock:
    """주식 종목 엔티티
    
    종목 코드로 식별되는 엔티티입니다.
    """
    code: str  # 식별자
    name: str
    market_cap: MarketCap
    change_ratio: ChangeRatio
    theme: Optional['Theme'] = None
    
    def __post_init__(self):
        if not self.code:
            raise ValueError("종목 코드는 필수입니다")
        if not self.name:
            raise ValueError("종목명은 필수입니다")
    
    @property
    def market_cap_trillion(self) -> float:
        """시가총액 (조 단위) - 하위 호환성 유지"""
        return self.market_cap.in_trillion
    
    def weighted_change(self) -> float:
        """시가총액으로 가중된 등락률"""
        return self.change_ratio.weighted_by(self.market_cap)


@dataclass
class Theme:
    """테마 엔티티
    
    테마명으로 식별되며 여러 종목을 포함합니다.
    """
    name: str  # 식별자
    stocks: List[Stock] = field(default_factory=list)
    parent_group: Optional[str] = None
    
    def __post_init__(self):
        if not self.name:
            raise ValueError("테마명은 필수입니다")
    
    def add_stock(self, stock: Stock) -> None:
        """종목 추가"""
        if stock not in self.stocks:
            self.stocks.append(stock)
            stock.theme = self
    
    def remove_stock(self, stock: Stock) -> None:
        """종목 제거"""
        if stock in self.stocks:
            self.stocks.remove(stock)
            stock.theme = None
    
    @property
    def total_market_cap(self) -> MarketCap:
        """테마 내 총 시가총액"""
        if not self.stocks:
            return MarketCap.zero()
        
        total = MarketCap.zero()
        for stock in self.stocks:
            total = total + stock.market_cap
        return total
    
    @property
    def weighted_change_ratio(self) -> float:
        """가중 평균 등락률
        
        시가총액으로 가중 평균한 테마의 등락률을 계산합니다.
        """
        if not self.stocks:
            return 0.0
        
        total_cap = self.total_market_cap
        if total_cap.value_in_won == 0:
            return 0.0
        
        weighted_sum = sum(stock.weighted_change() for stock in self.stocks)
        return weighted_sum / total_cap.in_trillion
    
    @property
    def stock_count(self) -> int:
        """종목 개수"""
        return len(self.stocks)


@dataclass
class ThemeGroup:
    """테마 그룹 데이터 클래스 (집계용)
    
    여러 테마를 그룹화한 통계 정보를 저장합니다.
    """
    name: str
    market_cap: MarketCap
    change_sum: float  # 가중 평균 계산용 (등락률 * 시가총액) 합계
    
    @property
    def weighted_change_ratio(self) -> float:
        """가중 평균 등락률"""
        if self.market_cap.value_in_won == 0:
            return 0.0
        return self.change_sum / self.market_cap.in_trillion

