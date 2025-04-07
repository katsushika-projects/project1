from django.urls import path

from . import views

app_name = "items"

urlpatterns = [
    path("", views.ItemListView.as_view()),
    path("create/", views.ItemCreateAPIView.as_view()),
    path("<uuid:pk>/", views.ItemRetrieveUpdateDestroyView.as_view()),
    path("<uuid:pk>/purchase/", views.ItemPurchaseView.as_view()),
    path("<uuid:pk>/cancel/", views.ItemCancelView.as_view()),
    path("<uuid:pk>/relisting/", views.ItemReListingView.as_view()),
    path("<uuid:pk>/complete/", views.ItemCompleteView.as_view()),
    path("<uuid:pk>/like-toggle/", views.ItemLikeToggleView.as_view()),
    path("<uuid:pk>/report/", views.ReportAPIView.as_view()),
    path("user/like/", views.UserLikeItemListView.as_view()),
    path("user/sell/", views.UserSellItemListView.as_view()),
    path("user/buy/", views.UserBuyItemListView.as_view()),
]
