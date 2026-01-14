import sys
import os

# src 디렉토리를 경로에 추가하여 모듈 import 가능하게 함
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from application.heatmap_service import HeatmapService
from presentation.visualizer import HeatmapVisualizer

def main():
    try:
        # 1. 서비스 초기화 및 데이터 로드
        service = HeatmapService()
        df_final = service.get_heatmap_data()
        
        if df_final.empty:
            print("히트맵 데이터를 가져오지 못했습니다.")
            return
            
        print(f"히트맵 생성 대상 종목 수: {len(df_final)}")
        
        # 2. 그룹 통계 계산 (중간 노드용)
        group_stats = service.calculate_group_stats(df_final)
        
        # 3. 시각화 생성
        visualizer = HeatmapVisualizer()
        visualizer.create_treemap(df_final, group_stats)
        
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
