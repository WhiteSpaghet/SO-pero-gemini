import React, { useState, useEffect } from 'react'
import axios from 'axios'

// Estilos simples para el mapa
const mapSize = 500; // pixeles
const scale = 5; // 1 unidad de backend = 5 pixeles

function App() {
  const [taxis, setTaxis] = useState([])
  const [infoEmpresa, setInfoEmpresa] = useState({ ganancia: 0, viajes: 0 })
  const [mensaje, setMensaje] = useState("")

  const API_URL = "http://127.0.0.1:8000"

  // --- LOOP DE ACTUALIZACIÓN (POLLING) ---
  // Pide al backend el estado cada 500ms para animar el mapa
  useEffect(() => {
    const intervalo = setInterval(async () => {
      try {
        const res = await axios.get(`${API_URL}/estado`)
        setTaxis(res.data.taxis)
        setInfoEmpresa({
          ganancia: res.data.empresa_ganancia,
          viajes: res.data.viajes
        })
      } catch (e) {
        console.error("Error conectando con backend")
      }
    }, 500)
    return () => clearInterval(intervalo)
  }, [])

  // --- FUNCIONES DE BOTONES ---

  const crearTaxi = async () => {
    try {
      await axios.post(`${API_URL}/taxis`, {
        modelo: "Toyota Corolla",
        placa: "ABC-" + Math.floor(Math.random() * 1000)
      })
      setMensaje("Taxi solicitado...")
    } catch (e) {
      setMensaje("Error: Taxi rechazado por antecedentes")
    }
  }

  const pedirViaje = async () => {
    // Generamos coordenadas aleatorias para simular un cliente
    const origenX = Math.random() * 100
    const origenY = Math.random() * 100
    const destX = Math.random() * 100
    const destY = Math.random() * 100

    try {
      const res = await axios.post(`${API_URL}/solicitar_viaje`, {
        cliente_id: 1,
        origen_x: origenX,
        origen_y: origenY,
        destino_x: destX,
        destino_y: destY
      })
      
      if (res.data.taxi) {
        setMensaje(`Viaje asignado al Taxi #${res.data.taxi.id} (${res.data.taxi.modelo})`)
      } else {
        setMensaje(res.data.resultado)
      }
    } catch (e) {
      console.error(e)
    }
  }

  return (
    <div style={{ display: 'flex', gap: '20px', padding: '20px', fontFamily: 'sans-serif' }}>
      
      {/* COLUMNA IZQUIERDA: CONTROLES */}
      <div style={{ width: '300px' }}>
        <h1 style={{ color: '#ffcc00' }}>UNIE TAXI</h1>
        
        <div style={{ marginBottom: '20px', padding: '15px', border: '1px solid #ccc', borderRadius: '8px' }}>
          <h3>Panel de Control</h3>
          <p>Ganancias Empresa: <strong>${infoEmpresa.ganancia}</strong></p>
          <p>Viajes Totales: <strong>{infoEmpresa.viajes}</strong></p>
          <hr />
          <button onClick={crearTaxi} style={btnStyle}>➕ Registrar Nuevo Taxi</button>
          <button onClick={pedirViaje} style={{...btnStyle, background: '#28a745'}}>🙋‍♂️ Cliente: Solicitar Viaje</button>
        </div>

        <div style={{ padding: '10px', background: '#f8f9fa', borderRadius: '5px' }}>
          <strong>Log del Sistema:</strong>
          <p>{mensaje}</p>
        </div>
        
        <h4>Leyenda:</h4>
        <div style={{display:'flex', alignItems:'center', gap:'10px'}}>
          <div style={{width:20, height:20, background:'green'}}></div> Taxi Libre
        </div>
        <div style={{display:'flex', alignItems:'center', gap:'10px'}}>
          <div style={{width:20, height:20, background:'red'}}></div> Taxi Ocupado
        </div>
      </div>

      {/* COLUMNA DERECHA: MAPA */}
      <div style={{ position: 'relative', width: mapSize, height: mapSize, background: '#eee', border: '2px solid #333' }}>
        <span style={{position:'absolute', top:5, left:5, color:'#999'}}>Mapa de la Ciudad (100x100km)</span>
        
        {taxis.map(taxi => (
          <div 
            key={taxi.id}
            style={{
              position: 'absolute',
              left: taxi.x * scale, // Convertimos coords a pixeles
              top: taxi.y * scale,
              width: '20px',
              height: '20px',
              background: taxi.estado === 'LIBRE' ? 'green' : 'red',
              borderRadius: '50%',
              color: 'white',
              fontSize: '10px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              transition: 'all 0.5s linear', // Animación suave
              border: '2px solid white',
              boxShadow: '0 2px 4px rgba(0,0,0,0.3)'
            }}
          >
            {taxi.id}
          </div>
        ))}
      </div>
    </div>
  )
}

const btnStyle = {
  display: 'block',
  width: '100%',
  padding: '10px',
  marginBottom: '10px',
  cursor: 'pointer',
  background: '#007bff',
  color: 'white',
  border: 'none',
  borderRadius: '5px',
  fontSize: '16px'
}

export default App