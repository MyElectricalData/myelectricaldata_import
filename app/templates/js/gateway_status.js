if (document.URL.indexOf("/usage_point_id/") >= 0) {
    $.ajax({
        type: 'GET',
        url: '/account_status/' + usage_point_id
    })
        .done(function (data) {
            data = JSON.parse(JSON.stringify(data))
            let date = new Date(data["consent_expiration_date"]);
            let day = date.getDate().toString().padStart(2, '0');
            let month = date.getMonth() + 1;
            month = month.toString().padStart(2, '0');
            let year = date.getFullYear();
            let quota_class = "stat_value";
            if (data["quota_reached"] === true) {
                quota_class = "stat_value_warning";
            }
            let gateway_state = "success.png"
            let information = ""
            let information_class = "stat_value"
            if (data["valid"] === false || data["valid"] === undefined) {
                gateway_state = "error.png";
                information = data["information"]
                information_class = "stat_value_warning";
            }

            if (isNaN(day) || isNaN(month) || isNaN( year)) {
                var consent_data =  "Inconnu"
            }else{
                var consent_data =  day + "/" + month + "/" + year
            }
            if (data["call_number"] === undefined) {
                var call_number = 0
            }else{
                var call_number = data["call_number"]
            }
            if (data["quota_limit"] === undefined) {
                var quota_limit = 0
            }else{
                var quota_limit = data["quota_limit"]
            }
            if (data["last_call"] === undefined) {
                var last_call = "---"
            }else{
                var last_call = data["last_call"]
            }
            if(information === undefined) {
                information = "Soucis sur le compte<br>Vérifier les logs ou votre configuration"
            }
            content = "<table class='stat_table'>" +
                "<tr>" +
                "<td class='stat_key'>Expiration des consentements</td><td class='stat_value'>" + consent_data + "</td>" +
                "</tr>" +
                "<tr>" +
                "<td class='stat_key'>Nombre d'appels journaliers</td><td class='" + quota_class + "'>" + call_number + " / " + quota_limit + "</td>" +
                "</tr>" +
                "<tr>" +
                "<td class='stat_key'>Statut du compte</td><td class='stat_value'><img src='/static/img/" + gateway_state + "' style='width: 18px;'></td>" +
                "</tr>" +
                "<tr>" +
                "<td class='stat_key'>Date du dernier import</td><td class='stat_value'>" + last_call + "</td>" +
                "</tr>" +
                "<tr>" +
                "<td class='" + information_class + "' colspan='2'>" + information + "</td>" +
                "</tr>" +
                "</table>"
            $("#stat").html(content)
        })
} else {
    $.ajax({
        type: 'GET',
        url: '/gateway_status/'
    })
        .done(function (data) {
            data = JSON.parse(JSON.stringify(data))
            let gateway_state = "success.png"
            let information = ""
            let information_class = "stat_value"
            version = data["version"]
            if (data["status"] === false) {
                gateway_state = "error.png";
                information = data["information"]
                information_class = "stat_value_warning";
            }
            content = "<table class='stat_table'>" +
                "<tr>" +
                "<td class='stat_key'>Statut de la passerelle</td><td class='stat_value'><img src='/static/img/" + gateway_state + "' style='width: 18px;'></td>" +
                "</tr>" +
                "<tr>" +
                "<td class='stat_key'>Version</td><td class='stat_value' style='width: 150px'>" + version + "</td>" +
                "</tr>" +
                "<tr>" +
                "<td class='" + information_class + "' colspan='2'>" + information + "</td>" +
                "</tr>" +
                "</table>"
            $("#stat").html(content)
        })
}
