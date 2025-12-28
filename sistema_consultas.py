"""
================================================================================
    SISTEMA DE CONSULTAS OFTALMOLÓGICAS - CLÍNICA "VISIÓN CLARA"
    Framework: Flask
    Propósito: Demo para evidencias de testing en metodologías ágiles
================================================================================
"""

from flask import Flask, render_template, request, jsonify
from datetime import datetime, timedelta
import json

app = Flask(__name__)

# Almacenamiento en memoria (simulación)
citas = []
pacientes = {
    "12345678-9": {
        "rut": "12345678-9",
        "nombre": "Juan Pérez",
        "email": "juan.perez@email.com",
        "telefono": "+56912345678",
        "historial": [
            {
                "fecha": "2025-11-15",
                "tipo": "Control de rutina",
                "diagnostico": "Miopía leve (-1.5)",
                "doctor": "Dra. María González"
            },
            {
                "fecha": "2025-10-10",
                "tipo": "Examen de vista",
                "diagnostico": "Visión normal",
                "doctor": "Dr. Carlos Soto"
            }
        ]
    },
    "98765432-1": {
        "rut": "98765432-1",
        "nombre": "Ana Silva",
        "email": "ana.silva@email.com",
        "telefono": "+56987654321",
        "historial": [
            {
                "fecha": "2025-12-01",
                "tipo": "Examen de fondo de ojo",
                "diagnostico": "Normal",
                "doctor": "Dra. María González"
            }
        ]
    }
}

doctores = [
    {"id": 1, "nombre": "Dra. María González", "especialidad": "Oftalmología General"},
    {"id": 2, "nombre": "Dr. Carlos Soto", "especialidad": "Cirugía Refractiva"},
    {"id": 3, "nombre": "Dra. Patricia Rojas", "especialidad": "Retina y Vítreo"}
]


@app.route('/')
def index():
    """Página principal del sistema"""
    return render_template('index.html')


@app.route('/api/paciente/<rut>', methods=['GET'])
def obtener_paciente(rut):
    """API: Obtiene información de un paciente por RUT"""
    if rut in pacientes:
        return jsonify(pacientes[rut])
    else:
        return jsonify({'error': 'Paciente no encontrado'}), 404


@app.route('/api/doctores', methods=['GET'])
def obtener_doctores():
    """API: Obtiene lista de doctores disponibles"""
    return jsonify(doctores)


@app.route('/api/citas', methods=['GET'])
def obtener_citas():
    """API: Obtiene todas las citas agendadas"""
    return jsonify(citas)


@app.route('/api/citas/<rut>', methods=['GET'])
def obtener_citas_paciente(rut):
    """API: Obtiene citas de un paciente específico"""
    citas_paciente = [c for c in citas if c['rut_paciente'] == rut]
    return jsonify(citas_paciente)


@app.route('/api/agendar', methods=['POST'])
def agendar_cita():
    """API: Agenda una nueva cita oftalmológica"""
    data = request.json
    
    # Validación 1: Datos requeridos
    campos_requeridos = ['rut_paciente', 'doctor_id', 'fecha', 'hora', 'tipo_consulta']
    for campo in campos_requeridos:
        if campo not in data or not data[campo]:
            return jsonify({'error': f'Campo requerido: {campo}'}), 400
    
    # Validación 2: Paciente existe
    if data['rut_paciente'] not in pacientes:
        return jsonify({'error': 'Paciente no registrado en el sistema'}), 400
    
    # Validación 3: Doctor existe
    doctor = next((d for d in doctores if d['id'] == int(data['doctor_id'])), None)
    if not doctor:
        return jsonify({'error': 'Doctor no encontrado'}), 400
    
    # Validación 4: Fecha debe ser futura
    try:
        fecha_cita = datetime.strptime(data['fecha'], '%Y-%m-%d')
        if fecha_cita.date() < datetime.now().date():
            return jsonify({'error': 'La fecha de la cita debe ser futura'}), 400
    except ValueError:
        return jsonify({'error': 'Formato de fecha inválido (usar YYYY-MM-DD)'}), 400
    
    # Validación 5: No permitir citas duplicadas (mismo paciente, fecha, hora)
    for cita in citas:
        if (cita['rut_paciente'] == data['rut_paciente'] and 
            cita['fecha'] == data['fecha'] and 
            cita['hora'] == data['hora']):
            return jsonify({'error': 'Ya existe una cita para este paciente en esta fecha y hora'}), 400
    
    # Validación 6: No permitir doble reserva del mismo doctor
    for cita in citas:
        if (cita['doctor_id'] == int(data['doctor_id']) and 
            cita['fecha'] == data['fecha'] and 
            cita['hora'] == data['hora']):
            return jsonify({'error': 'El doctor ya tiene una cita agendada en este horario'}), 400
    
    # Crear nueva cita
    paciente = pacientes[data['rut_paciente']]
    nueva_cita = {
        'id': len(citas) + 1,
        'rut_paciente': data['rut_paciente'],
        'nombre_paciente': paciente['nombre'],
        'doctor_id': int(data['doctor_id']),
        'nombre_doctor': doctor['nombre'],
        'fecha': data['fecha'],
        'hora': data['hora'],
        'tipo_consulta': data['tipo_consulta'],
        'estado': 'Agendada',
        'fecha_creacion': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    citas.append(nueva_cita)
    
    return jsonify({
        'success': True,
        'mensaje': 'Cita agendada exitosamente',
        'cita': nueva_cita
    })


@app.route('/api/cancelar/<int:cita_id>', methods=['POST'])
def cancelar_cita(cita_id):
    """API: Cancela una cita existente"""
    for cita in citas:
        if cita['id'] == cita_id:
            cita['estado'] = 'Cancelada'
            return jsonify({
                'success': True,
                'mensaje': 'Cita cancelada exitosamente'
            })
    
    return jsonify({'error': 'Cita no encontrada'}), 404


@app.route('/api/limpiar', methods=['POST'])
def limpiar_citas():
    """API: Limpia todas las citas (útil para testing)"""
    global citas
    citas = []
    return jsonify({'success': True, 'mensaje': 'Todas las citas han sido eliminadas'})


@app.route('/api/estado', methods=['GET'])
def estado_sistema():
    """API: Verifica el estado del sistema"""
    return jsonify({
        'estado': 'Operativo',
        'pacientes_registrados': len(pacientes),
        'doctores_disponibles': len(doctores),
        'citas_agendadas': len(citas),
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })


if __name__ == '__main__':
    print("="*80)
    print("SISTEMA DE CONSULTAS OFTALMOLÓGICAS - CLÍNICA VISIÓN CLARA")
    print("="*80)
    print("Servidor iniciando en: http://localhost:5000")
    print("Presiona CTRL+C para detener")
    print("="*80)
    
    app.run(debug=True, port=5000)
