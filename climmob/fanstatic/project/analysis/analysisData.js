jQuery(document).ready(function() {

    $('.i-checks').iCheck({
        checkboxClass: 'icheckbox_square-green',
        radioClass: 'iradio_square-green',
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

    $("[name='ckb_Infosheets']").bootstrapSwitch('state',true);

    $("#ckb_Infosheets").on('switchChange.bootstrapSwitch', function(event, state) {

        if($(this).is(':checked')) {
            $("#txt_infosheets").val('true');
        }
        else{
            $("#txt_infosheets").val('false');
        }
    });

});


