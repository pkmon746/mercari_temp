"""
포켓몬 카드 가격 검색 Streamlit 앱
메르카리 일본에서 포켓몬 카드 가격 정보를 검색하고 통계를 표시
"""

import streamlit as st
import pandas as pd
from datetime import datetime

# plotly import 시도
try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    st.warning("⚠️ plotly가 설치되지 않아 차트 기능이 제한됩니다.")

# 로컬 모듈
import config
from mercari_scraper import search_card_sync
from utils import (
    calculate_price_statistics,
    format_price,
    create_listings_dataframe,
    filter_listings_by_price,
    filter_listings_by_status
)


# 페이지 설정
st.set_page_config(
    page_title=config.PAGE_TITLE,
    page_icon=config.PAGE_ICON,
    layout=config.LAYOUT
)


def main():
    """메인 애플리케이션"""
    
    # 헤더
    st.title(config.PAGE_TITLE)
    st.markdown("**메르카리 일본**에서 실시간 포켓몬 카드 가격을 확인하세요")
    
    # 사이드바 - 검색 폼
    with st.sidebar:
        st.header("🔍 카드 검색")
        
        # 입력 폼
        with st.form("search_form"):
            card_number = st.text_input(
                "카드 번호 *",
                placeholder="예: 025/165, SV-P-123",
                help="포켓몬 카드 번호를 입력하세요"
            )
            
            card_name = st.text_input(
                "카드 이름 (선택사항)",
                placeholder="예: 피카츄, リザードン",
                help="더 정확한 검색을 위해 카드 이름을 입력하세요"
            )
            
            search_button = st.form_submit_button(
                "🔍 검색",
                use_container_width=True,
                type="primary"
            )
        
        # 정보
        st.divider()
        st.caption("💡 **팁**")
        st.caption("• 카드 번호는 필수입니다")
        st.caption("• 카드 이름을 함께 입력하면 더 정확합니다")
        st.caption("• 검색에는 수십 초가 걸릴 수 있습니다")
    
    # 검색 실행
    if search_button:
        if not card_number:
            st.error("❌ 카드 번호를 입력해주세요!")
            return
        
        # 검색 진행
        with st.spinner(config.STATUS_MESSAGES['searching']):
            result = search_card_sync(card_number, card_name)
        
        # 결과 처리
        if not result['success']:
            st.error(f"❌ {config.STATUS_MESSAGES['error']}: {result.get('error', '알 수 없는 오류')}")
            return
        
        listings = result['listings']
        
        if not listings:
            st.warning(f"⚠️ {config.STATUS_MESSAGES['no_results']}")
            st.info(f"검색어: `{result.get('query', '')}`")
            return
        
        # 세션 스테이트에 저장
        st.session_state['search_result'] = result
        st.session_state['card_number'] = card_number
        st.session_state['card_name'] = card_name
        st.success(f"✅ {config.STATUS_MESSAGES['complete']}")
    
    # 결과 표시
    if 'search_result' in st.session_state:
        display_results(st.session_state['search_result'])


