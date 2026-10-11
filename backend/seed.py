from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import select

from app.database import Base, SessionLocal, engine
from app.models import Cita, Medico

load_dotenv(Path(__file__).resolve().parent / ".env")

MEDICOS = [
    {
        "nombre": "Laura Gómez",
        "especialidad": "Medicina general",
        "correo": "laura.gomez@clinica.test",
    },
    {
        "nombre": "Andrés Ruiz",
        "especialidad": "Pediatría",
        "correo": "andres.ruiz@clinica.test",
    },
    {
        "nombre": "Sofía Mejía",
        "especialidad": "Dermatología",
        "correo": "sofia.mejia@clinica.test",
    },
]

CITAS = [
    {
        "paciente": "Camila Torres",
        "correo_medico": "laura.gomez@clinica.test",
        "fecha_hora": datetime.fromisoformat("2026-10-12T09:00:00"),
        "motivo": "Control general",
    },
    {
        "paciente": "Mateo Rojas",
        "correo_medico": "andres.ruiz@clinica.test",
        "fecha_hora": datetime.fromisoformat("2026-10-12T10:30:00"),
        "motivo": "Vacunación",
    },
    {
        "paciente": "Valeria Ortiz",
        "correo_medico": "sofia.mejia@clinica.test",
        "fecha_hora": datetime.fromisoformat("2026-10-13T08:00:00"),
        "motivo": "Revisión de piel",
    },
    {
        "paciente": "Daniel Peña",
        "correo_medico": "laura.gomez@clinica.test",
        "fecha_hora": datetime.fromisoformat("2026-10-13T11:00:00"),
        "motivo": "Dolor de cabeza",
    },
]


def cargar_datos() -> None:
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as db, db.begin():
        medicos_por_correo = {}
        for datos_medico in MEDICOS:
            medico = db.scalar(
                select(Medico).where(Medico.correo == datos_medico["correo"])
            )
            if medico is None:
                medico = Medico(**datos_medico)
                db.add(medico)
                db.flush()
            medicos_por_correo[medico.correo] = medico

        for datos_cita in CITAS:
            medico = medicos_por_correo[datos_cita["correo_medico"]]
            cita_existente = db.scalar(
                select(Cita.id).where(
                    Cita.medico_id == medico.id,
                    Cita.paciente == datos_cita["paciente"],
                    Cita.fecha_hora == datos_cita["fecha_hora"],
                )
            )
            if cita_existente is None:
                db.add(
                    Cita(
                        medico=medico,
                        paciente=datos_cita["paciente"],
                        fecha_hora=datos_cita["fecha_hora"],
                        motivo=datos_cita["motivo"],
                    )
                )


if __name__ == "__main__":
    cargar_datos()
    print("Datos de prueba cargados.")
