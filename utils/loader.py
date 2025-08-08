import pandas as pd
import os
import glob

def load_uploaded_or_folder_csvs(uploaded_files):
    if uploaded_files:
        return uploaded_files
    data_folder = 'data'
    if os.path.exists(data_folder):
        csv_files = glob.glob(os.path.join(data_folder, '*.csv'))
        return [open(f, 'rb') for f in csv_files]
    return []

def load_category_data():
    category_path = "./Vending_Machine_Category.csv"
    cat_df = pd.read_csv(category_path)
    return cat_df.rename(columns={"제품명": "Product Name", "제품 카테고리": "Product Category"})
