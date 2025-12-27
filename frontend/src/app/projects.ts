import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule],
  styles: [`
    .prj-refresh-btn {
      padding: 10px;
      width: 40px;
      height: 40px;
      border: 1px solid #ccc;
      border-radius: 5px;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .prj-refresh-btn:hover {
      background-color: #0057adff;
    }
    .prj-table {
      margin-top: 15px;
      width: 100%;
      border-collapse: collapse;
      border-radius: 5px;
    }
    .prj-table th
    .prj-table td {
      border: 1px solid #cccccc41;
      padding: 15px;
      text-align: left;
    }
    .prj-table th {
      font-weight: bold;
    }
  `],
  template: `
    <div style="margin: 25px;">

      <div style="display: flex; gap: 10px;">
        <button class="prj-refresh-btn" (click)="refresh()">
          <i class="fa-solid fa-arrows-rotate"></i>
        </button>
        <button class="prj-refresh-btn" (click)="refresh()">
          <i class="fa-solid fa-plus"></i>
        </button>
      </div>

      @if (data$ | async; as data) {
        <table class="prj-table" border="2">
          <thead>
            <tr>
              <th>PROJECTS</th>
              <th>DESCRIPTION</th>
              <th>STATUS</th>
            </tr>
          </thead>
          <tbody>
            @for (item of data; track item.project_key) {
              <tr>
                <td>{{ item.project_key }}</td>
                <td>{{ item.description }}</td>
                <td>
                  @if (item.is_active == true ) {
                    <i class="fa-solid fa-circle-check" style="color: green;"></i>
                  } @else {
                    <i class="fa-solid fa-circle-xmark" style="color: red;"></i>
                  }
                </td>
              </tr>
            }
          </tbody>
        </table>

      } @else {
        <p>Loading...</p>
      }

    </div>
  `
})

export class Project {
  http = inject(HttpClient);
  data$: Observable<any[]> = this.http.get<any[]>('api/projects');
  refresh() {
    this.data$ = this.http.get<any[]>('api/projects');
  }
}
