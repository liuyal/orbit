import { bootstrapApplication } from '@angular/platform-browser';
import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { provideHttpClient, HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';


@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule],
  template: `

    <button (click)="refresh()">Refresh</button>
    
    @if (data$ | async; as data) {
      <p>{{ data | json }}</p>
    } @else {
      <p>Loading...</p>
    }
  `
})

export class App {
  http = inject(HttpClient);
  data$: Observable<any[]> = this.http.get<any[]>('api/projects');

  refresh() {
    this.data$ = this.http.get<any[]>('api/projects');
  }
}

bootstrapApplication(App, { providers: [provideHttpClient()] });