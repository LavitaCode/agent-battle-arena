export interface ArenaEvent {
  id: string;
  run_id: string;
  type: string;
  message: string;
  timestamp: string;
  payload?: Record<string, unknown>;
}
