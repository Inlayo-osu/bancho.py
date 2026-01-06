// User types
export interface User {
  id: number
  name: string
  country: string
  priv: number
  clan_id?: number
  clan_name?: string
  clan_tag?: string
  registered_on: string
  latest_activity: string
}

// Stats types
export interface UserStats {
  id: number
  mode: number
  tscore: number
  rscore: number
  pp: number
  plays: number
  playtime: number
  acc: number
  max_combo: number
  total_hits: number
  replay_views: number
  xh_count: number
  x_count: number
  sh_count: number
  s_count: number
  a_count: number
  rank: number
  country_rank: number
}

// Beatmap types
export interface Beatmap {
  id: number
  set_id: number
  status: number
  md5: string
  artist: string
  title: string
  version: string
  creator: string
  filename: string
  last_update: string
  total_length: number
  max_combo: number
  frozen: boolean
  plays: number
  passes: number
  mode: number
  bpm: number
  cs: number
  ar: number
  od: number
  hp: number
  diff: number
}

// Score types
export interface Score {
  id: number
  beatmap_md5: string
  userid: number
  pp: number
  score: number
  max_combo: number
  mods: number
  acc: number
  n300: number
  n100: number
  n50: number
  nmiss: number
  ngeki: number
  nkatu: number
  grade: string
  status: number
  mode: number
  play_time: string
  time_elapsed: number
  perfect: boolean
}

// Leaderboard types
export interface LeaderboardUser extends User {
  stats: UserStats
  rank: number
}

// API Response types
export interface ApiResponse<T> {
  status: 'success' | 'error'
  data?: T
  message?: string
}

// Session types
export interface Session {
  authenticated: boolean
  user_data?: {
    id: number
    name: string
    priv: number
    country: string
  }
}

// Game modes
export enum GameMode {
  OSU = 0,
  TAIKO = 1,
  CATCH = 2,
  MANIA = 3
}

// Mods
export enum Mods {
  NOMOD = 0,
  NOFAIL = 1,
  EASY = 2,
  TOUCHSCREEN = 4,
  HIDDEN = 8,
  HARDROCK = 16,
  SUDDENDEATH = 32,
  DOUBLETIME = 64,
  RELAX = 128,
  HALFTIME = 256,
  NIGHTCORE = 512,
  FLASHLIGHT = 1024,
  AUTOPLAY = 2048,
  SPUNOUT = 4096,
  AUTOPILOT = 8192,
  PERFECT = 16384,
  KEY4 = 32768,
  KEY5 = 65536,
  KEY6 = 131072,
  KEY7 = 262144,
  KEY8 = 524288,
  FADEIN = 1048576,
  RANDOM = 2097152,
  CINEMA = 4194304,
  TARGET = 8388608,
  KEY9 = 16777216,
  KEYCOOP = 33554432,
  KEY1 = 67108864,
  KEY3 = 134217728,
  KEY2 = 268435456,
  SCOREV2 = 536870912
}

// Map status
export enum BeatmapStatus {
  NOT_SUBMITTED = -1,
  PENDING = 0,
  UPDATE_AVAILABLE = 1,
  RANKED = 2,
  APPROVED = 3,
  QUALIFIED = 4,
  LOVED = 5
}
