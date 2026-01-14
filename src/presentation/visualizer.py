import plotly.graph_objects as go
import pandas as pd
import os
from domain.theme_config import THEME_HIERARCHY

class HeatmapVisualizer:
    """히트맵 시각화 클래스"""
    
    def create_treemap(self, df_final: pd.DataFrame, group_stats: dict, output_file: str = 'theme_heatmap.html'):
        """데이터프레임을 기반으로 Plotly Treemap을 생성하고 저장합니다."""
        
        ids = []
        labels = []
        parents = []
        values = []
        colors = []
        custom_data = []
        text_templates = []
        
        root_id = "KRX_Themes"
        root_label = "대한민국 테마별 증시"
        
        # 1. Root 노드
        ids.append(root_id)
        labels.append(root_label)
        parents.append("")
        
        total_mkt_cap = df_final['시가총액_조'].sum()
        total_change = (df_final['ChagesRatio'] * df_final['시가총액_조']).sum() / total_mkt_cap if total_mkt_cap > 0 else 0
        
        values.append(total_mkt_cap)
        colors.append(total_change)
        custom_data.append(total_change)
        text_templates.append("<b>%{label}</b>")
        
        # 2. 테마(Branch) 노드
        theme_groups = df_final.groupby('테마')
        
        for theme_name, group in theme_groups:
            parent_group = THEME_HIERARCHY.get(theme_name)
            
            theme_mkt_cap = group['시가총액_조'].sum()
            theme_change_sum = (group['ChagesRatio'] * group['시가총액_조']).sum()
            theme_change = theme_change_sum / theme_mkt_cap if theme_mkt_cap > 0 else 0
            
            if parent_group:
                parent_id = f"Group_{parent_group}"
            else:
                parent_id = root_id
                
            theme_id = f"Theme_{theme_name}"
            
            ids.append(theme_id)
            labels.append(theme_name)
            parents.append(parent_id)
            values.append(theme_mkt_cap)
            colors.append(theme_change)
            custom_data.append(theme_change)
            text_templates.append("<b>%{label}</b>")
            
        # 3. 중간 그룹 노드 (예: '2차전지')
        for group_name, stats in group_stats.items():
            group_id = f"Group_{group_name}"
            
            group_cap = stats['cap']
            group_change = stats['change_sum'] / group_cap if group_cap > 0 else 0
                
            ids.append(group_id)
            labels.append(group_name)
            parents.append(root_id)
            values.append(group_cap)
            colors.append(group_change)
            custom_data.append(group_change)
            text_templates.append("<b>%{label}</b>")
            
        # 4. 종목(Leaf) 노드
        for _, row in df_final.iterrows():
            stock_name = row['종목명']
            theme_name = row['테마']
            
            stock_id = f"{theme_name}_{stock_name}"
            parent_id = f"Theme_{theme_name}"
            
            ids.append(stock_id)
            labels.append(stock_name)
            parents.append(parent_id)
            values.append(row['시가총액_조'])
            colors.append(row['ChagesRatio'])
            custom_data.append(row['ChagesRatio'])
            text_templates.append("<b>%{label}</b><br>%{value:.2f}조<br>%{customdata:.2f}%")
            
        # 5. 시각화 생성
        custom_colorscale = [
            [0.0, 'blue'],
            [0.5, '#444444'],
            [1.0, 'red']
        ]
        
        fig = go.Figure(go.Treemap(
            ids=ids,
            labels=labels,
            parents=parents,
            values=values,
            branchvalues='total',
            maxdepth=2,
            marker=dict(
                colors=colors,
                colorscale=custom_colorscale,
                cmid=0,
                cmin=-5,
                cmax=5,
                colorbar=dict(title="등락률(%)")
            ),
            customdata=custom_data,
            texttemplate=text_templates,
            hovertemplate='<b>%{label}</b><br>시가총액: %{value:.2f}조 원<br>등락률: %{customdata:.2f}%<extra></extra>',
            textposition='middle center'
        ))
        
        fig.update_layout(
            title='대한민국 테마별 증시 히트맵',
            margin=dict(t=50, l=10, r=10, b=10),
            font=dict(family="Malgun Gothic", size=15)
        )
        
        fig.write_html(output_file)
        print(f"\n히트맵 생성 완료: {output_file}")
        
        # 브라우저 자동 실행
        try:
            os.startfile(output_file)
        except AttributeError:
            import webbrowser
            webbrowser.open(output_file)
