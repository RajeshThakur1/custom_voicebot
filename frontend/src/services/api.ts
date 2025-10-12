import axios from 'axios';

// Base API configuration
// Use proxy path for development to avoid CORS issues
const API_BASE_URL = '/api'; // This will be proxied to http://localhost:8001 by Vite

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// API service class for name operations
export interface UploadPdfResponse {
  id?: string | number;
  name?: string;
  // Allow arbitrary fields from backend response without forcing UI to depend on them
  [key: string]: unknown;
}

export class APIService {
  
  // Upload PDF document
  static async uploadPdf(
    file: File,
    documentName: string,
    onProgress?: (percent: number) => void
  ): Promise<UploadPdfResponse> {
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('document_name', documentName);
      
      const response = await api.post('/documents/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          if (!progressEvent.total) return;
          const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onProgress?.(percent);
        },
      });
      return response.data;
    } catch (error) {
      console.error('Error uploading PDF:', error);
      throw new Error('Failed to upload PDF document');
    }
  }

  // Delete PDF document
  static async deletePdf(pdfId: number): Promise<void> {
    try {
      await api.delete(`/pdf/${pdfId}`);
    } catch (error) {
      console.error('Error deleting PDF:', error);
      throw new Error('Failed to delete PDF document');
    }
  }

  // Get PDF document by ID
  static async getPdfById(pdfId: number): Promise<any> {
    try {
      const response = await api.get(`/pdf/${pdfId}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching PDF:', error);
      throw new Error('Failed to fetch PDF document');
    }
  }
}

export default api;
