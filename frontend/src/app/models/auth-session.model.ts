import { User } from './user.model';

export interface AuthSession {
  authenticated: boolean;
  user: User | null;
}
