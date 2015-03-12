"use strict"
// Makes the browser show you syntax errors

function refreshData() {
	// $('#get-moar-data').attr("disabled", true)
	$.ajax(
		{url: '/fetch_data',}
	);
};

$('#get-moar-data').on('click', refreshData);


function getReport() {
	$.get(
		"/check_week_number",
		function (result) {
			// Take the week number that was returned and append to the route call
			$(location).attr('href', 'week/' + result);
	});
};

$('#show-bio-retro').on('click', getReport);


$(function () {

	$.each($('.day-clickable').children(), function (i, elm) {

		// This goes up one level in the DOM, gets the sibling object  
		// (the tr above the clickable element), gets its children (the row of
		// datestrings) and gets the string at the same index as the
		// element the user clicked. 
		var date_string = $(elm).parent().prev().children().eq(i).text();

		$(elm).on('click', function () {
			// the /slash in front of /day is important or else this *appends* to the current location
			debugger;
			$(location).attr('href', '/day/' + date_string);
		})
	});
});