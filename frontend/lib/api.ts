const API_BASE = "/api/v1";

export interface StartupListItem {
  id: number;
  name: string;
  sector: string | null;
  funding_stage: string | null;
  state: string | null;
  ai_label: string | null;
  ai_confidence: number | null;
  source_count: number;
}

export interface StartupDetail extends StartupListItem {
  website: string | null;
  description: string | null;
  founders: string | null;
  funding_amount_usd: number | null;
  employee_count_estimate: string | null;
  ai_signals: string | null;
  tech_stack_mentions: string | null;
  business_area: string | null;
  program: string | null;
  cohort_year: number | null;
  cohort_cycle: string | null;
  inovativa_status: string | null;
  created_at: string | null;
  updated_at: string | null;
  classifications: Classification[];
  validations: Validation[];
  recommendations: Recommendation[];
  briefings: Briefing[];
  sources: Source[];
}

export interface Classification {
  id: number;
  label: string;
  confidence: number | null;
  justification: string | null;
  classified_at: string | null;
}

export interface Validation {
  id: number;
  is_valid: boolean;
  issues: string | null;
  source_count: number | null;
  validated_at: string | null;
}

export interface Recommendation {
  id: number;
  nvidia_technology: string;
  technical_justification: string | null;
  business_justification: string | null;
  priority: string;
  implementation_complexity: string | null;
  suggested_next_action: string | null;
  created_at: string | null;
}

export interface Briefing {
  id: number;
  briefing_text: string;
  created_at: string | null;
}

export interface Source {
  id: number;
  url: string;
  extraction_method: string;
  fetched_at: string | null;
}

export interface Stats {
  total_startups: number;
  classified: number;
  unclassified: number;
  by_ai_label: {
    ai_native: number;
    ai_enabled: number;
    non_ai: number;
  };
  top_sectors: { sector: string; count: number }[];
  top_recommended_technologies: { nvidia_technology: string; count: number }[];
}

export interface SearchResult {
  query: string;
  reason: string;
  total: number;
  results: {
    id: number;
    name: string;
    sector: string | null;
    funding_stage: string | null;
    state: string | null;
    has_ai: boolean;
  }[];
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

async function fetchJSON<T>(url: string, init?: RequestInit): Promise<T> {
  const res = await fetch(url, {
    ...init,
    headers: { "Content-Type": "application/json", ...init?.headers },
  });
  if (!res.ok) {
    throw new Error(`API error: ${res.status} ${res.statusText}`);
  }
  return res.json();
}

export async function getStartups(params?: {
  page?: number;
  page_size?: number;
  sector?: string;
  ai_label?: string;
  funding?: string;
  state?: string;
  q?: string;
}): Promise<PaginatedResponse<StartupListItem>> {
  const searchParams = new URLSearchParams();
  if (params?.page) searchParams.set("page", String(params.page));
  if (params?.page_size) searchParams.set("page_size", String(params.page_size));
  if (params?.sector) searchParams.set("sector", params.sector);
  if (params?.ai_label) searchParams.set("ai_label", params.ai_label);
  if (params?.funding) searchParams.set("funding", params.funding);
  if (params?.state) searchParams.set("state", params.state);
  if (params?.q) searchParams.set("q", params.q);
  const qs = searchParams.toString();
  return fetchJSON(`${API_BASE}/startups/${qs ? `?${qs}` : ""}`);
}

export async function getStartup(id: number): Promise<StartupDetail> {
  return fetchJSON(`${API_BASE}/startups/${id}/`);
}

export async function analyzeStartup(id: number): Promise<{
  startup_id: number;
  classification: { label: string | null; confidence: number | null };
  recommendations: { technology: string; priority: string }[];
  briefing: string | null;
}> {
  return fetchJSON(`${API_BASE}/startups/${id}/analyze/`, { method: "POST" });
}

export async function getStats(): Promise<Stats> {
  return fetchJSON(`${API_BASE}/stats/`);
}

export async function searchStartups(
  query: string
): Promise<SearchResult> {
  return fetchJSON(`${API_BASE}/startups/search/?q=${encodeURIComponent(query)}`);
}
