import { Component } from '@angular/core';
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

  constructor(private apiService: ApiService) {}

  sendMessage() {
    if (!this.currentQuestion.trim() || this.isLoading) return;

    const question = this.currentQuestion.trim();
    this.currentQuestion = '';

    this.messages.push({ role: 'user', content: question });
    this.isLoading = true;

    this.apiService.sendMessage(question).subscribe({
      next: (res) => {
        this.isLoading = false;
        this.messages.push({
          role: 'assistant',
          content: res.answer,
          sources: res.sources
        });
      },
      error: () => {
        this.isLoading = false;
        this.messages.push({
          role: 'assistant',
          content: '❌ Erreur lors de la génération de la réponse.'
        });
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
  }
}