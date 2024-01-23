def test_consumption_vs_production_consistent():
    from templates.usage_point import UsagePoint

    up = UsagePoint("pdl1")
    up.recap_production_data = {"2023": {"month": {1: 2, 2: 2, 3: 2}}}
    up.recap_consumption_data = {"2023": {"month": {1: 1, 2: 1, 3: 1}}}
    up.consumption_vs_production("2023")
    assert (
        up.javascript
        == """            
            google.charts.load("current", {packages:["corechart"]});
            google.charts.setOnLoadCallback(drawChartProductionVsConsumption2023);
            function drawChartProductionVsConsumption2023() {
                var data = google.visualization.arrayToDataTable([
                ['Mois', 'Consommation', 'Production'],
            ['1', 0.001, 0.002],['2', 0.001, 0.002],['3', 0.001, 0.002],
                ])
                data.sort([{column: 0}]);
                var options = {
                  title : '2023',
                  vAxis: {title: 'Consommation (kWh)'},
                  hAxis: {title: 'Mois'},
                  seriesType: 'bars',
                  series: {5: {type: 'line'}}
                };

                var chart = new google.visualization.ComboChart(document.getElementById('chart_daily_production_compare_2023'));
                chart.draw(data, options);
            }
            """
    )


def test_consumption_vs_production_wrong_year():
    from templates.usage_point import UsagePoint

    up = UsagePoint("pdl1")
    up.recap_production_data = {"2023": {"month": {1: 2, 2: 2, 3: 2}}}
    up.recap_consumption_data = {"2022": {"month": {1: 1, 2: 1, 3: 1}}, "2023": {"month": {1: 1, 2: 1, 3: 1}}}
    up.consumption_vs_production("2022")
    assert (
        up.javascript
        == """            
            google.charts.load("current", {packages:["corechart"]});
            google.charts.setOnLoadCallback(drawChartProductionVsConsumption2022);
            function drawChartProductionVsConsumption2022() {
                var data = google.visualization.arrayToDataTable([
                ['Mois', 'Consommation', 'Production'],
            ['1', 0.001, 0.0],['2', 0.001, 0.0],['3', 0.001, 0.0],
                ])
                data.sort([{column: 0}]);
                var options = {
                  title : '2022',
                  vAxis: {title: 'Consommation (kWh)'},
                  hAxis: {title: 'Mois'},
                  seriesType: 'bars',
                  series: {5: {type: 'line'}}
                };

                var chart = new google.visualization.ComboChart(document.getElementById('chart_daily_production_compare_2022'));
                chart.draw(data, options);
            }
            """
    )


def test_consumption_vs_production_inconsistent():
    from templates.usage_point import UsagePoint

    up = UsagePoint("pdl1")
    up.recap_production_data = {"2023": {"month": {1: 2, 3: 2}}}
    up.recap_consumption_data = {"2023": {"month": {2: 1, 4: 1}}}
    up.consumption_vs_production("2023")
    assert (
        up.javascript
        == """            
            google.charts.load("current", {packages:["corechart"]});
            google.charts.setOnLoadCallback(drawChartProductionVsConsumption2023);
            function drawChartProductionVsConsumption2023() {
                var data = google.visualization.arrayToDataTable([
                ['Mois', 'Consommation', 'Production'],
            ['1', 0.0, 0.002],['2', 0.001, 0.0],['3', 0.0, 0.002],['4', 0.001, 0.0],
                ])
                data.sort([{column: 0}]);
                var options = {
                  title : '2023',
                  vAxis: {title: 'Consommation (kWh)'},
                  hAxis: {title: 'Mois'},
                  seriesType: 'bars',
                  series: {5: {type: 'line'}}
                };

                var chart = new google.visualization.ComboChart(document.getElementById('chart_daily_production_compare_2023'));
                chart.draw(data, options);
            }
            """
    )
