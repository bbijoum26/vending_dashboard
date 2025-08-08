import pandas as pd
import os

# === 경로 설정 ===
raw_data_dir = r"C:\Users\fishr\vending_dashboard\utils"

cleaned_data_dir = r"C:\Users\fishr\vending_dashboard\data"
os.makedirs(cleaned_data_dir, exist_ok=True)

# === 컬럼 후보 매핑 ===
column_candidates = {
    "Product Name": ["商品名称", "상품명칭"],
    "Quantity Ordered": ["商品数量", "상품수량"],
    "Total Amount": ["订单实收金额", "실제 주문금액"],
    "Order Time": ["创建时间", "생성시간"]
}

for file in os.listdir(raw_data_dir):
    # ~로 시작하는 임시파일 제외
    if file.endswith(".xlsx") and not file.startswith("~$"):
        path = os.path.join(raw_data_dir, file)
        df = pd.read_excel(path)

        # === 실제 컬럼명 기반 매핑 ===
        rename_dict = {}
        for new_col, candidates in column_candidates.items():
            for c in candidates:
                if c in df.columns:
                    rename_dict[c] = new_col
                    break

        df = df[list(rename_dict.keys())].rename(columns=rename_dict)

        # === 파일명에서 Machine ID 추출 ===
        file_name_no_ext = os.path.splitext(file)[0]
        machine_id = file_name_no_ext.split("_")[0]

        rows = []
        for _, row in df.iterrows():
            try:
                names = [x.strip() for x in str(row["Product Name"]).split(',')]
                qtys = [x.strip() for x in str(row["Quantity Ordered"]).split(',')]

                if len(names) != len(qtys):
                    continue

                try:
                    qtys = [int(q) for q in qtys]
                except ValueError:
                    qtys = [1 for _ in qtys]

                total_qty = sum(qtys)
                try:
                    amount = float(row["Total Amount"])
                except Exception:
                    amount = 0.0

                order_time = pd.to_datetime(row["Order Time"], errors='coerce')
                if pd.isna(order_time):
                    continue

                # 금액 분배 (마지막 행 보정)
                split_amounts = []
                running_sum = 0
                for idx, qty in enumerate(qtys):
                    if idx == len(qtys) - 1:
                        split_amounts.append(round(amount - running_sum))
                    else:
                        portion = qty / total_qty if total_qty != 0 else 0
                        split_val = round(amount * portion)
                        split_amounts.append(split_val)
                        running_sum += split_val

                for name, qty, split_amount in zip(names, qtys, split_amounts):
                    rows.append({
                        "Product Name": name,
                        "Quantity Ordered": qty,
                        "Total Sales": split_amount,
                        "Order Time": order_time,
                        "Year": order_time.year,
                        "Month": order_time.month,
                        "Day": order_time.day,
                        "Order HourMinute": order_time.strftime("%H:%M"),
                        "Machine": machine_id
                    })

            except Exception as e:
                print(f"Row 처리 중 오류 발생: {e}")
                continue

        df_cleaned = pd.DataFrame(rows)
        save_path = os.path.join(cleaned_data_dir, f"{file_name_no_ext}.csv")
        df_cleaned.to_csv(save_path, index=False, encoding='utf-8-sig')
        print(f"{file_name_no_ext}.csv 저장 완료.")