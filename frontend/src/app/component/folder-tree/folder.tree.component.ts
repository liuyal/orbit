import { Component, EventEmitter, Input, Output } from '@angular/core';
import { CommonModule } from '@angular/common';

export interface FolderNode {
  name: string;
  path: string;
  count: number;
  expanded: boolean;
  children: FolderNode[];
}

/**
 * Builds a nested folder tree from a flat list of '/' delimited folder paths.
 * Each node's count includes itself and all of its descendants.
 */
export function buildFolderTree(folderPaths: (string | undefined | null)[]): FolderNode[] {
  const root: FolderNode[] = [];

  const findOrCreate = (levelNodes: FolderNode[], name: string, path: string): FolderNode => {
    let node = levelNodes.find(n => n.name === name);
    if (!node) {
      node = { name, path, count: 0, expanded: false, children: [] };
      levelNodes.push(node);
    }
    return node;
  };

  for (const folderPath of folderPaths) {
    const segments = (folderPath || '')
      .split('/')
      .map(segment => segment.trim())
      .filter(segment => segment.length > 0);

    let levelNodes = root;
    let currentPath = '';
    for (const segment of segments) {
      currentPath += '/' + segment;
      const node = findOrCreate(levelNodes, segment, currentPath);
      node.count++;
      levelNodes = node.children;
    }
  }

  const sortNodes = (nodes: FolderNode[]): void => {
    nodes.sort((a, b) => a.name.localeCompare(b.name));
    nodes.forEach(node => sortNodes(node.children));
  };
  sortNodes(root);

  return root;
}

/**
 * Returns true if a folder path matches the selected folder, either exactly
 * or as a descendant of it.
 */
export function isFolderPathMatch(folderPath: string | undefined | null, selectedFolder: string | null): boolean {
  if (!selectedFolder) {
    return true;
  }
  const folder = folderPath || '';
  return folder === selectedFolder || folder.startsWith(selectedFolder + '/');
}

@Component({
  selector: 'app-folder-tree',
  standalone: true,
  imports: [CommonModule],
  styleUrls: ['./folder.tree.component.css'],
  templateUrl: './folder.tree.component.html'
})
export class FolderTreeComponent {
  @Input() title = 'Folders';
  @Input() allLabel = 'All Folders';
  @Input() totalCount = 0;
  @Input() folderTree: FolderNode[] = [];
  @Input() selectedFolder: string | null = null;
  @Output() folderSelected = new EventEmitter<string | null>();

  selectFolder(path: string | null): void {
    const next = this.selectedFolder === path ? null : path;
    this.folderSelected.emit(next);
  }

  toggleFolder(node: FolderNode): void {
    node.expanded = !node.expanded;
  }
}
