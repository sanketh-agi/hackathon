const BASE_URL = (import.meta as any).env?.VITE_API_BASE_URL ?? "/api";

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers:
      options.body && !(options.body instanceof FormData)
        ? { "Content-Type": "application/json", ...options.headers }
        : options.headers,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`${res.status} ${res.statusText}: ${text}`);
  }
  if (res.status === 204) return undefined as T;
  const contentType = res.headers.get("content-type") || "";
  if (contentType.includes("application/json")) return res.json();
  return (await res.text()) as unknown as T;
}

export interface Customer {
  id: number;
  name: string;
  app_url: string;
  config_json: Record<string, unknown>;
  created_at: string;
}

export interface DocumentItem {
  id: number;
  customer_id: number;
  doc_type: string;
  filename: string;
  extracted_text_preview: string;
  uploaded_at: string;
}

export interface Rule {
  id: number;
  customer_id: number;
  document_id: number;
  sheet_name: string;
  rule_name: string;
  description: string;
  workflow: string;
}

export interface TestCase {
  id: number;
  customer_id: number;
  rule_id: number | null;
  title: string;
  preconditions: string;
  steps_json: string[];
  expected_result: string;
  priority: string;
  requirement_trace: string;
  status: string;
  generated_at: string;
  approved_at: string | null;
}

export interface PlaywrightScript {
  id: number;
  test_case_id: number;
  code: string;
  generated_at: string;
}

export interface TestRun {
  id: number;
  test_case_id: number;
  status: string;
  result_json: Record<string, unknown>;
  started_at: string;
  finished_at: string | null;
}

export const api = {
  listCustomers: () => request<Customer[]>("/customers"),
  createCustomer: (data: { name: string; app_url: string; config_json?: Record<string, unknown> }) =>
    request<Customer>("/customers", { method: "POST", body: JSON.stringify(data) }),

  listDocuments: (customerId: number) => request<DocumentItem[]>(`/customers/${customerId}/documents`),
  uploadDocument: (customerId: number, docType: string, file: File) => {
    const form = new FormData();
    form.append("doc_type", docType);
    form.append("file", file);
    return request<DocumentItem>(`/customers/${customerId}/documents`, { method: "POST", body: form });
  },

  listRules: (customerId: number) => request<Rule[]>(`/customers/${customerId}/rules`),

  listTestCases: (customerId: number) => request<TestCase[]>(`/customers/${customerId}/test-cases`),
  generateTestCases: (customerId: number, ruleId: number, instructions: string, countHint?: number) =>
    request<TestCase[]>(`/customers/${customerId}/test-cases/generate`, {
      method: "POST",
      body: JSON.stringify({ rule_id: ruleId, instructions, count_hint: countHint }),
    }),
  updateTestCase: (id: number, data: Partial<TestCase>) =>
    request<TestCase>(`/test-cases/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
  approveTestCase: (id: number) => request<TestCase>(`/test-cases/${id}/approve`, { method: "POST" }),

  generateScript: (testCaseId: number) =>
    request<PlaywrightScript>(`/test-cases/${testCaseId}/generate-script`, { method: "POST" }),
  getScript: (testCaseId: number) => request<PlaywrightScript>(`/test-cases/${testCaseId}/script`),

  runTestCase: (testCaseId: number) => request<TestRun>(`/test-cases/${testCaseId}/run`, { method: "POST" }),
  listRuns: (testCaseId: number) => request<TestRun[]>(`/test-cases/${testCaseId}/runs`),

  reportUrl: (customerId: number) => `${BASE_URL}/customers/${customerId}/report`,
};
