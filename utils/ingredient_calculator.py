import pandas as pd
from io import BytesIO
import streamlit as st
import re

# Constants
POWDER_GRAMS_PER_SECOND = 6.4
SYRUP_GRAMS_PER_SECOND = 3.4

POWDER_TYPES = ["밀크 파우더", "바닐라 파우더", "초코 파우더", "토피넛 파우더", "청귤 파우더", "녹차 파우더"]
SYRUP_TYPES = ["레몬 시럽", "메론 시럽", "복숭아 시럽", "청포도 시럽", "패션후르츠 시럽", "얼그레이레몬 하이볼 시럽"]

# 이름 정규화 함수 (좀 더 강력하게 개선)
def normalize_name(name):
    name = str(name).strip().lower()
    name = re.sub(r"(hot|ice)[ ]?", "", name)  # hot/ice 제거
    name = re.sub(r"[ \-\(\)\[\]\+]", "", name)  # 공백, 특수문자 제거
    return name


# 재료 분해 함수
def extract_powder_syrup_usage(ingredients, powder_total, syrup_total):
    powder_result = {p: 0.0 for p in POWDER_TYPES}
    syrup_result = {s: 0.0 for s in SYRUP_TYPES}

    if not isinstance(ingredients, str) or ingredients.strip() == "":
        return powder_result, syrup_result

    ingredient_list = [normalize_name(x) for x in ingredients.split(",")]

    powder_norm = [normalize_name(p) for p in POWDER_TYPES]
    syrup_norm = [normalize_name(s) for s in SYRUP_TYPES]

    used_powders = [p for p, pn in zip(POWDER_TYPES, powder_norm) if pn in ingredient_list]
    used_syrups = [s for s, sn in zip(SYRUP_TYPES, syrup_norm) if sn in ingredient_list]

    if used_powders and powder_total > 0:
        share = powder_total / len(used_powders)
        for p in used_powders:
            powder_result[p] = share

    if used_syrups and syrup_total > 0:
        share = syrup_total / len(used_syrups)
        for s in used_syrups:
            syrup_result[s] = share

    return powder_result, syrup_result


# 원재료 사용량 계산
def calculate_ingredient_usage(df, recipe_folder="recipe"):
    results = []

    for machine in df['ParsedMachine'].unique():
        clean_machine = machine.replace("\\", "/").split("/")[-1]
        recipe_path = f"{recipe_folder}/{clean_machine}_Recipe.xlsx"

        try:
            recipe_df = pd.read_excel(recipe_path)
        except FileNotFoundError:
            st.warning(f"⚠️ {clean_machine}_Recipe.xlsx 파일을 찾을 수 없습니다.")
            continue

        recipe_df = recipe_df.rename(columns={
            '제품명': 'Product Name',
            '원료명': 'Ingredients',
            '원두 글라인딩 양': 'Bean',
            '1번 파우더량(S)': 'Powder1',
            '2번 파우더량(S)': 'Powder2',
            '시럽량(S)': 'Syrup'
        })

        recipe_df['Product Name'] = recipe_df['Product Name'].apply(normalize_name)
        recipe_df['Powder'] = (recipe_df['Powder1'] + recipe_df['Powder2']) * POWDER_GRAMS_PER_SECOND
        recipe_df['Syrup'] = recipe_df['Syrup'] * SYRUP_GRAMS_PER_SECOND

        sub_df = df[df['ParsedMachine'] == machine].copy()
        sub_df['Product Name'] = sub_df['Product Name'].apply(normalize_name)

        merged = sub_df.merge(recipe_df[['Product Name', 'Ingredients', 'Bean', 'Powder', 'Syrup']],
                              on='Product Name', how='left')

        # NaN → 0
        merged[['Bean', 'Powder', 'Syrup']] = merged[['Bean', 'Powder', 'Syrup']].fillna(0)
        merged['Quantity Ordered'] = pd.to_numeric(merged['Quantity Ordered'], errors='coerce').fillna(0)

        merged['Total Bean'] = merged['Bean'] * merged['Quantity Ordered']
        merged['Total Powder'] = merged['Powder'] * merged['Quantity Ordered']
        merged['Total Syrup'] = merged['Syrup'] * merged['Quantity Ordered']

        missing = merged[merged['Ingredients'].isna()]['Product Name'].unique()
        if len(missing) > 0:
            st.warning(f"❗ 레시피에 매칭되지 않은 상품: {', '.join(missing)}")

        for _, row in merged.iterrows():
            powder_use, syrup_use = extract_powder_syrup_usage(
                row['Ingredients'], row['Total Powder'], row['Total Syrup']
            )

            result_row = {
                'Year': row['Year'],
                'Month': row['Month'],
                'ParsedMachine': clean_machine,
                'Product Name': row['Product Name'],
                'Total Bean': row['Total Bean'],
            }
            result_row.update(powder_use)
            result_row.update(syrup_use)
            results.append(result_row)

    return pd.DataFrame(results)


# 요약 함수
def summarize_ingredients(ingredient_df):
    ingredient_df = ingredient_df.fillna(0)  # 필수
    group_cols = ['Year', 'Month', 'ParsedMachine']
    bean_summary = ingredient_df.groupby(group_cols)['Total Bean'].sum().reset_index()
    powder_summary = ingredient_df.groupby(group_cols)[POWDER_TYPES].sum().reset_index()
    syrup_summary = ingredient_df.groupby(group_cols)[SYRUP_TYPES].sum().reset_index()
    return bean_summary, powder_summary, syrup_summary


# 시각화 탭
def render_ingredient_tab(ingredient_df, selected_machine=None):
    st.subheader("🥣 원재료 사용량 분석")

    filtered_df = ingredient_df.copy()
    if selected_machine and selected_machine != "전체":
        filtered_df = filtered_df[filtered_df['ParsedMachine'] == selected_machine]

    if filtered_df.empty:
        st.warning("⚠️ 선택한 자판기에 해당하는 원재료 데이터가 없습니다.")
        return

    bean_summary, powder_summary, syrup_summary = summarize_ingredients(filtered_df)

    bean_summary["봉 수"] = (bean_summary["Total Bean"] / 1000).round(2)
    for col in POWDER_TYPES:
        powder_summary[f"{col} (봉 수)"] = (powder_summary[col] / 1000).round(2)
    for col in SYRUP_TYPES:
        syrup_summary[f"{col} (통 수)"] = (syrup_summary[col] / 1300).round(2)

    st.subheader("📥 원재료 사용량 엑셀 다운로드")
    excel_data = save_ingredient_excel(bean_summary, powder_summary, syrup_summary)
    st.download_button("엑셀 다운로드", data=excel_data, file_name="원재료_사용량_요약.xlsx")

    tab1, tab2, tab3 = st.tabs(["☕ 원두", "🥄 파우더", "🍯 시럽"])
    with tab1:
        st.dataframe(bean_summary, use_container_width=True)
    with tab2:
        st.dataframe(powder_summary, use_container_width=True)
    with tab3:
        st.dataframe(syrup_summary, use_container_width=True)


# 엑셀 저장
def save_ingredient_excel(bean_df, powder_df, syrup_df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        bean_df.to_excel(writer, sheet_name='원두 사용량', index=False)
        powder_df.to_excel(writer, sheet_name='파우더 사용량', index=False)
        syrup_df.to_excel(writer, sheet_name='시럽 사용량', index=False)
    return output.getvalue()
