import streamlit as st
import pandas as pd
from io import BytesIO

def render_download_tab(df):
    st.subheader("⬇️ 엑셀 다운로드")

    def create_excel(df):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # 월별
            month_df = df.groupby(['Year', 'Month', 'ParsedMachine'])['Total Sales'].sum().unstack(fill_value=0)
            month_df['Total'] = month_df.sum(axis=1)
            month_df.to_excel(writer, sheet_name='월별 매출')

            # 주차별
            week_df = df.groupby(['Year', 'Month', 'Week', 'ParsedMachine'])['Total Sales'].sum().unstack(fill_value=0)
            week_df['Total'] = week_df.sum(axis=1)
            week_df.to_excel(writer, sheet_name='주차별 매출')

            # 일별
            day_df = df.groupby(['Year', 'Month', 'Day', 'ParsedMachine'])['Total Sales'].sum().unstack(fill_value=0)
            day_df['Total'] = day_df.sum(axis=1)
            day_df.to_excel(writer, sheet_name='일별 매출')

        return output.getvalue()

    excel_bytes = create_excel(df)
    st.download_button("📥 엑셀 다운로드", excel_bytes, file_name="vending_sales_report.xlsx")

    st.subheader("📊 월별 자판기별 매출 요약표")
    pivot_df = df.pivot_table(index=['Year', 'Month'], columns='ParsedMachine', values='Total Sales', aggfunc='sum', fill_value=0)
    pivot_df['Total'] = pivot_df.sum(axis=1)
    st.dataframe(pivot_df, use_container_width=True)
