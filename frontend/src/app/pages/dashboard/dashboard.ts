import { CommonModule } from '@angular/common';
import { Component, inject, signal } from '@angular/core';
import { FormControl, ReactiveFormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { ClipboardList, LucideAngularModule, Plus, Swords, Trophy, Users } from 'lucide-angular';
import { ButtonModule } from 'primeng/button';
import { CardModule } from 'primeng/card';
import { InputTextModule } from 'primeng/inputtext';
import { MessageModule } from 'primeng/message';
import { ProgressSpinnerModule } from 'primeng/progressspinner';
import { SelectModule } from 'primeng/select';
import { TagModule } from 'primeng/tag';
import { TextareaModule } from 'primeng/textarea';
import { catchError, combineLatest, map, of } from 'rxjs';

import { AgentProfile } from '../../models/agent-profile.model';
import { AgentTemplate } from '../../models/agent-template.model';
import { BattleDetail, LeaderboardEntry } from '../../models/battle.model';
import { Quest } from '../../models/quest.model';
import { User } from '../../models/user.model';
import { AgentProfileService } from '../../services/agent-profile/agent-profile';
import { Auth } from '../../services/auth/auth';
import { BattleService } from '../../services/battle/battle';
import { QuestService } from '../../services/quest/quest';
import { RankingService } from '../../services/ranking/ranking';
import { TemplateService } from '../../services/template/template';

@Component({
  selector: 'app-dashboard',
  imports: [
    CommonModule,
    ReactiveFormsModule,
    RouterLink,
    LucideAngularModule,
    ButtonModule,
    CardModule,
    InputTextModule,
    MessageModule,
    ProgressSpinnerModule,
    SelectModule,
    TagModule,
    TextareaModule,
  ],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.css',
})
export class Dashboard {
  private readonly authService = inject(Auth);
  private readonly templateService = inject(TemplateService);
  private readonly profileService = inject(AgentProfileService);
  private readonly questService = inject(QuestService);
  private readonly battleService = inject(BattleService);
  private readonly rankingService = inject(RankingService);
  private readonly router = inject(Router);

  readonly selectedQuestId = new FormControl('', { nonNullable: true });
  readonly selectedProfileId = new FormControl('', { nonNullable: true });
  readonly overridePath = new FormControl('app/main.py', { nonNullable: true });
  readonly overrideContent = new FormControl('', { nonNullable: true });
  readonly errorMessage = signal('');
  readonly battleIcon = Swords;
  readonly createIcon = Plus;
  readonly templateIcon = Users;
  readonly leaderboardIcon = Trophy;
  readonly questIcon = ClipboardList;

  readonly vm$ = combineLatest([
    this.authService.me().pipe(catchError(() => of({ authenticated: false, user: null }))),
    this.templateService.listAgentTemplates().pipe(catchError(() => of([] as AgentTemplate[]))),
    this.profileService.listMine().pipe(catchError(() => of([] as AgentProfile[]))),
    this.questService.list().pipe(catchError(() => of([] as Quest[]))),
    this.battleService.list().pipe(catchError(() => of([] as BattleDetail[]))),
    this.rankingService.listLeaderboard().pipe(catchError(() => of([] as LeaderboardEntry[]))),
  ]).pipe(
    map(([session, templates, profiles, quests, battles, leaderboard]) => {
      if (!session.authenticated) {
        this.router.navigate(['/login']);
      }
      if (!this.selectedQuestId.value && quests.length > 0) {
        this.selectedQuestId.setValue(quests[0].id);
      }
      if (!this.selectedProfileId.value && profiles.length > 0) {
        this.selectedProfileId.setValue(profiles[0].id);
      }
      return {
        user: session.user as User | null,
        templates,
        profiles,
        quests,
        questOptions: quests.map((quest) => ({
          label: `${quest.title} · ${quest.difficulty}`,
          value: quest.id,
        })),
        profileOptions: profiles.map((profile) => ({
          label: `${profile.name} · ${profile.archetype}`,
          value: profile.id,
        })),
        battles,
        leaderboard,
      };
    })
  );

  createBattle() {
    this.errorMessage.set('');
    const workspaceFiles =
      this.overrideContent.value.trim().length > 0
        ? { [this.overridePath.value]: this.overrideContent.value }
        : undefined;
    this.battleService
      .create({
        quest_id: this.selectedQuestId.value,
        agent_profile_id: this.selectedProfileId.value,
        workspace_files: workspaceFiles,
      })
      .subscribe({
        next: (detail) => this.router.navigate(['/battles', detail.battle.id]),
        error: () => this.errorMessage.set('Nao foi possivel criar a battle agora.'),
      });
  }

  statusSeverity(status: string): 'success' | 'info' | 'warn' | 'danger' | 'secondary' | 'contrast' {
    if (status === 'completed') {
      return 'success';
    }
    if (status === 'failed') {
      return 'danger';
    }
    if (status === 'queued' || status === 'running') {
      return 'warn';
    }
    if (status === 'ready') {
      return 'info';
    }
    return 'secondary';
  }

  statusLabel(status: string): string {
    const labels: Record<string, string> = {
      waiting_for_opponent: 'aguardando oponente',
      ready: 'pronta',
      queued: 'na fila',
      running: 'executando',
      completed: 'concluída',
      failed: 'falhou',
    };
    return labels[status] ?? status;
  }
}
