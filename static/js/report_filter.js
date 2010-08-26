/* jquery code for filter report module */


$(document).ready(function() {
	
	// Hide the visibility of Filter headers and body
	$("#filter-headers").addClass("hidden");
	$("#filter-body").addClass("hidden");
	
	//Style the link
	$("#add-filter .addlink").hover(function() {
  		$(this).addClass('link_style');},
  		function() {
  		$(this).removeClass('link_style');
  	});
	
	
	//Bind click event for 'Add a Filter' label
	$("#add-filter .addlink").bind('click', function(){
		
		if($("#filter-headers").is(".hidden") && $("#filter-body").is(".hidden"))
		{
			$("#filter-headers").removeClass("hidden").appendTo("#theader");
			$("#filter-body").removeClass("hidden").insertAfter("#theader");
		}
		else
		{
			//$("#filter-headers").clone().insertAfter("#theader");
			$("#filter-body").clone().insertAfter("#theader");
		}
		
	});
	
	$("#filter-form-model").bind("change", function(e) {
		$("#filter-body select.fields").removeClass("visible");
		$(".filter-fields-" + e.target.value).addClass("visible");
	});
	
	
	
});
