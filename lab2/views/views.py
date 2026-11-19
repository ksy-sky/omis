# views/views.py
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from abc import ABC, abstractmethod
from app.constants import *

class IView(ABC):
    @abstractmethod
    def display(self, data):
        pass

    @abstractmethod
    def refresh(self, data):
        pass

class BaseView(tk.Frame, IView):
    def __init__(self):
        super().__init__(None)
        self.navigator = None
        self.configure(bg="#f0f0f0")

class AuthView(BaseView):
    def __init__(self, authController):
        super().__init__()
        self.controller = authController
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(pady=20, expand=True, fill="both")

        self.loginFrame = ttk.Frame(self.notebook, padding=20)
        self.notebook.add(self.loginFrame, text="Войти")
        ttk.Label(self.loginFrame, text="Почта:").grid(row=0, column=0, sticky="e")
        self.loginEmail = ttk.Entry(self.loginFrame)
        self.loginEmail.grid(row=0, column=1, pady=5)
        ttk.Label(self.loginFrame, text="Пароль:").grid(row=1, column=0, sticky="e")
        self.loginPass = ttk.Entry(self.loginFrame, show="*")
        self.loginPass.grid(row=1, column=1, pady=5)
        ttk.Button(self.loginFrame, text="Войти", command=self._onLoginClicked).grid(row=2, column=0, columnspan=2, pady=10)

        self.regFrame = ttk.Frame(self.notebook, padding=20)
        self.notebook.add(self.regFrame, text="Регистрация")
        ttk.Label(self.regFrame, text="Никнейм:").grid(row=0, column=0, sticky="e")
        self.regNick = ttk.Entry(self.regFrame)
        self.regNick.grid(row=0, column=1, pady=5)
        ttk.Label(self.regFrame, text="Почта:").grid(row=1, column=0, sticky="e")
        self.regEmail = ttk.Entry(self.regFrame)
        self.regEmail.grid(row=1, column=1, pady=5)
        ttk.Label(self.regFrame, text="Пароль:").grid(row=2, column=0, sticky="e")
        self.regPass = ttk.Entry(self.regFrame, show="*")
        self.regPass.grid(row=2, column=1, pady=5)
        ttk.Button(self.regFrame, text="Зарегистрироваться", command=self._onRegClicked).grid(row=3, column=0, columnspan=2, pady=10)

    def _onLoginClicked(self):
        user = self.controller.login(self.loginEmail.get(), self.loginPass.get())
        if user:
            self.displayLoginResult(True, user)
        else:
            self.displayLoginResult(False)

    def _onRegClicked(self):
        user = self.controller.register(self.regNick.get(), self.regEmail.get(), self.regPass.get())
        self.displayRegistrationResult(user is not None)

    def showRegistrationForm(self):
        self.notebook.select(1)

    def showLoginForm(self):
        self.notebook.select(0)

    def displayRegistrationResult(self, success):
        if success:
            messagebox.showinfo("Успех", "Регистрация успешна! Войдите.")
            self.notebook.select(0)
        else:
            messagebox.showerror("Ошибка", "Email уже занят.")

    def displayLoginResult(self, success, user=None):
        if success:
            self.navigator("catalog", data=user)
        else:
            if messagebox.askretrycancel("Ошибка авторизации", "Неверная почта или пароль. Повторить?"):
                self._onLoginClicked()
            else:
                self.navigator("auth")

    def display(self, data):
        self.showLoginForm()

    def refresh(self, data):
        pass

