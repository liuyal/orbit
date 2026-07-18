import {
  Component,
  inject,
  OnInit,
  OnDestroy,
  ChangeDetectorRef,
  ViewChild,
  ElementRef,
  HostListener,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { MatTableDataSource, MatTableModule } from '@angular/material/table';
import { LoaderComponent } from '../loader/loader.component';
import { EmptyStateComponent } from '../empty-state/empty.state.component';
import { ErrorStateComponent } from '../error-state/error.state.component';
import { TestCyclesService, TestCycle } from '../../services/tm.cycles.service';
import { computeProgressSummaries, ProgressSegment } from '../tm-cycle/tm.cycle.progress.utils';
import * as echarts from 'echarts';
import { STATUS_ORDER, STATUS_COLORS, buildChartOption } from './tm.results.graph.options';

type FilterOption = 'NIGHTLY' | 'WEEKLY' | 'RELEASE' | 'ALL';

@Component({
  selector: 'app-tm-results-graph',
  standalone: true,
  imports: [
    CommonModule,
    MatTableModule,
    LoaderComponent,
    EmptyStateComponent,
    ErrorStateComponent,
  ],
  styleUrls: ['./tm.results.graph.component.css'],
  templateUrl: './tm.results.graph.component.html',
})
export class TmResultsGraphComponent implements OnInit, OnDestroy {
  private chartEl: HTMLDivElement | null = null;

  @ViewChild('chartContainer') set chartContainer(el: ElementRef<HTMLDivElement>) {
    if (el && el.nativeElement !== this.chartEl) {
      this.chartEl = el.nativeElement;
      this.chartInstance?.dispose();
      this.chartInstance = echarts.init(el.nativeElement);
      this.chartInstance.on('click', (params: any) => {
        const cycleKey = params.name ?? params.value;
        if (cycleKey) {
          window.open(`/projects/${this.projectKey}/cycle/${cycleKey}`, '_blank');
        }
      });
      this.updateChart();
    }
  }

  cdr = inject(ChangeDetectorRef);
  router = inject(Router);
  route = inject(ActivatedRoute);

  cyclesDataSource: MatTableDataSource<TestCycle>;
  progressSummaries: Record<string, ProgressSegment[]> = {};
  projectKey = '';
  isLoading = false;
  error = '';

  readonly filterOptions: FilterOption[] = ['NIGHTLY', 'WEEKLY', 'RELEASE', 'ALL'];
  activeFilter: FilterOption = 'NIGHTLY';
  dropdownOpen = false;

  private chartInstance: echarts.ECharts | null = null;
  private resizeListener = (): void => {
    this.chartInstance?.resize();
  };

  constructor(private testCyclesService: TestCyclesService) {
    this.cyclesDataSource = new MatTableDataSource<TestCycle>([]);
  }

  get filteredCycles(): TestCycle[] {
    const cycles = this.cyclesDataSource.data;
    if (this.activeFilter === 'ALL') return cycles;
    const keyword = this.activeFilter.toLowerCase();
    return cycles.filter((c) => c.title?.toLowerCase().includes(keyword));
  }

  get sortedFilteredCycles(): TestCycle[] {
    return [...this.filteredCycles].sort((a, b) => {
      const na = parseInt(a.test_cycle_key.replace(/\D+/g, ''), 10) || 0;
      const nb = parseInt(b.test_cycle_key.replace(/\D+/g, ''), 10) || 0;
      return na - nb;
    });
  }

  setFilter(filter: FilterOption): void {
    this.activeFilter = filter;
    this.dropdownOpen = false;
    this.updateChart();
  }

  toggleDropdown(event: MouseEvent): void {
    event.stopPropagation();
    this.dropdownOpen = !this.dropdownOpen;
  }

  @HostListener('document:click')
  closeDropdown(): void {
    this.dropdownOpen = false;
  }

  ngOnInit(): void {
    window.addEventListener('resize', this.resizeListener);
    this.route.params.subscribe((params) => {
      this.projectKey = params['projectKey'];
      console.log('Test cycle tab for project:', this.projectKey);
      this.loadTestCycles();
    });
  }

  ngOnDestroy(): void {
    window.removeEventListener('resize', this.resizeListener);
    this.chartInstance?.dispose();
    this.chartInstance = null;
  }

  private updateChart(): void {
    if (!this.chartInstance) return;

    const cycles = this.sortedFilteredCycles;
    const categories = cycles.map((c) => c.test_cycle_key);
    const xLabels = cycles.map((c) => {
      if (!c.created_at) return '';
      const d = new Date(c.created_at);
      return `${d.getUTCFullYear()}-${String(d.getUTCMonth() + 1).padStart(2, '0')}`;
    });
    // console.log('[chart] cycle keys + created_at dates:', cycles.map((c) => ({ key: c.test_cycle_key, created_at: c.created_at, label: xLabels[cycles.indexOf(c)] })));
    const series: echarts.SeriesOption[] = STATUS_ORDER.map((status) => ({
      name: status.replace('_', ' '),
      type: 'line',
      stack: 'total',
      areaStyle: { opacity: 0.3 },
      emphasis: { focus: 'series' },
      smooth: false,
      symbol: 'circle',
      symbolSize: 7,
      cursor: 'pointer',
      itemStyle: { color: STATUS_COLORS[status] ?? '#9e9e9e' },
      data: cycles.map((c) => {
        const segments = this.progressSummaries[c.test_cycle_key] ?? [];
        return segments.find((s) => s.result === status)?.count ?? 0;
      }),
    }));

    this.chartInstance.setOption(buildChartOption(categories, series, this.projectKey, xLabels), { notMerge: true });
  }

  loadTestCycles(): void {
    this.isLoading = true;
    this.error = '';

    this.testCyclesService.getTestCyclesbyProjectKey(this.projectKey).subscribe({
      next: (response) => {
        this.cyclesDataSource.data = Array.isArray(response) ? response : [];
        this.progressSummaries = computeProgressSummaries(this.cyclesDataSource.data);
        this.isLoading = false;
        this.cdr.markForCheck();
        this.updateChart();
      },
      error: (error) => {
        console.error('Error fetching test cycles data:', error);
        this.error = `Error fetching test cycles data: ${error.message || error}`;
        this.isLoading = false;
        this.cdr.markForCheck();
      },
    });
  }

}

