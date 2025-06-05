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

const API_BASE_URL = 'http://localhost:8000'

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

function CarbonResults({ results, loading, error }) {
  if (loading) {
    return (
      <div className="results-panel loading">
        <h3>🔄 Analyzing Carbon Sequestration...</h3>
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
      </div>
    )
  }

  const formatNumber = (num) => {
    if (num >= 1000000) return `${(num / 1000000).toFixed(2)}M`
    if (num >= 1000) return `${(num / 1000).toFixed(2)}K`
    return num.toFixed(2)
  }

  return (
    <div className="results-panel success">
      <h3>🌿 Carbon Analysis Results</h3>
      
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
        
        <div className="result-item">
          <div className="result-label">Analysis Date</div>
          <div className="result-value">{results.date}</div>
        </div>
      </div>
      
      <div className="carbon-impact">
        <p>💡 <strong>Impact:</strong> This kelp forest sequesters the equivalent of CO₂ from approximately {Math.round(results.co2e_t / 4.6)} passenger cars for one year.</p>
      </div>
    </div>
  )
}

function App() {
  const [carbonResults, setCarbonResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [analysisDate, setAnalysisDate] = useState(new Date().toISOString().split('T')[0])

  const analyzeCarbonSequestration = useCallback(async (wkt, points) => {
    setLoading(true)
    setError(null)
    
    try {
      const params = new URLSearchParams({
        date: analysisDate,
        aoi: wkt
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
  }, [analysisDate])

  // Victoria, BC coordinates
  const victoriaCenter = [48.4284, -123.3656]

  return (
    <div className="app">
      <header className="app-header">
        <h1>🌊 Kelpie Carbon Dashboard</h1>
        <p>Interactive kelp biomass estimation and carbon sequestration analysis</p>
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
          Powered by Sentinel-2 satellite imagery • 
          <a href={`${API_BASE_URL}/docs`} target="_blank" rel="noopener noreferrer"> API Documentation</a>
        </p>
      </footer>
    </div>
  )
}

export default App
