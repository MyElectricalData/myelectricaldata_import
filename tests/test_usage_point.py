def test_consumption_vs_production_consistent():
    from templates.usage_point import UsagePoint

    up = UsagePoint("pdl1")
    up.recap_production_data = {"2023": {"month": {1: 2, 2: 2, 3: 2}}}
    up.recap_consumption_data = {"2023": {"month": {1: 1, 2: 1, 3: 1}}}
    up.consumption_vs_production("2023")
    assert "google.charts.load" in up.javascript
    assert "drawChartProductionVsConsumption2023" in up.javascript
    assert "ComboChart" in up.javascript
    assert "'Mois', 'Consommation', 'Production'" in up.javascript


def test_consumption_vs_production_wrong_year():
    from templates.usage_point import UsagePoint

    up = UsagePoint("pdl1")
    up.recap_production_data = {"2023": {"month": {1: 2, 2: 2, 3: 2}}}
    up.recap_consumption_data = {"2022": {"month": {1: 1, 2: 1, 3: 1}}, "2023": {"month": {1: 1, 2: 1, 3: 1}}}
    up.consumption_vs_production("2022")
    assert "drawChartProductionVsConsumption2022" in up.javascript
    assert "chart_daily_production_compare_2022" in up.javascript


def test_consumption_vs_production_inconsistent():
    from templates.usage_point import UsagePoint

    up = UsagePoint("pdl1")
    up.recap_production_data = {"2023": {"month": {1: 2, 3: 2}}}
    up.recap_consumption_data = {"2023": {"month": {2: 1, 4: 1}}}
    up.consumption_vs_production("2023")
    assert "chart_daily_production_compare_2023" in up.javascript
    assert "arrayToDataTable" in up.javascript
