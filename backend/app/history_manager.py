# C:\AiSkin\app\history_manager.py
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict

class HistoryManager:
    def __init__(self):
        self.history_file = Path("user_history.json")
        self.history = self._load_history()
    
    def _load_history(self) -> List[Dict]:
        if self.history_file.exists():
            with open(self.history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def _save_history(self):
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)
    
    def add_analysis(self, analysis: Dict):
        analysis['date'] = datetime.now().isoformat()
        self.history.append(analysis)
        self._save_history()
    
    def get_history(self) -> List[Dict]:
        return self.history
    
    def delete_analysis(self, analysis_id: str) -> bool:
        initial_length = len(self.history)
        self.history = [a for a in self.history if a.get('id') != analysis_id]
        if len(self.history) != initial_length:
            self._save_history()
            return True
        return False
    
    def get_user_stats(self) -> Dict:
        if not self.history:
            return {}
        
        diseases = [h['disease'] for h in self.history]
        return {
            'total_analyses': len(self.history),
            'common_disease': max(set(diseases), key=diseases.count),
            'last_analysis': self.history[-1]['date'],
            'improvement_trend': "stable"
        }