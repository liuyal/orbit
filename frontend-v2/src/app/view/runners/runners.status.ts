import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { NavbarComponent } from '../../component/navbar/navbar';
import { RunnersStatusTableComponent } from '../../component/runners-status-table/runners.status.table.component';

@Component({
  selector: 'app-runners-status',
  standalone: true,
  imports: [
    CommonModule,
    NavbarComponent,
    RunnersStatusTableComponent
  ],
  styleUrls: ['./runners.status.css'],
  templateUrl: './runners.status.html'
})

export class RunnersStatus implements OnInit, OnDestroy {

  ngOnInit(): void {
    console.log('ngOnInit called');
  }

  ngOnDestroy(): void {
    console.log('ngOnDestroy called');
  }
}