class CatalogView(BaseView):
    def __init__(self, catalogController):
        super().__init__()
        self.controller = catalogController
        self.currentUser = None

        header = ttk.Frame(self)
        header.pack(fill="x", padx=10, pady=10)
        ttk.Label(header, text="Каталог экскурсий", font=("Arial", 16, "bold")).pack(side="left")
        self.searchEntry = ttk.Entry(header, width=30)
        self.searchEntry.insert(0, "Поиск туров...")
        self.searchEntry.pack(side="left", padx=10)
        ttk.Button(header, text="Личный кабинет", command=lambda: self.navigator("cabinet", data=self.currentUser)).pack(side="right")
        ttk.Button(header, text="Выход", command=lambda: self.navigator("exit")).pack(side="right", padx=5)

        mainPane = ttk.PanedWindow(self, orient="horizontal")
        mainPane.pack(fill="both", expand=True, padx=10)

        filters = ttk.LabelFrame(mainPane, text="Фильтры", padding=10)
        mainPane.add(filters, weight=1)

        ttk.Label(filters, text="Город:").pack(anchor="w")
        self.cityVar = tk.StringVar(value="Любой")
        self.cityCb = ttk.Combobox(filters, textvariable=self.cityVar, values=["Любой", "Минск", "Брест"])
        self.cityCb.pack(fill="x", pady=5)
        self.cityCb.bind("<<ComboboxSelected>>", lambda e: self._applyFilters())

        ttk.Label(filters, text="Тематика:").pack(anchor="w")
        self.themeVar = tk.StringVar(value="Любая")
        self.themeCb = ttk.Combobox(filters, textvariable=self.themeVar, values=["Любая", "История", "Природа", "Архитектура"])
        self.themeCb.pack(fill="x", pady=5)
        self.themeCb.bind("<<ComboboxSelected>>", lambda e: self._applyFilters())

        ttk.Label(filters, text="Длительность (неактивно):").pack(anchor="w")
        self.durVar = tk.StringVar(value="Любая")
        ttk.Combobox(filters, textvariable=self.durVar, values=["Любая", "До 1 часа", "1-2 часа"]).pack(fill="x", pady=5)

        ttk.Label(filters, text="Сортировка:").pack(anchor="w", pady=(10, 0))
        self.sortVar = tk.StringVar(value="По умолчанию")
        self.sortCb = ttk.Combobox(filters, textvariable=self.sortVar, values=["По умолчанию", "По названию", "По длительности", "По рейтингу"])
        self.sortCb.pack(fill="x", pady=5)
        self.sortCb.bind("<<ComboboxSelected>>", lambda e: self._applyFilters())

        self.cardsContainer = ttk.Frame(mainPane)
        mainPane.add(self.cardsContainer, weight=3)

        canvas = tk.Canvas(self.cardsContainer)
        scrollbar = ttk.Scrollbar(self.cardsContainer, orient="vertical", command=canvas.yview)
        self.scrollableFrame = ttk.Frame(canvas)
        self.scrollableFrame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.scrollableFrame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _applyFilters(self):
        tours = self.controller.getCatalog()
        if self.cityVar.get() != "Любой":
            tours = self.controller.filterByCity(self.cityVar.get())
        if self.themeVar.get() != "Любая":
            tours = [t for t in tours if t.theme == self.themeVar.get()]
        criteria = self.sortVar.get()
        if criteria == "По названию":
            tours = self.controller.sort("title")
        elif criteria == "По длительности":
            tours = self.controller.sort("duration")
        elif criteria == "По рейтингу":
            tours = self.controller.sort("rating")
        self.updateCatalog(tours)

    def displayCatalog(self, tours):
        self.updateCatalog(tours)

    def displayFilters(self):
        pass

    def updateCatalog(self, tours):
        for widget in self.scrollableFrame.winfo_children():
            widget.destroy()
        for tour in tours:
            card = ttk.Frame(self.scrollableFrame, relief="groove", borderwidth=2, padding=10)
            card.pack(fill="x", pady=10, padx=10)
            ttk.Label(card, text=tour.title, font=("Arial", 12, "bold")).pack(anchor="w")
            rating = sum(r.rating for r in tour.reviews) / len(tour.reviews) if tour.reviews else 0
            ttk.Label(card, text=f"{tour.city} | {tour.theme} | {tour.duration} мин. | Рейтинг: {rating:.1f}").pack(anchor="w")
            ttk.Button(card, text="Начать тур", command=lambda t=tour.id: self.navigator("tour", data={"user": self.currentUser, "tour_id": t})).pack(anchor="e", pady=5)

    def display(self, data):
        self.currentUser = data
        self.displayCatalog(self.controller.getCatalog())
        self.displayFilters()

    def refresh(self, data):
        pass

