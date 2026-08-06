import { Component, signal, ChangeDetectionStrategy } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { FooterComponent } from './component/footer/footer';

@Component({
  selector: 'app-root',
  imports: [
    RouterOutlet,
    FooterComponent
  ],
  templateUrl: './app.component.html',
  changeDetection: ChangeDetectionStrategy.Eager,
  styleUrl: './app.component.css'
})
export class App {
  protected readonly title = signal('orbit');
}
