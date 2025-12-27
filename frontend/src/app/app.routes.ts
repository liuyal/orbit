import { Routes } from '@angular/router';
import { App } from './app';
import { Project } from './projects';

export const routes: Routes = [
  { path: '', component: App },
  { path: 'projects', component: Project }
];