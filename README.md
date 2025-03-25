# ETL Facturación de API
 
Este repositorio esta dedicado a la prueba técnica para la vacante de Ecosistemas de Bancolombia desarrollado en la versión de Python 3.12.3, se trata de un sistema de facturación de una API y permite a los usuarios seleccionar empresas para facturación y filtrar la información por un rango de tiempo determinado.
 
---
 
## Entradas
 
### 1️⃣ Selección de empresas
Permite al usuario definir qué empresas incluir en la facturación. Se presentan cuatro opciones:
 
- **0. Todas las empresas Activas** → Se seleccionan todas las empresas activas en la base de datos.
- **1. Todas las empresas Inactivas** → Se seleccionan todas las empresas inactivas.
- **2. Seleccionar una empresa** → Muestra una lista de empresas y permite elegir una específica.
- **3. Seleccionar varias empresas** → Muestra una lista de empresas y permite elegir varias ingresando los números correspondientes separados por espacios.
 
### 2️⃣ Filtrado por fecha
Filtra los registros de llamadas (`apicall`) según el rango de fechas definido por el usuario. Se presentan tres opciones:
 
- **0. Año/Mes** → Filtra los datos por un año y mes específicos.
- **1. Año** → Filtra todos los datos de un año en particular.
- **2. Todo el histórico** → No se aplica ningún filtro de fecha, usando todos los registros.
 
---
## Funcionamiento
 
### **Proceso**
1. Se construye una consulta SQL con filtros según la opción elegida.
2. Se ejecuta la consulta sobre la base de datos.
3. Se devuelve un `DataFrame` con los registros filtrados.
4. Se realiza el proceso de transformación de los datos.
5. Se guarda un excel con la factura localmente.
6. Se envía correo de la ejecución de la rutina.
 
### **Ejecución**
Para ejecutar el proyecto en Windows se debe tener instalado Python y ademas seguir los siguientes pasos.
```bash
git clone https://github.com/juan-quirozt/prueba_batsej.git
cd prueba_batsej
python -m venv venv
venv/Scripts/activate
pip install -r requirements.txt
python ejecucion.py
```

Para ejecutar los test ejecutar el siguiente comando
```bash
pytest
# O alternativamente
python -m unittest discover
```