from cmath import log
from re import L
from django.shortcuts import redirect, render
from main_app.forms import FeedingForm
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from .models import Cat, Toy, Photo
import boto3, uuid
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

S3_BASE_URL = 'https://s3.us-east-1.amazonaws.com/'
BUCKET = 'catcollector-avatar-cn'

# Create your views here.
def home(request):
  return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

# class Cat:  # Note that parens are optional if not inheriting from another class
#   def __init__(self, name, breed, description, age):
#     self.name = name
#     self.breed = breed
#     self.description = description
#     self.age = age

# cats = [
#   Cat('Lolo', 'tabby', 'foul little demon', 3),
#   Cat('Sachi', 'tortoise shell', 'diluted tortoise shell', 0),
#   Cat('Raven', 'black tripod', '3 legged cat', 4),
#   Cat('Bryan', 'Weak', 'weak and lacking', 16),
# ]

@login_required
def cat_index(request):
    cats = Cat.objects.filter(user=request.user) # shows cats for logged in user ...
    return render(request, 'cats/index.html', {'cats': cats})

@login_required
def cats_detail(request, cat_id):
    cat = Cat.objects.get(id=cat_id)
    # instantiate FeedingForm to be rendered in template
    toys_cat_doesnt_have = Toy.objects.exclude(id__in = cat.toys.all().values_list('id'))
    feeding_form = FeedingForm()
    return render(request, 'cats/details.html', { 'cat': cat, 
    'feeding_form': feeding_form, 'toys': toys_cat_doesnt_have})

@login_required
def add_feeding(request, cat_id):
    form = FeedingForm(request.POST) # create ModelForm using data in req.post
    if form.is_valid():
        new_feeding = form.save(commit=False)
        new_feeding.cat_id = cat_id
        new_feeding.save()
        return redirect('detail', cat_id=cat_id)

@login_required
def assoc_toy(request, cat_id, toy_id):
    Cat.objects.get(id=cat_id).toys.add(toy_id)
    return redirect('detail', cat_id=cat_id)

@login_required
def assoc_toy_delete(request, cat_id, toy_id):
  Cat.objects.get(id=cat_id).toys.remove(toy_id)
  return redirect('detail', cat_id=cat_id)

@login_required
def add_photo(request, cat_id):
  # attempt to collect the photo file data
  photo_file = request.FILES.get('photo-file', None)
  # use conditional logic to determine if file is present
  if photo_file:
  # if it's present, we will create a reference the the boto3 client
    s3 = boto3.client('s3')
    # create a unique id for each photo file
    key = uuid.uuid4().hex[:6] + photo_file.name[photo_file.name.rfind('.'):]
    # funny_cat.png = jdbw7f.png
    # upload the photo file to aws s3
    try:
    # if successful
      s3.upload_fileobj(photo_file, BUCKET, key)
      # take the exchanged url and save it to the database
      url = f"{S3_BASE_URL}{BUCKET}/{key}"
      # 1) create photo instance with photo model and provide cat_id as foreign key val
      photo = Photo(url=url, cat_id=cat_id)
      # 2) save the photo instance to the database
      photo.save()
    except Exception as error:
      print("Error uploading photo: ", error)
      return redirect('detail', cat_id=cat_id)
    # print an error message
  return redirect('detail', cat_id=cat_id)
  # redirect the user to the origin 


"""
    check if the request method is POST,
    we need to create a new user because from was submitted
    
    1) use the form data from the request to create a form/model instance from the model form
    2) validate the form to ensure it was completed
      2.2) if form not valid - redirect the user to the signup page with an error message
    3) saving the user object to the database
    4) login the user (creates a session for the logged in user in the database)
    5) redirect the user to the cats index page
  """

"""
    else the request is GET == the user clicked on the signup link
    1) create a blank instance of the model form
    2) provide that form instance to a registration template
    3) render the template so the user can fill out the form
  """

def signup(request):
    error_messages = ''
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
        else:
            error_messages = 'Invalid Info - Try Again'
    form = UserCreationForm()
    return render(request, 'registration/signup.html', {
        'form': form,
        'error_messages': error_messages
    })

class CatCreate(LoginRequiredMixin, CreateView):
  model = Cat
  fields = ['name', 'breed', 'description', 'age']
  success_url = '/cats/'

  def form_valid(self, form):
    form.instance.user = self.request.user
    return super().form_valid(form)

class CatUpdate(LoginRequiredMixin, UpdateView):
    model = Cat
    fields = ['breed', 'description', 'age']

class CatDelete(LoginRequiredMixin, DeleteView):
    model = Cat
    success_url = '/cats/'

class ToyList(LoginRequiredMixin, ListView):
  model = Toy
  template_name = 'toys/index.html'

class ToyDetail(LoginRequiredMixin, DetailView):
  model = Toy
  template_name = 'toys/detail.html'

class ToyCreate(LoginRequiredMixin, CreateView):
    model = Toy
    fields = ['name', 'color']

class ToyUpdate(LoginRequiredMixin, UpdateView):
    model = Toy
    fields = ['name', 'color']

class ToyDelete(LoginRequiredMixin, DeleteView):
    model = Toy
    success_url = '/toys/'