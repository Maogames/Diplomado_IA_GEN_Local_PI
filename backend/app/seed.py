"""Carga datos SINTÉTICOS de prueba (usuarios, inventario y préstamos de ejemplo).

Uso:  python -m app.seed            (crea tablas y datos si la base está vacía)
      python -m app.seed --reiniciar (borra todo y vuelve a cargar)

Todas las cuentas de prueba usan la contraseña  Demo1234!
No ejecutar en producción: el script se niega si LAB_ENTORNO=produccion.
"""

import random
import sys
from datetime import timedelta

from sqlalchemy import select

from .config import get_settings
from .database import Base, SessionLocal, engine
from .models import (
    Categoria,
    Elemento,
    EstadoPrestamo,
    Prestamo,
    PrestamoDetalle,
    Rol,
    TipoMovimiento,
    Usuario,
)
from .security import hash_password
from .services.inventario import aplicar_movimiento
from .tiempo import ahora, hoy_local

CLAVE_DEMO = "Demo1234!"

USUARIOS = [
    ("Administrador del Sistema", "admin@lab.test", Rol.admin, None, None),
    ("Coordinación de Laboratorios", "coordinacion@lab.test", Rol.coordinador, None, None),
    ("Carlos Muñoz (Técnico)", "tecnico@lab.test", Rol.tecnico, None, "+573000000001"),
    ("Laura Gómez (Técnica)", "tecnico2@lab.test", Rol.tecnico, None, None),
    ("Ing. Patricia Ordóñez", "docente@lab.test", Rol.docente, None, "+573000000002"),
    ("Ing. Javier Castillo", "docente2@lab.test", Rol.docente, None, None),
    ("Ana Sofía Rivera", "estudiante@lab.test", Rol.estudiante, "2021100101", "+573000000003"),
    ("Miguel Ángel Paz", "estudiante2@lab.test", Rol.estudiante, "2021100102", None),
    ("Valentina Erazo", "estudiante3@lab.test", Rol.estudiante, "2022100205", None),
    ("Santiago Bolaños", "estudiante4@lab.test", Rol.estudiante, "2022100231", None),
]

