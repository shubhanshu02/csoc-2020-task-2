import datetime
from django.http import Http404
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from store.models import *
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


def index(request):
    return render(request, 'store/index.html')

def bookDetailView(request, bid):
    template_name = 'store/book_detail.html'
    
    # List of available book id(s)
    avail = []
    for i in Book.objects.all():
        avail.append(i.id)
    
    # If the id in the request is in the list,  
    if bid in avail:
        book = Book.objects.filter(id = bid).first()
        available_copies = BookCopy.objects.filter(book = book).filter(status = True).count()
    # Else return page not found
    else:
        raise Http404('Book does not exist')

    ## USER GIVEN RATING OF THE BOOK ##

    # All rating objects for the book
    totalRatings = UserRating.objects.filter(book = book)
    # check if user is logged in
    # and rating objects are present for the book
    if request.user.is_authenticated and totalRatings.count() > 0:
        myRating = totalRatings.filter(user_id = request.user.id).first()
        # If user rating is found
        if myRating != None:
            givenRating = myRating.rating
    # Else the rating for the book by the user is None
    else:
        givenRating = None


    context = {
        'book': book,
        'num_available': available_copies,
        'usrating': givenRating,
    }
    return render(request, template_name, context=context)



@csrf_exempt
def bookListView(request):
    template_name = 'store/book_list.html'
    get_data = request.GET

    ## SELECTION OF BOOK OBJECTS i.e. SEARCH ##

    # search is case insensitive
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
    # Search for Loaned Books by the user
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
    if request.method == 'POST':
        # Get the copies of the required book if it is available for loan
        book_id = request.POST['bid']
        books = BookCopy.objects.filter(book_id = book_id, status = True)

        # If copy is available
        if books.count() > 0:
            msg = 'success' 
            # Select the first copy
            books = books.first()
            # Set to unavailable
            books.status = False
            # User is the borrower
            books.borrower = request.user
            # Current date is borrow date
            books.borrow_date = datetime.date.today()
            # Save the model object
            books.save()
        else:
            # The following two are possible:
            #   1. Either no such book is found, or
            #   2. no such book is available for loan
            msg = 'failure'

        # Return the message
        response_data = {
            'message': msg,
        }
        return JsonResponse(response_data)

    # This page is not available for user to view and is just for data exchange
    else:
        raise Http404


@csrf_exempt
@login_required
def returnBookView(request):
    # Books are returned through POST method 
    if request.method == 'POST': 
        # Get the desired book copy
        id = request.POST['bid']
        book = BookCopy.objects.filter(id = id, status = False).first()

        # If not found, book = None
        if book != None:
            # Set status to available
            book.status = True
            # Set borrower to none
            book.borrower = None
            # Set borrow date to none
            book.borrow_date = None
            # Save the object
            book.save()
            msg = 'success'
        else:
            msg = 'failure'

        response_data = {
            'message': msg,
        }
        return JsonResponse(response_data)

    # This page is not available for user to view and is just for data exchange
    else:
        raise Http404


@csrf_exempt
@login_required
def ChangeRatingView(request):
    if request.method == 'POST':
        # Check if the user has already rated the same book
        book_id = request.POST['bid']
        value = request.POST['value']
        book = UserRating.objects.filter(book_id = book_id, user = request.user)
        # Book for which the rating is given
        b = Book.objects.filter(id = book_id)[0]

        # If found, change the rating
        if len(book) != 0:
            book = book.first()
            book.rating = value
            book.save()
        # Else, create the new UserRating object
        else:
            # New Rating object
            bnb = UserRating(book = b, user = request.user, rating = value)
            # Save the rating
            bnb.save()

        ## WHEN USER HAS CHANGED RATING, AVG RATING OF THE BOOK CHANGES ##

        # All rating objects for the book
        totalRatings = UserRating.objects.filter(book_id = book_id)
        # Avg rating variable
        r = 0
        # If rating objects are found for the book
        if len(totalRatings) != 0:
            for Rating in totalRatings:
                r += Rating.rating
            r /= len(totalRatings)
        # If no user has rated the book
        else:
            # -1 indicates no rating is available
            r = -1
        # Save this rating to two decimal points
        b.rating = round(r, 1)
        b.save()
        
        context = {
            'rating': round(r,1),
        }
        return JsonResponse(context)

    # This page is not available for user to view and is just for data exchange
    else:
        raise Http404

@csrf_exempt
@login_required
def RemoveRatingView(request):
    if request.method == 'POST':
        # Check if the user has already rated the same book
        book_id = request.POST['bid']
        rating = UserRating.objects.filter(book_id = book_id, user = request.user)
        b = Book.objects.filter(id = book_id).first()

        # If user has rated, delete the rating object
        # And update average rating of the book
        if len(rating) != 0:
            rating = rating.first()
            rating.delete()
            msg = 'success'

            ## AVERAGE RATING ##

            # All rating objects associated with the book
            rating = UserRating.objects.filter(book_id = book_id)
            if len(rating) != 0:
                # variable to store the average rating
                r = 0
                # Take average of each rating
                for i in rating:
                    r += i.rating
                r /= len(rating)

            # No rating object is found
            else:
                r = -1

            # Update the rating
            b.rating = r
            b.save()

        # If rating wasn't found, send fail msg to the browser
        else:
            msg = 'fail'
            # If no change was down, r = -2
            r = -2


        context = {
            'msg': msg,
            'value': r
        }
        return JsonResponse(context)

    # This page is not available for user to view and is just for data exchange
    else:
        raise Http404