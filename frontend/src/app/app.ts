import { Component } from '@angular/core';
import { UploadComponent } from './components/upload/upload';
import { ChatComponent } from './components/chat/chat';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [UploadComponent, ChatComponent],
  templateUrl: './app.html',
  styleUrls: ['./app.scss']
})
export class App {
  title = 'RAG Assistant';
}