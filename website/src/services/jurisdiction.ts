import { apiFetch } from "./api"
import type { Jurisdiction } from "@/types/jurisdiction"

export const getJurisdictions = () => apiFetch<Jurisdiction[]>(`/jurisdictions`)

export const getJurisdiction = (id: number) =>
  apiFetch<Jurisdiction>(`/jurisdiction/${id}`)
