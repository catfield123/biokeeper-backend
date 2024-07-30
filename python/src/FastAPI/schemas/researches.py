from pydantic import BaseModel, field_validator, model_validator
from datetime import datetime, date
from typing import Union
from schemas.common import validate_identifier

class ResearchBase(BaseModel):
    id: int
    name: str

class ResearchResponse(ResearchBase):
    status: str
    created_at: datetime
    updated_at: datetime
    created_by: int
    day_start: datetime
    day_end: datetime
    comment: str | None
    approval_required: bool
    n_samples: int

class ResearchRequest(BaseModel):
    research_identifier : int | str

    @field_validator('research_identifier', mode="before")
    def validate_research_identifier(cls, v):
        return validate_identifier(v, 'research_identifier must be either an integer or a string')
    
class GetResearchRequest(ResearchRequest):
    pass

class SendResearchParticipantRequest(ResearchRequest):
    pass

class CandidateRequest(BaseModel):
    candidate_identifier : int | str

    @field_validator('candidate_identifier', mode="before")
    def validate_candidate_identifier(cls, v):
        return validate_identifier(v, 'candidate_identifier must be either an integer or a string')

class ApproveResearchRequest(BaseModel):
    candidate_identifier : int | str
    @field_validator('candidate_identifier', mode="before")
    def validate_candidate_identifier(cls, v):
        return validate_identifier(v, 'candidate_identifier must be either an integer or a string')

class DeclineResearchRequest(BaseModel):
    candidate_identifier : int | str

    @field_validator('candidate_identifier', mode="before")
    def validate_research_identifier(cls, v):
        return validate_identifier(v, 'candidate_identifier must be either an integer or a string')

class TextDescription(BaseModel):
    type: str = "text"
    text: str

class PolygonDescription(BaseModel):
    type: str = "polygon"
    coordinates: list[tuple[float, float]]
    text: str

    @field_validator('coordinates', mode='before')
    def validate_coordinates(cls, v):
        if len(v) < 4:
            raise ValueError('Each polygon must have at least 4 points including the closing point')
        return v

    @model_validator(mode='after')
    def check_polygon_validity(cls, values):
        coordinates = values.coordinates

        if coordinates[0] != coordinates[-1]:
            raise ValueError('Polygon must be closed, first and last point must be the same')
        
        if len(set(coordinates[:-1])) != len(coordinates[:-1]):
            raise ValueError('Polygon has repeated points, which is not allowed')
                
        if cls.has_self_intersections(coordinates):
            raise ValueError('Polygon sides intersect with each other')

        return values

    @staticmethod
    def has_self_intersections(coordinates: list[tuple[float, float]]) -> bool:
        def do_intersect(p1, q1, p2, q2):
            def orientation(p, q, r):
                val = (q[1] - p[1]) * (r[0] - q[0]) - (q[0] - p[0]) * (r[1] - q[1])
                if val == 0:
                    return 0
                elif val > 0:
                    return 1
                else:
                    return 2

            def on_segment(p, q, r):
                if (q[0] <= max(p[0], r[0]) and q[0] >= min(p[0], r[0]) and
                        q[1] <= max(p[1], r[1]) and q[1] >= min(p[1], r[1])):
                    return True
                return False

            o1 = orientation(p1, q1, p2)
            o2 = orientation(p1, q1, q2)
            o3 = orientation(p2, q2, p1)
            o4 = orientation(p2, q2, q1)

            if o1 != o2 and o3 != o4:
                return True

            if o1 == 0 and on_segment(p1, p2, q1):
                return True
            if o2 == 0 and on_segment(p1, q2, q1):
                return True
            if o3 == 0 and on_segment(p2, p1, q2):
                return True
            if o4 == 0 and on_segment(p2, q1, q2):
                return True

            return False

        n = len(coordinates)
        for i in range(n - 2):
            for j in range(i + 1, n - 1):
                if do_intersect(coordinates[i], coordinates[i + 1], coordinates[j], coordinates[j + 1]):
                    return True
        return False

    


class PointDescription(BaseModel):
    type: str = "point"
    coordinates: tuple[float, float]
    text: str

Description = Union[TextDescription, PolygonDescription, PointDescription]

class CreateResearchRequest(BaseModel):
    research_name: str
    day_start: date
    research_comment: str | None
    approval_required: bool = True
    descriptions: list[Description]

    @field_validator('research_comment', mode="before")
    def validate_comment(cls, v):
        if v is None:
            return ''
        return v

    @model_validator(mode='after')
    def check_single_text_description(cls, values):
        descriptions = values.descriptions
        text_descriptions = [desc for desc in descriptions if isinstance(desc, TextDescription)]
        if len(text_descriptions) > 1:
            raise ValueError('There can be no more than one description with type "text"')
        return values

class ResearchNewStatusResponse(BaseModel):
    research_identifier: int | str
    status: str

class MyResearch(BaseModel):
    research_id: int


