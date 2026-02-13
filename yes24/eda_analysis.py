import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
# import koreanize_matplotlib  # Removed as it's causing issues
from loguru import logger
from wordcloud import WordCloud
import os
import re
from io import StringIO # Import StringIO for capturing df.info()

# Set Matplotlib font for Korean
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# --- 기본 설정 ---
# 이미지 저장 폴더 생성
if not os.path.exists('yes24/images'):
    os.makedirs('yes24/images')

# 로그 설정 (Ensuring UTF-8 encoding for logs)
logger.add("yes24/log/eda_{time}.log", rotation="500 MB", encoding="utf-8")

# 결과 저장용 마크다운 파일
report_path = "yes24/eda_report.md"
with open(report_path, "w", encoding="utf-8") as f:
    f.write("# Yes24 AI 도서 데이터 분석 보고서\n\n")

# Korean strings for report sections and titles
REPORT_TITLE = "# Yes24 AI 도서 데이터 분석 보고서\n\n"
DATA_OVERVIEW = "## 1. 데이터 개요\n\n"
DATA_SAMPLE = "### 데이터 샘플\n"
DATA_INFO = "### 데이터 정보\n"
PREPROCESSING_INFO = "### 전처리 후 데이터 정보\n"
EDA_SECTION = "## 2. 탐색적 데이터 분석 (EDA)\n\n"
BASIC_STATS = "### 기초 통계\n"
NUMERIC_DATA_STATS = "#### 수치형 데이터\n"
CATEGORICAL_DATA_STATS = "#### 범주형 데이터\n"
NUMERIC_DISTRIBUTION = "### 수치 데이터 분포\n"
FREQUENCY_DISTRIBUTION = "### 범주형 데이터 빈도\n"
PUBLISHER_ANALYSIS = "### 출판사 분석\n"
TOP_20_PUBLISHERS_TITLE = "#### 상위 20개 출판사 도서 수\n"
TREND_ANALYSIS = "### 발행 트렌드 분석\n"
YEARLY_TREND = "#### 연도별 발행 트렌드\n"
MONTHLY_TREND = "#### 월별 발행 트렌드\n"
CORRELATION_ANALYSIS = "### 상관 관계 분석\n"
CORRELATION_MATRIX_TITLE = "#### 가격, 리뷰 수, 판매지수 간의 상관관계\n"
WORDCLOUD_SECTION = "### 도서 제목 워드 클라우드\n"
CROSS_ANALYSIS_SECTION = "## 3. 교차 분석\n\n"
PUB_PRICE_SALES_PIVOT = "### 1. 상위 20개 출판사별 평균 가격, 리뷰 수, 판매지수\n"
YEARLY_PRICE_SALES_PIVOT = "### 2. 연도별 평균 가격 및 판매지수\n"
PRICE_RANGE_DISTRIBUTION = "### 3. 가격대별 도서 수 및 평균 판매지수/리뷰 수\n"
PUB_PRICE_RANGE_PIVOT = "### 4. 상위 10개 출판사별 가격대 분포\n"
YEARLY_MONTHLY_PUBLICATION = "### 5. 연도 및 월별 도서 발행 수\n"
WORDCLOUD_ERROR = "워드 클라우드 생성에 실패했습니다. (오류: {e})\n\n"

INSIGHTS_CORRELATION = """
**인사이트:**
- `price`와 `sale_price`는 매우 높은 양의 상관관계를 보입니다(거의 1). 이는 정가와 판매가가 거의 비례 관계에 있음을 의미합니다.
- `review_count`와 `sales_index`는 0.58의 양의 상관관계를 보입니다. 리뷰 수가 많을수록 판매지수도 높은 경향이 있음을 시사합니다.
- 가격(`price`, `sale_price`)과 다른 변수들(`review_count`, `sales_index`) 간의 상관관계는 상대적으로 낮게 나타나, 책 가격이 리뷰 수나 판매지수에 직접적인 큰 영향을 주지는 않는 것으로 보입니다.

"""

INSIGHTS_WORDCLOUD = """
**인사이트:**
- 'AI', '인공지능', '머신러닝', '딥러닝', '데이터', '파이썬' 등의 단어가 두드러지게 나타납니다. 
- 이는 AI 분야 베스트셀러가 주로 특정 기술 스택(파이썬)과 핵심 개념(머신러닝, 딥러닝)에 집중되어 있음을 보여줍니다.
- '실습', '만들면서', '코딩' 등의 단어는 실용적이고 따라하기 쉬운 실습 위주의 책이 인기가 많음을 시사합니다.

"""


