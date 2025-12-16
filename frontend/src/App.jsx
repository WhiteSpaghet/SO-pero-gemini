import React, { useState, useEffect } from 'react'
import axios from 'axios'

const API_URL = "http://127.0.0.1:8000"
const mapSize = 500;
const scale = 5;

// --- ESTILOS ---
const panelStyle = { border: '1px solid #ddd', padding: '20px', borderRadius: '8px', background: '#f9f9f9', height: '100%', display: 'flex', flexDirection: 'column' }
const statBox = { background: 'white', padding: '15px', borderRadius: '5px', border: '1px solid #eee', marginBottom: '15px' }
const btnStyle = { width: '100%', padding: '10px', color: 'white', border: 'none', borderRadius: '5px', cursor: 'pointer', fontSize: '14px', fontWeight: 'bold', marginBottom: '5px' }
const tabActive = { padding: '10px 20px', cursor: 'pointer', background: '#333', color: 'white', border: 'none', borderRadius: '5px 5px 0 0', fontWeight: 'bold' }
const tabInactive = { padding: '10px 20px', cursor: 'pointer', background: '#eee', color: '#666', border: 'none', borderRadius: '5px 5px 0 0' }

const clockContainerStyle = { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px', background: '#333', color: 'white', padding: '10px', borderRadius: '5px' }
const digitalClockStyle = { fontFamily: 'monospace', fontSize: '20px', color: '#0f0', fontWeight: 'bold', background: '#000', padding: '2px 10px', borderRadius: '3px', border: '1px solid #555' }

// --- COMPONENTES ---

const VistaAdmin = ({ infoEmpresa, taxis, mejorTaxi, registrarTaxi, eliminarTaxi, simulacionActiva, intervalo, actualizarSimulacion, taxiSeleccionado, setTaxiSeleccionado }) => {
  
  // Buscamos el objeto completo del taxi seleccionado
  const detalleTaxi = taxis.find(t => t.id === taxiSeleccionado);

  return (
    <div style={panelStyle}>
      <h3>👮‍♂️ Panel de Administración</h3>
      
      {/* 1. MOSTRAR DETALLES SI HAY UN TAXI SELECCIONADO */}
      {detalleTaxi ? (
        <div style={{background: '#e3f2fd', border: '2px solid #2196f3', padding: '15px', borderRadius: '8px', marginBottom: '15px', position: 'relative'}}>
          <button 
            onClick={() => setTaxiSeleccionado(null)}
            style={{position: 'absolute', top: 5, right: 5, background: 'transparent', border: 'none', fontSize: '16px', cursor: 'pointer', fontWeight: 'bold', color: '#666'}}
          >✕</button>
          <h4 style={{marginTop: 0, color: '#1565c0'}}>🚖 Detalles Taxi #{detalleTaxi.id}</h4>
          <div style={{fontSize: '13px', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '5px'}}>
            <span>Modelo: <strong>{detalleTaxi.modelo}</strong></span>
            <span>Placa: <strong>{detalleTaxi.placa}</strong></span>
            <span>Estado: <strong style={{color: detalleTaxi.estado === 'LIBRE' ? 'green' : 'red'}}>{detalleTaxi.estado}</strong></span>
            <span>Calif: <strong>⭐ {detalleTaxi.calificacion}</strong></span>
            <span>Viajes: <strong>{detalleTaxi.viajes}</strong></span>
            <span>Ganado: <strong>${detalleTaxi.ganancias.toFixed(2)}</strong></span>
          </div>
          <div style={{marginTop: 10, textAlign: 'center'}}>
             <button 
                onClick={() => { eliminarTaxi(detalleTaxi.id); setTaxiSeleccionado(null); }}
                disabled={detalleTaxi.estado === 'OCUPADO'}
                style={{background: '#dc3545', color: 'white', border: 'none', padding: '5px 10px', borderRadius: '3px', cursor: 'pointer', width: '100%'}}
             >
               Despedir Taxista (Eliminar)
             </button>
          </div>
        </div>
      ) : (
        <div style={statBox}>
          <p>Ganancia Total: <strong>${infoEmpresa.ganancia}</strong></p>
          <p>Viajes Totales: <strong>{infoEmpresa.viajes}</strong></p>
          
          {mejorTaxi ? (
            <div style={{background: '#fff8e1', padding: '10px', borderRadius: '5px', border: '1px solid #ffe082', marginTop: 10}}>
              <span>🏆 <strong>Empleado del Mes:</strong></span><br/>#{mejorTaxi.id} ({mejorTaxi.modelo}) - ${mejorTaxi.ganancias}
            </div>
          ) : <p style={{color: '#999', fontStyle: 'italic'}}>Sin datos.</p>}
        </div>
      )}

      {/* CONTROLES DE SIMULACIÓN */}
      <div style={{paddingTop: 10, borderTop: '1px solid #eee'}}>
        <button onClick={() => actualizarSimulacion({ activa: !simulacionActiva })} style={{...btnStyle, background: simulacionActiva ? '#6f42c1' : '#6c757d'}}>
          {simulacionActiva ? '🛑 DETENER SIMULACIÓN' : '🤖 INICIAR SIMULACIÓN AUTO'}
        </button>
        <div style={{marginTop: 10}}>
          <label style={{fontSize: 12, fontWeight: 'bold', color: '#555'}}>Velocidad Generación (segundos):</label>
          <div style={{display: 'flex', alignItems: 'center', gap: 10}}>
            <span style={{fontSize: 12}}>🚀 0.1s</span>
            <input type="range" min="0.1" max="2.0" step="0.1" value={intervalo} onChange={(e) => actualizarSimulacion({ intervalo: parseFloat(e.target.value) })} style={{flex: 1}}/>
            <span style={{fontSize: 12}}>🐢 2s</span>
          </div>
        </div>
      </div>
      
      <hr style={{margin: '10px 0', border: '0', borderTop: '1px solid #eee'}}/>
      <button onClick={registrarTaxi} style={{...btnStyle, background: '#007bff'}}>➕ Contratar Nuevo Taxi</button>
      
      {/* LISTA RESUMIDA */}
      <h4>Flota ({taxis.length})</h4>
      <div style={{flex: 1, overflowY: 'auto', border: '1px solid #eee', background: 'white', padding: '5px', borderRadius: '5px'}}>
        <ul style={{listStyle: 'none', padding: 0, margin: 0}}>
          {taxis.map(t => (
            <li 
              key={t.id} 
              onClick={() => setTaxiSeleccionado(t.id)} // CLICK EN LISTA TAMBIÉN SELECCIONA
              style={{
                display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '5px', 
                borderBottom: '1px solid #f0f0f0', fontSize: '13px', cursor: 'pointer',
                background: taxiSeleccionado === t.id ? '#e3f2fd' : 'transparent'
              }}
            >
              <span><strong>#{t.id}</strong> {t.modelo} <span style={{fontSize: 10, marginLeft: 5, color: t.estado==='LIBRE'?'green':'red'}}>({t.estado})</span></span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  )
}

const VistaCliente = ({ miIdCliente, setMiIdCliente, solicitarViaje, mensaje, clientes }) => {
  const miClienteDatos = clientes.find(c => c.id === parseInt(miIdCliente))
  return (
    <div style={panelStyle}>
      <h3>🙋‍♂️ App de Cliente</h3>
      <div style={{marginBottom: 20}}>
        <label>Tu ID:</label>
        <input type="number" min="1" value={miIdCliente} onChange={(e) => setMiIdCliente(e.target.value)} style={{width: '50px', marginLeft: 10}}/>
      </div>
      {miClienteDatos && (
        <div style={{background: '#e3f2fd', padding: '10px', borderRadius: '5px', marginBottom: '15px', border: '1px solid #90caf9'}}>
          <p style={{margin: 0, fontSize: '14px', color: '#1565c0'}}>
            👤 <strong>{miClienteDatos.nombre}</strong><br/>
            Has realizado: <strong>{miClienteDatos.viajes} viajes</strong>
          </p>
        </div>
      )}
      <button onClick={solicitarViaje} style={{...btnStyle, background: '#28a745'}}>🚕 Solicitar Viaje</button>
      <div style={{marginTop: 10, padding: 10, background: '#e9ffe9', border: '1px solid #b2d8b2', borderRadius: '5px', fontSize: '13px'}}><strong>Estado:</strong> {mensaje}</div>
    </div>
  )
}

const VistaTaxista = ({ taxis, miIdTaxi, setMiIdTaxi }) => {
  const miTaxiDatos = taxis.find(t => t.id === parseInt(miIdTaxi))
  return (
    <div style={panelStyle}>
      <h3>🚖 App de Conductor</h3>
      <div style={{marginBottom: 15}}>
        <label>Soy el Taxi ID: </label>
        <select onChange={(e) => setMiIdTaxi(e.target.value)} value={miIdTaxi || ''}><option value="">Seleccionar...</option>{taxis.map(t => <option key={t.id} value={t.id}>#{t.id} - {t.modelo}</option>)}</select>
      </div>
      {miTaxiDatos ? (
        <div style={statBox}>
          <p>Estado: <strong style={{color: miTaxiDatos.estado === 'LIBRE' ? 'green' : 'red'}}>{miTaxiDatos.estado}</strong></p>
          <p>Mis Ganancias: <strong>${miTaxiDatos.ganancias.toFixed(2)}</strong></p>
          <p>Viajes Realizados: <strong>{miTaxiDatos.viajes}</strong></p> 
          <p>Placa: <strong>{miTaxiDatos.placa}</strong></p>
          <p>Calif: <strong>⭐ {miTaxiDatos.calificacion}</strong></p>
          {miTaxiDatos.estado === 'OCUPADO' && <div style={{marginTop: 10, padding: 5, background: '#fff3cd', fontSize: 12}}>⚠️ PASAJERO A BORDO</div>}
        </div>
      ) : <p style={{color: '#666'}}>Selecciona tu ID.</p>}
    </div>
  )
}

export default function App() {
  const [taxis, setTaxis] = useState([])
  const [clientes, setClientes] = useState([]) 
  const [infoEmpresa, setInfoEmpresa] = useState({ ganancia: 0, viajes: 0 })
  const [mejorTaxi, setMejorTaxi] = useState(null)
  const [simulacionActiva, setSimulacionActiva] = useState(false)
  const [intervalo, setIntervalo] = useState(0.3) 
  const [rolActual, setRolActual] = useState('ADMIN') 
  const [mensaje, setMensaje] = useState("Sistema iniciado.")
  const [miIdTaxi, setMiIdTaxi] = useState(null)
  const [miIdCliente, setMiIdCliente] = useState(1)
  const [tiempoSimulado, setTiempoSimulado] = useState("00:00")
  
  // ESTADO NUEVO: TAXI SELECCIONADO EN MAPA
  const [taxiSeleccionado, setTaxiSeleccionado] = useState(null)

  useEffect(() => {
    const intervaloId = setInterval(async () => {
      try {
        const res = await axios.get(`${API_URL}/estado`)
        setTaxis(res.data.taxis)
        setClientes(res.data.clientes || []) 
        setInfoEmpresa({ ganancia: res.data.empresa_ganancia, viajes: res.data.viajes })
        setMejorTaxi(res.data.mejor_taxi)
        setSimulacionActiva(res.data.simulacion_activa)
        setTiempoSimulado(res.data.tiempo_simulado)
      } catch (e) { console.error("Conectando...") }
    }, 50) 
    return () => clearInterval(intervaloId)
  }, [])

  const registrarTaxi = async () => { try { await axios.post(`${API_URL}/taxis`, { modelo: "Toyota", placa: `ABC-${Math.floor(Math.random() * 999)}` }); setMensaje("Admin: Taxi creado.") } catch (e) { setMensaje("Error al crear taxi.") } }
  const eliminarTaxi = async (id) => { try { await axios.delete(`${API_URL}/taxis/${id}`); setMensaje(`Admin: Taxi ${id} eliminado.`) } catch (error) { alert("No se pudo eliminar: " + error.response.data.detail) } }
  const actualizarSimulacion = async (config) => {
    if (config.activa !== undefined) setSimulacionActiva(config.activa)
    if (config.intervalo !== undefined) setIntervalo(config.intervalo)
    try { await axios.post(`${API_URL}/simulacion/config`, config) } catch (e) { console.error(e) }
  }
  const solicitarViaje = async () => {
    setMensaje("Buscando...")
    try {
      const res = await axios.post(`${API_URL}/solicitar_viaje`, { cliente_id: miIdCliente, origen_x: Math.random()*100, origen_y: Math.random()*100, destino_x: Math.random()*100, destino_y: Math.random()*100 })
      if (res.data.taxi_id) setMensaje(`Asignado Taxi #${res.data.taxi_id}`)
      else setMensaje(res.data.resultado)
    } catch (e) { setMensaje("Error de conexión.") }
  }

  return (
    <div style={{ fontFamily: 'Arial', padding: '20px', maxWidth: '950px', margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px', borderBottom: '2px solid #ccc', paddingBottom: '10px' }}>
        <h2 style={{margin:0, color: '#d4af37'}}>UNIE TAXI</h2>
        <div style={{display:'flex', gap:'10px'}}>
          <button onClick={() => setRolActual('ADMIN')} style={rolActual === 'ADMIN' ? tabActive : tabInactive}>👮‍♂️ ADMIN</button>
          <button onClick={() => setRolActual('CLIENTE')} style={rolActual === 'CLIENTE' ? tabActive : tabInactive}>🙋‍♂️ CLIENTE</button>
          <button onClick={() => setRolActual('TAXI')} style={rolActual === 'TAXI' ? tabActive : tabInactive}>🚖 TAXISTA</button>
        </div>
      </div>
      <div style={{ display: 'flex', gap: '20px' }}>
        <div style={{ width: '350px', height: '600px' }}>
          {rolActual === 'ADMIN' && 
            <VistaAdmin 
              infoEmpresa={infoEmpresa} taxis={taxis} mejorTaxi={mejorTaxi} registrarTaxi={registrarTaxi} eliminarTaxi={eliminarTaxi} 
              simulacionActiva={simulacionActiva} intervalo={intervalo} actualizarSimulacion={actualizarSimulacion}
              // PASAMOS LOS ESTADOS AL HIJO
              taxiSeleccionado={taxiSeleccionado} setTaxiSeleccionado={setTaxiSeleccionado}
            />
          }
          {rolActual === 'CLIENTE' && <VistaCliente miIdCliente={miIdCliente} setMiIdCliente={setMiIdCliente} solicitarViaje={solicitarViaje} mensaje={mensaje} clientes={clientes} />}
          {rolActual === 'TAXI' && <VistaTaxista taxis={taxis} miIdTaxi={miIdTaxi} setMiIdTaxi={setMiIdTaxi} />}
          <div style={{marginTop: 10, fontSize: 12, color: '#999'}}>Log: {mensaje}</div>
        </div>
        <div style={{ width: mapSize }}>
          <div style={clockContainerStyle}>
             <span>MAPA DE LA CIUDAD</span>
             <div style={{display:'flex', alignItems:'center', gap:'10px'}}>
               <span style={{fontSize:12, color:'#ccc'}}>HORA SIMULADA:</span>
               <div style={digitalClockStyle}>{tiempoSimulado}</div>
             </div>
          </div>
          <div style={{ position: 'relative', width: mapSize, height: mapSize, background: '#eee', border: '3px solid #333' }}>
            {taxis.map(taxi => (
              <div 
                key={taxi.id} 
                // EVENTO CLICK: SELECCIONA EL TAXI
                onClick={() => setTaxiSeleccionado(taxi.id)}
                style={{
                  position: 'absolute', left: taxi.x * scale, top: taxi.y * scale, width: '18px', height: '18px',
                  background: taxi.estado === 'LIBRE' ? '#28a745' : '#dc3545', borderRadius: '50%',
                  // RESALTADO VISUAL: Borde Dorado si está seleccionado
                  border: taxiSeleccionado === taxi.id ? '3px solid gold' : (miIdTaxi == taxi.id && rolActual === 'TAXI' ? '3px solid blue' : '2px solid white'),
                  boxShadow: '0 2px 5px rgba(0,0,0,0.3)', transition: 'all 0.5s linear', 
                  zIndex: taxiSeleccionado === taxi.id ? 200 : (miIdTaxi == taxi.id ? 100 : 1),
                  cursor: 'pointer' // Cambia el cursor a manita
                }} 
                title={`Click para ver Taxi ${taxi.id}`}>
                {/* Etiqueta flotante si está seleccionado */}
                {taxiSeleccionado === taxi.id && <span style={{position:'absolute', top:-25, left:-15, background:'gold', color:'black', padding:'2px 5px', borderRadius:4, fontSize:10, fontWeight:'bold', whiteSpace:'nowrap'}}>#{taxi.id}</span>}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}