class TourView(BaseView):
    def __init__(self, tourController, reviewController):
        super().__init__()
        self.tourCtrl = tourController
        self.revCtrl = reviewController
        self.currentTour = None
        self.currentStep = 1
        self.totalSteps = 0
        self.currentUser = None
        self.extensionSlot = ttk.Frame(self)
        self.extensionSlot.pack(fill="x", padx=10)
        self._draftReview = None  # Для exit-действия формы отзыва

        header = ttk.Frame(self)
        header.pack(fill="x", padx=10, pady=10)
        # Exit-действие: fixProgress при любом выходе из тура (раздел 8 п.1)
        ttk.Button(header, text="Назад к каталогу", command=self._onBackToCatalogClicked).pack(side="left")
        self.stepLabel = ttk.Label(header, text="", font=("Arial", 12))
        self.stepLabel.pack(side="right")

        content = ttk.PanedWindow(self, orient="horizontal")
        content.pack(fill="both", expand=True, padx=10)

        self.infoFrame = ttk.Frame(content, padding=10)
        content.add(self.infoFrame, weight=1)
        self.photoPlaceholder = tk.Canvas(self.infoFrame, width=300, height=200, bg="gray")
        self.photoPlaceholder.pack(pady=10)
        self.titleLabel = ttk.Label(self.infoFrame, text="", font=("Arial", 14, "bold"))
        self.titleLabel.pack()
        self.descLabel = ttk.Label(self.infoFrame, text="", wraplength=300, justify="left")
        self.descLabel.pack(pady=10)

        self.mapCanvas = tk.Canvas(content, width=300, height=400, bg="lightblue")
        content.add(self.mapCanvas, weight=1)

        navFrame = ttk.Frame(self)
        navFrame.pack(fill="x", padx=10, pady=10)
        ttk.Button(navFrame, text="Назад", command=self._onPrevClicked).pack(side="left", padx=5)
        self.nextBtn = ttk.Button(navFrame, text="Далее", command=self._onNextClicked)
        self.nextBtn.pack(side="right", padx=5)
        ttk.Button(navFrame, text="В избранное", command=self._onFavClicked).pack(side="right", padx=5)

    def _onBackToCatalogClicked(self):
        # Exit-действие: fixProgress при любом выходе (раздел 8 п.1)
        if self.currentTour and self.currentUser:
            self.tourCtrl.fixProgress(self.currentUser.id, self.currentTour.id)
        self.navigator("catalog", data=self.currentUser)

    def _onNextClicked(self):
        if self.currentStep < self.totalSteps:
            self.currentStep += 1
            self.displayRoutePoint(self.tourCtrl.getRoutePoint(self.currentTour.id, self.currentStep))

    def _onPrevClicked(self):
        if self.currentStep > 1:
            self.currentStep -= 1
            self.displayRoutePoint(self.tourCtrl.getRoutePoint(self.currentTour.id, self.currentStep))

    def _onFavClicked(self):
        if self.currentTour and self.currentUser:
            self.tourCtrl.addToFavorites(self.currentUser.id, self.currentTour.id)
            messagebox.showinfo("Успех", "Экскурсия добавлена в избранное!")

    def displayRoutePoint(self, point):
        if not point:
            return
        self.stepLabel.config(text=f"Шаг {self.currentStep} из {self.totalSteps} | {self.currentTour.title}")
        self.titleLabel.config(text=point.title)
        self.descLabel.config(text=point.description)
        self.photoPlaceholder.delete("all")
        self.photoPlaceholder.create_text(150, 100, text=f"[Фото: {point.image}]", fill="white")
        self.mapCanvas.delete("all")
        points = self.tourCtrl._tourRepo.getRoutePoints(self.currentTour.id)
        for p in points:
            x, y = map(int, p.coordinates.split(","))
            color = "red" if p.orderNumber == self.currentStep else "blue"
            self.mapCanvas.create_oval(x - 10, y - 10, x + 10, y + 10, fill=color)
            self.mapCanvas.create_text(x, y - 15, text=str(p.orderNumber))
        if self.currentStep == self.totalSteps:
            self.nextBtn.config(text="Завершить", command=self._onFinishClicked)
        else:
            self.nextBtn.config(text="Далее", command=self._onNextClicked)

    def displayRouteMap(self, points):
        pass

    def _onFinishClicked(self):
        # Exit-действие: fixProgress (дублируется, но так по диаграмме)
        if self.currentTour and self.currentUser:
            self.tourCtrl.fixProgress(self.currentUser.id, self.currentTour.id)
        self.showCongratulations()
        self.showReviewForm()

    def showCongratulations(self):
        messagebox.showinfo("Поздравляем!", "Вы успешно прошли экскурсию!")

    def showReviewForm(self):
        # Exit-действие формы отзыва (раздел 8 п.6):
        # - при ВХОДЕ создаём черновик через leaveReview (пустой текст, rating=0)
        # - при ВЫХОДЕ (Отправить или Пропустить) вызываем sendReviewToModeration
        if not (self.currentTour and self.currentUser):
            self.navigator("catalog", data=self.currentUser)
            return

        # Создаём черновик при входе
        self._draftReview = self.revCtrl.leaveReview(
            self.currentUser.id, self.currentTour.id, "", 0
        )

        # Диалог формы отзыва
        rating = simpledialog.askinteger("Отзыв", "Оценка (1-5):", minvalue=1, maxvalue=5)
        if rating is not None:
            text = simpledialog.askstring("Отзыв", "Ваш комментарий:") or ""
            # Дописываем тот же объект в памяти
            self._draftReview.rating = rating
            self._draftReview.text = text
            self.revCtrl._reviewRepo.save(self._draftReview)

        # Exit-действие: при любом выходе отправляем на модерацию
        self.revCtrl.sendReviewToModeration(self._draftReview.id)
        self.navigator("catalog", data=self.currentUser)

    def display(self, data):
        self.currentUser = data["user"]
        self.currentTour = self.tourCtrl.startTour(data["tour_id"])
        self.totalSteps = len(self.currentTour.routePoints)
        self.currentStep = 1
        self.displayRouteMap(self.currentTour.routePoints)
        self.displayRoutePoint(self.tourCtrl.getRoutePoint(self.currentTour.id, 1))

    def refresh(self, data):
        pass

