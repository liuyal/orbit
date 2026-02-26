import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-landing',
  standalone: true,
  imports: [RouterLink],
  templateUrl: './landing.html',
  styleUrls: ['./landing.css']
})

export class Landing {
  getFileServerUrl(): string {
    if (typeof window !== 'undefined') {
      return `${window.location.protocol}//${window.location.hostname}:8443/files/`;
    }
    return '//:8443/files/';
  }
}
