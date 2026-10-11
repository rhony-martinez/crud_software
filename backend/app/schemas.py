from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class MedicoIn(BaseModel):
    nombre: str = Field(min_length=2, max_length=100)
    especialidad: str = Field(min_length=2, max_length=100)
    correo: str = Field(min_length=1)


class MedicoOut(MedicoIn):
    model_config = ConfigDict(from_attributes=True)

    id: int


class MedicoResumenOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    especialidad: str


class CitaIn(BaseModel):
    medico_id: int
    paciente: str = Field(min_length=2, max_length=100)
    fecha_hora: datetime
    motivo: str | None = Field(default=None, max_length=200)

    @field_validator("fecha_hora")
    @classmethod
    def fecha_sin_zona_horaria(cls, value: datetime) -> datetime:
        if value.tzinfo is not None and value.utcoffset() is not None:
            raise ValueError("La fecha y hora no debe incluir zona horaria")
        return value


class CitaOut(CitaIn):
    model_config = ConfigDict(from_attributes=True)

    id: int
    medico: MedicoResumenOut
