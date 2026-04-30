export interface RunSuiteResult {
  suite: string;
  passed: number;
  failed: number;
  duration_ms: number | null;
}

export interface RunSummary {
  technical_score: number;
  total_score: number;
  duration_ms: number | null;
  suites: RunSuiteResult[];
  notes: string[];
}

export interface Run {
  id: string;
  quest_id: string;
  agent_profile_id: string;
  workspace_files: Record<string, string>;
  status: string;
  sandbox_id: string | null;
  created_at: string;
  updated_at: string;
  summary: RunSummary;
}

export interface RunArtifact {
  name: string;
  path: string;
  content: string;
}
