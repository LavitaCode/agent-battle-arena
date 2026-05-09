import { CommonModule } from '@angular/common';
import { Component, inject } from '@angular/core';
import { RouterLink } from '@angular/router';
import { LucideAngularModule, Trophy } from 'lucide-angular';
import { CardModule } from 'primeng/card';
import { TagModule } from 'primeng/tag';
import { catchError, of } from 'rxjs';

import { LeaderboardEntry } from '../../models/battle.model';
import { RankingService } from '../../services/ranking/ranking';

@Component({
  selector: 'app-ranking',
  imports: [CommonModule, RouterLink, LucideAngularModule, CardModule, TagModule],
  templateUrl: './ranking.html',
  styleUrl: './ranking.css',
})
export class Ranking {
  private readonly rankingService = inject(RankingService);
  readonly trophyIcon = Trophy;
  readonly leaderboard$ = this.rankingService
    .listLeaderboard()
    .pipe(catchError(() => of([] as LeaderboardEntry[])));
}
