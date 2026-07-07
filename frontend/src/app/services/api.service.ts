import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { UploadResponse, ChatResponse, Document } from '../models/interfaces';

@Injectable({
  providedIn: 'root'
})
export class ApiService {

  private baseUrl = 'http://localhost:8000/api';

  constructor(private http: HttpClient) {}

  uploadDocument(file: File): Observable<UploadResponse> {
    const formData = new FormData();
    formData.append('file', file);
    return this.http.post<UploadResponse>(
      `${this.baseUrl}/upload`, formData
    );
  }

  getDocuments(): Observable<{documents: Document[], count: number}> {
    return this.http.get<{documents: Document[], count: number}>(
      `${this.baseUrl}/documents`
    );
  }

  deleteDocument(fileId: string): Observable<any> {
    return this.http.delete(`${this.baseUrl}/documents/${fileId}`);
  }

  sendMessage(question: string, fileIds?: string[]): Observable<ChatResponse> {
  const body: any = { question };
  if (fileIds && fileIds.length > 0) {
    body.file_ids = fileIds;
  }
  return this.http.post<ChatResponse>(`${this.baseUrl}/chat`, body);
}
}