from django.shortcuts import render

class ViewFactory:
    @staticmethod
    def get_renderer(request, role):
        templates={
            'creador': 'creador_home.html',
            'participante': 'participante_home.html'
        }
        template = templates.get(role, 'login.html')
        return render(request, template)