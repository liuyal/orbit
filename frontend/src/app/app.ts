import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
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
  data$: Observable<any[]> = this.http.get<any[]>('api/tm/projects');
  refresh() {
    this.data$ = this.http.get<any[]>('api/tm/projects');
  }
}

