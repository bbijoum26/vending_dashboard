import streamlit as st
import plotly.express as px

def render_overview_tab(filtered, df):
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

def render_top_tab(filtered):
    st.subheader("🏆 Top 10 인기 메뉴")
    top10_df = filtered.groupby('Product Name')['Quantity Ordered'].sum().sort_values(ascending=True).tail(10).reset_index()
    fig3 = px.bar(top10_df, x='Quantity Ordered', y='Product Name', orientation='h')
    st.plotly_chart(fig3, use_container_width=True)

    st.subheader("📊 카테고리별 매출")
    cat_df = filtered.groupby('Product Category')['Total Sales'].sum().reset_index()
    fig4 = px.pie(cat_df, values='Total Sales', names='Product Category', hole=0.4)
    st.plotly_chart(fig4, use_container_width=True)

def render_time_tab(filtered):
    st.subheader("📆 요일별 매출")
    weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    weekday_df = filtered.groupby('Weekday')['Total Sales'].sum().reindex(weekday_order).reset_index()
    fig5 = px.bar(weekday_df, x='Weekday', y='Total Sales')
    st.plotly_chart(fig5, use_container_width=True)

    st.subheader("⏰ 시간대별 매출")
    hour_df = filtered.groupby('Hour')['Total Sales'].sum().reset_index()
    fig6 = px.bar(hour_df, x='Hour', y='Total Sales')
    st.plotly_chart(fig6, use_container_width=True)
