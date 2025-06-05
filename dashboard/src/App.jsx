import { useState, useCallback } from 'react'
import { MapContainer, TileLayer, useMapEvents } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import './App.css'

// Fix for default markers
delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
})

const API_BASE_URL = 'https://kelpie-carbon.onrender.com'

function DrawingController({ onPolygonComplete }) {
  const [isDrawing, setIsDrawing] = useState(false)
  const [currentPoints, setCurrentPoints] = useState([])
  const [drawnLayers, setDrawnLayers] = useState([])

  const map = useMapEvents({
    click(e) {
      if (!isDrawing) return
      
      const newPoint = [e.latlng.lat, e.latlng.lng]
      const newPoints = [...currentPoints, newPoint]
      setCurrentPoints(newPoints)
      
      // Add marker for the point
      const marker = L.marker(newPoint).addTo(map)
      setDrawnLayers(prev => [...prev, marker])
      
      // Draw line segments
      if (newPoints.length > 1) {
        const polyline = L.polyline([newPoints[newPoints.length - 2], newPoint], {
          color: 'blue',
          weight: 2
        }).addTo(map)
        setDrawnLayers(prev => [...prev, polyline])
      }
    },
    
    dblclick(e) {
      if (!isDrawing || currentPoints.length < 3) return
      
      // Complete the polygon
      const polygon = L.polygon(currentPoints, {
        color: 'green',
        fillColor: 'lightgreen',
        fillOpacity: 0.3
      }).addTo(map)
      
      setDrawnLayers(prev => [...prev, polygon])
      
      // Convert to WKT format
      const wktCoords = currentPoints.map(point => `${point[1]} ${point[0]}`).join(', ')
      const wkt = `POLYGON((${wktCoords}, ${currentPoints[0][1]} ${currentPoints[0][0]}))`
      
      onPolygonComplete(wkt, currentPoints)
      setIsDrawing(false)
      setCurrentPoints([])
    }
  })

  const startDrawing = () => {
    clearAll()
    setIsDrawing(true)
    setCurrentPoints([])
  }

  const clearAll = () => {
    drawnLayers.forEach(layer => map.removeLayer(layer))
    setDrawnLayers([])
    setIsDrawing(false)
    setCurrentPoints([])
  }

  return (
    <div className="drawing-controls">
      <button 
        onClick={startDrawing} 
        disabled={isDrawing}
        className={isDrawing ? 'drawing' : ''}
      >
        {isDrawing ? 'Drawing... (double-click to finish)' : 'Draw Polygon'}
      </button>
      <button onClick={clearAll}>Clear</button>
    </div>
  )
}

function EnhancedControls({ useRealLandsat, setUseRealLandsat, includeMap, setIncludeMap, mapType, setMapType }) {
  return (
    <div className="enhanced-controls">
      <div className="control-group">
        <label className="control-label">
          <input
            type="checkbox"
            checked={useRealLandsat}
            onChange={(e) => setUseRealLandsat(e.target.checked)}
          />
          🛰️ Try Real Landsat Data
        </label>
        <small>Attempts to use actual Landsat imagery instead of synthetic data</small>
      </div>
      
      <div className="control-group">
        <label className="control-label">
          <input
            type="checkbox"
            checked={includeMap}
            onChange={(e) => setIncludeMap(e.target.checked)}
          />
          🗺️ Generate Result Map
        </label>
        <small>Creates a visual map of the analysis results</small>
      </div>
      
      {includeMap && (
        <div className="control-group">
          <label className="control-label">Map Type:</label>
          <select 
            value={mapType} 
            onChange={(e) => setMapType(e.target.value)}
            className="map-type-select"
          >
            <option value="geojson">📊 GeoJSON (Data)</option>
            <option value="static">🖼️ Static Image</option>
            <option value="interactive">🌐 Interactive</option>
          </select>
        </div>
      )}
    </div>
  )
}

