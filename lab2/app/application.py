# app/app.py
import tkinter as tk
from tkinter import messagebox
from app.constants import (
    ROLE_TRAVELER, ROLE_ADMIN, STATUS_PUBLISHED, STATUS_PENDING,
    REVIEW_STATUS_PUBLISHED, REVIEW_STATUS_PENDING, COMPLAINT_STATUS_PENDING,
    MINUTES_PER_POINT, SPLASH_MS
)
from model.repositories import (
    UserRepository, TourRepository, ReviewRepository,
    ComplaintRepository, AchievementRepository
)
from model.data import User, Tour, RoutePoint, Review, Complaint, Achievement
from views.views import GoodbyeView
from infra.di import DependencyContainer


class SystemConfigurator:
    def __init__(self):
        self._container = None

    def configureDependencies(self, container):
        """Запоминает контейнер и регистрирует репозитории."""
        self._container = container
        repos = self.createRepositories()
        for repo in repos:
            container.register(type(repo).__name__, repo)

    def createRepositories(self):
        """Создаёт 5 репозиториев, заполняет демо-данными, возвращает список."""
        userRepo = UserRepository()
        tourRepo = TourRepository()
        reviewRepo = ReviewRepository()
        complaintRepo = ComplaintRepository()
        achievementRepo = AchievementRepository()

        # --- Демо-данные (раздел 10 PDF) ---
        katya = User(id="user1", nickname="Катя Пушистова", email="katya@example.com", role=ROLE_TRAVELER, password="1234")
        admin = User(id="admin1", nickname="Администратор", email="admin@example.com", role=ROLE_ADMIN, password="admin")
        user123 = User(id="user123", nickname="user123", email="user123@example.com", role=ROLE_TRAVELER, password="123")
        user456 = User(id="user456", nickname="Алексей С.", email="user456@example.com", role=ROLE_TRAVELER, password="123")
        for u in [katya, admin, user123, user456]:
            userRepo.save(u)

        ach1 = Achievement(id="ach1", title="Первый тур", description="Пройти первую экскурсию", icon="🥇", condition="completed >= 1")
        ach2 = Achievement(id="ach2", title="Исследователь", description="Посетить 5 городов", icon="🧭", condition="cities >= 5")
        achievementRepo.save(ach1)
        achievementRepo.save(ach2)
        achievementRepo.assignAchievement("user1", "ach1")

        minsk = Tour(id="tour1", authorId="admin1", title="Прогулка по Минску", city="Минск", theme="История", duration=60, status=STATUS_PUBLISHED, description="Исторический центр.")
        tourRepo.save(minsk)
        points_minsk = [
            RoutePoint(id="p1", tourId="tour1", title="Собор Сошествия Святого Духа", orderNumber=1, coordinates="100,100", image="cathedral.jpg", description="Главный храм."),
            RoutePoint(id="p2", tourId="tour1", title="Площадь Свободы", orderNumber=2, coordinates="200,150", image="square.jpg", description="Центр."),
            RoutePoint(id="p3", tourId="tour1", title="Троицкое предместье", orderNumber=3, coordinates="300,200", image="troitskoe.jpg", description="Район."),
            RoutePoint(id="p4", tourId="tour1", title="Остров Слёз", orderNumber=4, coordinates="400,250", image="island.jpg", description="Мемориал."),
            RoutePoint(id="p5", tourId="tour1", title="Набережная Свислочи", orderNumber=5, coordinates="500,300", image="river.jpg", description="Река."),
        ]
        for p in points_minsk:
            tourRepo.saveRoutePoint("tour1", p)
            minsk.routePoints.append(p)

        brest = Tour(id="tour2", authorId="admin1", title="Брестская крепость", city="Брест", theme="История", duration=90, status=STATUS_PUBLISHED, description="Мемориал.")
        tourRepo.save(brest)
        points_brest = [
            RoutePoint(id="p6", tourId="tour2", title="Главный вход", orderNumber=1, coordinates="100,100", image="gate.jpg", description="Вход."),
            RoutePoint(id="p7", tourId="tour2", title="Холмские ворота", orderNumber=2, coordinates="200,200", image="gates.jpg", description="Ворота."),
            RoutePoint(id="p8", tourId="tour2", title="Штык-нож", orderNumber=3, coordinates="300,300", image="bayonet.jpg", description="Монумент."),
        ]
        for p in points_brest:
            tourRepo.saveRoutePoint("tour2", p)
            brest.routePoints.append(p)

        pushcha = Tour(id="tour3", authorId="admin1", title="Беловежская пуща", city="Брест", theme="Природа", duration=120, status=STATUS_PUBLISHED, description="Заповедник.")
        tourRepo.save(pushcha)
        points_pushcha = [
            RoutePoint(id="p9", tourId="tour3", title="Визит-центр", orderNumber=1, coordinates="150,150", image="center.jpg", description="Начало."),
            RoutePoint(id="p10", tourId="tour3", title="Вольеры зубров", orderNumber=2, coordinates="350,250", image="zubr.jpg", description="Зубры."),
        ]
        for p in points_pushcha:
            tourRepo.saveRoutePoint("tour3", p)
            pushcha.routePoints.append(p)

        pending_tour = Tour(id="tour4", authorId="user123", title="Путешествие по набережной Свислочи", city="Минск", theme="Архитектура", duration=45, status=STATUS_PENDING, description="Прогулка.")
        tourRepo.save(pending_tour)
        for i in range(1, 4):
            p = RoutePoint(id=f"pp{i}", tourId="tour4", title=f"Точка {i}", orderNumber=i, coordinates=f"{100*i},{100*i}", image="river.jpg", description="Описание")
            tourRepo.saveRoutePoint("tour4", p)
            pending_tour.routePoints.append(p)

        rev1 = Review(id="rev1", userId="user1", tourId="tour1", text="Отлично!", image="", rating=5, date=1700000000, status=REVIEW_STATUS_PUBLISHED)
        rev2 = Review(id="rev2", userId="user1", tourId="tour1", text="Хорошо", image="", rating=4, date=1700000000, status=REVIEW_STATUS_PUBLISHED)
        rev3 = Review(id="rev3", userId="user1", tourId="tour2", text="Супер", image="", rating=5, date=1700000000, status=REVIEW_STATUS_PUBLISHED)
        rev4 = Review(id="rev4", userId="user456", tourId="tour1", text="Чудесный маршрут, но фото не отсюда...", image="", rating=4, date=1700000000, status=REVIEW_STATUS_PENDING)
        for r in [rev1, rev2, rev3, rev4]:
            reviewRepo.save(r)
        minsk.reviews.extend([rev1, rev2, rev4])
        brest.reviews.append(rev3)
        tourRepo.save(minsk)
        tourRepo.save(brest)

        comp1 = Complaint(id="comp1", userId="user1", objectId="rev4", objectType="Review", status=COMPLAINT_STATUS_PENDING, description="Некорректное фото.")
        complaintRepo.save(comp1)

        return [userRepo, tourRepo, reviewRepo, complaintRepo, achievementRepo]

    def _repo(self, repositories, repo_type):
        """Вспомогательный: достаёт репозиторий нужного типа из списка."""
        return next((r for r in repositories if isinstance(r, repo_type)), None)

    def createControllers(self, repositories):
        """Принимает список репозиториев, создаёт 8 контроллеров, возвращает список."""
        userRepo = self._repo(repositories, UserRepository)
        tourRepo = self._repo(repositories, TourRepository)
        reviewRepo = self._repo(repositories, ReviewRepository)
        complaintRepo = self._repo(repositories, ComplaintRepository)
        achievementRepo = self._repo(repositories, AchievementRepository)

        controllers = []
        controllers.append(self._container.createController("createAuthController"))
        controllers.append(self._container.createController("createCatalogController"))
        controllers.append(self._container.createController("createTourController"))
        controllers.append(self._container.createController("createTourCreationController"))
        controllers.append(self._container.createController("createReviewController"))
        controllers.append(self._container.createController("createModerationController"))
        controllers.append(self._container.createController("createPersonalCabinetController"))
        controllers.append(self._container.createController("createComplaintController"))
        return controllers

    def createViews(self, controllers):
        """Принимает список контроллеров, создаёт 6 представлений, возвращает список."""
        # Достаём контроллеры по типу из контейнера (они уже закэшированы)
        views = []
        views.append(self._container.createView("createAuthView"))
        views.append(self._container.createView("createCatalogView"))
        views.append(self._container.createView("createTourView"))
        views.append(self._container.createView("createTourBuilderView"))
        views.append(self._container.createView("createPersonalCabinetView"))
        views.append(self._container.createView("createAdminPanelView"))
        return views


