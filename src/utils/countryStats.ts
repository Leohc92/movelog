import { COUNTRY_ALIASES } from '../static/countryAliases.ts'
import { chinaCities } from '../static/city.ts'

interface ActivityLocation {
  country_codes?: string[]
  location_country?: string | null
}

function normalize(code: string): string | undefined {
  return COUNTRY_ALIASES[code.trim().toLowerCase()]
}

export function getCountryCodes(activity: ActivityLocation): string[] {
  if (Array.isArray(activity.country_codes)) {
    return [...new Set(activity.country_codes.map(normalize).filter((code): code is string => Boolean(code)))]
  }
  const location = activity.location_country
  if (!location || location === 'None') return []
  if (location.startsWith('{')) {
    try {
      const parsed = JSON.parse(location.replace(/'/g, '"').replace(/None/g, 'null')) as { country?: string }
      const code = typeof parsed.country === 'string' ? normalize(parsed.country) : undefined
      return code ? [code] : []
    } catch { return [] }
  }
  const exact = normalize(location)
  if (exact) return [exact]
  const codes = new Set<string>()
  for (const [name, code] of Object.entries(COUNTRY_ALIASES)) {
    if (name.length > 1 && /[\u4e00-\u9fff]/.test(name) && location.includes(name)) codes.add(code)
  }
  if (!codes.size && chinaCities.some(city => location.includes(city.name))) codes.add('CN')
  return [...codes]
}

export function getVisitedCountries(activities: ActivityLocation[]): string[] {
  return [...new Set(activities.flatMap(getCountryCodes))].sort()
}

const countryNames = {
  zh: new Intl.DisplayNames(['zh-CN'], { type: 'region' }),
  en: new Intl.DisplayNames(['en'], { type: 'region' }),
}

export function getCountryName(code: string, locale: 'zh' | 'en'): string {
  return countryNames[locale].of(code) ?? code
}
