import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface TestCycles {
    id: string;
    test_cycle_key: string;
    project_key: string;
    title: string;
    description: string;
    created_at: string;
    updated_at: string;
    status: string;
    executions: object;
}

export interface TestCyclesResponseModel {
    test_cycles: TestCycles[];
}

@Injectable({
    providedIn: 'root'
})

export class TestCyclesService {
    private apiUrl = environment.host + '/api/' + environment.apiVersion;

    constructor(private http: HttpClient) { }

    /**
    * Get a list of test cycles
    * @returns An observable that emits the test cycles response model containing an array of test cycles.
    */
    getTestCyclesbyProjectKey(projectKey: string): Observable<TestCyclesResponseModel> {
        const headers = new HttpHeaders({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        });

        return this.http.get<TestCyclesResponseModel>(`${this.apiUrl}/tm/projects/${projectKey}/test-cycles`, { headers });
    }
}