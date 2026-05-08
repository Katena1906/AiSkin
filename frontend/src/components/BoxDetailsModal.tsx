import React from 'react';

interface BoundingBox {
  x: number;
  y: number;
  width: number;
  height: number;
  label: string;
  confidence: number;
}

interface BoxDetailsModalProps {
  box: BoundingBox | null;
  onClose: () => void;
}

const diseaseDescriptions: Record<string, { title: string, description: string, advice: string }> = {
  acne: {
    title: 'Акне',
    description: 'Воспалительное заболевание кожи, возникающее при закупорке сальных желез.',
    advice: 'Рекомендуется очищение, избегайте комедогенных средств, обратитесь к дерматологу.'
  },
  actinic_keratosis: {
    title: 'Актинический кератоз',
    description: 'Предраковое состояние кожи, вызванное солнечным повреждением.',
    advice: 'Требуется наблюдение дерматолога, используйте SPF 50+ ежедневно.'
  },
  basal_cell_carcinoma: {
    title: 'Базально-клеточная карцинома',
    description: 'Самый распространенный тип рака кожи.',
    advice: 'НЕМЕДЛЕННО обратитесь к дерматологу для биопсии и лечения.'
  },
  rosacea: {
    title: 'Розацеа',
    description: 'Хроническое воспалительное заболевание кожи лица.',
    advice: 'Избегайте триггеров (алкоголь, острая пища), используйте мягкие средства.'
  },
  healthy: {
    title: 'Здоровая кожа',
    description: 'Признаков заболевания не обнаружено.',
    advice: 'Продолжайте регулярный уход и используйте SPF.'
  }
};

const BoxDetailsModal: React.FC<BoxDetailsModalProps> = ({ box, onClose }) => {
  if (!box) return null;

  const info = diseaseDescriptions[box.label] || {
    title: box.label,
    description: 'Информация о данном состоянии отсутствует.',
    advice: 'Проконсультируйтесь с врачом.'
  };

  const handleBackdropClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Escape') {
      onClose();
    }
  };

  return (
    <div
      className="modal-overlay"
      onClick={handleBackdropClick}
      onKeyDown={handleKeyDown}
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-title"
      tabIndex={-1}
    >
      <div className="modal-container">
        <button className="modal-close" onClick={onClose} aria-label="Закрыть">
          ✕
        </button>
        
        <div className="modal-header">
          <span className="modal-icon">🔬</span>
          <h3 id="modal-title" className="modal-title">{info.title}</h3>
        </div>

        <div className="modal-body">
          <div className="modal-confidence">
            <span>Уверенность:</span>
            <strong>{(box.confidence * 100).toFixed(1)}%</strong>
          </div>

          <div className="modal-section">
            <h4>📋 Описание</h4>
            <p>{info.description}</p>
          </div>

          <div className="modal-section">
            <h4>💡 Рекомендации</h4>
            <p>{info.advice}</p>
          </div>

          <div className="modal-location">
            <h4>📍 Локация</h4>
            <p>Область обнаружена в указанной зоне на изображении.</p>
          </div>
        </div>

        <div className="modal-footer">
          <button className="modal-btn" onClick={onClose}>
            Понятно
          </button>
        </div>
      </div>

      <style>{`
        .modal-overlay {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(0, 0, 0, 0.5);
          backdrop-filter: blur(4px);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 1000;
          animation: fadeIn 0.2s ease;
        }

        @keyframes fadeIn {
          from { opacity: 0; }
          to { opacity: 1; }
        }

        @keyframes slideUp {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        .modal-container {
          background: white;
          border-radius: 28px;
          width: 90%;
          max-width: 480px;
          max-height: 85vh;
          overflow-y: auto;
          box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
          animation: slideUp 0.3s ease;
          position: relative;
        }

        .modal-close {
          position: absolute;
          top: 16px;
          right: 20px;
          background: none;
          border: none;
          font-size: 22px;
          cursor: pointer;
          color: #a8899e;
          transition: color 0.2s;
          z-index: 1;
        }

        .modal-close:hover {
          color: #e88bb0;
        }

        .modal-header {
          padding: 28px 28px 16px;
          border-bottom: 1px solid rgba(245, 169, 199, 0.2);
          display: flex;
          align-items: center;
          gap: 12px;
        }

        .modal-icon {
          font-size: 32px;
        }

        .modal-title {
          font-size: 1.5em;
          font-weight: 600;
          color: #7a5a6e;
          margin: 0;
        }

        .modal-body {
          padding: 20px 28px;
        }

        .modal-confidence {
          background: #fef6f9;
          padding: 12px 16px;
          border-radius: 16px;
          display: flex;
          justify-content: space-between;
          margin-bottom: 20px;
          font-size: 0.95rem;
          color: #7a5a6e;
        }

        .modal-confidence strong {
          color: #e88bb0;
          font-size: 1.1em;
        }

        .modal-section {
          margin-bottom: 20px;
        }

        .modal-section h4 {
          color: #e88bb0;
          margin-bottom: 8px;
          font-size: 1rem;
          font-weight: 600;
        }

        .modal-section p {
          color: #a8899e;
          line-height: 1.6;
          font-size: 0.95rem;
          margin: 0;
        }

        .modal-location {
          background: #fef6f9;
          padding: 12px 16px;
          border-radius: 16px;
          margin-top: 8px;
        }

        .modal-location h4 {
          color: #e88bb0;
          margin-bottom: 8px;
          font-size: 0.9rem;
          font-weight: 600;
        }

        .modal-location p {
          color: #a8899e;
          font-size: 0.85rem;
          margin: 0;
        }

        .modal-footer {
          padding: 16px 28px 28px;
          border-top: 1px solid rgba(245, 169, 199, 0.15);
        }

        .modal-btn {
          width: 100%;
          background: linear-gradient(135deg, #f5a9c7, #e88bb0);
          color: white;
          border: none;
          padding: 12px 20px;
          border-radius: 40px;
          font-size: 1rem;
          font-weight: 500;
          cursor: pointer;
          transition: all 0.2s;
        }

        .modal-btn:hover {
          transform: translateY(-1px);
          box-shadow: 0 6px 14px rgba(232, 139, 176, 0.3);
        }
      `}</style>
    </div>
  );
};

export default BoxDetailsModal;