import { apiClient } from './client'
import type { LeaderboardUser } from '@/types'

export interface LeaderboardParams {
  mode: number
  mods: number
  country?: string
  page?: number
  limit?: number
}

export const leaderboardApi = {
  // Get leaderboard
  async getLeaderboard(params: LeaderboardParams): Promise<LeaderboardUser[]> {
    return apiClient.get(`/v1/get_leaderboard`, { params })
  }
}
