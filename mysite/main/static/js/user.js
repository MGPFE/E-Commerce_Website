$(document).ready(function() {
	$("#user-code-btn").click(function() {
		var code_display = $("#user-code").css("display");

		if(code_display == "none") {
			$("#user-code").fadeIn().css("display", "inline-block");
			$(this).html("Ukryj kod")
		} else {
			$("#user-code").fadeOut()
			$(this).html("Pokaż kod")
		}
	});
});