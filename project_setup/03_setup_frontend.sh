#!/bin/bash
set -e

# This script creates a stub for the Angular frontend. It does not rely on
# the Angular CLI; instead it provides a minimal structure that can be
# extended by installing Angular later. It then invokes the quests setup.

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "Setting up frontend skeleton..."

# index.html at the root of the src folder
cat <<'HTML' > "$ROOT_DIR/frontend/src/index.html"
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Agent Battle Arena</title>
  </head>
  <body>
    <app-root></app-root>
    <!--
      In a real Angular project, this file is generated and managed by the CLI.
      For the MVP skeleton, this minimal file mounts the root component.
    -->
    <script type="module" src="./main.ts"></script>
  </body>
</html>
HTML

# Main entry file to bootstrap the application with standalone components and HTTP support
cat <<'MAIN_TS' > "$ROOT_DIR/frontend/src/main.ts"
// Main entry point for the Angular application.
// This file bootstraps the standalone AppComponent and configures the HTTP client.
import { bootstrapApplication } from '@angular/platform-browser';
import { provideHttpClient } from '@angular/common/http';
import { AppComponent } from './app/app.component';

bootstrapApplication(AppComponent, {
  providers: [provideHttpClient()],
}).catch((err) => console.error(err));
MAIN_TS

# AppComponent TypeScript file using standalone component and importing QuestListComponent
cat <<'APP_COMPONENT_TS' > "$ROOT_DIR/frontend/src/app/app.component.ts"
import { Component } from '@angular/core';
import { QuestListComponent } from './components/quest-list/quest-list.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [QuestListComponent],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css'],
})
export class AppComponent {
  title = 'Agent Battle Arena';
}
APP_COMPONENT_TS

# AppComponent HTML template
cat <<'APP_COMPONENT_HTML' > "$ROOT_DIR/frontend/src/app/app.component.html"
<h1>{{ title }}</h1>
<p>
  Bem-vindo à Agent Battle Arena! Esta é a interface stub do projeto. Aqui você
  poderá acompanhar desafios, enviar soluções e ver os rankings. Para obter a
  versão completa, substitua este stub por um projeto Angular real.
</p>
APP_COMPONENT_HTML

# AppComponent CSS file
cat <<'APP_COMPONENT_CSS' > "$ROOT_DIR/frontend/src/app/app.component.css"
/* Styles for the AppComponent. Customize as needed. */
h1 {
  color: #333;
  margin-top: 2rem;
  text-align: center;
}

p {
  max-width: 600px;
  margin: 1rem auto;
  line-height: 1.5;
  text-align: center;
}
APP_COMPONENT_CSS



# Additional Angular structure: models, services and components
mkdir -p "$ROOT_DIR/frontend/src/app/models"
mkdir -p "$ROOT_DIR/frontend/src/app/services"
mkdir -p "$ROOT_DIR/frontend/src/app/components/quest-list"

# TypeScript interface for quests
cat <<'QUEST_MODEL_TS' > "$ROOT_DIR/frontend/src/app/models/quest.ts"
export interface Quest {
  id: number;
  name: string;
  description: string;
}
QUEST_MODEL_TS

# Angular service to fetch quests from the backend
cat <<'QUEST_SERVICE_TS' > "$ROOT_DIR/frontend/src/app/services/quest.service.ts"
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Quest } from '../models/quest';

@Injectable({ providedIn: 'root' })
export class QuestService {
  private apiUrl = '/api/v1/quests';

  constructor(private http: HttpClient) {}

  getQuests(): Observable<Quest[]> {
    return this.http.get<Quest[]>(this.apiUrl);
  }
}
QUEST_SERVICE_TS

# Angular component for listing quests using standalone component
cat <<'QUEST_LIST_COMPONENT_TS' > "$ROOT_DIR/frontend/src/app/components/quest-list/quest-list.component.ts"
import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { QuestService } from '../../services/quest.service';
import { Quest } from '../../models/quest';

@Component({
  selector: 'app-quest-list',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './quest-list.component.html',
  styleUrls: ['./quest-list.component.css'],
})
export class QuestListComponent implements OnInit {
  quests: Quest[] = [];

  constructor(private questService: QuestService) {}

  ngOnInit(): void {
    this.loadQuests();
  }

  private loadQuests(): void {
    this.questService.getQuests().subscribe({
      next: (data) => (this.quests = data),
      error: (err) => console.error('Failed to load quests', err),
    });
  }
}
QUEST_LIST_COMPONENT_TS

# HTML template for the quest list component
cat <<'QUEST_LIST_COMPONENT_HTML' > "$ROOT_DIR/frontend/src/app/components/quest-list/quest-list.component.html"
<div class="quest-list">
  <h2>Lista de Quests</h2>
  <ul>
    <li *ngFor="let quest of quests">
      <strong>{{ quest.name }}</strong>
      <p>{{ quest.description }}</p>
    </li>
  </ul>
</div>
QUEST_LIST_COMPONENT_HTML

# CSS styles for the quest list component
cat <<'QUEST_LIST_COMPONENT_CSS' > "$ROOT_DIR/frontend/src/app/components/quest-list/quest-list.component.css"
.quest-list {
  max-width: 600px;
  margin: 2rem auto;
  padding: 1rem;
  background-color: #f9f9f9;
  border-radius: 4px;
}

.quest-list h2 {
  text-align: center;
  margin-bottom: 1rem;
}

.quest-list ul {
  list-style-type: none;
  padding: 0;
}

.quest-list li {
  padding: 0.5rem;
  border-bottom: 1px solid #e0e0e0;
}

.quest-list li:last-child {
  border-bottom: none;
}

.quest-list strong {
  display: block;
  font-weight: bold;
  margin-bottom: 0.25rem;
}
.quest-list p {
  margin: 0;
}
QUEST_LIST_COMPONENT_CSS

echo "Frontend skeleton created with quest list component and service."

# Remove legacy Angular module file if it exists. The project uses standalone
# components (Angular 21), so no app.module.ts is needed.
rm -f "$ROOT_DIR/frontend/src/app/app.module.ts"

# Proceed to quests setup
bash "$SCRIPT_DIR/04_setup_quests.sh"