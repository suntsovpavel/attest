from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse
from django.shortcuts import redirect, render
from .forms import LoginForm, RecipeForm, EditRecipeForm
from datetime import datetime
from django.core.files.storage import FileSystemStorage
import random

from .models import MyUser, Recipe, Category

# Главная с 5 случайными рецептами кратко
def index(request):                                             
    NUM_RECIPES = 5
    # Случайным образом выбираем NUM_RECIPES рецептов:  
    all_recipes = Recipe.objects.all()    
    indexes = [i for i in range(len(all_recipes))]    
    data_recipes = []
    count = 0    
    while len(indexes) > 0 and count < NUM_RECIPES:        
        index = indexes.pop(random.randint(0, len(indexes)-1)) 
        data_recipes.append({'recipe': all_recipes[index], 
                            'short_desc': all_recipes[index].short_desc()})   
        count += 1

    return render(request, 'myapp/index.html', {'title': 'Главная', 
                                                'data_recipes': data_recipes})   

# Страница авторизации
def my_login(request):
    # !!! Если авторизованный пользователь вошел на страницу авторизации - отменяем авторизацию:
    if request.user.is_authenticated:
        logout(request)

    if request.method == 'POST':
        form = LoginForm(request.POST)               
        if form.is_valid():    
            username = form.cleaned_data['name']    
            password = form.cleaned_data['password']    
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                # Проверяем, внесен ли пользователь в список MyUser. Если нет - добавляем
                myUser = MyUser.objects.filter(username=username).first()
                if myUser is None:
                    myUser = MyUser(username=username, date_register=datetime.now())
                    myUser.save()
                return redirect('/')                
            else:
                message = 'Логин либо пароль некорректны!' 
        else:
            message = 'Некорректный формат введенных данных!'                
    else:
        message = 'Введите логин и пароль'
        form = LoginForm()
    return render(request, 'myapp/login.html', {'title': 'Авторизация', 
                                                'message': message,
                                                'form':form})

# Страница регистрации 
# Используем готовую форму ввода данных регистрации UserCreationForm
def my_reg(request):    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():    
            form.save()
            username = form.cleaned_data['username']    
            password = form.cleaned_data['password1']    
            user = authenticate(request, username=username, password=password)
            login(request, user)
            myUser = MyUser(username=username, date_register=datetime.now())
            myUser.save()
            return redirect('/')
        else:
            message = 'Некорректный формат введенных данных!'                
    else:
        message = 'Регистрация нового пользователя'
        form = UserCreationForm()
    return render(request, 'myapp/reg.html', {'title': 'Регистрация', 
                                                'message': message,
                                                'form':form})

# Страница выхода (де-авторизации)
def my_logout(request): 
    if request.user.is_authenticated:
        logout(request)
    return redirect('/')

# Страница добавления рецепта
# Доступна только для авторизованного пользователя
def add_recipe(request):
    # Неавторизованных пользователей перебрасываем на страницу авторизации:
    if not request.user.is_authenticated:
        return redirect('/login/')
    
    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES)     
        if form.is_valid():   
            myUser = MyUser.objects.filter(username=request.user.username).first()
            if myUser is None:
                return HttpResponse(f'!!! Пользователь {request.user.username} отсутствует в базе!!!')
            else:                        
                category = form.cleaned_data['category']    
                if len(category) > 0:
                    name = form.cleaned_data['name']    
                    desc = form.cleaned_data['desc']    
                    cooking_steps = form.cleaned_data['cooking_steps']    
                    time_cooking = form.cleaned_data['time_cooking']                        
                    image = form.cleaned_data['image']  
                    fs = FileSystemStorage()
                    fs.save(image.name, image)
                
                    recipe = Recipe(author=myUser,
                                    name=name,
                                    desc=desc,
                                    cooking_steps=cooking_steps,
                                    time_cooking=time_cooking,
                                    image=image,
                                    date = datetime.now())    
                    recipe.save()
                    for name in category:
                        c = Category.objects.filter(name=name).first()
                        recipe.categories.add(c)
                    message = 'Рецепт успешно добавлен!'                     
                else:
                    message = 'Выберите как минимум одну категорию!'    
        else:
            message = 'Некорректные данные'    
    else:
        message = 'Новый рецепт. Заполните форму'
        form = RecipeForm()        
    return render(request, 'myapp/add_recipe.html', {'title': 'Новый рецепт', 
                                                    'message': message,
                                                    'form':form})   

