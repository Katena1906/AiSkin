import React, { useState } from 'react';

interface BoundingBox {
  x: number;
  y: number;
  width: number;
  height: number;
  label: string;
  confidence: number;
}

interface ImageAnnotatorProps {
  imageUrl: string;
  boxes?: BoundingBox[];
  heatmap?: string;
  onBoxClick?: (box: BoundingBox) => void;
}

const ImageAnnotator: React.FC<ImageAnnotatorProps> = ({
  imageUrl,
  boxes = [],
  heatmap,
  onBoxClick,
}) => {
  const [showHeatmap, setShowHeatmap] = useState(false);

  const getBoxColor = (label: string) => {
    const colors: Record<string, string> = {
      acne: '#e0bfd8',
      actinic_keratosis: '#e0bfd8',
      basal_cell_carcinoma: '#e0bfd8',
      rosacea: '#e0bfd8',
      healthy: '#8bb1a5',
    };
    return colors[label] || '#696d74';
  };

  const handleBoxKeyDown = (
    event: React.KeyboardEvent<SVGGElement>,
    box: BoundingBox
  ) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      onBoxClick?.(box);
    }
  };

  return (
    <section className="annotator">
      <div className="annotator__controls">
        <button
          type="button"
          onClick={() => setShowHeatmap(false)}
          className={showHeatmap ? 'annotator__toggle' : 'annotator__toggle is-active'}
        >
          Оригинал
        </button>
        {heatmap && (
          <button
            type="button"
            onClick={() => setShowHeatmap(true)}
            className={showHeatmap ? 'annotator__toggle is-active' : 'annotator__toggle'}
          >
            Тепловая карта
          </button>
        )}
      </div>

      <div className="annotator__stage">
        {!showHeatmap ? (
          <div className="annotator__frame">
            <img className="annotator__image" src={imageUrl} alt="Анализ кожи" />
            <svg className="annotator__overlay" viewBox="0 0 100 100" preserveAspectRatio="none">
              {boxes.map((box, idx) => {
                const color = getBoxColor(box.label);
                const labelY = Math.min(box.y + box.height + 5, 96);

                return (
                  <g
                    key={idx}
                    className="annotator-box"
                    onClick={() => onBoxClick?.(box)}
                    onKeyDown={(event) => handleBoxKeyDown(event, box)}
                    role="button"
                    tabIndex={0}
                  >
                    <rect
                      x={box.x}
                      y={box.y}
                      width={box.width}
                      height={box.height}
                      rx="2.5"
                      className="annotator-box__shape"
                      stroke={color}
                    />
                    <text
                      x={box.x}
                      y={labelY}
                      className="annotator-box__label"
                      fill={color}
                    >
                      {box.label}: {(box.confidence * 100).toFixed(0)}%
                    </text>
                  </g>
                );
              })}
            </svg>
          </div>
        ) : (
          <img className="annotator__image" src={heatmap} alt="Тепловая карта" />
        )}
      </div>

      {boxes.length > 0 && (
        <div className="annotator__hint">
          <p>Нажмите на любую рамку, чтобы увидеть подробности</p>
        </div>
      )}
    </section>
  );
};

export default ImageAnnotator;
