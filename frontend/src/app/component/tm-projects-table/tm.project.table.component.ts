import { Component, inject, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { LoaderComponent } from '../loader/loader.component';
import { ProjectsService, Projects } from '../../services/tm.project.service';
import { MatTableDataSource, MatTableModule } from '@angular/material/table';
import { EmptyStateComponent } from '../empty-state/empty.state.component';
import { ErrorStateComponent } from '../error-state/error.state.component';
import { StatusBadgeComponent } from '../status-badge/status.badge.component';
import { Router } from '@angular/router';

@Component({
  selector: 'app-tm-projects-table',
  standalone: true,
  imports: [
    CommonModule,
    MatTableModule,
    LoaderComponent,
    EmptyStateComponent,
    ErrorStateComponent,
    StatusBadgeComponent
  ],
  styleUrls: ['./tm.project.table.component.css'],
  templateUrl: './tm.project.table.component.html'
})

export class TmProjectsTableComponent implements OnInit {
  cdr = inject(ChangeDetectorRef);
  router = inject(Router);
  displayedColumns = ['KEY', 'DESCRIPTION', '# TESTS', '# CYCLES', 'STATUS'];
  projectsDataSource: MatTableDataSource<Projects>;
  isLoading = false;
  error = '';

  constructor(
    private projectsService: ProjectsService
  ) {
    this.projectsDataSource = new MatTableDataSource<Projects>([]);
  }

  loadProjects() {
    this.isLoading = true;
    this.error = '';

    this.projectsService.getProjects().subscribe({
      next: (response) => {
        this.projectsDataSource.data = Array.isArray(response) ? response : [];
        console.log('Projects data loaded:', this.projectsDataSource.data);
        this.isLoading = false;
        this.cdr.markForCheck();
      },
      error: (error) => {
        console.error('Error fetching projects data:', error);
        this.error = `Error fetching projects data: ${error.message || error}`;
        this.isLoading = false;
        this.cdr.markForCheck();
      }
    });
  }

  onProjectClick(event: MouseEvent, projectKey: string) {
    if (event.button === 1) {
      // Middle mouse button
      event.preventDefault();
      const url = this.router.serializeUrl(this.router.createUrlTree(['/projects', projectKey, 'test-cases']));
      window.open(url, '_blank');
    } else if (event.button === 0) {
      // Left mouse button
      this.router.navigate(['/projects', projectKey, 'test-cases']);
    }
  }

  ngOnInit(): void {
    this.loadProjects();
  }
}

