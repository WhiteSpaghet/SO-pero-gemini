// frontend/src/App.jsx
import { useState, useEffect } from 'react'
import axios from 'axios'
import './App.css' // Puedes usar el estilo por defecto o borrarlo

function App() {
  const [tareas, setTareas] = useState([])
  const [nuevoTitulo, setNuevoTitulo] = useState("")

  // URL de tu Backend
  const API_URL = "http://127.0.0.1:8000"

  // 1. Función para cargar datos desde Python
  const cargarTareas = async () => {
    try {
      const respuesta = await axios.get(`${API_URL}/tareas`)
      setTareas(respuesta.data)
    } catch (error) {
      console.error("Error cargando tareas:", error)
    }
  }

  // 2. Función para enviar datos a Python
  const manejarEnvio = async (e) => {
    e.preventDefault() // Evita que la página se recargue
    if (!nuevoTitulo) return

    try {
      await axios.post(`${API_URL}/tareas`, {
        titulo: nuevoTitulo,
        completada: false
      })
      setNuevoTitulo("") // Limpiar input
      cargarTareas()     // Recargar la lista para ver el cambio
    } catch (error) {
      console.error("Error creando tarea:", error)
    }
  }

  // Se ejecuta automáticamente al abrir la página
  useEffect(() => {
    cargarTareas()
  }, [])

  return (
    <div style={{ maxWidth: '600px', margin: '0 auto', padding: '20px', fontFamily: 'sans-serif' }}>
      <h1>Gestor de Tareas (React + Python)</h1>

      {/* Formulario */}
      <form onSubmit={manejarEnvio} style={{ display: 'flex', gap: '10px', marginBottom: '20px' }}>
        <input 
          type="text" 
          value={nuevoTitulo}
          onChange={(e) => setNuevoTitulo(e.target.value)}
          placeholder="Escribe una nueva tarea..."
          style={{ flex: 1, padding: '10px', fontSize: '16px' }}
        />
        <button type="submit" style={{ padding: '10px 20px', cursor: 'pointer' }}>
          Agregar
        </button>
      </form>

      {/* Lista */}
      <div style={{ background: '#f4f4f4', padding: '20px', borderRadius: '8px' }}>
        {tareas.length === 0 ? <p>Cargando tareas...</p> : (
          <ul style={{ listStyle: 'none', padding: 0 }}>
            {tareas.map((tarea) => (
              <li key={tarea.id} style={{ 
                background: 'white', 
                margin: '10px 0', 
                padding: '10px', 
                borderLeft: tarea.completada ? '5px solid green' : '5px solid orange',
                display: 'flex',
                justifyContent: 'space-between'
              }}>
                <span>{tarea.titulo}</span>
                <small>{tarea.completada ? "Hecho" : "Pendiente"}</small>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}

export default App