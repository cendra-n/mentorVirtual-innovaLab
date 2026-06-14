from django.urls import path
from .views import BookListView, BookDetailView, AskStepView

urlpatterns = [
    path('books/',                   BookListView.as_view(),   name='tutor-books'),
    path('books/<int:book_id>/',     BookDetailView.as_view(), name='tutor-book-detail'),
    
    path('ask_step/',                AskStepView.as_view(),    name='tutor-ask-step'),
]
