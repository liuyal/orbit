import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface Projects {
    id: string;
    project_key: string;
    description: string;
    created_at: string;
    updated_at: string;
    is_active: boolean;
    test_case_count: number;
    test_cycles_count: number;
    labels: object[];
}

export interface ProjectsResponseModel {
    projects: Projects[];
}

@Injectable({
    providedIn: 'root'
})

export class ProjectsService {
    private apiUrl = environment.host + '/api/' + environment.apiVersion;

    constructor(private http: HttpClient) { }

    /**
    * Get a list of projects
    * @returns An observable that emits the projects response model containing an array of projects.
    */
    getProjects(): Observable<ProjectsResponseModel> {
        const headers = new HttpHeaders({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        });

        return this.http.get<ProjectsResponseModel>(`${this.apiUrl}/tm/projects`, { headers });
    }
}