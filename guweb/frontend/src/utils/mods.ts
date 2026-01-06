import { Mods } from '@/types'

interface ModInfo {
  name: string
  short: string
  color?: string
}

const MOD_INFO: Record<number, ModInfo> = {
  [Mods.NOFAIL]: { name: 'No Fail', short: 'NF' },
  [Mods.EASY]: { name: 'Easy', short: 'EZ' },
  [Mods.TOUCHSCREEN]: { name: 'Touch Screen', short: 'TD' },
  [Mods.HIDDEN]: { name: 'Hidden', short: 'HD' },
  [Mods.HARDROCK]: { name: 'Hard Rock', short: 'HR' },
  [Mods.SUDDENDEATH]: { name: 'Sudden Death', short: 'SD' },
  [Mods.DOUBLETIME]: { name: 'Double Time', short: 'DT' },
  [Mods.RELAX]: { name: 'Relax', short: 'RX', color: '#00ccff' },
  [Mods.HALFTIME]: { name: 'Half Time', short: 'HT' },
  [Mods.NIGHTCORE]: { name: 'Nightcore', short: 'NC' },
  [Mods.FLASHLIGHT]: { name: 'Flashlight', short: 'FL' },
  [Mods.AUTOPLAY]: { name: 'Auto', short: 'AT' },
  [Mods.SPUNOUT]: { name: 'Spun Out', short: 'SO' },
  [Mods.AUTOPILOT]: { name: 'Autopilot', short: 'AP', color: '#ffaa00' },
  [Mods.PERFECT]: { name: 'Perfect', short: 'PF' },
  [Mods.SCOREV2]: { name: 'ScoreV2', short: 'V2' }
}

export function getModsString(modsValue: number): string {
  if (modsValue === 0) return 'NM'
  
  const mods: string[] = []
  
  // Check each mod flag
  for (const [value, info] of Object.entries(MOD_INFO)) {
    const modValue = parseInt(value)
    if (modsValue & modValue) {
      mods.push(info.short)
    }
  }
  
  // Handle special cases
  let result = mods.join('')
  
  // DT + NC = NC only
  if (result.includes('NC') && result.includes('DT')) {
    result = result.replace('DT', '')
  }
  
  // SD + PF = PF only
  if (result.includes('PF') && result.includes('SD')) {
    result = result.replace('SD', '')
  }
  
  return result || 'NM'
}

export function getModsArray(modsValue: number): ModInfo[] {
  if (modsValue === 0) return []
  
  const mods: ModInfo[] = []
  
  for (const [value, info] of Object.entries(MOD_INFO)) {
    const modValue = parseInt(value)
    if (modsValue & modValue) {
      mods.push(info)
    }
  }
  
  return mods
}

export function hasRelax(modsValue: number): boolean {
  return (modsValue & Mods.RELAX) !== 0
}

export function hasAutopilot(modsValue: number): boolean {
  return (modsValue & Mods.AUTOPILOT) !== 0
}

export function isVanilla(modsValue: number): boolean {
  return !hasRelax(modsValue) && !hasAutopilot(modsValue)
}
