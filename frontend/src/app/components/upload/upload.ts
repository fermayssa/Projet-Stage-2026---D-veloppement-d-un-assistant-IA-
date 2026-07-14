import { Component, OnInit, Output, EventEmitter, ChangeDetectorRef } from '@angular/core';
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

  // Aperçu document
  previewDocId: string | null = null;
  previewData: any = null;
  isLoadingPreview = false;

  constructor(
    private apiService: ApiService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit() {
    this.loadDocuments();
  }

  loadDocuments() {
    this.apiService.getDocuments().subscribe({
      next: (res) => {
        this.documents = res.documents;
        this.cdr.detectChanges();
      },
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
    this.cdr.detectChanges();

    this.apiService.uploadDocument(file).subscribe({
      next: (res) => {
        this.isUploading = false;
        this.uploadSuccess = true;
        this.uploadMessage = `"${res.filename}" importé — ${res.chunks_created} chunks`;
        this.loadDocuments();
        this.documentUploaded.emit();
        this.cdr.detectChanges();
      },
      error: (err) => {
        this.isUploading = false;
        this.uploadSuccess = false;
        this.uploadMessage = `Erreur : ${err.error?.detail || 'Upload échoué'}`;
        this.cdr.detectChanges();
      }
    });
  }

  deleteDocument(fileId: string, event: Event) {
    event.stopPropagation(); // Empêche l'ouverture du preview
    if (this.previewDocId === fileId) {
      this.closePreview();
    }
    this.apiService.deleteDocument(fileId).subscribe({
      next: () => this.loadDocuments(),
      error: (err) => console.error('Erreur suppression', err)
    });
  }

  togglePreview(doc: Document) {
    if (this.previewDocId === doc.file_id) {
      this.closePreview();
      return;
    }

    this.previewDocId = doc.file_id;
    this.previewData = null;
    this.isLoadingPreview = true;
    this.cdr.detectChanges();

    this.apiService.getDocumentPreview(doc.file_id).subscribe({
      next: (data) => {
        this.previewData = data;
        this.isLoadingPreview = false;
        this.cdr.detectChanges();
      },
      error: () => {
        this.isLoadingPreview = false;
        this.previewData = { error: 'Impossible de charger l\'aperçu' };
        this.cdr.detectChanges();
      }
    });
  }

  closePreview() {
    this.previewDocId = null;
    this.previewData = null;
    this.cdr.detectChanges();
  }
}