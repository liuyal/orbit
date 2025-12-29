import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';

@Component({
  selector: 'test-cases',
  standalone: true,
  imports: [CommonModule],
  styles: [`
    .navbar {
      background-color: #1e1e1e;
      border-bottom: 2px solid #0057adff;
      padding: 0 30px;
      height: 70px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
      position: sticky;
      top: 0;
      z-index: 100;
    }
    .navbar-brand {
      display: flex;
      align-items: center;
      gap: 12px;
      font-size: 24px;
      font-weight: 700;
      color: #ffffff;
      padding: 20px;
    }
    .navbar-brand i {
      color: #0172ad;
      font-size: 28px;
    }
    .back-button {
      background: none;
      border: 1px solid #0057adff;
      color: #4da6ff;
      padding: 8px 16px;
      border-radius: 6px;
      cursor: pointer;
      font-size: 14px;
      display: flex;
      align-items: center;
      gap: 8px;
      transition: all 0.2s;
    }
    .back-button:hover {
      background-color: #0057adff;
      color: white;
    }
    .content {
      margin: 40px;
    }
    .page-header {
      margin-bottom: 20px;
    }
    .page-header h1 {
      color: #ffffff;
      font-size: 32px;
      margin: 0 0 10px 0;
    }
    .project-info {
      font-size: 20px;
    }
    .tabs-container {
      margin-top: 30px;
      background-color: #1e1e1e;
      border-radius: 8px 8px 0 0;
      border-bottom: 2px solid #333;
    }
    .tabs {
      display: flex;
      gap: 0;
    }
    .tab {
      padding: 15px 30px;
      background-color: #1e1e1e;
      border: none;
      color: #ffffffff;
      font-size: 16px;
      font-weight: 500;
      cursor: pointer;
      border-bottom: 3px solid transparent;
      transition: all 0.2s;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .tab:hover {
      color: #e0e0e0;
      background-color: #252525;
    }
    .tab.active {
      color: #ffffff;
      background-color: #2a2a2a;
      border-bottom-color: #0057adff;
    }
    .tab-content {
      padding: 30px;
      color: #e0e0e0;
      background-color: #1e1e1e;
      border-radius: 0 0 8px 8px;
      min-height: 400px;
    }
  `],
  template: `
    <nav class="navbar">
      <div class="navbar-brand">
        <i class="fa-solid fa-rocket"></i>
        <span>ORBIT</span>
      </div>
      <button class="back-button" (click)="goBack()">
        <i class="fa-solid fa-arrow-left"></i>
        Back to Projects
      </button>
    </nav>

    <div class="content">
      <div class="tabs-container">
        <div class="tabs">
          <button 
            class="tab" 
            [class.active]="activeTab === 'test-cases'"
            (click)="activeTab = 'test-cases'">
            <i class="fa-solid fa-flask"></i>
            Test Cases
          </button>
          <button 
            class="tab" 
            [class.active]="activeTab === 'test-cycles'"
            (click)="activeTab = 'test-cycles'">
            <i class="fa-regular fa-rectangle-list"></i>
            Test Cycles
          </button>
        </div>
      </div>

      <div class="tab-content">
        @if (activeTab === 'test-cases') {
          <div>
            <p style="color: #999;">Test cases functionality coming soon...</p>
          </div>
        } @else if (activeTab === 'test-cycles') {
          <div>
            <p style="color: #999;">Test cycles functionality coming soon...</p>
          </div>
        }
      </div>
    </div>
  `
})

export class TestCases {
  route = inject(ActivatedRoute);
  router = inject(Router);
  projectKey = '';
  activeTab: 'test-cases' | 'test-cycles' = 'test-cases';

  ngOnInit() {
    this.route.params.subscribe(params => {
      this.projectKey = params['projectKey'];
      console.log('Test Cases page for project:', this.projectKey);
    });
  }

  goBack() {
    this.router.navigate(['/projects']);
  }
}