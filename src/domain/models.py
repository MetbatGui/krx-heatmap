from dataclasses import dataclass
from typing import Optional

@dataclass
class Stock:
    """주식 종목 데이터 클래스"""
    code: str
    name: str
    market_cap: float  # 원 단위
    changes_ratio: float  # 퍼센트 (예: 2.5)
    theme: Optional[str] = None

    @property
    def market_cap_trillion(self) -> float:
        """시가총액 (조 단위)"""
        return self.market_cap / 1_000_000_000_000 if self.market_cap else 0

@dataclass
class ThemeGroup:
    """테마 그룹 데이터 클래스 (중간 그룹 노드용)"""
    name: str
    market_cap: float
    change_sum: float  # 가중 평균 계산용 (등락률 * 시가총액) 합계

    @property
    def weighted_change_ratio(self) -> float:
        """가중 평균 등락률"""
        return self.change_sum / self.market_cap if self.market_cap > 0 else 0
