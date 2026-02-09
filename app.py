"""
포켓몬 카드 가격 검색 - 데모 버전
Mercapi 대신 샘플 데이터 사용 (Streamlit Cloud 배포용)
"""

import streamlit as st
import pandas as pd
import random
from datetime import datetime
from typing import List, Dict, Optional
import statistics

# ===== 설정 =====
CURRENCY = "¥"
MERCARI_ITEM_URL = "https://jp.mercari.com/item"

# ===== 페이지 설정 =====
st.set_page_config(
    page_title="🎴 포켓몬 카드 가격 검색 (데모)",
    page_icon="🎴",
    layout="wide"
)

# ===== 샘플 데이터 생성 함수 =====

def generate_sample_data(card_number: str, card_name: Optional[str] = None) -> List[Dict]:
    """샘플 데이터 생성 (실제 mercapi 대신)"""
    
    # 샘플 포켓몬 카드 이미지 URL
    sample_images = [
        "https://images.pokemontcg.io/base1/4_hires.png",
        "https://images.pokemontcg.io/base1/1_hires.png",
        "https://images.pokemontcg.io/base1/2_hires.png",
    ]
    
    # 가격 범위 설정 (카드 번호에 따라 다르게)
    base_price = 1000
    if "pikachu" in (card_name or "").lower() or "025" in card_number:
        base_price = 2000
    
    # 30~80개의 샘플 데이터 생성
    num_items = random.randint(30, 80)
    listings = []
    
    for i in range(num_items):
        # 가격 변동
        price = int(base_price * random.uniform(0.5, 2.0))
        
        # 상태 (70%는 판매중, 30%는 판매완료)
        status = "on_sale" if random.random() > 0.3 else "sold_out"
        
        listing = {
            'item_id': f'm{random.randint(10000000000, 99999999999)}',
            'name': f'ポケモンカード {card_number} {card_name or ""}',
            'price': price,
            'status': status,
            'thumbnail': random.choice(sample_images),
            'url': f"{MERCARI_ITEM_URL}/m{random.randint(10000000000, 99999999999)}",
        }
        listings.append(listing)
    
    return listings


# ===== 핵심 함수들 =====

def search_card_demo(card_number: str, card_name: Optional[str] = None) -> Dict:
    """데모 검색 (샘플 데이터 반환)"""
    
    search_query = f"ポケモンカード {card_number}"
    if card_name:
        search_query += f" {card_name}"
    
    try:
        listings = generate_sample_data(card_number, card_name)
        
        return {
            'success': True,
            'query': search_query,
            'listings': listings,
            'is_demo': True
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'listings': [],
            'is_demo': True
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
    
    # 데모 알림
    st.info("ℹ️ **데모 버전**: 실제 메르카리 데이터 대신 샘플 데이터를 사용합니다. 실제 배포 시에는 mercapi를 사용하세요.")
    
    # 헤더
    st.title("🎴 포켓몬 카드 가격 검색")
    st.markdown("**메르카리 일본** 가격 검색 데모")
    
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
                placeholder="예: 피카츄, Pikachu",
                help="더 정확한 검색을 위해 입력"
            )
            
            search_btn = st.form_submit_button(
                "🔍 검색하기 (데모)",
                type="primary",
                use_container_width=True
            )
        
        st.divider()
        st.caption("💡 **데모 기능**")
        st.caption("• 샘플 데이터로 즉시 확인")
        st.caption("• 실제 기능 미리보기")
        st.caption("• 검색마다 랜덤 데이터 생성")
    
    # 검색 실행
    if search_btn:
        if not card_number.strip():
            st.error("❌ 카드 번호를 입력해주세요!")
            return
        
        # 검색 진행 (데모는 즉시 완료)
        with st.spinner("🔄 데이터 생성 중..."):
            result = search_card_demo(card_number.strip(), card_name.strip() if card_name else None)
        
        # 결과 처리
        if not result['success']:
            st.error(f"❌ 오류 발생: {result.get('error', '알 수 없는 오류')}")
            return
        
        if not result['listings']:
            st.warning("⚠️ 검색 결과가 없습니다.")
            return
        
        # 세션에 저장
        st.session_state['result'] = result
        st.session_state['card_number'] = card_number
        st.success(f"✅ 검색 완료! {len(result['listings'])}개의 샘플 데이터 생성")
    
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
        st.metric("평균 가격", format_price(stats['avg']))
    with col2:
        st.metric("중간 가격", format_price(stats['median']))
    with col3:
        st.metric("최저 가격", format_price(stats['min']))
    with col4:
        st.metric("최고 가격", format_price(stats['max']))
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("판매중 🟢", f"{stats['active']}개")
    with col2:
        st.metric("판매완료 ⚫", f"{stats['sold']}개")
    
    # 가격 분포 차트
    st.markdown("### 📈 가격 분포")
    
    if stats['active_prices'] or stats['sold_prices']:
        all_prices = stats['active_prices'] + stats['sold_prices']
        df_prices = pd.DataFrame({'가격': all_prices})
        st.bar_chart(df_prices['가격'].value_counts().sort_index())
    
    # 상품 목록
    st.markdown("### 🎯 상품 목록")
    
    # 필터
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status_filter = st.selectbox("상태", ["전체", "판매중", "판매완료"])
    with col2:
        sort_by = st.selectbox("정렬", ["가격 낮은순", "가격 높은순"])
    with col3:
        items_per_row = st.select_slider("한 줄에", options=[2, 3, 4, 5], value=4)
    
    # 필터링
    filtered = listings.copy()
    
    if status_filter == "판매중":
        filtered = [l for l in filtered if l['status'] != 'sold_out']
    elif status_filter == "판매완료":
        filtered = [l for l in filtered if l['status'] == 'sold_out']
    
    # 정렬
    if sort_by == "가격 낮은순":
        filtered = sorted(filtered, key=lambda x: x['price'])
    else:
        filtered = sorted(filtered, key=lambda x: x['price'], reverse=True)
    
    st.caption(f"📦 {len(filtered)}개 상품")
    
    # 그리드
    if filtered:
        for i in range(0, len(filtered), items_per_row):
            cols = st.columns(items_per_row)
            
            for j, col in enumerate(cols):
                idx = i + j
                if idx < len(filtered):
                    item = filtered[idx]
                    
                    with col:
                        st.image(item['thumbnail'], use_container_width=True)
                        
                        name = item['name'][:30] + "..." if len(item['name']) > 30 else item['name']
                        st.caption(name)
                        
                        st.markdown(f"**{format_price(item['price'])}**")
                        
                        if item['status'] == 'sold_out':
                            st.markdown("🔴 **판매완료**")
                        else:
                            st.markdown("🟢 **판매중**")
                        
                        st.link_button("보기 (데모)", item['url'], use_container_width=True)
                        st.divider()
    
    # CSV 다운로드
    st.markdown("### 📥 데이터 다운로드")
    
    if filtered:
        df = pd.DataFrame(filtered)
        csv = df.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            "📄 CSV 다운로드",
            csv,
            f"pokemon_demo_{st.session_state['card_number']}_{datetime.now().strftime('%Y%m%d')}.csv",
            "text/csv",
            use_container_width=True
        )


# ===== 앱 실행 =====
if __name__ == "__main__":
    main()