# (categoría, [(código, nombre, descripción, ubicación, cantidad, mínimo, consumible)])
CATALOGO = {
    "Microcontroladores y tarjetas": [
        ("MCU-001", "Arduino UNO R3", "Tarjeta ATmega328P con cable USB", "Estante A1", 20, 5, False),
        ("MCU-002", "ESP32 DevKit V1", "Wi-Fi + Bluetooth, 38 pines", "Estante A1", 15, 4, False),
        ("MCU-003", "Raspberry Pi 4 (4 GB)", "Incluye fuente USB-C y microSD 32 GB", "Gabinete G1", 6, 2, False),
        ("MCU-004", "Arduino Mega 2560", "Tarjeta ATmega2560", "Estante A1", 8, 2, False),
        ("MCU-005", "STM32 Nucleo-F401RE", "Tarjeta de desarrollo ARM Cortex-M4", "Estante A2", 5, 1, False),
    ],
    "Instrumentos de medición": [
        ("MED-001", "Multímetro digital UNI-T UT33D", "Voltaje, corriente, resistencia, continuidad", "Gabinete G2", 12, 3, False),
        ("MED-002", "Osciloscopio digital 2 canales 100 MHz", "Con 2 sondas x1/x10", "Mesa de instrumentos", 4, 1, False),
        ("MED-003", "Generador de funciones", "Senoidal, cuadrada y triangular hasta 20 MHz", "Mesa de instrumentos", 3, 1, False),
        ("MED-004", "Fuente de poder DC regulable 0-30 V / 5 A", "Doble salida", "Mesa de instrumentos", 6, 2, False),
        ("MED-005", "Pinza amperimétrica", "AC/DC hasta 400 A", "Gabinete G2", 3, 1, False),
        ("MED-006", "Analizador lógico 8 canales", "USB, 24 MHz", "Gabinete G2", 4, 1, False),
    ],
    "Herramientas manuales": [
        ("HER-001", "Cautín 60 W con base", "Temperatura regulable", "Estante B1", 10, 3, False),
        ("HER-002", "Pinza de punta", "Mango aislado", "Estante B1", 15, 4, False),
        ("HER-003", "Pinza peladora de cable", "Calibres 10-22 AWG", "Estante B1", 10, 3, False),
        ("HER-004", "Juego de destornilladores de precisión", "32 puntas", "Estante B2", 8, 2, False),
        ("HER-005", "Extractor de soldadura", "Tipo pistón", "Estante B1", 8, 2, False),
        ("HER-006", "Ponchadora RJ45", "Para cable UTP cat 5e/6", "Estante B2", 6, 2, False),
    ],
    "Componentes y módulos": [
        ("COM-001", "Protoboard 830 puntos", "Con cables jumper", "Cajonera C1", 30, 8, False),
        ("COM-002", "Módulo sensor ultrasónico HC-SR04", None, "Cajonera C2", 25, 5, False),
        ("COM-003", "Módulo relé 2 canales 5 V", None, "Cajonera C2", 15, 4, False),
        ("COM-004", "Servomotor SG90", None, "Cajonera C3", 20, 5, False),
        ("COM-005", "Pantalla LCD 16x2 con I2C", None, "Cajonera C3", 12, 3, False),
        ("COM-006", "Sensor de temperatura y humedad DHT22", None, "Cajonera C2", 18, 4, False),
        ("COM-007", "Driver de motores L298N", None, "Cajonera C3", 10, 3, False),
    ],
    "Redes y cómputo": [
        ("RED-001", "Switch administrable 8 puertos", "Gigabit, VLAN", "Rack R1", 4, 1, False),
        ("RED-002", "Router inalámbrico de práctica", "Doble banda", "Rack R1", 5, 1, False),
        ("RED-003", "Probador de cable de red", "RJ45 / RJ11", "Estante B2", 5, 2, False),
        ("RED-004", "Portátil de laboratorio", "Core i5, 16 GB RAM, Ubuntu", "Gabinete G3", 8, 2, False),
    ],
    "Material consumible": [
        ("CON-001", "Soldadura de estaño 60/40 (rollo 100 g)", None, "Cajonera C4", 20, 5, True),
        ("CON-002", "Resistencias surtidas (kit 600 u.)", None, "Cajonera C4", 10, 3, True),
        ("CON-003", "Cable UTP cat 6 (metro)", None, "Rack R1", 150, 30, True),
        ("CON-004", "Conectores RJ45 (bolsa 50 u.)", None, "Estante B2", 12, 3, True),
        ("CON-005", "Cables jumper macho-macho (paquete 40 u.)", None, "Cajonera C1", 25, 6, True),
        ("CON-006", "LEDs 5 mm surtidos (bolsa 100 u.)", None, "Cajonera C4", 8, 2, True),
    ],
}

PRACTICAS = [
    "Electrónica Digital - Práctica 3: Contadores",
    "Sistemas Embebidos - Lab 2: Sensores",
    "Redes de Computadores - Lab 4: VLAN",
    "Circuitos Eléctricos - Práctica 5: Ley de Ohm",
    "Internet de las Cosas - Proyecto de aula",
    "Robótica - Taller de servomotores",
]


