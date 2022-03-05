$(document).ready(function() {
	$(".coll").click(function() {
		this.classList.toggle("active");
		var content = this.nextElementSibling;
		if (content.style.maxHeight) {
			content.style.maxHeight = null;
		} else {
			content.style.maxHeight = content.scrollHeight + "px";
		}
	});

	var myCarousel = document.querySelector('#myCarousel')
	var carousel = new bootstrap.Carousel(myCarousel)
});