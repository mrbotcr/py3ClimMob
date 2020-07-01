/**
 * Created by brandon on 22/05/17.
 */

$(document).ready(function(){

    /*$('#SearchInTable').keyup(function()
	{
		searchTable($(this).val());
	});*/

        $('body').css('overflow-y','scroll');
        var Shuffle = window.Shuffle;
        var jQuery = window.jQuery;
        var myShuffle = new Shuffle(document.querySelector('.my-shuffle'), {
            itemSelector: '.feed-item',
            sizer: '.my-sizer-element',
            buffer: 1,
        });

        jQuery('input[name="shuffle-filter"]').on('change', function (evt) {
            var input = evt.currentTarget;
            if (input.checked) {
                myShuffle.filter(input.value);
                $(".forHidden").css("display","none")
                $("#options_"+input.value).css("display","block")

                //$(".forRefresh").css("width","49%");
            }
        });

        jQuery('.js-shuffle-search').on('keyup', function (evt) {
            var input = evt.currentTarget;
            var searchText = input.value.toLowerCase();

            myShuffle.filter(function (element, shuffle) {

                // If there is a current filter applied, ignore elements that don't match it.
                if (shuffle.group !== Shuffle.ALL_ITEMS) {
                    // Get the item's groups.
                    var groups = JSON.parse(element.getAttribute('data-groups'));
                    var isElementInCurrentGroup = groups.indexOf(shuffle.group) !== -1;

                    // Only search elements in the current group
                    if (!isElementInCurrentGroup) {
                        return false;
                    }
                }

                var titleText = element.getAttribute('data-title').toLowerCase().trim();
                return titleText.indexOf(searchText) !== -1;
            });

        });
});

/*function searchTable(searching)
{
    var table = $('#tabletechnologies');
    table.find('tr').each(function(index, row)
    {
        var allCells = $(row).find('td');

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
}*/
