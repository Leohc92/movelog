import polyline from '@mapbox/polyline'

type Bounds = [[number, number], [number, number]]

/** Bounds for every valid [longitude, latitude] point in the supplied routes. */
export function getRouteBounds(routes: Iterable<Iterable<readonly number[]>>): Bounds | null {
  let west = Infinity, south = Infinity, east = -Infinity, north = -Infinity
  for (const route of routes) {
    for (const [lng, lat] of route) {
      if (!Number.isFinite(lng) || !Number.isFinite(lat) || Math.abs(lng) > 180 || Math.abs(lat) > 90) continue
      west = Math.min(west, lng)
      south = Math.min(south, lat)
      east = Math.max(east, lng)
      north = Math.max(north, lat)
    }
  }
  return west === Infinity ? null : [[west, south], [east, north]]
}

/** Build a bounded-size thumbnail while keeping the complete track for maps. */
export function renderTrackSVG(summaryPolyline: string, size = 80): string {
  try {
    const coords = polyline.decode(summaryPolyline)
    if (coords.length < 2) return ''
    let minLat = Infinity, maxLat = -Infinity, minLng = Infinity, maxLng = -Infinity
    for (const [lat, lng] of coords) {
      minLat = Math.min(minLat, lat)
      maxLat = Math.max(maxLat, lat)
      minLng = Math.min(minLng, lng)
      maxLng = Math.max(maxLng, lng)
    }
    const latRange = maxLat - minLat || 0.001
    const lngRange = maxLng - minLng || 0.001
    const scale = Math.min((size - 8) / lngRange, (size - 8) / latRange)
    const offsetX = (size - lngRange * scale) / 2
    const offsetY = (size - latRange * scale) / 2
    const count = Math.min(coords.length, 2000)
    const points: string[] = []
    for (let i = 0; i < count; i++) {
      const [lat, lng] = coords[Math.round(i * (coords.length - 1) / (count - 1))]
      const x = (lng - minLng) * scale + offsetX
      const y = size - ((lat - minLat) * scale + offsetY)
      points.push(`${x.toFixed(1)},${y.toFixed(1)}`)
    }
    return points.join(' ')
  } catch {
    return ''
  }
}
