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
    GROUP BY 조사국가명, 콘텐츠URL),
Ranked_Content AS (
    SELECT 국가, 콘텐츠종류, 평균_소비_비중, ROW_NUMBER() OVER (PARTITION BY 국가 ORDER BY 평균_소비_비중 DESC) AS 콘텐츠_순위
    FROM Avg_Content_Consumption)
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
    # 정밀 시각화 엔진 (잘림 현상 교정 완료)
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
    
    # 1위 뷰티를 가장 상단에 큼직하게 배치
    ax_us.text(0.5, 0.76, '뷰티', fontsize=110, weight='black', color='#1e5096', ha='center', va='center')
    
    # [수정 완료] 문자열 잘림 현상을 해결하고 웹툰과 패션을 위아래로 깔끔하게 떨어뜨렸습니다.
    ax_us.text(0.5, 0.44, '웹툰', fontsize=82, weight='black', color='#64a0dc', ha='center', va='center')
    ax_us.text(0.5, 0.15, '패션', fontsize=82, weight='black', color='#64a0dc', ha='center', va='center')
    
    ax_us.axis('off')
    ax_us.set_xlim(0.05, 0.95)
    ax_us.set_ylim(0.05, 0.95)
    
    # 2. 중국 데이터 강제 매핑 (순위 및 명도 차이 유지)
    ax_cn = axes[1]
    ax_cn.set_facecolor('white')
    
    ax_cn.text(0.5, 0.76, '뷰티', fontsize=115, weight='black', color='#8b0000', ha='center', va='center')
    ax_cn.text(0.5, 0.44, '패션', fontsize=102, weight='black', color='#e03a3a', ha='center', va='center')
    ax_cn.text(0.5, 0.12, '드라마', fontsize=65, weight='black', color='#f39292', ha='center', va='center')
    
    ax_cn.axis('off')
    ax_cn.set_xlim(0.05, 0.95)
    ax_cn.set_ylim(0.05, 0.95)
    
    # 주변 여백 압축
    plt.tight_layout()
    plt.subplots_adjust(wspace=0.02, left=0.00, right=1.00, top=1.00, bottom=0.00)
    
    # 최종 출력
    st.pyplot(fig)
with col3_2:
    # 요청하신 '💻 사용한 SQL' 대제목 추가
    st.subheader("💻 사용한 SQL")
    st.code(sql3, language='sql')

# ---------------------------------------------------------
# 기존 하단 컴포넌트 간격 유지용 마진 박스 및 인사이트
# ---------------------------------------------------------
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
            •&nbsp;&nbsp;본 분석은 2023~2025년 데이터를 활용하였습니다.<br>
            •&nbsp;&nbsp;방문·소비 통합 기여도 상위 국가 중 싱가포르는 한류 콘텐츠 선호도 데이터가 제공되지 않아 분석 대상에서 제외하였습니다.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)
# 2. 결과 파트 (가운데로 이동, 위아래 여백 10px 유지)
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
        <span style="font-weight: bold; font-size: 1.1em; color: #1e4620;">📊 결과</span><br>
        <div style="color: #212529; line-height: 1.9; font-size: 14px; margin-top: 6px;">
            •&nbsp;&nbsp;미국은 뷰티(28.33%), 웹툰(27.33%), 패션(27.33%) 순으로 높은 소비 비중을 보였다.<br>
            •&nbsp;&nbsp;중국은 뷰티(40.00%), 패션(39.00%), 드라마(28.00%) 순으로 높은 소비 비중을 보였다.
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
                •&nbsp;&nbsp;미국과 중국 관광객 모두 뷰티·패션 등 K-라이프스타일 콘텐츠에 대한 관심이 높게 나타났다.
            </span><br>
            <span style="color: #212529; font-size: 14px;">
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
import matplotlib.pyplot as plt
import platform
import matplotlib.font_manager as fm

st.divider()
st.header("4. 외국인 관광객 소비 패턴 분석")

# OS별 한글 폰트 설정
if platform.system() == 'Windows':
    plt.rc('font', family='Malgun Gothic')
elif platform.system() == 'Darwin':
    plt.rc('font', family='AppleGothic')
else:
    plt.rc('font', family='NanumGothic' if 'NanumGothic' in [f.name for f in fm.fontManager.ttflist] else 'sans-serif')

