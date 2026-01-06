import { apiClient } from './client'
import type { User, UserStats, Score, ApiResponse } from '@/types'

export interface UserProfileData {
  user: User
  stats: Record<string, UserStats>
  recent_scores: Score[]
  best_scores: Score[]
  status: {
    online: boolean
    status: number
  }
}

export const userApi = {
  // Get user profile
  async getProfile(userId: number, mode: number = 0, mods: number = 0): Promise<UserProfileData> {
    return apiClient.get(`/v1/get_profile_data`, {
      params: { id: userId, mode, mods }
    })
  },

  // Get user stats
  async getStats(userId: number, mode: number = 0): Promise<UserStats> {
    return apiClient.get(`/v1/get_user_stats`, {
      params: { id: userId, mode }
    })
  },

  // Get user scores
  async getScores(userId: number, scope: 'best' | 'recent', mode: number = 0, limit: number = 5): Promise<Score[]> {
    return apiClient.get(`/v1/get_user_scores`, {
      params: { id: userId, scope, mode, limit }
    })
  },

  // Get user by name
  async getUserByName(name: string): Promise<User> {
    return apiClient.get(`/v1/get_user`, {
      params: { name }
    })
  }
}
