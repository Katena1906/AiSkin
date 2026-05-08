import React, { useState } from 'react';
import ProbabilityBar from './ProbabilityBar';
import { AnalysisResult, Recommendations, DrugRecommendation, BoundingBox } from '../types';
import ImageAnnotator from './ImageAnnotator';
import BoxDetailsModal from './BoxDetailsModal';

interface ResultsProps {
  analysis: AnalysisResult;
  recommendations: Recommendations;
  onReset: () => void;
  uploadedImageUrl?: string;
}

const diseaseNames: Record<string, string> = {
  acne: 'Акне',
  actinic_keratosis: 'Актинический кератоз',
  basal_cell_carcinoma: 'Базально-клеточная карцинома',
  rosacea: 'Розацеа',
  healthy: 'Здоровая кожа',
};

const warningLabels: Record<string, string> = {
  low: 'Низкий',
  informational: 'Информационный',
  advisory: 'Рекомендуемый',
  moderate: 'Средний',
  high: 'Высокий',
  critical: 'Критический',
};

const formatList = (items?: string[]) => items && items.length > 0 ? items.join(', ') : 'Нет данных';

const MedicationCard: React.FC<{ drug: DrugRecommendation }> = ({ drug }) => {
  return (
    <div className="product-card">
      <div className="product-card__body">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
          <div>
            <h4 className="product-card__title">{drug.name}</h4>
            <div className="product-card__brand">{drug.drug_class}</div>
          </div>
          <div style={{ 
            background: drug.prescription_required ? '#e6bcd3' : '#98a8a6', 
            padding: '4px 12px', 
            borderRadius: '20px', 
            fontSize: '12px',
            fontWeight: 500
          }}>
            {drug.prescription_required ? 'По рецепту' : 'Без рецепта'}
          </div>
        </div>

        <div className="product-card__description">{drug.how_it_works}</div>

        <div style={{ marginBottom: '12px' }}>
          <div style={{ marginBottom: '8px' }}>
            <strong>Действующее вещество:</strong> {drug.generic_name || 'Не указано'}
          </div>
          <div style={{ marginBottom: '8px' }}>
            <strong>Торговые названия:</strong> {formatList(drug.brand_names)}
          </div>
        </div>

        <div className="product-how-to">
          <strong>Побочные эффекты:</strong> {formatList(drug.side_effects)}
        </div>
        
        <div className="product-reason" style={{ background: drug.risk_level === 'critical' ? '#fdaadc62' : '#a5f1f133' }}>
          <strong>Предупреждение:</strong> {drug.warning}
        </div>
      </div>
    </div>
  );
};

