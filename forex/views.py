import re
from statistics import mode
from django.views.decorators.csrf import csrf_exempt
from .models import *
from django.http import JsonResponse
from .past_prediction_by_model import past_predict_by_model
from datetime import datetime
from .serializers import *
from rest_framework import viewsets
from django.utils.timezone import make_aware
from django.shortcuts import render, redirect


def generate_report(_rs, _currency_id, _interval_id, _from_date, _to_date):
    print("########################### GENERATE REPORT ############################")
    report_history_predictions = ReportHistoryPrediction.objects.all().filter(report_status=_rs)
    per_list = []
    for rhp in report_history_predictions:
        per_list.append(0 if rhp.predicted_hit_high == None else 1)
        per_list.append(0 if rhp.predicted_hit_low == None else 1)

    percent = (len([p for p in per_list if p > 0]) / len(per_list)) * 100
    Report.objects.create(
        report_status=_rs,
        currency_id=_currency_id,
        interval_id=_interval_id,
        from_date=make_aware(_from_date),
        to_date=make_aware(_to_date),
        percentage=percent
    )


@csrf_exempt
def predict(request):
    user_id = request.POST['user_id']
    request_id = request.POST['request_id']
    from_date = request.POST['from_date']
    to_date = request.POST['to_date']
    currency = request.POST['currency_id']
    interval = request.POST['interval_id']
    model = request.POST['model_id']

    # from_date = datetime.strptime(from_date, "%d/%m/%Y")
    from_date = datetime.strptime(from_date, "%Y-%m-%d")
    # to_date = datetime.strptime(to_date, "%d/%m/%Y")
    to_date = datetime.strptime(to_date, "%Y-%m-%d")

    rs = ReportStatus.objects.create(
        status='0', comment='in process', user_id=user_id)

    print("Report Status", rs, type(rs))

    currency_id = Currency.objects.get(id=currency)
    interval_id = Interval.objects.get(id=interval)
    model_id = ForexModel.objects.get(id=model)

    # print(currency_id, interval_id, model_id.model_high.__str__(), model_id.model_low.__str__())
    # print(type(currency_id), type(interval_id), type(model_id.model_high.__str__()), type(model_id.model_low.__str__()))

    result, message = past_predict_by_model(
        user_id, request_id, from_date, to_date, currency_id, interval_id, model_id, rs)

    if result:
        rs.status = '1'
        rs.comment = message
        rs.save()
        generate_report(rs, currency_id, interval_id, from_date, to_date)
        # ReportStatus.objects.filter(request_id=request_id).update(
        #     status='1', comment=message)
        return JsonResponse({'SUCCESS': f'{user_id} {request_id} {from_date} {to_date} {currency_id} {interval} {model_id} {message}'})

    else:
        rs.status = '2'
        rs.comment = message
        rs.save()
        # ReportStatus.objects.filter(request_id=request_id).update(
        #     status='2', comment=message)
        return JsonResponse({'FAILED': f'{user_id} {request_id} {from_date} {to_date} {currency_id} {interval} {model_id} {message}'})


class CurrencyViewSet(viewsets.ModelViewSet):
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer


class IntervalViewSet(viewsets.ModelViewSet):
    queryset = Interval.objects.all()
    serializer_class = IntervalSerializer


@csrf_exempt
def get_model(request):
    currency_id = request.POST['currency_id']
    interval_id = request.POST['interval_id']
    forex_model = ForexModel.objects.all().filter(
        currency_id=currency_id, interval_id=interval_id, is_active=True)
    forex_models = []
    for model in forex_model:
        # print([{"id": model.id, "name": f"{model.currency_id} v{model.version}"}])
        forex_models.append(
            {"id": model.id, "name": f"{model.currency_id} v{model.version}"})

    return JsonResponse(forex_models, safe=False)


@csrf_exempt
def index(request):
    print("IN INDEX")
    # print("POST DATA", request.POST)
    # if request.POST:
    #     currency_id = request.POST.get("currency_id")
    #     interval_id = request.POST.get("interval_id")

    #     if currency_id:
    #         models = ForexModel.objects.all().filter(currency_id=currency_id)
        
    #     if interval_id:
    #         models = ForexModel.objects.all().filter(interval_id=interval_id)
        
    #     if currency_id and interval_id:
    #         models = ForexModel.objects.all().filter(currency_id=currency_id, interval_id=interval_id)
        
    # else:
    models = ForexModel.objects.all()
        
    _rs_data = ReportStatus.objects.all().order_by("-id")
    currency_data = Currency.objects.all()
    interval_data = Interval.objects.all()
    _r_last_data = Report.objects.last()
    _r_data = Report.objects.all()
    print("MODELS DATA")
    for i in models:
        print(i.description)
    context = {
        "report_statuses": _rs_data,
        "reports": _r_data,
        "last_report": _r_last_data,
        "currencies": currency_data,
        "intervals": interval_data,
        "models": models,
    }
    return render(request, "back_testing.html", context)


@csrf_exempt
def currency(request, currency):
    print("IN SELECTED CURRENCY ID")
    print(currency, type(currency))
    models = ForexModel.objects.all().filter(currency_id=currency)
    _rs_data = ReportStatus.objects.all()
    currency_data = Currency.objects.all()
    interval_data = Interval.objects.all()
    _r_last_data = Report.objects.last()
    _r_data = Report.objects.all()
    context = {
        "currency_id": int(currency),
        "report_statuses": _rs_data,
        "reports": _r_data,
        "last_report": _r_last_data,
        "currencies": currency_data,
        "intervals": interval_data,
        "models": models,
    }
    return render(request, "back_testing.html", context)


@csrf_exempt
def interval(request, currency, interval):
    print("IN SELECTED INTERVAL ID")
    print(currency, interval)
    models = ForexModel.objects.all().filter(currency_id=currency, interval_id=interval)
    print(models)
    _rs_data = ReportStatus.objects.all()
    currency_data = Currency.objects.all()
    interval_data = Interval.objects.all()
    _r_last_data = Report.objects.last()
    _r_data = Report.objects.all()
    context = {
        "currency_id": int(currency),
        "interval_id": int(interval),
        "report_statuses": _rs_data,
        "reports": _r_data,
        "last_report": _r_last_data,
        "currencies": currency_data,
        "intervals": interval_data,
        "models": models,
    }
    return render(request, "back_testing.html", context)


def report(request):
    _r_last_data = Report.objects.last()
    _r_data = Report.objects.all()
    context = {
        "reports": _r_data,
        "last_report": _r_last_data,
    }
    return render(request, "report.html", context)


def report_status(request, report_status_id):
    print("REPORT STATUS ID", report_status_id)
    report_status = ReportStatus.objects.get(id=report_status_id)
    report = Report.objects.get(report_status=report_status)
    report_history_prediction = ReportHistoryPrediction.objects.filter(report_status = report_status_id)
    # for i in report_history_prediction:
    #     print("REPORT HIST: ", i.report_status)

    print(report)
    context = {
        "last_report": report,
        "report_history_prediction": report_history_prediction,
    }
    return render(request, "report_status.html", context)