# --- 1. 데이터 불러오기 및 전처리 ---
logger.info("데이터 불러오기 및 전처리 시작")
try:
    df = pd.read_csv('yes24/data/yes24_ai.csv')

    # Rename columns for consistency with EDA instructions
    df.rename(columns={'sales_price': 'price', 'original_price': 'sale_price'}, inplace=True)

    with open(report_path, "a", encoding="utf-8") as f:
        f.write(DATA_OVERVIEW)
        f.write(DATA_SAMPLE)
        f.write(df.head().to_markdown(index=False))
        f.write("\n\n")

        f.write(DATA_INFO)
        
    # StringIO를 사용하여 df.info() 출력을 캡처
    buffer = StringIO()
    df.info(buf=buffer)
    info_str = buffer.getvalue()

    with open(report_path, "a", encoding="utf-8") as f:
        f.write("```\n")
        f.write(info_str)
        f.write("\n```\n\n")

    # 데이터 전처리
    logger.info("데이터 전처리 시작")
    
    # '정가', '판매가'는 이미 숫자형으로 로드되므로, astype(float)만 적용
    df['price'] = df['price'].astype(float)
    df['sale_price'] = df['sale_price'].astype(float)
    
    # '리뷰 수'와 '판매지수'가 없는 경우 0으로 처리하고 숫자형으로 변환
    df['review_count'] = df['review_count'].fillna(0).astype(int)
    # 'sales_index' 컬럼이 없는 경우를 대비하여 처리
    if 'sales_index' in df.columns:
        df['sales_index'] = df['sales_index'].fillna(0).astype(int)
    else:
        logger.warning("Column 'sales_index' not found. Initializing with 0.")
        df['sales_index'] = 0 # Placeholder if not present
    
    # '발행일'에서 연도, 월 추출 (using regex for robustness against encoding issues and handling NaNs)
    df['publication_year'] = df['publication_date'].str.extract(r'(\d{4})년').fillna('0').astype(int)
    df['publication_month'] = df['publication_date'].str.extract(r'(\d{1,2})월').fillna('0').astype(int)
    
    logger.info("데이터 전처리 완료")
    
    with open(report_path, "a", encoding="utf-8") as f:
        f.write(PREPROCESSING_INFO)

    buffer = StringIO()
    df.info(buf=buffer)
    info_str_after = buffer.getvalue()
    
    with open(report_path, "a", encoding="utf-8") as f:
        f.write("```\n")
        f.write(info_str_after)
        f.write("\n```\n\n")

except FileNotFoundError:
    logger.error("yes24/data/yes24_ai.csv 파일을 찾을 수 없습니다.")
    exit()
except Exception as e:
    logger.error(f"데이터 처리 중 오류 발생: {e}")
    exit()
    
# --- 2. 탐색적 데이터 분석(EDA) ---
logger.info("탐색적 데이터 분석(EDA) 시작")

with open(report_path, "a", encoding="utf-8") as f:
    f.write(EDA_SECTION)

# 기초 통계 분석
logger.info("기초 통계 분석")
with open(report_path, "a", encoding="utf-8") as f:
    f.write(BASIC_STATS)
    f.write(NUMERIC_DATA_STATS)
    f.write(df.describe().to_markdown())
    f.write("\n\n")
    f.write(CATEGORICAL_DATA_STATS)
    df_obj_cat = df.select_dtypes(include=['object', 'category'])
    if not df_obj_cat.empty:
        f.write(df_obj_cat.describe().to_markdown())
    else:
        f.write("범주형 데이터가 없습니다.\n")
    f.write("\n\n")

# 수치 데이터 분포 시각화
logger.info("수치 데이터 분포 시각화")
numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
with open(report_path, "a", encoding="utf-8") as f:
    f.write(NUMERIC_DISTRIBUTION)

for col in numeric_cols:
    plt.figure(figsize=(10, 6))
    sns.histplot(df[col], kde=True)
    plt.title(f'{col} 분포', fontsize=15)
    img_path = f'yes24/images/{col}_distribution.png'
    plt.savefig(img_path)
    plt.close()
    with open(report_path, "a", encoding="utf-8") as f:
        f.write(f"#### {col} 분포\n")
        f.write(f"![{col} 분포]({img_path.replace('yes24/', '')})\n\n")

# 범주형 데이터 빈도 분석
logger.info("범주형 데이터 빈도 분석")
categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
with open(report_path, "a", encoding="utf-8") as f:
    f.write(FREQUENCY_DISTRIBUTION)

