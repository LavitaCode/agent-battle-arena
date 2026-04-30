export interface PostMortem {
  id: string;
  run_id: string;
  final_score: number;
  tests_passed: number;
  tests_failed: number;
  claude_analysis: string;
  strengths: string[];
  failures: string[];
  suggestions: string[];
}
