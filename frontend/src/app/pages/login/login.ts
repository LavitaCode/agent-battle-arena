import { CommonModule } from '@angular/common';
import { Component, inject, signal } from '@angular/core';
import { FormControl, ReactiveFormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';

import { Auth } from '../../services/auth/auth';

@Component({
  selector: 'app-login',
  imports: [CommonModule, ReactiveFormsModule, RouterLink],
  templateUrl: './login.html',
  styleUrl: './login.css',
})
export class Login {
  private readonly authService = inject(Auth);
  private readonly router = inject(Router);

  readonly githubLogin = new FormControl('', { nonNullable: true });
  readonly inviteCode = new FormControl('ALPHA-ACCESS', { nonNullable: true });
  readonly errorMessage = signal('');

  submit() {
    this.errorMessage.set('');
    this.authService.login(this.githubLogin.value, this.inviteCode.value).subscribe({
      next: () => this.router.navigate(['/dashboard']),
      error: () => this.errorMessage.set('Nao foi possivel entrar no closed alpha. Confira o login e o invite.'),
    });
  }
}
