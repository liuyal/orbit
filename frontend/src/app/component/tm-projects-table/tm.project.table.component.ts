import { Component, inject, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { LoaderComponent } from '../loader/loader.component';
import { ProjectsService, Projects } from '../../services/tm.project.service';
import { MatTableDataSource } from '@angular/material/table';
import { EmptyStateComponent } from '../empty-state/empty.state.component';
import { ErrorStateComponent } from '../error-state/error.state.component';

@Component({
  selector: 'app-tm-projects-table',
  standalone: true,
  imports: [
    CommonModule,
    LoaderComponent,
    EmptyStateComponent,
    ErrorStateComponent
  ],
  styleUrls: ['./tm.project.table.component.css'],
  templateUrl: './tm.project.table.component.html'
})

export class TmProjectsTableComponent implements OnInit {
  cdr = inject(ChangeDetectorRef);
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

  ngOnInit(): void {
    this.loadProjects();
  }
}

