import { Routes } from '@angular/router';
import { Landing } from './view/landing/landing';
import { RunnersStatus } from './view/runners-status/runners.status';
import { TmProjects } from './view/tm-projects/tm.projects';

export const routes: Routes = [
  { path: '', component: Landing },
  { path: 'runner-status', component: RunnersStatus },
  { path: 'projects', component: TmProjects }
];
