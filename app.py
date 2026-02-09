"""
포켓몬 카드 가격 검색 - 완전 독립 실행 버전
모든 기능이 이 파일 하나에 포함됨
"""

import streamlit as st
import pandas as pd
import asyncio
import statistics
from datetime import datetime
from typing import List, Dict, Optional

# ===== mercapi import =====
try:
    from mercapi import Mercapi
    MERCAPI_AVAILABLE = True
except ImportError:
    MERCAPI_AVAILABLE = False

# ===== 설정 =====
CURRENCY = "¥"
MERCARI_ITEM_URL = "https://jp.mercari.com/item"
DEFAULT_SEARCH_LIMIT = 120

# ===== 페이지 설정 =====
st.set_page_config(
    page_title="🎴 포켓몬 카드 가격 검색",
    page_icon="🎴",
    layout="wide"
)

# ===== 핵심 함수들 =====

def search_card_sync(card_number: str, card_name: Optional[str] = None) -> Dict:
    """포켓몬 카드 검색"""
    
    if not MERCAPI_AVAILABLE:
        return {
            'success': False, 
            'error': 'mercapi 라이브러리가 필요합니다. pip install mercapi', 
            'listings': []
        }
    
    search_query = f"ポケモンカード {card_number}"
    if card_name:
        search_query += f" {card_name}"
    
    try:
        mercapi = Mercapi()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        results = loop.run_until_complete(
            mercapi.search(
                keyword=search_query,
                limit=DEFAULT_SEARCH_LIMIT,
                sort='created_time',
                order='desc'
            )
        )
        loop.close()
        
        listings = []
        for item in results.items:
            listing = {
                'item_id': item.id,
                'name': item.name,
                'price': item.price,
                'status': item.status,
                'thumbnail': item.thumbnails[0] if item.thumbnails else "",
                'url': f"{MERCARI_ITEM_URL}/{item.id}",
            }
            listings.append(listing)
        
        return {
            'success': True,
            'query': search_query,
            'listings': listings
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'listings': []
        }


def calculate_stats(listings: List[Dict]) -> Dict:
    """통계 계산"""
    if not listings:
        return {
            'total': 0, 'active': 0, 'sold': 0,
            'avg': None, 'median': None, 'min': None, 'max': None,
            'active_prices': [], 'sold_prices': []
        }
    
    active_prices = [l['price'] for l in listings if l['status'] != 'sold_out']
    sold_prices = [l['price'] for l in listings if l['status'] == 'sold_out']
    all_prices = active_prices + sold_prices
    
    return {
        'total': len(listings),
        'active': len(active_prices),
        'sold': len(sold_prices),
        'avg': round(statistics.mean(all_prices), 2) if all_prices else None,
        'median': round(statistics.median(all_prices), 2) if all_prices else None,
        'min': min(all_prices) if all_prices else None,
        'max': max(all_prices) if all_prices else None,
        'active_prices': active_prices,
        'sold_prices': sold_prices
    }


def format_price(price: Optional[float]) -> str:
    """가격 포맷"""
    return f"{CURRENCY}{int(price):,}" if price else "-"


# ===== 메인 애플리케이션 =====

def main():
    """메인 앱"""
    
    # 헤더
    st.title("🎴 포켓몬 카드 가격 검색")
    st.markdown("**메르카리 일본**에서 실시간 포켓몬 카드 시세를 확인하세요")
    
    # mercapi 체크
    if not MERCAPI_AVAILABLE:
        st.error("❌ mercapi 라이브러리가 설치되지 않았습니다.")
        st.code("pip install mercapi", language="bash")
        st.stop()
    
    # 사이드바 - 검색
    with st.sidebar:
        st.header("🔍 카드 검색")
        
        with st.form("search_form"):
            card_number = st.text_input(
                "카드 번호 *",
                placeholder="예: 025/165, SV-P-123",
                help="포켓몬 카드 번호를 입력하세요"
            )
            
            card_name = st.text_input(
                "카드 이름 (선택)",
                placeholder="예: 피카츄, リザードン",
                help="더 정확한 검색을 위해 입력"
            )
            
            search_btn = st.form_submit_button(
                "🔍 검색하기",
                type="primary",
                use_container_width=True
            )
        
        st.divider()
        st.caption("💡 **사용 팁**")
        st.caption("• 카드 번호는 필수입니다")
        st.caption("• 검색은 30초~1분 소요됩니다")
        st.caption("• 최대 120개 상품을 검색합니다")
        
        st.divider()
        st.caption("⚠️ **주의사항**")
        st.caption("• 메르카리 이용약관을 준수하세요")
        st.caption("• 과도한 검색은 제한될 수 있습니다")
    
    # 검색 실행
    if search_btn:
        if not card_number.strip():
            st.error("❌ 카드 번호를 입력해주세요!")
            return
        
        # 검색 진행
        with st.spinner("🔄 메르카리에서 데이터를 가져오는 중... 잠시만 기다려주세요!"):
            result = search_card_sync(card_number.strip(), card_name.strip() if card_name else None)
        
        # 결과 처리
        if not result['success']:
            st.error(f"❌ 오류 발생: {result.get('error', '알 수 없는 오류')}")
            return
        
        if not result['listings']:
            st.warning("⚠️ 검색 결과가 없습니다.")
            st.info(f"검색어: `{result.get('query', '')}`")
            st.caption("💡 카드 번호나 이름을 다시 확인해보세요")
            return
        
        # 세션에 저장
        st.session_state['result'] = result
        st.session_state['card_number'] = card_number
        st.success(f"✅ 검색 완료! {len(result['listings'])}개의 상품을 찾았습니다.")
    
    # 결과 표시
    if 'result' in st.session_state:
        display_results()


