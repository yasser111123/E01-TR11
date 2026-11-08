import streamlit as st
import pandas as pd
import re

st.set_page_config(
    page_title="Harness Splices Dashboard & Gamme Finder",
    page_icon="⚡",
    layout="wide"
)

@st.cache_data
def load_and_parse_excel(file_path):
    """
    Parses all numeric sheets from the Excel workbook to extract:
    - E-Code (e.g. E01)
    - Version number (e.g. 1, 2, 3...)
    - List of references (e.g. 240130122S--A)
    """
    xls = pd.ExcelFile(file_path)
    records = []
    
    for sheet_name in xls.sheet_names:
        # Process only numbered sheets (e.g., '1', '2', '3'...)
        if not sheet_name.isdigit():
            continue
            
        df = pd.read_excel(xls, sheet_name=sheet_name, header=None)
        
        # 1. Extract E-code (usually in row index 0)
        e_code = None
        for val in df.iloc[0].dropna():
            val_str = str(val).strip()
            if re.match(r'^E\d+$', val_str, re.IGNORECASE):
                e_code = val_str.upper()
                break
        
        # Fallback search in first 3 rows if not found on index 0
        if not e_code:
            for r in range(min(3, len(df))):
                for val in df.iloc[r].dropna():
                    val_str = str(val).strip()
                    if re.match(r'^E\d+$', val_str, re.IGNORECASE):
                        e_code = val_str.upper()
                        break
                if e_code:
                    break
        
        if not e_code:
            e_code = "E01" # Default fallback
            
        # 2. Extract Version Number (Sheet name or cell under E-code)
        version = sheet_name.strip()
        
        # 3. Extract References (Look for codes starting with 24013...)
        references = []
        for r in range(min(20, len(df))):
            for val in df.iloc[r].dropna():
                val_str = str(val).strip()
                if val_str.startswith("24013"):
                    references.append(val_str)
        
        # Remove duplicates while preserving order
        references = list(dict.fromkeys(references))
        
        for ref in references:
            records.append({
                "Reference": ref,
                "E_Code": e_code,
                "Version": version,
                "Sheet": sheet_name
            })
            
    return pd.DataFrame(records)

# File path settings
EXCEL_FILE = "DG.TR11.  Splices_X1310_HARN DASHBOARD DG.xlsx"

st.title("⚡ Dashboard DG & Gamme Database Finder")
st.markdown("Recherche rapide des Références, Versions et E-Codes")

try:
    df_data = load_and_parse_excel(EXCEL_FILE)
    st.sidebar.success(f"✅ Excel chargé avec succès! ({len(df_data)} références trouvées)")
except Exception as e:
    st.error(f"Erreur lors du chargement du fichier Excel: {e}")
    st.stop()

# --- Search Interface ---
search_query = st.text_input("🔍 Entrez le code ou la référence (ex: 3200, 240133200S--A, ou E01):", "")

if search_query:
    query = search_query.strip().upper()
    
    # Filter dataset based on partial match in Reference, E_Code, or Version
    filtered_df = df_data[
        df_data['Reference'].str.upper().str.contains(query) |
        df_data['E_Code'].str.upper().str.contains(query) |
        (df_data['Version'] == query)
    ]
    
    if not filtered_df.empty:
        st.subheader(f"Résultats pour : `{search_query}`")
        
        # Display summary metrics
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Matchs", len(filtered_df))
        col2.metric("Versions concernées", ", ".join(filtered_df['Version'].unique()))
        col3.metric("E-Codes concernés", ", ".join(filtered_df['E_Code'].unique()))
        
        # Results Table
        st.dataframe(filtered_df, use_container_width=True)
    else:
        st.warning(f"Aucun résultat trouvé pour `{search_query}`.")

else:
    # Display full dataset by default
    st.subheader("📋 Liste Complète des Versions et Références")
    st.dataframe(df_data, use_container_width=True)