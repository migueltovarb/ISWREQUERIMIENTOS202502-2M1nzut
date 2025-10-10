"""
MovieTime - Gestión de venta de boletos por consola con persistencia en CSV.

Archivos:
  - funciones.csv: codigo,pelicula,hora,precio
  - ventas.csv:    fecha_hora,codigo_funcion,cantidad,total

Requisitos cubiertos:
- Registrar funciones (película, hora, precio) con código único (ingresado o autogenerado).
- Listar funciones.
- Vender boletos con validaciones y total.
- Resumen de ventas del día (boletos y dinero).
- Persistencia en CSV, interfaz clara, validaciones básicas.
"""

import csv
import os
from datetime import datetime, date
from typing import Dict, List, Optional

FUNCIONES_CSV = "funciones.csv"
VENTAS_CSV = "ventas.csv"

# ------------------------- Utilidades de archivo -------------------------

def ensure_csv_headers():
    """Crea los CSV si no existen o fueron eliminados."""
    try:
        if not os.path.exists(FUNCIONES_CSV):
            with open(FUNCIONES_CSV, "w", newline="", encoding="utf-8") as f:
                csv.writer(f).writerow(["codigo", "pelicula", "hora", "precio"])
        if not os.path.exists(VENTAS_CSV):
            with open(VENTAS_CSV, "w", newline="", encoding="utf-8") as f:
                csv.writer(f).writerow(["fecha_hora", "codigo_funcion", "cantidad", "total"])
    except Exception as e:
        print(f"⚠️ Error asegurando CSV: {e}")

