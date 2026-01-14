import sys
import os

# 프로젝트 루트를 경로에 추가
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.join(project_root, 'src'))

from application.heatmap_service import HeatmapService
from application.view_model_builder import HeatmapViewModelBuilder
from presentation.visualizer import HeatmapVisualizer

def main():
    try:
        # 1. 서비스 초기화 및 데이터 로드
        service = HeatmapService()
        
        # Domain Model 사용 (새로운 방식)
        themes = service.get_themes()
        
        if not themes:
            print("히트맵 데이터를 가져오지 못했습니다.")
            return
            
        print(f"히트맵 생성 대상 종목 수: {sum(theme.stock_count for theme in themes)}")
        
        # 2. 그룹 통계 계산
        group_stats = service.get_group_stats_models(themes)
        
        # 3. ViewModel 생성
        view_model = HeatmapViewModelBuilder.build(themes, group_stats)
        
        # 4. 시각화 생성 (현재 디렉토리에 저장)
        output_file = os.path.join(os.path.dirname(__file__), 'theme_heatmap.html')
        visualizer = HeatmapVisualizer()
        visualizer.create_treemap_from_viewmodel(view_model, output_file)
        
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

