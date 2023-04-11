$(".alert_redirect").click(function (e) {
    var url = $(this).attr("about")
    $.confirm({
        columnClass: 'col-md-4 col-md-offset-8 col-xs-4 col-xs-offset-8',
        containerFluid: true, // this will add 'container-fluid' instead of 'container'
        boxWidth: '600px',
        useBootstrap: false,
        title: 'Confirmation',
        content: 'Vous allez être rediriger vers ' + url,
        buttons: {
            confirm: {
                text: 'OK!',
                btnClass: 'btn-blue',
                action: function () {
                    location.href = url;
                }
            },
            cancel: {
                text: 'Non merci',
                btnClass: 'btn-blue',
            },
        }
    });
});

$(".paypal_link").click(function () {
    $("#paypal_form").first().submit();
});