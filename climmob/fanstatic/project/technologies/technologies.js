
jQuery(document).ready(function() {

    $('.i-checks').iCheck({
        checkboxClass: 'icheckbox_square-green',
        radioClass: 'iradio_square-green',
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

    $('.i-checksAlias').iCheck({
        checkboxClass: 'icheckbox_square-green',
        radioClass: 'iradio_square-green',
    });

    $('.i-checksAliasExtra').iCheck({
        checkboxClass: 'icheckbox_square-purple',
        radioClass: 'iradio_square-purple',
    });

    $('.i-checksAlias').on('ifChanged', function()
    {

        id = $(this).attr("id")
        if ($(this).prop('checked')) {
            $('#txt_technologies_alias_included').val($('#txt_technologies_alias_included').val()+id+",");
            $('#txt_technologies_alias_excluded').val($('#txt_technologies_alias_excluded').val().replace(id+",",""));
        } else {
            $('#txt_technologies_alias_included').val($('#txt_technologies_alias_included').val().replace(id+",",""));
            $('#txt_technologies_alias_excluded').val($('#txt_technologies_alias_excluded').val()+id+",");
        }

    });

    $('.i-checksAliasExtra').on('ifChanged', function()
    {

        id = $(this).attr("id")
        if ($(this).prop('checked')) {
            $('#txt_technologies_alias_included').val($('#txt_technologies_alias_included').val()+id+",");
            $('#txt_technologies_alias_excluded').val($('#txt_technologies_alias_excluded').val().replace(id+",",""));
        } else {
            $('#txt_technologies_alias_included').val($('#txt_technologies_alias_included').val().replace(id+",",""));
            $('#txt_technologies_alias_excluded').val($('#txt_technologies_alias_excluded').val()+id+",");
        }

    });

});



