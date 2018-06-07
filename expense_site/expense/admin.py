from django.contrib import admin
from django.db import models
from django.forms import TextInput, Textarea
from .models import Files, Expense, Category, Names


class FilesAdmin(admin.ModelAdmin):
    list_display = ['get_file_expenses_link', 'file_name', 'get_file_total']
    ordering = ['-file_name']


admin.site.register(Files,FilesAdmin)


class NamesAdmin(admin.ModelAdmin):
    list_display= ['name', 'cat']
    search_fields = ['name']
    list_editable = ['cat']

admin.site.register(Names, NamesAdmin)


def function_creator(i):
    def func(ma,request,queryset):
        for item in queryset:
            name = Names.objects.get_or_create(name=item.name_id)[0]
            name.cat_id = i
            name.save()
            #queryset.update(name__cat__id=i)
    func.short_description = "Set Category %s" % Category.objects.get(id=i).name
    return (func, func.short_description,func.short_description)


class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('get_file_name', 'date', 'name_id', 'total', 'charge', 'charge_number', 'total_charges', 'notes', 'get_cat')
    list_filter = ['date', 'name__cat__name']
    search_fields = ['name__name', 'file__file_name', 'notes']
    actions = [("Set Category %s"%Category.objects.get(id=i.id).name, function_creator(i.id)) for i in Category.objects.all()]

    def get_actions(self, request):
        return dict(self.actions)

admin.site.register(Expense, ExpenseAdmin)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    list_editable = ['name']
    ordering = ['id']
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size':'20'})},
        models.TextField: {'widget': Textarea(attrs={'rows':1, 'cols':40})},
    }

admin.site.register(Category, CategoryAdmin)


