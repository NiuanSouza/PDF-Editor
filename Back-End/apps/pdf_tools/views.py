from django.views.generic import TemplateView

class MergeView(TemplateView):
    template_name = 'pdf_tools/merge.html'