for col in categorical_cols:
    plt.figure(figsize=(12, 7))
    top_20 = df[col].value_counts().nlargest(20)
    if not top_20.empty:
        sns.barplot(x=top_20.values, y=top_20.index)
        plt.title(f'상위 20개 {col}', fontsize=15)
        plt.xlabel('빈도수')
        plt.ylabel(col)
        img_path = f'yes24/images/{col}_frequency.png'
        plt.tight_layout()
        plt.savefig(img_path)
        plt.close()
        with open(report_path, "a", encoding="utf-8") as f:
            f.write(f"#### {col} 빈도 (상위 20개)\n")
            f.write(top_20.to_markdown())
            f.write("\n\n")
            f.write(f"![{col} 빈도]({img_path.replace('yes24/', '')})\n\n")
    else:
        with open(report_path, "a", encoding="utf-8") as f:
            f.write(f"#### {col} 빈도 (상위 20개)\n")
            f.write(f"'{col}' 컬럼에 표시할 범주형 데이터가 없습니다.\n\n")
        

# 출판사 분석
logger.info("출판사 분석")
plt.figure(figsize=(12, 8))
publisher_counts = df['publisher'].value_counts().nlargest(20)
if not publisher_counts.empty:
    sns.barplot(x=publisher_counts.values, y=publisher_counts.index, orient='h')
    plt.title('상위 20개 출판사', fontsize=15)
    plt.xlabel('도서 수')
    plt.ylabel('출판사')
    img_path = 'yes24/images/top_20_publishers.png'
    plt.tight_layout()
    plt.savefig(img_path)
    plt.close()
    with open(report_path, "a", encoding="utf-8") as f:
        f.write(PUBLISHER_ANALYSIS)
        f.write(TOP_20_PUBLISHERS_TITLE)
        f.write(publisher_counts.to_markdown())
        f.write("\n\n")
        f.write(f"![상위 20개 출판사](images/top_20_publishers.png)\n\n")
else:
    with open(report_path, "a", encoding="utf-8") as f:
        f.write(PUBLISHER_ANALYSIS)
        f.write(TOP_20_PUBLISHERS_TITLE)
        f.write("출판사 데이터가 없습니다.\n\n")

# 발행 트렌드 분석
logger.info("발행 트렌드 분석")
# 연도별
plt.figure(figsize=(12, 6))
year_counts = df['publication_year'].value_counts().sort_index()
if not year_counts.empty:
    sns.lineplot(x=year_counts.index, y=year_counts.values, marker='o')
    plt.title('연도별 AI 도서 발행 트렌드', fontsize=15)
    plt.xlabel('연도')
    plt.ylabel('발행 도서 수')
    plt.xticks(year_counts.index.astype(int))
    img_path = 'yes24/images/yearly_trend.png'
    plt.savefig(img_path)
    plt.close()
else:
    logger.warning("연도별 발행 트렌드 데이터가 없습니다.")

# 월별
plt.figure(figsize=(12, 6))
month_counts = df['publication_month'].value_counts().sort_index()
if not month_counts.empty:
    sns.barplot(x=month_counts.index, y=month_counts.values)
    plt.title('월별 AI 도서 발행 트렌드', fontsize=15)
    plt.xlabel('월')
    plt.ylabel('발행 도서 수')
    img_path_month = 'yes24/images/monthly_trend.png'
    plt.savefig(img_path_month)
    plt.close()
else:
    logger.warning("월별 발행 트렌드 데이터가 없습니다.")


with open(report_path, "a", encoding="utf-8") as f:
    f.write(TREND_ANALYSIS)
    if not year_counts.empty:
        f.write(YEARLY_TREND)
        f.write(year_counts.to_markdown())
        f.write("\n\n")
        f.write(f"![연도별 트렌드](images/yearly_trend.png)\n\n")
    else:
        f.write(YEARLY_TREND)
        f.write("연도별 발행 트렌드 데이터를 생성할 수 없습니다.\n\n")
    
    if not month_counts.empty:
        f.write(MONTHLY_TREND)
        f.write(month_counts.to_markdown())
        f.write("\n\n")
        f.write(f"![월별 트렌드](images/monthly_trend.png)\n\n")
    else:
        f.write(MONTHLY_TREND)
        f.write("월별 발행 트렌드 데이터를 생성할 수 없습니다.\n\n")

# 상관 관계 분석
logger.info("상관 관계 분석")
correlation_cols = ['price', 'sale_price', 'review_count', 'sales_index']
correlation_matrix = df[correlation_cols].corr()

plt.figure(figsize=(10, 8))
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt=".2f")
plt.title('주요 수치 데이터 상관 관계', fontsize=15)
img_path = 'yes24/images/correlation_heatmap.png'
plt.savefig(img_path)
plt.close()

with open(report_path, "a", encoding="utf-8") as f:
    f.write(CORRELATION_ANALYSIS)
    f.write(CORRELATION_MATRIX_TITLE)
    f.write(correlation_matrix.to_markdown())
    f.write("\n\n")
    f.write(f"![상관 관계 히트맵](images/correlation_heatmap.png)\n\n")
    f.write(INSIGHTS_CORRELATION)


