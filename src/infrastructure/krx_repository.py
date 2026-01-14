import FinanceDataReader as fdr
import pandas as pd

class KrxRepository:
    """KRX 데이터 저장소"""
    
    def fetch_listing(self) -> pd.DataFrame:
        """KRX 전체 종목 데이터를 가져옵니다."""
        print("KRX 데이터 로딩 중...")
        try:
            df = fdr.StockListing('KRX')
            print(f"KRX 종목 수: {len(df)}")
            return df
        except Exception as e:
            print(f"KRX 데이터 로딩 실패: {e}")
            return pd.DataFrame()