def display_results():
    """검색 결과 표시"""
    
    listings = st.session_state['result']['listings']
    stats = calculate_stats(listings)
    
    # 제목
    st.divider()
    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader(f"📊 검색 결과: {st.session_state['card_number']}")
    with col2:
        st.metric("총 매물", f"{stats['total']}개")
    
    # 가격 통계
    st.markdown("### 💰 가격 통계")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("평균 가격", format_price(stats['avg']), help="전체 상품의 평균 가격")
    with col2:
        st.metric("중간 가격", format_price(stats['median']), help="중간값 (median)")
    with col3:
        st.metric("최저 가격", format_price(stats['min']), help="가장 저렴한 상품")
    with col4:
        st.metric("최고 가격", format_price(stats['max']), help="가장 비싼 상품")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("판매중 🟢", f"{stats['active']}개", help="현재 판매 중인 상품")
    with col2:
        st.metric("판매완료 ⚫", f"{stats['sold']}개", help="이미 판매된 상품")
    
    # 가격 분포 차트
    st.markdown("### 📈 가격 분포")
    
    if stats['active_prices'] or stats['sold_prices']:
        all_prices = stats['active_prices'] + stats['sold_prices']
        
        # 가격대별 분포 (Streamlit 기본 차트)
        df_prices = pd.DataFrame({'가격': all_prices})
        price_counts = df_prices['가격'].value_counts().sort_index()
        
        st.bar_chart(price_counts)
        
        # 간단한 통계 테이블
        col1, col2 = st.columns(2)
        
        with col1:
            if stats['active_prices']:
                st.write("**판매중 상품 가격 분포**")
                df_active = pd.DataFrame(stats['active_prices'], columns=['가격'])
                st.dataframe(df_active.describe(), use_container_width=True)
        
        with col2:
            if stats['sold_prices']:
                st.write("**판매완료 상품 가격 분포**")
                df_sold = pd.DataFrame(stats['sold_prices'], columns=['가격'])
                st.dataframe(df_sold.describe(), use_container_width=True)
    
    # 상품 목록
    st.markdown("### 🎯 상품 목록")
    
    # 필터 옵션
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status_filter = st.selectbox(
            "상태 필터",
            ["전체 보기", "판매중만", "판매완료만"]
        )
    
    with col2:
        sort_by = st.selectbox(
            "정렬 기준",
            ["가격 낮은순", "가격 높은순"]
        )
    
    with col3:
        items_per_row = st.select_slider(
            "한 줄에 표시",
            options=[2, 3, 4, 5],
            value=4
        )
    
    # 필터링
    filtered = listings.copy()
    
    if status_filter == "판매중만":
        filtered = [l for l in filtered if l['status'] != 'sold_out']
    elif status_filter == "판매완료만":
        filtered = [l for l in filtered if l['status'] == 'sold_out']
    
    # 정렬
    if sort_by == "가격 낮은순":
        filtered = sorted(filtered, key=lambda x: x['price'])
    else:
        filtered = sorted(filtered, key=lambda x: x['price'], reverse=True)
    
    st.caption(f"📦 총 {len(filtered)}개 상품")
    
    # 그리드로 상품 표시
    if filtered:
        for i in range(0, len(filtered), items_per_row):
            cols = st.columns(items_per_row)
            
            for j, col in enumerate(cols):
                idx = i + j
                if idx < len(filtered):
                    item = filtered[idx]
                    
                    with col:
                        # 이미지
                        if item['thumbnail']:
                            st.image(item['thumbnail'], use_container_width=True)
                        else:
                            st.info("🖼️ 이미지 없음")
                        
                        # 상품명 (30자로 제한)
                        name = item['name'][:30] + "..." if len(item['name']) > 30 else item['name']
                        st.caption(name)
                        
                        # 가격
                        st.markdown(f"**{format_price(item['price'])}**")
                        
                        # 상태 배지
                        if item['status'] == 'sold_out':
                            st.markdown("🔴 **판매완료**")
                        else:
                            st.markdown("🟢 **판매중**")
                        
                        # 링크 버튼
                        st.link_button(
                            "메르카리에서 보기",
                            item['url'],
                            use_container_width=True
                        )
                        
                        st.divider()
    else:
        st.info("필터 조건에 맞는 상품이 없습니다.")
    
    # 데이터 다운로드
    st.markdown("### 📥 데이터 다운로드")
    
    if filtered:
        df = pd.DataFrame(filtered)
        
        # 한글 컬럼명으로 변경
        df_download = df.copy()
        df_download['상태'] = df_download['status'].map({
            'sold_out': '판매완료',
            'on_sale': '판매중'
        })
        df_download['가격_formatted'] = df_download['price'].apply(format_price)
        
        # CSV 생성
        csv = df_download[['name', '가격_formatted', '상태', 'url']].to_csv(
            index=False, 
            encoding='utf-8-sig',
            columns=['name', '가격_formatted', '상태', 'url'],
            header=['상품명', '가격', '상태', 'URL']
        )
        
        st.download_button(
            label="📄 CSV 파일 다운로드",
            data=csv,
            file_name=f"pokemon_card_{st.session_state['card_number']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )


# ===== 앱 실행 =====
if __name__ == "__main__":
    main()
