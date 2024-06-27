<script>
	import { spring } from 'svelte/motion';
	import { onMount } from 'svelte';
	import fortunes from './fortuneCookies.json';

	let cookieOpen = false;
	let fortune = '';

	const rotation = spring(0, {
		stiffness: 0.1,
		damping: 0.25
	});

	// const fortunes = [
	// 	'Your creativity will lead you to success.',
	// 	'A journey of a thousand miles begins with a single step.',
	// 	'The best way to predict the future is to create it.',
	// 	'Your kindness will be rewarded tenfold.',
	// 	'Embrace change, it leads to new opportunities.'
	// ];

	function crackCookie() {
		cookieOpen = !cookieOpen;
		rotation.set(cookieOpen ? 180 : 0);
		if (cookieOpen) {
			fortune = fortunes[Math.floor(Math.random() * fortunes.length)];
		}
	}

	onMount(() => {
		fortune = fortunes[Math.floor(Math.random() * fortunes.length)];
	});
</script>

<main>
	<h1>Fortune Cookie</h1>
	<div class="cookie-container">
		<div class="cookie" on:click={crackCookie}>
			<div class="cookie-half top" style="transform: rotateX({$rotation}deg)"></div>
			<div class="cookie-half bottom"></div>
		</div>
		{#if cookieOpen}
			<p class="fortune">{fortune}</p>
		{/if}
	</div>
	<p class="instruction">Click the cookie to {cookieOpen ? 'close' : 'open'} it</p>
</main>

<style>
	main {
		display: flex;
		flex-direction: column;
		align-items: center;
		font-family: Arial, sans-serif;
		height: 100vh;
		justify-content: center;
		background-color: #f0f0f0;
	}

	.cookie-container {
		perspective: 1000px;
		margin-bottom: 20px;
	}

	.cookie {
		width: 200px;
		height: 100px;
		position: relative;
		transform-style: preserve-3d;
		cursor: pointer;
	}

	.cookie-half {
		position: absolute;
		width: 100%;
		height: 100%;
		backface-visibility: hidden;
		border-radius: 50% 50% 50% 50% / 60% 60% 40% 40%;
	}

	.top {
		background-color: #d4a017;
		transform-origin: bottom;
	}

	.bottom {
		background-color: #c19a16;
	}

	.fortune {
		text-align: center;
		max-width: 200px;
		margin-top: 20px;
		font-style: italic;
	}

	.instruction {
		margin-top: 20px;
		color: #666;
	}
</style>
