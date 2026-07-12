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
  page?: number;
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  sources?: Source[];
  filtered_by?: string[] | string;
}

export interface ChatResponse {
  question: string;
  answer: string;
  sources: Source[];
  filtered_by?: string[] | string;
}

// NOUVEAU
export interface ChatRequest {
  question: string;
  file_ids?: string[];
}
export interface FormField {
  id: string;
  label: string;
  type: 'text' | 'number' | 'date' | 'email' | 'textarea' | 'select';
  placeholder?: string;
  valeur_extraite?: string;
  obligatoire?: boolean;
  options?: string[];
  valeur_editee?: string;
}

export interface FormSuggestion {
  titre_formulaire: string;
  description: string;
  champs: FormField[];
}

export interface GeneratedForm {
  titre_formulaire: string;
  description: string;
  champs: FormField[];
  file_id: string;
  generated_at: string;
}