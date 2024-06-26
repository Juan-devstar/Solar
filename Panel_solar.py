from flask import Flask, render_template, request
import math
import os

app = Flask(__name__)

def obtener_diagrama(num_paneles):
    """Obtiene el nombre del archivo del diagrama de conexión según el número de paneles."""
    if num_paneles <= 10:
        return 'conexion_10_paneles.html'
    elif num_paneles <= 20:
        return 'conexion_20_paneles.html'
    else:
        return 'conexion_default.html'

def calcular_potencia_total(dispositivos):
    """Calcula la potencia total necesaria en kWh"""
    potencia_total_kwh = 0
    for dispositivo in dispositivos:
        consumo_watt = dispositivo['consumo'] * dispositivo['cantidad']
        horas_uso = dispositivo['horas_uso']
        potencia_total_kwh += (consumo_watt / 1000) * horas_uso
    return potencia_total_kwh

def calcular_potencia_panel_solar(max_potencia_panel=0.55):
    """Calcula la potencia de cada panel solar en kW y la cantidad de paneles necesarios"""
    irradiacion_solar = 5.0  # Promedio de horas solares pico
    eficiencia_panel = 0.15  # Ejemplo de eficiencia del 15%
    area_panel = 1.6  # Área de un panel en m²

    # Calcular la potencia del panel, limitada por max_potencia_panel
    potencia_panel_kw = min(area_panel * eficiencia_panel * irradiacion_solar, max_potencia_panel)
    return potencia_panel_kw

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calcular', methods=['POST'])
def calcular():
    location = request.form['location']
    dispositivos = []

    # Obtener datos de los dispositivos del formulario
    for key, value in request.form.items():
        if key.startswith('dispositivo_'):
            nombre = key.split('_')[1]
            consumo = float(request.form[f'consumo_{nombre}'])
            cantidad = int(request.form[f'cantidad_{nombre}'])
            horas_uso = float(request.form[f'horas_uso_{nombre}'])
            dispositivos.append({
                'nombre': nombre,
                'consumo': consumo,
                'cantidad': cantidad,
                'horas_uso': horas_uso
            })

    # Calcular la potencia total en kWh
    potencia_total_kwh = calcular_potencia_total(dispositivos)

    # Calcular la potencia de cada panel solar y la cantidad de paneles necesarios
    potencia_panel_kw = calcular_potencia_panel_solar()
    num_paneles = math.ceil(potencia_total_kwh / potencia_panel_kw)

    result_text = {
        'location': location,
        'dispositivos': dispositivos,
        'potencia_total_kwh': potencia_total_kwh,
        'potencia_panel_kw': potencia_panel_kw,
        'num_paneles': num_paneles
    }

    return render_template('result.html', result=result_text)

@app.route('/simular', methods=['POST'])
def simular():
    num_paneles = request.form.get('num_paneles', type=int)

    # Obtener el nombre del archivo del diagrama de conexión según el número de paneles
    nombre_diagrama = obtener_diagrama(num_paneles)

    # Verificar si el archivo existe en el directorio de diagramas
    path_diagrama = os.path.join(app.root_path, 'static', 'diagramas_conexion', nombre_diagrama)
    if os.path.exists(path_diagrama):
        return render_template('diagramas_conexion/' + nombre_diagrama)
    else:
        # Si no se encuentra, redirigir a una página de error o manejar como sea necesario
        return render_template('error.html', mensaje='Diagrama no encontrado.')

if __name__ == '__main__':
    app.run(debug=True)
