import { CommonModule } from '@angular/common';
import { Component, inject } from '@angular/core';
import { RouterLink } from '@angular/router';
import { catchError, of } from 'rxjs';

import { Quest } from '../../models/quest.model';
import { QuestService } from '../../services/quest/quest';

@Component({
  selector: 'app-quest-queue',
  imports: [CommonModule, RouterLink],
  templateUrl: './quest-queue.html',
  styleUrl: './quest-queue.css',
})
export class QuestQueue {
  private readonly questService = inject(QuestService);

  readonly quests$ = this.questService.list().pipe(catchError(() => of([] as Quest[])));
}