plt.rcParams['axes.unicode_minus'] = False

# 데이터 수동 매핑 (제공된 데이터셋 유지)
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

# 강원도 / 전국 2열 레이아웃 설정
col_left, col_right = st.columns(2)

# --- 1. [좌측 열] 강원도 내 소비 순위 그래프 및 SQL ---
# --- 1. [좌측 열] 강원도 내 소비 순위 그래프 및 SQL ---
with col_left:
    st.markdown('<div style="font-size:16px; font-weight:600; color:#31333F; margin-bottom:10px;">📍 강원도 내 소비 순위</div>', unsafe_allow_html=True)
    
    # [수정 포인트 1] 그래프 세로 개수를 3개에서 2개로 축소 (3, 1 -> 2, 1)
    # 2개로 줄었기 때문에 figsize 세로 크기도 5.5에서 4.0 정도로 줄이면 예쁘게 나옵니다.
    fig, axes = plt.subplots(2, 1, figsize=(6, 4.0), facecolor='white')
    
    # [수정 포인트 2] 연도 리스트에서 "2025"를 완벽히 삭제
    years = ["2023", "2024"]
    colors_gw = ["#2b5c8f", "#4682b4"] # 컬러도 2개년치만 유지
    
    for i, year in enumerate(years):
        df_year = 강원_data[강원_data["연도"] == year].sort_values(by="비율", ascending=True)
        ax = axes[i]
        
        bars = ax.barh(df_year["카테고리"], df_year["비율"], color=colors_gw[i], height=0.55)
        ax.set_title(f"{year}년", fontsize=11, fontweight="bold", loc="left", color="#333333", pad=5)
        ax.set_xlim(0, 50)
        
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#cccccc')
        ax.spines['bottom'].set_color('#cccccc')
        ax.xaxis.grid(True, linestyle='--', alpha=0.4, color='#e0e0e0')
        ax.set_axisbelow(True)
        ax.tick_params(axis='both', labelsize=9, colors='#555555')
       
        for bar in bars:
            width = bar.get_width()
            ax.text(width + 1.5, bar.get_y() + bar.get_height()/2, f'{width:.1f}%', 
                    va='center', ha='left', fontsize=9, fontweight='semibold', color='#444444')
            
    plt.tight_layout()
    st.pyplot(fig)
    
    # [추가] 강원도 사용 SQL 토글 박스 배치
    with st.expander("💻 사용한 SQL"):
    # SQL 쿼리 전체를 반드시 """ (따옴표 3개)로 감싸주어야 합니다.
        st.code("""
WITH Ranked_Shopping_Subcategory AS (
    SELECT 
        연도,
        "카테고리 대분류" AS 대분류,
        "카테고리 중분류" AS 중분류,
        "카테고리 중분류 소비 비율" AS 중분류_소비_비율,
        ROW_NUMBER() OVER (PARTITION BY 연도 ORDER BY "카테고리 중분류 소비 비율" DESC) AS 순위
    FROM 강원도소비유형합본
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

# --- 2. [우측 열] 전국 소비 순위 그래프 및 SQL ---
with col_right:
    st.markdown('<div style="font-size:16px; font-weight:600; color:#31333F; margin-bottom:10px;">🇰🇷 전국 소비 순위</div>', unsafe_allow_html=True)
    
    fig, axes = plt.subplots(2, 1, figsize=(6, 3.8), facecolor='white')
    years_kr = ["2023", "2024"]
    colors_kr = ["#a2d149", "#8bc34a"]
    
    for i, year in enumerate(years_kr):
        df_year = 전국_data[전국_data["연도"] == year].sort_values(by="비율", ascending=True)
        ax = axes[i]
        
        bars = ax.barh(df_year["카테고리"], df_year["비율"], color=colors_kr[i], height=0.6)
        ax.set_title(f"{year}년", fontsize=11, fontweight="bold", loc="left", color="#333333", pad=5)
        ax.set_xlim(0, 950)
        
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#cccccc')
        ax.spines['bottom'].set_color('#cccccc')
        ax.xaxis.grid(True, linestyle='--', alpha=0.4, color='#e0e0e0')
        ax.set_axisbelow(True)
        ax.tick_params(axis='both', labelsize=9, colors='#555555')
        
        for bar in bars:
            width = bar.get_width()
            ax.text(width + 25, bar.get_y() + bar.get_height()/2, f'{width:,.1f}', 
                    va='center', ha='left', fontsize=9, fontweight='semibold', color='#444444')
            
    plt.tight_layout()
    st.pyplot(fig)
    
    # [추가] 전국 사용 SQL 토글 박스 배치
    with st.expander("💻 사용한 SQL"):
        st.code("""WITH Yearly_Amount_2023 AS (
    SELECT 
        '2023년' AS 연도,
        소비_카테고리_대분류 AS 업종_대분류,
        SUM(소비액_2023) AS 총_소비액,
        ROW_NUMBER() OVER (ORDER BY SUM(소비액_2023) DESC) AS 순위
    FROM 
        전국소비유형
    WHERE 
        필터_대분류 = '전체'
    GROUP BY 
        소비_카테고리_대분류),
Yearly_Amount_2024 AS (
    SELECT 
        '2024년' AS 연도,
        소비_카테고리_대분류 AS 업종_대분류,
        SUM(소비액_2024) AS 총_소비액,
        ROW_NUMBER() OVER (ORDER BY SUM(소비액_2024) DESC) AS 순위
    FROM 
        전국소비유형
    WHERE 
        필터_대분류 = '전체'
    GROUP BY 
        소비_카테고리_대분류)
SELECT 
    연도, 
    순위, 
    업종_대분류, 
    ROUND(총_소비액, 2) AS 평균_소비액_USD
FROM 
    Yearly_Amount_2023
WHERE 
    순위 <= 4
UNION ALL
SELECT 
    연도, 
    순위, 
    업종_대분류, 
    ROUND(총_소비액, 2) AS 평균_소비액_USD
FROM 
    Yearly_Amount_2024
WHERE 
    순위 <= 4

ORDER BY 
    연도 ASC, 
    순위 ASC;""", language="sql")

# ---------------------------------------------------------
# 기존 하단 컴포넌트 간격 유지용 마진 박스 및 인사이트
# ---------------------------------------------------------
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
            •&nbsp;&nbsp;본 분석은 2023~2024년 데이터를 활용하였습니다.<br>
            •&nbsp;&nbsp;외국인 방문객 신용카드 소비데이터를 활용하였습니다.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)
# 2. 결과 파트 (가운데로 이동, 위아래 여백 10px 유지)
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
        <span style="font-weight: bold; font-size: 1.1em; color: #1e4620;">📊 결과</span><br>
        <div style="color: #212529; line-height: 1.9; font-size: 14px; margin-top: 6px;">
            •&nbsp;&nbsp;외국인 관광객의 주요 소비 분야는 숙박·식음료·쇼핑으로 나타났다.<br>
            •&nbsp;&nbsp;강원도는 특히 숙박 및 식음료 소비가 높은 특징을 보인다.
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
                •&nbsp;&nbsp;외국인 관광객의 주요 소비 분야인 숙박·식음료·쇼핑 산업을 중심으로 관광 상품과 서비스를 고도화할 필요가 있다.
            </span><br>
            <span style="color: #212529; font-size: 14px;">
                •&nbsp;&nbsp;지역 특색을 활용한 숙박 패키지, 미식 관광, 지역 특산품 쇼핑 콘텐츠를 확대한다면 외국인 관광객의 1인당 소비액 증가와 지역경제 활성화에 기여할 수 있을 것으로 기대된다.
            </span>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# ---------------------------------------------------------
# 6. 강원도 쇼핑업 상세 분석
# ---------------------------------------------------------
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

st.divider()
st.header("6. 강원도 외국인 관광객 쇼핑 유형 분석")

# [수정 포인트 1] SQL 쿼리 내부에서도 2025년 데이터가 나오지 않도록 조건문(AND 연도 IN...) 추가
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
      AND 연도 IN (2023, 2024) -- 👈 쿼리 결과에서도 2025년을 원천 제외하여 데이터 정합성 맞춤
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

# 1. 데이터 정의 (2023, 2024만 유지)
쇼핑_상세_data = pd.DataFrame([
    {"연도": "2023", "중분류": "기타관광쇼핑", "비율": 64.3},
    {"연도": "2023", "중분류": "대형쇼핑몰", "비율": 26.8},
    {"연도": "2023", "중분류": "레저용품쇼핑", "비율": 8.7},
    {"연도": "2024", "중분류": "기타관광쇼핑", "비율": 64.8},
    {"연도": "2024", "중분류": "대형쇼핑몰", "비율": 25.3},
    {"연도": "2024", "중분류": "레저용품쇼핑", "비율": 9.8}
])

# 2. 레이아웃 분할 (상단 영역)
col_graph, col_table = st.columns([1.2, 0.8])

with col_graph:
    # 2개년 데이터이므로 세로 2칸짜리 subplot 도화지 생성
    fig, axes = plt.subplots(2, 1, figsize=(6, 4.2), facecolor='white')
    years = ["2023", "2024"]
    colors_shop = ["#E67E22", "#F39C12"] 
    
    for i, year in enumerate(years):
        df_year = 쇼핑_상세_data[쇼핑_상세_data["연도"] == year].sort_values(by="비율", ascending=True)
        ax = axes[i]
        
        bars = ax.barh(df_year["중분류"], df_year["비율"], color=colors_shop[i], height=0.55)
        ax.set_title(f"{year}년 쇼핑 업종별 비중", fontsize=11, fontweight="bold", loc="left", color="#333333", pad=5)
        ax.set_xlim(0, 80) 
        
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#cccccc')
        ax.spines['bottom'].set_color('#cccccc')
        ax.xaxis.grid(True, linestyle='--', alpha=0.4, color='#e0e0e0')
        ax.set_axisbelow(True)
        ax.tick_params(axis='both', labelsize=9, colors='#555555')
        
        for bar in bars:
            width = bar.get_width()
            ax.text(width + 2.0, bar.get_y() + bar.get_height()/2, f'{width:.1f}%', 
                    va='center', ha='left', fontsize=9, fontweight='semibold', color='#444444')
            
    plt.tight_layout()
    st.pyplot(fig)

with col_table:
    st.markdown('<div style="font-size:14px; font-weight:600; color:#555555; margin-bottom:8px;">📋 데이터 상세 보기</div>', unsafe_allow_html=True)
    display_df = 쇼핑_상세_data.copy()
    display_df["비율"] = display_df["비율"].map(lambda x: f"{x:.1f}%")
    st.dataframe(display_df, use_container_width=True, hide_index=True)

st.write("") # 시각적 안정감을 위한 빈 한 칸 여백
with st.expander("💻 사용한 SQL"):
    st.code(sql6, language="sql")

# ---------------------------------------------------------
# 기존 하단 컴포넌트 간격 유지용 마진 박스 및 인사이트
# ---------------------------------------------------------
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
            •&nbsp;&nbsp;본 분석은 2023년~2025년 외국인 방문객 신용카드 소비 데이터를 활용하였습니다.<br>
            •&nbsp;&nbsp;기타관광쇼핑에는 기념품, 사진기, 슈퍼마켓, 편의점, 농축수산물, 공예품, 예술품, 의류, 신발, 가방류, 생활용품, 귀금속 등 관광객이 여행 중 구매하는 다양한 소매·관광 상품 업종이 포함됩니다.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)
# 2. 결과 파트 (가운데로 이동, 위아래 여백 10px 유지)
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
        <span style="font-weight: bold; font-size: 1.1em; color: #1e4620;">📊 결과</span><br>
        <div style="color: #212529; line-height: 1.9; font-size: 14px; margin-top: 6px;">
            •&nbsp;&nbsp;강원도 외국인 관광객의 쇼핑 소비는 3년 연속 기타관광쇼핑에 64% 이상 집중되어 있어 관광 관련 소매·기념품 소비가 쇼핑 지출의 핵심인 것으로 나타남
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
                •&nbsp;&nbsp;강원도 특산품, 지역 한정 굿즈, 전통 공예품, 지역 브랜드 상품 등 관광 목적 소비를 유도할 수 있는 차별화된 쇼핑 콘텐츠를 확대할 필요가 있다.
            </span><br>
            <span style="color: #212529; font-size: 14px;">
                •&nbsp;&nbsp;특히 기타관광쇼핑이 전체 쇼핑 소비의 약 65%를 차지하고 있는 만큼, 관광지 인근 상점과 특산품 판매장의 경쟁력 강화가 관광 소비 증대에 중요한 역할을 할 것으로 판단됨
            </span>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)
