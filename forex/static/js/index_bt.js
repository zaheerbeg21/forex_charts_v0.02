django_url = "http://127.0.0.1:8000/"

var currency_select = document.getElementById("currency");
var interval_select = document.getElementById("interval");
var model_select = document.getElementById("model");
var from_date = document.getElementById("from_date");
var to_date = document.getElementById("to_date");
var calculate_btn = document.getElementById("calculate-btn");

if (currency_select.value != "") {
    interval_select.disabled = false;
} else {
    interval_select.disabled = true;
    model_select.disabled = true;
}

if (interval_select.value != "") {
    model_select.disabled = false;
} else {
    model_select.disabled = true;
}


function onCurrencySelect() {
    console.log(document.cookie);
    interval_select.disabled = false;
    var currency_id = currency_select.value;
    if (currency_id != "") {
        window.location.href = django_url + "index/" + currency_id + "/"
    } else {
        interval_select.disabled = true;
        model_select.disabled = true;
    }
}

function onIntervalSelect() {
    model_select.disabled = false;
    var interval_id = interval_select.value;
    var currency_id = currency_select.value;
    if (interval_id != "") {
        window.location.href = django_url + "index/" + currency_id + "/" + interval_id + "/"
    } else {
        model_select.disabled = true;
    }
}

function onModelSelect() {
    var model_id = model_select.value;
    if (model_id != "") {
        from_date.disabled = false;
    } else {
        from_date.disabled = true;
    }
}

function calculate_prediction() {
    console.log(currency_select.value);
    console.log(interval_select.value);
    console.log(model_select.value);
    console.log(from_date.value);
    console.log(to_date.value);

    var predict_formdata = new FormData();
    predict_formdata.append("user_id", "1234");
    predict_formdata.append("request_id", "7890");
    predict_formdata.append("from_date", from_date.value);
    predict_formdata.append("to_date", to_date.value);
    predict_formdata.append("currency_id", currency_select.value);
    predict_formdata.append("interval_id", interval_select.value);
    predict_formdata.append("model_id", model_select.value);

    var predict_request_options = {
        method: 'POST',
        body: predict_formdata,
        redirect: 'follow'
    };

    fetch(django_url + "predict/", predict_request_options)
        .then(response => response.text())
        .then(result => {
            console.log("result " + result);
        })
        .catch(error => console.log('error', error));
    
    window.location.href = django_url + "index/";
}

function onFromDateChange() {
    var from_date_value = from_date.value;
    if (from_date_value != "") {
        to_date.disabled = false;
    } else {
        to_date.disabled = true;
    }
}

function onToDateChange() {
    var to_date_value = to_date.value;
    if (to_date_value != "") {
        calculate_btn.disabled = false;
    } else {
        calculate_btn.disabled = true;
    }
}