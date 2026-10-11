from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Cita, Medico
from app.schemas import MedicoIn, MedicoOut

router = APIRouter(prefix="/medicos", tags=["medicos"])
DbSession = Annotated[Session, Depends(get_db)]


@router.get("", response_model=list[MedicoOut])
def listar_medicos(db: DbSession):
    return db.scalars(select(Medico).order_by(Medico.id)).all()


@router.post("", response_model=MedicoOut, status_code=status.HTTP_201_CREATED)
def crear_medico(datos: MedicoIn, db: DbSession):
    medico = Medico(**datos.model_dump())
    db.add(medico)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un médico con ese correo",
        ) from None
    db.refresh(medico)
    return medico


@router.get("/{medico_id}", response_model=MedicoOut)
def obtener_medico(medico_id: Annotated[int, Path(gt=0)], db: DbSession):
    medico = db.get(Medico, medico_id)
    if medico is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Médico no encontrado",
        )
    return medico


@router.put("/{medico_id}", response_model=MedicoOut)
def actualizar_medico(
    datos: MedicoIn,
    medico_id: Annotated[int, Path(gt=0)],
    db: DbSession,
):
    medico = db.get(Medico, medico_id)
    if medico is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Médico no encontrado",
        )

    medico_existente = db.scalar(
        select(Medico.id).where(
            Medico.correo == datos.correo,
            Medico.id != medico_id,
        )
    )
    if medico_existente is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un médico con ese correo",
        )

    for campo, valor in datos.model_dump().items():
        setattr(medico, campo, valor)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un médico con ese correo",
        ) from None
    db.refresh(medico)
    return medico


@router.delete("/{medico_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_medico(
    medico_id: Annotated[int, Path(gt=0)],
    db: DbSession,
) -> Response:
    medico = db.get(Medico, medico_id)
    if medico is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Médico no encontrado",
        )

    tiene_citas = db.scalar(
        select(Cita.id).where(Cita.medico_id == medico_id).limit(1)
    )
    if tiene_citas is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se puede eliminar un médico con citas",
        )

    db.delete(medico)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se puede eliminar un médico con citas",
        ) from None
    return Response(status_code=status.HTTP_204_NO_CONTENT)
