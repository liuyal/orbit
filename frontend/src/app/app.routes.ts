import { Routes } from '@angular/router';
import { Landing } from './view/landing/landing';
import { RunnersStatus } from './view/runners-status/runners.status';
import { TmProjects } from './view/tm-projects/tm.projects';
import { TmTests } from './view/tm-tests/tm.tests';
import { TmCase } from './view/tm-case/tm.case';
import { TmCycle } from './view/tm-cycle/tm.cycle';
import { TmExecution } from './view/tm-execution/tm.execution';

export const routes: Routes = [
  { path: '', component: Landing },
  { path: 'runner-status', component: RunnersStatus },
  { path: 'projects', component: TmProjects },
  { path: 'projects/:projectKey', component: TmTests },
  { path: 'projects/:projectKey/case/:caseKey', component: TmCase },
    { path: 'projects/:projectKey/case/:caseKey/execution/:executionKey', component: TmExecution },
  { path: 'projects/:projectKey/cycle/:cycleKey', component: TmCycle }
];
