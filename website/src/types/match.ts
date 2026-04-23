export interface Match {
  id: number
  official_id: number
  jurisdiction_id: number
  agenda_item_id: number
  matched_interest: string
  confidence: number
  flagged: boolean
  reason: string | null
  pdf_url: string | null
  attachment_name: string | null
  event_date: string | null
  year: number
  created_at: string
}
