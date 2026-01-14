import pandas as pd
import os

class ThemeFileRepository:
    """테마 파일 저장소"""
    
    def __init__(self, file_path: str = 'data/theme_data/unique_theme_heatmap_data.xlsx'):
        self.file_path = file_path

    def load_themes(self) -> pd.DataFrame:
        """엑셀 파일에서 테마 데이터를 읽어와 (테마, 종목명) 형태의 DataFrame으로 변환합니다."""
        if not os.path.exists(self.file_path):
            print(f"오류: {self.file_path} 파일이 없습니다.")
            return pd.DataFrame()

        try:
            # sheet_name='테마상세' 로드 (Wide Format: Columns=Themes, Values=Stocks)
            df_wide = pd.read_excel(self.file_path, sheet_name='테마상세')
            
            # Melt / Unpivot to Long Format
            long_data = []
            for col in df_wide.columns:
                theme_name = str(col).strip()
                # 해당 테마의 종목 리스트 (NaN 제외)
                stocks = df_wide[col].dropna().astype(str).tolist()
                
                for stock in stocks:
                    long_data.append({
                        '테마': theme_name,
                        '종목명': stock.strip()
                    })
            
            df_long = pd.DataFrame(long_data, columns=['테마', '종목명'])
            
            print(f"테마 데이터 로딩 및 변환 완료: {len(df_long)}개 항목 (Unique 종목 {df_long['종목명'].nunique()}개)")
            return df_long
            
        except Exception as e:
            print(f"테마 파일 읽기 실패: {e}")
            import traceback
            traceback.print_exc()
            return pd.DataFrame()