class ExcursionPlatformApp:
    def __init__(self):
        self.container = DependencyContainer()
        self.root = None
        self.currentUser = None
        self.currentFrame = None
        self.views = {}

    def main(self):
        self.initializeSystem()
        self.launchApp()
        self.root.mainloop()

    def initializeSystem(self):
        self.root = tk.Tk()
        self.root.title("Платформа виртуальных экскурсий")
        self.root.geometry("1000x650")

        splash = tk.Label(self.root, text="Загрузка системы...", font=("Arial", 24))
        splash.pack(expand=True)
        self.root.update()

        configurator = SystemConfigurator()
        configurator.configureDependencies(self.container)
        repositories = configurator.createRepositories()
        # Регистрируем репозитории (configureDependencies уже сделал это, но на всякий случай)
        for repo in repositories:
            self.container.register(type(repo).__name__, repo)
        configurator.createControllers(repositories)
        configurator.createViews([])  # controllers уже в контейнере

        # Создаём GoodbyeView напрямую (это довесок, на диаграмме его нет)
        self.views["goodbye"] = GoodbyeView()

        self.root.after(SPLASH_MS, splash.pack_forget)

    def launchApp(self):
        self.views["auth"] = self.container.resolve("createAuthView")
        self.views["catalog"] = self.container.resolve("createCatalogView")
        self.views["tour"] = self.container.resolve("createTourView")
        self.views["tourBuilder"] = self.container.resolve("createTourBuilderView")
        self.views["cabinet"] = self.container.resolve("createPersonalCabinetView")
        self.views["admin"] = self.container.resolve("createAdminPanelView")

        for view in self.views.values():
            view.navigator = self.showScreen

        self.showScreen("auth")

    def stopApp(self):
        self.root.destroy()

    def showScreen(self, name, data=None):
        if name == "request_admin":
            self._handleAdminRequest(data)
            return

        if name == "exit":
            # UI_Выход: показываем "До свидания!" на SPLASH_MS, потом закрываем
            if self.currentFrame:
                self.currentFrame.pack_forget()
            goodbye = self.views.get("goodbye")
            if goodbye:
                self.currentFrame = goodbye
                goodbye.pack(fill="both", expand=True)
            self.root.after(SPLASH_MS, self.stopApp)
            return

        if self.currentFrame:
            self.currentFrame.pack_forget()

        view = self.views.get(name)
        if view:
            self.currentFrame = view
            view.pack(fill="both", expand=True)
            view.display(data)

    def _handleAdminRequest(self, user):
        authCtrl = self.container.resolve("createAuthController")
        if authCtrl.checkAdminRights(user.id):
            self.showScreen("admin", data=user)
        else:
            if messagebox.askyesno("Права", "У вас нет прав администратора. Запросить права?"):
                authCtrl.grantAdminRights(user.id)
                user.role = ROLE_ADMIN
                messagebox.showinfo("Успех", "Права администратора запрошены и выданы!")
                self.showScreen("admin", data=user)
