$(document).scroll(function() {
	var y = $(window).scrollTop();
	// console.log(y);
	if (y >= 200) {
		$(".go-up-div").fadeIn().css("display", "flex");
		// this.style.display = "flex";
	} else {
		$(".go-up-div").fadeOut();
		// this.style.display = "none";
	}
});

window.setTimeout(function() {
	$(".alert").fadeTo(500, 0).slideUp(500, function() {
		$(this).remove();
	});
}, 3000);
