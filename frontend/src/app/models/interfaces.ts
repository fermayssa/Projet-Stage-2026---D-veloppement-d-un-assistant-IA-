export interface UploadResponse {
  message: string;
  file_id: string;
  filename: string;
  document_type: string;
  pages: number;
  chars_extracted: number;
  chunks_created: number;
  indexed: boolean;
}

export interface Document {
  file_id: string;
  filename: string;
  type: string;
  pages: number;
  chunks: number;
  indexed: boolean;
}

export interface Source {
  filename: string;
  score: number;
  text_preview: string;
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  sources?: Source[];
}

export interface ChatResponse {
  question: string;
  answer: string;
  sources: Source[];
}