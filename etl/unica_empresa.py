import sys
from load import obtener_apicalls_por_mes_anio, obtener_apicalls_por_anio, obtener_apicalls_historico, obtener_comercios

def seleccionar_opcion(prompt, opciones_validas):
    """Solicita una opción válida dentro de un conjunto de opciones con validación."""
    while True:
        try:
            opcion = int(input(prompt))
            if opcion in opciones_validas:
                return opcion
            print(f"❌ Error: Opción no válida. Debe ser una de {opciones_validas}.")
        except ValueError:
            print("❌ Error: Debe ingresar un número válido.")

def solicitar_mes():
    """Solicita un mes válido (1-12)."""
    while True:
        try:
            mes = int(input("➡️ Ingrese el mes (1-12): "))
            if 1 <= mes <= 12:
                return mes
            print("❌ Error: El mes debe estar entre 1 y 12.")
        except ValueError:
            print("❌ Error: Debe ingresar un número válido.")

def solicitar_anio():
    """Solicita un año válido."""
    while True:
        try:
            anio = int(input("➡️ Ingrese el año (ejemplo: 2024): "))
            if anio >= 1900:
                return anio
            print("❌ Error: Año no válido.")
        except ValueError:
            print("❌ Error: Debe ingresar un número válido.")

def main():
    print("📌 Por favor seleccione la forma de facturación.")
    print("0. Mes/Año específico")
    print("1. Año específico")
    print("2. Todo el histórico")

    forma_facturacion = seleccionar_opcion("➡️ Ingrese su elección: ", {0, 1, 2})

    anio, mes = None, None
    if forma_facturacion == 0:
        mes = solicitar_mes()
        anio = solicitar_anio()
        print(f"📅 Facturación seleccionada para: {mes}/{anio}")
    elif forma_facturacion == 1:
        anio = solicitar_anio()
        print(f"📅 Facturación seleccionada para el año: {anio}")
    else:
        print("📜 Facturación para todo el histórico seleccionada.")

    print("\n📌 Seleccione las empresas que desea facturar:")
    print("0. Todas las empresas Activas")
    print("1. Todas las empresas Inactivas")
    print("2. Seleccionar empresa")
    print("3. Seleccionar varias empresas")

    tipo_facturacion = seleccionar_opcion("➡️ Ingrese su elección: ", {0, 1, 2, 3})

    comercios = obtener_comercios()
    print("\n📊 DataFrame de Comercios obtenidos:")
    print(comercios)

    comercios_seleccionados = []

    if tipo_facturacion in {2, 3}:
        print("\n🏢 Lista de empresas disponibles:")
        for idx, row in comercios.iterrows():
            print(f"{idx}. {row['commerce_name']}")

        if tipo_facturacion == 2:
            empresa_idx = seleccionar_opcion("➡️ Seleccione una empresa por su índice: ", set(range(len(comercios))))
            comercios_seleccionados.append(comercios.iloc[empresa_idx]["commerce_id"])
            print(f"✅ Empresa seleccionada: {comercios.iloc[empresa_idx]['commerce_name']}")
        else:
            while True:
                indices = input("➡️ Seleccione los índices separados por espacio: ").split()
                try:
                    indices = [int(i) for i in indices]
                    if all(i in range(len(comercios)) for i in indices):
                        comercios_seleccionados = [comercios.iloc[i]["commerce_id"] for i in indices]
                        print(f"✅ Empresas seleccionadas: {[comercios.iloc[i]['commerce_name'] for i in indices]}")
                        break
                    print("❌ Error: Uno o más índices no son válidos.")
                except ValueError:
                    print("❌ Error: Debe ingresar números separados por espacio.")

    print("\n⚙️ Procesando facturación según selección...")

    df_facturacion = []
    for commerce_id in comercios_seleccionados:
        if forma_facturacion == 0:
            df = obtener_apicalls_por_mes_anio(anio, mes, commerce_id)
        elif forma_facturacion == 1:
            df = obtener_apicalls_por_anio(anio, commerce_id)
        else:
            df = obtener_apicalls_historico(commerce_id)
        
        print(f"\n📊 DataFrame generado para comercio ID {commerce_id}:")
        print(df)

        df_facturacion.append(df)

    print("✅ Datos obtenidos y almacenados en DataFrames.")
    print("\n📊 Todos los DataFrames generados:")
    for dataframe in df_facturacion:
        print(dataframe)

if __name__ == "__main__":
    main()
