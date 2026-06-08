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

# 메인 타이틀 및 서브 타이틀 글자 크기 확대
st.markdown('<h1 style="font-size: 34px; font-weight: bold; margin-bottom: 5px;">외국인 관광객 인사이트 대시보드</h1>', unsafe_allow_html=True)
st.markdown('<p style="font-size: 18px; color: #555555; margin-bottom: 25px;">강원도를 방문하는 외국인들의 소비 패턴과 방문 트렌드를 분석합니다.</p>', unsafe_allow_html=True)

# 데이터 조회를 위한 함수
def run_query(q):
    with get_connection() as conn:
        return pd.read_sql(q, conn)

# ---------------------------------------------------------
# 1. 1인당 객단가 비교 (외국인 vs 외지인)
# ---------------------------------------------------------
st.markdown('<h2 style="font-size: 26px; font-weight: bold; margin-top: 20px; margin-bottom: 15px;">1. 외국인·외지인 관광객 객단가 비교</h2>', unsafe_allow_html=True)

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
    st.markdown('<h3 style="font-size: 20px; font-weight: bold; margin-bottom: 10px;">📊 객단가 비교</h3>', unsafe_allow_html=True)
    # 테이블 내부 텍스트 크기 확대를 위한 컴포넌트 커스텀 스타일링
    st.write(
        f"""
        <style>
            div[data-testid="stTable"] table {{ font-size: 17px !important; }}
        </style>
        """, unsafe_allow_html=True
    )
    st.table(df1.style.format("{:,.0f} (원)"))
with col1_2:
    st.markdown('<h3 style="font-size: 20px; font-weight: bold; margin-bottom: 10px;">💻 사용한 SQL</h3>', unsafe_allow_html=True)
    st.code(sql1, language='sql')

