import { Component, inject, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { NavbarComponent } from '../../navbar/navbar';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, FormsModule, NavbarComponent],
  styleUrls: ['./projects.css'],
  templateUrl: './projects.html'
})

export class Project {
  http = inject(HttpClient);
  cdr = inject(ChangeDetectorRef);
  router = inject(Router);
  projects: any[] = [];
  isLoading = true;
  error = '';
  showCreateModal = false;
  showEditModal = false;
  newProject = {
    project_key: '',
    description: '',
    is_active: true
  };
  editProjectData = {
    project_key: '',
    description: '',
    is_active: true
  };
  errors = {
    project_key: '',
    description: ''
  };
  apiError = '';

  ngOnInit() {
    this.loadProjects();
  }

  loadProjects() {
    this.isLoading = true;
    this.error = '';
    this.http.get<any[]>('/api/tm/projects').subscribe({
      next: (data) => {
        this.projects = data;
        this.isLoading = false;
        this.cdr.detectChanges();
      },
      error: (error) => {
        console.error('Error loading projects:', error);
        this.error = 'Failed to load projects. Please try again.';
        this.projects = [];
        this.isLoading = false;
        this.cdr.detectChanges();
      },
      complete: () => {
        // Ensure loading state is cleared even if something unexpected happens
        this.isLoading = false;
        this.cdr.detectChanges();
      }
    });

    // Add a safety timeout to prevent infinite loading
    setTimeout(() => {
      if (this.isLoading) {
        console.warn('Loading projects timed out after 10 seconds');
        this.isLoading = false;
        this.cdr.detectChanges();
      }
    }, 10000);
  }

  create() {
    console.log('Create project clicked');
    this.showCreateModal = true;
  }

  closeModal() {
    this.showCreateModal = false;
    this.resetForm();
  }

  resetForm() {
    this.newProject = {
      project_key: '',
      description: '',
      is_active: true
    };
    this.errors = {
      project_key: '',
      description: ''
    };
    this.apiError = '';
  }

  validateForm(): boolean {
    this.errors = {
      project_key: '',
      description: ''
    };

    let isValid = true;

    if (!this.newProject.project_key || this.newProject.project_key.trim() === '') {
      this.errors.project_key = 'Project key cannot be empty';
      isValid = false;
    }

    return isValid;
  }

  submitProject() {
    if (!this.validateForm()) {
      console.log('Validation failed');
      return;
    }

    this.apiError = '';
    console.log('Submitting project:', this.newProject);
    this.http.post('/api/tm/projects', this.newProject).subscribe({
      next: (response) => {
        console.log('Project created successfully:', response);
        this.closeModal();
        this.loadProjects();
      },
      error: (error) => {
        console.error('Error creating project:', error);
        console.log('Error object:', JSON.stringify(error, null, 2));

        // Extract error message from API response
        let errorMessage = 'Failed to create project. Please try again.';

        if (error.error) {
          // If error.error is a string, use it directly
          if (typeof error.error === 'string') {
            errorMessage = error.error;
          }
          // If error.error is an object, try to extract the message
          else if (typeof error.error === 'object') {
            errorMessage = error.error.message
              || error.error.detail
              || error.error.error
              || JSON.stringify(error.error);
          }
        } else if (error.message) {
          errorMessage = error.message;
        } else if (error.statusText) {
          errorMessage = `${error.status}: ${error.statusText}`;
        }
        this.apiError = errorMessage;
        this.cdr.detectChanges();
      }
    });
  }

  editProject(project: any) {
    console.log('Edit project:', project);
    this.editProjectData = {
      project_key: project.project_key,
      description: project.description,
      is_active: project.is_active
    };
    this.showEditModal = true;
  }

  closeEditModal() {
    this.showEditModal = false;
    this.resetEditForm();
  }

  resetEditForm() {
    this.editProjectData = {
      project_key: '',
      description: '',
      is_active: true
    };
    this.errors = {
      project_key: '',
      description: ''
    };
    this.apiError = '';
  }

  submitEditProject() {
    this.errors = {
      project_key: '',
      description: ''
    };
    this.apiError = '';

    console.log('Submitting edited project:', this.editProjectData);
    const url = `/api/tm/projects/${this.editProjectData.project_key}`;

    // Prepare the update payload (only description and is_active)
    const updatePayload = {
      description: this.editProjectData.description,
      is_active: this.editProjectData.is_active
    };

    this.http.put(url, updatePayload).subscribe({
      next: (response) => {
        console.log('Project updated successfully:', response);
        this.closeEditModal();
        this.loadProjects();
      },
      error: (error) => {
        console.error('Error updating project:', error);
        console.log('Error object:', JSON.stringify(error, null, 2));

        // Extract error message from API response
        let errorMessage = 'Failed to update project. Please try again.';

        if (error.error) {
          if (typeof error.error === 'string') {
            errorMessage = error.error;
          }
          else if (typeof error.error === 'object') {
            errorMessage = error.error.message
              || error.error.detail
              || error.error.error
              || JSON.stringify(error.error);
          }
        } else if (error.message) {
          errorMessage = error.message;
        } else if (error.statusText) {
          errorMessage = `${error.status}: ${error.statusText}`;
        }
        this.apiError = errorMessage;
        this.cdr.detectChanges();
      }
    });
  }

  deleteProject(project: any) {
    if (confirm(`Are you sure you want to delete project "${project.project_key}"?`)) {
      const url = `/api/tm/projects/${project.project_key}`;
      this.http.delete(url, { body: { "force": true } }).subscribe({
        next: (response) => {
          console.log('Project deleted successfully:', response);
          this.loadProjects();
        },
        error: (error) => {
          console.error('=== DELETE ERROR ===');
          console.error('Error object:', error);
          alert(`Failed to delete project.\nStatus: ${error.status}\nURL: ${error.url}\nMessage: ${error.message || error.statusText}`);
        }
      });
    }
  }

  navigateToTestCases(projectKey: string) {
    console.log('Navigating to test cases for project:', projectKey);
    this.router.navigate(['/test-cases', projectKey]);
  }

  onProjectClick(event: MouseEvent, projectKey: string) {
    if (event.button === 1) { // Middle mouse button
      event.preventDefault();
      const url = this.router.serializeUrl(
        this.router.createUrlTree(['/test-cases', projectKey])
      );
      window.open(url, '_blank');
    } else if (event.button === 0) { // Left mouse button
      this.navigateToTestCases(projectKey);
    }
  }
}
