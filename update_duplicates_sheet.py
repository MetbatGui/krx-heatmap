import pandas as pd
import unicodedata

def normalize_str(s):
    if pd.isna(s) or str(s).lower() == 'nan':
        return None
    val = str(s).strip()
    if not val:
        return None
    return unicodedata.normalize('NFC', val)

def update_duplicates_sheet():
    file_path = 'data/theme_data/unique_theme_heatmap_data.xlsx'
    print(f"Loading {file_path}...")
    
    try:
        xl = pd.ExcelFile(file_path)
        # Load all sheets to preserve them
        sheet_dict = {sn: pd.read_excel(xl, sn) for sn in xl.sheet_names}
        df_detail = sheet_dict.get('테마상세')
        
        if df_detail is None:
            print("Error: '테마상세' sheet not found.")
            return

        print("Scanning for duplicates...")
        stock_themes = {}
        for col in df_detail.columns:
            theme = normalize_str(col)
            stocks = df_detail[col].dropna().apply(normalize_str).unique()
            for s in stocks:
                if s not in stock_themes: stock_themes[s] = []
                stock_themes[s].append(theme)
        
        # Filter strictly > 1
        duplicates_data = []
        max_themes = 0
        
        for stock, themes in stock_themes.items():
            if len(themes) > 1:
                themes.sort()
                row = {'종목명': stock}
                for i, t in enumerate(themes):
                    row[f'테마{i+1}'] = t
                duplicates_data.append(row)
                max_themes = max(max_themes, len(themes))
                
        print(f"Found {len(duplicates_data)} remaining duplicates.")
        
        # Create new DataFrame
        new_columns = ['종목명'] + [f'테마{i+1}' for i in range(max_themes)]
        df_new_duplicates = pd.DataFrame(duplicates_data, columns=new_columns)
        
        # Update the dictionary
        sheet_dict['중복종목'] = df_new_duplicates
        
        # Save back
        print("Saving updated file...")
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            for sheet_name, df in sheet_dict.items():
                df.to_excel(writer, sheet_name=sheet_name, index=False)
                
        print("Done. '중복종목' sheet has been refreshed.")
        
    except Exception as e:
        print(f"Error updating file: {e}")

if __name__ == "__main__":
    update_duplicates_sheet()
