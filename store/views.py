import datetime
from django.http import Http404
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from store.models import *
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from store.models import Book, BookCopy, UserRating
# Create your views here.

def index(request):
    return render(request, 'store/index.html')

def bookDetailView(request, bid):
    template_name = 'store/book_detail.html'

    avail = []
    for i in Book.objects.all():
        avail.append(i.id)
    
    if bid in avail:
        books = Book.objects.filter(id = bid).first()
        num = BookCopy.objects.filter(book = books).filter(status = True).count()
    else:
        raise Http404('Book does not exist')

    avgratings = UserRating.objects.filter(book = books)
    r = 0
    if len(avgratings) != 0:
        for i in avgratings:
            r += i.rating
        r /= len(avgratings)
    books.rating = round(r, 2)
    books.save()
    if request.user.is_authenticated and avgratings.count() > 0:
        avgratings = avgratings.filter(user_id = request.user.id).first()
        if avgratings != None:
            avgratings = avgratings.rating
    else:
        avgratings = None
    context = {
        'book': books,
        'num_available': num,
        'usrating': avgratings,
    }

    return render(request, template_name, context=context)


@csrf_exempt
def bookListView(request):
    template_name = 'store/book_list.html'
    get_data = request.GET

    books = Book.objects.all()
    if 'title' in get_data.keys():
        books = books.filter(title__icontains = get_data['title'])
    if 'author' in get_data.keys():
        books = books.filter(author__icontains = get_data['author'])
    if 'genre' in get_data.keys():
        books = books.filter(genre__icontains = get_data['genre'])

    context = {
        'books': books,
    }
    for i in books:
        x = UserRating.objects.filter(book = i)
        r = 0
        if len(x) != 0:
            for i in x:
                r += i.rating
            r /= len(x)
        i.rating = round(r, 2)
        i.save()

    return render(request, template_name, context=context)

@login_required
def viewLoanedBooks(request):
    template_name = 'store/loaned_books.html'

    books = BookCopy.objects.filter(borrower = request.user)
    context = {
        'books': books,
    }
    return render(request, template_name, context=context)

@csrf_exempt
@login_required
def loanBookView(request):
    
    '''
    Check if an instance of the asked book is available.
    If yes, then set the message to 'success', otherwise 'failure'
    '''
    book_id = request.POST['bid']
    books = BookCopy.objects.filter(book_id = book_id, status = True)
    if books.count() > 0:
        msg = 'success' 
        books = books.first()
        books.status = False
        books.borrower = request.user
        books.borrow_date = datetime.date.today()
        books.save()
    else:
        msg = 'failure'
    response_data = {
        'message': msg,
    }
    return JsonResponse(response_data)


@csrf_exempt
@login_required
def returnBookView(request):
    id = request.POST['bid']
    book = BookCopy.objects.filter(id = id, status = False).first()
    if (book is not None):
        book.status = True
        book.borrower = None
        book.borrow_date = None
        book.save()
        msg = 'success'
    else:
        msg = 'failure'
    response_data = {
        'message': msg,
    }
    return JsonResponse(response_data)


@csrf_exempt
@login_required
def ChangeRatingView(request):
    book_id = request.POST['bid']
    value = request.POST['value']
    book = UserRating.objects.filter(book_id = book_id, user = request.user)
    if len(book) != 0:
        book = book.first()
        book.rating = value
        book.save()
    else:
        b = Book.objects.filter(id = book_id)[0]
        bnb = UserRating(book = b, user = request.user, rating = value)
        bnb.save()


    avgratings = UserRating.objects.filter(book_id = book_id)
    r = 0
    if len(avgratings) != 0:
        for i in avgratings:
            r += i.rating
        r /= len(avgratings)
    b = Book.objects.filter(id = book_id)[0]
    b.rating = round(r, 2)
    b.save()
    context = {
        'rating': round(r,2),
    }
    return JsonResponse(context)