const Results: React.FC<ResultsProps> = ({ analysis, recommendations, onReset, uploadedImageUrl }) => {
  const treatmentPlan = recommendations.treatment_plan;
  const topRisks = Object.entries(analysis.all_probabilities).sort((a, b) => b[1] - a[1]);
  
  const [selectedBox, setSelectedBox] = useState<BoundingBox | null>(null);

  const handleBoxClick = (box: BoundingBox) => {
    setSelectedBox(box);
  };

  const handleCloseModal = () => {
    setSelectedBox(null);
  };

  return (
    <div style={{ animation: 'fadeIn 0.5s ease' }}>
      {selectedBox && (
        <BoxDetailsModal box={selectedBox} onClose={handleCloseModal} />
      )}

      <style>{`
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(20px); }
          to { opacity: 1; transform: translateY(0); }
        }
      `}</style>

      <div className="top-prediction">
        <h3>Результат анализа</h3>
        <div className="disease-name">{diseaseNames[analysis.disease] || analysis.disease}</div>
        <div className="confidence">Уверенность: {(analysis.confidence * 100).toFixed(1)}%</div>
        {analysis.needs_doctor && (
          <div className="urgent-warning">
            Требуется срочная консультация врача!
          </div>
        )}
      </div>

      <div style={{ display: 'flex', gap: '32px', flexWrap: 'wrap', marginBottom: '24px' }}>
        <div style={{ flex: 2, minWidth: '200px' }}>
          <div style={{ background: '#f5fafa', padding: '16px', borderRadius: '16px' }}>
            <div style={{ color: '#929ea7', fontSize: '12px', marginBottom: '4px' }}>Степень риска</div>
            <div style={{ fontWeight: 600, fontSize: '18px' }}>{warningLabels[treatmentPlan?.warning_level] || 'Не определен'}</div>
          </div>
        </div>
        <div style={{ flex: 2, minWidth: '200px' }}>
          <div style={{ background: '#f5fafa', padding: '16px', borderRadius: '16px' }}>
            <div style={{ color: '#929ea7', fontSize: '12px', marginBottom: '4px' }}>Консультация врача</div>
            <div style={{ fontWeight: 600, fontSize: '18px' }}>{treatmentPlan?.doctor_consultation_required ? 'Обязательна' : 'Не обязательна'}</div>
          </div>
        </div>
        <div style={{ flex: 3, minWidth: '250px' }}>
          <div style={{ background: '#f5fafa', padding: '16px', borderRadius: '16px' }}>
            <div style={{ color: '#929ea7', fontSize: '12px', marginBottom: '4px' }}>Ключевые ингредиенты</div>
            <div style={{ fontWeight: 500 }}>{recommendations.ingredient_focus?.slice(0, 4).join(', ') || 'Нет данных'}</div>
          </div>
        </div>
      </div>

      {analysis.bounding_boxes && analysis.bounding_boxes.length > 0 && uploadedImageUrl && (
        <ImageAnnotator
          imageUrl={uploadedImageUrl}
          boxes={analysis.bounding_boxes}
          heatmap={analysis.heatmap}
          onBoxClick={handleBoxClick}
        />
      )}

      <h3 style={{ marginBottom: '20px', color: '#868d96' }}>Вероятности диагнозов:</h3>
      {topRisks.map(([key, value]) => (
        <ProbabilityBar key={key} label={key} value={value} />
      ))}

      {treatmentPlan && (
        <>
          <div style={{ background: '#f0f6f6', borderRadius: '20px', padding: '24px', margin: '24px 0' }}>
            <h3 style={{ marginBottom: '12px', color: '#5a7a8a' }}>О заболевании</h3>
            <p style={{ lineHeight: '1.6', color: '#a1adbb' }}>{treatmentPlan.explanation}</p>
            
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px', marginTop: '20px' }}>
              <div>
                <h4 style={{ color: '#909da5', marginBottom: '12px' }}>Цели лечения</h4>
                <ul style={{ paddingLeft: '20px' }}>
                  {treatmentPlan.treatment_goals?.map((goal: string, i: number) => (
                    <li key={i} style={{ marginBottom: '8px' }}>{goal}</li>
                  ))}
                </ul>
              </div>
              {recommendations.skin_type_advice && (
                <div>
                  <h4 style={{ color: '#8f9aa1', marginBottom: '12px' }}>Тип кожи: {recommendations.skin_type_advice.text}</h4>
                  <ul style={{ paddingLeft: '20px' }}>
                    {recommendations.skin_type_advice.tips?.slice(0, 3).map((tip: string, i: number) => (
                      <li key={i} style={{ marginBottom: '8px' }}>{tip}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>

          {treatmentPlan.doctor_consultation_required && (
            <div style={{ background: '#fff0e6', borderRadius: '20px', padding: '24px', marginBottom: '24px', borderLeft: '4px solid #e8b4b8' }}>
              <h3 style={{ color: '#dda9c6', marginBottom: '8px' }}>⚠️ Важное предупреждение</h3>
              <p>Для данного состояния ТРЕБУЕТСЯ консультация дерматолога. Не занимайтесь самолечением.</p>
            </div>
          )}

          <div style={{ marginBottom: '24px' }}>
            <h3 style={{ marginBottom: '16px', color: '#4a5a6e' }}>Первая линия терапии</h3>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '12px' }}>
              {treatmentPlan.first_line_treatments?.map((treatment: string, i: number) => (
                <span key={i} style={{ background: '#e0f3f0', padding: '8px 16px', borderRadius: '20px', fontSize: '14px', color: '#5a7a8a' }}>
                  {treatment}
                </span>
              ))}
            </div>
          </div>

          {treatmentPlan.otc_recommendations && treatmentPlan.otc_recommendations.length > 0 && (
            <div style={{ marginBottom: '32px' }}>
              <h3 style={{ marginBottom: '20px', color: '#4a5a6e' }}>Безрецептурные средства</h3>
              <div className="products-grid">
                {treatmentPlan.otc_recommendations.map((drug: DrugRecommendation, idx: number) => (
                  <MedicationCard key={idx} drug={drug} />
                ))}
              </div>
            </div>
          )}

          {treatmentPlan.prescription_medications && treatmentPlan.prescription_medications.length > 0 && (
            <div style={{ marginBottom: '32px' }}>
              <h3 style={{ marginBottom: '20px', color: '#696d72' }}>Рецептурные препараты (только по назначению врача)</h3>
              <div className="products-grid">
                {treatmentPlan.prescription_medications.map((drug: DrugRecommendation, idx: number) => (
                  <MedicationCard key={idx} drug={drug} />
                ))}
              </div>
            </div>
          )}

          <div style={{ marginTop: '48px', paddingTop: '32px', borderTop: '2px solid #daefed' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', marginBottom: '24px' }}>
              <h2 style={{ fontSize: '1.5em', color: '#4a5a6e' }}>Рекомендации по уходу</h2>
              <button onClick={onReset} className="btn-secondary">
                Новый анализ
              </button>
            </div>
            
            <div className="routine-steps">
              <div className="routine-step">
                <h4>Утро</h4>
                <ul>
                  {recommendations.skincare_routine?.morning?.map((step: string, i: number) => (
                    <li key={i}>{step}</li>
                  ))}
                </ul>
              </div>
              <div className="routine-step">
                <h4>Вечер</h4>
                <ul>
                  {recommendations.skincare_routine?.evening?.map((step: string, i: number) => (
                    <li key={i}>{step}</li>
                  ))}
                </ul>
              </div>
            </div>

            {recommendations.general_advice && (
              <div className="advice-card">
                <h3>Общие рекомендации</h3>
                <ul className="advice-list">
                  {recommendations.general_advice.map((advice: string, i: number) => (
                    <li key={i}>{advice}</li>
                  ))}
                </ul>
              </div>
            )}

            {recommendations.seasonal_advice && (
              <div className="advice-card">
                <h3>{recommendations.seasonal_advice.season}</h3>
                <p>{recommendations.seasonal_advice.advice}</p>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
};

export default Results;