def cargar(reiniciar: bool = False) -> None:
    if get_settings().entorno == "produccion":
        raise SystemExit("El seed de datos sintéticos no se ejecuta en producción.")
    if reiniciar:
        Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    rnd = random.Random(42)
    with SessionLocal() as db:
        if db.scalar(select(Usuario).limit(1)):
            print("La base ya tiene datos. Use --reiniciar para recargar.")
            return

        clave = hash_password(CLAVE_DEMO)
        usuarios = {}
        for nombre, email, rol, codigo, tel in USUARIOS:
            u = Usuario(nombre=nombre, email=email, rol=rol, codigo_institucional=codigo,
                        telefono_whatsapp=tel, password_hash=clave)
            db.add(u)
            usuarios[email] = u
        db.flush()
        tecnico = usuarios["tecnico@lab.test"]

        elementos: list[Elemento] = []
        for nombre_cat, items in CATALOGO.items():
            cat = Categoria(nombre=nombre_cat)
            db.add(cat)
            db.flush()
            for codigo, nombre, desc, ubic, cant, minimo, consumible in items:
                e = Elemento(codigo=codigo, nombre=nombre, descripcion=desc, categoria_id=cat.id, ubicacion=ubic,
                             stock_minimo=minimo, es_consumible=consumible, cantidad_total=0, cantidad_disponible=0)
                db.add(e)
                db.flush()
                aplicar_movimiento(db, e, TipoMovimiento.entrada, cant, tecnico, motivo="Inventario inicial (sintético)")
                elementos.append(e)

        prestables = [e for e in elementos if not e.es_consumible]
        consumibles = [e for e in elementos if e.es_consumible]
        estudiantes = [u for u in usuarios.values() if u.rol == Rol.estudiante]
        docentes = [u for u in usuarios.values() if u.rol == Rol.docente]
        hoy = hoy_local()

        # Escenarios: (estado final, días desde la solicitud, días de plazo)
        escenarios = (
            [(EstadoPrestamo.devuelto, rnd.randint(10, 40), 7) for _ in range(10)]
            + [(EstadoPrestamo.entregado, rnd.randint(1, 4), 7) for _ in range(4)]
            + [(EstadoPrestamo.entregado, rnd.randint(12, 20), 5) for _ in range(3)]  # vencidos
            + [(EstadoPrestamo.aprobado, 1, 5) for _ in range(2)]
            + [(EstadoPrestamo.pendiente, 0, 5) for _ in range(4)]
            + [(EstadoPrestamo.rechazado, 6, 5), (EstadoPrestamo.cancelado, 3, 5)]
        )
        for estado, hace, plazo in escenarios:
            solicitado = ahora() - timedelta(days=hace, hours=rnd.randint(0, 8))
            p = Prestamo(
                solicitante_id=rnd.choice(estudiantes).id,
                docente_responsable_id=rnd.choice(docentes).id,
                practica=rnd.choice(PRACTICAS),
                fecha_devolucion_prevista=hoy - timedelta(days=hace) + timedelta(days=plazo),
                canal=rnd.choice(["web", "web", "whatsapp"]),
                creado_en=solicitado,
            )
            for e in rnd.sample(prestables, rnd.randint(1, 3)):
                p.detalles.append(PrestamoDetalle(elemento=e, cantidad=rnd.randint(1, 2)))
            db.add(p)
            db.flush()

            if estado in (EstadoPrestamo.aprobado, EstadoPrestamo.entregado, EstadoPrestamo.devuelto,
                          EstadoPrestamo.rechazado):
                p.aprobado_por_id = p.docente_responsable_id
                p.aprobado_en = solicitado + timedelta(hours=2)
            if estado == EstadoPrestamo.rechazado:
                p.motivo_rechazo = "La práctica fue reprogramada."
            if estado in (EstadoPrestamo.entregado, EstadoPrestamo.devuelto):
                for d in p.detalles:
                    aplicar_movimiento(db, d.elemento, TipoMovimiento.prestamo, d.cantidad, tecnico,
                                       motivo=f"Entrega del préstamo #{p.id}", prestamo_id=p.id)
                p.entregado_por_id = tecnico.id
                p.entregado_en = solicitado + timedelta(hours=3)
            if estado == EstadoPrestamo.devuelto:
                for d in p.detalles:
                    aplicar_movimiento(db, d.elemento, TipoMovimiento.devolucion, d.cantidad, tecnico,
                                       motivo=f"Devolución del préstamo #{p.id}", prestamo_id=p.id)
                p.recibido_por_id = tecnico.id
                p.devuelto_en = solicitado + timedelta(days=rnd.randint(2, 6))
            p.estado = estado

        for e in rnd.sample(consumibles, 4):
            aplicar_movimiento(db, e, TipoMovimiento.salida, max(1, e.cantidad_disponible // 3), tecnico,
                               motivo="Consumo en prácticas de la semana")
        # Un consumible queda bajo el mínimo para que aparezca en las alertas.
        led = next(e for e in consumibles if e.codigo == "CON-006")
        aplicar_movimiento(db, led, TipoMovimiento.salida, led.cantidad_disponible - 1, tecnico,
                           motivo="Consumo en proyecto de aula")

        db.commit()
        print(f"Datos sintéticos cargados: {len(usuarios)} usuarios, {len(elementos)} elementos, "
              f"{len(escenarios)} préstamos.")
        print(f"Contraseña de todas las cuentas de prueba: {CLAVE_DEMO}")
        for _, email, rol, _, _ in USUARIOS:
            print(f"  {rol.value:<12} {email}")


if __name__ == "__main__":
    cargar(reiniciar="--reiniciar" in sys.argv)
