import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface RunnerStatus {
    id: string;
    name: string;
    os: string;
    status: string;
    busy: boolean;
    labels: object[];
    queried_ts: number;
    designation: string;
    job: string;
    job_url: string;
    job_trigger_user: string;
}

export interface RunnersResponseModel {
    runners: RunnerStatus[];
}

@Injectable({
    providedIn: 'root'
})

export class RunnersStatusService {
    private apiUrl = environment.host + '/api/' + environment.apiVersion;

    constructor(private http: HttpClient) { }

    /**
    * Get a list of runners
    * @returns An observable that emits the runners response model containing an array of connected runners.
    */
    getRunners(): Observable<RunnersResponseModel> {
        const headers = new HttpHeaders({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        });

        return this.http.get<RunnersResponseModel>(`${this.apiUrl}/runners/status`, { headers });
    }
}