import streamlit as st
import pandas as pd
import os
import glob
from io import BytesIO
import plotly.express as px

# -----------------------------------
# 기본 설정
# -----------------------------------
st.set_page_config(page_title="Vending Machine Sales Dashboard", layout="wide")
st.title("🥤 Vending Machine Sales Dashboard")

# -----------------------------------
# 파일 업로드 or data 폴더에서 자동 보내오기
# -----------------------------------
uploaded_files = st.file_uploader("📂 자판기 매주 CSV 파일 업로드 (여러 개 가능)", type="csv", accept_multiple_files=True)
if not uploaded_files:
    st.info("💡 업로드된 파일이 없어 data 폴더에서 CSV를 자동으로 보내오는다.")
    data_folder = 'data'
    if os.path.exists(data_folder):
        csv_files = glob.glob(os.path.join(data_folder, '*.csv'))
    else:
        csv_files = []
    uploaded_files = [open(f, 'rb') for f in csv_files]

# -----------------------------------
# 제품 카테고리 로드
# -----------------------------------
@st.cache_data
def load_category_data():
    category_path = "./Vending_Machine_Category.csv"
    cat_df = pd.read_csv(category_path)
    return cat_df.rename(columns={"제품명": "Product Name", "제품 카테고리": "Product Category"})

category_df = load_category_data()

# -----------------------------------
# CSV 파싱
# -----------------------------------
@st.cache_data
def read_and_parse(files):
    all_data = []
    for file in files:
        filename = os.path.basename(file.name)
        try:
            machine = filename.split("_sales_")[0]
            month = int(filename.split("_sales_")[1].replace(".csv", ""))
        except:
            st.warning(f"❗ 파일명 형식이 잘못되었습니다: {filename}")
            continue

        df = pd.read_csv(file)
        df['ParsedMachine'] = machine
        df['ParsedMonth'] = month
        all_data.append(df)

    if all_data:
        return pd.concat(all_data, ignore_index=True)
    else:
        return pd.DataFrame()

