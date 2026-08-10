"""
Endpoints CRUD pour les personnes surveillées.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.models.base import get_db
from app.models.person import Person
from app.schemas.person import PersonCreate, PersonRead, PersonUpdate

router = APIRouter()


@router.post("/", response_model=PersonRead, status_code=status.HTTP_201_CREATED)
def create_person(person: PersonCreate, db: Session = Depends(get_db)):
    """Crée une nouvelle personne surveillée."""
    db_person = Person(**person.dict())
    db.add(db_person)
    db.commit()
    db.refresh(db_person)
    return db_person


@router.get("/", response_model=List[PersonRead])
def list_persons(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Liste les personnes surveillées."""
    return db.query(Person).offset(skip).limit(limit).all()


@router.get("/{person_id}", response_model=PersonRead)
def get_person(person_id: int, db: Session = Depends(get_db)):
    """Récupère une personne par ID."""
    person = db.query(Person).filter(Person.id == person_id).first()
    if not person:
        raise HTTPException(status_code=404, detail="Personne non trouvée")
    return person


@router.put("/{person_id}", response_model=PersonRead)
def update_person(person_id: int, person_update: PersonUpdate, db: Session = Depends(get_db)):
    """Met à jour une personne."""
    person = db.query(Person).filter(Person.id == person_id).first()
    if not person:
        raise HTTPException(status_code=404, detail="Personne non trouvée")
    
    for field, value in person_update.dict(exclude_unset=True).items():
        setattr(person, field, value)
    
    db.commit()
    db.refresh(person)
    return person


@router.delete("/{person_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_person(person_id: int, db: Session = Depends(get_db)):
    """Supprime une personne (soft delete)."""
    person = db.query(Person).filter(Person.id == person_id).first()
    if not person:
        raise HTTPException(status_code=404, detail="Personne non trouvée")
    
    person.is_active = 0
    db.commit()
