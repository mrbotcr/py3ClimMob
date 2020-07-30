
$(document).ready(function(){
    $('#newproject_tag').tagsinput({
        tagClass: 'label label-primary',
    });
    //ClimMobMaps.init();

    function isNumeric(value)
    {
        return /^\d+$/.test(value);
    }

    $('#newproject_code').on('input',function()
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

    var project_registration_and_analysis = $("#project_registration_and_analysis");
    var checked = 0;
    if (project_registration_and_analysis.is(':checked'))
        checked = 1;

    if(checked == 1)
        project_registration_and_analysis.bootstrapSwitch('state',true);
    else
        project_registration_and_analysis.bootstrapSwitch('state',false);
});
