/*
$(document).ready(function(){

    function isNumeric(value)
    {
        return /^\d+$/.test(value);
    }

    $('#user_name').on('input',function()
    {
        var value = $(this).val();
        if(isNumeric(value))
        {
            $(this).val("");
        }
        else
        {
            var value_without_space = value.replace(/[^a-z0-9]/gi,'')
            $(this).val(value_without_space);
        }
    });

    $("#user_cnty").select2();
    $("#user_sector").select2();
    $('.i-checks').iCheck({
        checkboxClass: 'icheckbox_square-green',
        radioClass: 'iradio_square-green',
    });



});*/
