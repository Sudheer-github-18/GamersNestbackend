"""
URL configuration for src project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from rest_framework.routers import DefaultRouter
from userauths.schemas.api import schema_view
from userauths import views as userauths_views
from core import views as core_views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)
from userauths.views import ObtainTokenPairWithFacebook, ProfileUpdateView

from allauth.account.views import LoginView

from django.conf import settings
from django.conf.urls.static import static

from userauths.facebook import FacebookLogin




router = DefaultRouter()
router.register("user",userauths_views.UserViewSet, basename="user")
router.register('friend-requests', core_views.FriendRequestViewSet,basename="friends")
router.register('friends', core_views.FriendViewSet,basename="friend")
#router.register('profile',userauths_views.UserProfileViewSet,basename="social-auth")


urlpatterns = [
    path('admin/', admin.site.urls),
    path('token/', ObtainTokenPairWithFacebook.as_view(), name='token_obtain_pair_facebook'),
    path('api/user/<uuid:pk>/',
         userauths_views.UserDetailView.as_view(), name='user-detail'),
    path('', include(router.urls)),
   #path('profile/', UserProfileViewSet.as_view({'put': 'update'}), name='profile-update'),
    path('api/', include('rest_framework.urls')),
    path('accounts/', include('allauth.urls')),
    path('accounts/', include('allauth.socialaccount.urls')),
    path('social/', include('social_django.urls', namespace='social')),
    path('dj-rest-auth/', include('dj_rest_auth.urls')),
    path('dj-rest-auth/facebook/', FacebookLogin.as_view(), name='fb_login'),
    path('dj-rest-auth/registration/', include('dj_rest_auth.registration.urls')),
    path('dj-rest-auth/social/', include('allauth.socialaccount.urls')),
    path('accounts/facebook/login/callback/', LoginView.as_view(), name='facebook_login_callback'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),

    path('profile/update/', ProfileUpdateView.as_view(), name='profile-update'),

]

urlpatterns += router.urls


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
