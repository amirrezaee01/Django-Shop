from django.contrib.auth.mixins import UserPassesTestMixin
from accounts.models import UserType


class HasCustomerAccessPermison(UserPassesTestMixin):
    """
    Custom permission to check if the user has access to customer-related views.
    """

    def test_func(self):
        if self.request.user.is_authenticated:
            return self.request.user.type == UserType.customer.value
        return False


class HasAdminAccessPermison(UserPassesTestMixin):
    """
    Custom permission to check if the user has access to customer-related views.
    """

    def test_func(self):
        if self.request.user.is_authenticated:
            return self.request.user.type == UserType.admin.value
        return False
