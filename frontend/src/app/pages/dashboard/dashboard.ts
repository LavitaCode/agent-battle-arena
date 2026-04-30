import { CommonModule } from '@angular/common';
import { Component, inject, signal } from '@angular/core';
import { FormControl, ReactiveFormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
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
  imports: [CommonModule, ReactiveFormsModule, RouterLink],
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
}
