import streamlit as st
from utils.loader import load_uploaded_or_folder_csvs, load_category_data
from utils.parser import parse_csv_files, preprocess_data, apply_filters
from utils.visualizer import render_overview_tab, render_top_tab, render_time_tab
from utils.exporter import render_download_tab
from utils.ingredient_calculator import calculate_ingredient_usage, render_ingredient_tab


st.set_page_config(page_title="Vending Machine Dashboard", layout="wide")
st.title("🥤 Vending Machine Sales Dashboard")

# 1. 파일 로드
uploaded_files = st.file_uploader("📂 자판기 CSV 업로드", type="csv", accept_multiple_files=True)
files = load_uploaded_or_folder_csvs(uploaded_files)

# 2. 카테고리 불러오기
category_df = load_category_data()

# 3. CSV 파싱 및 병합
if files:
    raw_df = parse_csv_files(files)
    if not raw_df.empty:
        df = preprocess_data(raw_df, category_df)

        # 필터링
        selected_month, selected_machine, filtered = apply_filters(df)

        # 탭 구성
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["개요", "Top10/카테고리", "시간대 분석", "원재료 사용량", "데이터 다운로드"])

        with tab1:
            render_overview_tab(filtered, df)

        with tab2:
            render_top_tab(filtered)

        with tab3:
            render_time_tab(filtered)

        with tab4:
            ingredient_df = calculate_ingredient_usage(df, recipe_folder="recipe")
            if not ingredient_df.empty:
                render_ingredient_tab(ingredient_df, selected_machine)  # ✅ 자판기 이름 넘겨줌
            else:
                st.warning("❗ 원재료 데이터를 계산할 수 없습니다.")

        with tab5:
            render_download_tab(df)

    else:
        st.warning("❗ CSV 내용이 비어있습니다.")
else:
    st.info("💡 CSV 파일을 업로드하거나, 저장소의 data 폴더에 파일을 넣어주세요.\n예: A_sales_007.csv")
