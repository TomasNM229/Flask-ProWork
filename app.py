import cx_Oracle
import sys

from flask import Flask, jsonify, request

# Configruación para MacOS (Wilmar)
if sys.platform.startswith("darwin"):
    cx_Oracle.init_oracle_client(lib_dir="/Volumes/instantclient-basic-macos.x64-19.8.0.0.0dbru")
# cd /Volumes/instantclient-basic-macos.x64-19.8.0.0.0dbru
# ./install_ic.sh

app = Flask(__name__)

def establecerConexion():
    """
    Establece conexión con base de datos
    """
    # IMPORTANTE: Es recomendable que los siguientes valores se establezcan como variables de ambiente, y se recuperen de esa manera
    conexion = cx_Oracle.connect(user="GINNET01", password="GINNET2024", dsn="38.253.155.235:1521/bdginnet", encoding="UTF-8")
    return conexion

@app.route('/')
def indice():
    """
    Muestra mensaje de bienvenida en página principal
    
    """
    
    return("ProWorkAPI")

@app.route('/personal', methods=['POST'])
def validarCredenciales() -> jsonify:
    """
    Valida datos para inicio de sesión
    """
    try:
        conexion = establecerConexion()
    except Exception:
        return jsonify({'error': conexion, 'mensaje': "Error conectando a la base de datos", 'exito': False})
    personal = None
    try:
        data = request.get_json()
        if data['ID_PERSONAL'] == '' or data['ID_INSTITUCION'] == '' or data['PASSWORD'] == '' :
            return jsonify({'mensaje': "Datos incompletos", 'exito': False})
        with conexion.cursor() as cursor:
                cursor.callproc('PRO_WORK.PERSONALMOSTRAR', [data.get('ID_PERSONAL'), data.get('ID_INSTITUCION'), data.get('PASSWORD')])
                for results in cursor.getimplicitresults():
                    for row in results:
                        personal = {'ID_PERSONAL': row[0],
                                    'NOMBRE': row[1],
                                    'APELLIDO_PATERNO': row[2],
                                    'APELLIDO_MATERNO': row[3],
                                    'CARGO': row[4],
                                    'AREA': row[5],
                                    'CORREO': row[6],
                                    'TELEFONO': row[7],
                                    'ID_TIPO_TRABAJADOR': row[8],
                                    'ID_INSTITUCION': row[9]}
                if personal:
                    return jsonify({'datos': personal, 'mensaje': "Ok", 'exito': True})
                else:
                    return jsonify({'mensaje': "Datos incorrectos", 'exito': False})
    except Exception:
        return jsonify({'mensaje': "Error en el procedimiento", 'exito': False})

@app.route('/parametros/<ID_INSTITUCION>/<ID_PERSONAL>', methods=['GET'])
def listarParametrosPorInstitucionPersonal(ID_INSTITUCION: str, ID_PERSONAL: str) -> jsonify:
    """
    Listar tabla Parametros
    """
    try:
        conexion = establecerConexion()
    except Exception:
        return jsonify({'error': conexion, 'mensaje': "Error conectando a la base de datos", 'exito': False})
    parametros = None
    try:
        with conexion.cursor() as cursor:
            cursor.callproc('PRO_WORK.INSTITUCION_PARAMETROMOSTRAR', [ID_INSTITUCION, ID_PERSONAL])
            for results in cursor.getimplicitresults():
                for row in results:
                    print(row)
                    parametros = {'VERIFICACION_EVENTO_MINUTOS': row[0],
                                  'HORA_INICIO_REFRIGERIO_PRG': row[1],
                                  'HORA_FIN_REFRIGERIO_PRG': row[2],
                                  'ACTUALIZACION_MINUTOS_IMPRODUCTIVOS': row[3],
                                  'VERIFICACION_PROGRAMA_MINUTOS': row[4],
                                  'VERIFICACION_AVANCE_MINUTOS': row[5]}
            if parametros:
                return jsonify({'datos': parametros, 'mensaje': "Ok", 'exito': True})
            else:
                return jsonify({'mensaje': "Error iniciando la aplicación", 'exito': False})
    except Exception:
        return jsonify({'mensaje': "Error con los datos", 'exito': False})

@app.route('/programas/<ID_PERSONAL>', methods=['GET'])
def listarProgramas(ID_PERSONAL: str) -> jsonify:
    """
    Listar tabla Programas
    """
    try:
        conexion = establecerConexion()
    except Exception:
        return jsonify({'error': conexion, 'mensaje': "Error conectando a la base de datos", 'exito': False})
    programas = []
    temp = None
    try:
        with conexion.cursor() as cursor:
            cursor.callproc('PRO_WORK.PERSONA_HERRAMIENTASMOSTRAR', [ID_PERSONAL])
            for results in cursor.getimplicitresults():
                for row in results:
                    temp = {'HERRAMIENTA': row[0]}
                    programas.append(temp)
            return jsonify({'datos': programas, 'mensaje': "Ok", 'exito': True})
    except Exception:
        return jsonify({'mensaje': "Error al recopilar datos", 'exito': False})