function CarbonResults({ results, loading, error }) {
  if (loading) {
    return (
      <div className="results-panel loading">
        <h3>🔄 Analyzing Carbon Sequestration...</h3>
        <p>Processing with enhanced features...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="results-panel error">
        <h3>❌ Analysis Error</h3>
        <p>{error}</p>
      </div>
    )
  }

  if (!results) {
    return (
      <div className="results-panel">
        <h3>🌊 Kelp Carbon Analysis</h3>
        <p>Draw a polygon on the map to analyze kelp biomass and carbon sequestration potential.</p>
        <p><strong>Enhanced Features:</strong> Real Landsat data integration and result mapping available!</p>
      </div>
    )
  }

  const formatNumber = (num) => {
    if (num >= 1000000) return `${(num / 1000000).toFixed(2)}M`
    if (num >= 1000) return `${(num / 1000).toFixed(2)}K`
    return num.toFixed(2)
  }

  const getDataSourceIcon = (source) => {
    switch(source) {
      case 'landsat_real': return '🛰️'
      case 'synthetic': return '🧮'
      default: return '❓'
    }
  }

  const getDataSourceLabel = (source) => {
    switch(source) {
      case 'landsat_real': return 'Real Landsat Data'
      case 'synthetic': return 'Synthetic Data'
      default: return 'Unknown Source'
    }
  }

  return (
    <div className="results-panel success">
      <h3>🌿 Enhanced Carbon Analysis Results</h3>
      
      {/* Data Source Information */}
      <div className="data-source-info">
        <span className="data-source-badge">
          {getDataSourceIcon(results.data_source)} {getDataSourceLabel(results.data_source)}
        </span>
        {results.landsat_metadata && results.landsat_metadata.error && (
          <small className="metadata-note">
            Note: {results.landsat_metadata.error}
          </small>
        )}
        {results.landsat_metadata && results.landsat_metadata.scene_id && (
          <small className="metadata-note">
            Scene: {results.landsat_metadata.scene_id}
          </small>
        )}
      </div>
      
      <div className="result-grid">
        <div className="result-item">
          <div className="result-label">Area</div>
          <div className="result-value">{formatNumber(results.area_m2)} m²</div>
        </div>
        
        <div className="result-item">
          <div className="result-label">FAI Index</div>
          <div className="result-value">{results.mean_fai.toFixed(3)}</div>
        </div>
        
        <div className="result-item">
          <div className="result-label">NDRE Index</div>
          <div className="result-value">{results.mean_ndre.toFixed(3)}</div>
        </div>
        
        <div className="result-item highlight">
          <div className="result-label">Kelp Biomass</div>
          <div className="result-value">{formatNumber(results.biomass_t)} tonnes</div>
        </div>
        
        <div className="result-item highlight">
          <div className="result-label">CO₂ Sequestered</div>
          <div className="result-value">{formatNumber(results.co2e_t)} tonnes CO₂e</div>
        </div>
        
        {/* Enhanced Fields */}
        <div className="result-item">
          <div className="result-label">Biomass Density</div>
          <div className="result-value">{formatNumber(results.biomass_density_t_ha)} t/ha</div>
        </div>
        
        <div className="result-item">
          <div className="result-label">Analysis Date</div>
          <div className="result-value">{results.date}</div>
        </div>
      </div>
      
      {/* Result Map Display */}
      {results.result_map && (
        <div className="result-map-section">
          <h4>📍 Result Map</h4>
          {results.result_map.success ? (
            <div className="map-result">
              {results.result_map.type === 'static_map' && results.result_map.image_base64 && (
                <div className="static-map">
                  <img 
                    src={`data:image/png;base64,${results.result_map.image_base64}`}
                    alt="Carbon Analysis Map"
                    className="result-map-image"
                  />
                </div>
              )}
              
              {results.result_map.type === 'interactive_map' && results.result_map.html && (
                <div className="interactive-map">
                  <iframe
                    srcDoc={results.result_map.html}
                    className="result-map-iframe"
                    title="Interactive Carbon Analysis Map"
                  />
                </div>
              )}
              
              {results.result_map.type === 'geojson_map' && results.result_map.geojson && (
                <div className="geojson-map">
                  <details>
                    <summary>📊 GeoJSON Data</summary>
                    <pre className="geojson-data">
                      {JSON.stringify(results.result_map.geojson, null, 2)}
                    </pre>
                  </details>
                </div>
              )}
            </div>
          ) : (
            <div className="map-error">
              <p>⚠️ Map generation failed: {results.result_map.error}</p>
            </div>
          )}
        </div>
      )}
      
      <div className="carbon-impact">
        <p>💡 <strong>Impact:</strong> This kelp forest sequesters the equivalent of CO₂ from approximately {Math.round(results.co2e_t / 4.6)} passenger cars for one year.</p>
        <p>🌱 <strong>Density:</strong> {formatNumber(results.biomass_density_t_ha)} tonnes of biomass per hectare.</p>
      </div>
    </div>
  )
}

