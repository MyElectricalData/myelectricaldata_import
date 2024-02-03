$(document.body).on('click', '.datatable_button', function () {
    let name = $(this).attr("name");
    // let tag = $(this).attr("id").split("_")[0];
    let tag = $(this).attr("title")
    let type = name.split("_")[0]
    let usage_point_id = name.split("_")[1]
    let date = name.split("_")[2]
    if (type === "import" || type === "reset") {
        // IMPORT OR RESET
        if (!$('[id="' + tag + '_' + type + '_' + date + '"]').hasClass("datatable_button_disable")) {
            $(this).css("display", "none");
            url = '/usage_point_id/' + usage_point_id + '/' + tag + '/' + type + '/' + date
            $.ajax({
                type: 'GET',
                url: url
            })
                .done(function (data) {
                    data = $.parseJSON(JSON.stringify(data))
                    if (tag.includes("detail") && type != "reset") {
                        setTimeout(function () {
                            $('#dataTableConsommationDetail').DataTable(datatable_consumption_detail).ajax.reload();
                            ;
                        }, 1000);
                    }
                    if (data.hasOwnProperty('error') && data['error'] === "true") {
                        $('[id="' + tag + '_' + type + '_' + date + '"]').css("display", "block");
                        if (data.hasOwnProperty('notif')) {
                            $.notify(data["notif"], {style: 'enedis', className: 'error'});
                        }
                        $('[id="' + tag + '_fail_count_' + date + '"]').html(data["result"]['fail_count']);
                    } else {
                        if (data.hasOwnProperty('notif')) {
                            $.notify(data["notif"], {style: 'enedis', className: 'success'});
                        }
                        if (type === "reset") {
                            $('[id="' + tag + '_reset_' + date + '"]').css("display", "none");
                            $('[id="' + tag + '_import_' + date + '"]').css("display", "block");
                            $('[id="' + tag + '_icon_' + date + '"]').removeClass("icon_success");
                            $('[id="' + tag + '_icon_' + date + '"]').addClass("icon_failed");
                            $('[id="' + tag + '_conso_event_date_' + date + '"]').html("");
                            $('[id="' + tag + '_conso_w_' + date + '"]').html("0");
                            $('[id="' + tag + '_conso_kw_' + date + '"]').html("0");
                            $('[id="' + tag + '_conso_a_' + date + '"]').html("0");
                            $('[id="' + tag + '_hc_daily_' + date + '"]').html("-");
                            $('[id="' + tag + '_hp_daily_' + date + '"]').html("-");
                            $('[id="' + tag + '_fail_count_' + date + '"]').html(data["result"]['fail_count']);
                            $('[id="' + tag + '_blacklist_' + date + '"]').css("display", "block");
                            $('[id="' + tag + '_whitelist_' + date + '"]').css("display", "none")
                            $('[id="' + tag + '_blacklist_' + date + '"]').removeClass("datatable_button_disable");
                        } else {
                            if (data["result"]["date"] === date) {
                                if (data["result"]['hc'] == 0) {
                                    hc = "-"
                                } else {
                                    hc = data["result"]['hc'] / 1000
                                }
                                if (data["result"]['hp'] == 0) {
                                    hp = "-"
                                } else {
                                    hp = data["result"]['hp'] / 1000
                                }
                                $('[id="' + tag + '_reset_' + date + '"]').css("display", "block");
                                $('[id="' + tag + '_import_' + date + '"]').css("display", "none");
                                $('[id="' + tag + '_icon_' + date + '"]').removeClass("icon_failed");
                                $('[id="' + tag + '_icon_' + date + '"]').addClass("icon_success");
                                $('[id="' + tag + '_conso_event_date_' + date + '"]').html(data["result"]['event_date']);
                                $('[id="' + tag + '_conso_w_' + date + '"]').html(data["result"]['value']);
                                $('[id="' + tag + '_conso_kw_' + date + '"]').html(data["result"]['value'] / 1000);
                                ampere = data["result"]['value'] / 230
                                ampere = Math.round((ampere + Number.EPSILON) * 100) / 100
                                $('[id="' + tag + '_conso_a_' + date + '"]').html(ampere);
                                $('[id="' + tag + '_hc_daily_' + date + '"]').html(hc);
                                $('[id="' + tag + '_hp_daily_' + date + '"]').html(hp);
                                $('[id="' + tag + '_fail_count_' + date + '"]').html(data["result"]['fail_count']);
                                $('[id="' + tag + '_blacklist_' + date + '"]').css("display", "block");
                                $('[id="' + tag + '_whitelist_' + date + '"]').css("display", "none");
                                $('[id="' + tag + '_blacklist_' + date + '"]').addClass("datatable_button_disable");
                            } else {
                                $.notify("La donnée n'est pas disponible chez Enedis.", {
                                    style: 'enedis',
                                    className: 'error'
                                });
                                $('[id="' + tag + '_' + type + '_' + date + '"]').css("display", "block");
                            }
                        }
                    }

                });
        }
    } else {
        // BLACKLIST
        if (!$('[id="' + tag + '_' + type + '_' + date + '"]').hasClass("datatable_button_disable")) {
            url = '/usage_point_id/' + usage_point_id + '/' + tag + '/' + type + '/' + date
            $.ajax({
                type: 'GET',
                url: url
            })
                .done(function (data) {
                    data = JSON.parse(JSON.stringify(data))
                    if (data.hasOwnProperty('error') && data['error'] === "true") {
                        $('[id="' + tag + '_' + type + '_' + date + '"]').css("display", "block");
                        if (data.hasOwnProperty('notif')) {
                            $.notify(data["notif"], {style: 'enedis', className: 'error'});
                        }
                    } else {
                        if (data.hasOwnProperty('notif')) {
                            $.notify(data["notif"], {style: 'enedis', className: 'success'});
                        }
                        if (type === "blacklist") {
                            $('[id="' + tag + '_blacklist_' + date + '"]').css("display", "none");
                            $('[id="' + tag + '_whitelist_' + date + '"]').css("display", "block");
                            $('[id="' + tag + '_icon_' + date + '"]').removeClass("icon_failed");
                            $('[id="' + tag + '_icon_' + date + '"]').addClass("icon_success");
                            $('[id="' + tag + '_conso_w_' + date + '"]').html("0");
                            $('[id="' + tag + '_conso_kw_' + date + '"]').html("0");
                            $('[id="' + tag + '_hc_daily_' + date + '"]').html("-");
                            $('[id="' + tag + '_hp_daily_' + date + '"]').html("-");
                            $('[id="' + tag + '_reset_' + date + '"]').css("display", "none");
                            $('[id="' + tag + '_import_' + date + '"]').css("display", "block");
                            $('[id="' + tag + '_import_' + date + '"]').addClass("datatable_button_disable");
                        } else {
                            $('[id="' + tag + '_blacklist_' + date + '"]').css("display", "block");
                            $('[id="' + tag + '_whitelist_' + date + '"]').css("display", "none");
                            $('[id="' + tag + '_icon_' + date + '"]').removeClass("icon_success");
                            $('[id="' + tag + '_icon_' + date + '"]').addClass("icon_failed");
                            $('[id="' + tag + '_reset_' + date + '"]').css("display", "none");
                            $('[id="' + tag + '_import_' + date + '"]').css("display", "block");
                            $('[id="' + tag + '_blacklist_' + date + '"]').removeClass("datatable_button_disable");
                            $('[id="' + tag + '_import_' + date + '"]').removeClass("datatable_button_disable");
                        }
                    }
                });
        }
    }
});