# Страница редактирования рецепта
# Доступна только для авторизованного пользователя, который является автором рецепта
def edit_recipe(request):
    # Неавторизованных пользователей перебрасываем на страницу авторизации:
    if not request.user.is_authenticated:
        return redirect('/login/')
    
    # Выборка рецептов текущего пользователя:
    myUser = MyUser.objects.filter(username=request.user.username).first()
    recipes = Recipe.objects.select_related('author').filter(author=myUser)
    if len(recipes) == 0:
        message = f'У пользователя {request.user.username} нет рецептов для редактирования'
        return render(request, 'myapp/message_out.html', {'title': 'Сообщение', 'content': message})

    if request.method == 'POST':
        form = EditRecipeForm(request.POST, request.FILES, recipes=recipes)     
        if form.is_valid():   
            category = form.cleaned_data['category']    
            if len(category) > 0:
                select_recipe = form.cleaned_data['select_recipe']    
                recipe = Recipe.objects.filter(name=select_recipe).first()                                    

                recipe.name = form.cleaned_data['name']    
                recipe.desc = form.cleaned_data['desc']    
                recipe.cooking_steps = form.cleaned_data['cooking_steps']    
                recipe.time_cooking = form.cleaned_data['time_cooking']                    
                recipe.image = form.cleaned_data['image']  
                recipe.date = datetime.now()
                recipe.save()                
                for name in category:
                    c = Category.objects.filter(name=name).first()
                    if not c in recipe.categories.all():
                        recipe.categories.add(c)
                
                fs = FileSystemStorage()
                fs.save(recipe.image.name, recipe.image)

                message = 'Рецепт успешно изменен!' 

                # обновляем список recipes и отображение Select recipe в форме
                recipes = Recipe.objects.select_related('author').filter(author=myUser)
                form = EditRecipeForm(recipes=recipes)        
            else:
                message = 'Выберите как минимум одну категорию!'    
        else:
            message = 'Некорректные данные'    
    else:
        message = 'Редактирование рецепта. Заполните форму'
        form = EditRecipeForm(recipes=recipes)        
    return render(request, 'myapp/add_recipe.html', {'title': 'Редактировать рецепт', 
                                                    'message': message,
                                                    'form':form})      

# Страница с одним подробным рецептом
def show_recipe(request, pk:int):
    recipe = Recipe.objects.filter(pk=pk).first()
    if recipe is None:
        # Выводим названия всех рецептов в БД на выбор
        list_id = [recipe.pk for recipe in Recipe.objects.all()]
        message = f'Введен некорректный id.\nИмеются в наличии: {list_id}'
        return render(request, 'myapp/message_out.html', {'title': 'Сообщение', 'content': message})       
    else:
        print(recipe.categories.all())
        return render(request, 'myapp/show_recipe.html', {'title': 'Показать рецепт',                                                        
                                                        'recipe':recipe,                                                        
                                                        'categories': '; '.join([x.get_name() for x in recipe.categories.all()])})         

# формируем вспомогательную таблицу категорий
# def fill_categories(request):  
#     # удаляем все существующие записи в БД
#     c = Category.objects.last()  
#     while c is not None: 
#         c.delete()
#         c = Category.objects.last()         

#     categories = ['выпечка',
#                   'мясная продукция',
#                   'молочная продукция',
#                   'салаты',
#                   'супы',
#                   'легкие закуски',
#                   'первые блюда',
#                   'вторые блюда',
#                   'напитки',
#                   'десерты',
#                   ]
#     for index,name in enumerate(categories):
#         cat = Category(name=name, desc=f'some description{index}')
#         cat.save()
#     return redirect('/')


