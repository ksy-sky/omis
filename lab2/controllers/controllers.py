# controllers/controllers.py
import uuid
import time
from model.data import User, Tour, RoutePoint, Review, Complaint
from app.constants import (
    ROLE_TRAVELER, ROLE_ADMIN,
    STATUS_DRAFT, STATUS_PENDING, STATUS_PUBLISHED, STATUS_REJECTED,
    REVIEW_STATUS_DRAFT, REVIEW_STATUS_PENDING, REVIEW_STATUS_PUBLISHED, REVIEW_STATUS_REJECTED,
    COMPLAINT_STATUS_PENDING, MINUTES_PER_POINT
)

class AuthController:
    def __init__(self, userRepo):
        self._userRepo = userRepo

    def register(self, nickname, email, password):
        if self._userRepo.getByEmail(email):
            return None
        newUser = User(
            id=uuid.uuid4().hex,
            nickname=nickname,
            email=email,
            role=ROLE_TRAVELER,
            password=password
        )
        self._userRepo.save(newUser)
        return newUser

    def login(self, email, password):
        user = self._userRepo.getByEmail(email)
        if user and user.password == password:
            return user
        return None

    def checkAdminRights(self, userId):
        user = self._userRepo.getById(userId)
        return user.role == ROLE_ADMIN if user else False

    def grantAdminRights(self, userId):
        user = self._userRepo.getById(userId)
        if user:
            user.role = ROLE_ADMIN
            self._userRepo.save(user)

class CatalogController:
    def __init__(self, tourRepo):
        self._tourRepo = tourRepo

    def getCatalog(self):
        return self._tourRepo.getByStatus(STATUS_PUBLISHED)

    def filterByCity(self, city):
        return [t for t in self.getCatalog() if t.city == city]

    def filterByTheme(self, theme):
        return [t for t in self.getCatalog() if t.theme == theme]

    def sort(self, criteria):
        tours = self.getCatalog()
        if criteria == "title":
            return sorted(tours, key=lambda t: t.title)
        elif criteria == "duration":
            return sorted(tours, key=lambda t: t.duration)
        elif criteria == "rating":
            def avg_rating(t):
                if not t.reviews:
                    return 0
                return sum(r.rating for r in t.reviews) / len(t.reviews)
            return sorted(tours, key=avg_rating, reverse=True)
        return tours

class TourController:
    def __init__(self, tourRepo, userRepo):
        self._tourRepo = tourRepo
        self._userRepo = userRepo

    def startTour(self, tourId):
        tour = self._tourRepo.getById(tourId)
        if tour:
            tour.routePoints = self._tourRepo.getRoutePoints(tourId)
        return tour

    def getRoutePoint(self, tourId, number):
        points = self._tourRepo.getRoutePoints(tourId)
        for p in points:
            if p.orderNumber == number:
                return p
        return None

    def fixProgress(self, userId, tourId):
        user = self._userRepo.getById(userId)
        tour = self._tourRepo.getById(tourId)
        if user and tour and tour not in user.completedTours:
            user.completedTours.append(tour)
            self._userRepo.save(user)

    def addToFavorites(self, userId, tourId):
        user = self._userRepo.getById(userId)
        tour = self._tourRepo.getById(tourId)
        if user and tour and tour not in user.favoriteTours:
            user.favoriteTours.append(tour)
            self._userRepo.save(user)

class TourCreationController:
    def __init__(self, tourRepo):
        self._tourRepo = tourRepo

    def createTour(self, title, city, theme, description):
        newTour = Tour(
            id=uuid.uuid4().hex,
            authorId="",
            title=title,
            city=city,
            theme=theme,
            duration=0,
            status=STATUS_DRAFT,
            description=description
        )
        self._tourRepo.save(newTour)
        return newTour

    def addRoutePoint(self, tourId, point):
        tour = self._tourRepo.getById(tourId)
        if tour:
            existing = self._tourRepo.getRoutePoints(tourId)
            point.orderNumber = len(existing) + 1
            self._tourRepo.saveRoutePoint(tourId, point)
            tour.routePoints.append(point)
            tour.duration += MINUTES_PER_POINT
            self._tourRepo.save(tour)

    def sendToModeration(self, tourId):
        tour = self._tourRepo.getById(tourId)
        if tour:
            tour.status = STATUS_PENDING
            self._tourRepo.save(tour)

