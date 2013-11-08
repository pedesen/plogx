$(document).ready(function(){
	$.getJSON( "/stats_per_day/20131106", function( data ) {
		console.log(data)
	});
});
