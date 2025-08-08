import pandas as pd
import streamlit as st
import os

def parse_csv_files(files):
    all_data = []
    for file in files:
        filename = os.path.basename(file.name)
        try:
            machine = filename.split("_sales_")[0]
            month = int(filename.split("_sales_")[1].replace(".csv", ""))
        except:
            continue

        df = pd.read_csv(file)
        df['ParsedMachine'] = machine
        df['ParsedMonth'] = month
        all_data.append(df)

    if all_data:
        return pd.concat(all_data, ignore_index=True)
    return pd.DataFrame()

def preprocess_data(df, category_df):
    df['Order Time'] = pd.to_datetime(df['Order Time'])
    df['Week'] = df['Order Time'].dt.isocalendar().week
    df['Day'] = df['Order Time'].dt.day
    df['Month'] = df['Order Time'].dt.month
    df['Year'] = df['Order Time'].dt.year
    df['Weekday'] = df['Order Time'].dt.day_name()
    df['Hour'] = df['Order Time'].dt.hour
    df = df.merge(category_df[['Product Name', 'Product Category']], on='Product Name', how='left')
    return df

def apply_filters(df):
    months = sorted(df['Month'].unique())
    machines = sorted(df['ParsedMachine'].unique())
    machines.insert(0, "전체")

    col1, col2 = st.columns(2)
    with col1:
        selected_month = st.selectbox("📅 월 선택", months)
    with col2:
        selected_machine = st.selectbox("🏪 자판기 선택", machines)

    if selected_machine == "전체":
        filtered = df[df['Month'] == selected_month]
    else:
        filtered = df[(df['Month'] == selected_month) & (df['ParsedMachine'] == selected_machine)]

    return selected_month, selected_machine, filtered
