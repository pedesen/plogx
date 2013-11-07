$(document).ready(function(){
	$.getJSON( "/all_items", function( data ) {
		console.log(data);
		alert("Logs loaded (see console)");
	});
});
