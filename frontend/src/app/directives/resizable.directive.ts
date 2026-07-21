import { Directive, ElementRef, Input, OnInit, Renderer2, HostListener } from '@angular/core';

@Directive({
  selector: '[appResizable]',
  standalone: true
})
export class ResizableDirective implements OnInit {
  // 'right' = poignée à droite (sidebar gauche qui s'agrandit vers la droite)
  // 'left'  = poignée à gauche  (sidebar droite qui s'agrandit vers la gauche)
  @Input('appResizable') edge: 'left' | 'right' = 'right';
  @Input() minWidth = 200;
  @Input() maxWidth = 480;
  @Input() defaultWidth = 260;
  @Input() storageKey?: string;

  private handle!: HTMLElement;
  private startX = 0;
  private startWidth = 0;
  private resizing = false;

  constructor(private el: ElementRef<HTMLElement>, private renderer: Renderer2) {}

  ngOnInit(): void {
    const saved = this.storageKey ? Number(localStorage.getItem(this.storageKey)) : NaN;
    const initialWidth = !isNaN(saved) && saved > 0 ? saved : this.defaultWidth;
    this.setWidth(initialWidth);

    this.handle = this.renderer.createElement('div');
    this.renderer.addClass(this.handle, 'resize-handle');
    this.renderer.addClass(this.handle, `resize-handle-${this.edge}`);
    this.renderer.appendChild(this.el.nativeElement, this.handle);
    this.renderer.setStyle(this.el.nativeElement, 'position', 'relative');

    this.renderer.listen(this.handle, 'mousedown', (event: MouseEvent) => this.onMouseDown(event));
  }

  private onMouseDown(event: MouseEvent): void {
    event.preventDefault();
    this.resizing = true;
    this.startX = event.clientX;
    this.startWidth = this.el.nativeElement.getBoundingClientRect().width;
    document.body.style.cursor = 'col-resize';
    document.body.style.userSelect = 'none';
  }

  @HostListener('document:mousemove', ['$event'])
  onMouseMove(event: MouseEvent): void {
    if (!this.resizing) return;
    const delta = event.clientX - this.startX;
    // Sur le panneau droit, glisser vers la gauche doit AGRANDIR le panneau
    const directionalDelta = this.edge === 'right' ? delta : -delta;
    let newWidth = this.startWidth + directionalDelta;
    newWidth = Math.min(this.maxWidth, Math.max(this.minWidth, newWidth));
    this.setWidth(newWidth);
  }

  @HostListener('document:mouseup')
  onMouseUp(): void {
    if (!this.resizing) return;
    this.resizing = false;
    document.body.style.cursor = '';
    document.body.style.userSelect = '';

    if (this.storageKey) {
      const width = Math.round(this.el.nativeElement.getBoundingClientRect().width);
      localStorage.setItem(this.storageKey, String(width));
    }
  }

  private setWidth(width: number): void {
    this.renderer.setStyle(this.el.nativeElement, 'width', `${width}px`);
  }
}