class TourBuilderView(BaseView):
    def __init__(self, tourCreationController):
        super().__init__()
        self.controller = tourCreationController
        self.currentUser = None
        self.currentTour = None

        header = ttk.Frame(self)
        header.pack(fill="x", padx=10, pady=10)
        # Exit-действие: sendToModeration при любом выходе (раздел 8 п.2)
        ttk.Button(header, text="Назад", command=self._onBackClicked).pack(side="left")
        ttk.Label(header, text="Создание экскурсии", font=("Arial", 14, "bold")).pack(side="left", padx=20)

        form = ttk.Frame(self, padding=10)
        form.pack(fill="x")
        ttk.Label(form, text="Название:").grid(row=0, column=0, sticky="e")
        self.titleEntry = ttk.Entry(form)
        self.titleEntry.grid(row=0, column=1, sticky="ew")
        ttk.Label(form, text="Город:").grid(row=1, column=0, sticky="e")
        self.cityEntry = ttk.Entry(form)
        self.cityEntry.grid(row=1, column=1, sticky="ew")
        ttk.Label(form, text="Тематика:").grid(row=2, column=0, sticky="e")
        self.themeEntry = ttk.Entry(form)
        self.themeEntry.grid(row=2, column=1, sticky="ew")
        ttk.Label(form, text="Описание:").grid(row=3, column=0, sticky="ne")
        self.descText = tk.Text(form, height=3)
        self.descText.grid(row=3, column=1, sticky="ew")
        ttk.Button(form, text="Сохранить черновик", command=self._onSaveDraftClicked).grid(row=4, column=0, columnspan=2, pady=10)

        self.mapCanvas = tk.Canvas(self, width=400, height=200, bg="lightgreen")
        self.mapCanvas.pack(pady=10)
        self.mapCanvas.bind("<Button-1>", self._onMapClick)

        ttk.Label(self, text="Точки маршрута:").pack()
        self.pointsListbox = tk.Listbox(self, height=5)
        self.pointsListbox.pack()

        btns = ttk.Frame(self)
        btns.pack(pady=10)
        ttk.Button(btns, text="Отправить на публикацию", command=self._onSubmitClicked).pack(side="right", padx=5)

    def _onBackClicked(self):
        # Exit-действие: sendToModeration при любом выходе (раздел 8 п.2)
        if self.currentTour:
            self.controller.sendToModeration(self.currentTour.id)
        self.navigator("cabinet", data=self.currentUser)

    def _onSaveDraftClicked(self):
        self.currentTour = self.controller.createTour(
            self.titleEntry.get(),
            self.cityEntry.get(),
            self.themeEntry.get(),
            self.descText.get("1.0", "end")
        )
        self.currentTour.authorId = self.currentUser.id
        self.mapCanvas.focus_set()
        self.mapCanvas.configure(bg="lightyellow")
        messagebox.showinfo("Успех", "Черновик сохранен. Кликайте по карте.")

    def _onMapClick(self, event):
        if not self.currentTour:
            messagebox.showwarning("Внимание", "Сначала сохраните черновик!")
            return
        self.showAddPointForm(event.x, event.y)

    def showTourCreationForm(self):
        pass

    def displayMapForMarkers(self):
        pass

    def showAddPointForm(self, x, y):
        name = simpledialog.askstring("Точка маршрута", "Название точки:")
        if name:
            desc = simpledialog.askstring("Точка маршрута", "Описание:") or ""
            imagePath = filedialog.askopenfilename(title="Выберите фото", filetypes=[("Images", "*.jpg *.png *.jpeg")])
            imageName = imagePath.split("/")[-1] if imagePath else "new.jpg"
            from model.data import RoutePoint
            import uuid
            point = RoutePoint(
                id=uuid.uuid4().hex,
                tourId=self.currentTour.id,
                title=name,
                orderNumber=len(self.pointsListbox.get(0, "end")) + 1,
                coordinates=f"{x},{y}",
                image=imageName,
                description=desc
            )
            self.controller.addRoutePoint(self.currentTour.id, point)
            self.mapCanvas.create_oval(x - 10, y - 10, x + 10, y + 10, fill="red")
            self.mapCanvas.create_text(x, y - 15, text=str(point.orderNumber))
            self.pointsListbox.insert("end", f"Точка {point.orderNumber}: {name}")

    def _onSubmitClicked(self):
        # Exit-действие: sendToModeration (дублируется, но так по диаграмме)
        if self.currentTour:
            self.controller.sendToModeration(self.currentTour.id)
            self.displayModerationStatus()

    def displayModerationStatus(self):
        messagebox.showinfo("Статус", "Экскурсия отправлена на модерацию!")
        self.navigator("catalog", data=self.currentUser)

    def display(self, data):
        self.currentUser = data
        self.showTourCreationForm()
        self.displayMapForMarkers()

    def refresh(self, data):
        pass

