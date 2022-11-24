let usage_point_id = $("#usage_point_id").val()
$("#select_usage_point_id").change(function () {
    $.LoadingOverlay("show", loading);
    location.href = "/usage_point_id/" + $("#select_usage_point_id").val();
});