
import FinanceDataReader as fdr
import pandas as pd
import plotly.express as px

# -----------------------------------------------------------------------------
# 1. KRX Data Fetching & Preparation
# -----------------------------------------------------------------------------

print("Fetching KRX listing data...")
try:
    # Fetch KRX stocks (Price/Marcap data)
    df_price = fdr.StockListing('KRX')
    print(f"Fetched {len(df_price)} price records.")

    # Fetch KRX Sector data
    df_desc = fdr.StockListing('KRX-DESC')
    print(f"Fetched {len(df_desc)} sector records.")

    # Merge on Code
    df = pd.merge(df_price, df_desc[['Code', 'Sector']], on='Code', how='left')

    # Fill missing Sector
    df['Sector'] = df['Sector'].fillna('기타')

    # Filter valid Sector (if we want to exclude '기타', or keep it)
    # For top stocks, usually they have sectors.
    
    # Sort by Market Cap (Marcap) descending
    if 'Marcap' in df.columns:
        df = df.sort_values(by='Marcap', ascending=False)
    
    # Take Top 100 stocks for the heatmap
    TOP_N = 100
    df = df.head(TOP_N).copy()

    # Define Sector Mapping to User Themes (Natural Korean Names)
    def map_sector_to_theme(sector):
        if pd.isna(sector): return "기타"
        
        # Keyword-based mapping
        # Samsung(통신 및 방송 장비), LG(가정용 기기), Hynix(반도체)
        # Added '통신', '가정용 기기', '디스플레이' to catch Samsung/LG correctly as IT
        if any(x in sector for x in ['반도체', '전기전자', 'IT부품', '통신장비', '휴대폰', '전자', '통신', '가정용 기기', '디스플레이']): return "IT/반도체"
        
        # Naver/Kakao(서비스업 - often), but let's catch keywords if possible, or broad '서비스업' with checks
        if any(x in sector for x in ['소프트웨어', '인터넷', '게임', 'IT서비스', '컴퓨터', '포털']): return "플랫폼/소프트웨어"
        
        if any(x in sector for x in ['은행', '증권', '보험', '금융', '투자']): return "금융"
        if any(x in sector for x in ['의료', '바이오', '생명', '제약', '의약품']): return "바이오/헬스케어"
        
        # Defense/Aerospace (Requested by user) - Priority over general machinery
        if any(x in sector for x in ['항공', '방산', '우주', '무기', '미사일']): return "방산/항공우주"
        
        # Heavy Industry
        if any(x in sector for x in ['기계', '조선', '건설', '전기장비', '중공업']): return "중공업/기계/건설"
        
        # Chemicals/Materials (POSCO is 철강금속)
        if any(x in sector for x in ['화학', '철강', '금속', '제지', '비철', '소재']): return "화학/소재"
        
        # Consumer
        if any(x in sector for x in ['식음료', '음식료', '생활', '화장품', '담배']): return "음식료/화장품"
        if any(x in sector for x in ['자동차', '부품', '가전', '섬유', '의복']): return "자동차/가전"
        
        # Energy/Utility
        if any(x in sector for x in ['에너지', '석유']): return "에너지"
        if any(x in sector for x in ['전력', '가스', '유틸리티']): return "유틸리티"
        
        # Services
        if any(x in sector for x in ['운송', '해운', '물류', '창고']): return "운송/물류"
        # '방송' is here, but Samsung uses '통신' which is caught above.
        if any(x in sector for x in ['호텔', '레저', '미디어', '엔터', '방송', '교육', '여행', '콘텐츠']): return "레저/엔터"
        if any(x in sector for x in ['유통', '백화점', '소매', '판매', '상업']): return "유통"
        
        # Generic Services/Holding often fall here
        if any(x in sector for x in ['무역', '상사', '서비스', '지주', '기타금융']): return "상사/지주사"
        
        return "기타" # Fallback

    # Apply Mapping
    df['Theme'] = df['Sector'].apply(map_sector_to_theme)
    
    # Normalize Data for Visualization (Rename to Korean)
    # Market Cap: Convert to Trillion KRW for readability
    df['Marcap'] = df['Marcap'].fillna(0)
    df['시가총액'] = df['Marcap'] / 1_000_000_000_000
    df['등락률'] = df['ChagesRatio'].fillna(0)
    df['종목명'] = df['Name']
    df['섹터'] = df['Theme'] # Use refined Theme as '섹터' for display 
    
    # Prepare final columns
    heatmap_data = df[['섹터', '종목명', '시가총액', '등락률']].copy()
    
    # Label에는 상세 정보(시가총액, 등락률)만 포함합니다. 종목명은 자동으로 표시됩니다.
    heatmap_data['Label'] = heatmap_data.apply(
        lambda x: f"<span style='font-size:0.8em'>{x['시가총액']:.2f}조</span><br><span style='font-size:0.8em'>{x['등락률']}%</span>", axis=1
    )

    print(f"Prepared top {len(heatmap_data)} stocks for heatmap.")

