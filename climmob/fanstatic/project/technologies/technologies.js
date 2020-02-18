
jQuery(document).ready(function() {

    $('.i-checks').iCheck({
        checkboxClass: 'icheckbox_square-green',
        radioClass: 'iradio_square-green',
    });

	$('.dataTables-example').DataTable({
        responsive: true,
        "paging": false
    });

    $('.i-checks').on('ifChanged', function()
    {

        id = $(this).attr("id")
        if ($(this).prop('checked')) {
            $('#txt_technologies_included').val($('#txt_technologies_included').val()+id+",");
            $('#txt_technologies_excluded').val($('#txt_technologies_excluded').val().replace(id+",",""));
        } else {
            $('#txt_technologies_included').val($('#txt_technologies_included').val().replace(id+",",""));
            $('#txt_technologies_excluded').val($('#txt_technologies_excluded').val()+id+",");
        }

    });

});



