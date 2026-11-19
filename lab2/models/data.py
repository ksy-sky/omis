# model/data.py
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    pass

@dataclass
class User:
    id: str
    nickname: str
    email: str
    role: str
    password: str
    createdTours: List['Tour'] = field(default_factory=list)
    completedTours: List['Tour'] = field(default_factory=list)
    favoriteTours: List['Tour'] = field(default_factory=list)
    reviews: List['Review'] = field(default_factory=list)
    complaints: List['Complaint'] = field(default_factory=list)
    achievements: List['Achievement'] = field(default_factory=list)

@dataclass
class Tour:
    id: str
    authorId: str
    title: str
    city: str
    theme: str
    duration: int
    status: str
    description: str
    routePoints: List['RoutePoint'] = field(default_factory=list)
    reviews: List['Review'] = field(default_factory=list)

@dataclass
class RoutePoint:
    id: str
    tourId: str
    title: str
    orderNumber: int
    coordinates: str
    image: str
    description: str

@dataclass
class Review:
    id: str
    userId: str
    tourId: str
    text: str
    image: str
    rating: int
    date: int
    status: str

@dataclass
class Complaint:
    id: str
    userId: str
    objectId: str
    objectType: str
    status: str
    description: str

@dataclass
class Achievement:
    id: str
    title: str
    description: str
    icon: str
    condition: str
