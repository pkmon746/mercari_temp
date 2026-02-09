"""
포켓몬 카드 가격 검색 - 직접 API 호출 버전
mercapi 대신 httpx로 직접 메르카리 API 호출
"""

import streamlit as st
import pandas as pd
import httpx
import asyncio
import statistics
from datetime import datetime
from typing import List, Dict, Optional
import json

# ===== 설정 =====
CURRENCY = "¥"
MERCARI_API_URL = "https://api.mercari.jp/v2/entities:search"
MERCARI_ITEM_URL = "https://jp.mercari.com/item"

# ===== 페이지 설정 =====
st.set_page_config(
    page_title="🎴 포켓몬 카드 가격 검색",
    page_icon="🎴",
    layout="wide"
)

# ===== API 호출 함수 =====

async def search_mercari_api(keyword: str, limit: int = 120) -> List[Dict]:
    """메르카리 API 직접 호출"""
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json',
    }
    
    params = {
        'keyword': keyword,
        'limit': limit,
        'sort': 'created_time',
        'order': 'desc',
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                MERCARI_API_URL,
                params=params,
                headers=headers,
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                return parse_mercari_response(data)
            else:
                st.error(f"API 오류: {response.status_code}")
                return []
                
    except Exception as e:
        st.error(f"API 호출 실패: {str(e)}")
        return []


def parse_mercari_response(data: dict) -> List[Dict]:
    """메르카리 API 응답 파싱"""
    
    listings = []
    
    # API 응답 구조에 따라 파싱 (실제 구조는 다를 수 있음)
    items = data.get('items', [])
    
    for item in items:
        listing = {
            'item_id': item.get('id', ''),
            'name': item.get('name', ''),
            'price': item.get('price', 0),
            'status': item.get('status', 'on_sale'),
            'thumbnail': item.get('thumbnails', [''])[0] if item.get('thumbnails') else '',
            'url': f"{MERCARI_ITEM_URL}/{item.get('id', '')}",
        }
        listings.append(listing)
    
    return listings


def search_card_sync(card_number: str, card_name: Optional[str] = None) -> Dict:
    """동기 방식으로 검색"""
    
    search_query = f"ポケモンカード {card_number}"
    if card_name:
        search_query += f" {card_name}"
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        listings = loop.run_until_complete(search_mercari_api(search_query))
        loop.close()
        
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


# ===== 통계 함수 =====

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


# ===== 메인 앱 =====

def main():
    st.title("🎴 포켓몬 카드 가격 검색")
    st.markdown("**메르카리 일본** 실시간 가격 검색")
    
    with st.sidebar:
        st.header("🔍 검색")
        
        with st.form("search"):
            card_number = st.text_input("카드 번호 *", placeholder="예: 025/165")
            card_name = st.text_input("카드 이름", placeholder="예: 피카츄")
            search_btn = st.form_submit_button("🔍 검색", type="primary", use_container_width=True)
        
        st.divider()
        st.caption("💡 검색은 최대 1분 소요됩니다")
    
    if search_btn:
        if not card_number.strip():
            st.error("❌ 카드 번호를 입력하세요")
            return
        
        with st.spinner("🔄 메르카리 검색 중..."):
            result = search_card_sync(card_number.strip(), card_name.strip() if card_name else None)
        
        if not result['success']:
            st.error(f"❌ 오류: {result.get('error')}")
            st.warning("💡 메르카리 API 접근에 문제가 있을 수 있습니다. 나중에 다시 시도해주세요.")
            return
        
        if not result['listings']:
            st.warning("⚠️ 검색 결과 없음")
            return
        
        st.session_state['result'] = result
        st.session_state['card_number'] = card_number
        st.success(f"✅ {len(result['listings'])}개 발견!")
    
    if 'result' in st.session_state:
        display_results()


def display_results():
    """결과 표시"""
    
    listings = st.session_state['result']['listings']
    stats = calculate_stats(listings)
    
    st.divider()
    st.subheader(f"📊 {st.session_state['card_number']}")
    
    # 통계
    st.markdown("### 💰 가격 통계")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("평균", format_price(stats['avg']))
    with col2:
        st.metric("중간값", format_price(stats['median']))
    with col3:
        st.metric("최저", format_price(stats['min']))
    with col4:
        st.metric("최고", format_price(stats['max']))
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("판매중 🟢", f"{stats['active']}개")
    with col2:
        st.metric("판매완료 ⚫", f"{stats['sold']}개")
    
    # 차트
    st.markdown("### 📈 분포")
    if stats['active_prices'] or stats['sold_prices']:
        all_prices = stats['active_prices'] + stats['sold_prices']
        df = pd.DataFrame({'가격': all_prices})
        st.bar_chart(df['가격'].value_counts().sort_index())
    
    # 목록
    st.markdown("### 🎯 상품 목록")
    
    col1, col2 = st.columns(2)
    with col1:
        status = st.selectbox("상태", ["전체", "판매중", "판매완료"])
    with col2:
        sort = st.selectbox("정렬", ["가격 낮은순", "가격 높은순"])
    
    filtered = listings
    if status == "판매중":
        filtered = [l for l in filtered if l['status'] != 'sold_out']
    elif status == "판매완료":
        filtered = [l for l in filtered if l['status'] == 'sold_out']
    
    if sort == "가격 낮은순":
        filtered = sorted(filtered, key=lambda x: x['price'])
    else:
        filtered = sorted(filtered, key=lambda x: x['price'], reverse=True)
    
    st.caption(f"{len(filtered)}개")
    
    # 그리드
    for i in range(0, len(filtered), 4):
        cols = st.columns(4)
        for j, col in enumerate(cols):
            idx = i + j
            if idx < len(filtered):
                item = filtered[idx]
                with col:
                    if item['thumbnail']:
                        st.image(item['thumbnail'], use_container_width=True)
                    
                    st.caption(item['name'][:30] + "...")
                    st.markdown(f"**{format_price(item['price'])}**")
                    st.markdown("🔴 판매완료" if item['status'] == 'sold_out' else "🟢 판매중")
                    st.link_button("보기", item['url'], use_container_width=True)
                    st.divider()
    
    # 다운로드
    st.markdown("### 📥 다운로드")
    df = pd.DataFrame(filtered)
    csv = df.to_csv(index=False, encoding='utf-8-sig')
    st.download_button("📄 CSV", csv, f"pokemon_{st.session_state['card_number']}.csv", "text/csv")


if __name__ == "__main__":
    main()
