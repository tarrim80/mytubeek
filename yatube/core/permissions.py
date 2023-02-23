from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy


class AuthorPermissionMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.get_object().author == self.request.user

    def handle_no_permission(self):
        if self.raise_exception or not self.request.user.is_authenticated:
            return super().handle_no_permission()
        return redirect(reverse_lazy('posts:index'))
