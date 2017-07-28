from django.shortcuts import render, redirect
from django.conf import settings
from django.core.files.storage import FileSystemStorage

from uploads.core.models import Document
from uploads.core.forms import DocumentForm


def home(request):
    documents = Document.objects.all()
    return render(request, 'core/home.html', { 'documents': documents })

def search(request):
    '''  '''
    return render(request, 'core/index.html')

def simple_upload(request):
    if request.method == 'POST':
        if myfile not in request.FILES:
            print "No file uploaded"
            return redirect ('core/simple_upload.html')
        else:
            myfile = request.FILES['myfile']
            fs = FileSystemStorage()
            filename = fs.save(myfile.name, myfile)
            uploaded_file_url = fs.url(filename)
            return render(request, 'core/simple_upload.html', {
                'uploaded_file_url': uploaded_file_url
            })
    else:
        return redirect('core/simple_upload.html')


def model_form_upload(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = DocumentForm()
    return render(request, 'core/model_form_upload.html', {
        'form': form
    })

def login(request):
    ''' Renders /login URL '''
    return render(request, 'core/login.html')

def register(request):
    errors = User.objects.user_validator(request.POST)
    if errors:
        for tag, error in errors.iteritems():
            messages.error(request, error, extra_tags=tag)
        return redirect('/')
    else:
        # query for username
        q = User.objects.filter(username=request.POST['username'])
        if q.count() > 0:
            # check for existing user
            messages.error(request, "A user account with that username already \
            exists", extra_tags="username")
            return redirect('/')
        else:
            hashed_pw = bcrypt.hashpw(request.POST['password'].encode(), bcrypt.gensalt())
            q = User.objects.create(name = request.POST['name'], username = request.POST['username'], password=hashed_pw)
            request.session['user_id'] = q.id
            request.session['username'] = q.username
            return redirect('/success')
    return redirect('/')

def log_in(request):
    # check user for that username
    # then check password
    found_users = User.objects.filter(username=request.POST['username'])
    if found_users.count() > 0:
        # check password
        found_user = found_users.first()
        if bcrypt.checkpw(request.POST['password'].encode(), found_user.password.encode()) is True:
            # log in user
            request.session['user_id'] = found_user.id  # user_id from username query
            request.session['username'] = found_user.username
            return redirect('/success')
        else:
            messages.error(request, "Login Failed", extra_tags="username")
            return redirect('/')
    else:
        messages.error(request, "Invalid login", extra_tags="username")
        return redirect('/')

def success(request):
    ''' Redirects user to /home if user passes login() or register() '''
    return redirect('/')