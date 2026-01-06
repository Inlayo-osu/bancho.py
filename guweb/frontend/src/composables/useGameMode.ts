import { ref, computed } from 'vue'
import { GameMode } from '@/types'

export interface ModeInfo {
  id: number
  name: string
  short: string
  icon: string
  color: string
}

const MODE_INFO: Record<GameMode, ModeInfo> = {
  [GameMode.OSU]: {
    id: 0,
    name: 'osu!',
    short: 'std',
    icon: 'fa-circle',
    color: '#ff66aa'
  },
  [GameMode.TAIKO]: {
    id: 1,
    name: 'osu!taiko',
    short: 'taiko',
    icon: 'fa-drum',
    color: '#ff8c1a'
  },
  [GameMode.CATCH]: {
    id: 2,
    name: 'osu!catch',
    short: 'catch',
    icon: 'fa-apple-alt',
    color: '#66cc66'
  },
  [GameMode.MANIA]: {
    id: 3,
    name: 'osu!mania',
    short: 'mania',
    icon: 'fa-th',
    color: '#a366ff'
  }
}

export function useGameMode() {
  const currentMode = ref<GameMode>(GameMode.OSU)

  const modeInfo = computed(() => MODE_INFO[currentMode.value])
  const modeName = computed(() => modeInfo.value.name)
  const modeColor = computed(() => modeInfo.value.color)
  const modeIcon = computed(() => modeInfo.value.icon)

  function setMode(mode: GameMode) {
    currentMode.value = mode
  }

  function getModeInfo(mode: GameMode): ModeInfo {
    return MODE_INFO[mode]
  }

  return {
    currentMode,
    modeInfo,
    modeName,
    modeColor,
    modeIcon,
    setMode,
    getModeInfo
  }
}
