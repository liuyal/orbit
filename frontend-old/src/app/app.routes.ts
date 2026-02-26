import { Routes } from '@angular/router';
import { Landing } from './landing/landing';
import { Project } from './tm/projects/projects';
import { TestCases } from './tm/test_cases/test_cases';
import { TestCaseFormComponent } from './tm/test_cases/test_case_form';
import { TestExecutionComponent } from './tm/test_execution/test_execution';
import { TestCycles } from './tm/test_cycles/test_cycles';
import { TestCycleFormComponent } from './tm/test_cycles/test_cycle_form';
import { Runners } from './runners/runners';

export const routes: Routes = [
  { path: '', component: Landing },
  { path: 'projects', component: Project },
  { path: 'runners', component: Runners },
  { path: 'test-cases/:projectKey', component: TestCases },
  { path: 'test-cases/:projectKey/create', component: TestCaseFormComponent },
  { path: 'test-cases/:projectKey/test-case/:testCaseKey', component: TestCaseFormComponent },
  { path: 'test-cases/:projectKey/executions/:executionKey', component: TestExecutionComponent },
  { path: 'test-cycles/:projectKey', component: TestCycles },
  { path: 'test-cycles/:projectKey/create', component: TestCycleFormComponent },
  { path: 'test-cycles/:projectKey/cycle/:testCycleKey', component: TestCycleFormComponent }
];