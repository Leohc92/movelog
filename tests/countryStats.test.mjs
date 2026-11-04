import assert from 'node:assert/strict'
import test from 'node:test'
import { getCountryCodes, getVisitedCountries, getCountryName } from '../src/utils/countryStats.ts'

test('generic workout labels do not invent a country', () => {
  for (const location_country of ['徒步', '跑步', '爬楼', null]) {
    assert.deepEqual(getCountryCodes({ location_country }), [])
  }
})

test('GPS countries override generic and stale location names', () => {
  assert.deepEqual(getCountryCodes({ country_codes: ['JP'], location_country: '上海市' }), ['JP'])
  assert.deepEqual(getCountryCodes({ country_codes: [], location_country: '徒步' }), [])
})

test('cross-border visits are counted once, with Hong Kong part of China', () => {
  const activities = [
    { country_codes: ['CN', 'HK'] },
    { country_codes: ['JP'] },
    { country_codes: ['KR'] },
    { country_codes: ['TH'] },
    { country_codes: ['FR', 'IT', 'CH'] },
    { country_codes: ['CH'] },
  ]
  assert.deepEqual(getVisitedCountries(activities), ['CH', 'CN', 'FR', 'IT', 'JP', 'KR', 'TH'])
})

test('legacy explicit country names remain supported', () => {
  assert.deepEqual(getCountryCodes({ location_country: "{'country': 'Japan'}" }), ['JP'])
  assert.deepEqual(getCountryCodes({ location_country: '上海市 公路骑行' }), ['CN'])
  assert.equal(getCountryName('JP', 'zh'), '日本')
})