# 1. 참고 파트 (글자 크기 확대 및 스타일 조정)
st.markdown(
    """
    <div style="
        background-color: #f8f9fa; 
        padding: 22px 26px; 
        border-radius: 0.5rem; 
        margin-top: 15px;
        margin-bottom: 15px;
        border: none;
    ">
        <span style="font-weight: bold; font-size: 1.3em; color: #333333;">📌 참고</span><br>
        <div style="color: #212529; line-height: 2.0; font-size: 16px; margin-top: 8px;">
            •&nbsp;&nbsp;본 분석은 2025년 5월~2026년 4월 기준 데이터를 활용하였습니다.<br>
            •&nbsp;&nbsp;외지인은 강원특별자치도 외 지역에 거주하는 국내 방문자를 의미합니다.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# 2. 가설 설정 파트 (글자 크기 확대 및 스타일 조정)
st.markdown(
    """
    <div style="
        background-color: #f1f9f5; 
        padding: 22px 26px; 
        border-radius: 0.5rem; 
        margin-top: 15px;
        margin-bottom: 15px;
        border: none;
    ">
        <span style="font-weight: bold; font-size: 1.3em; color: #1e4620;">❓ 가설 설정</span><br>
        <div style="color: #212529; line-height: 2.0; font-size: 16px; margin-top: 8px;">
            •&nbsp;&nbsp;외국인 방문객의 평균 객단가는 외지인 방문객의 평균 객단가보다 높을 것이다.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# 3. 인사이트 파트 (글자 크기 확대 및 스타일 조정)
st.markdown(
    """
    <div style="
        background-color: #e8f0fe; 
        padding: 22px 26px; 
        border-radius: 0.5rem; 
        margin-top: 15px;
        margin-bottom: 15px;
        border: none;
    ">
        <span style="font-weight: bold; font-size: 1.3em; color: #1a73e8;">💡 인사이트</span><br>
        <div style="line-height: 2.0; margin-top: 8px;">
            <span style="color: #000000; font-weight: bold; font-size: 17.5px;">
                •&nbsp;&nbsp;분석 결과, 외국인 방문객의 평균 객단가는 외지인 방문객보다 낮게 나타났다.
            </span><br>
            <span style="color: #212529; font-size: 16px;">
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
st.markdown('<h2 style="font-size: 26px; font-weight: bold; margin-top: 20px; margin-bottom: 15px;">2. 강원도 방문·소비 통합 기여도 상위 국가</h2>', unsafe_allow_html=True)
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
    fig2.update_layout(title_font_size=20, font_size=14) # Plotly 차트 글씨 크기 확대
    st.plotly_chart(fig2, use_container_width=True)
with col2_2:
    st.markdown('<h3 style="font-size: 20px; font-weight: bold; margin-bottom: 10px;">💻 사용한 SQL</h3>', unsafe_allow_html=True)
    st.code(sql2, language='sql')

st.markdown(
    """
    <div style="
        background-color: #f8f9fa; 
        padding: 22px 26px; 
        border-radius: 0.5rem; 
        margin-top: 15px;
        margin-bottom: 15px;
        border: none;
    ">
        <span style="font-weight: bold; font-size: 1.3em; color: #333333;">📌 참고</span><br>
        <div style="color: #212529; line-height: 2.0; font-size: 16px; margin-top: 8px;">
            •&nbsp;&nbsp;본 분석은 2023년~2025년 데이터를 활용하였습니다.<br>
            •&nbsp;&nbsp;국가별 평균 방문 비율과 평균 소비금액 비율을 합산하여 통합 점수를 산출하였습니다.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div style="
        background-color: #e8f0fe; 
        padding: 22px 26px; 
        border-radius: 0.5rem; 
        margin-top: 15px;
        margin-bottom: 15px;
        border: none;
    ">
        <span style="font-weight: bold; font-size: 1.3em; color: #1a73e8;">💡 인사이트</span><br>
        <div style="line-height: 2.0; margin-top: 8px;">
            <span style="color: #000000; font-weight: bold; font-size: 17.5px;">
                •&nbsp;&nbsp;미국, 싱가포르, 중국은 방문 비율과 소비 비율 모두 높은 국가로 나타났다.
            </span><br>
            <span style="color: #212529; font-size: 16px;">
                •&nbsp;&nbsp;해당 국가 관광객은 강원도 관광산업에 대한 기여도가 높은 핵심 수요층으로 판단된다.<br>
                •&nbsp;&nbsp;향후 국가별 특성을 반영한 맞춤형 관광 콘텐츠와 마케팅 전략 수립이 필요하다.
            </span>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


# ---------------------------------------------------------
# 3. 미국/중국 선호 콘텐츠 (Top 3)
# ---------------------------------------------------------
st.divider()
st.markdown('<h2 style="font-size: 26px; font-weight: bold; margin-top: 20px; margin-bottom: 15px;">3. 미국/중국 선호 콘텐츠 (Top 3)</h2>', unsafe_allow_html=True)

sql3 = """
WITH Avg_Content_Consumption AS (
    SELECT 조사국가명 AS 국가, 콘텐츠URL AS 콘텐츠종류, AVG(CAST(전체총합수 AS DECIMAL(10,2))) AS 평균_소비_비중
    FROM 한국문화콘텐츠소비
    WHERE 조사국가명 IN ('미국', '중국') AND 보고서년도내용 IN ('2023', '2024', '2025') AND 항목명 LIKE '%비중%'
    GROUP BY 조사국가명, 콘텐츠URL),
Ranked_Content AS (
    SELECT 국가, 콘텐츠종류, 평균_소비_비중, ROW_NUMBER() OVER (PARTITION BY 국가 ORDER BY 평균_소비_비중 DESC) AS 콘텐츠_순위
    FROM Avg_Content_Consumption)
SELECT 국가, 콘텐츠_순위 AS 순위, 콘텐츠종류, ROUND(평균_소비_비중, 2) AS 평균_소비비중_퍼센트
FROM Ranked_Content WHERE 콘텐츠_순위 <= 3;
"""
df3 = run_query(sql3)

col3_1, col3_2 = st.columns([1, 1])

with col3_1:
    # 소제목 디자인은 글씨 크기를 16px로 확대
    st.markdown(
        """
        <div style="display: flex; justify-content: space-between; width: 100%; margin-top: 5px; margin-bottom: 15px; padding-left: 2px;">
            <div style="width: 50%; text-align: left; font-family: 'Source Sans Pro', sans-serif; color: #31333f; font-weight: 600; font-size: 16px;">미국 선호 콘텐츠</div>
            <div style="width: 50%; text-align: left; font-family: 'Source Sans Pro', sans-serif; color: #31333f; font-weight: 600; font-size: 16px; padding-left: 15px;">중국 선호 콘텐츠</div>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # ⚠️ [보안 유지] 요청하신 대로 시각화 내부 텍스트(80px, 60px 등)의 크기는 '절대' 건드리지 않고 원본 유지함
    st.markdown(
        """
        <div style="display: flex; width: 100%; height: 330px; background-color: white; border-radius: 4px; box-sizing: border-box;">
            <div style="width: 50%; display: flex; flex-direction: column; justify-content: center; align-items: center; border-right: 1px solid #eeeeee; padding-right: 10px;">
                <div style="font-size: 80px; font-weight: 900; color: #1e5096; line-height: 1.1; letter-spacing: -2px; margin-bottom: 5px;">뷰티</div>
                <div style="font-size: 60px; font-weight: 900; color: #64a0dc; line-height: 1.1; letter-spacing: -1px; margin-bottom: 5px;">웹툰</div>
                <div style="font-size: 60px; font-weight: 900; color: #64a0dc; line-height: 1.1; letter-spacing: -1px;">패션</div>
            </div>
            <div style="width: 50%; display: flex; flex-direction: column; justify-content: center; align-items: center; padding-left: 10px;">
                <div style="font-size: 83px; font-weight: 900; color: #8b0000; line-height: 1.1; letter-spacing: -2px; margin-bottom: 5px;">뷰티</div>
                <div style="font-size: 73px; font-weight: 900; color: #e03a3a; line-height: 1.1; letter-spacing: -1px; margin-bottom: 5px;">패션</div>
                <div style="font-size: 48px; font-weight: 900; color: #f39292; line-height: 1.1; letter-spacing: -1px;">드라마</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col3_2:
    st.markdown('<h3 style="font-size: 20px; font-weight: bold; margin-bottom: 10px;">💻 사용한 SQL</h3>', unsafe_allow_html=True)
    st.code(sql3, language="sql")

# 참고 파트 글자 크기 확대
st.markdown(
    """
    <div style="
        background-color: #f8f9fa; 
        padding: 22px 26px; 
        border-radius: 0.5rem; 
        margin-top: 15px;
        margin-bottom: 15px;
        border: none;
    ">
        <span style="font-weight: bold; font-size: 1.3em; color: #333333;">📌 참고</span><br>
        <div style="color: #212529; line-height: 2.0; font-size: 16px; margin-top: 8px;">
            •&nbsp;&nbsp;본 분석은 2023~2025년 데이터를 활용하였습니다.<br>
            •&nbsp;&nbsp;방문·소비 통합 기여도 상위 국가 중 싱가포르는 한류 콘텐츠 선호도 데이터가 제공되지 않아 분석 대상에서 제외하였습니다.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# 결과 파트 글자 크기 확대
st.markdown(
    """
    <div style="
        background-color: #f1f9f5; 
        padding: 22px 26px; 
        border-radius: 0.5rem; 
        margin-top: 15px;
        margin-bottom: 15px;
        border: none;
    ">
        <span style="font-weight: bold; font-size: 1.3em; color: #1e4620;">📊 결과</span><br>
        <div style="color: #212529; line-height: 2.0; font-size: 16px; margin-top: 8px;">
            •&nbsp;&nbsp;미국은 뷰티(28.33%), 웹툰(27.33%), 패션(27.33%) 순으로 높은 소비 비중을 보였다.<br>
            •&nbsp;&nbsp;중국은 뷰티(40.00%), 패션(39.00%), 드라마(28.00%) 순으로 높은 소비 비중을 보였다.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# 인사이트 파트 글자 크기 확대
st.markdown(
    """
    <div style="
        background-color: #e8f0fe; 
        padding: 22px 26px; 
        border-radius: 0.5rem; 
        margin-top: 15px;
        margin-bottom: 15px;
        border: none;
    ">
        <span style="font-weight: bold; font-size: 1.3em; color: #1a73e8;">💡 인사이트</span><br>
        <div style="line-height: 2.0; margin-top: 8px;">
            <span style="color: #000000; font-weight: bold; font-size: 17.5px;">
                •&nbsp;&nbsp;미국과 중국 관광객 모두 뷰티·패션 등 K-라이프스타일 콘텐츠에 대한 관심이 높게 나타났다.
            </span><br>
            <span style="color: #212529; font-size: 16px;">
                •&nbsp;&nbsp;따라서 강원도 축제 및 관광 마케팅에서는 국가별 선호 콘텐츠를 반영한 맞춤형 프로그램 기획이 필요하다.
            </span>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


# -----------------------------------------------------------------
# 4 & 5. 외국인 신용카드 소비 트렌드 시각화 엔진 (+ SQL 박스 포함)
# -----------------------------------------------------------------
st.divider()
st.markdown('<h2 style="font-size: 26px; font-weight: bold; margin-top: 20px; margin-bottom: 15px;">4. 외국인 관광객 소비 패턴 분석</h2>', unsafe_allow_html=True)

강원_data = pd.DataFrame([
    {"연도": "2023", "카테고리": "숙박업", "비율": 38.3},
    {"연도": "2023", "카테고리": "식음료업", "비율": 24.4},
    {"연도": "2023", "카테고리": "쇼핑업", "비율": 23.9},
    {"연도": "2024", "카테고리": "숙박업", "비율": 32.4},
    {"연도": "2024", "카테고리": "식음료업", "비율": 28.2},
    {"연도": "2024", "카테고리": "쇼핑업", "비율": 24.9}
])

전국_data = pd.DataFrame([
    {"연도": "2023", "카테고리": "국제 교통비", "비율": 745.2},
    {"연도": "2023", "카테고리": "쇼핑비", "비율": 453.3},
    {"연도": "2023", "카테고리": "숙박비", "비율": 439.1},
    {"연도": "2023", "카테고리": "식음료비", "비율": 288.9},
    {"연도": "2024", "카테고리": "국제 교통비", "비율": 617.7},
    {"연도": "2024", "카테고리": "쇼핑비", "비율": 439.2},
    {"연도": "2024", "카테고리": "숙박비", "비율": 377.8},
    {"연도": "2024", "카테고리": "식음료비", "비율": 258.6}
])

col_left, col_right = st.columns(2)

# --- 1. [좌측 열] 강원도 내 소비 순위 그래프 글자 크기 확대 ---
with col_left:
    st.markdown('<div style="font-size:18px; font-weight:600; color:#31333F; margin-bottom:12px;">📍 강원도 내 소비 순위</div>', unsafe_allow_html=True)
    
    # 내부 텍스트 라벨과 타이틀 크기를 눈에 띄게 키웠습니다.
    st.markdown(
        """
        <div style="background-color: white; border: 1px solid #eeeeee; border-radius: 4px; padding: 18px; height: 380px; display: flex; flex-direction: column; justify-content: space-between; font-family: sans-serif;">
            <div>
                <div style="font-size: 14px; font-weight: bold; color: #333333; margin-bottom: 8px; text-align: left;">2023년</div>
                <div style="display: flex; align-items: center; margin-bottom: 8px;">
                    <div style="width: 70px; font-size: 13px; color: #444444; text-align: right; padding-right: 10px; font-weight: bold;">쇼핑업</div>
                    <div style="flex-grow: 1; background-color: #f0f2f6; height: 18px; border-radius: 2px; overflow: hidden;">
                        <div style="background-color: #2b5c8f; width: 47.8%; height: 100%;"></div>
                    </div>
                    <div style="width: 55px; font-size: 13px; font-weight: bold; color: #333333; padding-left: 8px;">23.9%</div>
                </div>
                <div style="display: flex; align-items: center; margin-bottom: 8px;">
                    <div style="width: 70px; font-size: 13px; color: #444444; text-align: right; padding-right: 10px; font-weight: bold;">식음료업</div>
                    <div style="flex-grow: 1; background-color: #f0f2f6; height: 18px; border-radius: 2px; overflow: hidden;">
                        <div style="background-color: #2b5c8f; width: 48.8%; height: 100%;"></div>
                    </div>
                    <div style="width: 55px; font-size: 13px; font-weight: bold; color: #333333; padding-left: 8px;">24.4%</div>
                </div>
                <div style="display: flex; align-items: center; margin-bottom: 10px;">
                    <div style="width: 70px; font-size: 13px; color: #444444; text-align: right; padding-right: 10px; font-weight: bold;">숙박업</div>
                    <div style="flex-grow: 1; background-color: #f0f2f6; height: 18px; border-radius: 2px; overflow: hidden;">
                        <div style="background-color: #2b5c8f; width: 76.6%; height: 100%;"></div>
                    </div>
                    <div style="width: 55px; font-size: 13px; font-weight: bold; color: #333333; padding-left: 8px;">38.3%</div>
                </div>
            </div>
            <hr style="margin: 10px 0; border: none; border-top: 1px dashed #dddddd;">
            <div>
                <div style="font-size: 14px; font-weight: bold; color: #333333; margin-bottom: 8px; text-align: left;">2024년</div>
                <div style="display: flex; align-items: center; margin-bottom: 8px;">
                    <div style="width: 70px; font-size: 13px; color: #444444; text-align: right; padding-right: 10px; font-weight: bold;">쇼핑업</div>
                    <div style="flex-grow: 1; background-color: #f0f2f6; height: 18px; border-radius: 2px; overflow: hidden;">
                        <div style="background-color: #4682b4; width: 49.8%; height: 100%;"></div>
                    </div>
                    <div style="width: 55px; font-size: 13px; font-weight: bold; color: #333333; padding-left: 8px;">24.9%</div>
                </div>
                <div style="display: flex; align-items: center; margin-bottom: 8px;">
                    <div style="width: 70px; font-size: 13px; color: #444444; text-align: right; padding-right: 10px; font-weight: bold;">식음료업</div>
                    <div style="flex-grow: 1; background-color: #f0f2f6; height: 18px; border-radius: 2px; overflow: hidden;">
                        <div style="background-color: #4682b4; width: 56.4%; height: 100%;"></div>
                    </div>
                    <div style="width: 55px; font-size: 13px; font-weight: bold; color: #333333; padding-left: 8px;">28.2%</div>
                </div>
                <div style="display: flex; align-items: center;">
                    <div style="width: 70px; font-size: 13px; color: #444444; text-align: right; padding-right: 10px; font-weight: bold;">숙박업</div>
                    <div style="flex-grow: 1; background-color: #f0f2f6; height: 18px; border-radius: 2px; overflow: hidden;">
                        <div style="background-color: #4682b4; width: 64.8%; height: 100%;"></div>
                    </div>
                    <div style="width: 55px; font-size: 13px; font-weight: bold; color: #333333; padding-left: 8px;">32.4%</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    with st.expander("💻 사용한 SQL"):
        st.code("""
WITH Ranked_Shopping_Subcategory AS (
    SELECT 
        연도,
        "카테고리 대분류" AS 대분류,
        "카테고리 중분류" AS 중분류,
        "카테고리 중분류 소비 비율" AS 중분류_소비_비율,
        ROW_NUMBER() OVER (PARTITION BY 연도 ORDER BY "카테고리 중분류 소비 비율" DESC) AS 순위
    FROM 강원도소비유 유형합본
    WHERE 
        "카테고리 대분류" = '쇼핑업'    
        AND 연도 IN (2023, 2024))
SELECT 
    연도,
    순위,
    대분류,
    중분류,
    CAST(ROUND(중분류_소비_비율, 1) AS VARCHAR) || '%' AS 중분류_소비_비율
FROM 
    Ranked_Shopping_Subcategory 
WHERE 
    순위 <= 3
ORDER BY 
    연도 ASC, 
    순위 ASC;
        """, language="sql")

# --- 2. [우측 열] 전국 소비 순위 그래프 및 SQL 글자 크기 확대 ---
with col_right:
    st.markdown('<div style="font-size:18px; font-weight:600; color:#31333F; margin-bottom:12px;">🇰🇷 전국 소비 순위</div>', unsafe_allow_html=True)
    
    st.markdown(
        """
        <div style="background-color: white; border: 1px solid #eeeeee; border-radius: 4px; padding: 18px; height: 380px; display: flex; flex-direction: column; justify-content: space-between; font-family: sans-serif;">
            <div>
                <div style="font-size: 14px; font-weight: bold; color: #333333; margin-bottom: 6px; text-align: left;">2023년</div>
                <div style="display: flex; align-items: center; margin-bottom: 6px;">
                    <div style="width: 80px; font-size: 13px; color: #444444; text-align: right; padding-right: 10px; font-weight: bold;">식음료비</div>
                    <div style="flex-grow: 1; background-color: #f0f2f6; height: 15px; border-radius: 2px; overflow: hidden;">
                        <div style="background-color: #a2d149; width: 30.4%; height: 100%;"></div>
                    </div>
                    <div style="width: 55px; font-size: 13px; font-weight: bold; color: #333333; padding-left: 8px;">288.9</div>
                </div>
                <div style="display: flex; align-items: center; margin-bottom: 6px;">
                    <div style="width: 80px; font-size: 13px; color: #444444; text-align: right; padding-right: 10px; font-weight: bold;">숙박비</div>
                    <div style="flex-grow: 1; background-color: #f0f2f6; height: 15px; border-radius: 2px; overflow: hidden;">
                        <div style="background-color: #a2d149; width: 46.2%; height: 100%;"></div>
                    </div>
                    <div style="width: 55px; font-size: 13px; font-weight: bold; color: #333333; padding-left: 8px;">439.1</div>
                </div>
                <div style="display: flex; align-items: center; margin-bottom: 6px;">
                    <div style="width: 80px; font-size: 13px; color: #444444; text-align: right; padding-right: 10px; font-weight: bold;">쇼핑비</div>
                    <div style="flex-grow: 1; background-color: #f0f2f6; height: 15px; border-radius: 2px; overflow: hidden;">
                        <div style="background-color: #a2d149; width: 47.7%; height: 100%;"></div>
                    </div>
                    <div style="width: 55px; font-size: 13px; font-weight: bold; color: #333333; padding-left: 8px;">453.3</div>
                </div>
                <div style="display: flex; align-items: center; margin-bottom: 6px;">
                    <div style="width: 80px; font-size: 13px; color: #444444; text-align: right; padding-right: 10px; font-weight: bold;">국제 교통비</div>
                    <div style="flex-grow: 1; background-color: #f0f2f6; height: 15px; border-radius: 2px; overflow: hidden;">
                        <div style="background-color: #a2d149; width: 78.4%; height: 100%;"></div>
                    </div>
                    <div style="width: 55px; font-size: 13px; font-weight: bold; color: #333333; padding-left: 8px;">745.2</div>
                </div>
            </div>
            <hr style="margin: 8px 0; border: none; border-top: 1px dashed #dddddd;">
            <div>
                <div style="font-size: 14px; font-weight: bold; color: #333333; margin-bottom: 6px; text-align: left;">2024년</div>
                <div style="display: flex; align-items: center; margin-bottom: 6px;">
                    <div style="width: 80px; font-size: 13px; color: #444444; text-align: right; padding-right: 10px; font-weight: bold;">식음료비</div>
                    <div style="flex-grow: 1; background-color: #f0f2f6; height: 15px; border-radius: 2px; overflow: hidden;">
                        <div style="background-color: #8bc34a; width: 27.2%; height: 100%;"></div>
                    </div>
                    <div style="width: 55px; font-size: 13px; font-weight: bold; color: #333333; padding-left: 8px;">258.6</div>
                </div>
                <div style="display: flex; align-items: center; margin-bottom: 6px;">
                    <div style="width: 80px; font-size: 13px; color: #444444; text-align: right; padding-right: 10px; font-weight: bold;">숙박비</div>
                    <div style="flex-grow: 1; background-color: #f0f2f6; height: 15px; border-radius: 2px; overflow: hidden;">
                        <div style="background-color: #8bc34a; width: 39.7%; height: 100%;"></div>
                    </div>
                    <div style="width: 55px; font-size: 13px; font-weight: bold; color: #333333; padding-left: 8px;">377.8</div>
                </div>
                <div style="display: flex; align-items: center; margin-bottom: 6px;">
                    <div style="width: 80px; font-size: 13px; color: #444444; text-align: right; padding-right: 10px; font-weight: bold;">쇼핑비</div>
                    <div style="flex-grow: 1; background-color: #f0f2f6; height: 15px; border-radius: 2px; overflow: hidden;">
                        <div style="background-color: #8bc34a; width: 46.2%; height: 100%;"></div>
                    </div>
                    <div style="width: 55px; font-size: 13px; font-weight: bold; color: #333333; padding-left: 8px;">439.2</div>
                </div>
                <div style="display: flex; align-items: center;">
                    <div style="width: 80px; font-size: 13px; color: #444444; text-align: right; padding-right: 10px; font-weight: bold;">국제 교통비</div>
                    <div style="flex-grow: 1; background-color: #f0f2f6; height: 15px; border-radius: 2px; overflow: hidden;">
                        <div style="background-color: #8bc34a; width: 65.0%; height: 100%;"></div>
                    </div>
                    <div style="width: 55px; font-size: 13px; font-weight: bold; color: #333333; padding-left: 8px;">617.7</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    with st.expander("💻 사용한 SQL"):
        st.code("""WITH Yearly_Amount_2023 AS ... (중략) ... ORDER BY 연도 ASC, 순위 ASC;""", language="sql")

# 하단 텍스트 및 박스 크기 확대
st.markdown(
    """
    <div style="
        background-color: #f8f9fa; 
        padding: 22px 26px; 
        border-radius: 0.5rem; 
        margin-top: 15px;
        margin-bottom: 15px;
        border: none;
    ">
        <span style="font-weight: bold; font-size: 1.3em; color: #333333;">📌 참고</span><br>
        <div style="color: #212529; line-height: 2.0; font-size: 16px; margin-top: 8px;">
            •&nbsp;&nbsp;본 분석은 2023~2024년 데이터를 활용하였습니다.<br>
            •&nbsp;&nbsp;외국인 방문객 신용카드 소비데이터를 활용하였습니다.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div style="
        background-color: #f1f9f5; 
        padding: 22px 26px; 
        border-radius: 0.5rem; 
        margin-top: 15px;
        margin-bottom: 15px;
        border: none;
    ">
        <span style="font-weight: bold; font-size: 1.3em; color: #1e4620;">📊 결과</span><br>
        <div style="color: #212529; line-height: 2.0; font-size: 16px; margin-top: 8px;">
            •&nbsp;&nbsp;외국인 관광객의 주요 소비 분야는 숙박·식음료·쇼핑으로 나타났다.<br>
            •&nbsp;&nbsp;강원도는 특히 숙박 및 식음료 소비가 높은 특징을 보인다.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div style="
        background-color: #e8f0fe; 
        padding: 22px 26px; 
        border-radius: 0.5rem; 
        margin-top: 15px;
        margin-bottom: 15px;
        border: none;
    ">
        <span style="font-weight: bold; font-size: 1.3em; color: #1a73e8;">💡 인사이트</span><br>
        <div style="line-height: 2.0; margin-top: 8px;">
            <span style="color: #000000; font-weight: bold; font-size: 17.5px;">
                •&nbsp;&nbsp;외국인 관광객의 주요 소비 분야인 숙박·식음료·쇼핑 산업을 중심으로 관광 상품과 서비스를 고도화할 필요가 있다.
            </span><br>
            <span style="color: #212529; font-size: 16px;">
                •&nbsp;&nbsp;지역 특색을 활용한 숙박 패키지, 미식 관광, 지역 특산품 쇼핑 콘텐츠를 확대한다면 외국인 관광객의 1인당 소비액 증가와 지역경제 활성화에 기여할 수 있을 것으로 기대된다.
            </span>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# ---------------------------------------------------------
# 5. 강원도 쇼핑업 상세 분석
# ---------------------------------------------------------
st.divider()
st.markdown('<h2 style="font-size: 26px; font-weight: bold; margin-top: 20px; margin-bottom: 15px;">5. 강원도 외국인 관광객 쇼핑 유형 분석</h2>', unsafe_allow_html=True)

sql6 = """
WITH Ranked_Shopping_Subcategory AS (
    SELECT 
        연도, 
        "카테고리 대분류" AS 대분류, 
        "카테고리 중분류" AS 중분류, 
        "카테고리 중분류 소비 비율" AS 중분류_소비_비율,
        ROW_NUMBER() OVER (PARTITION BY 연도 ORDER BY "카테고리 중분류 소비 비율" DESC) AS 순위
    FROM 강원도소비유형합본 
    WHERE "카테고리 대분류" = '쇼핑업'
      AND 연도 IN (2023, 2024)
)
SELECT 
    연도, 
    순위, 
    중분류, 
    CAST(ROUND(중분류_소비_비율, 1) AS VARCHAR) || '%' AS 중분류_소비_비율
FROM Ranked_Shopping_Subcategory 
WHERE 순위 <= 3 
ORDER BY 연도 ASC, 순위 ASC;
"""
df6 = run_query(sql6)

쇼핑_상세_data = pd.DataFrame([
    {"연도": "2023", "중분류": "기타관광쇼핑", "비율": 64.3},
    {"연도": "2023", "중분류": "대형쇼핑몰", "비율": 26.8},
    {"연도": "2023", "중분류": "레저용품쇼핑", "비율": 8.7},
    {"연도": "2024", "중분류": "기타관광쇼핑", "비율": 64.8},
    {"연도": "2024", "중분류": "대형쇼핑몰", "비율": 25.3},
    {"연도": "2024", "중분류": "레저용품쇼핑", "비율": 9.8}
])

col_graph, col_table = st.columns([1.2, 0.8])

# 5번 쇼핑업 상세 데이터 시각화 컴포넌트 내부 글씨 확대
with col_graph:
    st.markdown(
        """
        <div style="background-color: white; border: 1px solid #eeeeee; border-radius: 4px; padding: 18px; height: 380px; display: flex; flex-direction: column; justify-content: space-between; font-family: sans-serif;">
            <div>
                <div style="font-size: 14px; font-weight: bold; color: #333333; margin-bottom: 8px; text-align: left;">2023년 쇼핑 업종별 비중</div>
                <div style="display: flex; align-items: center; margin-bottom: 8px;">
                    <div style="width: 95px; font-size: 13px; color: #444444; text-align: right; padding-right: 10px; font-weight: bold;">레저용품쇼핑</div>
                    <div style="flex-grow: 1; background-color: #f0f2f6; height: 18px; border-radius: 2px; overflow: hidden;">
                        <div style="background-color: #E67E22; width: 10.8%; height: 100%;"></div>
                    </div>
                    <div style="width: 55px; font-size: 13px; font-weight: bold; color: #333333; padding-left: 8px;">8.7%</div>
                </div>
                <div style="display: flex; align-items: center; margin-bottom: 8px;">
                    <div style="width: 95px; font-size: 13px; color: #444444; text-align: right; padding-right: 10px; font-weight: bold;">대형쇼핑몰</div>
                    <div style="flex-grow: 1; background-color: #f0f2f6; height: 18px; border-radius: 2px; overflow: hidden;">
                        <div style="background-color: #E67E22; width: 33.5%; height: 100%;"></div>
                    </div>
                    <div style="width: 55px; font-size: 13px; font-weight: bold; color: #333333; padding-left: 8px;">26.8%</div>
                </div>
                <div style="display: flex; align-items: center; margin-bottom: 10px;">
                    <div style="width: 95px; font-size: 13px; color: #444444; text-align: right; padding-right: 10px; font-weight: bold;">기타관광쇼핑</div>
                    <div style="flex-grow: 1; background-color: #f0f2f6; height: 18px; border-radius: 2px; overflow: hidden;">
                        <div style="background-color: #E67E22; width: 80.3%; height: 100%;"></div>
                    </div>
                    <div style="width: 55px; font-size: 13px; font-weight: bold; color: #333333; padding-left: 8px;">64.3%</div>
                </div>
            </div>
            <hr style="margin: 10px 0; border: none; border-top: 1px dashed #dddddd;">
            <div>
                <div style="font-size: 14px; font-weight: bold; color: #333333; margin-bottom: 8px; text-align: left;">2024년 쇼핑 업종별 비중</div>
                <div style="display: flex; align-items: center; margin-bottom: 8px;">
                    <div style="width: 95px; font-size: 13px; color: #444444; text-align: right; padding-right: 10px; font-weight: bold;">레저용품쇼핑</div>
                    <div style="flex-grow: 1; background-color: #f0f2f6; height: 18px; border-radius: 2px; overflow: hidden;">
                        <div style="background-color: #F39C12; width: 12.2%; height: 100%;"></div>
                    </div>
                    <div style="width: 55px; font-size: 13px; font-weight: bold; color: #333333; padding-left: 8px;">9.8%</div>
                </div>
                <div style="display: flex; align-items: center; margin-bottom: 8px;">
                    <div style="width: 95px; font-size: 13px; color: #444444; text-align: right; padding-right: 10px; font-weight: bold;">대형쇼핑몰</div>
                    <div style="flex-grow: 1; background-color: #f0f2f6; height: 18px; border-radius: 2px; overflow: hidden;">
                        <div style="background-color: #F39C12; width: 31.6%; height: 100%;"></div>
                    </div>
                    <div style="width: 55px; font-size: 13px; font-weight: bold; color: #333333; padding-left: 8px;">25.3%</div>
                </div>
                <div style="display: flex; align-items: center;">
                    <div style="width: 95px; font-size: 13px; color: #444444; text-align: right; padding-right: 10px; font-weight: bold;">기타관광쇼핑</div>
                    <div style="flex-grow: 1; background-color: #f0f2f6; height: 18px; border-radius: 2px; overflow: hidden;">
                        <div style="background-color: #F39C12; width: 81.0%; height: 100%;"></div>
                    </div>
                    <div style="width: 55px; font-size: 13px; font-weight: bold; color: #333333; padding-left: 8px;">64.8%</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col_table:
    st.markdown('<div style="font-size:16px; font-weight:600; color:#555555; margin-bottom:10px;">📋 데이터 상세 보기</div>', unsafe_allow_html=True)
    # 데이터 테이블 내부 폰트 확대
    st.write(
        f"""
        <style>
            div[data-testid="stDataFrame"] table {{ font-size: 16px !important; }}
        </style>
        """, unsafe_allow_html=True
    )
    display_df = 쇼핑_상세_data.copy()
    display_df["비율"] = display_df["비율"].map(lambda x: f"{x:.1f}%")
    st.dataframe(display_df, use_container_width=True, hide_index=True)

st.write("") 
with st.expander("💻 사용한 SQL"):
    st.code(sql6, language="sql")

# 마지막 파트 안내 컴포넌트 글자 크기 확대
st.markdown(
    """
    <div style="
        background-color: #f8f9fa; 
        padding: 22px 26px; 
        border-radius: 0.5rem; 
        margin-top: 15px;
        margin-bottom: 15px;
        border: none;
    ">
        <span style="font-weight: bold; font-size: 1.3em; color: #333333;">📌 참고</span><br>
        <div style="color: #212529; line-height: 2.0; font-size: 16px; margin-top: 8px;">
            •&nbsp;&nbsp;본 분석은 2023년~2025년 외국인 방문객 신용카드 소비 데이터를 활용하였습니다.<br>
            •&nbsp;&nbsp;기타관광쇼핑에는 기념품, 사진기, 슈퍼마켓, 편의점, 농축수산물, 공예품, 예술품, 의류, 신발, 가방류, 생활용품, 귀금속 등 관광객이 여행 중 구매하는 다양한 소매·관광 상품 업종이 포함됩니다.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div style="
        background-color: #f1f9f5; 
        padding: 22px 26px; 
        border-radius: 0.5rem; 
        margin-top: 15px;
        margin-bottom: 15px;
        border: none;
    ">
        <span style="font-weight: bold; font-size: 1.3em; color: #1e4620;">📊 결과</span><br>
        <div style="color: #212529; line-height: 2.0; font-size: 16px; margin-top: 8px;">
            •&nbsp;&nbsp;강원도 외국인 관광객의 쇼핑 소비는 3년 연속 기타관광쇼핑에 64% 이상 집중되어 있어 관광 관련 소매·기념품 소비가 쇼핑 지출의 핵심인 것으로 나타남
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div style="
        background-color: #e8f0fe; 
        padding: 22px 26px; 
        border-radius: 0.5rem; 
        margin-top: 15px;
        margin-bottom: 15px;
        border: none;
    ">
        <span style="font-weight: bold; font-size: 1.3em; color: #1a73e8;">💡 인사이트</span><br>
        <div style="line-height: 2.0; margin-top: 8px;">
            <span style="color: #000000; font-weight: bold; font-size: 17.5px;">
                •&nbsp;&nbsp;강원도 특산품, 지역 한정 굿즈, 전통 공예품, 지역 브랜드 상품 등 관광 목적 소비를 유도할 수 있는 차별화된 쇼핑 콘텐츠를 확대할 필요가 있다.
            </span><br>
            <span style="color: #212529; font-size: 16px;">
                •&nbsp;&nbsp;특히 기타관광쇼핑이 전체 쇼핑 소비의 약 65%를 차지하고 있는 만큼, 관광지 인근 상점과 특산품 판매장의 경쟁력 강화가 관광 소비 증대에 중요한 역할을 할 것으로 판단됨
            </span>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)
