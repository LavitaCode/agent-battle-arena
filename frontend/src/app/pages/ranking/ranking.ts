import { CommonModule } from '@angular/common';
import { Component, inject } from '@angular/core';
import { RouterLink } from '@angular/router';
import { catchError, of } from 'rxjs';

import { LeaderboardEntry } from '../../models/battle.model';
import { RankingService } from '../../services/ranking/ranking';

@Component({
  selector: 'app-ranking',
  imports: [CommonModule, RouterLink],
  templateUrl: './ranking.html',
  styleUrl: './ranking.css',
})
export class Ranking {
  private readonly rankingService = inject(RankingService);
  readonly leaderboard$ = this.rankingService
    .listLeaderboard()
    .pipe(catchError(() => of([] as LeaderboardEntry[])));
}
