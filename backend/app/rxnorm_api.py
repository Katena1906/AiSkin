import json
import os
from typing import List, Dict
from datetime import datetime

class RxNormAPI:
    def __init__(self):
        self.base_url = "https://rxnav.nlm.nih.gov/REST"
        
        data_path = os.path.join(os.path.dirname(__file__), 'drug_data.json')
        with open(data_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        
        self.disease_mapping = self.data['disease_mapping']
        self.drug_details = self.data['drug_details']
        self.treatment_rationale = self.data['treatment_rationale']
        self.risk_warnings = self.data['risk_warnings']
        
        self.russian_names = {
            'isotretinoin': 'Изотретиноин', 'tretinoin': 'Третиноин', 'adapalene': 'Адапален',
            'clindamycin': 'Клиндамицин', 'benzoyl peroxide': 'Бензоил пероксид', 'salicylic acid': 'Салициловая кислота',
            'metronidazole': 'Метронидазол', 'azelaic acid': 'Азелаиновая кислота', 'ivermectin': 'Ивермектин',
            'doxycycline': 'Доксициклин', 'fluorouracil': 'Фторурацил', 'imiquimod': 'Имиквимод',
            'vismodegib': 'Висмодегиб', 'sonidegib': 'Сонидегиб', 'brimonidine': 'Бримонидин'
        }

    async def search_drugs(self, disease: str, limit: int = 3) -> List[Dict]:
        drugs = []
        
        if disease not in self.disease_mapping:
            return []
        
        search_terms = self.disease_mapping[disease]['search_terms']
        
        for term in search_terms[:limit]:
            drug_info = self.drug_details.get(term, {})
            
            drugs.append({
                'name': self.russian_names.get(term, term.capitalize()),
                'generic_name': term,
                'brand_names': drug_info.get('common_brands', []),
                'drug_class': drug_info.get('class', 'Неизвестно'),
                'how_it_works': drug_info.get('how_it_works', ''),
                'side_effects': drug_info.get('side_effects', []),
                'warning': drug_info.get('warning', 'Проконсультируйтесь с врачом.'),
                'prescription_required': term not in ['salicylic acid', 'benzoyl peroxide', 'adapalene'],
                'source': 'RxNorm'
            })
        
        return drugs

class TreatmentGenerator:
    def __init__(self):
        self.rxnorm = RxNormAPI()
        self.treatment_rationale = self.rxnorm.treatment_rationale
        self.risk_warnings = self.rxnorm.risk_warnings
    
    async def generate_treatment_plan(self, disease: str, confidence: float) -> Dict:
        rationale = self.treatment_rationale.get(disease, self.treatment_rationale['healthy'])
        
        plan = {
            'disease': disease,
            'confidence': confidence,
            'severity': self._get_severity_level(confidence),
            'explanation': rationale['explanation'],
            'treatment_goals': rationale['goals'],
            'first_line_treatments': rationale['first_line'],
            'second_line_treatments': rationale['second_line'] if confidence > 0.7 else [],
            'prescription_medications': [],
            'otc_recommendations': [],
            'lifestyle_modifications': self._get_lifestyle_advice(disease),
            'warning_level': self._get_warning_level(disease, confidence),
            'doctor_consultation_required': self._doctor_required(disease, confidence)
        }
        
        medications = await self.rxnorm.search_drugs(disease, limit=4)
        
        for med in medications:
            if med['prescription_required']:
                risk = self.risk_warnings.get(med['generic_name'], {})
                med['risk_level'] = risk.get('level', 'moderate')
                med['risk_message'] = risk.get('message', 'Проконсультируйтесь с врачом.')
                plan['prescription_medications'].append(med)
            else:
                plan['otc_recommendations'].append(med)
        
        return plan
    
    def _get_severity_level(self, confidence: float) -> str:
        if confidence > 0.85:
            return 'severe'
        elif confidence > 0.7:
            return 'moderate'
        elif confidence > 0.5:
            return 'mild'
        return 'low'
    
    def _get_warning_level(self, disease: str, confidence: float) -> str:
        if disease == 'basal_cell_carcinoma' and confidence > 0.5:
            return 'critical'
        elif disease == 'actinic_keratosis' and confidence > 0.7:
            return 'high'
        elif disease in ['acne', 'rosacea'] and confidence > 0.8:
            return 'advisory'
        return 'informational'
    
    def _doctor_required(self, disease: str, confidence: float) -> bool:
        if disease == 'basal_cell_carcinoma':
            return True
        if disease == 'actinic_keratosis' and confidence > 0.7:
            return True
        if confidence > 0.85:
            return True
        return False
    
    def _get_lifestyle_advice(self, disease: str) -> List[Dict]:
        advice = {
            'acne': [
                {'category': 'Уход за кожей', 'tip': 'Умывайтесь дважды в день мягким средством', 'why': 'Удаляет избыток кожного сала без повреждения барьера'},
                {'category': 'Питание', 'tip': 'Рассмотрите низкогликемическую диету', 'why': 'Высокий гликемический индекс может ухудшать акне'},
                {'category': 'Избегайте', 'tip': 'Не выдавливайте прыщи', 'why': 'Предотвращает рубцевание и инфекцию'}
            ],
            'rosacea': [
                {'category': 'Уход', 'tip': 'Используйте средства без отдушек', 'why': 'Отдушки провоцируют обострения'},
                {'category': 'Питание', 'tip': 'Избегайте алкоголя и острой пищи', 'why': 'Частые триггеры покраснения'},
                {'category': 'Избегайте', 'tip': 'Избегайте горячего душа', 'why': 'Тепло расширяет сосуды'}
            ],
            'actinic_keratosis': [
                {'category': 'Солнцезащита', 'tip': 'SPF 50+ каждые 2 часа', 'why': 'Предотвращает новые поражения'},
                {'category': 'Образ жизни', 'tip': 'Носите UPF одежду', 'why': 'Физическая защита наиболее эффективна'},
                {'category': 'Мониторинг', 'tip': 'Ежемесячный осмотр кожи', 'why': 'Раннее выявление изменений'}
            ],
            'basal_cell_carcinoma': [
                {'category': 'Медицина', 'tip': 'НЕМЕДЛЕННО ОБРАТИТЕСЬ К ДЕРМАТОЛОГУ', 'why': 'Требуется биопсия и лечение'},
                {'category': 'Солнцезащита', 'tip': 'Строгая защита от солнца', 'why': 'Предотвращает рецидивы'},
                {'category': 'Мониторинг', 'tip': 'Регулярные осмотры кожи', 'why': 'Повышенный риск новых БКК'}
            ],
            'healthy': [
                {'category': 'Уход', 'tip': 'Ежедневное увлажнение', 'why': 'Поддерживает барьер кожи'},
                {'category': 'Солнцезащита', 'tip': 'SPF 30+ ежедневно', 'why': 'Предотвращает фотостарение и рак'},
                {'category': 'Профилактика', 'tip': 'Ежегодный осмотр кожи', 'why': 'Раннее выявление изменений'}
            ]
        }
        return advice.get(disease, advice['healthy'])