def load_funciones() -> Dict[str, Dict[str, str]]:
    """
    Retorna dict por código:
    { codigo: { "pelicula": str, "hora": str, "precio": float_str } }
    """
    ensure_csv_headers()
    funciones: Dict[str, Dict[str, str]] = {}
    with open(FUNCIONES_CSV, "r", newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            codigo = row["codigo"].strip()
            if codigo:
                funciones[codigo] = {
                    "pelicula": row["pelicula"].strip(),
                    "hora": row["hora"].strip(),
                    "precio": row["precio"].strip(),
                }
    return funciones

def save_funcion(codigo: str, pelicula: str, hora: str, precio: float):
    ensure_csv_headers()
    with open(FUNCIONES_CSV, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([codigo, pelicula, hora, f"{precio:.2f}"])

def save_venta(codigo_funcion: str, cantidad: int, total: float):
    ensure_csv_headers()
    with open(VENTAS_CSV, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        w.writerow([now, codigo_funcion, str(cantidad), f"{total:.2f}"])

def load_ventas_del_dia(hoy: date) -> List[Dict[str, str]]:
    ensure_csv_headers()
    ventas: List[Dict[str, str]] = []
    with open(VENTAS_CSV, "r", newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            # fecha_hora con formato "YYYY-MM-DD HH:MM:SS"
            try:
                dt = datetime.strptime(row["fecha_hora"], "%Y-%m-%d %H:%M:%S")
            except Exception:
                # si la fila está mal formada, la ignoramos
                continue
            if dt.date() == hoy:
                ventas.append(row)
    return ventas

# ------------------------- Lógica de negocio -------------------------

def generate_next_code(existing_codes: List[str]) -> str:
    """
    Genera próximo código tipo FUN###. Si no hay, arranca en FUN001.
    """
    prefix = "FUN"
    nmax = 0
    for c in existing_codes:
        if c.startswith(prefix):
            suf = c[len(prefix):]
            if suf.isdigit():
                nmax = max(nmax, int(suf))
    return f"{prefix}{nmax+1:03d}"

def input_nonempty(prompt: str) -> str:
    while True:
        s = input(prompt).strip()
        if s:
            return s
        print("⚠️  No puede estar vacío.")

def input_float(prompt: str, min_value: Optional[float] = None) -> float:
    while True:
        s = input(prompt).strip().replace(",", ".")
        try:
            v = float(s)
            if min_value is not None and v < min_value:
                print(f"⚠️  Debe ser un número >= {min_value}.")
                continue
            return v
        except ValueError:
            print("⚠️  Ingrese un número válido.")

def input_int(prompt: str, min_value: Optional[int] = None) -> int:
    while True:
        s = input(prompt).strip()
        try:
            v = int(s)
            if min_value is not None and v < min_value:
                print(f"⚠️  Debe ser un entero >= {min_value}.")
                continue
            return v
        except ValueError:
            print("⚠️  Ingrese un entero válido.")

def registrar_funcion():
    funciones = load_funciones()
    print("\n== Registrar nueva función ==")
    pelicula = input_nonempty("Película: ")
    hora = input_nonempty("Hora (ej. 18:30): ")
    precio = input_float("Precio del boleto: ", min_value=0.0)

    # código: usuario puede ingresar o autogenerar
    codigo = input("Código (deje vacío para autogenerar): ").strip().upper()
    if not codigo:
        codigo = generate_next_code(list(funciones.keys()))
        print(f"→ Código generado: {codigo}")
    else:
        if codigo in funciones:
            print("❌ Ya existe una función con ese código. Operación cancelada.")
            return

    save_funcion(codigo, pelicula, hora, precio)
    print(f"✅ Función '{pelicula}' registrada con código {codigo}.")

def listar_funciones():
    funciones = load_funciones()
    print("\n== Funciones disponibles ==")
    if not funciones:
        print("(no hay funciones registradas)")
        return
    # Encabezado
    print(f"{'CÓDIGO':<8}  {'PELÍCULA':<30}  {'HORA':<8}  {'PRECIO':>8}")
    print("-" * 62)
    for codigo, data in sorted(funciones.items()):
        pelicula = (data['pelicula'][:27] + '...') if len(data['pelicula']) > 30 else data['pelicula']
        hora = data['hora']
        try:
            precio = float(data['precio'])
        except ValueError:
            precio = 0.0
        print(f"{codigo:<8}  {pelicula:<30}  {hora:<8}  ${int(precio):,}".replace(",", "."))

def vender_boletos():
    funciones = load_funciones()
    if not funciones:
        print("\n❌ No hay funciones registradas. Registre una primero.")
        return

    print("\n== Vender boletos ==")
    codigo = input_nonempty("Código de la función: ").upper()
    if codigo not in funciones:
        print("❌ La función no existe. Verifique el código.")
        return

    cantidad = input_int("Cantidad de boletos: ", min_value=1)

    try:
        precio = float(funciones[codigo]["precio"])
    except ValueError:
        print("❌ Precio inválido en la función. Corrija el registro.")
        return

    total = precio * cantidad
    print(f"Total a pagar: ${int(total):,}".replace(",", "."))
    save_venta(codigo, cantidad, total)
    print("✅ Venta registrada.")

def resumen_ventas_del_dia():
    print("\n== Resumen de ventas del día ==")
    hoy = date.today()
    ventas = load_ventas_del_dia(hoy)
    if not ventas:
        print("No hay ventas registradas para hoy.")
        return

    total_boletos = 0
    total_dinero = 0.0
    for v in ventas:
        try:
            total_boletos += int(v["cantidad"])
            total_dinero += float(v["total"])
        except ValueError:
            continue

    print(f"Fecha: {hoy.isoformat()}")
    print(f"Boletos vendidos: {total_boletos}")
    print(f"Dinero recaudado: ${int(total_dinero):,}".replace(",", "."))

# ------------------------- Interfaz de usuario -------------------------

def menu():
    ensure_csv_headers()
    opciones = {
        "1": ("Registrar función", registrar_funcion),
        "2": ("Listar funciones", listar_funciones),
        "3": ("Vender boletos", vender_boletos),
        "4": ("Resumen de ventas del día", resumen_ventas_del_dia),
        "0": ("Salir", None),
    }

    while True:
        print("\n====== TaquillaCLI ======")
        for k in ["1", "2", "3", "4", "0"]:
            print(f"{k}. {opciones[k][0]}")
        op = input("Seleccione una opción: ").strip()

        if op == "0":
            print("¡Hasta luego!")
            break
        elif op in opciones:
            try:
                opciones[op][1]()  # type: ignore
            except Exception as e:
                print(f"⚠️  Ocurrió un error: {e}")
        else:
            print("Opción inválida. Intente de nuevo.")

if __name__ == "__main__":
    menu()
