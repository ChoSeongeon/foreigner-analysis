import streamlit as st
import pandas as pd
import sqlite3
import os
import plotly.express as px

# 1. 페이지 설정 및 데이터베이스 연결 체크
st.set_page_config(page_title="강원도 외국인 관광 인사이트", layout="wide")

DB_PATH = "강릉.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

# 데이터베이스 파일 존재 여부 확인
if not os.path.exists(DB_PATH):
    st.error(f"❌ '{DB_PATH}' 파일을 찾을 수 없습니다. 데이터베이스 파일이 같은 폴더에 있는지 확인해주세요.")
    st.stop()

st.title("외국인 관광객 인사이트 대시보드")
st.markdown("강원도를 방문하는 외국인들의 소비 패턴과 방문 트렌드를 분석합니다.")

# 데이터 조회를 위한 함수
def run_query(q):
    with get_connection() as conn:
        return pd.read_sql(q, conn)

# ---------------------------------------------------------
# 1. 1인당 객단가 비교 (외국인 vs 외지인)
# ---------------------------------------------------------
st.header("1. 외국인·외지인 관광객 객단가 비교")

# SQL 쿼리에서 ROUND(..., 2)를 ROUND(..., 0)으로 수정하여 소수점을 제거했습니다.
sql1 = """
SELECT
    ROUND((SELECT SUM(c.지역관광소비액_백만원 * 1000000.0) FROM 외국인관광소비 c WHERE c.기준년월일 BETWEEN 202505 AND 202604) /
          (SELECT SUM(v.방문자수) FROM 외국인방문자수 v WHERE v.기준년월일 BETWEEN 202505 AND 202604), 0) AS 외국인_평균객단가,
    ROUND((SELECT SUM(s.관광소비액_백만원 * 1000000.0) FROM 전국대비관광소비추이외지인 s WHERE s.기준연월 BETWEEN 202505 AND 202604 AND s.지역명 = '강원특별자치도') /
          (SELECT SUM(o.방문자수) FROM 외지인방문자수 o WHERE o.기준년월 BETWEEN 202505 AND 202604), 0) AS 외지인_평균객단가;
"""
df1 = run_query(sql1)

col1_1, col1_2 = st.columns([1, 1])
with col1_1:
    st.subheader("📊 객단가 비교")
    st.table(df1.style.format("{:,.0f} (원)"))
with col1_2:
    st.subheader("💻 사용한 SQL")
    st.code(sql1, language='sql')

