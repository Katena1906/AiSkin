from typing import List, Dict
from datetime import datetime
from rxnorm_api import TreatmentGenerator

class SmartProductRecommender:
    def __init__(self):
        self.treatment_generator = TreatmentGenerator()
        
        self.ingredient_focus = {
            'acne': ['салициловая кислота', 'ниацинамид', 'цинк', 'ретинол', 'бензоил пероксид'],
            'rosacea': ['азелаиновая кислота', 'ниацинамид', 'центелла', 'сквалан', 'метронидазол'],
            'actinic_keratosis': ['витамин с', 'ниацинамид', 'ретинол', 'фторурацил'],
            'basal_cell_carcinoma': ['пантенол', 'центелла', 'аллантоин', 'висмодегиб'],
            'healthy': ['гиалуроновая кислота', 'керамиды', 'пептиды', 'витамин е']
        }
    
    async def get_smart_recommendations(self, disease: str, confidence: float, skin_type: str = None) -> Dict:
        treatment_plan = await self.treatment_generator.generate_treatment_plan(disease, confidence)
        
        return {
            'disease': disease,
            'confidence': confidence,
            'treatment_plan': treatment_plan,
            'ingredient_focus': self.ingredient_focus.get(disease, self.ingredient_focus['healthy']),
            'skin_type_advice': self._get_skin_type_advice(skin_type) if skin_type else {},
            'seasonal_advice': self._get_seasonal_advice(),
            'general_advice': self._get_general_advice(disease),
            'skincare_routine': self._get_routine(disease)
        }
    
    def _get_skin_type_advice(self, skin_type: str) -> Dict:
        advice = {
            'oily': {'text': 'Жирная кожа', 'tips': ['Легкие текстуры', 'Увлажнение'], 'avoid': ['Тяжелые масла']},
            'dry': {'text': 'Сухая кожа', 'tips': ['Кремы с керамидами', 'Пить воду'], 'avoid': ['Спиртовые тоники']},
            'sensitive': {'text': 'Чувствительная кожа', 'tips': ['Средства без отдушек', 'SPF'], 'avoid': ['Ретинол', 'Кислоты']}
        }
        return advice.get(skin_type, advice['dry'])
    
    def _get_seasonal_advice(self) -> Dict:
        month = datetime.now().month
        if month <= 2 or month == 12:
            return {'season': 'Зима', 'advice': 'Защита от холода, SPF, питательные кремы'}
        elif 3 <= month <= 5:
            return {'season': 'Весна', 'advice': 'Легкие текстуры, витамин С'}
        elif 6 <= month <= 8:
            return {'season': 'Лето', 'advice': 'SPF 50+, антиоксиданты, увлажнение'}
        else:
            return {'season': 'Осень', 'advice': 'Восстановление кожи, добавьте ретинол'}
    
    def _get_general_advice(self, disease: str) -> List[str]:
        advice = {
            'acne': ['Очищайте кожу дважды в день', 'Используйте некомедогенные средства', 'Не выдавливайте прыщи'],
            'rosacea': ['Избегайте горячей воды', 'Защищайте кожу от солнца', 'Исключите алкоголь и острую пищу'],
            'actinic_keratosis': ['SPF 50+ ежедневно', 'Носите защитную одежду', 'Регулярно проверяйтесь у дерматолога'],
            'basal_cell_carcinoma': ['НЕМЕДЛЕННО ОБРАТИТЕСЬ К ВРАЧУ', 'Требуется биопсия', 'Строгая фотозащита'],
            'healthy': ['Ежедневное увлажнение', 'SPF 30+ каждый день', 'Пейте воду']
        }
        return advice.get(disease, advice['healthy'])
    
    def _get_routine(self, disease: str) -> Dict:
        routines = {
            'acne': {
                'morning': ['Мягкое очищение', 'Легкий увлажняющий крем', 'SPF 30+'],
                'evening': ['Двойное очищение', 'Сыворотка с ниацинамидом', 'Увлажняющий крем']
            },
            'rosacea': {
                'morning': ['Умывание прохладной водой', 'Успокаивающий крем', 'SPF 50+'],
                'evening': ['Мягкое очищение', 'Сыворотка с азелаиновой кислотой', 'Успокаивающий крем']
            },
            'actinic_keratosis': {
                'morning': ['Мягкое очищение', 'Антиоксидантная сыворотка', 'SPF 50+'],
                'evening': ['Очищение', 'Регенерирующий крем', 'Восстанавливающий бальзам']
            },
            'basal_cell_carcinoma': {
                'morning': ['Мягкое очищение', 'Восстанавливающий крем', 'SPF 50+'],
                'evening': ['Мягкое очищение', 'Цикапласт бальзам']
            },
            'healthy': {
                'morning': ['Очищение', 'Сыворотка с витамином С', 'Увлажняющий крем', 'SPF 30+'],
                'evening': ['Двойное очищение', 'Ретинол 2-3 раза в неделю', 'Увлажняющий крем']
            }
        }
        return routines.get(disease, routines['healthy'])