from typing import Annotated
from fastapi import Depends
from fastapi.routing import APIRouter
from db_manager import DBM
from datetime import date

from schemas import TokenPayload
from utils import get_current_user

router = APIRouter()

@router.get('/researches')
def get_researches(token_payload: Annotated[TokenPayload, Depends(get_current_user)]):
    return DBM.researches.get_all()

@router.get('/researches/{research_name}')
def get_research(research_name):
    return DBM.researches.get_info(research_name)

@router.get('/researches/{research_name}/status')
def get_research_status(research_name):
    return DBM.researches.status_of(research_name)

@router.post('/researches')
def create_research(research_name: str, user_name: str, day_start: date):
    return DBM.researches.new(research_name, user_name, day_start)
