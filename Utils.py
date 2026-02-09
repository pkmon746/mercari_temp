"""
유틸리티 함수
데이터 처리, 통계 계산 등의 헬퍼 함수
"""

import statistics
from typing import List, Dict, Optional
import pandas as pd
import config


def calculate_price_statistics(listings: List[Dict]) -> Dict:
    """
    가격 통계 계산
    
    Args:
        listings: 상품 목록
        
    Returns:
        가격 통계 딕셔너리
    """
    if not listings:
        return {
            'total_listings': 0,
            'active_listings': 0,
            'sold_listings': 0,
            'average_price': None,
            'median_price': None,
            'min_price': None,
            'max_price': None,
            'active_prices': [],
            'sold_prices': []
        }
    
    # 가격 분류
    active_prices = []
    sold_prices = []
    
    for listing in listings:
        price = listing['price']
        if listing['status'] == 'sold_out':
            sold_prices.append(price)
        else:
            active_prices.append(price)
    
    all_prices = active_prices + sold_prices
    
    return {
        'total_listings': len(listings),
        'active_listings': len(active_prices),
        'sold_listings': len(sold_prices),
        'average_price': round(statistics.mean(all_prices), 2) if all_prices else None,
        'median_price': round(statistics.median(all_prices), 2) if all_prices else None,
        'min_price': min(all_prices) if all_prices else None,
        'max_price': max(all_prices) if all_prices else None,
        'active_prices': active_prices,
        'sold_prices': sold_prices
    }


def format_price(price: Optional[float]) -> str:
    """
    가격 포맷팅
    
    Args:
        price: 가격
        
    Returns:
        포맷된 가격 문자열
    """
    if price is None:
        return "-"
    return f"{config.CURRENCY}{int(price):,}"


def create_listings_dataframe(listings: List[Dict]) -> pd.DataFrame:
    """
    상품 목록을 DataFrame으로 변환
    
    Args:
        listings: 상품 목록
        
    Returns:
        pandas DataFrame
    """
    if not listings:
        return pd.DataFrame()
    
    df = pd.DataFrame(listings)
    
    # 상태 한글화
    df['status_kr'] = df['status'].map({
        'sold_out': config.ITEM_STATUS['sold_out'],
        'on_sale': config.ITEM_STATUS['on_sale']
    })
    
    # 가격 포맷팅
    df['price_formatted'] = df['price'].apply(lambda x: f"{config.CURRENCY}{x:,}")
    
    return df


def get_price_distribution(prices: List[int], bins: int = 10) -> Dict:
    """
    가격 분포 계산
    
    Args:
        prices: 가격 리스트
        bins: 구간 개수
        
    Returns:
        가격 분포 데이터
    """
    if not prices:
        return {'bins': [], 'counts': []}
    
    import numpy as np
    
    counts, bin_edges = np.histogram(prices, bins=bins)
    
    return {
        'bins': bin_edges.tolist(),
        'counts': counts.tolist()
    }


def filter_listings_by_price(
    listings: List[Dict],
    min_price: Optional[int] = None,
    max_price: Optional[int] = None
) -> List[Dict]:
    """
    가격 범위로 상품 필터링
    
    Args:
        listings: 상품 목록
        min_price: 최소 가격
        max_price: 최대 가격
        
    Returns:
        필터링된 상품 목록
    """
    filtered = listings
    
    if min_price is not None:
        filtered = [l for l in filtered if l['price'] >= min_price]
    
    if max_price is not None:
        filtered = [l for l in filtered if l['price'] <= max_price]
    
    return filtered


def filter_listings_by_status(
    listings: List[Dict],
    status: str
) -> List[Dict]:
    """
    상태로 상품 필터링
    
    Args:
        listings: 상품 목록
        status: 'on_sale' 또는 'sold_out'
        
    Returns:
        필터링된 상품 목록
    """
    return [l for l in listings if l['status'] == status]


def get_recent_listings(listings: List[Dict], limit: int = 10) -> List[Dict]:
    """
    최근 등록된 상품 가져오기
    
    Args:
        listings: 상품 목록
        limit: 최대 개수
        
    Returns:
        최근 상품 목록
    """
    # created_at 기준으로 정렬 (없으면 원본 순서 유지)
    sorted_listings = sorted(
        listings,
        key=lambda x: x.get('created_at', ''),
        reverse=True
    )
    
    return sorted_listings[:limit]
