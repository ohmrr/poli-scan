import type { Holding } from "./holding"

export interface Official {
  id: number
  full_name: string
  jurisdiction_id: number
  jurisdiction_slug: string
  agency: string | null
  position: string | null
  email: string | null
  legistar_person_id: number | null
  holdings: Holding[]
}
