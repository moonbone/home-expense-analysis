from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from .models import Expense, Category, Names
from django.db.models import Sum, Case, When, F,Q
from datetime import datetime
from dateutil.relativedelta import relativedelta

def details(request):
    print (request.GET)
    if int(request.GET['cat']) == -1:
        return render(request, 'details/details.html',
                  {'details': Expense.objects.raw(r"SELECT * from expense  LEFT JOIN names on expense.name = names.name LEFT JOIN files on expense.file_id = files.id LEFT JOIN Category on names.cat = Category.id"
                                                  r" where (names.name is null or Category.id = 0) "
                                                  r" and expense.date > date('now','start of month','-%s month') "
                                                  r" ORDER BY date"%request.GET['monthsback'])
                   })


    return render(request, 'details/details.html',
                  {'details': Expense.objects.filter(date__gte= datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0) -
                                                                relativedelta(months=int(request.GET['monthsback'])),
                                                     name__cat__id=int(request.GET['cat'])).order_by('date')
                   })

def missing(request):
    if request.method == "POST":
        #'''
        for k in sorted(request.POST.keys(), reverse=True):
            if k == 'csrfmiddlewaretoken' or request.POST[k] == '0':
                continue
            if '_txt' in k:
                if request.POST[k]:
                    print(k, request.POST[k])
                    ex = Expense.objects.get(id=k[:-4])
                    ex.name_id = ex.name_id + '_' + request.POST[k]
                    ex.save()
            else:
                if int(request.POST[k],10) == -1:
                    ex = Expense.objects.get(id=k)
                    ex.name_id = ex.name_id + '_' + "IGNORE"
                    ex.save()

                print(k, request.POST[k])
                name = Names.objects.get_or_create(expense__id=k,
                                                   defaults={'name': Expense.objects.get(id=k).name_id})[0]
                name.cat_id = int(request.POST[k])
                name.save()
        '''
        #'''

    last_month_list = Expense.objects.raw(r"SELECT * from expense  LEFT JOIN names on expense.name = names.name LEFT JOIN Category on names.cat = Category.id LEFT JOIN files on expense.file_id = files.id"
                                          r" where (names.name is null or Category.id = 0) "
                                          r" and expense.date > date('now','start of month','-12 month') "
                                          r" ORDER BY date")

    return render(request, 'missing/missing.html',
                  {'missing': last_month_list,
                   'total': sum(map(lambda ex: ex.charge, last_month_list)),
                   'categories': Category.objects.all() })

#& Q(name__isnull=False)
def report(request):
    sums= Category.objects.filter(Q(id__gt=0)).annotate(
        lastMonth= Sum(Case(When(names__expense__date__gte=
                                 datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0) -
                                 relativedelta(months=1),
                                 names__expense__charge_number=1,
                                 then=F('names__expense__charge')*F('names__expense__total_charges')))),
        lastQuarter= Sum(Case(When(names__expense__date__gte=
                                   datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0) -
                                   relativedelta(months=3),
                                   names__expense__charge_number=1,
                                   then=F('names__expense__charge')*F('names__expense__total_charges')))),
        lastHalf= Sum(Case(When(names__expense__date__gte=
                                datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0) -
                                relativedelta(months=6),
                                names__expense__charge_number=1,
                                then=F('names__expense__charge')*F('names__expense__total_charges')))),
        lastYear= Sum(Case(When(names__expense__date__gte=
                                datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0) -
                                relativedelta(months=12),
                                names__expense__charge_number=1,
                                then=F('names__expense__charge')*F('names__expense__total_charges')))))


    totals = Expense.objects.filter(~Q(id=-1)).aggregate(
                       lastMonth=Sum(Case(When(date__gte=
                                               datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0) -
                                               relativedelta(months=1),
                                               charge_number=1,
                                               then=F('charge')*F('total_charges')))),
                       lastQuarter= Sum(Case(When(date__gte=
                                                  datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0) -
                                                  relativedelta(months=3),
                                                  charge_number=1,
                                                  then=F('charge')*F('total_charges')))),
                       lastHalf= Sum(Case(When(date__gte=
                                               datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0) -
                                               relativedelta(months=6),
                                               charge_number=1,
                                               then=F('charge')*F('total_charges')))),
                       lastYear= Sum(Case(When(date__gte=
                                               datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0) -
                                               relativedelta(months=12),
                                               charge_number=1,
                                               then=F('charge')*F('total_charges')))))

    not_categorized = Expense.objects.filter(~Q(id=-1)).aggregate(
        lastMonth= totals['lastMonth'] - Sum(Case(When(date__gte=
                                 datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0) -
                                 relativedelta(months=1),
                                 charge_number=1,
                                 name__cat__isnull=False,
                                 then=F('charge')*F('total_charges')))),
        lastQuarter= totals['lastQuarter'] - Sum(Case(When(date__gte=
                                 datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0) -
                                 relativedelta(months=3),
                                 charge_number=1,
                                 name__cat__isnull=False,
                                 then=F('charge')*F('total_charges')))),
        lastHalf= totals['lastHalf'] - Sum(Case(When(date__gte=
                                 datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0) -
                                 relativedelta(months=6),
                                 charge_number=1,
                                 name__cat__isnull=False,
                                 then=F('charge')*F('total_charges')))),
        lastYear= totals['lastYear'] - Sum(Case(When(date__gte=
                                 datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0) -
                                 relativedelta(months=12),
                                 charge_number=1,
                                 name__cat__isnull=False,
                                 then=F('charge')*F('total_charges')))),

    )

    return render(request, 'report/report.html',
                  {'sums': sums,
                   'not_categorized': not_categorized,
                   'totals': totals,
                   'income': 10000,
                   })
