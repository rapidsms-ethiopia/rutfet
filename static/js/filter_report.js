/* jquery code for filter report module */


$(document).ready(function() {
	
	// Hide the visibility of Filter by, date range and group by options
	$("#filter-place_type").addClass("hidden");
	$("#filter-place_name").addClass("hidden");
	$("#filter-period_start").addClass("hidden");
	$("#filter-period_end").addClass("hidden");
	$("#filter-groupby").addClass("hidden");
	
	// By default select the Enty model and related options
	if($("#filter-form-model :selected").val() == "entry")
	{
		$("#filter-place_type").removeClass("hidden");
		$("#filter-place_name").removeClass("hidden");
		$("#filter-period_start").removeClass("hidden");
		$("#filter-period_end").removeClass("hidden");
		$("#filter-groupby").removeClass("hidden");
	}
	
	else if ($("#filter-form-model :selected").val() == "rutfreporter" || $("#filter-form-model :selected").val() == "webuser" || $("#filter-form-model :selected").val() == "healthpost")
	{
		$("#filter-place_type").removeClass("hidden");
		$("#filter-place_name").removeClass("hidden");
		$("#filter-period_start").addClass("hidden");
		$("#filter-period_end").addClass("hidden");
		$("#filter-groupby").addClass("hidden");
	}
	else if ($("#filter-form-model :selected").val() == "alert")
	{
		$("#filter-place_type").removeClass("hidden");
		$("#filter-place_name").removeClass("hidden");
		//$("#filter-period_start").removeClass("hidden");
		//$("#filter-period_end").removeClass("hidden");
		$("#filter-groupby").addClass("hidden");	
	}
	else
	{
		$("#filter-place_type").addClass("hidden");
		$("#filter-place_name").addClass("hidden");
		$("#filter-period_start").addClass("hidden");
		$("#filter-period_end").addClass("hidden");
		$("#filter-groupby").addClass("hidden");	
	}
	
	//Display filtering options based on the selected model			
	$("#filter-form-model").bind("change", function(e) {
		//alert(e.target.value)
		if(e.target.value == "entry")
		{
			$("#filter-place_type").removeClass("hidden");
			$("#filter-place_name").removeClass("hidden");
			$("#filter-period_start").removeClass("hidden");
			$("#filter-period_end").removeClass("hidden");
			$("#filter-groupby").removeClass("hidden");
		}
		else if (e.target.value == "rutfreporter" || e.target.value == "webuser" || e.target.value == "healthpost")
		{
			$("#filter-place_type").removeClass("hidden");
			$("#filter-place_name").removeClass("hidden");
			$("#filter-period_start").addClass("hidden");
			$("#filter-period_end").addClass("hidden");
			$("#filter-groupby").addClass("hidden");
		}
		else if (e.target.value == "alert")
		{
			$("#filter-place_type").removeClass("hidden");
			$("#filter-place_name").removeClass("hidden");
			//$("#filter-period_start").removeClass("hidden");
			//$("#filter-period_end").removeClass("hidden");
			$("#filter-groupby").addClass("hidden");	
		}
		else
		{
			$("#filter-place_type").addClass("hidden");
			$("#filter-place_name").addClass("hidden");
			$("#filter-period_start").addClass("hidden");
			$("#filter-period_end").addClass("hidden");
			$("#filter-groupby").addClass("hidden");	
		}
	});
	
	
	
	
	
});
