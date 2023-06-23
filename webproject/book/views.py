from django.shortcuts import render
from book.models import *
from django.db.models import Q
from book.form import *
from django.http import HttpResponse
from datetime import datetime, timedelta
from django.core.exceptions import ObjectDoesNotExist

## 도서 검색하기(제목, 저자, ISBN 중 1개이상의 키워드를 이용하여)
def search_books(request):
    query = request.GET.get('query')  # 검색어를 GET 파라미터로 받아옴

    # 책 검색
    books = None

    if query:
        query_parts = query.split()

        # 검색 쿼리 동적 구성
        q_objects = Q()

        for part in query_parts:
            q_objects |= Q(title__icontains=part) | Q(author__icontains=part) | Q(isbn__icontains=part)

        books = Book.objects.filter(q_objects)

    context = {
        'query': query,
        'books': books,
    }

    return render(request, 'search_results.html', context)


## email이 있는지 체크
def checkemail(email):
    try:
        member = Member.objects.get(email=email)
        return member
    except Member.DoesNotExist:
        return None


## email의 마일리지 확인
def mymileage(request):
    if request.method == 'POST':
        form = Emailform(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            member = checkemail(email)
            if member:
                mileage = member.mileage
                return render(request, '.html', {'mileage': mileage})
            else:
                member = registeremail(email)
                mileage = member.mileage
                return render(request, '.html', {'mileage': mileage})
    else:
        form = Emailform()
    
    context = {'form': form}
    return render(request, '.html', context)


## 이메일 DB에 등록
def registeremail(email):
    member = Member(email = email)
    member.save()
    return member


##경매 신청(신청자들의 정보(마일리지 기준)를 내림차순으로 저장)
def usemileage(request):
    if request.method == 'POST':
        form = Mileageform(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            mileage = form.cleaned_data['mileage']
            
            # 회원 정보 가져오기
            try:
                member = Member.objects.get(email=email)
            except ObjectDoesNotExist:
                return render(request, 'mileage_usage.html', {'error_message': '해당 이메일로 등록된 회원이 없습니다.'})
            
            # 마일리지 차감
            if member.mileage >= mileage:
                member.mileage -= mileage
                member.save()
                
            # 경매 신청자들의 마일리지를 내림차순으로 저장
            participants = AuctionParticipant.objects.order_by('-mileage')
            
            return render(request, 'mileage_usage.html', {'mileage': mileage, 'participants': participants})
    else:
        form = Emailform()
    
    context = {'form': form}
    return render(request, 'mileage_usage.html', context)



def index(request):
    return render(request, 'book/index.html')

def register(request):
    return render(request, 'book/register.html')

def signup(request):
    return render(request, 'book/signup.html')


##경매에 도서를 등록(+ 경매 시간)
def register_auction(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            # 경매 등록 시간
            auction_start_time = datetime.now()
            # 경매 종료 시간
            auction_end_time = auction_start_time + timedelta(hours=24)

            # 폼 데이터 저장
            book = form.save(commit=False)
            book.auction_start_time = auction_start_time
            book.auction_end_time = auction_end_time
            book.save()

            return redirect('auction_list')
    else:
        form = BookForm()

    context = {'form': form}
    return render(request, 'register_auction.html', context)


