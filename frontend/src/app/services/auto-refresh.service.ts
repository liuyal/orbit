import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';

export interface AutoRefreshSettings {
  runnersStatus: boolean;
}

@Injectable({
  providedIn: 'root'
})

export class AutoRefreshService {
  private static readonly STORAGE_KEY = 'auto-refresh-settings';
  private static readonly VERSION_KEY = 'auto-refresh-settings-version';
  private static readonly CURRENT_VERSION = '1.0.0';
  private static readonly DEFAULT_SETTINGS: AutoRefreshSettings = {
    runnersStatus: false
  };

  private settingsSubject = new BehaviorSubject<AutoRefreshSettings>(this.loadSettings());

  constructor() {
    // Initialize with saved settings
    this.settingsSubject.next(this.loadSettings());
  }

  /**
   * Get the current auto-refresh settings as an observable
   */
  getSettings(): Observable<AutoRefreshSettings> {
    return this.settingsSubject.asObservable();
  }

  /**
   * Get the current auto-refresh settings synchronously
   */
  getCurrentSettings(): AutoRefreshSettings {
    return this.settingsSubject.value;
  }

  /**
   * Get auto-refresh state for a specific component
   */
  getAutoRefreshState(component: keyof AutoRefreshSettings): boolean {
    return this.settingsSubject.value[component];
  }

  /**
   * Set auto-refresh state for a specific component
   */
  setAutoRefreshState(component: keyof AutoRefreshSettings, enabled: boolean): void {
    const currentSettings = this.settingsSubject.value;
    const newSettings = {
      ...currentSettings,
      [component]: enabled
    };

    this.settingsSubject.next(newSettings);
    this.saveSettings(newSettings);
  }

  /**
   * Toggle auto-refresh state for a specific component
   */
  toggleAutoRefresh(component: keyof AutoRefreshSettings): boolean {
    const currentState = this.getAutoRefreshState(component);
    const newState = !currentState;
    this.setAutoRefreshState(component, newState);
    return newState;
  }

  /**
   * Reset all auto-refresh settings to default
   */
  resetToDefaults(): void {
    this.settingsSubject.next({ ...AutoRefreshService.DEFAULT_SETTINGS });
    this.saveSettings(AutoRefreshService.DEFAULT_SETTINGS);
  }

  /**
   * Check if the stored data structure matches the current version
   */
  private isDataStructureValid(parsed: any): boolean {
    // Check if all required properties exist and are boolean values
    const requiredProperties: (keyof AutoRefreshSettings)[] = ['runnersStatus'];

    for (const prop of requiredProperties) {
      if (!(prop in parsed) || typeof parsed[prop] !== 'boolean') {
        return false;
      }
    }

    // Check for any unexpected properties (indicating a newer version was saved)
    const expectedKeys = new Set(requiredProperties);
    const actualKeys = new Set(Object.keys(parsed));

    // If there are any keys we don't expect, the data structure has changed
    for (const key of actualKeys) {
      if (!expectedKeys.has(key as keyof AutoRefreshSettings)) {
        return false;
      }
    }

    return true;
  }

  /**
   * Load settings from localStorage
   */
  private loadSettings(): AutoRefreshSettings {
    try {
      const stored = localStorage.getItem(AutoRefreshService.STORAGE_KEY);
      const storedVersion = localStorage.getItem(AutoRefreshService.VERSION_KEY);

      if (stored && storedVersion === AutoRefreshService.CURRENT_VERSION) {
        const parsed = JSON.parse(stored);

        // Validate the data structure
        if (this.isDataStructureValid(parsed)) {
          return {
            runnersStatus: parsed.runnersStatus
          };
        } else {
          console.warn('Auto-refresh settings data structure is invalid, resetting to defaults');
          this.clearStoredSettings();
        }
      } else if (stored) {
        // Version mismatch or no version stored
        console.warn('Auto-refresh settings version mismatch or missing version, resetting to defaults');
        this.clearStoredSettings();
      }
    } catch (error) {
      console.warn('Failed to load auto-refresh settings from localStorage:', error);
      this.clearStoredSettings();
    }

    return { ...AutoRefreshService.DEFAULT_SETTINGS };
  }

  /**
   * Save settings to localStorage
   */
  private saveSettings(settings: AutoRefreshSettings): void {
    try {
      localStorage.setItem(AutoRefreshService.STORAGE_KEY, JSON.stringify(settings));
      localStorage.setItem(AutoRefreshService.VERSION_KEY, AutoRefreshService.CURRENT_VERSION);
    } catch (error) {
      console.warn('Failed to save auto-refresh settings to localStorage:', error);
    }
  }

  /**
   * Clear stored settings (used when resetting due to version mismatch)
   */
  private clearStoredSettings(): void {
    try {
      localStorage.removeItem(AutoRefreshService.STORAGE_KEY);
      localStorage.removeItem(AutoRefreshService.VERSION_KEY);
    } catch (error) {
      console.warn('Failed to clear auto-refresh settings from localStorage:', error);
    }
  }
}
