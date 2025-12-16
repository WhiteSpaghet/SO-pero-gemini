import React, { useState, useEffect } from 'react'
import axios from 'axios'

// --- CONFIGURACIÓN VISUAL ---
const API_URL = "http://127.0.0.1:8000"
const mapSize = 500;
const scale = 5;

export default function App() {
  // Estado global de la simulación
  const [taxis, setTaxis] = useState([])
  const [infoEmpresa, setInfoEmpresa] = useState({ ganancia: 0, viajes: 0 })
  
  // Estado de la Interfaz (Roles)
  const [rolActual, setRolActual] = useState('ADMIN') // ADMIN, TAXI, CLIENTE
  const [mensaje, setMensaje] = useState("Sistema iniciado.")
  
  // Estados específicos para roles
  const [miIdTaxi, setMiIdTaxi] = useState(null) // Para simular que soy un taxi específico
  const [miIdCliente, setMiIdCliente] = useState(1) // ID simulado de cliente

  // --- MOTOR DE ACTUALIZACIÓN (POLLING) ---
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
        console.error("Conectando con servidor...")
      }
    }, 500)
    return () => clearInterval(intervalo)
  }, [])

  // --- ACCIONES ---

  const registrarTaxi = async () => {
    try {
      const res = await axios.post(`${API_URL}/taxis`, {
        modelo: "Toyota",
        placa: `ABC-${Math.floor(Math.random() * 999)}`
      })
      setMensaje(`Admin: Taxi ${res.data.id} creado con éxito.`)
    } catch (e) {
      setMensaje("Error: Taxi rechazado por antecedentes.")
    }
  }

  const solicitarViaje = async () => {
    setMensaje("Cliente: Buscando taxi...")
    try {
      const res = await axios.post(`${API_URL}/solicitar_viaje`, {
        cliente_id: miIdCliente,
        origen_x: Math.random() * 100,
        origen_y: Math.random() * 100,
        destino_x: Math.random() * 100,
        destino_y: Math.random() * 100
      })
      
      if (res.data.taxi_id) {
        setMensaje(`Cliente: ¡Taxi asignado! Viene el ${res.data.modelo} (#${res.data.taxi_id})`)
      } else {
        setMensaje(`Cliente: ${res.data.resultado}`)
      }
    } catch (e) {
      setMensaje("Error de conexión.")
    }
  }

  // --- VISTAS POR ROL (COMPONENTES) ---

  const VistaAdmin = () => (
    <div style={panelStyle}>
      <h3>👮‍♂️ Panel de Administración</h3>
      <p>Control total del sistema UNIE TAXI.</p>
      
      <div style={statBox}>
        <p>Ganancia Total: <strong>${infoEmpresa.ganancia}</strong></p>
        <p>Viajes Totales: <strong>{infoEmpresa.viajes}</strong></p>
        <p>Taxis Activos: <strong>{taxis.length}</strong></p>
      </div>

      <button onClick={registrarTaxi} style={{...btnStyle, background: '#007bff'}}>
        ➕ Contratar Nuevo Taxi
      </button>
      
      <p style={{fontSize: '12px', color: '#666'}}>
        *El Admin puede ver la ubicación de todos en el mapa.
      </p>
    </div>
  )

  const VistaCliente = () => (
    <div style={panelStyle}>
      <h3>🙋‍♂️ App de Cliente</h3>
      <p>Bienvenido. ¿A dónde quieres ir hoy?</p>
      
      <div style={{marginBottom: 20}}>
        <label>Tu ID de Usuario:</label>
        <input 
          type="number" 
          value={miIdCliente} 
          onChange={(e) => setMiIdCliente(e.target.value)}
          style={{width: '50px', marginLeft: 10}}
        />
      </div>

      <button onClick={solicitarViaje} style={{...btnStyle, background: '#28a745'}}>
        🚕 Solicitar Viaje Ahora
      </button>

      <div style={{marginTop: 20, padding: 10, background: '#e9ffe9', border: '1px solid #b2d8b2'}}>
        <strong>Estado:</strong> {mensaje}
      </div>
    </div>
  )

  const VistaTaxista = () => {
    // Buscamos los datos de "MI" taxi en la lista general
    const miTaxiDatos = taxis.find(t => t.id === parseInt(miIdTaxi))

    return (
      <div style={panelStyle}>
        <h3>🚖 App de Conductor</h3>
        
        <div style={{marginBottom: 15}}>
          <label>Soy el Taxi ID: </label>
          <select onChange={(e) => setMiIdTaxi(e.target.value)} value={miIdTaxi || ''}>
            <option value="">Seleccionar...</option>
            {taxis.map(t => <option key={t.id} value={t.id}>Taxi #{t.id} ({t.modelo})</option>)}
          </select>
        </div>

        {miTaxiDatos ? (
          <div style={statBox}>
            <p>Estado: <strong style={{color: miTaxiDatos.estado === 'LIBRE' ? 'green' : 'red'}}>{miTaxiDatos.estado}</strong></p>
            <p>Mis Ganancias: <strong>${miTaxiDatos.ganancias.toFixed(2)}</strong></p>
            <p>Placa: <strong>{miTaxiDatos.placa}</strong></p>
            <p>Calif: <strong>⭐ {miTaxiDatos.calificacion}</strong></p>
            {miTaxiDatos.estado === 'OCUPADO' && (
               <div style={{marginTop: 10, padding: 5, background: '#fff3cd'}}>
                 ⚠️ <strong>¡CLIENTE A BORDO!</strong><br/>
                 Conduciendo al destino...
               </div>
            )}
          </div>
        ) : (
          <p style={{color: '#666'}}>Selecciona tu ID arriba para ver tus estadísticas y ganancias.</p>
        )}
      </div>
    )
  }

  // --- RENDERIZADO PRINCIPAL ---
  return (
    <div style={{ fontFamily: 'Arial', padding: '20px', maxWidth: '900px', margin: '0 auto' }}>
      
      {/* HEADER CON PESTAÑAS */}
      <div style={{ display: 'flex', gap: '10px', marginBottom: '20px', borderBottom: '2px solid #ccc', paddingBottom: '10px' }}>
        <button onClick={() => setRolActual('ADMIN')} style={rolActual === 'ADMIN' ? tabActive : tabInactive}>👮‍♂️ ADMIN</button>
        <button onClick={() => setRolActual('CLIENTE')} style={rolActual === 'CLIENTE' ? tabActive : tabInactive}>🙋‍♂️ CLIENTE</button>
        <button onClick={() => setRolActual('TAXI')} style={rolActual === 'TAXI' ? tabActive : tabInactive}>🚖 TAXISTA</button>
      </div>

      <div style={{ display: 'flex', gap: '20px' }}>
        
        {/* COLUMNA IZQUIERDA: CAMBIA SEGÚN EL ROL */}
        <div style={{ width: '350px' }}>
          {rolActual === 'ADMIN' && <VistaAdmin />}
          {rolActual === 'CLIENTE' && <VistaCliente />}
          {rolActual === 'TAXI' && <VistaTaxista />}
          
          {/* Log global pequeño */}
          <div style={{marginTop: 20, fontSize: 12, color: '#999'}}>
            Log Global: {mensaje}
          </div>
        </div>

        {/* COLUMNA DERECHA: MAPA (Siempre visible para ver la simulación) */}
        <div style={{ position: 'relative', width: mapSize, height: mapSize, background: '#eee', border: '3px solid #333' }}>
          <span style={{position:'absolute', top: 5, left: 5, color: '#888', fontWeight: 'bold'}}>
            MAPA DE LA CIUDAD (Vista Satelital)
          </span>
          
          {taxis.map(taxi => (
            <div 
              key={taxi.id}
              style={{
                position: 'absolute',
                left: taxi.x * scale, 
                top: taxi.y * scale,
                width: '18px',
                height: '18px',
                background: taxi.estado === 'LIBRE' ? '#28a745' : '#dc3545',
                borderRadius: '50%',
                border: miIdTaxi == taxi.id && rolActual === 'TAXI' ? '3px solid blue' : '2px solid white', // Resaltar mi taxi
                boxShadow: '0 2px 5px rgba(0,0,0,0.3)',
                transition: 'all 0.5s linear',
                zIndex: miIdTaxi == taxi.id ? 100 : 1
              }}
              title={`Taxi ${taxi.id}`}
            >
              {/* Si soy taxista, muestro mi número encima */}
              {rolActual === 'TAXI' && miIdTaxi == taxi.id && 
                <span style={{position:'absolute', top:-20, left:-10, background:'blue', color:'white', padding:'2px 5px', borderRadius:4, fontSize:10}}>Yo</span>
              }
            </div>
          ))}
        </div>

      </div>
    </div>
  )
}

// --- ESTILOS CSS EN JS ---
const panelStyle = { border: '1px solid #ddd', padding: '20px', borderRadius: '8px', background: '#f9f9f9', height: '100%' }
const statBox = { background: 'white', padding: '15px', borderRadius: '5px', border: '1px solid #eee', marginBottom: '15px' }
const btnStyle = { width: '100%', padding: '12px', color: 'white', border: 'none', borderRadius: '5px', cursor: 'pointer', fontSize: '16px', fontWeight: 'bold' }
const tabActive = { padding: '10px 20px', cursor: 'pointer', background: '#333', color: 'white', border: 'none', borderRadius: '5px 5px 0 0', fontWeight: 'bold' }
const tabInactive = { padding: '10px 20px', cursor: 'pointer', background: '#eee', color: '#666', border: 'none', borderRadius: '5px 5px 0 0' }