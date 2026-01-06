export interface GradeInfo {
  letter: string
  color: string
  icon?: string
}

const GRADE_COLORS: Record<string, string> = {
  'XH': '#d4d4d4',
  'X': '#ffdd55',
  'SH': '#d4d4d4',
  'S': '#ffdd55',
  'A': '#88da20',
  'B': '#4a9beb',
  'C': '#d08cf7',
  'D': '#ff6666',
  'F': '#666666'
}

export function getGradeInfo(grade: string): GradeInfo {
  const normalizedGrade = grade.toUpperCase().replace('SS', 'X')
  
  return {
    letter: normalizedGrade,
    color: GRADE_COLORS[normalizedGrade] || '#ffffff'
  }
}

export function getGradeClass(grade: string): string {
  return `rank-${grade.toLowerCase().replace('ss', 'x')}`
}
