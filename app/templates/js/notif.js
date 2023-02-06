$.notify.addStyle('enedis', {
    html: "<div><span data-notify-text/></div>"
});
let searchParams = new URLSearchParams(window.location.search)
if (searchParams.has('notif') == true) {
    $.notify(message, {style: 'enedis', className: 'error'});
}