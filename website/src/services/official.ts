import type { Official } from "@/types/official"
import { apiFetch } from "./api"

export const getOfficialById = (id: number) =>
  apiFetch<Official>(`/officials/${id}`)
