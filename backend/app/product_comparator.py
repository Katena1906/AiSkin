# C:\AiSkin\app\product_comparator.py
from typing import List, Dict

class ProductComparator:
    def compare_products(self, products: List[Dict]) -> Dict:
        if len(products) < 2:
            return {}
        
        return {
            'best_price': min(products, key=lambda x: x.get('price', float('inf'))),
            'best_rating': max(products, key=lambda x: x.get('effectiveness', 0)),
            'best_value': self._calculate_best_value(products),
            'comparison_table': self._create_comparison_table(products)
        }
    
    def _calculate_best_value(self, products: List[Dict]) -> Dict:
        for product in products:
            if product.get('price') and product.get('effectiveness'):
                product['value_score'] = product['effectiveness'] / (product['price'] / 1000)
        return max(products, key=lambda x: x.get('value_score', 0))
    
    def _create_comparison_table(self, products: List[Dict]) -> List[Dict]:
        table = []
        for product in products:
            table.append({
                'name': product['name'],
                'price': product.get('price', 'N/A'),
                'rating': product.get('effectiveness', 'N/A'),
                'reviews': product.get('user_reviews', 0)
            })
        return table