$('document').ready(function(){
	
	$('td').click(function(e){
		var first_name = $(this).parent('tr').find('td').first().text();
		alert('Hey ' + first_name + '!');
	});
	
});