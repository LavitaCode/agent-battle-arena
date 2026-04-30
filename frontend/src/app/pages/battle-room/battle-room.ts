import { CommonModule } from '@angular/common';
import { Component, computed, inject, signal } from '@angular/core';
import { FormControl, ReactiveFormsModule } from '@angular/forms';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { catchError, combineLatest, map, of, startWith, switchMap, timer } from 'rxjs';

import { AgentProfile } from '../../models/agent-profile.model';
import { AuthSession } from '../../models/auth-session.model';
import { BattleDetail, BattleReplayBundle } from '../../models/battle.model';
import { Auth } from '../../services/auth/auth';
import { AgentProfileService } from '../../services/agent-profile/agent-profile';
import { BattleService } from '../../services/battle/battle';

@Component({
  selector: 'app-battle-room',
  imports: [CommonModule, ReactiveFormsModule, RouterLink],
  templateUrl: './battle-room.html',
  styleUrl: './battle-room.css',
})
export class BattleRoom {
  private readonly route = inject(ActivatedRoute);
  private readonly authService = inject(Auth);
  private readonly battleService = inject(BattleService);
  private readonly profileService = inject(AgentProfileService);

  readonly joinProfileId = new FormControl('', { nonNullable: true });
  readonly overridePath = new FormControl('app/main.py', { nonNullable: true });
  readonly overrideContent = new FormControl('', { nonNullable: true });
  readonly errorMessage = signal('');
  readonly replayBundle = signal<BattleReplayBundle | null>(null);

  readonly me$ = this.authService.me().pipe(catchError(() => of({ authenticated: false, user: null } as AuthSession)));
  readonly myProfiles$ = this.profileService.listMine().pipe(catchError(() => of([] as AgentProfile[])));
  readonly battleId$ = this.route.paramMap.pipe(map((params) => params.get('id') ?? ''));
  readonly battle$ = this.battleId$.pipe(
    switchMap((battleId) =>
      timer(0, 2500).pipe(
        switchMap(() => this.battleService.getById(battleId)),
        catchError(() => of(null))
      )
    )
  );
  readonly vm$ = combineLatest([this.me$, this.myProfiles$, this.battle$]).pipe(
    map(([session, profiles, detail]) => ({ session, profiles, detail }))
  );

  isCreator = computed(() => false);

  joinBattle(detail: BattleDetail) {
    this.errorMessage.set('');
    const profileId = this.joinProfileId.value;
    const workspaceFiles =
      this.overrideContent.value.trim().length > 0
        ? { [this.overridePath.value]: this.overrideContent.value }
        : {};
    this.battleService.join(detail.battle.id, { agent_profile_id: profileId, workspace_files: workspaceFiles }).subscribe({
      next: () => {},
      error: () => this.errorMessage.set('Nao foi possivel entrar na battle.'),
    });
  }

  submitWorkspace(detail: BattleDetail) {
    this.errorMessage.set('');
    this.battleService.submit(detail.battle.id, { [this.overridePath.value]: this.overrideContent.value }).subscribe({
      next: () => {},
      error: () => this.errorMessage.set('Falha ao atualizar a submissao.'),
    });
  }

  startBattle(detail: BattleDetail) {
    this.errorMessage.set('');
    this.battleService.start(detail.battle.id).subscribe({
      next: () => {},
      error: () => this.errorMessage.set('Nao foi possivel iniciar a battle.'),
    });
  }

  loadReplay(detail: BattleDetail) {
    this.battleService.getReplay(detail.battle.id).subscribe({
      next: (bundle) => this.replayBundle.set(bundle),
      error: () => this.errorMessage.set('Replay ainda nao esta disponivel.'),
    });
  }

  isParticipant(detail: BattleDetail, session: AuthSession): boolean {
    const userId = session.user?.id;
    return !!userId && detail.participants.some((item) => item.user_id === userId);
  }

  canStart(detail: BattleDetail, session: AuthSession): boolean {
    return detail.battle.created_by_user_id === session.user?.id && detail.battle.status === 'ready';
  }
}
