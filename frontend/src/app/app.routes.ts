import { Routes } from '@angular/router';
import { App } from './app';
import { Project } from './projects';
import { TestCases } from './test_cases';

export const routes: Routes = [
  { path: '', component: App },
  { path: 'projects', component: Project },
  { path: 'test-cases/:projectKey', component: TestCases }
];