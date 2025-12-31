import { Routes } from '@angular/router';
import { Landing } from './landing';
import { Project } from './tm/projects';
import { TestCases } from './tm/test_cases';
import { TestCaseCreate } from './tm/test_case_create';

export const routes: Routes = [
  { path: '', component: Landing },
  { path: 'projects', component: Project },
  { path: 'test-cases/:projectKey', component: TestCases },
  { path: 'test-cases/:projectKey/create', component: TestCaseCreate }
];