let searchParams = new URLSearchParams(window.location.search)

$.notify.addStyle('enedis', {
  html: "<div><span data-notify-text/></div>"
});

if (searchParams.has('notif') == true) {
    var message = atob(searchParams.get('notif'));

    // jQuery(document).ready(function () {
    //     $.notify.addStyle('error', {
    //         html:
    //             "<div>" +
    //             "<div class='title'>" + "ERROR" + "</div>" +
    //             "<div class='body'/>" + message + "</div>" +
    //             "</div>"
    //     });
    //     $.notify({title: message}, {
    //         style: 'error',
    //         position: 'top-right'
    //     })
    // });
    //
    $.notify(message, { style: 'enedis', className: 'error'});
}