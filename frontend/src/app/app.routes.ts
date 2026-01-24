import { Routes } from '@angular/router';
import { Landing } from './landing/landing';
import { Project } from './tm/projects/projects';
import { TestCases } from './tm/test_cases/test_cases';
import { TestCaseFormComponent } from './tm/test_cases/test_case_form';
import { TestCycles } from './tm/test_cycles/test_cycles';
import { TestCycleFormComponent } from './tm/test_cycles/test_cycle_form';

export const routes: Routes = [
  { path: '', component: Landing },
  { path: 'projects', component: Project },
  { path: 'test-cases/:projectKey', component: TestCases },
  { path: 'test-cases/:projectKey/create', component: TestCaseFormComponent },
  { path: 'test-cases/:projectKey/edit/:testCaseKey', component: TestCaseFormComponent },
  { path: 'test-cycles/:projectKey', component: TestCycles },
  { path: 'test-cycles/:projectKey/create', component: TestCycleFormComponent },
  { path: 'test-cycles/:projectKey/edit/:testCycleKey', component: TestCycleFormComponent }
];