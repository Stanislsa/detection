"""
Router pour la gestion des profils personnes.

CRUD personnes surveillées.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import crud, schemas, models
from backend.dependencies import get_db

router = APIRouter()


@router.get("/", response_model=List[schemas.Person])
async def get_profiles(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Récupère la liste de toutes les personnes surveillées.
    
    Args:
        skip: Nombre d'éléments à sauter (pagination)
        limit: Nombre maximum d'éléments à retourner
        db: Session de base de données
    
    Returns:
        Liste des personnes
    """
    persons = crud.get_persons(db, skip=skip, limit=limit)
    return persons


@router.get("/{person_id}", response_model=schemas.Person)
async def get_profile(person_id: int, db: Session = Depends(get_db)):
    """
    Récupère une personne par son ID.
    
    Args:
        person_id: ID de la personne
        db: Session de base de données
    
    Returns:
        Personne demandée
    
    Raises:
        HTTPException: Si la personne n'existe pas
    """
    person = crud.get_person(db, person_id)
    if person is None:
        raise HTTPException(status_code=404, detail="Personne non trouvée")
    return person


@router.post("/", response_model=schemas.Person, status_code=status.HTTP_201_CREATED)
async def create_profile(person: schemas.PersonCreate, db: Session = Depends(get_db)):
    """
    Crée une nouvelle personne surveillée.
    
    Args:
        person: Données de la personne à créer
        db: Session de base de données
    
    Returns:
        Personne créée
    """
    return crud.create_person(db, person)


@router.put("/{person_id}", response_model=schemas.Person)
async def update_profile(
    person_id: int,
    person: schemas.PersonUpdate,
    db: Session = Depends(get_db)
):
    """
    Met à jour une personne surveillée.
    
    Args:
        person_id: ID de la personne
        person: Nouvelles données de la personne
        db: Session de base de données
    
    Returns:
        Personne mise à jour
    
    Raises:
        HTTPException: Si la personne n'existe pas
    """
    updated_person = crud.update_person(db, person_id, person)
    if updated_person is None:
        raise HTTPException(status_code=404, detail="Personne non trouvée")
    return updated_person


@router.delete("/{person_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile(person_id: int, db: Session = Depends(get_db)):
    """
    Supprime une personne surveillée.
    
    Args:
        person_id: ID de la personne
        db: Session de base de données
    
    Raises:
        HTTPException: Si la personne n'existe pas
    """
    success = crud.delete_person(db, person_id)
    if not success:
        raise HTTPException(status_code=404, detail="Personne non trouvée")


@router.get("/{person_id}/falls", response_model=List[schemas.FallEvent])
async def get_person_falls(
    person_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Récupère l'historique des chutes d'une personne.
    
    Args:
        person_id: ID de la personne
        skip: Nombre d'éléments à sauter (pagination)
        limit: Nombre maximum d'éléments à retourner
        db: Session de base de données
    
    Returns:
        Liste des chutes de la personne
    
    Raises:
        HTTPException: Si la personne n'existe pas
    """
    person = crud.get_person(db, person_id)
    if person is None:
        raise HTTPException(status_code=404, detail="Personne non trouvée")
    
    falls = crud.get_fall_events_by_person(db, person_id, skip=skip, limit=limit)
    return falls
