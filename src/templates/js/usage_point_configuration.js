// noinspection SyntaxError

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

jQuery.validator.addMethod("customDateValidator", function(value, element) {
   var re = /^([0-9]{4}|[0-9]{2})[./-]([0]?[1-9]|[1][0-2])[./-]([0]?[1-9]|[1|2][0-9]|[3][0|1])$/ ;
   if (! re.test(value) ) return false
   try{jQuery.datepicker.parseDate( 'yy-mm-dd', value);return true ;}
   catch(e){return false;}
   },
   "Format de date incorrect : YYYY-MM-DD"
);

$( "#configuration_consumption_max_date" ).datepicker({
        dateFormat: "yy-mm-dd",
        changeMonth: true,
        changeYear: true,
        showButtonPanel: true
    }
);
$( "#configuration_consumption_detail_max_date" ).datepicker({
        dateFormat: "yy-mm-dd",
        changeMonth: true,
        changeYear: true,
        showButtonPanel: true
    }
);

$( "#configuration_production_max_date" ).datepicker({
        dateFormat: "yy-mm-dd",
        changeMonth: true,
        changeYear: true,
        showButtonPanel: true
    }
);
$( "#configuration_production_detail_max_date" ).datepicker({
        dateFormat: "yy-mm-dd",
        changeMonth: true,
        changeYear: true,
        showButtonPanel: true
    }
);

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
            required: true,
            number: true,
        },
        consumption_price_hp: {
            required: true,
            number: true,
        },
        consumption_price_base: {
            required: true,
            number: true,
        },
        production_price: {
            required: true,
            number: true,
        },
        // activation_date_daily: {
        //     customDateValidator: true
        // },
        // activation_date_detail: {
        //     customDateValidator: true
        // },
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