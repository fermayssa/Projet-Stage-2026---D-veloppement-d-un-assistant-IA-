import { Component, Input, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { GeneratedForm, FormField } from '../../models/interfaces';

@Component({
  selector: 'app-form-viewer',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './form-viewer.html',
  styleUrls: ['./form-viewer.scss']
})
export class FormViewerComponent implements OnInit {

  @Input() form!: GeneratedForm;
  isEditing = false;
  editableFields: FormField[] = [];

  constructor(private cdr: ChangeDetectorRef) {}

  ngOnInit() {
    this.editableFields = this.form.champs.map(f => ({
      ...f,
      valeur_editee: f.valeur_extraite || ''
    }));
  }

  toggleEdit() {
    this.isEditing = !this.isEditing;
    this.cdr.detectChanges();
  }

  downloadJson() {
    const data = {
      titre: this.form.titre_formulaire,
      date_generation: this.form.generated_at,
      champs: this.editableFields.map(f => ({
        label: f.label,
        valeur: f.valeur_editee || f.valeur_extraite
      }))
    };

    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${this.form.titre_formulaire.replace(/\s+/g, '_')}.json`;
    a.click();
    URL.revokeObjectURL(url);
  }

  downloadPdf() {
    const content = this.buildPdfContent();
    const blob = new Blob([content], { type: 'text/html' });
    const url = URL.createObjectURL(blob);

    const printWindow = window.open(url, '_blank');
    if (printWindow) {
      printWindow.onload = () => {
        printWindow.print();
        URL.revokeObjectURL(url);
      };
    }
  }

  private buildPdfContent(): string {
    const rows = this.editableFields.map(f => `
      <tr>
        <td style="font-weight:600;padding:8px 12px;border:1px solid #ddd;background:#f9f9f9;width:40%">${f.label}</td>
        <td style="padding:8px 12px;border:1px solid #ddd">${f.valeur_editee || f.valeur_extraite || '-'}</td>
      </tr>
    `).join('');

    return `
      <!DOCTYPE html>
      <html>
      <head>
        <meta charset="utf-8">
        <title>${this.form.titre_formulaire}</title>
        <style>
          body { font-family: 'Segoe UI', sans-serif; padding: 40px; color: #111; }
          h1 { font-size: 20px; margin-bottom: 8px; }
          p { color: #666; font-size: 13px; margin-bottom: 24px; }
          table { width: 100%; border-collapse: collapse; }
        </style>
      </head>
      <body>
        <h1>${this.form.titre_formulaire}</h1>
        <p>${this.form.description}</p>
        <table>${rows}</table>
      </body>
      </html>
    `;
  }
}