let searchParams = new URLSearchParams(window.location.search)

if (searchParams.has('notif_body') == true) {
    var notif_title = atob(searchParams.get('notif_title'));
    var notif_body = atob(searchParams.get('notif_body'));

    jQuery(document).ready(function () {
        $.notify.addStyle('error', {
            html:
                "<div>" +
                "<div class='title'>" + notif_title + "</div>" +
                "<div class='body'/>" + notif_body + "</div>" +
                "</div>"
        });
        $.notify({title: notif_title}, {
            style: 'error',
            position: 'top-right'
        })
    });
}