/*
Fixed table header on scroll
*/

$(document).ready(function(){
    function change_input(parent_element) {
	    if ($(parent_element).find('option:selected').val() == 0) {
	    	$(parent_element).parents('tr').find('input.datepicker').attr('disabled', true)
	    	$(parent_element).parents('tr').find('input.datepicker').val(null)
	    } else {
	    	$(parent_element).parents('tr').find('input.datepicker').attr('disabled', false)
	    }
	}
	$('.mode_selector').each(function() {
		change_input(this)
	})

    $('.mode_selector').change(function() {
		change_input(this)
    })

});
