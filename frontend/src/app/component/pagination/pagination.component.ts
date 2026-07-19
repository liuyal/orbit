import { Component, EventEmitter, Input, Output } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-pagination',
  standalone: true,
  imports: [CommonModule],
  styleUrls: ['./pagination.component.css'],
  templateUrl: './pagination.component.html'
})
export class PaginationComponent {
  @Input() pageIndex = 0;
  @Input() pageSize = 20;
  @Input() totalItems = 0;
  @Input() pageSizeOptions: number[] = [20, 50, 100];

  @Output() pageIndexChange = new EventEmitter<number>();
  @Output() pageSizeChange = new EventEmitter<number>();

  get rangeStart(): number {
    return this.totalItems === 0 ? 0 : this.pageIndex * this.pageSize + 1;
  }

  get rangeEnd(): number {
    return Math.min(this.totalItems, (this.pageIndex + 1) * this.pageSize);
  }

  get hasPreviousPage(): boolean {
    return this.pageIndex > 0;
  }

  get hasNextPage(): boolean {
    return this.rangeEnd < this.totalItems;
  }

  get totalPages(): number {
    return Math.max(1, Math.ceil(this.totalItems / this.pageSize));
  }

  get currentPage(): number {
    return this.pageIndex + 1;
  }

  get visiblePages(): (number | 'ellipsis')[] {
    const total = this.totalPages;
    const current = this.currentPage;
    if (total <= 1) return [1];

    const delta = 2;
    const rangeStart = Math.max(2, current - delta);
    const rangeEnd = Math.min(total - 1, current + delta);

    const pages: (number | 'ellipsis')[] = [1];
    if (rangeStart > 2) pages.push('ellipsis');
    for (let i = rangeStart; i <= rangeEnd; i++) pages.push(i);
    if (rangeEnd < total - 1) pages.push('ellipsis');
    pages.push(total);
    return pages;
  }

  goToPreviousPage(): void {
    if (this.hasPreviousPage) this.pageIndexChange.emit(this.pageIndex - 1);
  }

  goToNextPage(): void {
    if (this.hasNextPage) this.pageIndexChange.emit(this.pageIndex + 1);
  }

  goToPage(page: number): void {
    if (!Number.isFinite(page)) return;
    const clamped = Math.min(Math.max(Math.trunc(page), 1), this.totalPages);
    this.pageIndexChange.emit(clamped - 1);
  }

  onPageSizeChange(size: number): void {
    this.pageSizeChange.emit(size);
  }
}
