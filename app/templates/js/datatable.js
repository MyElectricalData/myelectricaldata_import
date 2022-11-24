$(".datatable_button").click(function () {
    let name = $(this).attr("name");
    let tag = $(this).attr("id").split("_")[0];
    let type = name.split("_")[0]
    let usage_point_id = name.split("_")[1]
    let date = name.split("_")[2]
    if (type === "import" || type === "reset") {
        // IMPORT OR RESET
        $(this).css("display", "none");
        url = '/usage_point_id/' + usage_point_id + '/' + tag + '/' + type + '/' + date
        $.ajax({
            type: 'GET',
            url: url
        })
            .done(function (data) {
                data = $.parseJSON(JSON.stringify(data))
                if (data.hasOwnProperty('error') && data['error'] === "true") {
                    $('#' + tag + '_' + type + '_' + date).css("display", "block");
                    if (data.hasOwnProperty('notif')) {
                        $.notify(data["notif"], {style: 'enedis', className: 'error'});
                    }
                    $('#' + tag + '_fail_count_' + date).html(data["result"]['fail_count']);
                } else {
                    if (data.hasOwnProperty('notif')) {
                        $.notify(data["notif"], {style: 'enedis', className: 'success'});
                    }
                    if (type === "reset") {
                        $('#' + tag + '_reset_' + date).css("display", "none");
                        $('#' + tag + '_import_' + date).css("display", "block");
                        $('#' + tag + '_icon_' + date).removeClass("icon_success");
                        $('#' + tag + '_icon_' + date).addClass("icon_failed");
                        $('#' + tag + '_conso_w_' + date).html("0 W");
                        $('#' + tag + '_conso_kw_' + date).html("0 kW");
                        $('#' + tag + '_fail_count_' + date).html(data["result"]['fail_count']);
                        $('#' + tag + '_blacklist_' + date).css("display", "block");
                        $('#' + tag + '_whitelist_' + date).css("display", "none")
                        $('#' + tag + '_blacklist_' + date).removeClass("datatable_button_disable");
                    } else {
                        if (data["result"]["date"] === date) {
                            $('#' + tag + '_reset_' + date).css("display", "block");
                            $('#' + tag + '_import_' + date).css("display", "none");
                            $('#' + tag + '_icon_' + date).removeClass("icon_failed");
                            $('#' + tag + '_icon_' + date).addClass("icon_success");
                            $('#' + tag + '_conso_w_' + date).html(data["result"]['value'] + " W");
                            $('#' + tag + '_conso_kw_' + date).html(data["result"]['value'] / 1000 + " kW");
                            $('#' + tag + '_fail_count_' + date).html(data["result"]['fail_count']);
                            $('#' + tag + '_blacklist_' + date).css("display", "block");
                            $('#' + tag + '_whitelist_' + date).css("display", "none");
                            $('#' + tag + '_blacklist_' + date).addClass("datatable_button_disable");
                        } else {
                            $.notify("La donnée n'est pas disponible chez Enedis.", {
                                style: 'enedis',
                                className: 'error'
                            });
                            $('#' + tag + '_' + type + '_' + date).css("display", "block");
                        }
                    }
                }

            });
    } else {
        // BLACKLIST
        if (!$('#' + tag + '_' + type + '_' + date).hasClass("datatable_button_disable")) {
            url = '/usage_point_id/' + usage_point_id + '/' + tag + '/' + type + '/' + date
            $.ajax({
                type: 'GET',
                url: url
            })
                .done(function (data) {
                    data = JSON.parse(JSON.stringify(data))
                    if (data.hasOwnProperty('error') && data['error'] === "true") {
                        $('#' + tag + '_' + type + '_' + date).css("display", "block");
                        if (data.hasOwnProperty('notif')) {
                            $.notify(data["notif"], {style: 'enedis', className: 'error'});
                        }
                    } else {
                        if (data.hasOwnProperty('notif')) {
                            $.notify(data["notif"], {style: 'enedis', className: 'success'});
                        }
                        if (type === "blacklist") {
                            $('#' + tag + '_blacklist_' + date).css("display", "none");
                            $('#' + tag + '_whitelist_' + date).css("display", "block");
                            $('#' + tag + '_icon_' + date).removeClass("icon_failed");
                            $('#' + tag + '_icon_' + date).addClass("icon_success");
                            $('#' + tag + '_conso_w_' + date).html("0 W");
                            $('#' + tag + '_conso_kw_' + date).html("0 kW");
                            $('#' + tag + '_reset_' + date).css("display", "block");
                            $('#' + tag + '_import_' + date).css("display", "none");
                        } else {
                            $('#' + tag + '_blacklist_' + date).css("display", "block");
                            $('#' + tag + '_whitelist_' + date).css("display", "none");
                            $('#' + tag + '_icon_' + date).removeClass("icon_success");
                            $('#' + tag + '_icon_' + date).addClass("icon_failed");
                            $('#' + tag + '_reset_' + date).css("display", "none");
                            $('#' + tag + '_import_' + date).css("display", "block");
                            $('#' + tag + '_blacklist_' + date).removeClass("datatable_button_disable");
                        }
                    }
                });
        }
    }
});


let french = {
    processing: "Traitement en cours...",
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
let datatable_config = {
    columnDefs: [
        {
            targets: -1,
            className: 'dt-body-center dt-head-center',
            // orderDataType: "dom-select",
            // render: function (data, type, row, meta) {
            //     if (type === 'sort') {
            //         switch (data) {
            //             case 'Blaclist':
            //                 return 0;
            //             case 'Uncommon':
            //                 return 1;
            //             case 'Rare':
            //                 return 2;
            //             case 'Lengendary':
            //                 return 3;
            //         }
            //     }
            // }
        },
        {
            targets: -2,
            className: 'dt-body-center dt-head-center',
        },
        {
            targets: -3,
            className: 'dt-head-center',
        },
        {
            targets: -4,
            className: 'dt-body-center dt-head-center',
        }
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
    order: [[0, 'desc']],
    language: french
}
$('#dataTableConsommation').DataTable(datatable_config);
$('#dataTableProduction').DataTable(datatable_config);