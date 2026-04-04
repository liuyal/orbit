import { Routes } from '@angular/router';
import { Landing } from './view/landing/landing';
import { RunnersStatus } from './view/runners-status/runners.status';
import { TmProjects } from './view/tm-projects/tm.projects';
import { TmTests } from './view/tm-tests/tm.tests';

export const routes: Routes = [
  { path: '', component: Landing },
  { path: 'runner-status', component: RunnersStatus },
  { path: 'projects', component: TmProjects },
  { path: 'projects/:projectKey', component: TmTests }
];
