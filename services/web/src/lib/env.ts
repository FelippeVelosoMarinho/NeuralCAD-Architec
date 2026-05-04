/** Base URL FastAPI — nunca usar input do utilizador para o host */
export function getApiBase(): string {
  return import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8010";
}
