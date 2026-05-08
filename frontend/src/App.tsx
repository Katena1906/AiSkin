import React, { useEffect, useState } from 'react';
import UploadArea from './components/UploadArea';
import Results from './components/Results';
import { analyzeImage } from './services/api';
import { ApiResponse } from './types';
import './App.css';

const App: React.FC = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<ApiResponse | null>(null);
  const [uploadedImageUrl, setUploadedImageUrl] = useState<string>('');

  useEffect(() => {
    return () => {
      if (uploadedImageUrl) {
        URL.revokeObjectURL(uploadedImageUrl);
      }
    };
  }, [uploadedImageUrl]);

  const handleFileSelect = async (file: File) => {
    setIsLoading(true);

    if (uploadedImageUrl) {
      URL.revokeObjectURL(uploadedImageUrl);
    }

    const imageUrl = URL.createObjectURL(file);
    setUploadedImageUrl(imageUrl);

    try {
      const response = await analyzeImage(file);
      if (response.success) {
        setResult(response);
      } else {
        alert('Анализ не удалось выполнить');
      }
    } catch (error) {
      alert('Ошибка подключения к серверу');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app-shell">
      <header className="app-hero">
        <div className="app-hero__eyebrow">Анализ кожи с ИИ</div>
        <h1 className="app-hero__title">AiSkin</h1>
        <p className="app-hero__subtitle">
          Загрузите фото, чтобы получить разбор состояния кожи, список вероятных диагнозов и рекомендации по уходу.
        </p>
      </header>

      <main className="app-main">
        {!result ? (
          <UploadArea onFileSelect={handleFileSelect} isLoading={isLoading} />
        ) : (
          <Results
            analysis={result.analysis}
            recommendations={result.recommendations}
            onReset={() => setResult(null)}
            uploadedImageUrl={uploadedImageUrl}
          />
        )}
        {isLoading && (
          <div className="loading-state" aria-live="polite">
            <div className="loading-state__spinner" />
            <p className="loading-state__text">Анализируем изображение...</p>
          </div>
        )}
      </main>

      <footer className="app-footer">
        <p>Результаты носят справочный характер и не заменяют консультацию врача.</p>
      </footer>
    </div>
  );
};

export default App;