function App() {
  const [carbonResults, setCarbonResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [analysisDate, setAnalysisDate] = useState(new Date().toISOString().split('T')[0])
  
  // Enhanced API options
  const [useRealLandsat, setUseRealLandsat] = useState(true)
  const [includeMap, setIncludeMap] = useState(true)
  const [mapType, setMapType] = useState('geojson')

  const analyzeCarbonSequestration = useCallback(async (wkt, points) => {
    setLoading(true)
    setError(null)
    
    try {
      const params = new URLSearchParams({
        date: analysisDate,
        aoi: wkt,
        use_real_landsat: useRealLandsat.toString(),
        include_map: includeMap.toString(),
        map_type: mapType
      })
      
      const response = await fetch(`${API_BASE_URL}/carbon?${params}`)
      
      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || `HTTP ${response.status}`)
      }
      
      const data = await response.json()
      setCarbonResults(data)
    } catch (err) {
      console.error('Carbon analysis error:', err)
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [analysisDate, useRealLandsat, includeMap, mapType])

  // Victoria, BC coordinates
  const victoriaCenter = [48.4284, -123.3656]

  return (
    <div className="app">
      <header className="app-header">
        <h1>🌊 Kelpie Carbon Dashboard</h1>
        <p>Enhanced kelp biomass estimation with real Landsat data and result mapping</p>
      </header>

      <div className="app-content">
        <div className="map-section">
          <div className="map-controls">
            <div className="date-control">
              <label htmlFor="analysis-date">Analysis Date:</label>
              <input
                id="analysis-date"
                type="date"
                value={analysisDate}
                onChange={(e) => setAnalysisDate(e.target.value)}
                max={new Date().toISOString().split('T')[0]}
              />
            </div>
            
            <EnhancedControls
              useRealLandsat={useRealLandsat}
              setUseRealLandsat={setUseRealLandsat}
              includeMap={includeMap}
              setIncludeMap={setIncludeMap}
              mapType={mapType}
              setMapType={setMapType}
            />
          </div>

          <MapContainer 
            center={victoriaCenter} 
            zoom={11} 
            style={{ height: '500px', width: '100%' }}
            className="map-container"
          >
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
            
            <DrawingController onPolygonComplete={analyzeCarbonSequestration} />
          </MapContainer>
        </div>

        <div className="results-section">
          <CarbonResults 
            results={carbonResults} 
            loading={loading} 
            error={error}
          />
        </div>
      </div>

      <footer className="app-footer">
        <p>
          Enhanced with real Landsat data via Microsoft Planetary Computer • 
          <a href={`${API_BASE_URL}/docs`} target="_blank" rel="noopener noreferrer"> API Documentation</a>
        </p>
      </footer>
    </div>
  )
}

export default App