class PersonalCabinetView(BaseView):
    def __init__(self, personalCabinetController):
        super().__init__()
        self.controller = personalCabinetController
        self.currentUser = None
        self.extensionSlot = ttk.Frame(self)
        self.extensionSlot.pack(fill="x", padx=10)

        header = ttk.Frame(self)
        header.pack(fill="x", padx=10, pady=10)
        ttk.Button(header, text="Назад", command=lambda: self.navigator("catalog", data=self.currentUser)).pack(side="left")
        ttk.Label(header, text="Личный кабинет", font=("Arial", 14, "bold")).pack(side="left", padx=20)
        ttk.Button(header, text="Права администратора", command=lambda: self.navigator("request_admin", data=self.currentUser)).pack(side="right")

        self.profileLbl = ttk.Label(self, text="", font=("Arial", 12))
        self.profileLbl.pack(pady=10)

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10)
        self.favFrame = ttk.Frame(self.notebook)
        self.notebook.add(self.favFrame, text="Избранное")
        self.createdFrame = ttk.Frame(self.notebook)
        self.notebook.add(self.createdFrame, text="Мои маршруты")
        self.completedFrame = ttk.Frame(self.notebook)
        self.notebook.add(self.completedFrame, text="Пройденные")
        self.achFrame = ttk.Frame(self.notebook)
        self.notebook.add(self.achFrame, text="Достижения")

        ttk.Button(self, text="Создать экскурсию", command=lambda: self.navigator("tourBuilder", data=self.currentUser)).pack(pady=10)

    def _renderList(self, parent, tours):
        for w in parent.winfo_children():
            w.destroy()
        if not tours:
            ttk.Label(parent, text="Пусто").pack()
        for t in tours:
            ttk.Label(parent, text=f"- {t.title} ({t.status})").pack(anchor="w", pady=2)

    def displayProfile(self, user):
        self.profileLbl.config(text=f"Профиль: {user.nickname} ({user.email})")

    def displayCompletedTours(self, tours):
        self._renderList(self.completedFrame, tours)

    def displayCreatedTours(self, tours):
        self._renderList(self.createdFrame, tours)

    def displayFavoriteTours(self, tours):
        self._renderList(self.favFrame, tours)

    def displayAchievements(self, achievements):
        for w in self.achFrame.winfo_children():
            w.destroy()
        if not achievements:
            ttk.Label(self.achFrame, text="Нет достижений").pack()
        for a in achievements:
            ttk.Label(self.achFrame, text=f"{a.icon} {a.title} — {a.description}").pack(anchor="w", pady=2)

    def display(self, data):
        self.currentUser = data
        self.displayProfile(self.controller.getProfile(self.currentUser.id))
        self.displayCompletedTours(self.controller.getCompletedTours(self.currentUser.id))
        self.displayCreatedTours(self.controller.getCreatedTours(self.currentUser.id))
        self.displayFavoriteTours(self.controller.getFavoriteTours(self.currentUser.id))
        self.displayAchievements(self.controller.getAchievements(self.currentUser.id))

    def refresh(self, data):
        pass

