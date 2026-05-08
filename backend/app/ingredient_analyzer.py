from typing import List, Dict

class IngredientAnalyzer:
    def __init__(self):
        self.bad_ingredients = {
            'acne': ['isopropyl myristate', 'lanolin', 'coconut oil', 'alcohol'],
            'rosacea': ['menthol', 'camphor', 'alcohol', 'fragrance', 'essential oils'],
            'sensitive': ['parfum', 'limonene', 'linalool', 'alcohol']
        }
        
        self.good_ingredients = {
            'acne': ['salicylic acid', 'niacinamide', 'zinc', 'retinol'],
            'rosacea': ['azelaic acid', 'niacinamide', 'centella', 'squalane'],
            'sensitive': ['panthenol', 'allantoin', 'bisabolol', 'thermal water']
        }
    
    def analyze_ingredients(self, ingredients_text: str, skin_condition: str) -> Dict:
        ingredients_lower = ingredients_text.lower()
        
        found_bad = [ing for ing in self.bad_ingredients.get(skin_condition, []) 
                    if ing in ingredients_lower]
        found_good = [ing for ing in self.good_ingredients.get(skin_condition, []) 
                     if ing in ingredients_lower]
        
        score = 100 - (len(found_bad) * 15) + (len(found_good) * 10)
        score = max(0, min(100, score))
        
        return {
            'score': score,
            'good_ingredients': found_good,
            'bad_ingredients': found_bad,
            'verdict': 'Suitable' if score >= 70 else 'Risk present' if score >= 40 else 'Not recommended',
            'explanation': self._generate_explanation(found_good, found_bad)
        }
    
    def _generate_explanation(self, good: List[str], bad: List[str]) -> str:
        explanation = []
        if good:
            explanation.append(f"Contains beneficial components: {', '.join(good)}")
        if bad:
            explanation.append(f"Contains potentially irritating components: {', '.join(bad)}")
        return ' '.join(explanation) if explanation else "Composition requires additional analysis"