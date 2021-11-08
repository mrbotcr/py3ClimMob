jQuery(document).ready(function() {

    $('.i-checks').iCheck({
        checkboxClass: 'icheckbox_square-green',
        radioClass: 'iradio_square-green',
    });

    $('.i-checksAll').iCheck({
        checkboxClass: 'icheckbox_square-green',
        radioClass: 'iradio_square-green',
    });

    $('.i-checksAll').on('ifChanged', function()
    {
        id = $(this).attr("id")
        if ($(this).prop('checked')) {
            $("." + id).iCheck('check');
        }else{
            $("." + id).iCheck('uncheck');
        }
    });


    $('.i-checks').on('ifChanged', function()
    {

        id = $(this).attr("id")
        if ($(this).prop('checked')) {

            $('#txt_included_in_analysis').val($('#txt_included_in_analysis').val()+id+",");
        } else {
            $('#txt_included_in_analysis').val($('#txt_included_in_analysis').val().replace(id+",",""));
        }

    });

    $('.explanatorySelect').on('ifChanged', function()
    {
        id = $(this).attr("variable")

        if ($(this).prop('checked')) {

            $('#txt_splits').val($('#txt_splits').val()+id+",");
        } else {
            $('#txt_splits').val($('#txt_splits').val().replace(id+",",""));
        }

    });

    $("[name='ckb_Infosheets']").bootstrapSwitch('state',true);

    $("#ckb_Infosheets").on('switchChange.bootstrapSwitch', function(event, state) {

        if($(this).is(':checked')) {
            $("#txt_infosheets").val('true');
        }
        else{
            $("#txt_infosheets").val('false');
        }
    });

    $("[name='ckb_Splits']").bootstrapSwitch('state',true);

    $("#ckb_Splits").on('switchChange.bootstrapSwitch', function(event, state) {

        if($(this).is(':checked')) {
            values = $("#txt_splits").val().substring(6);
            $("#txt_splits").val('true,'+ values);
        }
        else{
            values = $("#txt_splits").val().substring(5);
            $("#txt_splits").val('false,'+values);
        }

    });

});


