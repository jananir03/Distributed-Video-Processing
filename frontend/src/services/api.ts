import axios from 'axios';
import type { JobItem, OutputItem, PageResult, VideoItem } from '../types';

export const API_BASE = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000').replace(/\/$/, '');
export const api = axios.create({ baseURL: API_BASE, timeout: 120000 });
api.interceptors.request.use(config => { config.headers['X-Correlation-ID'] ||= crypto.randomUUID(); return config; });

const asArray = <T,>(data: unknown): T[] => {
  if (Array.isArray(data)) return data as T[];
  if (data && typeof data === 'object') {
    const obj = data as Record<string, unknown>;
    for (const key of ['items', 'videos', 'jobs', 'outputs', 'thumbnails', 'results']) if (Array.isArray(obj[key])) return obj[key] as T[];
  }
  return [];
};
export const videoApi = {
  async list(): Promise<PageResult<VideoItem>> { const { data } = await api.get('/api/v1/upload/videos', { params: { limit: 100, offset: 0 } }); return { items: asArray<VideoItem>(data), total: data?.total ?? asArray<VideoItem>(data).length }; },
  async get(id: string): Promise<VideoItem> { const { data } = await api.get(`/api/v1/upload/videos/${encodeURIComponent(id)}`); return data; },
  async upload(file: File, onProgress?: (n: number) => void): Promise<VideoItem> { const form = new FormData(); form.append('file', file); const { data } = await api.post('/api/v1/upload/videos/upload', form, { headers: { 'Content-Type': 'multipart/form-data' }, onUploadProgress: e => onProgress?.(e.total ? Math.round(e.loaded * 100 / e.total) : 0) }); return data; },
  async status(id: string): Promise<Record<string, unknown>> { const { data } = await api.get(`/api/v1/videos/${encodeURIComponent(id)}/status`); return data; },
  async process(id: string): Promise<Record<string, unknown>> { const { data } = await api.post(`/api/v1/videos/${encodeURIComponent(id)}/process`); return data; },
  async jobs(id: string): Promise<JobItem[]> { const { data } = await api.get('/api/v1/orchestrator/jobs', { params: { video_id: id, limit: 100, offset: 0 } }); return asArray<JobItem>(data); },
  async outputs(id: string): Promise<OutputItem[]> { const { data } = await api.get(`/api/v1/media/videos/${encodeURIComponent(id)}/outputs`, { params: { limit: 100, offset: 0 } }); return asArray<OutputItem>(data); },
  async thumbnails(id: string): Promise<unknown> { const { data } = await api.get(`/api/v1/thumbnails/${encodeURIComponent(id)}`); return data; },
  streamUrl(id: string, profile: string) { return `${API_BASE}/api/v1/media/videos/${encodeURIComponent(id)}/stream?profile=${encodeURIComponent(profile)}`; },
  downloadUrl(id: string, profile: string) { return `${API_BASE}/api/v1/media/videos/${encodeURIComponent(id)}/download?profile=${encodeURIComponent(profile)}`; },
  thumbnailUrl(id: string, profile: string) { return `${API_BASE}/api/v1/thumbnails/${encodeURIComponent(id)}/${encodeURIComponent(profile)}`; }
};
export function errorMessage(error: unknown): string { if (axios.isAxiosError(error)) { const d = error.response?.data as { detail?: unknown } | undefined; return typeof d?.detail === 'string' ? d.detail : JSON.stringify(d?.detail ?? error.message); } return error instanceof Error ? error.message : 'Something went wrong'; }
