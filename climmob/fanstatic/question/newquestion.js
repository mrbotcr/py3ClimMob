/**
 * Created by brandon on 27/06/16.
 */

$(document).ready(function()
{
    function isNumeric(value)
    {
        return /^\d+$/.test(value);
    }

    $('#question_code').on('input',function()
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

    $("#question_group").select2();
    $("#question_dtype").select2();
    var type = $('#question_dtype').val();

    var objQRegistration = $("#ckb_registrationrequired");
    var registration = 0;
    if (objQRegistration.is(':checked'))
        registration = 1;

    var assessment = 0;
    var objQAssessment = $("#ckb_assessmentrequired");
    if (objQAssessment.is(':checked'))
        assessment = 1;

    var objQRequired = $("#ckb_required_value");
    var question_requiredvalue = 0;
    if (objQRequired.is(':checked'))
        question_requiredvalue = 1;

    var objQVisible = $("#ckb_required_visible");
    var question_visible = 0;
    if (objQVisible.is(':checked'))
        question_visible = 1;


    if(type==2 || type==3)
        $('#div_unit').css('display', 'block');
    else {
        $('#div_unit').css('display', 'none');
        $("#txt_unit").val("");
    }


    if(registration == 1)
        objQRegistration.bootstrapSwitch('state',true);
    else
        objQRegistration.bootstrapSwitch('state',false);

    if (assessment == 1)
        objQAssessment.bootstrapSwitch('state',true);
    else
        objQAssessment.bootstrapSwitch('state',false);

    if (question_requiredvalue == 1)
        objQRequired.bootstrapSwitch('state',true);
    else
        objQRequired.bootstrapSwitch('state',false);

    if (question_visible == 1)
        objQVisible.bootstrapSwitch('state',true);
    else
        objQVisible.bootstrapSwitch('state',false);

    $('#question_dtype').change(function()
    {
        var value = $('#question_dtype').val();

        if(value==2 || value==3)
            $('#div_unit').css('display', 'block');
        else {
            $('#div_unit').css('display', 'none');
            $("#txt_unit").val("");
        }

        if(value== 9 || value == 10)
        {
            objQRegistration.bootstrapSwitch('state',false);
            $("#div_submissions").css('display','none')
        }else
        {
            $("#div_submissions").css('display','block')
        }
    });

});




$("#ckb_registrationrequired").on('switchChange.bootstrapSwitch', function(event, state) {
    if($(this).is(':checked')) {
        $("#ckb_assessmentrequired").bootstrapSwitch('state', false);
    }
});

$("#ckb_assessmentrequired").on('switchChange.bootstrapSwitch', function(event, state) {
    if($(this).is(':checked')) {
        $("#ckb_registrationrequired").bootstrapSwitch('state', false);
    }
});


