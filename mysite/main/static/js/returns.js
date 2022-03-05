$(document).ready(function() {
	checkResize();

	$(window).resize(function() {
		checkResize();
	});
});

function checkResize() {
	var width = $(window).width();

	if(width <= 751) {
		$(".arrow").html("&darr;");
	} else {
		$(".arrow").html("&rarr;");
	}
}