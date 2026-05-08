import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';

interface UploadAreaProps {
  onFileSelect: (file: File) => void;
  isLoading: boolean;
}

const UploadArea: React.FC<UploadAreaProps> = ({ onFileSelect, isLoading }) => {
  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0 && !isLoading) {
      onFileSelect(acceptedFiles[0]);
    }
  }, [onFileSelect, isLoading]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'image/*': ['.jpg', '.jpeg', '.png'] },
    maxFiles: 1,
    disabled: isLoading,
  });

  return (
    <div
      className="upload-area"
      {...getRootProps()}
      style={{
        border: `2px dashed ${isDragActive ? '#ee9dcc' : '#9da6b4'}`,
        borderRadius: '24px',
        padding: '60px',
        textAlign: 'center',
        cursor: isLoading ? 'not-allowed' : 'pointer',
        backgroundColor: isDragActive ? '#eef5ff' : '#f7fbff',
        transition: 'all 0.3s',
        opacity: isLoading ? 0.6 : 1,
      }}
    >
      <input {...getInputProps()} />
      <div style={{ fontSize: '64px', marginBottom: '20px' }}></div>
      <h3 style={{ marginBottom: '10px', color: '#17324d' }}>
        {isDragActive ? 'Отпустите изображение здесь' : 'Загрузите фото кожи'}
      </h3>
      <p style={{ color: '#5b708a', marginBottom: '24px' }}>
        Нажмите или перетащите файл JPG, JPEG или PNG
      </p>
      <button
        style={{
          background: 'linear-gradient(135deg, #db89b9 0%, #df92b2 100%)',
          color: 'white',
          border: 'none',
          padding: '12px 32px',
          borderRadius: '40px',
          fontSize: '16px',
          cursor: isLoading ? 'not-allowed' : 'pointer',
        }}
        disabled={isLoading}
      >
        Выбрать изображение
      </button>
    </div>
  );
};

export default UploadArea;
