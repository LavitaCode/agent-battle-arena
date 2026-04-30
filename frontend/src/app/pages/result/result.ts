import { CommonModule } from '@angular/common';
import { Component, inject } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { catchError, forkJoin, map, of, switchMap } from 'rxjs';

import { ArenaService } from '../../services/arena/arena';
import { RankingService } from '../../services/ranking/ranking';

@Component({
  selector: 'app-result',
  imports: [CommonModule, RouterLink],
  templateUrl: './result.html',
  styleUrl: './result.css',
})
export class Result {
  private readonly route = inject(ActivatedRoute);
  private readonly arenaService = inject(ArenaService);
  private readonly rankingService = inject(RankingService);

  readonly runId$ = this.route.paramMap.pipe(map((params) => params.get('id') ?? ''));
  readonly bundle$ = this.runId$.pipe(
    switchMap((runId) => this.arenaService.getRunBundle(runId)),
    catchError(() => of(null))
  );

  readonly ranking$ = this.bundle$.pipe(
    switchMap((bundle) => {
      if (!bundle) {
        return of([]);
      }
      return this.rankingService.listForQuest(bundle.run.quest_id);
    }),
    catchError(() => of([]))
  );

  readonly artifacts$ = this.runId$.pipe(
    switchMap((runId) =>
      forkJoin({
        list: this.arenaService.listArtifacts(runId),
        diff: this.arenaService.getArtifact(runId, 'workspace_diff'),
        stdout: this.arenaService.getArtifact(runId, 'stdout_log'),
      })
    ),
    catchError(() => of(null))
  );
}
