
jQuery(document).ready(function() {

    $('.i-checksAll').iCheck({
        checkboxClass: 'icheckbox_square-green',
        radioClass: 'iradio_square-green',
    });

    $('.i-checks').iCheck({
        checkboxClass: 'icheckbox_square-green',
        radioClass: 'iradio_square-green',
    });

    $('.i-checksExtra').iCheck({
        checkboxClass: 'icheckbox_square-purple',
        radioClass: 'iradio_square-purple',
    });


    $('.dataTables-example').DataTable({
        responsive: true,
        "paging": false
    });

    $('.i-checks').on('ifChanged', function()
    {
        console.log("Hola");
        id = $(this).attr("id")
        if ($(this).prop('checked')) {
            $('#txt_technologies_included').val($('#txt_technologies_included').val()+id+",");
            $('#txt_technologies_excluded').val($('#txt_technologies_excluded').val().replace(id+",",""));
        } else {
            $('#txt_technologies_included').val($('#txt_technologies_included').val().replace(id+",",""));
            $('#txt_technologies_excluded').val($('#txt_technologies_excluded').val()+id+",");
        }

    });

    $('.i-checksExtra').on('ifChanged', function()
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

    $('.i-checksAll').on('ifChanged', function()
    {
        if ($(this).prop('checked')) {
            $('#txt_unselect').css("display","inline-block")
            $('#txt_select').css("display","none")
            $('.i-checks').iCheck('check');
            $('.i-checksExtra').iCheck('check');
        } else
        {
            $('#txt_unselect').css("display","none")
            $('#txt_select').css("display","inline-block")
            $('#txt_select').html("Select all");
            $('.i-checks').iCheck('uncheck');
            $('.i-checksExtra').iCheck('uncheck');
        }

    });
});



function searchTable(searching)
{
    var table = $('#tabletechnologies');
    table.find('tr').each(function(index, row)
    {
        var allCells = $(row).find('td b');

        if(allCells.length > 0)
        {
            var found = false;
            allCells.each(function(index, td)
            {
                var regExp = new RegExp(searching, 'i');
                if(regExp.test($(td).text()))
                {
                    found = true;
                    return false;
                }
            });
            if(found == true)
                $(row).show();
            else {
                if (row.className != "clm-option")
            		$(row).hide();
            }
        }
    });
}