from django.urls import path
from .views import BookListView, BookDetailView, AskStepView, BookAskView, PulsoChatView

urlpatterns = [
    path('books/',                   BookListView.as_view(),   name='tutor-books'),
    path('books/<int:book_id>/',     BookDetailView.as_view(), name='tutor-book-detail'),
    path('books/<int:book_id>/ask/', BookAskView.as_view(),    name='tutor-book-ask'),

    path('ask_step/',                AskStepView.as_view(),    name='tutor-ask-step'),
    path('chat/',                    PulsoChatView.as_view(),  name='tutor-chat'),
]
