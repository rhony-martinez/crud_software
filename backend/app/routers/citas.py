from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.models import Cita, Medico
from app.schemas import CitaIn, CitaOut

router = APIRouter(prefix="/citas", tags=["citas"])
DbSession = Annotated[Session, Depends(get_db)]
DUPLICATE_SLOT_DETAIL = "Ya existe una cita para este médico en esa fecha y hora"


def obtener_medico_o_error(medico_id: int, db: Session) -> Medico:
    medico = db.get(Medico, medico_id)
    if medico is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Médico no encontrado",
        )
    return medico


def validar_horario_disponible(
    medico_id: int,
    fecha_hora: datetime,
    db: Session,
    cita_id: int | None = None,
) -> None:
    consulta = select(Cita.id).where(
        Cita.medico_id == medico_id,
        Cita.fecha_hora == fecha_hora,
    )
    if cita_id is not None:
        consulta = consulta.where(Cita.id != cita_id)

    if db.scalar(consulta) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=DUPLICATE_SLOT_DETAIL,
        )


@router.get("", response_model=list[CitaOut])
def listar_citas(db: DbSession):
    consulta = (
        select(Cita)
        .options(selectinload(Cita.medico))
        .order_by(Cita.fecha_hora, Cita.id)
    )
    return db.scalars(consulta).all()


@router.post("", response_model=CitaOut, status_code=status.HTTP_201_CREATED)
def crear_cita(datos: CitaIn, db: DbSession):
    medico = obtener_medico_o_error(datos.medico_id, db)
    validar_horario_disponible(datos.medico_id, datos.fecha_hora, db)
    cita = Cita(**datos.model_dump(exclude={"medico_id"}), medico=medico)
    db.add(cita)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        if db.get(Medico, datos.medico_id) is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Médico no encontrado",
            ) from None
        validar_horario_disponible(datos.medico_id, datos.fecha_hora, db)
        raise
    db.refresh(cita)
    return cita


@router.get("/{cita_id}", response_model=CitaOut)
def obtener_cita(cita_id: Annotated[int, Path(gt=0)], db: DbSession):
    consulta = (
        select(Cita)
        .options(selectinload(Cita.medico))
        .where(Cita.id == cita_id)
    )
    cita = db.scalar(consulta)
    if cita is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cita no encontrada",
        )
    return cita


@router.put("/{cita_id}", response_model=CitaOut)
def actualizar_cita(
    datos: CitaIn,
    cita_id: Annotated[int, Path(gt=0)],
    db: DbSession,
):
    cita = db.get(Cita, cita_id)
    if cita is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cita no encontrada",
        )
    medico = obtener_medico_o_error(datos.medico_id, db)
    validar_horario_disponible(
        datos.medico_id,
        datos.fecha_hora,
        db,
        cita_id=cita_id,
    )

    cita.medico = medico
    cita.paciente = datos.paciente
    cita.fecha_hora = datos.fecha_hora
    cita.motivo = datos.motivo
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        if db.get(Medico, datos.medico_id) is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Médico no encontrado",
            ) from None
        validar_horario_disponible(
            datos.medico_id,
            datos.fecha_hora,
            db,
            cita_id=cita_id,
        )
        raise
    db.refresh(cita)
    return cita


@router.delete("/{cita_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_cita(cita_id: Annotated[int, Path(gt=0)], db: DbSession) -> Response:
    cita = db.get(Cita, cita_id)
    if cita is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cita no encontrada",
        )
    db.delete(cita)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
