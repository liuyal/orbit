import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface TestCases {
    id: string;
    test_case_key: string;
    project_key: string;
    title: string;
    description: string;
    folder: string;
    created_at: string;
    updated_at: string;
    priority: string;
    test_script: string;
    last_result: string;
    last_execution_key: string;
    failing_steps: string;
    test_frequency: object[];
    labels: object[];
    links: object[];
}

export interface TestCasesResponseModel {
    test_cases: TestCases[];
}

@Injectable({
    providedIn: 'root'
})

export class TestCasesService {
    private apiUrl = environment.host + '/api/' + environment.apiVersion;

    constructor(private http: HttpClient) { }

    /**
    * Get a list of test cases
    * @returns An observable that emits the test cases response model containing an array of test cases.
    */
    getTestCasesbyProjectKey(projectKey: string): Observable<TestCasesResponseModel> {
        const headers = new HttpHeaders({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        });

        return this.http.get<TestCasesResponseModel>(`${this.apiUrl}/tm/projects/${projectKey}/test-cases`, { headers });
    }
}