class AdminPanelView(BaseView):
    def __init__(self, moderationController, complaintController):
        super().__init__()
        self.modCtrl = moderationController
        self.compCtrl = complaintController

        header = ttk.Frame(self)
        header.pack(fill="x", padx=10, pady=10)
        ttk.Label(header, text="Панель администратора", font=("Arial", 14, "bold")).pack(side="left", padx=20)

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10)
        self.toursTab = ttk.Frame(self.notebook)
        self.notebook.add(self.toursTab, text="Маршруты")
        self.reviewsTab = ttk.Frame(self.notebook)
        self.notebook.add(self.reviewsTab, text="Отзывы")
        self.complaintsTab = ttk.Frame(self.notebook)
        self.notebook.add(self.complaintsTab, text="Жалобы")

    def _renderModList(self, parent, items, isTour):
        for w in parent.winfo_children():
            w.destroy()
        for item in items:
            frm = ttk.Frame(parent)
            frm.pack(fill="x", pady=5)
            title = item.title if isTour else item.text
            ttk.Label(frm, text=title).pack(side="left")
            ttk.Button(frm, text="Одобрить", command=lambda i=item: self._approve(i, isTour)).pack(side="right", padx=5)
            ttk.Button(frm, text="Отклонить", command=lambda i=item: self._reject(i, isTour)).pack(side="right")

    def _approve(self, item, isTour):
        if isTour:
            self.modCtrl.approveTour(item.id)
        else:
            self.modCtrl.approveReview(item.id)
        self.showModerationResult(True)

    def _reject(self, item, isTour):
        if isTour:
            self.modCtrl.rejectTour(item.id)
        else:
            self.modCtrl.rejectReview(item.id)
        self.showModerationResult(True)

    def displayToursForModeration(self, tours):
        self._renderModList(self.toursTab, tours, isTour=True)

    def displayReviewsForModeration(self, reviews):
        self._renderModList(self.reviewsTab, reviews, isTour=False)

    def displayComplaints(self, complaints):
        for w in self.complaintsTab.winfo_children():
            w.destroy()
        for c in complaints:
            frm = ttk.Frame(self.complaintsTab)
            frm.pack(fill="x", pady=5)
            ttk.Label(frm, text=f"Жалоба на {c.objectType} {c.objectId}: {c.description}").pack(side="left")
            ttk.Button(frm, text="Принять", command=lambda cid=c.id: self._resolveComp(cid, DECISION_ACCEPTED)).pack(side="right", padx=5)
            ttk.Button(frm, text="Отклонить", command=lambda cid=c.id: self._resolveComp(cid, DECISION_DECLINED)).pack(side="right")

    def _resolveComp(self, cid, decision):
        self.compCtrl.reviewComplaint(cid, decision)
        self.showModerationResult(True)

    def showModerationResult(self, success):
        if success:
            self.displayToursForModeration(self.modCtrl.getToursForModeration())
            self.displayReviewsForModeration(self.modCtrl.getReviewsForModeration())
            self.displayComplaints(self.compCtrl.getComplaintsForModeration())
            messagebox.showinfo("Успех", "Действие выполнено.")

    def display(self, data):
        self.displayToursForModeration(self.modCtrl.getToursForModeration())
        self.displayReviewsForModeration(self.modCtrl.getReviewsForModeration())
        self.displayComplaints(self.compCtrl.getComplaintsForModeration())

    def refresh(self, data):
        pass

class GoodbyeView(BaseView):
    def __init__(self):
        super().__init__()
        self.label = ttk.Label(self, text="До свидания!", font=("Arial", 24))
        self.label.pack(expand=True)

    def display(self, data):
        pass

    def refresh(self, data):
        pass
