document.addEventListener('DOMContentLoaded', () => {

	// Get all "navbar-burger" elements
	const $navbarBurgers = Array.prototype.slice.call(document.querySelectorAll('.navbar-burger'), 0);

	// Add a click event on each of them
	$navbarBurgers.forEach(el => {
		el.addEventListener('click', () => {

			// Get the target from the "data-target" attribute
			const target = el.dataset.target;
			const $target = document.getElementById(target);

			// Toggle the "is-active" class on both the "navbar-burger" and the "navbar-menu"
			el.classList.toggle('is-active');
			$target.classList.toggle('is-active');

		});
	});

	// Handle message-accordions
	const messageAccordions = document.querySelectorAll('.message-accordion');

	for(let i = 0; i < messageAccordions.length; i++){
		const accordion = messageAccordions[i];
		const button = accordion.querySelector('div.message-header a');
		const buttonLabel = button.querySelector('span.icon i');
		const accordionBody = accordion.querySelector('div.message-body');

		button.onclick = function(){
			accordionBody.classList.toggle('is-hidden');
			buttonLabel.classList.toggle('la-plus-circle');
			buttonLabel.classList.toggle('la-minus-circle');
		};
	}

});