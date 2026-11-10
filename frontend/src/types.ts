export interface VideoItem { id: string; original_filename: string; content_type?: string; file_extension?: string; file_size_bytes?: number; status?: string; created_at?: string; updated_at?: string; }
export interface JobItem { id: string; video_id: string; profile?: string; status?: string; attempt_count?: number; max_attempts?: number; error_message?: string | null; output_path?: string | null; created_at?: string; updated_at?: string; }
export interface PageResult<T> { items: T[]; total?: number; limit?: number; offset?: number; }
export interface OutputItem { profile?: string; resolution?: string; status?: string; output_path?: string; [key: string]: unknown; }
