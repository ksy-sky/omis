# infra/di.py
from controllers.controllers import (
    AuthController, CatalogController, TourController, TourCreationController,
    ReviewController, ModerationController, PersonalCabinetController, ComplaintController
)
from views.views import (
    AuthView, CatalogView, TourView, TourBuilderView, PersonalCabinetView, AdminPanelView
)

class ControllerFactory:
    def createAuthController(self, userRepo):
        return AuthController(userRepo)

    def createCatalogController(self, tourRepo):
        return CatalogController(tourRepo)

    def createTourController(self, tourRepo, userRepo):
        return TourController(tourRepo, userRepo)

    def createTourCreationController(self, tourRepo):
        return TourCreationController(tourRepo)

    def createReviewController(self, reviewRepo):
        return ReviewController(reviewRepo)

    def createModerationController(self, tourRepo, reviewRepo):
        return ModerationController(tourRepo, reviewRepo)

    def createPersonalCabinetController(self, userRepo, tourRepo, achievementRepo):
        return PersonalCabinetController(userRepo, tourRepo, achievementRepo)

    def createComplaintController(self, complaintRepo):
        return ComplaintController(complaintRepo)

class ViewFactory:
    def createAuthView(self, authController):
        return AuthView(authController)

    def createCatalogView(self, catalogController):
        return CatalogView(catalogController)

    def createTourView(self, tourController, reviewController):
        return TourView(tourController, reviewController)

    def createTourBuilderView(self, tourCreationController):
        return TourBuilderView(tourCreationController)

    def createPersonalCabinetView(self, personalCabinetController):
        return PersonalCabinetView(personalCabinetController)

    def createAdminPanelView(self, moderationController, complaintController):
        return AdminPanelView(moderationController, complaintController)

class DependencyContainer:
    def __init__(self):
        self._services = {}
        self._customCreators = {}
        self.controllerFactory = ControllerFactory()
        self.viewFactory = ViewFactory()

    def register(self, key, implementation):
        self._services[key] = implementation

    def registerCreator(self, key, creator):
        self._customCreators[key] = creator

    def resolve(self, key):
        return self._services.get(key)

    def createController(self, type):
        if type in self._customCreators:
            return self._customCreators[type]()
        if type in self._services:
            return self._services[type]
        
        method = getattr(self.controllerFactory, type, None)
        if method:
            if type == "createAuthController":
                instance = method(self.resolve("UserRepository"))
            elif type == "createCatalogController":
                instance = method(self.resolve("TourRepository"))
            elif type == "createTourController":
                instance = method(self.resolve("TourRepository"), self.resolve("UserRepository"))
            elif type == "createTourCreationController":
                instance = method(self.resolve("TourRepository"))
            elif type == "createReviewController":
                instance = method(self.resolve("ReviewRepository"))
            elif type == "createModerationController":
                instance = method(self.resolve("TourRepository"), self.resolve("ReviewRepository"))
            elif type == "createPersonalCabinetController":
                instance = method(self.resolve("UserRepository"), self.resolve("TourRepository"), self.resolve("AchievementRepository"))
            elif type == "createComplaintController":
                instance = method(self.resolve("ComplaintRepository"))
            else:
                return None
            self._services[type] = instance
            return instance
        return None

    def createView(self, type):
        if type in self._customCreators:
            return self._customCreators[type]()
        if type in self._services:
            return self._services[type]
        
        method = getattr(self.viewFactory, type, None)
        if method:
            if type == "createAuthView":
                instance = method(self.createController("createAuthController"))
            elif type == "createCatalogView":
                instance = method(self.createController("createCatalogController"))
            elif type == "createTourView":
                instance = method(self.createController("createTourController"), self.createController("createReviewController"))
            elif type == "createTourBuilderView":
                instance = method(self.createController("createTourCreationController"))
            elif type == "createPersonalCabinetView":
                instance = method(self.createController("createPersonalCabinetController"))
            elif type == "createAdminPanelView":
                instance = method(self.createController("createModerationController"), self.createController("createComplaintController"))
            else:
                return None
            self._services[type] = instance
            return instance
        return None