let french = {
    // processing: "Traitement en cours...",
    processing: '<div class="d-flex justify-content-center align-items-center"><div class="spinner-border text-primary" role="status"><span class="sr-only">Traitement en cours...</span></div></div>',
    search: "Rechercher&nbsp;:",
    lengthMenu: "Afficher _MENU_ &eacute;l&eacute;ments",
    info: "Affichage de l'&eacute;lement _START_ &agrave; _END_ sur _TOTAL_ &eacute;l&eacute;ments",
    infoEmpty: "Affichage de l'&eacute;lement 0 &agrave; 0 sur 0 &eacute;l&eacute;ments",
    infoFiltered: "(filtr&eacute; de _MAX_ &eacute;l&eacute;ments au total)",
    infoPostFix: "",
    loadingRecords: "Chargement en cours...",
    zeroRecords: "Aucun &eacute;l&eacute;ment &agrave; afficher",
    emptyTable: "Aucune donnée disponible dans le tableau",
    paginate: {
        first: "Premier",
        previous: "Pr&eacute;c&eacute;dent",
        next: "Suivant",
        last: "Dernier"
    },
    aria: {
        sortAscending: ": activer pour trier la colonne par ordre croissant",
        sortDescending: ": activer pour trier la colonne par ordre décroissant"
    }
}