@app.route('/asistencia/inicia/<ID_PERSONAL>', methods=['PUT'])
def actualizarAsistenciaInicia(ID_PERSONAL: str) -> jsonify:
    """
    Establece hora inicio
    """
    try:
        conexion = establecerConexion()
    except Exception:
        return jsonify({'error': conexion, 'mensaje': "Error conectando a la base de datos", 'exito': False})
    try:
        with conexion.cursor() as cursor:
            cursor.callproc('PRO_WORK.ASISTENCIAINICIAR', [ID_PERSONAL])
            conexion.commit()
            return jsonify({'mensaje': "Ok", 'exito': True})
    except Exception:
        return jsonify({'mensaje': "Error inicializando jornada", 'exito': False})

@app.route('/asistencia/finaliza/<ID_PERSONAL>', methods=['PUT'])
def actualizarAsistenciaFinaliza(ID_PERSONAL: str) -> jsonify:
    """
    Establece hora fin
    """
    try:
        conexion = establecerConexion()
    except Exception:
        return jsonify({'error': conexion, 'mensaje': "Error conectando a la base de datos", 'exito': False})
    try:
        with conexion.cursor() as cursor:
            cursor.callproc('PRO_WORK.ASISTENCIAFINALIZAR', [ID_PERSONAL])
            conexion.commit()
            return jsonify({'mensaje': "Ok", 'exito': True})
    except Exception:
        return jsonify({'mensaje': "Error finalizando jornada", 'exito': False})

@app.route('/justifica/<ID_INSTITUCION>', methods=['GET'])
def listarJustifica(ID_INSTITUCION: str) -> jsonify:
    """
    Listar tabla Tipo_Justifica
    """
    try:
        conexion = establecerConexion()
    except Exception:
        return jsonify({'error': conexion, 'mensaje': "Error conectando a la base de datos", 'exito': False})
    justificaciones = []
    temp = None
    try:
        with conexion.cursor() as cursor:
            cursor.callproc('PRO_WORK.PERSONA_JUSTIFICACIONMOSTRAR', [ID_INSTITUCION])
            for results in enumerate(cursor.getimplicitresults()):
                for row in results[1]:
                    temp = {'ID_JUSTIFICACION': row[0],
                            'DESCRIPCION': row[1],
                            'MINUTOS_JUSTIFICADOS': row[2]}
                    justificaciones.append(temp)
            return jsonify({'datos': justificaciones, 'mensaje': "Ok", 'exito': True})
    except Exception:
        return jsonify({'mensaje': "Error al recopilar datos", 'exito': False})

@app.route('/evento', methods=['POST'])
def grabarEvento() -> jsonify:
    """
    Crea evento
    """
    try:
        conexion = establecerConexion()
    except Exception:
        return jsonify({'error': conexion, 'mensaje': "Error conectando a la base de datos", 'exito': False})

    try:
        with conexion.cursor() as cursor:
            cursor.callproc('PRO_WORK.PERSONAL_EVENTO_DIAGUARDAR', list(request.json.values()))
            conexion.commit()
            return jsonify({'mensaje': "Ok", 'exito': True})
    except Exception as e:
        print(e)
        return jsonify({'mensaje': "Error al grabar evento", 'exito': False})

@app.route('/minutos/improductivos/<ID_PERSONAL>/<VALOR>', methods=['PUT'])
def actualizarMinutosImproductivos(ID_PERSONAL:str, VALOR: int) -> jsonify:
    """
    Actualiza minutos improductvos establecidos en parametros
    """
    try:
        conexion = establecerConexion()
    except Exception:
        return jsonify({'error': conexion, 'mensaje': "Error conectando a la base de datos", 'exito': False})
    try:
        with conexion.cursor() as cursor:
            cursor.callproc('PRO_WORK.ACTUALIZAMINUTOSIMPRODUCTIVOS', [ID_PERSONAL, VALOR])
            conexion.commit()
            return jsonify({'mensaje': "Ok", 'exito': True})
    except Exception:
        return jsonify({'mensaje': "Error actualizando minutos improductivos", 'exito': False})

@app.route('/refrigerio/inicia/<ID_PERSONAL>', methods=['PUT'])
def actualizarRefrigerioInicia(ID_PERSONAL: str) -> jsonify:
    """
    Establece hora inicio de refrigerio
    """
    try:
        conexion = establecerConexion()
    except Exception:
        return jsonify({'error': conexion, 'mensaje': "Error conectando a la base de datos", 'exito': False})
    try:
        with conexion.cursor() as cursor:
            cursor.callproc('PRO_WORK.REFRIGERIOINICIAR', [ID_PERSONAL])
            conexion.commit()
            return jsonify({'mensaje': "Ok", 'exito': True})
    except Exception:
        return jsonify({'mensaje': "Error inicializando refrigerio", 'exito': False})

@app.route('/refrigerio/finaliza/<ID_PERSONAL>', methods=['PUT'])
def actualizarRefrigerioFinaliza(ID_PERSONAL: str) -> jsonify:
    """
    Establece hora fin de refrigerio
    """
    try:
        conexion = establecerConexion()
    except Exception:
        return jsonify({'error': conexion, 'mensaje': "Error conectando a la base de datos", 'exito': False})
    try:
        with conexion.cursor() as cursor:
            cursor.callproc('PRO_WORK.REFRIGERIOFINALIZAR', [ID_PERSONAL])
            conexion.commit()
            return jsonify({'mensaje': "Ok", 'exito': True})
    except Exception:
        return jsonify({'mensaje': "Error finalizando refrigerio", 'exito': False})

if __name__ == "__main__":
    app.run(debug=True)