if uploaded_files:
    df = read_and_parse(uploaded_files)

    # -----------------------------------
    # 전처리
    # -----------------------------------
    df['Order Time'] = pd.to_datetime(df['Order Time'])
    df['Week'] = df['Order Time'].dt.isocalendar().week
    df['Day'] = df['Order Time'].dt.day
    df['Month'] = df['Order Time'].dt.month
    df['Year'] = df['Order Time'].dt.year
    df['Weekday'] = df['Order Time'].dt.day_name()
    df['Hour'] = df['Order Time'].dt.hour

    weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    # -----------------------------------
    # 카테고리 merge
    # -----------------------------------
    df = df.merge(category_df[['Product Name', 'Product Category']], on='Product Name', how='left')

    # -----------------------------------
    # 필터
    # -----------------------------------
    months = sorted(df['Month'].unique())
    machines = sorted(df['ParsedMachine'].unique())
    machines.insert(0, "전체")  # 전체 추가

    col1, col2 = st.columns(2)
    with col1:
        selected_month = st.selectbox("📅 월 선택", months)
    with col2:
        selected_machine = st.selectbox("🏪 자판기 선택", machines)

    if selected_machine == "전체":
        filtered = df[df['Month'] == selected_month]
    else:
        filtered = df[(df['Month'] == selected_month) & (df['ParsedMachine'] == selected_machine)]

    # -----------------------------------
    # 탭 구성
    # -----------------------------------
    tab1, tab2, tab3, tab4 = st.tabs(["개요", "Top10/카테고리", "시간대 분석", "데이터 다운로드"])

    # -----------------------------------
    # 탭1: 개요
    # -----------------------------------
    with tab1:
        if not filtered.empty:
            total_sales = filtered['Total Sales'].sum()
            total_orders = filtered['Quantity Ordered'].sum()
            top_item = filtered.groupby('Product Name')['Quantity Ordered'].sum().idxmax()

            k1, k2, k3 = st.columns(3)
            k1.metric("💵 총 매출", f"₩{total_sales:,.0f}")
            k2.metric("🧾 총 주문 수량", f"{total_orders:,}")
            k3.metric("🔥 인기 메뉴", top_item)

            st.subheader("📈 자판기 월 매출 비교")
            line_df = df.groupby(['Month', 'ParsedMachine'])['Total Sales'].sum().reset_index()
            fig2 = px.line(line_df, x='Month', y='Total Sales', color='ParsedMachine', markers=True)
            st.plotly_chart(fig2, use_container_width=True)

            st.subheader("📅 일별 매출")
            daily = filtered.groupby('Day')['Total Sales'].sum()
            fig1 = px.bar(x=daily.index, y=daily.values, labels={'x': '일', 'y': '매출'})
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.warning("⚠️ 선택한 조건에 해당하는 데이터가 없습니다.")


    # -----------------------------------
    # 탭2: 메뉴
    # -----------------------------------
    with tab2:
        st.subheader("🏆 Top 10 인기 메뉴")
        top10_df = filtered.groupby('Product Name')['Quantity Ordered'].sum().sort_values(ascending=True).tail(10).reset_index()
        fig3 = px.bar(top10_df, x='Quantity Ordered', y='Product Name', orientation='h')
        st.plotly_chart(fig3, use_container_width=True)

        st.subheader("📊 카테고리별 매출")
        cat_df = filtered.groupby('Product Category')['Total Sales'].sum().reset_index()
        fig4 = px.pie(cat_df, values='Total Sales', names='Product Category', hole=0.4)
        st.plotly_chart(fig4, use_container_width=True)

    # -----------------------------------
    # 탭3: 시간대 분석
    # -----------------------------------
    with tab3:
        st.subheader("📆 요일별 매출")
        weekday_df = filtered.groupby('Weekday')['Total Sales'].sum().reindex(weekday_order).reset_index()
        weekday_df.columns = ['Weekday', 'Total Sales']
        fig5 = px.bar(weekday_df, x='Weekday', y='Total Sales', labels={'Weekday': '요일', 'Total Sales': '매출'})
        st.plotly_chart(fig5, use_container_width=True)

        st.subheader("⏰ 시간대별 매출")
        hour_df = filtered.groupby('Hour')['Total Sales'].sum().reset_index()
        fig6 = px.bar(hour_df, x='Hour', y='Total Sales', labels={'Hour': '시간', 'Total Sales': '매출'})
        st.plotly_chart(fig6, use_container_width=True)


    # -----------------------------------
    # 탭4: 다운로드
    # -----------------------------------
    with tab4:
        st.subheader("⬇️ 엑셀 다운로드")

        def create_excel(df):
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                # 월/주차/일별 요약 시트
                month_df = df.groupby(['Year', 'Month', 'ParsedMachine'])['Total Sales'].sum().unstack(fill_value=0)
                month_df['Total'] = month_df.sum(axis=1)
                month_df.to_excel(writer, sheet_name='월별 매출')

                week_df = df.groupby(['Year', 'Month', 'Week', 'ParsedMachine'])['Total Sales'].sum().unstack(fill_value=0)
                week_df['Total'] = week_df.sum(axis=1)
                week_df.to_excel(writer, sheet_name='주차별 매출')

                day_df = df.groupby(['Year', 'Month', 'Day', 'ParsedMachine'])['Total Sales'].sum().unstack(fill_value=0)
                day_df['Total'] = day_df.sum(axis=1)
                day_df.to_excel(writer, sheet_name='일별 매출')

                # 자판기별 상세 요약 시트 하나로 구성
                for m in df['ParsedMachine'].unique():
                    machine_df = df[df['ParsedMachine'] == m]
                    start_row = 0

                    # 하나의 시트에 이어붙이기
                    sheet_name = f'{m}_상세'
                    machine_df.groupby(['Year', 'Month'])[['Quantity Ordered', 'Total Sales']].sum().reset_index().to_excel(writer, sheet_name=sheet_name, startrow=start_row, index=False)
                    start_row += len(machine_df.groupby(['Year', 'Month'])) + 3

                    machine_df.groupby(['Year', 'Month', 'Week'])[['Quantity Ordered', 'Total Sales']].sum().reset_index().to_excel(writer, sheet_name=sheet_name, startrow=start_row, index=False)
                    start_row += len(machine_df.groupby(['Year', 'Month', 'Week'])) + 3

                    machine_df.groupby(['Year', 'Month', 'Day'])[['Quantity Ordered', 'Total Sales']].sum().reset_index().to_excel(writer, sheet_name=sheet_name, startrow=start_row, index=False)
                    start_row += len(machine_df.groupby(['Year', 'Month', 'Day'])) + 3

                    machine_df.groupby('Product Name')[['Quantity Ordered', 'Total Sales']].sum().sort_values(by='Quantity Ordered', ascending=False).reset_index().to_excel(writer, sheet_name=sheet_name, startrow=start_row, index=False)
                    start_row += len(machine_df['Product Name'].unique()) + 3

                    machine_df.groupby('Product Category')[['Quantity Ordered', 'Total Sales']].sum().sort_values(by='Total Sales', ascending=False).reset_index().to_excel(writer, sheet_name=sheet_name, startrow=start_row, index=False)

            return output.getvalue()

        excel_bytes = create_excel(df)
        st.download_button("📥 엑셀 다운로드", excel_bytes, file_name="vending_sales_full_report.xlsx")

        st.subheader("📊 월별 자판기별 매출 요약표")
        pivot_df = df.pivot_table(index=['Year', 'Month'], columns='ParsedMachine', values='Total Sales', aggfunc='sum', fill_value=0)
        pivot_df['Total'] = pivot_df.sum(axis=1)
        st.dataframe(pivot_df, use_container_width=True)

else:
    st.info("💡 CSV 파일을 업로드하거나, 저장소의 data 폴더에 파일을 넣어주세요.\n예: A_sales_007.csv")