var consumption_columnDefs = [];
consumption_columnDefs.push({targets: 0, className: 'dt-body-center dt-head-center'});
consumption_columnDefs.push({targets: 1, className: 'dt-body-center dt-head-center'});
consumption_columnDefs.push({targets: 2, className: 'dt-body-center dt-head-center'});
consumption_columnDefs.push({targets: 3, className: 'dt-body-center dt-head-center', orderable: false});
consumption_columnDefs.push({targets: 4, className: 'dt-body-center dt-head-center', orderable: false});
consumption_columnDefs.push({targets: 5, className: 'dt-body-center dt-head-center', orderable: false});
consumption_columnDefs.push({targets: 6, className: 'dt-body-center dt-head-center',});
consumption_columnDefs.push({targets: 7, className: 'dt-head-center', orderable: false});
consumption_columnDefs.push({targets: 8, className: 'dt-body-center dt-head-center loading_bg', orderable: false});
consumption_columnDefs.push({targets: 9, className: 'dt-body-center dt-head-center loading_bg', orderable: false});

var consumption_columns = [];
consumption_columns.push({"width": "auto"});
consumption_columns.push({"width": "auto"});
consumption_columns.push({"width": "auto"});
consumption_columns.push({"width": "auto"});
consumption_columns.push({"width": "auto"});
consumption_columns.push({"width": "auto"});
consumption_columns.push({"width": "auto"});
consumption_columns.push({"width": "auto"});
consumption_columns.push({"width": "auto"});
consumption_columns.push({"width": "auto"});

