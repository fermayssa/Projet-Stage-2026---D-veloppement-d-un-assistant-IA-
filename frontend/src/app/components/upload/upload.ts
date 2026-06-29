import { Component, OnInit, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService } from '../../services/api.service';
import { Document } from '../../models/interfaces';

@Component({
  selector: 'app-upload',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './upload.html',
  styleUrls: ['./upload.scss']
})
export class UploadComponent implements OnInit {

  @Output() documentUploaded = new EventEmitter<void>();

  documents: Document[] = [];
  isUploading = false;
  uploadMessage = '';
  uploadSuccess = false;
  isDragOver = false;

  constructor(private apiService: ApiService) {}

  ngOnInit() {
    this.loadDocuments();
  }

  loadDocuments() {
    this.apiService.getDocuments().subscribe({
      next: (res) => this.documents = res.documents,
      error: (err) => console.error('Erreur chargement', err)
    });
  }

  onFileSelected(event: any) {
    const file = event.target.files[0];
    if (file) this.uploadFile(file);
  }

  onDragOver(event: DragEvent) {
    event.preventDefault();
    this.isDragOver = true;
  }

  onDragLeave() {
    this.isDragOver = false;
  }

  onDrop(event: DragEvent) {
    event.preventDefault();
    this.isDragOver = false;
    const file = event.dataTransfer?.files[0];
    if (file) this.uploadFile(file);
  }

  uploadFile(file: File) {
    this.isUploading = true;
    this.uploadMessage = '';

    this.apiService.uploadDocument(file).subscribe({
      next: (res) => {
        this.isUploading = false;
        this.uploadSuccess = true;
        this.uploadMessage = `✅ "${res.filename}" importé — ${res.chunks_created} chunks`;
        this.loadDocuments();
        this.documentUploaded.emit();
      },
      error: (err) => {
        this.isUploading = false;
        this.uploadSuccess = false;
        this.uploadMessage = `❌ Erreur : ${err.error?.detail || 'Upload échoué'}`;
      }
    });
  }

  deleteDocument(fileId: string) {
    this.apiService.deleteDocument(fileId).subscribe({
      next: () => this.loadDocuments(),
      error: (err) => console.error('Erreur suppression', err)
    });
  }
}