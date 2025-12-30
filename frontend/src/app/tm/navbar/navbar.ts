import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';

@Component({
  selector: 'app-navbar',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './navbar.html',
  styleUrls: ['./navbar.css']
})
export class NavbarComponent {
  @Input() showBackButton: boolean = false;
  @Input() backButtonText: string = 'Back';
  @Input() backButtonAction?: () => void;

  handleBackClick() {
    if (this.backButtonAction) {
      this.backButtonAction();
    }
  }
}
