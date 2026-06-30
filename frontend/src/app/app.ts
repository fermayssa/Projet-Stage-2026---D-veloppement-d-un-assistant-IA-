import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { UploadComponent } from './components/upload/upload';
import { ChatComponent } from './components/chat/chat';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, UploadComponent, ChatComponent],
  templateUrl: './app.html',
  styleUrls: ['./app.scss']
})
export class App {
  title = 'RAG Assistant';

  activeSection: string = 'documents';
  documentsExpanded = true;

  navItems = [
    { id: 'documents', label: 'Documents', icon: '▤', expandable: true },
    { id: 'corpus', label: 'Corpus', icon: '▦', expandable: false },
    { id: 'conversations', label: 'Conversations', icon: '◔', expandable: false },
    { id: 'historique', label: 'Historique', icon: '◷', expandable: false },
    { id: 'parametres', label: 'Paramètres', icon: '⚙', expandable: false }
  ];

  selectSection(id: string) {
    if (id === 'documents') {
      this.documentsExpanded = !this.documentsExpanded;
    }
    this.activeSection = id;
  }
}