# 인사이트 파트 위에 '참고' 파트를 새로 추가했습니다.
# 필요에 따라 안에 들어갈 내용을 수정하여 사용하세요.
# 1. 참고 파트 (가장 위로 이동, 위아래 여백 10px 유지)
st.markdown(
    """
    <div style="
        background-color: #f8f9fa; 
        padding: 18px 22px; 
        border-radius: 0.5rem; 
        margin-top: 10px;
        margin-bottom: 10px;
        border: none;
    ">
        <span style="font-weight: bold; font-size: 1.1em;">📌 참고</span><br>
        <div style="color: #212529; line-height: 1.9; font-size: 14px; margin-top: 6px;">
            •&nbsp;&nbsp;본 분석은 2025년 5월~2026년 4월 기준 데이터를 활용하였습니다.<br>
            •&nbsp;&nbsp;외지인은 강원특별자치도 외 지역에 거주하는 국내 방문자를 의미합니다.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# 2. 가설 설정 파트 (가운데로 이동, 위아래 여백 10px 유지)
st.markdown(
    """
    <div style="
        background-color: #f1f9f5; 
        padding: 18px 22px; 
        border-radius: 0.5rem; 
        margin-top: 10px;
        margin-bottom: 10px;
        border: none;
    ">
        <span style="font-weight: bold; font-size: 1.1em; color: #1e4620;">❓ 가설 설정</span><br>
        <div style="color: #212529; line-height: 1.9; font-size: 14px; margin-top: 6px;">
            •&nbsp;&nbsp;외국인 방문객의 평균 객단가는 외지인 방문객의 평균 객단가보다 높을 것이다.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# 3. 인사이트 파트 (마지막 위치 유지, 첫 줄 서식 및 여백 10px 유지)
st.markdown(
    """
    <div style="
        background-color: #e8f0fe; 
        padding: 18px 22px; 
        border-radius: 0.5rem; 
        margin-top: 10px;
        margin-bottom: 10px;
        border: none;
    ">
        <span style="font-weight: bold; font-size: 1.1em; color: #1a73e8;">💡 인사이트</span><br>
        <div style="line-height: 1.9; margin-top: 6px;">
            <span style="color: #000000; font-weight: bold; font-size: 15.5px;">
                •&nbsp;&nbsp;분석 결과, 외국인 방문객의 평균 객단가는 외지인 방문객보다 낮게 나타났다.
            </span><br>
            <span style="color: #212529; font-size: 14px;">
                •&nbsp;&nbsp;원인 분석 결과 필리핀(9.3%), 베트남(8.3%) 방문객 비중이 높게 나타났으며, 이들 중 일부는 관광보다 취업·근로 목적 방문 비중이 높은 것으로 추정된다.<br>
                •&nbsp;&nbsp;따라서 외국인 방문객 전체를 관광객으로 간주하기보다 방문 목적을 고려한 세분화 분석이 필요하다.
            </span>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# ---------------------------------------------------------
# 2. 국가별 평균 방문자 비율+소비율 상위 3개국
# ---------------------------------------------------------
st.divider()
st.header("2. 강원도 방문·소비 통합 기여도 상위 국가")
sql2 = """
WITH Avg_Visit AS (
    SELECT 국가, AVG(방문자_비율) AS 평균_방문_비율 FROM 외국인방문합본
    WHERE 국가 <> '기타' AND 연도 BETWEEN 2023 AND 2025 GROUP BY 국가), 
Avg_Consumption AS (
    SELECT 국가, AVG(소비_비율) AS 평균_소비_비율 FROM 외국인소비합본
    WHERE 국가 <> '기타' AND 연도 BETWEEN 2023 AND 2025 GROUP BY 국가),
Combined_Metrics AS (
    SELECT V.국가, V.평균_방문_비율, C.평균_소비_비율, (V.평균_방문_비율 + C.평균_소비_비율) AS 총_합산_점수,
    ROW_NUMBER() OVER (ORDER BY (V.평균_방문_비율 + C.평균_소비_비율) DESC) AS 통합_순위
    FROM Avg_Visit V INNER JOIN Avg_Consumption C ON V.국가 = C.국가)
SELECT 통합_순위, 국가, ROUND(평균_방문비율_3개년, 2) as 평균_방문비율_3개년, ROUND(평균_소비비율_3개년, 2) as 평균_소비비율_3개년, ROUND(총_합산_점수, 2) as 총_합산_점수 
FROM (SELECT 통합_순위, 국가, 평균_방문_비율 as 평균_방문비율_3개년, 평균_소비_비율 as 평균_소비비율_3개년, 총_합산_점수 FROM Combined_Metrics WHERE 통합_순위 <= 3);
"""
df2 = run_query(sql2)

col2_1, col2_2 = st.columns([2, 1])
with col2_1:
    fig2 = px.bar(df2, x='국가', y='총_합산_점수', text='총_합산_점수', color='국가', title="강원도 방문 및 소비 비중 상위 국가")
    st.plotly_chart(fig2, use_container_width=True)
with col2_2:
    st.subheader("💻 사용한 SQL")
    st.code(sql2, language='sql')

st.markdown(
    """
    <div style="
        background-color: #f8f9fa; 
        padding: 18px 22px; 
        border-radius: 0.5rem; 
        margin-top: 10px;
        margin-bottom: 10px;
        border: none;
    ">
        <span style="font-weight: bold; font-size: 1.1em;">📌 참고</span><br>
        <div style="color: #212529; line-height: 1.9; font-size: 14px; margin-top: 6px;">
            •&nbsp;&nbsp;본 분석은 2023년~2025년 데이터를 활용하였습니다.<br>
            •&nbsp;&nbsp;국가별 평균 방문 비율과 평균 소비금액 비율을 합산하여 통합 점수를 산출하였습니다.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# 2. 인사이트 파트 (마지막 위치 유지, 첫 줄 서식 및 여백 10px 유지)
st.markdown(
    """
    <div style="
        background-color: #e8f0fe; 
        padding: 18px 22px; 
        border-radius: 0.5rem; 
        margin-top: 10px;
        margin-bottom: 10px;
        border: none;
    ">
        <span style="font-weight: bold; font-size: 1.1em; color: #1a73e8;">💡 인사이트</span><br>
        <div style="line-height: 1.9; margin-top: 6px;">
            <span style="color: #000000; font-weight: bold; font-size: 15.5px;">
                •&nbsp;&nbsp;미국, 싱가포르, 중국은 방문 비율과 소비 비율 모두 높은 국가로 나타났다.
            </span><br>
            <span style="color: #212529; font-size: 14px;">
                •&nbsp;&nbsp;해당 국가 관광객은 강원도 관광산업에 대한 기여도가 높은 핵심 수요층으로 판단된다.<br>
                •&nbsp;&nbsp;향후 국가별 특성을 반영한 맞춤형 관광 콘텐츠와 마케팅 전략 수립이 필요하다.
            </span>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

import matplotlib.pyplot as plt
from wordcloud import WordCloud

# ---------------------------------------------------------
# 3. 미국/중국 선호 콘텐츠 (Top 3)
# ---------------------------------------------------------
st.divider()
st.header("3. 미국/중국 선호 콘텐츠 (Top 3)")

sql3 = """
WITH Avg_Content_Consumption AS (
    SELECT 조사국가명 AS 국가, 콘텐츠URL AS 콘텐츠종류, AVG(CAST(전체총합수 AS DECIMAL(10,2))) AS 평균_소비_비중
    FROM 한국문화콘텐츠소비
    WHERE 조사국가명 IN ('미국', '중국') AND 보고서년도내용 IN ('2023', '2024', '2025') AND 항목명 LIKE '%비중%'
    GROUP BY 조사국가명, 콘텐츠URL
),
Ranked_Content AS (
    SELECT 국가, 콘텐츠종류, 평균_소비_비중, ROW_NUMBER() OVER (PARTITION BY 국가 ORDER BY 평균_소비_비중 DESC) AS 콘텐츠_순위
    FROM Avg_Content_Consumption
)
SELECT 국가, 콘텐츠_순위 AS 순위, 콘텐츠종류, ROUND(평균_소비_비중, 2) AS 평균_소비비중_퍼센트
FROM Ranked_Content WHERE 콘텐츠_순위 <= 3;
"""
df3 = run_query(sql3)

# 1. 시각화 영역과 SQL 영역 분할
col3_1, col3_2 = st.columns([1, 1])

with col3_1:
    # -----------------------------------------------------------------
    # 소제목 디자인 일치화 (상단 타이틀 배치)
    # -----------------------------------------------------------------
    st.markdown(
        """
        <div style="display: flex; justify-content: space-between; width: 100%; margin-top: 5px; margin-bottom: 15px; padding-left: 2px;">
            <div style="width: 50%; text-align: left; font-family: 'Source Sans Pro', sans-serif; color: #31333f; font-weight: 600; font-size: 14px;">미국 선호 콘텐츠</div>
            <div style="width: 50%; text-align: left; font-family: 'Source Sans Pro', sans-serif; color: #31333f; font-weight: 600; font-size: 14px; padding-left: 15px;">중국 선호 콘텐츠</div>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # -----------------------------------------------------------------
    # 정밀 시각화 엔진 (미국 파트 위아래 적층 레이아웃)
    # -----------------------------------------------------------------
    import matplotlib.pyplot as plt
    import matplotlib.font_manager as fm
    import platform
    
    # OS별 기본 한글 폰트 자동 지정
    if platform.system() == 'Windows':
        plt.rc('font', family='Malgun Gothic')
    elif platform.system() == 'Darwin':  # 맥
        plt.rc('font', family='AppleGothic')
    else:  # 리눅스/스트림릿 클라우드 서버 환경
        plt.rc('font', family='NanumGothic' if 'NanumGothic' in [f.name for f in fm.fontManager.ttflist] else 'sans-serif')
    
    # 도화지 크기 설정 (7, 4.2 규격 유지)
    fig, axes = plt.subplots(1, 2, figsize=(7, 4.2), facecolor='white')
    
    # 1. 미국 데이터 강제 매핑 (하위 단어 세로 적층 구조)
    ax_us = axes[0]
    ax_us.set_facecolor('white')
    
    # [해결] 1위 뷰티를 가장 상단에 큼직하게 배치
    ax_us.text(0.5, 0.76, '뷰티', fontsize=110, weight='black', color='#1e5096', ha='center', va='
with col3_2:
    # 요청하신 '💻 사용한 SQL' 대제목 추가
    st.subheader("💻 사용한 SQL")
    st.code(sql3, language='sql')

# ---------------------------------------------------------
# 기존 하단 컴포넌트 간격 유지용 마진 박스 및 인사이트
# ---------------------------------------------------------
st.markdown(
    """
    <div style="
        background-color: #e8f0fe; 
        padding: 18px 22px; 
        border-radius: 0.5rem; 
        margin-top: 20px;
        margin-bottom: 10px;
        border: none;
    ">
        <span style="font-weight: bold; font-size: 1.1em; color: #1a73e8;">💡 인사이트</span><br>
        <div style="line-height: 1.9; margin-top: 6px; color: #212529; font-size: 14px;">
            •&nbsp;&nbsp;미국 관광객은 드라마/영화 등 엔터테인먼트에, 중국 관광객은 쇼핑이나 특정 앱 서비스 비중이 높을 수 있습니다.<br>
            •&nbsp;&nbsp;국가별로 관심 있는 콘텐츠가 다르므로 타겟팅된 홍보 자료 제작이 필요합니다.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# ---------------------------------------------------------
# 4 & 5. 소비 분야 순위 (강원 vs 전국)
# ---------------------------------------------------------
st.divider()
st.header("4 & 5. 외국인 신용카드 소비 트렌드")

col4, col5 = st.columns(2)

with col4:
    st.subheader("📍 강원도 내 소비 순위")
    sql4 = """
    WITH Yearly_Category_Base AS (
        SELECT 연도, 카테고리_대분류, MAX(카테고리_대분류_소비_비율) AS 대분류_소비_비율
        FROM 강원도소비유형합본 GROUP BY 연도, 카테고리_대분류
    ),
    Ranked_Category AS (
        SELECT 연도, 카테고리_대분류, 대분류_소비_비율, ROW_NUMBER() OVER (PARTITION BY 연도 ORDER BY 대분류_소비_비율 DESC) AS 순위
        FROM Yearly_Category_Base
    )
    SELECT 연도, 순위, 카테고리_대분류, ROUND(대분류_소비_비율, 1) || '%' AS 소비_비율
    FROM Ranked_Category WHERE 순위 <= 3 ORDER BY 연도 ASC, 순위 ASC;
    """
    st.dataframe(run_query(sql4))

with col5:
    st.subheader("🇰🇷 전국 소비 순위")
    sql5 = """
    WITH Yearly_Amount_2023 AS (
        SELECT '2023년' AS 연도, 소비_카테고리_대분류 AS 업종_대분류, SUM(소비액_2023) AS 총_소비액, ROW_NUMBER() OVER (ORDER BY SUM(소비액_2023) DESC) AS 순위
        FROM 전국소비유형 WHERE 필터_대분류 = '전체' GROUP BY 소비_카테고리_대분류
    ),
    Yearly_Amount_2024 AS (
        SELECT '2024년' AS 연도, 소비_카테고리_대분류 AS 업종_대분류, SUM(소비액_2024) AS 총_소비액, ROW_NUMBER() OVER (ORDER BY SUM(소비액_2024) DESC) AS 순위
        FROM 전국소비유형 WHERE 필터_대분류 = '전체' GROUP BY 소비_카테고리_대분류
    )
    SELECT 연도, 순위, 업종_대분류, ROUND(총_소비액, 2) AS 소비액_USD FROM Yearly_Amount_2023 WHERE 순위 <= 4
    UNION ALL
    SELECT 연도, 순위, 업종_대분류, ROUND(총_소비액, 2) AS 소비액_USD FROM Yearly_Amount_2024 WHERE 순위 <= 4;
    """
    st.dataframe(run_query(sql5))

st.info("**💡 인사이트**\n- 강원도는 전국 트렌드와 달리 숙박이나 음식점 비중이 높을 가능성이 큽니다.\n- 전국 대비 강원도만의 특화된 소비 업종을 발굴하여 홍보할 필요가 있습니다.")


# ---------------------------------------------------------
# 6. 강원도 쇼핑업 상세 분석
# ---------------------------------------------------------
st.divider()
st.header("6. 강원도 외국인 쇼핑 상세")
sql6 = """
WITH Ranked_Shopping_Subcategory AS (
    SELECT 연도, 카테고리_대분류 AS 대분류, 카테고리_중분류 AS 중분류, 카테고리_중분류_소비_비율 AS 중분류_소비_비율,
    ROW_NUMBER() OVER (PARTITION BY 연도 ORDER BY 카테고리_중분류_소비_비율 DESC) AS 순위
    FROM 강원도소비유형합본 WHERE 카테고리_대분류 = '쇼핑업'
)
SELECT 연도, 순위, 중분류, CAST(ROUND(중분류_소비_비율, 1) AS VARCHAR) || '%' AS 중분류_소비_비율
FROM Ranked_Shopping_Subcategory WHERE 순위 <= 3 ORDER BY 연도 ASC, 순위 ASC;
"""
df6 = run_query(sql6)
st.table(df6)
st.code(sql6, language='sql')
st.info("**💡 인사이트**\n- 쇼핑 중에서도 어떤 품목(면세점, 대형마트 등)에 집중하는지 알 수 있습니다.\n- 특정 중분류의 인기가 높다면 해당 업종의 외국인 결제 편의성(간편결제 등)을 강화해야 합니다.")
