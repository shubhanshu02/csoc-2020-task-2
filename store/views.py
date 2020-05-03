from django.http import Http404
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from store.models import *
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from store.models import Book, BookCopy
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

    context = {
        'book': books,
        'num_available': num,
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
    msg = 'success' if books.count() > 0 else 'failure'
    response_data = {
        'message': msg,
    }
    return JsonResponse(response_data)

'''
FILL IN THE BELOW VIEW BY YOURSELF.
This view will return the issued book.
You need to accept the book id as argument from a post request.
You additionally need to complete the returnBook function in the loaned_books.html file
to make this feature complete
''' 
@csrf_exempt
@login_required
def returnBookView(request):
    print('\n\n\n\n', request.POST)


