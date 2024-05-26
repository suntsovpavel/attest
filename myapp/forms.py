from django import forms
from .models import Category, Recipe, MyUser

class LoginForm(forms.Form):
    name = forms.CharField(max_length=100)
    password = forms.CharField(max_length=100, widget=forms.PasswordInput())
    
class RecipeForm(forms.Form):        
    name = forms.CharField(max_length=100, required=True)
    desc = forms.CharField(max_length=2000, required=True,
                                widget=forms.Textarea(attrs={
                                    'class': 'form-control',
                                    'placeholder': 'Enter description'
                                }))
    cooking_steps = forms.CharField(max_length=2000, required=True,
                                widget=forms.Textarea(attrs={
                                    'class': 'form-control',
                                    'placeholder': 'Enter description'
                                }))
    time_cooking = forms.TimeField(required=True, widget=forms.DateInput(attrs={
                                   'class': 'form-control',
                                   'type': 'time'
                               }))  
    image = forms.ImageField() 
    category = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple(), 
                                         choices=set((x.name, x.name) for x in Category.objects.all()))  
    
#  RecipeForm  + name_for_search (выпадающий список имен рецептов для редактирования)
# class EditRecipeForm(forms.Form):  
class EditRecipeForm(forms.Form): 
    select_recipe = forms.ChoiceField()

    name = forms.CharField(max_length=100, required=True)

    desc = forms.CharField(max_length=2000, required=True,
                                widget=forms.Textarea(attrs={
                                    'class': 'form-control',
                                    'placeholder': 'Enter description'
                                }))
    cooking_steps = forms.CharField(max_length=2000, required=True,
                                widget=forms.Textarea(attrs={
                                    'class': 'form-control',
                                    'placeholder': 'Enter description'
                                }))
    time_cooking = forms.TimeField(required=True, widget=forms.DateInput(attrs={
                                   'class': 'form-control',
                                   'type': 'time'
                               }))  
    image = forms.ImageField() 
    category = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple(), 
                                         choices=set((x.name, x.name) for x in Category.objects.all())) 
    
    def __init__(self, *args, **kwargs):        
        self.recipes = kwargs.pop('recipes', None)      # передаем в форму список рецептов, доступных для редактирования
        super(EditRecipeForm, self).__init__(*args, **kwargs) 
        if self.recipes is not None:
            self.fields['select_recipe'].choices = [(x.name, x.name) for x in self.recipes]
            self.fields['select_recipe'].default = (self.recipes[0].name, self.recipes[0].name) 
