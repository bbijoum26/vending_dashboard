import pandas as pd
import os
import glob

DATA_FOLDER = 'data'

def save_uploaded_file(uploaded_file):
    os.makedirs(DATA_FOLDER, exist_ok=True)
    file_path = os.path.join(DATA_FOLDER, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path

def load_uploaded_or_folder_csvs(uploaded_files):
    if uploaded_files:
        saved_files = []
        for file in uploaded_files:
            saved_path = save_uploaded_file(file)
            saved_files.append(open(saved_path, 'rb'))
        return saved_files

    if os.path.exists(DATA_FOLDER):
        csv_files = glob.glob(os.path.join(DATA_FOLDER, '*.csv'))
        return [open(f, 'rb') for f in csv_files]
    return []

def load_category_data():
    category_path = "./Vending_Machine_Category.csv"
    cat_df = pd.read_csv(category_path)
    return cat_df.rename(columns={"제품명": "Product Name", "제품 카테고리": "Product Category"})
