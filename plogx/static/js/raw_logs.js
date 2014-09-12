$(document).ready(function(){
	$('.filter').multifilter();
	$('#current_day').html((moment($('#date').html(), "YYYYMMDD").format("MMMM DD, YYYY")));
});