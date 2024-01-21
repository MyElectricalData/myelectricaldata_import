from datetime import datetime, timezone

import pytz

from dependencies import daterange

utc = pytz.UTC


class Datatable:
    def __init__(self, usage_point_id):
        self.usage_point_id = usage_point_id

    def html(self, title, tag, daily_data, cache_last_date, option=None):
        if tag == "consumption_max_power":
            max_power = int(option["max_power"]) * 1000
            result = f"""
            <table id="dataTable{title}" class="display">
                <thead>
                    <tr>
                        <th class="title">Date</th>
                        <th class="title">Événement</th>
                        <th class="title">{title} (VA)</th>
                        <th class="title">{title} (kVA)</th>
                        <th class="title">Ampère (A)</th>
                        <th class="title">Échec</th>
                        <th class="title">En&nbsp;cache</th>
                        <th class="title">Cache</th>
                        <th class="title">Liste noire</th>
                    </tr>
                </thead>
                <tbody>
            """
        else:
            result = f"""
            <table id="dataTable{title}" class="display">
                <thead>
                    <tr>
                        <th class="title">Date</th>
                        <th class="title">{title} (Wh)</th>
                        <th class="title">{title} (kWh)</th>
                        <th class="title">Échec</th>
                        <th class="title">En&nbsp;cache</th>
                        <th class="title">Cache</th>
                        <th class="title">Liste noire</th>
                    </tr>
                </thead>
                <tbody>
            """
        all_data = {}
        recap = {}
        if daily_data:
            for data in daily_data:
                date_str = data.date.strftime("%Y-%m-%d")
                if tag == "consumption_max_power":
                    all_data[date_str] = {
                        "event_date": data.event_date,
                        "value": data.value,
                        "blacklist": data.blacklist,
                        "fail_count": data.fail_count,
                    }
                else:
                    all_data[date_str] = {
                        "value": data.value,
                        "blacklist": data.blacklist,
                        "fail_count": data.fail_count,
                    }
            start_date = utc.localize(cache_last_date)
            end_date = datetime.now(timezone.utc)
            if start_date:
                for single_date in daterange(start_date, end_date):
                    year = single_date.strftime("%Y")
                    month = single_date.strftime("%m")
                    if year not in recap:
                        recap[year] = {
                            "value": 0,
                            "month": {
                                "01": 0,
                                "02": 0,
                                "03": 0,
                                "04": 0,
                                "05": 0,
                                "06": 0,
                                "07": 0,
                                "08": 0,
                                "09": 0,
                                "10": 0,
                                "11": 0,
                                "12": 0,
                            },
                        }
                    date_text = single_date.strftime("%Y-%m-%d")
                    conso_w = "0"
                    conso_kw = "0"
                    conso_a = "0"
                    event_date = ""
                    cache_state = f'<div id="{tag}_icon_{date_text}" class="icon_failed">0</div>'
                    reset = f"""
                    <div id="{tag}_import_{date_text}" title="{tag}" name="import_{self.usage_point_id}_{date_text}" class="datatable_button datatable_button_import">
                        <input type="button" value="Importer"></div>
                    <div id="{tag}_reset_{date_text}"title="{tag}"  name="reset_{self.usage_point_id}_{date_text}"  class="datatable_button" style="display: none">
                        <input type="button" value="Vider"></div>
                    """
                    # print(all_data)
                    if date_text in all_data:
                        fail_count = all_data[date_text]["fail_count"]
                        if tag == "consumption_max_power":
                            if isinstance(all_data[date_text]["event_date"], datetime):
                                event_date = all_data[date_text]["event_date"].strftime("%H:%M:%S")
                        if fail_count == 0:
                            value = all_data[date_text]["value"]
                            blacklist_state = all_data[date_text]["blacklist"]
                            recap[year]["value"] = recap[year]["value"] + value
                            recap[year]["month"][month] = recap[year]["month"][month] + value
                            conso_w = f"{value}"
                            conso_kw = f"{value / 1000}"
                            conso_a = f"{round(int(conso_w) / 220, 1)}"
                            cache_state = f'<div id="{tag}_icon_{date_text}" class="icon_success">1</div>'
                            reset = f"""
                            <div id="{tag}_import_{date_text}" title="{tag}" name="import_{self.usage_point_id}_{date_text}" class="datatable_button datatable_button_import" style="display: none">
                                <input type="button" value="Importer"></div>
                            <div id="{tag}_reset_{date_text}" title="{tag}" name="reset_{self.usage_point_id}_{date_text}"  class="datatable_button">
                                <input type="button" value="Vider"></div>
                            """
                            display_blacklist = ""
                            display_whitelist = ""
                            if blacklist_state == 1:
                                display_blacklist = 'style="display: none"'
                            else:
                                display_whitelist = 'style="display: none"'
                            blacklist = f"""
                            <div class="datatable_button datatable_blacklist datatable_button_disable" title="{tag}" id="{tag}_blacklist_{date_text}" name="blacklist_{self.usage_point_id}_{date_text}" {display_blacklist}>
                                <input type="button" value="Blacklist"></div>
                            <div class="datatable_button datatable_whitelist" title="{tag}" id="{tag}_whitelist_{date_text}" name="whitelist_{self.usage_point_id}_{date_text}" {display_whitelist}>
                                <input type="button"  value="Whitelist"></div>
                            """
                        else:
                            blacklist = f"""
                            <div class="datatable_button datatable_blacklist" title="{tag}" id="{tag}_blacklist_{date_text}" name="blacklist_{self.usage_point_id}_{date_text}">
                                <input type="button" value="Blacklist"></div>
                            <div class="datatable_button datatable_whitelist" title="{tag}" id="{tag}_whitelist_{date_text}" name="whitelist_{self.usage_point_id}_{date_text}">
                                <input type="button"  value="Whitelist" style="display: none"></div>
                            """
                    else:
                        fail_count = 0
                        blacklist = f"""
                        <div class="datatable_button datatable_blacklist" title="{tag}" id="{tag}_blacklist_{date_text}" name="blacklist_{self.usage_point_id}_{date_text}">
                           <input type="button" value="Blacklist"></div>
                       <div class="datatable_button datatable_whitelist" title="{tag}" id="{tag}_whitelist_{date_text}" name="whitelist_{self.usage_point_id}_{date_text}">
                           <input type="button" value="Whitelist" style="display: none"></div>
                        """
                    if tag == "consumption_max_power":
                        if max_power <= int(conso_w):
                            style = "color:#FF0000; font-weight:bolder"
                        elif (max_power * 80 / 100) <= int(conso_w):
                            style = "color:#FFB600; font-weight:bolder"
                        else:
                            style = ""
                        result += f"""
                        <tr style="{style}">
                            <td><b>{date_text}</b></td>
                            <td id="{tag}_conso_event_date_{date_text}">{event_date}</td>
                            <td id="{tag}_conso_w_{date_text}">{conso_w}</td>
                            <td id="{tag}_conso_kw_{date_text}">{conso_kw}</td>
                            <td id="{tag}_conso_a_{date_text}">{conso_a}</td>
                            <td id="{tag}_fail_count_{date_text}">{fail_count}</td>
                            <td>{cache_state}</td>
                            <td class="loading_bg">{reset}</td>
                            <td class="loading_bg">{blacklist}</td>
                        </tr>"""
                    else:
                        result += f"""
                        <tr>
                            <td><b>{date_text}</b></td>
                            <td id="{tag}_conso_w_{date_text}">{conso_w}</td>
                            <td id="{tag}_conso_kw_{date_text}">{conso_kw}</td>
                            <td id="{tag}_fail_count_{date_text}">{fail_count}</td>
                            <td>{cache_state}</td>
                            <td class="loading_bg">{reset}</td>
                            <td class="loading_bg">{blacklist}</td>
                        </tr>"""
            result += "</tbody></table>"
        return {"recap": recap, "html": result}
