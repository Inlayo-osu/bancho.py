import { apiClient } from './client'
import type { Beatmap, Score } from '@/types'

export interface BeatmapData {
  beatmap: Beatmap
  set: Beatmap[]
  scores: Score[]
}

export const beatmapApi = {
  // Get beatmap data
  async getBeatmap(beatmapId: number, mode: number = 0, mods: number = 0): Promise<BeatmapData> {
    return apiClient.get(`/v1/get_map_info`, {
      params: { id: beatmapId, mode, mods }
    })
  },

  // Get beatmap scores
  async getBeatmapScores(
    beatmapId: number,
    mode: number = 0,
    mods: number = 0,
    scope: 'best' | 'recent' = 'best',
    limit: number = 50
  ): Promise<Score[]> {
    return apiClient.get(`/v1/get_map_scores`, {
      params: { id: beatmapId, mode, mods, scope, limit }
    })
  }
}
