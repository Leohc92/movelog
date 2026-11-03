import assert from 'node:assert/strict'
import test from 'node:test'
import polyline from '@mapbox/polyline'
import { getRouteBounds, renderTrackSVG } from '../src/utils/routeGeometry.ts'

test('short tracks retain their points and fit inside the thumbnail', () => {
  const points = renderTrackSVG(polyline.encode([[46, 6], [47, 8], [46, 9]]))
    .split(' ').map(point => point.split(',').map(Number))
  assert.equal(points.length, 3)
  assert.deepEqual(points[0], [4, 52])
  assert.deepEqual(points.at(-1), [76, 52])
  assert.ok(points.every(point => point.every(value => Number.isFinite(value) && value >= 4 && value <= 76)))
})

test('a 200,000-point trek renders without overflowing the call stack', () => {
  const coords = Array.from({ length: 200000 }, (_, i) => [46 + Math.sin(i / 1000) * 0.1, 6 + i / 1000000])
  const points = renderTrackSVG(polyline.encode(coords)).split(' ')
  assert.ok(points.length >= 2 && points.length <= 2000)
  assert.ok(points.every(point => point.split(',').map(Number).every(Number.isFinite)))
})

test('map overview includes a remote overseas route and its full extent', () => {
  const domesticRoutes = Array.from({ length: 20 }, () => [[121, 31], [122, 32]])
  assert.deepEqual(getRouteBounds([...domesticRoutes, [[7, 46], [6, 47]]]), [[6, 31], [122, 47]])
})

test('empty and invalid route coordinates do not produce invalid bounds', () => {
  assert.equal(getRouteBounds([]), null)
  assert.equal(getRouteBounds([[[NaN, 31], [121, Infinity], [500, 31]]]), null)
  assert.equal(renderTrackSVG(''), '')
  assert.equal(renderTrackSVG(polyline.encode([[46, 6]])), '')
})
