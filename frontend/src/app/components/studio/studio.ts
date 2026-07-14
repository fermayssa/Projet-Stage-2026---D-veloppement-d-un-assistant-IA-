import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService } from '../../services/api.service';
import { Document, FormField, FormSuggestion, GeneratedForm } from '../../models/interfaces';
import { FormViewerComponent } from '../form-viewer/form-viewer';
import { FormsModule } from '@angular/forms';

type StudioStep = 'idle' | 'selecting' | 'suggesting' | 'confirming' | 'viewing';

@Component({
  selector: 'app-studio',
  standalone: true,
  imports: [CommonModule, FormViewerComponent, FormsModule],
  templateUrl: './studio.html',
  styleUrls: ['./studio.scss']
})
export class StudioComponent implements OnInit {

  step: StudioStep = 'idle';
  documents: Document[] = [];
  selectedFileId: string = '';
  selectedFilename: string = '';
  suggestion: FormSuggestion | null = null;
  selectedFields: FormField[] = [];
  generatedForm: GeneratedForm | null = null;
  isLoading = false;
  errorMessage = '';

  // Ajouter après selectedFields
  showAddField = false;
  newField = {
    label: '',
    type: 'text' as 'text' | 'number' | 'date' | 'email' | 'textarea' | 'select',
    placeholder: '',
    obligatoire: false
  };
  fieldTypes = ['text', 'number', 'date', 'email', 'textarea', 'select'];

  // Ajouter ces méthodes
  openAddField() {
    this.showAddField = true;
    this.newField = { label: '', type: 'text', placeholder: '', obligatoire: false };
    this.cdr.detectChanges();
  }

  cancelAddField() {
    this.showAddField = false;
    this.cdr.detectChanges();
  }

  confirmAddField() {
    if (!this.newField.label.trim()) return;

    const field: FormField = {
      id: `custom_${Date.now()}`,
      label: this.newField.label.trim(),
      type: this.newField.type,
      placeholder: this.newField.placeholder,
      valeur_extraite: '',
      obligatoire: this.newField.obligatoire
    };

    // Ajouter à la suggestion et à la sélection
    this.suggestion!.champs.push(field);
    this.selectedFields.push(field);
    this.showAddField = false;
    this.cdr.detectChanges();
  }


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
      }
    });
  }

  startFormGeneration() {
    this.loadDocuments();
    this.step = 'selecting';
    this.errorMessage = '';
    this.cdr.detectChanges();
  }

  selectDocument(doc: Document) {
    this.selectedFileId = doc.file_id;
    this.selectedFilename = doc.filename;
    this.step = 'suggesting';
    this.isLoading = true;
    this.cdr.detectChanges();

    this.apiService.suggestFormFields(doc.file_id).subscribe({
      next: (res) => {
        this.suggestion = res;
        this.selectedFields = res.champs.map(f => ({ ...f, selected: true }));
        this.isLoading = false;
        this.step = 'confirming';
        this.cdr.detectChanges();
      },
      error: (err) => {
        this.isLoading = false;
        this.errorMessage = 'Erreur lors de l\'analyse du document.';
        this.step = 'idle';
        this.cdr.detectChanges();
      }
    });
  }

  toggleField(field: FormField) {
    const idx = this.selectedFields.findIndex(f => f.id === field.id);
    if (idx !== -1) {
      this.selectedFields.splice(idx, 1);
    } else {
      this.selectedFields.push(field);
    }
    this.cdr.detectChanges();
  }

  isFieldSelected(fieldId: string): boolean {
    return this.selectedFields.some(f => f.id === fieldId);
  }

  confirmAndGenerate() {
    if (this.selectedFields.length === 0) return;
    this.isLoading = true;
    this.cdr.detectChanges();

    this.apiService.generateForm(this.selectedFileId, this.selectedFields).subscribe({
      next: (res) => {
        this.generatedForm = {
          titre_formulaire: this.suggestion?.titre_formulaire || 'Formulaire généré',
          description: this.suggestion?.description || '',
          champs: res.champs || this.selectedFields,
          file_id: this.selectedFileId,
          generated_at: new Date().toISOString()
        };
        this.isLoading = false;
        this.step = 'viewing';
        this.cdr.detectChanges();
      },
      error: () => {
        this.isLoading = false;
        this.errorMessage = 'Erreur lors de la génération.';
        this.cdr.detectChanges();
      }
    });
  }

  reset() {
    this.step = 'idle';
    this.suggestion = null;
    this.selectedFields = [];
    this.generatedForm = null;
    this.errorMessage = '';
    this.cdr.detectChanges();
  }
}