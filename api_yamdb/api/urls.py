from django.urls import include, path
from rest_framework.routers import SimpleRouter

from . import views

app_name = 'api'

router = SimpleRouter()
router.register('users', views.UsersViewSet)
router.register('categories', views.CategoryViewSet)
router.register('genres', views.GenreViewSet)
router.register('titles', views.TitleViewSet)
router.register(
    r'titles/(?P<title_id>\d+)/reviews',
    views.ReviewViewSet, basename='reviews'
)
router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    views.CommentViewSet,
    basename='comments',
)
urlpatterns = [
    path('v1/auth/signup/', views.SignUpApiView.as_view(), name='signup'),
    path('v1/auth/token/', views.GetTokenApiView.as_view(), name='token'),
    path('v1/users/me/', views.SelfEditApiView.as_view(), name='self_edit'),
    path('v1/', include(router.urls)),
]