let datatable_consumption = {
    processing: true,
    serverSide: true,
    ajax: {
        url: "/datatable/" + usage_point_id + "/consumption",
        type: "GET",
        beforeSend: function () {
            $.LoadingOverlay("show", loading);
        },
        complete: function () {
            $.LoadingOverlay("hide", loading);
        },
    },
    columnDefs: consumption_columnDefs,
    columns: consumption_columns,
    aoColumnDefs: [
        {
            "mRender": function (data, type, row) {
                return alert(data)
            },
            "aTargets": [6]
        },
    ],
    order: [[0, 'asc']],
    language: french
}
let datatable_consumption_detail = {
    serverSide: true,
    retrieve: true,
    ajax: {
        url: "/datatable/" + usage_point_id + "/consumption_detail",
        type: "GET",
        beforeSend: function () {
            $.LoadingOverlay("show", loading);
        },
        complete: function () {
            $.LoadingOverlay("hide", loading);
        },
    },
    columnDefs: [
        {
            targets: 0,
            className: 'dt-body-center dt-head-center',
        },
        {
            targets: 1,
            className: 'dt-body-center dt-head-center',
        },
        {
            targets: 2,
            className: 'dt-body-center dt-head-center',
        },
        {
            targets: 3,
            className: 'dt-body-center dt-head-center',
        },
        {
            targets: 4,
            className: 'dt-body-center dt-head-center',
        },
        {
            targets: 5,
            className: 'dt-head-center',
            orderable: false
        },
        {
            targets: 6,
            className: 'dt-body-center dt-head-center loading_bg',
            orderable: false
        },
        {
            targets: 7,
            className: 'dt-body-center dt-head-center loading_bg',
            orderable: false
        },
    ],
    columns: [
        {"width": "20%"},
        {"width": "20%"},
        {"width": "20%"},
        {"width": "20%"},
        {"width": "10px"},
        {"width": "10px"},
        {"width": "10px"},
        {"width": "10px"},
    ],
    order: [[0, 'asc']],
    language: french
}
let datatable_production = {
    processing: true,
    serverSide: true,
    ajax: {
        url: "/datatable/" + usage_point_id + "/production",
        type: "GET",
        beforeSend: function () {
            $.LoadingOverlay("show", loading);
        },
        complete: function () {
            $.LoadingOverlay("hide", loading);
        },
    },
    columnDefs: [
        {
            targets: 0,
            className: 'dt-body-center dt-head-center',
        },
        {
            targets: 1,
            className: 'dt-body-center dt-head-center',
        },
        {
            targets: 2,
            className: 'dt-body-center dt-head-center',
        },
        {
            targets: 3,
            className: 'dt-body-center dt-head-center',
        },
        {
            targets: 4,
            className: 'dt-head-center',
            orderable: false
        },
        {
            targets: 5,
            className: 'dt-body-center dt-head-center loading_bg',
            orderable: false
        },
        {
            targets: 6,
            className: 'dt-body-center dt-head-center loading_bg',
            orderable: false
        },
    ],
    columns: [
        {"width": "30%"},
        {"width": "30%"},
        {"width": "30%"},
        {"width": "10px"},
        {"width": "50px"},
        {"width": "50px"},
        {"width": "50px"},
    ],
    aoColumnDefs: [
        {
            "mRender": function (data, type, row) {
                return alert(data)
            },
            "aTargets": [6]
        },
    ],
    order: [[0, 'asc']],
    language: french
}
let datatable_production_detail = {
    serverSide: true,
    retrieve: true,
    ajax: {
        url: "/datatable/" + usage_point_id + "/production_detail",
        type: "GET",
        beforeSend: function () {
            $.LoadingOverlay("show", loading);
        },
        complete: function () {
            $.LoadingOverlay("hide", loading);
        },
    },
    columnDefs: [
        {
            targets: 0,
            className: 'dt-body-center dt-head-center',
        },
        {
            targets: 1,
            className: 'dt-body-center dt-head-center',
        },
        {
            targets: 2,
            className: 'dt-body-center dt-head-center',
        },
        {
            targets: 3,
            className: 'dt-body-center dt-head-center',
        },
        {
            targets: 4,
            className: 'dt-body-center dt-head-center',
        },
        {
            targets: 5,
            className: 'dt-head-center',
            orderable: false
        },
        {
            targets: 6,
            className: 'dt-body-center dt-head-center loading_bg',
            orderable: false
        },
        {
            targets: 7,
            className: 'dt-body-center dt-head-center loading_bg',
            orderable: false
        },
    ],
    columns: [
        {"width": "20%"},
        {"width": "20%"},
        {"width": "20%"},
        {"width": "20%"},
        {"width": "10px"},
        {"width": "10px"},
        {"width": "10px"},
        {"width": "10px"},
    ],
    order: [[0, 'asc']],
    language: french
}
let datatable_config_power = {
    serverSide: true,
    retrieve: true,
    ajax: {
        url: "/datatable/" + usage_point_id + "/consumption_max_power",
        type: "GET",
        beforeSend: function () {
            $.LoadingOverlay("show", loading);
        },
        complete: function () {
            $.LoadingOverlay("hide", loading);
        },
    },
    columnDefs: [
        {
            targets: 0,
            className: 'dt-body-center dt-head-center',
        },
        {
            targets: 1,
            className: 'dt-body-center dt-head-center',
        },
        {
            targets: 2,
            className: 'dt-body-center dt-head-center',
        },
        {
            targets: 3,
            className: 'dt-body-center dt-head-center',
        },
        {
            targets: 4,
            className: 'dt-body-center dt-head-center',
        },
        {
            targets: 5,
            className: 'dt-body-center dt-head-center',
        },
        {
            targets: 6,
            className: 'dt-head-center',
        },
        {
            targets: 7,
            className: 'dt-body-center dt-head-center loading_bg',
        },
        {
            targets: 8,
            className: 'dt-body-center dt-head-center loading_bg',
        },

    ],
    columns: [
        {"width": "30%"},
        {"width": "10%"},
        {"width": "20%"},
        {"width": "20%"},
        {"width": "20%"},
        {"width": "10px"},
        {"width": "50px"},
        {"width": "50px"},
        {"width": "50px"},
    ],
    order: [[0, 'asc']],
    language: french
}
$('#dataTableConsommation').DataTable(datatable_consumption);
$('#dataTableConsommationDetail').DataTable(datatable_consumption_detail);
$('#dataTableProduction').DataTable(datatable_production);
$('#dataTableProductionDetail').DataTable(datatable_production_detail);
$('#dataTablePuissance').DataTable(datatable_config_power);
