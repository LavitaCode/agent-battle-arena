export interface Quest {
  id: string;
  title: string;
  description: string;
  difficulty: string;
  mode: string;
  time_limit_minutes: number;
  stack: {
    backend?: string | null;
    frontend?: string | null;
    database?: string | null;
  };
  objective?: string | null;
  requirements: string[];
  forbidden_actions: string[];
  instructions?: string | null;
}
