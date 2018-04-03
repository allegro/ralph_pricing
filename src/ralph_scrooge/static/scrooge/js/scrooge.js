/*
Disable or enable datapicker fields in extracosts
*/

$(document).ready(function(){
    function change_input(parent_element) {
    	/* Enable or disable fields with date*/
	    if ($(parent_element).find('option:selected').val() == 0) {
	    	$(parent_element).parents('tr').find('input.datepicker').attr('disabled', true);
	    	$(parent_element).parents('tr').find('input.datepicker').val(null);
	    } else {
	    	$(parent_element).parents('tr').find('input.datepicker').attr('disabled', false);
	    };
	};
	$('.mode_selector').each(function() {
		// Set enable/disable for fields at the begin
		change_input(this);
	});

    $('.mode_selector').change(function() {
		// Set enable/disable when select box change
		change_input(this);
    });
});
