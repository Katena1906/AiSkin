import axios from 'axios';
import { ApiResponse } from '../types';

const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
});

export const analyzeImage = async (file: File): Promise<ApiResponse> => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await api.post('/analyze', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
};