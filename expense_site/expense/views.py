from django.shortcuts import render

# Create your views here.
from .models import Expense, Category, Names
from django.db.models import Sum, Case, When, F,Q
from datetime import datetime
import datetime as dt

class datetime2(datetime):
    def __init__(self):
        super(dt.datetime, self).__init__(self)

    def now(tz=None):
        return dt.datetime(2018,12,1)

#datetime = datetime2

from dateutil.relativedelta import relativedelta
import sys
import os
from expense_site import settings
sys.path.append(os.path.join(settings.BASE_DIR,'..'))
from Consts import consts


THIS_MONTH = datetime.today().month
CURRENT_YEAR = datetime.today().year

LAST_YEAR = CURRENT_YEAR - 1
TWO_YEARS_AGO = CURRENT_YEAR - 2


LAST_MONTH = ((THIS_MONTH - 1 - 1) % 12) + 1

LAST_QUART = ((LAST_MONTH - 3)//3) % 4 + 1

LAST_HALF = ((LAST_MONTH - 6)//6) % 2 + 1

two_years_ago_start = datetime(TWO_YEARS_AGO, 1, 1)
two_years_ago_end = datetime(TWO_YEARS_AGO+1, 1, 1)

last_year_start = datetime(LAST_YEAR, 1, 1)
last_year_end = datetime(LAST_YEAR+1, 1, 1)

last_half_start = datetime(LAST_YEAR if LAST_MONTH < 6 else CURRENT_YEAR, (LAST_HALF-1)*6 + 1, 1)
last_half_end = datetime(CURRENT_YEAR, ((LAST_HALF*6) % 12) + 1, 1)

last_quart_start = datetime(LAST_YEAR if LAST_MONTH < 3 else CURRENT_YEAR, (LAST_QUART-1)*3 + 1, 1)
last_quart_end = datetime(CURRENT_YEAR, ((LAST_QUART*3) % 12) + 1, 1)

last_month_start = datetime(LAST_YEAR if LAST_MONTH == 12 else CURRENT_YEAR, LAST_MONTH, 1)
last_month_end = datetime(CURRENT_YEAR, (LAST_MONTH % 12) + 1, 1)

def details(request):
    print (request.GET)
    start_date = {1 : last_month_start,
                      3 : last_quart_start,
                      6 : last_half_start,
                      12: last_year_start}[int(request.GET['monthsback'])]
    end_date =   {1 : last_month_end,
                      3 : last_quart_end,
                      6 : last_half_end,
                      12: last_year_end}[int(request.GET['monthsback'])]
    if int(request.GET['cat']) == -1:
        return render(request, 'details/details.html',
                  {'details': Expense.objects.raw(r"SELECT * from expense  LEFT JOIN names on expense.name = names.name LEFT JOIN files on expense.file_id = files.id LEFT JOIN Category on names.cat = Category.id"
                                                  r" where (names.name is null or Category.id = 0) "
                                                  r" and expense.date > '%s' "
                                                  r" and expense.date < '%s'"
                                                  r" ORDER BY date"%(start_date, end_date))
                   })


    return render(request, 'details/details.html',
                  {'details': Expense.objects.filter(date__lt=end_date, date__gte= start_date,
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
    sums= Category.objects.filter(Q(id__gt=0,names__expense__date__lt=datetime.now())).annotate(
        lastMonth= Sum(Case(When(names__expense__date__gte=last_month_start,
                                 names__expense__date__lt=last_month_end,
                                 names__expense__charge_number=1,
                                 then=F('names__expense__charge')*F('names__expense__total_charges')))),
        lastQuarter= Sum(Case(When(names__expense__date__gte=last_quart_start,
                                   names__expense__date__lt=last_quart_end,
                                   names__expense__charge_number=1,
                                   then=F('names__expense__charge')*F('names__expense__total_charges')))),
        lastHalf= Sum(Case(When(names__expense__date__gte=last_half_start,
                                names__expense__date__lt=last_half_end,
                                names__expense__charge_number=1,
                                then=F('names__expense__charge')*F('names__expense__total_charges')))),
        lastYear= Sum(Case(When(names__expense__date__gte=last_year_start,
                                names__expense__date__lt=last_year_end,
                                names__expense__charge_number=1,
                                then=F('names__expense__charge')*F('names__expense__total_charges')))))


    totals = Expense.objects.filter(~Q(id=-1) and Q(date__lt=datetime.now())).aggregate(
                       lastMonth=Sum(Case(When(date__gte=last_month_start,
                                               date__lt=last_month_end,
                                               charge_number=1,
                                               then=F('charge')*F('total_charges')))),
                       lastQuarter= Sum(Case(When(date__gte=last_quart_start,
                                                  date__lt=last_quart_end,
                                                  charge_number=1,
                                                  then=F('charge')*F('total_charges')))),
                       lastHalf= Sum(Case(When(date__gte=last_half_start,
                                               date__lt=last_half_end,
                                               charge_number=1,
                                               then=F('charge')*F('total_charges')))),
                       lastYear= Sum(Case(When(date__gte=last_year_start,
                                               date__lt=last_year_end,
                                               charge_number=1,
                                               then=F('charge')*F('total_charges')))))

    not_categorized = Expense.objects.filter(~Q(id=-1)and Q(date__lt=datetime.now())).aggregate(
        lastMonth= totals['lastMonth'] - Sum(Case(When(date__gte=last_month_start,
                                                       date__lt=last_month_end,
                                                       charge_number=1,
                                                       name__cat__isnull=False,
                                                       then=F('charge')*F('total_charges')))),
        lastQuarter= totals['lastQuarter'] - Sum(Case(When(date__gte=last_quart_start,
                                                           date__lt=last_quart_end,
                                                           charge_number=1,
                                                           name__cat__isnull=False,
                                                           then=F('charge')*F('total_charges')))),
        lastHalf= totals['lastHalf'] - Sum(Case(When(date__gte=last_half_start,
                                                     date__lt=last_half_end,
                                                     charge_number=1,
                                                     name__cat__isnull=False,
                                                     then=F('charge')*F('total_charges')))),
        lastYear= totals['lastYear'] - Sum(Case(When(date__gte=last_year_start,
                                                     date__lt=last_year_end,
                                                     charge_number=1,
                                                     name__cat__isnull=False,
                                                     then=F('charge')*F('total_charges')))),

    )

    return render(request, 'report/report.html',
                  {'sums': sums,
                   'not_categorized': not_categorized,
                   'totals': totals,
                   'income': consts.monthly_income,
                   })