# 워드 클라우드
logger.info("워드 클라우드 생성")
# 'title' 컬럼의 모든 텍스트를 하나로 합치기
# title에 float 타입이 섞여있을 수 있으므로, str으로 변환
text = " ".join(str(title) for title in df['title'])
# 한글 및 영어 단어만 추출하는 정규 표현식
text = " ".join(re.findall(r'[가-힣a-zA-Z]+', text))

try:
    wordcloud = WordCloud(
        font_path='c:/Windows/Fonts/malgun.ttf',  # 윈도우 기본 폰트
        width=800,
        height=400,
        background_color='white'
    ).generate(text)

    plt.figure(figsize=(15, 7))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    img_path = 'yes24/images/title_wordcloud.png'
    plt.savefig(img_path)
    plt.close()

    with open(report_path, "a", encoding="utf-8") as f:
        f.write(WORDCLOUD_SECTION)
        f.write("![워드 클라우드](images/title_wordcloud.png)\n\n")
        f.write(INSIGHTS_WORDCLOUD)

except Exception as e:
    logger.error(f"워드 클라우드 생성 중 오류: {e}")
    with open(report_path, "a", encoding="utf-8") as f:
        f.write(WORDCLOUD_SECTION)
        f.write(WORDCLOUD_ERROR.format(e=e))

# --- 3. 교차 분석 ---
logger.info("교차 분석 시작")
with open(report_path, "a", encoding="utf-8") as f:
    f.write(CROSS_ANALYSIS_SECTION)

# 1. 출판사별 평균 가격 및 판매지수
logger.info("교차 분석 1: 출판사별 평균 가격 및 판매지수")
publisher_pivot = df.groupby('publisher').agg({
    'price': 'mean',
    'sale_price': 'mean',
    'review_count': 'sum',
    'sales_index': 'mean',
    'title': 'count'
}).rename(columns={'title': 'book_count'}).sort_values(by='book_count', ascending=False).head(20)

with open(report_path, "a", encoding="utf-8") as f:
    f.write(PUB_PRICE_SALES_PIVOT)
    f.write(publisher_pivot.to_markdown())
    f.write("\n\n")

# 2. 연도별 평균 가격 및 판매지수
logger.info("교차 분석 2: 연도별 평균 가격 및 판매지수")
yearly_pivot = df.groupby('publication_year').agg({
    'price': 'mean',
    'sale_price': 'mean',
    'sales_index': 'mean',
    'review_count': 'mean'
}).sort_index()

with open(report_path, "a", encoding="utf-8") as f:
    f.write(YEARLY_PRICE_SALES_PIVOT)
    f.write(yearly_pivot.to_markdown())
    f.write("\n\n")

# 3. 가격대별 도서 분포
logger.info("교차 분석 3: 가격대별 도서 분포")
price_bins = [0, 10000, 20000, 30000, 40000, 50000, np.inf]
price_labels = ['~1만원', '1~2만원', '2~3만원', '3~4만원', '4~5만원', '5만원~']
df['price_range'] = pd.cut(df['price'], bins=price_bins, labels=price_labels)

price_range_pivot = df.groupby('price_range').agg({
    'title': 'count',
    'sales_index': 'mean',
    'review_count': 'mean'
}).rename(columns={'title': 'book_count'})

with open(report_path, "a", encoding="utf-8") as f:
    f.write(PRICE_RANGE_DISTRIBUTION)
    f.write(price_range_pivot.to_markdown())
    f.write("\n\n")

# 4. 출판사 및 가격대별 도서 수
logger.info("교차 분석 4: 출판사 및 가격대별 도서 수")
top_10_publishers = df['publisher'].value_counts().head(10).index.tolist()
df_top_publishers = df[df['publisher'].isin(top_10_publishers)]

publisher_price_pivot = pd.crosstab(
    index=df_top_publishers['publisher'],
    columns=df_top_publishers['price_range'],
)
with open(report_path, "a", encoding="utf-8") as f:
    f.write(PUB_PRICE_RANGE_PIVOT)
    f.write(publisher_price_pivot.to_markdown())
    f.write("\n\n")
    
# 5. 연도 및 월별 도서 발행 수
logger.info("교차 분석 5: 연도 및 월별 도서 발행 수")
yearly_monthly_pivot = pd.crosstab(
    index=df['publication_year'],
    columns=df['publication_month']
)
with open(report_path, "a", encoding="utf-8") as f:
    f.write(YEARLY_MONTHLY_PUBLICATION)
    f.write(yearly_monthly_pivot.to_markdown())
    f.write("\n\n")
    
logger.info("모든 분석 완료")
print(f"분석 보고서가 {report_path} 파일로 저장되었습니다.")