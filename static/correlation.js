var apprun = false;
var source;
$("#test").on('submit', function (e) {
    var _ndays = $(ndays).val();
    var _lookback = $(lookback).val();
    var _instrument = $(instrument).val()
    var _correlation = $(correlation).val()

    source = new EventSource("/progress");
    apprun = true;

    $('#buttonSubmit').prop("disabled", true);

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
            $('#buttonSubmit').prop("disabled", false);
        },
        error: function (xhr) {
            //Do Something to handle error
        }
    });


    progressBar(true);

    e.preventDefault();
});


function progressBar(onoff) {
    switcher = onoff
    console.log("progress running...");
    if (source != null)
        console.log(source.readyState);
    if (switcher == true) {
        source.onmessage = function (event) {
            console.log("... new update");
            if (source != null)
                console.log(source.readyState);
            $('.progress-bar').css('width', event.data + '%').attr('aria-valuenow', event.data);
            $('.progress-bar-label').text(event.data + '%');

            if (event.data == 100 || apprun == false) {
                $('.progress-bar').addClass('bg-success');
                $('.progress-bar').removeClass('progress-bar-animated');
                $('.progress-bar').removeClass('progress-bar-striped ');

                switcher = false;

                console.log("progress getting stopped..." + switcher);
                if (source != null) {
                    source.close();
                    console.log(source.readyState);
                }
                source = null;
                console.log("progress STOPPED");
            } else {
                $('.progress-bar').removeClass('bg-success');
                $('.progress-bar').addClass('progress-bar-animated');
                $('.progress-bar').addClass('progress-bar-striped ');
            }
            event.preventDefault();
        }
    } else {

        console.log("progress getting stopped... jiji" + switcher);
        if (source != null) {
            source.close();
            console.log(source.readyState);
        }
        source = null;
        console.log("progress STOPPED");
    }
    return false;
}



$("#test").on('reset', function () {

    $.ajax({
        url: "/stop",
        type: "get",
        success: function (response) {
            console.log("--- progress getting stopped..." + switcher);
            if (source != null) {
                source.close();
                console.log(source.readyState);
            }
            source = null;
            console.log("--- progress STOPPED");
            apprun = false;
            progressBar(false);
            console.log("--- PARADO: " + response)
        },
        error: function (xhr) {
            //Do Something to handle error
            console.log("MIERDA")
        }
    });
    return false;
});