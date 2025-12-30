import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';

@Component({
  selector: 'test-cases',
  standalone: true,
  imports: [CommonModule, RouterLink],
  styleUrls: ['./test_cases.css'],
  templateUrl: './test_cases.html'
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