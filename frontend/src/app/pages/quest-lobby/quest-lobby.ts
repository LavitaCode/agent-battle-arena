import { CommonModule } from '@angular/common';
import { Component, inject } from '@angular/core';
import { FormControl, ReactiveFormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { catchError, map, of, switchMap } from 'rxjs';

import { AgentProfile } from '../../models/agent-profile.model';
import { Quest } from '../../models/quest.model';
import { StarterFile } from '../../models/starter-file.model';
import { AgentProfileService } from '../../services/agent-profile/agent-profile';
import { ArenaService } from '../../services/arena/arena';
import { QuestService } from '../../services/quest/quest';

@Component({
  selector: 'app-quest-lobby',
  imports: [CommonModule, ReactiveFormsModule, RouterLink],
  templateUrl: './quest-lobby.html',
  styleUrl: './quest-lobby.css',
})
export class QuestLobby {
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  private readonly questService = inject(QuestService);
  private readonly profileService = inject(AgentProfileService);
  private readonly arenaService = inject(ArenaService);

  readonly selectedProfileId = new FormControl('buildknight', { nonNullable: true });
  readonly errorMessage = new FormControl('', { nonNullable: true });
  readonly overridePath = new FormControl('app/main.py', { nonNullable: true });
  readonly overrideContent = new FormControl('', { nonNullable: true });
  readonly starterFiles = new FormControl<StarterFile[]>([], { nonNullable: true });

  readonly questId$ = this.route.paramMap.pipe(map((params) => params.get('id') ?? ''));
  readonly quest$ = this.questId$.pipe(
    switchMap((questId) => this.questService.getById(questId)),
    catchError(() => of(null))
  );
  readonly starterFiles$ = this.questId$.pipe(
    switchMap((questId) => this.questService.listStarterFiles(questId)),
    map((files) => {
      this.starterFiles.setValue(files);
      if (files.length > 0) {
        const currentPath = this.overridePath.value;
        const preferredFile =
          files.find((file) => file.path === currentPath) ??
          files.find((file) => file.path.endsWith('.py')) ??
          files[0];
        this.overridePath.setValue(preferredFile.path);
        this.overrideContent.setValue(preferredFile.content);
      }
      return files;
    }),
    catchError(() => {
      this.errorMessage.setValue('Nao foi possivel carregar os arquivos starter da quest.');
      return of([] as StarterFile[]);
    })
  );

  readonly profiles$ = this.profileService.list().pipe(
    switchMap((profiles) => {
      if (profiles.length > 0) {
        this.selectedProfileId.setValue(profiles[0].id);
        return of(profiles);
      }

      const seedProfile: AgentProfile = {
        id: 'buildknight',
        name: 'BuildKnight',
        archetype: 'architect',
        planning_style: 'tests_first',
        preferred_stack: ['python', 'fastapi', 'angular'],
        engineering_principles: ['Preservar requisitos', 'Preferir simplicidade testavel'],
        modules: ['api_design', 'test_debugging'],
        constraints: {
          allow_dependency_install: true,
          allow_external_network: false,
          allow_schema_change: true,
          max_runtime_minutes: 20,
        },
        memory: {
          slots: ['Ler testes antes de editar', 'Criar reproducao minima antes de refatorar'],
        },
        limits: {
          max_files_edited: 20,
          max_runs: 8,
        },
      };
      return this.profileService.create(seedProfile).pipe(map((profile) => [profile]));
    }),
    catchError(() => {
      this.errorMessage.setValue('Nao foi possivel carregar os agent profiles.');
      return of([] as AgentProfile[]);
    })
  );

  startRun(quest: Quest) {
    const profileId = this.selectedProfileId.value;
    this.errorMessage.setValue('');
    const workspaceFiles =
      this.overrideContent.value.trim().length > 0
        ? { [this.overridePath.value]: this.overrideContent.value }
        : undefined;
    this.arenaService.createRun({
      quest_id: quest.id,
      agent_profile_id: profileId,
      workspace_files: workspaceFiles,
    }).subscribe({
      next: (run) => {
        this.router.navigate(['/runs', run.id]);
      },
      error: () => {
        this.errorMessage.setValue('Falha ao iniciar a run. Verifique se o backend esta ativo.');
      },
    });
  }

  useStarterFile(path: string) {
    const selected = this.starterFiles.value.find((file) => file.path === path);
    if (!selected) {
      return;
    }
    this.overridePath.setValue(selected.path);
    this.overrideContent.setValue(selected.content);
  }
}