except Exception as e:
    print(f"Error fetching/processing data: {e}")
    # Fallback or Exit? For now, we exit to show the error.
    exit(1)

# -----------------------------------------------------------------------------
# 2. Create Treemap (Heatmap)
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# 2. Create Treemap (Heatmap) using graph_objects
# -----------------------------------------------------------------------------
import plotly.graph_objects as go

# 데이터 전처리: 계층 구조 직접 생성 (상위 노드 값 계산을 위함)
ids = []
labels = []
parents = []
values = []
colors = []
custom_data = [] # 타일 텍스트 표시용 데이터 (등락률)

# 1. Root Node (전체 시장)
root_id = "KRX_ROOT"
root_label = "대한민국 증시 (KRX Top 100)"
ids.append(root_id)
labels.append(root_label)
parents.append("")
# Root 값 집계
total_mkt_cap = heatmap_data['시가총액'].sum()
# 가중 평균 등락률 = Sum(등락률 * 시가총액) / Sum(시가총액)
total_weighted_change = (heatmap_data['등락률'] * heatmap_data['시가총액']).sum() / total_mkt_cap if total_mkt_cap else 0

values.append(total_mkt_cap)
colors.append(total_weighted_change)
custom_data.append(total_weighted_change)

# 2. Sector Nodes (섹터)
# 각 섹터별로 그룹화하여 집계
sector_group = heatmap_data.groupby('섹터').apply(
    lambda x: pd.Series({
        'mkt_cap_sum': x['시가총액'].sum(),
        'weighted_change': (x['등락률'] * x['시가총액']).sum() / x['시가총액'].sum() if x['시가총액'].sum() > 0 else 0
    })
)

for sector_name, row in sector_group.iterrows():
    sector_id = f"SECTOR_{sector_name}"
    ids.append(sector_id)
    labels.append(sector_name)
    parents.append(root_id)
    values.append(row['mkt_cap_sum'])
    colors.append(row['weighted_change'])
    custom_data.append(row['weighted_change'])

# 3. Leaf Nodes (개별 종목)
# 종목명 중복 방지를 위해 ID에 섹터나 코드를 결합하는 것이 안전하지만, 
# 여기서는 시각화 라벨(labels)과 고유 ID(ids)를 분리하여 처리
for i, row in heatmap_data.iterrows():
    # ID: 유니크해야 함 (섹터_종목명)
    stock_id = f"{row['섹터']}_{row['종목명']}"
    ids.append(stock_id)
    labels.append(row['종목명'])
    # 부모는 해당 섹터의 ID
    parents.append(f"SECTOR_{row['섹터']}")
    values.append(row['시가총액'])
    colors.append(row['등락률'])
    custom_data.append(row['등락률'])

# 사용자 정의 컬러 스케일
custom_colorscale = [
    [0.0, 'blue'],       # 하락
    [0.5, '#444444'],    # 보합
    [1.0, 'red']         # 상승
]

fig = go.Figure(go.Treemap(
    ids=ids,
    labels=labels,
    parents=parents,
    values=values,
    marker=dict(
        colors=colors,
        colorscale=custom_colorscale,
        cmid=0,
        cmin=-5,
        cmax=5,
        colorbar=dict(title="등락률(%)")
    ),
    branchvalues="total", # 부모 값은 자식 값의 합과 일치해야 함 (직접 계산했으므로 사용 가능)
    customdata=custom_data,
    # texttemplate: 화면에 보여줄 텍스트 포맷 (customdata를 사용하여 명시적으로 값 표시)
    texttemplate="<b>%{label}</b><br>%{value:.2f}조<br>%{customdata:.2f}%",
    hovertemplate='<b>%{label}</b><br>시가총액: %{value:.2f}조 원<br>등락률: %{customdata:.2f}%<extra></extra>',
    textposition='middle center',
    maxdepth=2
))

fig.update_layout(
    title='대한민국 증시 히트맵 (시가총액 상위 100)',
    margin=dict(t=50, l=25, r=25, b=25),
    font=dict(size=20, family="Malgun Gothic, AppleSDGothicNeo, sans-serif")
)

# -----------------------------------------------------------------------------
# 3. Output
# -----------------------------------------------------------------------------
output_file = "heatmap.html"
fig.write_html(output_file)
print(f"Successfully generated {output_file}")

# Automatically open in browser
try:
    fig.show()
except Exception:
    pass
