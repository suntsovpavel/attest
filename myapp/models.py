from django.db import models

class MyUser(models.Model):
    username = models.CharField(max_length=100)
    date_register = models.DateField()

    def __str__(self):
        return f'Логин: {self.username}, дата регистрации: {self.date_register}'

# Категории рецептов:
# ○ Название
# ○ *другие поля на ваш выбор
class Category(models.Model):
    name = models.CharField(max_length=100)
    desc = models.TextField()

    def __str__(self):
        return f'name: {self.name}, description:{self.desc}'
    
    def get_name(self):
        return self.name
    
class Ingredient(models.Model):
    name = models.CharField(max_length=100)   

    def __str__(self):
        return f'name: {self.name}'   
    
# модель Рецепт:
# - Автор(пользователь)
# - Название
# - Описание
# - Шаги приготовления
# - Время приготовления
# - дата создания/последней редакции
# - Изображение
# - список категорий
class Recipe(models.Model):
    author = models.ForeignKey(MyUser, on_delete=models.CASCADE)        
    name = models.CharField(max_length=100)
    desc = models.TextField()
    cooking_steps = models.TextField()
    time_cooking = models.TimeField()    
    date = models.DateField()       # дата создания либо последней редакции 
    image = models.ImageField() 
    categories = models.ManyToManyField(Category)

    NUM_WORDS = 30
    def short_desc(self):       # краткое описание
        splited = self.desc.split()        
        return ' '.join(splited[:self.NUM_WORDS])+' ...' if len(splited)>self.NUM_WORDS else self.desc

    def __str__(self):
        
        return f'name: {self.name}, short description: "{self.short_desc()}", by author: {self.author}'     