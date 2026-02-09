"""
메르카리 데이터 수집 모듈
mercapi 라이브러리를 사용하여 메르카리에서 포켓몬 카드 정보를 검색
"""

import asyncio
from typing import List, Dict, Optional
from mercapi import Mercapi
import config


class MercariScraper:
    """메르카리 스크래퍼 클래스"""
    
    def __init__(self):
        self.mercapi = Mercapi()
    
    async def search_pokemon_card(
        self,
        card_number: str,
        card_name: Optional[str] = None,
        limit: int = config.DEFAULT_SEARCH_LIMIT
    ) -> Dict:
        """
        포켓몬 카드 검색
        
        Args:
            card_number: 카드 번호 (예: "025/165")
            card_name: 카드 이름 (선택사항)
            limit: 최대 검색 결과 수
            
        Returns:
            검색 결과 딕셔너리
        """
        # 검색 쿼리 생성
        search_query = f"ポケモンカード {card_number}"
        if card_name:
            search_query += f" {card_name}"
        
        try:
            # 메르카리 검색
            results = await self.mercapi.search(
                keyword=search_query,
                limit=limit,
                sort=config.SEARCH_SORT_BY,
                order=config.SEARCH_ORDER
            )
            
            # 결과 파싱
            listings = []
            for item in results.items:
                listing = {
                    'item_id': item.id,
                    'name': item.name,
                    'price': item.price,
                    'status': item.status,
                    'thumbnail': item.thumbnails[0] if item.thumbnails else "",
                    'url': f"{config.MERCARI_ITEM_URL}/{item.id}",
                    'created_at': str(item.created) if hasattr(item, 'created') else None
                }
                listings.append(listing)
            
            return {
                'success': True,
                'query': search_query,
                'total_found': results.meta.num_found if hasattr(results, 'meta') else len(listings),
                'listings': listings
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'listings': []
            }
    
    async def get_item_details(self, item_id: str) -> Dict:
        """
        특정 상품의 상세 정보 조회
        
        Args:
            item_id: 메르카리 상품 ID
            
        Returns:
            상품 상세 정보
        """
        try:
            item = await self.mercapi.item(item_id)
            
            return {
                'success': True,
                'item_id': item.id,
                'name': item.name,
                'description': item.description,
                'price': item.price,
                'status': item.status,
                'seller': item.seller.name if hasattr(item, 'seller') else None,
                'images': item.photos if hasattr(item, 'photos') else [],
                'url': f"{config.MERCARI_ITEM_URL}/{item.id}"
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }


def search_card_sync(card_number: str, card_name: Optional[str] = None) -> Dict:
    """
    동기 방식으로 카드 검색 (Streamlit용)
    
    Args:
        card_number: 카드 번호
        card_name: 카드 이름 (선택사항)
        
    Returns:
        검색 결과
    """
    scraper = MercariScraper()
    
    # 이벤트 루프 생성 및 실행
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            scraper.search_pokemon_card(card_number, card_name)
        )
        loop.close()
        return result
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'listings': []
        }
