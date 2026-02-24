import { Routes } from '@angular/router';
import { Landing } from './view/landing/landing';
import { RunnersStatus } from './view/runners/runners.status';

export const routes: Routes = [
  { path: '', component: Landing },
  { path: 'runner-status', component: RunnersStatus },

];
