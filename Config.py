"""
설정 파일
애플리케이션 전역 상수 및 설정값
"""

# 검색 설정
DEFAULT_SEARCH_LIMIT = 120  # 최대 검색 결과 수
SEARCH_SORT_BY = 'created_time'  # 정렬 기준
SEARCH_ORDER = 'desc'  # 정렬 순서

# 캐시 설정
CACHE_TTL = 3600  # 캐시 유효 시간 (초)

# UI 설정
PAGE_TITLE = "🎴 포켓몬 카드 가격 검색"
PAGE_ICON = "🎴"
LAYOUT = "wide"

# 메르카리 URL
MERCARI_BASE_URL = "https://jp.mercari.com"
MERCARI_ITEM_URL = "https://jp.mercari.com/item"

# 통화
CURRENCY = "¥"

# 상태 메시지
STATUS_MESSAGES = {
    "searching": "메르카리에서 데이터를 가져오는 중...",
    "processing": "데이터 처리 중...",
    "complete": "검색 완료!",
    "error": "오류가 발생했습니다.",
    "no_results": "검색 결과가 없습니다."
}

# 상품 상태
ITEM_STATUS = {
    "on_sale": "판매중",
    "sold_out": "판매완료"
}

# 색상 테마
COLORS = {
    "primary": "#667eea",
    "secondary": "#764ba2",
    "success": "#4caf50",
    "warning": "#ff9800",
    "error": "#f44336",
    "info": "#2196f3"
}
