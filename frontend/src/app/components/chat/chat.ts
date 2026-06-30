import { Component, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../services/api.service';
import { ChatMessage } from '../../models/interfaces';

@Component({
  selector: 'app-chat',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './chat.html',
  styleUrls: ['./chat.scss']
})
export class ChatComponent {

  messages: ChatMessage[] = [];
  currentQuestion = '';
  isLoading = false;

  starterPrompts = [
    'De quoi parle ce document ?',
    'Résume le contenu principal',
    'Quelles sont les fonctionnalités décrites ?'
  ];

  followUpSuggestions = [
    'Peux-tu donner plus de détails ?',
    'Quelles sont les sources exactes ?',
    'Résume en une phrase'
  ];

  constructor(
    private apiService: ApiService,
    private cdr: ChangeDetectorRef
  ) {}

  sendMessage(text?: string) {
    const question = (text ?? this.currentQuestion).trim();
    if (!question || this.isLoading) return;

    this.currentQuestion = '';
    this.messages.push({ role: 'user', content: question });
    this.isLoading = true;
    this.cdr.detectChanges();

    this.apiService.sendMessage(question).subscribe({
      next: (res) => {
        this.isLoading = false;
        this.messages.push({
          role: 'assistant',
          content: res.answer,
          sources: res.sources
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
}