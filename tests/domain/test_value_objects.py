"""
Value Objects 단위 테스트
"""
import pytest
from src.domain.value_objects import MarketCap, ChangeRatio


class TestMarketCap:
    """MarketCap Value Object 테스트"""
    
    def test_create_market_cap(self):
        """시가총액 생성 테스트"""
        mc = MarketCap(1_000_000_000_000)  # 1조
        assert mc.value_in_won == 1_000_000_000_000
        assert mc.in_trillion == 1.0
        assert mc.in_billion == 10_000.0
    
    def test_negative_market_cap_raises_error(self):
        """음수 시가총액은 에러 발생"""
        with pytest.raises(ValueError, match="시가총액은 음수일 수 없습니다"):
            MarketCap(-1000)
    
    def test_market_cap_addition(self):
        """시가총액 덧셈 테스트"""
        mc1 = MarketCap(1_000_000_000_000)  # 1조
        mc2 = MarketCap(500_000_000_000)   # 0.5조
        result = mc1 + mc2
        
        assert result.in_trillion == 1.5
    
    def test_market_cap_multiplication(self):
        """시가총액 곱셈 테스트"""
        mc = MarketCap(1_000_000_000_000)  # 1조
        result = mc * 2
        
        assert result.in_trillion == 2.0
    
    def test_market_cap_comparison(self):
        """시가총액 비교 테스트"""
        mc1 = MarketCap(1_000_000_000_000)  # 1조
        mc2 = MarketCap(2_000_000_000_000)  # 2조
        
        assert mc2 > mc1
        assert mc1 < mc2
    
    def test_from_trillion(self):
        """조 단위로부터 생성"""
        mc = MarketCap.from_trillion(5.0)
        assert mc.in_trillion == 5.0
        assert mc.value_in_won == 5_000_000_000_000
    
    def test_zero(self):
        """0원 시가총액"""
        mc = MarketCap.zero()
        assert mc.value_in_won == 0
        assert mc.in_trillion == 0


class TestChangeRatio:
    """ChangeRatio Value Object 테스트"""
    
    def test_create_change_ratio(self):
        """등락률 생성 테스트"""
        cr = ChangeRatio(2.5)
        assert cr.value == 2.5
    
    def test_invalid_change_ratio_raises_error(self):
        """비정상적인 등락률은 에러 발생"""
        with pytest.raises(ValueError, match="등락률이 비정상적입니다"):
            ChangeRatio(150.0)  # ±100% 초과
    
    def test_weighted_by_market_cap(self):
        """시가총액으로 가중된 등락률"""
        cr = ChangeRatio(2.0)  # 2%
        mc = MarketCap(1_000_000_000_000)  # 1조
        
        weighted = cr.weighted_by(mc)
        assert weighted == 2.0  # 2% * 1조 = 2.0
    
    def test_change_ratio_properties(self):
        """등락률 속성 테스트"""
        positive = ChangeRatio(1.5)
        negative = ChangeRatio(-1.5)
        neutral = ChangeRatio(0.0)
        
        assert positive.is_positive
        assert not positive.is_negative
        assert not positive.is_neutral
        
        assert negative.is_negative
        assert not negative.is_positive
        
        assert neutral.is_neutral
        assert not neutral.is_positive
        assert not neutral.is_negative
    
    def test_zero(self):
        """보합 등락률"""
        cr = ChangeRatio.zero()
        assert cr.value == 0.0
        assert cr.is_neutral
