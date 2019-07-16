
$("#test").on('submit', function (e) {
    var _ndays = $(ndays).val();
    var _lookback = $(lookback).val();
    var _instrument = $(instrument).val()
    var _correlation = $(correlation).val()

    $.ajax({
        url: "/suggestions",
        type: "get",
        data: {
            ndays: _ndays,
            lookback: _lookback,
            instrument: _instrument,
            correlation: _correlation
        },
        success: function (response) {
            $("#place_for_graphs").html(response);
        },
        error: function (xhr) {
            //Do Something to handle error
        }
    });


    var source = new EventSource("/progress");
    source.onmessage = function (event) {
        $('.progress-bar').css('width', event.data + '%').attr('aria-valuenow', event.data);
        $('.progress-bar-label').text(event.data + '%');
        if (event.data == 100) {
            $('.progress-bar').addClass('bg-success');
            $('.progress-bar').removeClass('progress-bar-animated');
            $('.progress-bar').removeClass('progress-bar-striped ');
            source.close()
        } else {
            $('.progress-bar').removeClass('bg-success');
            $('.progress-bar').addClass('progress-bar-animated');
            $('.progress-bar').addClass('progress-bar-striped ');
        }
        event.preventDefault();
    }

    e.preventDefault();
});

$("#test").on('reset', function () {
    var _ndays = $(ndays).val();

    $.ajax({
        url: "/stop",
        type: "get",
        data: {
            ndays: _ndays
        },
        success: function (response) {
            console.log("PARADO")
        },
        error: function (xhr) {
            //Do Something to handle error
            console.log("MIERDA")
        }
    });
    return false;
});