import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../services/api.service';
import { ChatMessage, Document } from '../../models/interfaces';
import { ViewChild, ElementRef, AfterViewChecked } from '@angular/core';



@Component({
  selector: 'app-chat',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './chat.html',
  styleUrls: ['./chat.scss']
})
export class ChatComponent implements OnInit, AfterViewChecked {

  messages: ChatMessage[] = [];
  currentQuestion = '';
  isLoading = false;
  
  // Documents disponibles et sélection
  availableDocuments: Document[] = [];
  selectedFileIds: string[] = [];
  showDocumentSelector = false;
  filterMode: 'all' | 'selection' = 'all';

  starterPrompts = [
    'Quelles sont les technologies utilisées dans ce projet ?',
    'Résume le contenu du document principal',
    'Quels sont les besoins fonctionnels décrits ?'
  ];

  followUpSuggestions = [
    'Donne plus de détails sur ce point',
    'Cite le passage exact du document',
    'Quels autres documents parlent de ce sujet ?'
  ];

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
        this.availableDocuments = res.documents;
        this.cdr.detectChanges();
      }
    });
  }

  toggleDocumentSelector() {
    this.showDocumentSelector = !this.showDocumentSelector;
    if (this.showDocumentSelector) this.loadDocuments();
  }

  setFilterMode(mode: 'all' | 'selection') {
    this.filterMode = mode;
    if (mode === 'all') this.selectedFileIds = [];
    this.cdr.detectChanges();
  }

  toggleDocumentSelection(fileId: string) {
    const idx = this.selectedFileIds.indexOf(fileId);
    if (idx === -1) {
      this.selectedFileIds.push(fileId);
    } else {
      this.selectedFileIds.splice(idx, 1);
    }
    this.cdr.detectChanges();
  }

  isSelected(fileId: string): boolean {
    return this.selectedFileIds.includes(fileId);
  }

  getFilterLabel(): string {
    if (this.filterMode === 'all') return 'Tous les documents';
    if (this.selectedFileIds.length === 0) return 'Aucun document sélectionné';
    return `${this.selectedFileIds.length} document(s) sélectionné(s)`;
  }

  sendMessage(text?: string) {
    const question = (text ?? this.currentQuestion).trim();
    if (!question || this.isLoading) return;
    if (this.filterMode === 'selection' && this.selectedFileIds.length === 0) {
      alert('Veuillez sélectionner au moins un document.');
      return;
    }

    this.currentQuestion = '';
    this.showDocumentSelector = false;
    
    const fileIds = this.filterMode === 'selection' ? this.selectedFileIds : undefined;
    
    this.messages.push({ role: 'user', content: question });
    this.isLoading = true;
    this.cdr.detectChanges();

    this.apiService.sendMessage(question, fileIds).subscribe({
      next: (res) => {
        this.isLoading = false;
        this.messages.push({
          role: 'assistant',
          content: res.answer,
          sources: res.sources,
          filtered_by: res.filtered_by
        });
        this.cdr.detectChanges();
      },
      error: () => {
        this.isLoading = false;
        this.messages.push({
          role: 'assistant',
          content: "Erreur lors de la génération de la réponse."
        });
        this.cdr.detectChanges();
      }
    });
  }

  onKeyDown(event: KeyboardEvent) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      this.sendMessage();
    }
  }

  clearChat() {
    this.messages = [];
    this.cdr.detectChanges();
  }

  scorePercent(score: number): number {
    return Math.round(score * 100);
  }
  @ViewChild('messagesEnd') messagesEnd!: ElementRef;

  ngAfterViewChecked() {
    this.messagesEnd?.nativeElement?.scrollIntoView({ behavior: 'smooth' });
  }


}