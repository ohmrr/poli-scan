import type { Match } from "@/types/match"
import { apiFetch } from "./api"

export const getMatches = () => apiFetch<Match[]>(`/matches`)

export const getMatchesByJurisdiction = (jurisdiction: string) =>
  apiFetch<Match[]>(`/matches/${jurisdiction}`)
