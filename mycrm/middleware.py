from django.urls import reverse
from django.http import HttpResponseRedirect

class ValidLogin:

    def __init__(self, get_response) -> None:
        self.get_response = get_response

    def __call__(self, request):

        if not request.user.is_authenticated and request.path.split('/')[1] not in (
            reverse('login').split('/')[1], 'admin'
            ):
            return HttpResponseRedirect(reverse('login'))

        return self.get_response(request)