class ReviewController:
    def __init__(self, reviewRepo):
        self._reviewRepo = reviewRepo

    def leaveReview(self, userId, tourId, text, rating):
        newReview = Review(
            id=uuid.uuid4().hex,
            userId=userId,
            tourId=tourId,
            text=text,
            image="",
            rating=rating,
            date=int(time.time()),
            status=REVIEW_STATUS_DRAFT
        )
        self._reviewRepo.save(newReview)
        return newReview

    def sendReviewToModeration(self, reviewId):
        review = self._reviewRepo.getById(reviewId)
        if review:
            review.status = REVIEW_STATUS_PENDING
            self._reviewRepo.save(review)

class ModerationController:
    def __init__(self, tourRepo, reviewRepo):
        self._tourRepo = tourRepo
        self._reviewRepo = reviewRepo

    def getToursForModeration(self):
        return self._tourRepo.getByStatus(STATUS_PENDING)

    def approveTour(self, tourId):
        tour = self._tourRepo.getById(tourId)
        if tour:
            tour.status = STATUS_PUBLISHED
            self._tourRepo.save(tour)

    def rejectTour(self, tourId):
        tour = self._tourRepo.getById(tourId)
        if tour:
            tour.status = STATUS_REJECTED
            self._tourRepo.save(tour)

    def getReviewsForModeration(self):
        return self._reviewRepo.getByStatus(REVIEW_STATUS_PENDING)

    def approveReview(self, reviewId):
        review = self._reviewRepo.getById(reviewId)
        if review:
            review.status = REVIEW_STATUS_PUBLISHED
            self._reviewRepo.save(review)
            tour = self._tourRepo.getById(review.tourId)
            if tour and review not in tour.reviews:
                tour.reviews.append(review)
                self._tourRepo.save(tour)

    def rejectReview(self, reviewId):
        review = self._reviewRepo.getById(reviewId)
        if review:
            review.status = REVIEW_STATUS_REJECTED
            self._reviewRepo.save(review)

class PersonalCabinetController:
    def __init__(self, userRepo, tourRepo, achievementRepo):
        self._userRepo = userRepo
        self._tourRepo = tourRepo
        self._achievementRepo = achievementRepo

    def getProfile(self, userId):
        return self._userRepo.getById(userId)

    def getCompletedTours(self, userId):
        user = self._userRepo.getById(userId)
        return user.completedTours if user else []

    def getCreatedTours(self, userId):
        return [t for t in self._tourRepo.getAll() if t.authorId == userId]

    def getFavoriteTours(self, userId):
        user = self._userRepo.getById(userId)
        return user.favoriteTours if user else []

    def getAchievements(self, userId):
        return self._achievementRepo.getUserAchievements(userId)

class ComplaintController:
    def __init__(self, complaintRepo):
        self._complaintRepo = complaintRepo

    def submitComplaint(self, userId, objectId, description):
        newComp = Complaint(
            id=uuid.uuid4().hex,
            userId=userId,
            objectId=objectId,
            objectType="Tour",
            status=COMPLAINT_STATUS_PENDING,
            description=description
        )
        self._complaintRepo.save(newComp)
        return newComp

    def getComplaintsForModeration(self):
        return self._complaintRepo.getByStatus(COMPLAINT_STATUS_PENDING)

    def reviewComplaint(self, complaintId, decision):
        comp = self._complaintRepo.getById(complaintId)
        if comp:
            comp.status = decision
            self._complaintRepo.save(comp)
