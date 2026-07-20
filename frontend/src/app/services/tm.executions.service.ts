import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface TestExecutions {
    execution_key: string;
    project_key: string;
    test_case_key: string;
    test_cycle_key: string | null;
    result: string | null;
    custom_fields: Record<string, unknown> | null;
    comments: string | null;
    started_at: string | null;
    finished_at: string | null;
    links: any[];
}

@Injectable({
    providedIn: 'root'
})

export class TestExecutionsService {
    private apiUrl = environment.host + '/api/' + environment.apiVersion;

    constructor(private http: HttpClient) { }

    /**
    * Get a list of test executions by test case key
    * @returns An observable that emits an array of test executions for the given test case.
    */
    getTestExecutionsbyTestCase(projectKey: string, testCaseKey: string): Observable<TestExecutions[]> {
        const headers = new HttpHeaders({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        });

        return this.http.get<TestExecutions[]>(`${this.apiUrl}/tm/projects/${projectKey}/test-cases/${testCaseKey}/executions`, { headers });
    }
}
