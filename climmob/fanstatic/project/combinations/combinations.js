function setSizes() {
   var top = $("#header").height();
   var bottom = $("#footer").height();
   modalParent = window.parent.document.getElementById('modaliframecont');
   var ph = modalParent.clientHeight;
   console.log(top);
   console.log(bottom);
   console.log(ph);
   var total = ph-top-bottom-130;
   var stotal = total.toString() + "px";
   //document.getElementById("content").style.cssText = "max-height: " + stotal + "; overflow-y: auto;";
    return stotal;
}

$(document).ready(function(){
    var stage = Number(document.getElementById('stage').value);
    if (stage == 1) {

        $('.dataTables-example').DataTable( {
            scrollY:        setSizes(),
            "scrollCollapse": true,
            "paging":         false,
        } );

        var currScroll = $(".clm-scroll").val();
        $('.dataTables_scrollBody').scrollTop(currScroll);


        $('.dataTables_scrollBody').on('scroll', function() {
            var position = $('.dataTables_scrollBody').scrollTop();
            $(".clm-scroll").val(position);
        });
    }
    if (stage == 2) {
        $('.dataTables-example').DataTable( {
            scrollY:        setSizes(),
            "scrollCollapse": true,
            "paging":         false,
            "scrollX": true,
            "order": [],
            "searching": false
        } );
    }
});





//"scrollY":        "400px",
//$(window).resize(function() { setSizes(); });