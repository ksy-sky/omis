# model/repositories.py
from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any
from model.data import User, Tour, RoutePoint, Review, Complaint, Achievement

class IRepository(ABC):
    @abstractmethod
    def getById(self, id: str) -> Optional[Any]:
        pass

    @abstractmethod
    def save(self, obj: Any) -> None:
        pass

    @abstractmethod
    def delete(self, id: str) -> None:
        pass

    @abstractmethod
    def getAll(self) -> List[Any]:
        pass

class UserRepository(IRepository):
    def __init__(self):
        self._storage: Dict[str, User] = {}

    def getById(self, id: str) -> Optional[User]:
        return self._storage.get(id)

    def save(self, obj: User) -> None:
        self._storage[obj.id] = obj

    def delete(self, id: str) -> None:
        self._storage.pop(id, None)

    def getAll(self) -> List[User]:
        return list(self._storage.values())

    def getByEmail(self, email: str) -> Optional[User]:
        return next((u for u in self._storage.values() if u.email == email), None)

    def getByRole(self, role: str) -> List[User]:
        return [u for u in self._storage.values() if u.role == role]

class TourRepository(IRepository):
    def __init__(self):
        self._storage: Dict[str, Tour] = {}
        self._pointsStorage: Dict[str, List[RoutePoint]] = {}

    def getById(self, id: str) -> Optional[Tour]:
        return self._storage.get(id)

    def save(self, obj: Tour) -> None:
        self._storage[obj.id] = obj

    def delete(self, id: str) -> None:
        self._storage.pop(id, None)
        self._pointsStorage.pop(id, None)

    def getAll(self) -> List[Tour]:
        return list(self._storage.values())

    def getByStatus(self, status: str) -> List[Tour]:
        return [t for t in self._storage.values() if t.status == status]

    def getByCity(self, city: str) -> List[Tour]:
        return [t for t in self._storage.values() if t.city == city]

    def getByTheme(self, theme: str) -> List[Tour]:
        return [t for t in self._storage.values() if t.theme == theme]

    def getRoutePoints(self, tourId: str) -> List[RoutePoint]:
        points = self._pointsStorage.get(tourId, [])
        return sorted(points, key=lambda p: p.orderNumber)

    def saveRoutePoint(self, tourId: str, point: RoutePoint) -> None:
        if tourId not in self._pointsStorage:
            self._pointsStorage[tourId] = []
        self._pointsStorage[tourId].append(point)

class ReviewRepository(IRepository):
    def __init__(self):
        self._storage: Dict[str, Review] = {}

    def getById(self, id: str) -> Optional[Review]:
        return self._storage.get(id)

    def save(self, obj: Review) -> None:
        self._storage[obj.id] = obj

    def delete(self, id: str) -> None:
        self._storage.pop(id, None)

    def getAll(self) -> List[Review]:
        return list(self._storage.values())

    def getByTour(self, tourId: str) -> List[Review]:
        return [r for r in self._storage.values() if r.tourId == tourId]

    def getByStatus(self, status: str) -> List[Review]:
        return [r for r in self._storage.values() if r.status == status]

class ComplaintRepository(IRepository):
    def __init__(self):
        self._storage: Dict[str, Complaint] = {}

    def getById(self, id: str) -> Optional[Complaint]:
        return self._storage.get(id)

    def save(self, obj: Complaint) -> None:
        self._storage[obj.id] = obj

    def delete(self, id: str) -> None:
        self._storage.pop(id, None)

    def getAll(self) -> List[Complaint]:
        return list(self._storage.values())

    def getByStatus(self, status: str) -> List[Complaint]:
        return [c for c in self._storage.values() if c.status == status]

    def getByObject(self, objectId: str) -> List[Complaint]:
        return [c for c in self._storage.values() if c.objectId == objectId]

class AchievementRepository(IRepository):
    def __init__(self):
        self._storage: Dict[str, Achievement] = {}
        self._userAchievements: Dict[str, List[str]] = {}

    def getById(self, id: str) -> Optional[Achievement]:
        return self._storage.get(id)

    def save(self, obj: Achievement) -> None:
        self._storage[obj.id] = obj

    def delete(self, id: str) -> None:
        self._storage.pop(id, None)

    def getAll(self) -> List[Achievement]:
        return list(self._storage.values())

    def getUserAchievements(self, userId: str) -> List[Achievement]:
        ids = self._userAchievements.get(userId, [])
        return [self._storage[i] for i in ids if i in self._storage]

    def assignAchievement(self, userId: str, achievementId: str) -> None:
        if userId not in self._userAchievements:
            self._userAchievements[userId] = []
        if achievementId not in self._userAchievements[userId]:
            self._userAchievements[userId].append(achievementId)

    def checkCondition(self, userId: str, condition: str) -> bool:
        return True