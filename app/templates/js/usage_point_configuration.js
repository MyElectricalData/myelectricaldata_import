$('#configuration').draggable({
    containment: 'window'
});

$("#configuration").dialog({
    autoOpen: false,
    autoResize: false,
    draggable: false,
    resizable: false,
    width: 700,
    position: {my: "center center", at: "center center", of: window},
    modal: true,
    maxHeight: $(window).height(),
    open: function (event, ui) {
        $("body").css({overflow: 'hidden'})
    },
    beforeClose: function (event, ui) {
        $("body").css({overflow: 'inherit'})
    },
    buttons: {
        cancel: {
            text: 'Annuler',
            class: 'btn-blue',
            click: function () {
                $(this).dialog("close");
            }
        },
        formSubmit: {
            text: 'Sauvegarder',
            class: 'btn-blue',
            click: function (event) {
                sendForm()
            }
        },
    },
});

$("#formConfiguration").validate({
    lang: 'fr',
    rules: {
        usage_point_id: {
            required: true,
            digits: true,
            maxlength: 14,
            minlength: 14
        },
        name: {
            required: true,
        },
        token: {
            required: true,
        },
        consumption_price_hc: {
            number: true,
        },
        consumption_price_hp: {
            number: true,
        },
        consumption_price_base: {
            number: true,
        },
        production_price: {
            number: true,
        },
    }
});

function sendForm() {
    console.log($('#usage_point_id').val())
    if ($('#formConfiguration').valid()) {
        $.LoadingOverlay("show", loading);
        var formData = { {{configurationInput}} };
        var usage_poind_id = $('#usage_point_id').val()
        if (usage_poind_id == undefined) {
            var url = "/new_account"
        }else{
            var url = "/configuration/"+$('#usage_point_id').val()
        }
        $.ajax({
            type: "POST",
            url: url,
            data: formData,
            dataType: "json",
            encode: true,
        }).done(function (data) {
            window.location.reload();
        });
    }
}

$("#config_data").click(function (e) {
    $("#bottom_menu").removeClass("active")
    $("#configuration").data('url', "/configuration/{{usage_point_id}}").dialog('open');
    e.preventDefault();
});

$("#add_account").click(function (e) {
    $("#bottom_menu").removeClass("active")
    $("#configuration").data('url', "/new_account/").dialog('open');
    e.preventDefault();
});

var $dialog = $('<div></div>').dialog({
    title: "Aide",
    autoOpen: false,
    resizable: false,
    modal: true,
    maxWidth: $(window).width(),
    minWidth: $(window).width() / 2,
});

$(".help").click(function () {
    $dialog.dialog('open');
    $dialog.html($(this).attr("alt"));
});