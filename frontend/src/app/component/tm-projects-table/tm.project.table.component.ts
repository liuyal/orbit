import { Component, inject, OnInit, AfterViewInit, OnDestroy, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { LoaderComponent } from '../loader/loader.component';

@Component({
  selector: 'app-tm-projects-status-table',
  standalone: true,
  imports: [
    CommonModule,
    LoaderComponent
  ],
  styleUrls: ['./tm.project.table.component.css'],
  templateUrl: './tm.project.table.component.html'
})

export class TmProjectsTableComponent implements OnInit, AfterViewInit, OnDestroy {
  private spinnerTimeout?: any;
  cdr = inject(ChangeDetectorRef);
  isLoading = false;
  showSpinner = false;
  error = '';

  constructor() {

  }

  ngOnInit(): void {

  }

  ngAfterViewInit(): void {

  }

  ngOnDestroy(): void {
    if (this.spinnerTimeout) {
      clearTimeout(this.spinnerTimeout);
    }
  }
}

