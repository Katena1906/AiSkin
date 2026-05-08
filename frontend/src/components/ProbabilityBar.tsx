import React from 'react';

interface ProbabilityBarProps {
  label: string;
  value: number;
}

const diseaseNames: Record<string, string> = {
  acne: 'Акне',
  actinic_keratosis: 'Актинический кератоз',
  basal_cell_carcinoma: 'Базальноклеточный рак',
  rosacea: 'Розацеа',
  healthy: 'Здоровая кожа',
};

const ProbabilityBar: React.FC<ProbabilityBarProps> = ({ label, value }) => {
  const percent = (value * 100).toFixed(1);
  const gradientId = `probability-gradient-${label.replace(/[^a-z0-9]+/gi, '-').toLowerCase()}`;

  return (
    <div className="probability-card">
      <div className="probability-card__header">
        <span className="probability-card__label">{diseaseNames[label] || label}</span>
        <span className="probability-card__value">{percent}%</span>
      </div>
      <svg
        className="probability-card__meter"
        viewBox="0 0 100 12"
        preserveAspectRatio="none"
        role="img"
        aria-label={`Вероятность ${percent}% для ${diseaseNames[label] || label}`}
      >
        <defs>
          <linearGradient id={gradientId} x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#bbece3" />
            <stop offset="100%" stopColor="#849795" />
          </linearGradient>
        </defs>
        <rect className="probability-card__meter-track" x="0" y="0" width="100" height="12" rx="6" />
        <rect
          className="probability-card__meter-fill"
          x="0"
          y="0"
          width={value * 100}
          height="12"
          rx="6"
          fill={`url(#${gradientId})`}
        />
      </svg>
    </div>
  );
};

export default ProbabilityBar;
