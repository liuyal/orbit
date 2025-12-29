import { Component, inject, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { Observable } from 'rxjs';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, FormsModule],
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
    .navbar-menu {
      display: flex;
      align-items: center;
      gap: 25px;
    }
    .nav-link {
      color: #e0e0e0;
      text-decoration: none;
      font-size: 15px;
      font-weight: 500;
      padding: 8px 16px;
      border-radius: 6px;
      transition: all 0.2s;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .nav-link:hover {
      background-color: #2a2a2a;
      color: #ffffff;
    }
    .nav-link.active {
      background-color: #0057adff;
      color: #ffffff;
    }
    .prj-refresh-btn {
      padding: 10px;
      width: 40px;
      height: 40px;
      border: 1px solid #333;
      border-radius: 5px;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .prj-refresh-btn:hover {
      background-color: #0057adff;
    }
    .prj-create-btn {
      padding: 10px;
      width: 40px;
      height: 40px;
      border: 1px solid #333;
      border-radius: 5px;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .prj-create-btn:hover {
      background-color: #0057adff;
    }
    .modal-overlay {
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background-color: rgba(0, 0, 0, 0.75);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 1000;
    }
    .modal-content {
      background-color: #1e1e1e;
      padding: 40px 50px;
      border-radius: 12px;
      min-width: 600px;
      max-width: 800px;
      width: 90%;
      box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
      color: #e0e0e0;
      border: 1px solid #333;
    }
    .modal-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 30px;
      border-bottom: 2px solid #333;
      padding-bottom: 15px;
    }
    .modal-header h2 {
      margin: 0;
      color: #ffffff;
      font-size: 24px;
    }
    .close-btn {
      background: none;
      border: none;
      font-size: 32px;
      cursor: pointer;
      color: #999;
      transition: color 0.2s;
    }
    .close-btn:hover {
      color: #fff;
    }
    .form-group {
      margin-bottom: 25px;
    }
    .form-group label {
      display: block;
      margin-bottom: 8px;
      font-weight: bold;
      color: #e0e0e0;
      font-size: 15px;
    }
    .form-group input,
    .form-group textarea {
      width: 100%;
      padding: 12px 15px;
      border: 1px solid #444;
      border-radius: 6px;
      font-size: 15px;
      box-sizing: border-box;
      background-color: #2a2a2a;
      color: #e0e0e0;
      transition: border-color 0.2s;
    }
    .form-group textarea {
      resize: vertical;
      min-height: 120px;
    }
    .form-group input:focus,
    .form-group textarea:focus {
      outline: none;
      border-color: #0057adff;
      background-color: #2f2f2f;
    }
    .form-group input::placeholder,
    .form-group textarea::placeholder {
      color: #777;
    }
    .form-group input.error,
    .form-group textarea.error {
      border-color: #dc3545;
    }
    .form-group input:disabled {
      background-color: #1a1a1a;
      color: #777;
      cursor: not-allowed;
      border-color: #333;
    }
    .error-message {
      color: #ff6b6b;
      font-size: 13px;
      margin-top: 5px;
      display: block;
    }
    .alert-error {
      background-color: #dc354520;
      border: 1px solid #dc3545;
      color: #ff6b6b;
      padding: 12px 15px;
      border-radius: 6px;
      margin-bottom: 20px;
      font-size: 14px;
    }
    .form-actions {
      display: flex;
      gap: 15px;
      justify-content: flex-end;
      margin-top: 35px;
      padding-top: 20px;
      border-top: 1px solid #333;
    }
    .btn {
      padding: 12px 30px;
      border: none;
      border-radius: 6px;
      cursor: pointer;
      font-size: 15px;
      font-weight: 500;
      transition: all 0.2s;
    }
    .btn-primary {
      background-color: #0057adff;
      color: white;
    }
    .btn-primary:hover {
      background-color: #004090;
      transform: translateY(-1px);
      box-shadow: 0 4px 12px rgba(0, 87, 173, 0.4);
    }
    .btn-secondary {
      background-color: #444;
      color: white;
      border: 1px solid #555;
    }
    .btn-secondary:hover {
      background-color: #555;
      border-color: #666;
    }
    .toggle-wrapper {
      display: flex;
      align-items: center;
      gap: 15px;
    }
    .toggle-switch {
      position: relative;
      display: inline-block;
      width: 60px;
      height: 30px;
    }
    .toggle-switch input {
      opacity: 0;
      width: 0;
      height: 0;
    }
    .toggle-slider {
      position: absolute;
      cursor: pointer;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background-color: #444;
      transition: 0.3s;
      border-radius: 30px;
      border: 1px solid #555;
    }
    .toggle-slider:before {
      position: absolute;
      content: "";
      height: 22px;
      width: 22px;
      left: 4px;
      bottom: 3px;
      background-color: #999;
      transition: 0.3s;
      border-radius: 50%;
    }
    .toggle-switch input:checked + .toggle-slider {
      background-color: #0057adff;
    }
    .toggle-switch input:checked + .toggle-slider:before {
      transform: translateX(30px);
      background-color: white;
    }
    .toggle-switch input:focus + .toggle-slider {
      box-shadow: 0 0 1px #0057adff;
    }
    .toggle-label {
      font-size: 15px;
      color: #e0e0e0;
    }
    .prj-table {
      margin-top: 25px;
      width: 100%;
      border-collapse: separate;
      border-spacing: 0;
      border-radius: 8px;
      overflow: hidden;
      box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
      background-color: #1e1e1e;
    }
    .prj-table th {
      background-color: #0172ad;
      color: white;
      padding: 10px 20px;
      text-align: left;
      font-weight: 600;
      font-size: 15px;
      letter-spacing: 0.5px;
      text-transform: uppercase;
      border-bottom: 2px solid #004090;
    }
    .prj-table th:first-child {
      border-top-left-radius: 5px;
    }
    .prj-table th:last-child {
      border-top-right-radius: 5px;
      text-align: right;
      width: 200px;
      white-space: nowrap;
    }
    .prj-table td {
      padding: 10px 20px;
      text-align: left;
      border-bottom: 1px solid #333;
      background-color: #252525;
      color: #e0e0e0;
      font-size: 15px;
    }
    .prj-table td:last-child {
      text-align: right;
      width: 200px;
      white-space: nowrap;
    }
    .prj-table tbody tr {
      transition: background-color 0.2s ease;
    }
    .prj-table tbody tr:hover {
      background-color: #2a2a2a;
    }
    .prj-table tbody tr:hover td {
      background-color: #2a2a2a;
    }
    .prj-table tbody tr:last-child td:first-child {
      border-bottom-left-radius: 8px;
    }
    .prj-table tbody tr:last-child td:last-child {
      border-bottom-right-radius: 8px;
    }
    .prj-table tbody tr:last-child td {
      border-bottom: none;
    }
    .status-badge {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 6px 12px;
      border-radius: 20px;
      font-size: 13px;
      font-weight: 500;
    }
    .status-badge.active {
      background-color: #28a74520;
      color: #4ade80;
      border: 1px solid #4ade8050;
    }
    .status-badge.inactive {
      background-color: #dc354520;
      color: #f87171;
      border: 1px solid #f8717150;
    }
    .status-badge i {
      font-size: 12px;
    }
    .action-buttons {
      display: flex;
      gap: 8px;
      align-items: center;
      justify-content: flex-end;
    }
    .action-btn {
      padding: 8px 12px;
      border: none;
      border-radius: 5px;
      cursor: pointer;
      font-size: 13px;
      font-weight: 500;
      transition: all 0.2s;
      display: flex;
      align-items: center;
      gap: 5px;
    }
    .action-btn.edit {
      background-color: #0057adff;
      color: white;
    }
    .action-btn.edit:hover {
      background-color: #004090;
      transform: translateY(-1px);
    }
    .action-btn.delete {
      background-color: #dc3545;
      color: white;
    }
    .action-btn.delete:hover {
      background-color: #c82333;
      transform: translateY(-1px);
    }
  `],
  template: `
    <nav class="navbar">
      <div class="navbar-brand">
        <i class="fa-solid fa-rocket"></i>
        <span>ORBIT</span>
      </div>
      <!-- <div class="navbar-menu">
        <a href="/projects" class="nav-link active">
          <i class="fa-solid fa-folder-open"></i>
          Projects
        </a>
        <a href="#" class="nav-link">
          <i class="fa-solid fa-flask"></i>
          Test Cases
        </a>
        <a href="#" class="nav-link">
          <i class="fa-solid fa-rotate"></i>
          Test Cycles
        </a>
        <a href="#" class="nav-link">
          <i class="fa-solid fa-play"></i>
          Executions
        </a>
      </div> -->
    </nav>

    <div style="margin: 50px;">
      <div style="display: flex; gap: 10px; justify-content: flex-end;">
        <button class="prj-refresh-btn" (click)="refresh()">
          <i class="fa-solid fa-arrows-rotate"></i>
        </button>
        <button class="prj-create-btn" (click)="create()">
          <i class="fa-solid fa-plus"></i>
        </button>
      </div>

      @if (data$ | async; as data) {
        <table class="prj-table">
          <thead>
            <tr>
              <th>PROJECT KEY</th>
              <th>DESCRIPTION</th>
              <th>STATUS</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            @for (item of data; track item.project_key) {
              <tr>
                <td><strong>{{ item.project_key }}</strong></td>
                <td>{{ item.description }}</td>
                <td>
                  @if (item.is_active == true ) {
                    <span class="status-badge active">
                      <i class="fa-solid fa-circle-check"></i>
                      Active
                    </span>
                  } @else {
                    <span class="status-badge inactive">
                      <i class="fa-solid fa-circle-xmark"></i>
                      Inactive
                    </span>
                  }
                </td>
                <td>
                  <div class="action-buttons">
                    <button class="action-btn edit" (click)="editProject(item)">
                      <i class="fa-solid fa-pen-to-square"></i>
                      Edit
                    </button>
                    <button class="action-btn delete" (click)="deleteProject(item)">
                      <i class="fa-solid fa-trash"></i>
                      Delete
                    </button>
                  </div>
                </td>
              </tr>
            }
          </tbody>
        </table>
      } @else {}
    </div>

    <!-- Create Project Modal -->
    @if (showCreateModal) {
      <div class="modal-overlay" (click)="closeModal()">
        <div class="modal-content" (click)="$event.stopPropagation()">
          <div class="modal-header">
            <h2>Create New Project</h2>
            <button class="close-btn" (click)="closeModal()">&times;</button>
          </div>
          <form (ngSubmit)="submitProject()">
            @if (apiError) {
              <div class="alert-error">
                {{ apiError }}
              </div>
            }
            <div class="form-group">
              <label for="project_key">Project Key *</label>
              <input
                type="text"
                id="project_key"
                [(ngModel)]="newProject.project_key"
                name="project_key"
                placeholder="Enter project key"
                required
                [class.error]="errors.project_key"
              />
              @if (errors.project_key) {
                <span class="error-message">{{ errors.project_key }}</span>
              }
            </div>
            <div class="form-group">
              <label for="description">Description</label>
              <textarea
                id="description"
                [(ngModel)]="newProject.description"
                name="description"
                placeholder="Enter project description"
                required
                [class.error]="errors.description"
              ></textarea>
              @if (errors.description) {
                <span class="error-message">{{ errors.description }}</span>
              }
            </div>
            <div class="form-group">
              <label>Status</label>
              <div class="toggle-wrapper">
                <label class="toggle-switch">
                  <input
                    type="checkbox"
                    id="is_active"
                    [(ngModel)]="newProject.is_active"
                    name="is_active"
                  />
                  <span class="toggle-slider"></span>
                </label>
                <span class="toggle-label">{{ newProject.is_active ? 'Active' : 'Inactive' }}</span>
              </div>
            </div>
            <div class="form-actions">
              <button type="button" class="btn btn-secondary" (click)="closeModal()">
                Cancel
              </button>
              <button type="submit" class="btn btn-primary">
                Create
              </button>
            </div>
          </form>
        </div>
      </div>
    }

    <!-- Edit Project Modal -->
    @if (showEditModal) {
      <div class="modal-overlay" (click)="closeEditModal()">
        <div class="modal-content" (click)="$event.stopPropagation()">
          <div class="modal-header">
            <h2>Edit Project</h2>
            <button class="close-btn" (click)="closeEditModal()">&times;</button>
          </div>
          <form (ngSubmit)="submitEditProject()">
            @if (apiError) {
              <div class="alert-error">
                {{ apiError }}
              </div>
            }
            <div class="form-group">
              <label for="edit_project_key">Project Key *</label>
              <input
                type="text"
                id="edit_project_key"
                [(ngModel)]="editProjectData.project_key"
                name="edit_project_key"
                disabled
              />
            </div>
            <div class="form-group">
              <label for="edit_description">Description</label>
              <textarea
                id="edit_description"
                [(ngModel)]="editProjectData.description"
                name="edit_description"
                placeholder="Enter project description"
                required
                [class.error]="errors.description"
              ></textarea>
              @if (errors.description) {
                <span class="error-message">{{ errors.description }}</span>
              }
            </div>
            <div class="form-group">
              <label>Status</label>
              <div class="toggle-wrapper">
                <label class="toggle-switch">
                  <input
                    type="checkbox"
                    id="edit_is_active"
                    [(ngModel)]="editProjectData.is_active"
                    name="edit_is_active"
                  />
                  <span class="toggle-slider"></span>
                </label>
                <span class="toggle-label">{{ editProjectData.is_active ? 'Active' : 'Inactive' }}</span>
              </div>
            </div>
            <div class="form-actions">
              <button type="button" class="btn btn-secondary" (click)="closeEditModal()">
                Cancel
              </button>
              <button type="submit" class="btn btn-primary">
                Update
              </button>
            </div>
          </form>
        </div>
      </div>
    }
  `
})

export class Project {
  http = inject(HttpClient);
  cdr = inject(ChangeDetectorRef);
  data$: Observable<any[]> = this.http.get<any[]>('/api/projects');
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

  refresh() {
    console.log('Refresh project clicked');
    this.data$ = this.http.get<any[]>('/api/projects');
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
    this.http.post('/api/projects', this.newProject).subscribe({
      next: (response) => {
        console.log('Project created successfully:', response);
        this.closeModal();
        window.location.reload();
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
    const url = `/api/projects/${this.editProjectData.project_key}`;
    
    // Prepare the update payload (only description and is_active)
    const updatePayload = {
      description: this.editProjectData.description,
      is_active: this.editProjectData.is_active
    };

    this.http.put(url, updatePayload).subscribe({
      next: (response) => {
        console.log('Project updated successfully:', response);
        this.closeEditModal();
        window.location.reload();
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
      const url = `/api/projects/${project.project_key}`;
      console.log('=== DELETE REQUEST INFO ===');
      console.log('Project object:', JSON.stringify(project, null, 2));
      console.log('Project key:', project.project_key);
      console.log('Delete URL:', url);
      
      this.http.delete(url, { body: { "force": true } }).subscribe({
        next: (response) => {
          console.log('Project deleted successfully:', response);
          window.location.reload();
        },
        error: (error) => {
          console.error('=== DELETE ERROR ===');
          console.error('Full error object:', error);
          console.error('Status:', error.status);
          console.error('Status text:', error.statusText);
          console.error('URL that failed:', error.url);
          console.error('Error message:', error.message);
          console.error('Error body:', error.error);
          alert(`Failed to delete project.\nStatus: ${error.status}\nURL: ${error.url}\nMessage: ${error.message || error.statusText}`);
        }
      });
    }
  }
}
