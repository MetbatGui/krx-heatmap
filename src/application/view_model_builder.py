"""
Application Layer - ViewModel 변환기

Domain Model을 Presentation ViewModel로 변환하는 로직입니다.
"""
from typing import List, Dict
from domain.models import Theme, ThemeGroup
from presentation.view_models import HeatmapViewModel, TreemapNode


class HeatmapViewModelBuilder:
    """히트맵 ViewModel 생성기
    
    Domain Model을 Presentation 레이어의 ViewModel로 변환합니다.
    """
    
    @staticmethod
    def build(themes: List[Theme], group_stats: Dict[str, ThemeGroup]) -> HeatmapViewModel:
        """Domain Model로부터 HeatmapViewModel을 생성합니다.
        
        Args:
            themes: 테마 목록
            group_stats: 그룹 통계
            
        Returns:
            HeatmapViewModel
        """
        nodes: List[TreemapNode] = []
        root_id = "KRX_Themes"
        
        # 1. Root 노드
        total_mkt_cap = sum(theme.total_market_cap.in_trillion for theme in themes)
        
        if total_mkt_cap > 0:
            weighted_sum = sum(
                stock.weighted_change() 
                for theme in themes 
                for stock in theme.stocks
            )
            total_change = weighted_sum / total_mkt_cap
        else:
            total_change = 0.0
        
        nodes.append(TreemapNode(
            id=root_id,
            label="대한민국 테마별 증시",
            parent_id="",
            value=total_mkt_cap,
            color=total_change,
            custom_data=total_change,
            text_template="<b>%{label}</b>"
        ))
        
        # 2. 그룹 노드 (중간 계층)
        for group_name, group in group_stats.items():
            group_id = f"Group_{group_name}"
            
            nodes.append(TreemapNode(
                id=group_id,
                label=group_name,
                parent_id=root_id,
                value=group.market_cap.in_trillion,
                color=group.weighted_change_ratio,
                custom_data=group.weighted_change_ratio,
                text_template="<b>%{label}</b>"
            ))
        
        # 3. 테마 노드
        for theme in themes:
            parent_id = f"Group_{theme.parent_group}" if theme.parent_group else root_id
            theme_id = f"Theme_{theme.name}"
            
            nodes.append(TreemapNode(
                id=theme_id,
                label=theme.name,
                parent_id=parent_id,
                value=theme.total_market_cap.in_trillion,
                color=theme.weighted_change_ratio,
                custom_data=theme.weighted_change_ratio,
                text_template="<b>%{label}</b>"
            ))
        
        # 4. 종목 노드 (Leaf)
        for theme in themes:
            theme_id = f"Theme_{theme.name}"
            
            for stock in theme.stocks:
                stock_id = f"{theme.name}_{stock.name}"
                
                nodes.append(TreemapNode(
                    id=stock_id,
                    label=stock.name,
                    parent_id=theme_id,
                    value=stock.market_cap.in_trillion,
                    color=stock.change_ratio.value,
                    custom_data=stock.change_ratio.value,
                    text_template="<b>%{label}</b><br>%{value:.2f}조<br>%{customdata:.2f}%"
                ))
        
        return HeatmapViewModel(nodes=nodes)
