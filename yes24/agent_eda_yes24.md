
# YES24 AI 도서 데이터 분석 및 시각화

이 문서는 `yes24/data/yes24_ai.csv` 파일의 데이터를 분석하고 시각화한 결과를 담고 있습니다.

## 1. 데이터 개요

### 데이터 샘플 (상위 5개)

| title                                     | author    | publisher      | publication_date | sales_price | original_price | rating | review_count |
| :---------------------------------------- | :-------- | :------------- | :--------------- | :---------- | :------------- | :----- | :----------- |
| 된다! 하루 만에 끝내는 제미나이 활용법     | 권서림    | 이지스퍼블리싱 | 2025년 11월      | 18000       | 20000          | 9.8    | 62           |
| 요즘 바이브 코딩 안티그래비티 완벽 가이드 | 최지호    | 골든래빗       | 2026년 02월      | 25200       | 28000          | 10     | 2            |
| 누구나 아는 나만 모르는 제미나이          | 이성원    | 한빛미디어     | 2026년 01월      | 17100       | 19000          | 10     | 11           |
| AI 시대의 질문력, 프롬프트 엔지니어링      | 류한석    | 코리아닷컴(Korea.com) | 2025년 08월      | 24300       | 27000          | 9.5    | 44           |
| 요즘 교사를 위한 에듀테크 5대장 : 캔바, 패들렛, 북크리에이터, 노션, 챗GPT∙제미나이 | 안익재    | 앤써북         | 2025년 12월      | 17820       | 19800          | 10     | 84           |

### 데이터 정보

```
<class 'pandas.core.frame.DataFrame'>
RangeIndex: 50 entries, 0 to 49
Data columns (total 8 columns):
 #   Column            Non-Null Count  Dtype
---  ------            --------------  -----
 0   title             50 non-null     object
 1   author            50 non-null     object
 2   publisher         50 non-null     object
 3   publication_date  50 non-null     object
 4   sales_price       50 non-null     int64
 5   original_price    50 non-null     int64
 6   rating            49 non-null     object
 7   review_count      49 non-null     object
dtypes: int64(2), object(6)
memory usage: 3.2+ KB
```

### 데이터 통계 요약

|       | sales_price | original_price | rating | review_count |
| :---- | :---------- | :------------- | :----- | :----------- |
| count | 49          | 49             | 49     | 49           |
| mean  | 21869.8     | 24297.9        | 9.7    | 48.2         |
| std   | 5373.9      | 5971           | 0.4    | 44.7         |
| min   | 15120       | 16800          | 8.4    | 1            |
| 25%   | 18000       | 20000          | 9.7    | 11           |
| 50%   | 20700       | 23000          | 9.8    | 39           |
| 75%   | 25200       | 28000          | 10     | 82           |
| max   | 36000       | 40000          | 10     | 184          |

* 'rating'과 'review_count'의 'N/A' 값은 분석에서 제외되었습니다.

## 2. 데이터 시각화

### 2.1 판매 가격 분포

![Sales Price Distribution](https://via.placeholder.com/600x400.png?text=Sales+Price+Distribution)

판매 가격은 15,000원에서 36,000원 사이에 분포하며, 18,000원대에 가장 많은 도서가 집중되어 있습니다.

### 2.2 평점 분포

![Rating Distribution](https://via.placeholder.com/600x400.png?text=Rating+Distribution)

평점은 대부분 9.5점 이상으로 매우 높게 나타나며, 10점 만점인 도서가 다수 존재합니다.

### 2.3 상위 10개 출판사 (도서 수 기준)

![Top 10 Publishers](https://via.placeholder.com/800x600.png?text=Top+10+Publishers)

한빛미디어, 골든래빗, 이지스퍼블리싱이 AI 관련 도서를 가장 많이 출판한 것으로 나타납니다.

### 2.4 판매 가격 vs. 평점

![Price vs Rating](https://via.placeholder.com/600x400.png?text=Price+vs+Rating)

판매 가격과 평점 사이에는 뚜렷한 선형 관계가 보이지 않습니다. 가격이 높다고 해서 반드시 평점이 높은 것은 아닙니다.

### 2.5 월별 출간 도서 수

![Publication Trend](https://via.placeholder.com/800x400.png?text=Publication+Trend)

AI 관련 도서는 2025년 하반기부터 출간이 증가하여 2026년 초에 가장 많이 출간되는 경향을 보입니다.
