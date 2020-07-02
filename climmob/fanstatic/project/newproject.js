
$(document).ready(function(){
    $('.tagsinput').tagsinput({
        tagClass: 'label label-primary',
        cancelConfirmKeysOnEmpty: false,
    });
    ClimMobMaps.init();

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

    var ckb_localvariety = $("#ckb_localvariety");
    var localvariety = 0;
    if (ckb_localvariety.is(':checked'))
        localvariety = 1;

    if(localvariety == 1)
        ckb_localvariety.bootstrapSwitch('state',true);
    else
        ckb_localvariety.bootstrapSwitch('state',false);
});

var ClimMobMaps = function () {

    return {
        //main function to initiate map samples
        init: function ()
        {
            var currlat = 9.90471351;
            var currlong = -83.685279;
            if (document.getElementById("newproject_lat") !== null)
                currlat = $("#newproject_lat").val();
            if (document.getElementById("newproject_lon") !== null)
                currlong = $("#newproject_lon").val();

            punto = new google.maps.LatLng(currlat, currlong);

            var myOptions =
            {
                zoom: 1, center: punto, mapTypeId: google.maps.MapTypeId.ROADMAP
            };

            var map = new google.maps.Map(document.getElementById("gmap_marker"),  myOptions);

            var marker = new google.maps.Marker(
            {
                position:punto,
                draggable: true,
                map: map
            });

            google.maps.event.addListener(marker, 'drag', function()
            {
            lat = marker.getPosition().lat()
            lat = lat.toString().substr(0,9)
            lon = marker.getPosition().lng()
            lon = lon.toString().substr(0,9)
                $("#newproject_lat").val(parseFloat(lat));
                $("#newproject_lon").val(parseFloat(lon));
            });

            $('.nav-tabs a').on('shown.bs.tab',
                function ()
                {
                  google.maps.event.trigger(map, 'resize');
                  map.setCenter(new google.maps.LatLng(0, 0));
                }
            );
        }

    };

}();
