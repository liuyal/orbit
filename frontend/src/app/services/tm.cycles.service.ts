import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { MatList } from '@angular/material/list';

export interface TestCycle {
    id: string;
    test_cycle_key: string;
    project_key: string;
    title: string;
    description: string;
    created_at: string;
    updated_at: string;
    status: string;
    executions: { [execKey: string]: string };
}

export interface TestCyclesResponseModel {
    test_cycles: TestCycle[];
}

export interface TestCycleExecution {
    execution_key: string;
    test_case_key: string;
    test_cycle_key: string;
    project_key: string;
    title: string;
    description: string;
    result: string;
    last_result: string;
    status: string;
    started_at: string;
    finished_at: string | null;
    created_at: string;
    updated_at: string;
    comments: string;
    labels: string[];
    folder: string | null;
    priority: string | null;
    custom_fields: object;
    links: any[];
    test_frequency: string[];
    test_script: string | null;
}

@Injectable({
    providedIn: 'root'
})

export class TestCyclesService {
    private apiUrl = environment.host + '/api/' + environment.apiVersion;

    constructor(private http: HttpClient) { }

    /**
    * Get a list of test cycles
    * @param projectKey The key of the project to retrieve test cycles for.
    * @returns An observable that emits the test cycles response model containing an array of test cycles.
    */
    getTestCyclesbyProjectKey(projectKey: string): Observable<TestCyclesResponseModel> {
        const headers = new HttpHeaders({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        });

        return this.http.get<TestCyclesResponseModel>(`${this.apiUrl}/tm/projects/${projectKey}/cycles`, { headers });
    }

    /**
    * Get a specific test cycle execution info
    * @param testCycleKey The key of the test cycle to retrieve.
    * @return An observable that emits the test cycle details.
    */
    getCycleExecutionInfo(testCycleKey: string): Observable<{ [key: string]: TestCycleExecution }> {
        const headers = new HttpHeaders({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        });

        return this.http.get<{ [key: string]: TestCycleExecution }>(`${this.apiUrl}/tm/cycles/${testCycleKey}/executions`, { headers });
    }

    /**
    * Get a specific test cycle info
    * @param testCycleKey The key of the test cycle to retrieve.
    * @return An observable that emits the test cycle details.
    */
    getCycleInfo(testCycleKey: string): Observable<TestCycle> {
        const headers = new HttpHeaders({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        });

        return this.http.get<TestCycle>(`${this.apiUrl}/tm/cycles/${testCycleKey}`, { headers });
    }
}