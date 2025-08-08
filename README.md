# 🥤 Vending Machine Sales Dashboard

Streamlit을 사용한 자판기 매출 분석 대시보드입니다.  
CSV 파일 업로드를 통해 월별·주차별·시간대별 매출, 인기 제품, 원재료 사용량 등을 시각적으로 분석할 수 있습니다.

---

## 📦 기능 소개

| 기능 | 설명 |
|------|------|
| 📂 CSV 업로드 | 자판기 매출 CSV 파일 다중 업로드 |
| 📊 개요 분석 | 총 매출, 인기 상품, 일별 매출, 월별 비교 |
| 🏆 Top10 분석 | 인기 상품 및 카테고리별 매출 |
| ⏰ 시간대 분석 | 요일별 / 시간대별 매출 |
| 🥣 원재료 분석 | 원두, 파우더, 시럽 사용량 계산 |
| 📥 데이터 다운로드 | 엑셀 형식 매출 요약 다운로드 |

---

## 📁 폴더 구조

```kotlin
vending_dashboard/
├── app.py # Streamlit 메인 앱
├── requirements.txt # 필요한 Python 패키지 목록
├── README.md # 프로젝트 소개
├── Vending_Machine_Category.csv # 제품 카테고리 정의
├── utils/ # 기능별 모듈 폴더
│ ├── loader.py # CSV 및 카테고리 불러오기
│ ├── parser.py # CSV 파싱 및 전처리
│ ├── visualizer.py # 탭별 시각화
│ ├── exporter.py # 엑셀 다운로드 기능
│ └── ingredient_calculator.py # 원재료 계산 및 요약
└── recipe/ # 자판기별 레시피 엑셀 파일
```

## 🛠 설치 및 실행 방법

### 1. 환경 준비

```bash
git clone https://github.com/bbijoum26/vending_dashboard.git
cd vending_dashboard
pip install -r requirements.txt
```

### 2. 앱 실행

```bash
streamlit run app.py
```

---

## 📌 매출 CSV 파일 형식 예시

```csv
Order Time,Product Name,Quantity Ordered,Total Sales
2024-06-01 09:30:00,아메리카노,1,1500
2024-06-01 09:45:00,레몬에이드,2,3000
```

- 파일명 규칙: `A_sales_06.csv` → A는 자판기 이름, 06은 월
- 여러 개 업로드 시 병합됩니다.

---

## 🧪 원재료 분석을 위한 레시피 파일
- 경로: `recipe/A_Recipe.xlsx` (자판기명 + _Recipe.xlsx)
- 열 이름 예시

| 제품명 | 원료명 | 원두 글라인딩 양 | 1번 파우더량(S) | 2번 파우더량(S) | 시럽량(S) |
| --- | --- | --------- | ---------- | ---------- | ------ |

---

## 💡 기타 팁
- `data/` 폴더에 CSV 파일을 넣으면 자동 로드됩니다.
- `Vending_Machine_Category.csv` 파일로 제품 카테고리를 인식합니다.
- `utils/` 폴더가 Git에 누락되지 않도록 `.gitignore` 확인하세요.

---

## 📮 문의
- 개발자: @bbijoum26
- 피드백/이슈: [GitHub Issues](https://github.com/bbijoum26/vending_dashboard/issues)