def display_results(result: dict):
    """검색 결과 표시"""
    
    listings = result['listings']
    stats = calculate_price_statistics(listings)
    
    # 검색 정보
    st.divider()
    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader(f"📊 검색 결과: {st.session_state.get('card_number', '')}")
        if st.session_state.get('card_name'):
            st.caption(f"카드 이름: {st.session_state['card_name']}")
    with col2:
        st.metric("총 매물", f"{stats['total_listings']}개")
    
    # 가격 통계 카드
    st.markdown("### 💰 가격 통계")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "평균 가격",
            format_price(stats['average_price']),
            help="전체 상품의 평균 가격"
        )
    
    with col2:
        st.metric(
            "중간 가격",
            format_price(stats['median_price']),
            help="가격을 정렬했을 때 중간값"
        )
    
    with col3:
        st.metric(
            "최저 가격",
            format_price(stats['min_price']),
            help="가장 저렴한 상품 가격"
        )
    
    with col4:
        st.metric(
            "최고 가격",
            format_price(stats['max_price']),
            help="가장 비싼 상품 가격"
        )
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(
            "판매중 🟢",
            f"{stats['active_listings']}개",
            help="현재 판매 중인 상품 수"
        )
    
    with col2:
        st.metric(
            "판매완료 ⚫",
            f"{stats['sold_listings']}개",
            help="이미 판매된 상품 수"
        )
    
    # 가격 분포 차트
    st.markdown("### 📈 가격 분포")
    
    all_prices = stats['active_prices'] + stats['sold_prices']
    
    if all_prices:
        if PLOTLY_AVAILABLE:
            # 히스토그램
            fig = px.histogram(
                x=all_prices,
                nbins=20,
                labels={'x': '가격 (円)', 'y': '상품 수'},
                title="가격대별 상품 분포"
            )
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
            
            # 박스 플롯
            fig_box = go.Figure()
            
            if stats['active_prices']:
                fig_box.add_trace(go.Box(
                    y=stats['active_prices'],
                    name='판매중',
                    marker_color='lightgreen'
                ))
            
            if stats['sold_prices']:
                fig_box.add_trace(go.Box(
                    y=stats['sold_prices'],
                    name='판매완료',
                    marker_color='lightgray'
                ))
            
            fig_box.update_layout(
                title="판매 상태별 가격 분포",
                yaxis_title="가격 (円)",
                showlegend=True
            )
            st.plotly_chart(fig_box, use_container_width=True)
        else:
            # plotly가 없을 때 대체 - Streamlit 기본 차트
            st.bar_chart(pd.DataFrame({'가격': all_prices}).value_counts().sort_index())
            
            # 간단한 통계 표시
            col1, col2 = st.columns(2)
            with col1:
                if stats['active_prices']:
                    st.write("**판매중 가격 분포**")
                    st.write(pd.DataFrame(stats['active_prices'], columns=['가격']).describe())
            with col2:
                if stats['sold_prices']:
                    st.write("**판매완료 가격 분포**")
                    st.write(pd.DataFrame(stats['sold_prices'], columns=['가격']).describe())
    
    # 필터
    st.markdown("### 🎯 상품 목록")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status_filter = st.selectbox(
            "상태 필터",
            ["전체", "판매중만", "판매완료만"]
        )
    
    with col2:
        min_price = st.number_input(
            "최소 가격 (円)",
            min_value=0,
            value=0,
            step=100
        )
    
    with col3:
        max_price = st.number_input(
            "최대 가격 (円)",
            min_value=0,
            value=0,
            step=100
        )
    
    # 필터링
    filtered_listings = listings
    
    if status_filter == "판매중만":
        filtered_listings = filter_listings_by_status(filtered_listings, "on_sale")
    elif status_filter == "판매완료만":
        filtered_listings = filter_listings_by_status(filtered_listings, "sold_out")
    
    if min_price > 0 or max_price > 0:
        filtered_listings = filter_listings_by_price(
            filtered_listings,
            min_price if min_price > 0 else None,
            max_price if max_price > 0 else None
        )
    
    st.caption(f"총 {len(filtered_listings)}개 상품")
    
    # 상품 목록 (그리드)
    df = create_listings_dataframe(filtered_listings)
    
    if not df.empty:
        # 그리드 형식으로 표시
        cols_per_row = 4
        for i in range(0, len(filtered_listings), cols_per_row):
            cols = st.columns(cols_per_row)
            
            for j, col in enumerate(cols):
                idx = i + j
                if idx < len(filtered_listings):
                    listing = filtered_listings[idx]
                    
                    with col:
                        # 카드 컨테이너
                        with st.container():
                            # 이미지
                            if listing['thumbnail']:
                                st.image(
                                    listing['thumbnail'],
                                    use_container_width=True
                                )
                            else:
                                st.info("이미지 없음")
                            
                            # 상품명 (짧게)
                            name = listing['name'][:40] + "..." if len(listing['name']) > 40 else listing['name']
                            st.caption(name)
                            
                            # 가격
                            st.markdown(f"**{format_price(listing['price'])}**")
                            
                            # 상태 배지
                            if listing['status'] == 'sold_out':
                                st.markdown("🔴 판매완료")
                            else:
                                st.markdown("🟢 판매중")
                            
                            # 링크
                            st.link_button(
                                "메르카리에서 보기",
                                listing['url'],
                                use_container_width=True
                            )
                            
                            st.divider()
    else:
        st.info("필터 조건에 맞는 상품이 없습니다.")
    
    # 데이터 다운로드
    st.markdown("### 📥 데이터 다운로드")
    
    if not df.empty:
        csv = df.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="📄 CSV 다운로드",
            data=csv,
            file_name=f"pokemon_card_{st.session_state.get('card_number', 'data')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )


# 앱 실행
if __name__ == "__main__":
    main()
