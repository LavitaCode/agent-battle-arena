export interface AgentTemplate {
  id: string;
  name: string;
  archetype: string;
  description: string;
  recommended_for: string[];
  locked_fields: string[];
  default_profile_payload: Record<string, unknown>;
  editable_sections: string[];
  tips: string[];
}
